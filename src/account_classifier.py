"""
AWS Account Classification Module

This module provides functionality to classify AWS accounts based on
configurable patterns defined in the account_classification.yaml file.
"""

import os
from typing import Dict, List, Optional

import yaml

from .data_models import AWSAccount


class AccountClassifier:
    """Classifies AWS accounts based on configurable patterns."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the classifier with configuration."""
        if config_path is None:
            # Default to config file in the config directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(
                os.path.dirname(current_dir), "config", "account_classification.yaml"
            )

        self.config_path = config_path
        self.config = self._load_config()
        self.case_sensitive = self.config.get("case_sensitive", False)
        self.default_classification = self.config.get(
            "default_classification", "Unclassified"
        )

    def _load_config(self) -> Dict:
        """Load the classification configuration from YAML file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(
                f"Warning: Configuration file {self.config_path} not found. Using empty config."
            )
            return {"classifications": {}}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            return {"classifications": {}}

    def classify_account(self, account: AWSAccount) -> str:
        """
        Classify a single AWS account based on its name.

        Args:
            account: The AWS account to classify

        Returns:
            The classification name (e.g., "Production", "Development")
        """
        account_name = account.name
        if not self.case_sensitive:
            account_name = account_name.lower()

        classifications = self.config.get("classifications", {})

        for classification_name, rules in classifications.items():
            if self._matches_classification(account_name, rules):
                return classification_name

        return self.default_classification

    def _matches_classification(self, account_name: str, rules: Dict) -> bool:
        """
        Check if an account name matches the classification rules.

        Args:
            account_name: The account name to check (already case-normalized)
            rules: The classification rules (include/exclude patterns)

        Returns:
            True if the account matches this classification
        """
        include_patterns = rules.get("include", [])
        exclude_patterns = rules.get("exclude", [])

        # Normalize patterns for case sensitivity
        if not self.case_sensitive:
            include_patterns = [pattern.lower() for pattern in include_patterns]
            exclude_patterns = [pattern.lower() for pattern in exclude_patterns]

        # Check if account name matches any include pattern
        matches_include = False
        for pattern in include_patterns:
            if pattern in account_name:
                matches_include = True
                break

        # If no include patterns match, this classification doesn't apply
        if not matches_include:
            return False

        # Check if account name matches any exclude pattern
        for pattern in exclude_patterns:
            if pattern in account_name:
                return False

        return True

    def classify_accounts(self, accounts: List[AWSAccount]) -> Dict[str, str]:
        """
        Classify multiple AWS accounts.

        Args:
            accounts: List of AWS accounts to classify

        Returns:
            Dictionary mapping account ID to classification
        """
        classifications = {}
        for account in accounts:
            classifications[account.id] = self.classify_account(account)
        return classifications

    def get_classification_summary(
        self, accounts: List[AWSAccount]
    ) -> Dict[str, List[AWSAccount]]:
        """
        Get a summary of accounts grouped by classification.

        Args:
            accounts: List of AWS accounts to classify

        Returns:
            Dictionary mapping classification to list of accounts
        """
        summary = {}
        for account in accounts:
            classification = self.classify_account(account)
            if classification not in summary:
                summary[classification] = []
            summary[classification].append(account)
        return summary

    def get_available_classifications(self) -> List[str]:
        """Get list of all available classification names."""
        classifications = list(self.config.get("classifications", {}).keys())
        if self.default_classification not in classifications:
            classifications.append(self.default_classification)
        return classifications
