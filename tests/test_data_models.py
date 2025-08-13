"""
Tests for Data Models module.

These tests verify the data models work correctly without AWS connections.
"""

# No imports needed for basic data model tests

from src.data_models import AWSAccount, Role, User, UserAccountRoleGroup, UserSummary


class TestUser:
    """Test User data model."""

    def test_user_creation(self):
        """Test User object creation."""
        user = User(
            id="user123",
            username="john.doe",
            email="john.doe@example.com",
            display_name="John Doe",
        )

        assert user.id == "user123"
        assert user.username == "john.doe"
        assert user.email == "john.doe@example.com"
        assert user.display_name == "John Doe"
        assert user.name == "John Doe"  # Property that returns display_name or username

    def test_user_to_dict(self):
        """Test User name property."""
        user = User(
            id="user123",
            username="john.doe",
            email="john.doe@example.com",
            display_name="John Doe",
        )

        # Test that name property works correctly
        assert user.name == "John Doe"  # Should return display_name

        # Test with no display_name
        user_no_display = User(
            id="user456", username="jane.smith", email="jane@example.com"
        )
        assert user_no_display.name == "jane.smith"  # Should return username

    def test_user_equality(self):
        """Test User equality comparison."""
        user1 = User(id="user123", username="john.doe", email="john@example.com")
        user2 = User(id="user123", username="john.doe", email="john@example.com")
        user3 = User(id="user456", username="jane.doe", email="jane@example.com")

        assert user1 == user2
        assert user1 != user3


class TestAWSAccount:
    """Test AWSAccount data model."""

    def test_aws_account_creation(self):
        """Test AWSAccount object creation."""
        account = AWSAccount(id="123456789012", name="Production Account")

        assert account.id == "123456789012"
        assert account.name == "Production Account"

    def test_aws_account_str(self):
        """Test AWSAccount __str__ method."""
        account = AWSAccount(id="123456789012", name="Production Account")

        result = str(account)
        assert "123456789012" in result
        assert "Production Account" in result


