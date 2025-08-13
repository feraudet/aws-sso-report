"""
Tests for Data Collector module.

These tests use mocks to avoid real AWS connections.
"""

from unittest.mock import Mock, patch

from src.data_collector import DataCollector, _DataCollectorProxy, data_collector
from src.data_models import AWSAccount, Role, User


class TestDataCollector:
    """Test DataCollector class with mocked AWS clients."""

    @patch("src.data_collector.aws_clients")
    def test_data_collector_initialization(self, mock_aws_clients):
        """Test DataCollector initialization with mocked AWS clients."""
        mock_sso_admin = Mock()
        mock_identitystore = Mock()
        mock_organizations = Mock()

        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.identitystore = mock_identitystore
        mock_aws_clients.organizations = mock_organizations
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"
        mock_aws_clients.identity_store_id = "d-123456789"

        collector = DataCollector()

        assert collector.sso_admin == mock_sso_admin
        assert collector.identitystore == mock_identitystore
        assert collector.organizations == mock_organizations
        assert collector.instance_arn == "arn:aws:sso:::instance/ssoins-123"
        assert collector.identity_store_id == "d-123456789"

    @patch("src.data_collector.aws_clients")
    def test_get_users(self, mock_aws_clients):
        """Test getting users from Identity Store."""
        # Mock the identitystore client
        mock_identitystore = Mock()
        mock_aws_clients.identitystore = mock_identitystore
        mock_aws_clients.sso_admin = Mock()
        mock_aws_clients.organizations = Mock()
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_aws_clients.identity_store_id = "d-1234567890"

        # Mock paginator
        mock_paginator = Mock()
        mock_identitystore.get_paginator.return_value = mock_paginator

        # Mock paginate response
        mock_paginator.paginate.return_value = [
            {
                "Users": [
                    {
                        "UserId": "user1",
                        "UserName": "john.doe",
                        "DisplayName": "John Doe",
                        "Name": {"GivenName": "John", "FamilyName": "Doe"},
                        "Emails": [{"Value": "john@example.com", "Primary": True}],
                    }
                ]
            }
        ]

        # Create DataCollector after mocking
        collector = DataCollector()
        users = collector.get_users()

        assert len(users) == 1
        assert users[0]["UserId"] == "user1"
        assert users[0]["UserName"] == "john.doe"
        assert users[0]["DisplayName"] == "John Doe"
        assert users[0]["Emails"][0]["Value"] == "john@example.com"

    @patch("src.data_collector.aws_clients")
    def test_get_accounts(self, mock_aws_clients):
        """Test getting AWS accounts from Organizations."""
        # Mock the organizations client
        mock_organizations = Mock()
        mock_aws_clients.organizations = mock_organizations
        mock_aws_clients.identitystore = Mock()
        mock_aws_clients.sso_admin = Mock()
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_aws_clients.identity_store_id = "d-1234567890"

        # Mock paginator
        mock_paginator = Mock()
        mock_organizations.get_paginator.return_value = mock_paginator

        # Mock paginate response
        mock_paginator.paginate.return_value = [
            {
                "Accounts": [
                    {
                        "Id": "123456789012",
                        "Name": "Production",
                        "Email": "prod@example.com",
                        "Status": "ACTIVE",
                    }
                ]
            }
        ]

        # Create DataCollector after mocking
        collector = DataCollector()
        accounts = collector.get_accounts()

        assert len(accounts) == 1
        account = accounts["123456789012"]
        assert account.id == "123456789012"
        assert account.name == "Production"

    @patch("src.data_collector.permission_analyzer")
    @patch("src.data_collector.aws_clients")
    def test_get_permission_sets(self, mock_aws_clients, mock_permission_analyzer):
        """Test getting permission sets from SSO Admin."""
        # Mock the sso_admin client
        mock_sso_admin = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.identitystore = Mock()
        mock_aws_clients.organizations = Mock()
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_aws_clients.identity_store_id = "d-1234567890"

        # Mock list_permission_sets - need to use paginator
        mock_paginator = Mock()
        mock_sso_admin.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {
                "PermissionSets": [
                    "arn:aws:sso:::permissionSet/ps-123",
                    "arn:aws:sso:::permissionSet/ps-456",
                ]
            }
        ]

        # Mock describe_permission_set
        mock_sso_admin.describe_permission_set.side_effect = [
            {
                "PermissionSet": {
                    "Name": "AdminRole",
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ps-123",
                    "Description": "Admin access",
                }
            },
            {
                "PermissionSet": {
                    "Name": "ReadOnlyRole",
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ps-456",
                    "Description": "Read-only access",
                }
            },
        ]

        # Mock permission analyzer to avoid real analysis
        mock_permission_analyzer.create_role_from_permission_set.side_effect = [
            Mock(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123"),
            Mock(name="ReadOnlyRole", arn="arn:aws:sso:::permissionSet/ps-456"),
        ]

        # Create DataCollector after mocking
        collector = DataCollector()
        permission_sets = collector.get_permission_sets()

        assert len(permission_sets) == 2
        admin_role = permission_sets["arn:aws:sso:::permissionSet/ps-123"]
        readonly_role = permission_sets["arn:aws:sso:::permissionSet/ps-456"]
        assert admin_role.name == "AdminRole"
        assert readonly_role.name == "ReadOnlyRole"

    @patch("src.data_collector.aws_clients")
    def test_get_assignments(self, mock_aws_clients):
        """Test getting account assignments."""
        # Mock AWS clients completely to avoid real connections
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_aws_clients.identity_store_id = "d-1234567890"

        # Create a DataCollector instance with mocked dependencies
        collector = DataCollector()
        collector.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        collector.identity_store_id = "d-1234567890"

        # Mock the sso_admin client
        mock_sso_admin = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"

        # Mock list_account_assignments
        mock_sso_admin.list_account_assignments.return_value = {
            "AccountAssignments": [
                {
                    "AccountId": "123456789012",
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ps-123",
                    "PrincipalType": "USER",
                    "PrincipalId": "user1",
                }
            ]
        }

        # Create test data
        user = User(id="user1", username="john.doe", email="john@example.com")
        account = AWSAccount(id="123456789012", name="Production")
        role = Role(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123")

        assignments = collector.get_assignments([user], [account], [role])

        assert len(assignments) == 1
        assert assignments[0].user.id == "user1"
        assert assignments[0].account.id == "123456789012"
        assert assignments[0].role.name == "AdminRole"

    @patch("src.data_collector.permission_analyzer")
    @patch("src.data_collector.aws_clients")
    def test_collect_all_data(self, mock_aws_clients, mock_permission_analyzer):
        """Test collecting all data."""
        # Mock AWS clients completely to avoid real connections
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_aws_clients.identity_store_id = "d-1234567890"

        # Create a DataCollector instance with mocked dependencies
        collector = DataCollector()
        collector.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        collector.identity_store_id = "d-1234567890"

        # Mock AWS clients
        mock_identitystore = Mock()
        mock_organizations = Mock()
        mock_sso_admin = Mock()

        mock_aws_clients.identitystore = mock_identitystore
        mock_aws_clients.organizations = mock_organizations
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_aws_clients.identity_store_id = "d-1234567890"

        # Mock users
        mock_user_paginator = Mock()
        mock_identitystore.get_paginator.return_value = mock_user_paginator
        mock_user_paginator.paginate.return_value = [
            {
                "Users": [
                    {
                        "UserId": "user1",
                        "UserName": "john.doe",
                        "DisplayName": "John Doe",
                        "Name": {"GivenName": "John", "FamilyName": "Doe"},
                        "Emails": [{"Value": "john@example.com", "Primary": True}],
                    }
                ]
            }
        ]

        # Mock accounts
        mock_account_paginator = Mock()
        mock_organizations.get_paginator.return_value = mock_account_paginator
        mock_account_paginator.paginate.return_value = [
            {
                "Accounts": [
                    {
                        "Id": "123456789012",
                        "Name": "Production",
                        "Email": "prod@example.com",
                        "Status": "ACTIVE",
                    }
                ]
            }
        ]

        # Mock permission sets
        mock_sso_admin.list_permission_sets.return_value = {
            "PermissionSets": ["ps-123"]
        }
        mock_sso_admin.describe_permission_set.return_value = {
            "PermissionSet": {
                "Name": "AdminRole",
                "PermissionSetArn": "arn:aws:sso:::permissionSet/ps-123",
                "Description": "Admin access",
            }
        }

        # Mock assignments
        mock_sso_admin.list_account_assignments.return_value = {
            "AccountAssignments": [
                {
                    "AccountId": "123456789012",
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ps-123",
                    "PrincipalType": "USER",
                    "PrincipalId": "user1",
                }
            ]
        }

        # Mock permission analyzer
        mock_permission_analyzer.analyze_permission_set.return_value = Mock(
            read_score=5, write_score=7, admin_score=9
        )

        user_account_roles, user_summaries = collector.collect_all_data()

        assert len(user_account_roles) == 1
        assert len(user_summaries) == 1
        assert user_account_roles[0].user.username == "john.doe"
        assert user_account_roles[0].account.name == "Production"
        assert user_account_roles[0].role.name == "AdminRole"

    @patch("src.data_collector.get_data_collector")
    def test_global_instance_exists(self, mock_get_data_collector):
        """Test that global data_collector instance exists."""
        # Mock the get_data_collector function to avoid real AWS connections
        mock_collector = Mock()
        mock_get_data_collector.return_value = mock_collector

        assert data_collector is not None
        assert isinstance(data_collector, _DataCollectorProxy)

        # Test that the proxy can access DataCollector methods
        assert hasattr(data_collector, "get_users")
