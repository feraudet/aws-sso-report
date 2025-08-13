"""
Permission Scoring Configuration

This module loads and manages the permission scoring configuration
from YAML files to provide flexible and accurate AWS action scoring.
"""

import os
import re
from typing import Dict, List, Optional, Tuple

import yaml

# Try relative import first, fallback to absolute import
try:
    from .data_models import AccessLevel, PermissionScores, RiskLevel
except ImportError:
    try:
        from data_models import AccessLevel, PermissionScores, RiskLevel
    except ImportError:
        # Define minimal enums for standalone usage
        from enum import Enum

        class AccessLevel(Enum):
            READ_ONLY = "Read Only"
            READ_WRITE = "Read Write"
            FULL_ADMIN = "Full Admin"

        class RiskLevel(Enum):
            LOW = "Low"
            MEDIUM = "Medium"
            HIGH = "High"
            CRITICAL = "Critical"

        class PermissionScores:
            def __init__(self, read_score=0, write_score=0, admin_score=0):
                self.read_score = read_score
                self.write_score = write_score
                self.admin_score = admin_score


class PermissionScoringConfig:
    """Manages permission scoring configuration from YAML files."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration file path."""
        if config_path is None:
            # Default to config/permission_scoring_minimal.yaml relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(
                project_root, "config", "permission_scoring_minimal.yaml"
            )

        self.config_path = config_path
        self.config = self._load_config()

        # Cache compiled regex patterns for performance
        self._pattern_cache = {}
        self._compile_patterns()

    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {self.config_path}")
            print("Using default scoring logic.")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing configuration file: {e}")
            print("Using default scoring logic.")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration if file is not available."""
        return {
            "scoring_rules": {
                "risk_levels": {
                    "minimal": 1,
                    "low": 3,
                    "medium": 5,
                    "high": 8,
                    "critical": 10,
                },
                "defaults": {"read_score": 2, "write_score": 5, "admin_score": 0},
            },
            "services": {},
            "managed_policies": {"critical": [], "high": [], "medium": [], "low": []},
            "patterns": {"critical": [], "high": [], "medium": [], "low": []},
            "weights": {
                "service_specific": 1.0,
                "pattern_based": 0.7,
                "managed_policy": 1.2,
            },
        }

    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        patterns = self.config.get("patterns", {})
        for risk_level, pattern_list in patterns.items():
            self._pattern_cache[risk_level] = [
                re.compile(pattern, re.IGNORECASE) for pattern in pattern_list
            ]

    def score_managed_policy(self, policy_name: str) -> Tuple[int, int, int]:
        """
        Score a managed policy by name.

        Returns:
            Tuple of (read_score, write_score, admin_score)
        """
        managed_policies = self.config.get("managed_policies", {})

        # Check if policy is directly defined in managed_policies
        if policy_name in managed_policies:
            policy_config = managed_policies[policy_name]
            return (
                policy_config.get("read_score", 2),
                policy_config.get("write_score", 5),
                policy_config.get("admin_score", 0),
            )

        # Legacy support: Check old-style risk level lists
        risk_levels = self.config["scoring_rules"]["risk_levels"]
        for risk_level, policies in managed_policies.items():
            if isinstance(policies, list) and any(
                policy in policy_name for policy in policies
            ):
                score = risk_levels.get(risk_level, 5)

                if risk_level == "critical":
                    return (score, score, score)  # Full admin access
                elif risk_level == "high":
                    return (score, score, score // 2)  # High write, some admin
                elif risk_level == "medium":
                    return (score, score, 0)  # Medium write, no admin
                elif risk_level == "low":
                    return (score, 0, 0)  # Read-only

        # Default scoring for unknown managed policies
        defaults = self.config["scoring_rules"]["defaults"]
        return (
            defaults["read_score"],
            defaults["write_score"],
            defaults["admin_score"],
        )

    def score_action(self, action: str) -> Tuple[int, int, int, str, str]:
        """
        Score an individual AWS action.

        Returns:
            Tuple of (read_score, write_score, admin_score, risk_level, justification)
        """
        # Check for special actions first (wildcards, etc.)
        special_actions = self.config.get("special_actions", {})
        if action in special_actions:
            return self._score_special_action(action, special_actions[action])

        # Parse service and action
        if ":" not in action:
            return self._score_by_pattern(action)

        service, action_name = action.split(":", 1)
        service = service.lower()

        # Try service-specific scoring first
        services = self.config.get("services", {})
        if service in services:
            return self._score_service_action(service, action, services[service])

        # Fall back to pattern-based scoring
        return self._score_by_pattern(action)

    def _score_special_action(
        self, action: str, action_config: Dict
    ) -> Tuple[int, int, int, str, str]:
        """Score special actions like wildcards."""
        risk_levels = self.config["scoring_rules"]["risk_levels"]
        risk_name = action_config.get("risk_level", "critical")
        description = action_config.get("description", f"Special action {action}")

        base_score = risk_levels.get(risk_name, 10)

        # Generate human-readable justification
        if action == "*":
            justification = "Full administrative access: Complete control over all AWS services and resources"
        elif action == "*:*":
            justification = (
                "Wildcard access: Unrestricted permissions across all AWS services"
            )
        else:
            justification = f"Special permission: {description}"

        return (base_score, base_score, base_score, risk_name, justification)

    def _score_service_action(
        self, service: str, full_action: str, service_config: Dict
    ) -> Tuple[int, int, int, str, str]:
        """Score an action using service-specific configuration."""
        risk_levels = self.config["scoring_rules"]["risk_levels"]
        weight = self.config["weights"]["service_specific"]

        # Check if action is in the actions dictionary
        actions = service_config.get("actions", {})
        if full_action in actions:
            action_config = actions[full_action]
            risk_name = action_config.get("risk_level", "medium")
            description = action_config.get("description", f"Action {full_action}")

            base_score = risk_levels.get(risk_name, 5)
            weighted_score = int(base_score * weight)

            # Generate human-readable justification
            justification = f"{description} (Risk: {risk_name.upper()})"

            if risk_name == "critical":
                return (
                    weighted_score,
                    weighted_score,
                    weighted_score,
                    risk_name,
                    justification,
                )
            elif risk_name == "high":
                return (
                    weighted_score,
                    weighted_score,
                    weighted_score // 2,
                    risk_name,
                    justification,
                )
            elif risk_name == "medium":
                return (
                    weighted_score // 2,
                    weighted_score,
                    0,
                    risk_name,
                    justification,
                )
            elif risk_name == "low":
                justification += ". LOW: Read-only access - minimal security risk."
                return (weighted_score, 0, 0, risk_name, justification)

        # Legacy support: Check old-style risk level lists
        for risk_level in [
            "critical_actions",
            "high_risk_actions",
            "medium_risk_actions",
            "read_only_actions",
        ]:
            actions_list = service_config.get(risk_level, [])
            if full_action in actions_list:
                risk_name = risk_level.replace("_actions", "").replace("_risk", "")
                if risk_name == "read_only":
                    risk_name = "low"

                base_score = risk_levels.get(risk_name, 5)
                weighted_score = int(base_score * weight)

                # Generate justification for legacy configuration
                justification = f"Legacy service configuration: Action found in {risk_level} list. Risk level: {risk_name.upper()} (score: {base_score})"

                if risk_name == "critical":
                    justification += (
                        ". CRITICAL: High-risk action requiring immediate attention."
                    )
                    return (
                        weighted_score,
                        weighted_score,
                        weighted_score,
                        risk_name,
                        justification,
                    )
                elif risk_name == "high":
                    justification += ". HIGH: Significant security implications."
                    return (
                        weighted_score,
                        weighted_score,
                        weighted_score // 2,
                        risk_name,
                        justification,
                    )
                elif risk_name == "medium":
                    justification += ". MEDIUM: Moderate security risk."
                    return (
                        weighted_score // 2,
                        weighted_score,
                        0,
                        risk_name,
                        justification,
                    )
                elif risk_name == "low":
                    justification += ". LOW: Limited security impact."
                    return (weighted_score, 0, 0, risk_name, justification)

        # If not found in service-specific config, try patterns
        return self._score_by_pattern(full_action)

    def _score_by_pattern(self, action: str) -> Tuple[int, int, int, str, str]:
        """Score an action using pattern matching."""
        risk_levels = self.config["scoring_rules"]["risk_levels"]
        weight = self.config["weights"]["pattern_based"]

        # Check patterns in order of severity (critical first)
        for risk_level in ["critical", "high", "medium", "low"]:
            patterns = self._pattern_cache.get(risk_level, [])
            for pattern in patterns:
                if pattern.match(action):
                    base_score = risk_levels.get(risk_level, 5)
                    weighted_score = int(base_score * weight)

                    # Generate pattern-based justification
                    justification = f"Pattern-based scoring: Action '{action}' matches {risk_level.upper()} risk pattern. Score: {base_score} (weighted: {weighted_score})"

                    if risk_level == "critical":
                        justification += ". CRITICAL: Pattern indicates high-risk administrative action."
                        return (
                            weighted_score,
                            weighted_score,
                            weighted_score,
                            risk_level,
                            justification,
                        )
                    elif risk_level == "high":
                        justification += ". HIGH: Pattern indicates significant write/modify permissions."
                        return (
                            weighted_score,
                            weighted_score,
                            weighted_score // 2,
                            risk_level,
                            justification,
                        )
                    elif risk_level == "medium":
                        justification += (
                            ". MEDIUM: Pattern indicates standard write operations."
                        )
                        return (
                            weighted_score // 2,
                            weighted_score,
                            0,
                            risk_level,
                            justification,
                        )
                    elif risk_level == "low":
                        justification += (
                            ". LOW: Pattern indicates read-only operations."
                        )
                        return (weighted_score, 0, 0, risk_level, justification)

        # Default scoring for unknown actions
        defaults = self.config["scoring_rules"]["defaults"]
        justification = f"Unknown action: '{action}' - using default risk assessment"
        return (
            defaults["read_score"],
            defaults["write_score"],
            defaults["admin_score"],
            "unknown",
            justification,
        )

    def analyze_actions(
        self, actions: List[str]
    ) -> Tuple[AccessLevel, PermissionScores, List[str]]:
        """
        Analyze a list of actions and return overall assessment.

        Returns:
            Tuple of (access_level, permission_scores, high_risk_actions)
        """
        scores = PermissionScores()
        high_risk_actions = []
        has_admin = False
        has_write = False
        justifications = []

        for action in actions:
            (
                read_score,
                write_score,
                admin_score,
                risk_level,
                justification,
            ) = self.score_action(action)
            justifications.append(f"{action}: {justification}")

            # Accumulate scores (take maximum for each category)
            scores.read_score = max(scores.read_score, read_score)
            scores.write_score = max(scores.write_score, write_score)
            scores.admin_score = max(scores.admin_score, admin_score)

            # Track action types
            if admin_score > 0:
                has_admin = True
            if write_score > 0:
                has_write = True

            # Track high-risk actions
            if risk_level in ["critical", "high"]:
                high_risk_actions.append(action)

        # Determine access level
        if has_admin or scores.admin_score >= 5:
            access_level = AccessLevel.FULL_ADMIN
        elif has_write or scores.write_score >= 5:
            access_level = AccessLevel.READ_WRITE
        elif scores.read_score > 0:
            access_level = AccessLevel.READ_ONLY
        else:
            access_level = AccessLevel.UNKNOWN

        # Combine all justifications into a comprehensive explanation
        scores.justification = (
            f"Analysis of {len(actions)} actions. Access level: {access_level.value}. "
            + f"High-risk actions: {len(high_risk_actions)}. "
            + "Detailed breakdown: "
            + "; ".join(justifications[:5])
        )  # Limit to first 5 for readability

        if len(justifications) > 5:
            scores.justification += f" ... and {len(justifications) - 5} more actions."

        return access_level, scores, high_risk_actions

    def get_risk_explanation(self, action: str) -> str:
        """Get a human-readable explanation of why an action has its risk level."""
        _, _, _, risk_level, justification = self.score_action(action)
        return justification

        explanations = {
            "critical": "Critical risk - Can lead to full system compromise or privilege escalation",
            "high": "High risk - Can cause significant damage or security issues",
            "medium": "Medium risk - Can modify resources but limited impact",
            "low": "Low risk - Read-only or minimal impact operations",
            "unknown": "Unknown risk - Action not in configuration database",
        }

        return explanations.get(risk_level, "Risk level unknown")


# Global instance for convenience
_scoring_config_instance = None


def get_scoring_config() -> PermissionScoringConfig:
    """Get or create the global scoring configuration instance."""
    global _scoring_config_instance
    if _scoring_config_instance is None:
        _scoring_config_instance = PermissionScoringConfig()
    return _scoring_config_instance


# For backward compatibility
scoring_config = get_scoring_config()
