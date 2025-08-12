"""
Data Models and Structures

This module defines data classes and structures used throughout the
IAM Identity Center reporting application.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class AccessLevel(Enum):
    """Enumeration of access levels for roles."""

    READ_ONLY = "read-only"
    READ_WRITE = "read-write"
    FULL_ADMIN = "full-admin"
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

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


@dataclass
class User:
    """Represents a user in IAM Identity Center."""

    id: str
    username: str
    display_name: Optional[str] = None
    groups: List[str] = None

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
    responsible_group: Optional[str] = (
        None  # Group name or "DIRECT" for direct assignment
    )
    assignment_type: str = "UNKNOWN"  # "USER" or "GROUP"

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for CSV/Excel export."""
        return {
            "User": self.user.name,
            "Responsible Group": self.responsible_group or "DIRECT",
            "Assignment Type": self.assignment_type,
            "AWS Account": self.account.name,
            "Account ID": self.account.id,
            "Role Name": self.role.name,
            "Access Level": self.role.access_level.value,
            "Read Score": self.role.scores.read_score,
            "Write Score": self.role.scores.write_score,
            "Admin Score": self.role.scores.admin_score,
            "Risk Level": self.role.risk_level.value,
        }


@dataclass
class UserSummary:
    """Represents a user summary for JSON export."""

    user: User
    accounts: List[Dict[str, any]] = None

    def __post_init__(self):
        if self.accounts is None:
            self.accounts = []

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for JSON export."""
        return {
            "User": self.user.name,
            "Groups": self.user.groups,
            "AWS Accounts": self.accounts,
        }


# CSV field names for exports
CSV_FIELDNAMES = [
    "User",
    "Responsible Group",
    "Assignment Type",
    "AWS Account",
    "Account ID",
    "Role Name",
    "Access Level",
    "Read Score",
    "Write Score",
    "Admin Score",
    "Risk Level",
]
