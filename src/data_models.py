"""
Data Models and Structures

This module defines data classes and structures used throughout the
IAM Identity Center reporting application.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class AccessLevel(Enum):
    """Enumeration of access levels for roles."""

    READ_ONLY = "Read Only"
    READ_WRITE = "Read Write"
    FULL_ADMIN = "Admin"
    NO_ACCESS = "No access"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Enumeration of risk levels."""

    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class PermissionScores:
    """Represents permission scores for a role."""

    read_score: int = 0
    write_score: int = 0
    admin_score: int = 0
    justification: str = ""  # Explanation of why this score was assigned

    def get_risk_level(self) -> RiskLevel:
        """Calculate risk level based on scores."""
        if self.admin_score >= 8:
            return RiskLevel.CRITICAL
        elif self.admin_score >= 5 or self.write_score >= 8:
            return RiskLevel.HIGH
        elif self.write_score >= 5:
            return RiskLevel.MEDIUM
        elif self.read_score >= 5:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL


@dataclass
class Role:
    """Represents a role (Permission Set) with its analysis."""

    name: str
    arn: str
    access_level: AccessLevel = AccessLevel.UNKNOWN
    scores: PermissionScores = None

    def __post_init__(self):
        if self.scores is None:
            self.scores = PermissionScores()

    @property
    def risk_level(self) -> RiskLevel:
        """Get the risk level for this role."""
        return self.scores.get_risk_level()


@dataclass
class AWSAccount:
    """Represents an AWS account."""

    id: str
    name: str
    classification: str = "Unclassified"

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


@dataclass
class User:
    """Represents a user in IAM Identity Center."""

    id: str
    username: str
    display_name: Optional[str] = None
    email: str = "N/A"  # Primary email address from Identity Store
    groups: List[str] = None
    status: str = "Unknown"  # Enabled/Disabled - inferred from assignments

    def __post_init__(self):
        if self.groups is None:
            self.groups = []

    @property
    def name(self) -> str:
        """Get the display name or username."""
        return self.display_name or self.username


@dataclass
class UserAccountRoleGroup:
    """Represents a user-account-role assignment with responsible group."""

    user: User
    account: AWSAccount
    role: Role
    responsible_group: Optional[str] = None
    assignment_type: str = "UNKNOWN"  # "USER" or "GROUP"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV/Excel export."""
        # If user is disabled, override access level to "No access"
        access_level = (
            AccessLevel.NO_ACCESS.value
            if self.user.status.lower() == "disabled"
            else self.role.access_level.value
        )

        return {
            "User": self.user.name,
            "User Email": self.user.email,
            "User Status": self.user.status,
            "Responsible Group": self.responsible_group or "DIRECT",
            "Assignment Type": self.assignment_type,
            "AWS Account": self.account.name,
            "Account ID": self.account.id,
            "Account Classification": self.account.classification,
            "Role Name": self.role.name,
            "Access Level": access_level,
            "Read Score": self.role.scores.read_score,
            "Write Score": self.role.scores.write_score,
            "Admin Score": self.role.scores.admin_score,
            "Risk Level": self.role.risk_level.value,
            "Justification": self.role.scores.justification,
        }


@dataclass
class UserSummary:
    """Represents a user summary for JSON export."""

    user: User
    accounts: List[Dict[str, any]] = None

    def __post_init__(self):
        if self.accounts is None:
            self.accounts = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "User": self.user.name,
            "Groups": self.user.groups,
            "AWS Accounts": self.accounts,
        }


@dataclass
class UserAnalysis:
    """Represents a unique user for analysis export."""

    username: str
    email: str
    access_by_classification: Dict[
        str, str
    ] = None  # Classification -> highest access level

    def __post_init__(self):
        if self.access_by_classification is None:
            self.access_by_classification = {}

    def to_dict(self, classifications: List[str] = None) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        result = {
            "User": self.username,
            "Email": self.email,
        }

        # Add columns for each classification
        if classifications:
            for classification in classifications:
                result[classification] = self.access_by_classification.get(
                    classification, "No Access"
                )

        return result


@dataclass
class AccountAnalysis:
    """Represents an account analysis for export."""

    account_name: str
    account_id: str
    classification: str
    user_count: int
    admin_emails: List[str] = None
    read_write_emails: List[str] = None
    read_only_emails: List[str] = None

    def __post_init__(self):
        if self.admin_emails is None:
            self.admin_emails = []
        if self.read_write_emails is None:
            self.read_write_emails = []
        if self.read_only_emails is None:
            self.read_only_emails = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "Account Name": self.account_name,
            "Account ID": self.account_id,
            "Classification": self.classification,
            "User Count": self.user_count,
            "Admin Emails": "; ".join(sorted(self.admin_emails)),
            "Read Write Emails": "; ".join(sorted(self.read_write_emails)),
            "Read Only Emails": "; ".join(sorted(self.read_only_emails)),
        }


@dataclass
class RiskAnalysis:
    """Represents a risk analysis summary."""

    classification: str
    total_accounts: int
    total_users: int
    admin_users: int
    high_risk_users: int
    critical_risk_users: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "Classification": self.classification,
            "Total Accounts": self.total_accounts,
            "Total Users": self.total_users,
            "Admin Users": self.admin_users,
            "High Risk Users": self.high_risk_users,
            "Critical Risk Users": self.critical_risk_users,
        }


# CSV field names for exports
CSV_FIELDNAMES = [
    "User",
    "User Email",
    "User Status",
    "Responsible Group",
    "Assignment Type",
    "AWS Account",
    "Account ID",
    "Account Classification",
    "Role Name",
    "Access Level",
    "Read Score",
    "Write Score",
    "Admin Score",
    "Risk Level",
    "Justification",
]

# Base CSV field names for user analysis export (classifications will be added dynamically)
ANALYSIS_CSV_BASE_FIELDNAMES = [
    "User",
    "Email",
]

# CSV field names for account analysis export
ACCOUNT_ANALYSIS_CSV_FIELDNAMES = [
    "Account Name",
    "Account ID",
    "Classification",
    "User Count",
    "Admin Emails",
    "Read Write Emails",
    "Read Only Emails",
]

# CSV field names for risk analysis export
RISK_ANALYSIS_CSV_FIELDNAMES = [
    "Classification",
    "Total Accounts",
    "Total Users",
    "Admin Users",
    "High Risk Users",
    "Critical Risk Users",
]