class TestRole:
    """Test Role data model."""

    def test_role_creation(self):
        """Test Role object creation."""
        role = Role(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123456789")

        assert role.name == "AdminRole"
        assert role.arn == "arn:aws:sso:::permissionSet/ps-123456789"
        # Test default values
        from src.data_models import AccessLevel

        assert role.access_level == AccessLevel.UNKNOWN

    def test_role_risk_level(self):
        """Test Role risk_level property."""
        from src.data_models import PermissionScores, RiskLevel

        role = Role(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123456789")

        # Test with high admin score
        role.scores = PermissionScores(admin_score=9)
        assert role.risk_level == RiskLevel.CRITICAL

        # Test with medium write score
        role.scores = PermissionScores(write_score=6)
        assert role.risk_level == RiskLevel.MEDIUM


class TestUserAccountRoleGroup:
    """Test UserAccountRoleGroup data model."""

    def test_user_account_role_group_creation(self):
        """Test UserAccountRoleGroup object creation."""
        user = User(id="user123", username="john.doe", email="john@example.com")
        account = AWSAccount(id="123456789012", name="Prod")
        role = Role(name="Admin", arn="arn:aws:sso:::ps-123")

        assignment = UserAccountRoleGroup(
            user=user,
            account=account,
            role=role,
            responsible_group="DevOps Team",
            assignment_type="GROUP",
        )

        assert assignment.user == user
        assert assignment.account == account
        assert assignment.role == role
        assert assignment.responsible_group == "DevOps Team"
        assert assignment.assignment_type == "GROUP"

    def test_user_account_role_group_to_dict(self):
        """Test UserAccountRoleGroup to_dict method."""
        from src.data_models import PermissionScores

        user = User(
            id="user123",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        account = AWSAccount(id="123456789012", name="Prod")
        role = Role(name="Admin", arn="arn:aws:sso:::ps-123")
        role.scores = PermissionScores(read_score=5, write_score=7, admin_score=9)

        assignment = UserAccountRoleGroup(
            user=user,
            account=account,
            role=role,
            responsible_group="DevOps Team",
            assignment_type="GROUP",
        )

        result = assignment.to_dict()

        # Test the actual keys from the real to_dict method
        assert result["User"] == "John Doe"  # Should use user.name property
        assert result["User Email"] == "john@example.com"
        assert result["Responsible Group"] == "DevOps Team"
        assert result["Assignment Type"] == "GROUP"
        assert result["AWS Account"] == "Prod"
        assert result["Account ID"] == "123456789012"
        assert result["Role Name"] == "Admin"
        assert result["Access Level"] == role.access_level.value
        assert result["Read Score"] == 5
        assert result["Write Score"] == 7
        assert result["Admin Score"] == 9

    def test_user_account_role_group_default_values(self):
        """Test UserAccountRoleGroup with default values."""
        user = User(id="user123", username="john.doe", email="john@example.com")
        account = AWSAccount(id="123456789012", name="Prod")
        role = Role(name="Admin", arn="arn:aws:sso:::ps-123")

        assignment = UserAccountRoleGroup(user=user, account=account, role=role)

        assert assignment.responsible_group is None
        assert assignment.assignment_type == "UNKNOWN"

    def test_user_account_role_group_disabled_user_access_level(self):
        """Test that disabled users get 'No access' access level."""
        from src.data_models import AccessLevel, PermissionScores

        # Create a disabled user
        user = User(
            id="user123",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
            status="Disabled",
        )
        account = AWSAccount(id="123456789012", name="Prod")
        role = Role(name="Admin", arn="arn:aws:sso:::ps-123")
        role.access_level = AccessLevel.FULL_ADMIN
        role.scores = PermissionScores(read_score=5, write_score=7, admin_score=9)

        assignment = UserAccountRoleGroup(
            user=user,
            account=account,
            role=role,
            responsible_group="DevOps Team",
            assignment_type="GROUP",
        )

        result = assignment.to_dict()

        # Even though role has FULL_ADMIN access, disabled user should show "No access"
        assert result["Access Level"] == "No access"
        assert result["User Status"] == "Disabled"

    def test_user_account_role_group_enabled_user_access_level(self):
        """Test that enabled users get their actual access level."""
        from src.data_models import AccessLevel, PermissionScores

        # Create an enabled user
        user = User(
            id="user123",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
            status="Enabled",
        )
        account = AWSAccount(id="123456789012", name="Prod")
        role = Role(name="ReadOnlyRole", arn="arn:aws:sso:::ps-123")
        role.access_level = AccessLevel.READ_ONLY
        role.scores = PermissionScores(read_score=5, write_score=0, admin_score=0)

        assignment = UserAccountRoleGroup(
            user=user,
            account=account,
            role=role,
            responsible_group="DevOps Team",
            assignment_type="GROUP",
        )

        result = assignment.to_dict()

        # Enabled user should show their actual access level
        assert result["Access Level"] == "Read Only"
        assert result["User Status"] == "Enabled"

    def test_access_level_values(self):
        """Test that AccessLevel enum has the correct values."""
        from src.data_models import AccessLevel

        assert AccessLevel.READ_ONLY.value == "Read Only"
        assert AccessLevel.READ_WRITE.value == "Read Write"
        assert AccessLevel.FULL_ADMIN.value == "Admin"
        assert AccessLevel.NO_ACCESS.value == "No access"
        assert AccessLevel.UNKNOWN.value == "unknown"


class TestUserSummary:
    """Test UserSummary data model."""

    def test_user_summary_creation(self):
        """Test UserSummary object creation."""
        user = User(
            id="user123",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        accounts = [
            {"id": "123456789012", "name": "Account1"},
            {"id": "123456789013", "name": "Account2"},
        ]

        summary = UserSummary(user=user, accounts=accounts)

        assert summary.user == user
        assert summary.accounts == accounts

    def test_user_summary_to_dict(self):
        """Test UserSummary to_dict method."""
        user = User(
            id="user123",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        accounts = [
            {"id": "123456789012", "name": "Account1"},
            {"id": "123456789013", "name": "Account2"},
        ]

        summary = UserSummary(user=user, accounts=accounts)

        result = summary.to_dict()

        # Test the actual keys from the real to_dict method
        assert result["User"] == "John Doe"  # Should use user.name property
        assert result["Groups"] == []  # Default empty groups
        assert result["AWS Accounts"] == accounts

    def test_user_summary_empty_accounts(self):
        """Test UserSummary with empty accounts."""
        user = User(id="user123", username="john.doe", email="john@example.com")

        summary = UserSummary(user=user, accounts=[])

        result = summary.to_dict()
        assert (
            result["User"] == "john.doe"
        )  # Should use user.name property (username when no display_name)
        assert result["Groups"] == []  # Default empty groups
        assert result["AWS Accounts"] == []
