"""
Tests for Permission Analyzer module.

These tests use mocks to avoid real AWS connections.
"""

from unittest.mock import Mock, patch

from src.data_models import AWSAccount, Role, User
from src.permission_analyzer import PermissionAnalyzer, permission_analyzer


class TestPermissionAnalyzer:
    """Test PermissionAnalyzer class with mocked AWS clients."""

    @patch("src.permission_analyzer.aws_clients")
    def test_permission_analyzer_initialization(self, mock_aws_clients):
        """Test PermissionAnalyzer initialization with mocked AWS clients."""
        mock_sso_admin = Mock()
        mock_cloudtrail = Mock()

        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.cloudtrail = mock_cloudtrail
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        analyzer = PermissionAnalyzer()

        assert analyzer.sso_admin == mock_sso_admin
        assert analyzer.cloudtrail == mock_cloudtrail
        assert analyzer.instance_arn == "arn:aws:sso:::instance/ssoins-123"

    @patch("src.permission_analyzer.aws_clients")
    def test_get_permission_set_policies(self, mock_aws_clients):
        """Test get_permission_set_policies method with mocked responses."""
        mock_sso_admin = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        permission_set_arn = "arn:aws:sso:::permissionSet/ps-123"

        # Mock inline policy response
        mock_sso_admin.get_inline_policy_for_permission_set.return_value = {
            "InlinePolicy": '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}'
        }

        # Mock managed policies response
        mock_sso_admin.list_managed_policies_in_permission_set.return_value = {
            "AttachedManagedPolicies": [
                {
                    "Name": "AdministratorAccess",
                    "Arn": "arn:aws:iam::aws:policy/AdministratorAccess",
                }
            ]
        }

        # Mock customer managed policies response
        mock_sso_admin.list_customer_managed_policy_references_in_permission_set.return_value = {
            "CustomerManagedPolicyReferences": [{"Name": "CustomPolicy", "Path": "/"}]
        }

        analyzer = PermissionAnalyzer()
        policies = analyzer.get_permission_set_policies(permission_set_arn)

        assert "inline_policy" in policies
        assert "managed_policies" in policies
        assert "customer_managed_policies" in policies

        assert len(policies["managed_policies"]) == 1
        assert policies["managed_policies"][0]["Name"] == "AdministratorAccess"

    @patch("src.permission_analyzer.aws_clients")
    def test_analyze_permissions_basic(self, mock_aws_clients):
        """Test analyze_permissions method with basic data."""
        mock_sso_admin = Mock()
        mock_cloudtrail = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.cloudtrail = mock_cloudtrail
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        # Mock get_permission_set_policies
        mock_sso_admin.get_inline_policy_for_permission_set.return_value = {
            "InlinePolicy": ""
        }
        mock_sso_admin.list_managed_policies_in_permission_set.return_value = {
            "AttachedManagedPolicies": [
                {
                    "Name": "ReadOnlyAccess",
                    "Arn": "arn:aws:iam::aws:policy/ReadOnlyAccess",
                }
            ]
        }
        mock_sso_admin.list_customer_managed_policy_references_in_permission_set.return_value = {
            "CustomerManagedPolicyReferences": []
        }

        # Mock CloudTrail response (empty for simplicity)
        mock_cloudtrail.lookup_events.return_value = {"Events": []}

        # Create test data
        users = [User(id="user1", name="john.doe", email="john@example.com")]
        accounts = [
            AWSAccount(id="123456789012", name="Prod", email="prod@example.com")
        ]
        roles = [
            Role(
                name="ReadOnly",
                arn="arn:aws:sso:::permissionSet/ps-123",
                description="Read access",
            )
        ]
        assignments = [
            {
                "account_id": "123456789012",
                "permission_set_arn": "arn:aws:sso:::permissionSet/ps-123",
                "principal_type": "USER",
                "principal_id": "user1",
            }
        ]

        analyzer = PermissionAnalyzer()
        result = analyzer.analyze_permissions(users, accounts, roles, assignments)

        # Should return analysis results without AWS connections
        assert isinstance(result, list)

    @patch("src.permission_analyzer.aws_clients")
    def test_get_user_activity(self, mock_aws_clients):
        """Test get_user_activity method with mocked CloudTrail response."""
        mock_cloudtrail = Mock()
        mock_aws_clients.cloudtrail = mock_cloudtrail

        # Mock CloudTrail lookup_events response
        mock_cloudtrail.lookup_events.return_value = {
            "Events": [
                {
                    "EventTime": "2024-01-15T10:30:00Z",
                    "EventName": "AssumeRoleWithSAML",
                    "Username": "john.doe@example.com",
                    "Resources": [
                        {
                            "ResourceType": "AWS::IAM::Role",
                            "ResourceName": "arn:aws:iam::123456789012:role/aws-reserved/sso.amazonaws.com/ReadOnlyRole",
                        }
                    ],
                }
            ]
        }

        analyzer = PermissionAnalyzer()
        activity = analyzer.get_user_activity("john.doe@example.com", days=30)

        assert isinstance(activity, list)
        assert len(activity) == 1
        assert activity[0]["EventName"] == "AssumeRoleWithSAML"

    @patch("src.permission_analyzer.aws_clients")
    def test_analyze_unused_permissions(self, mock_aws_clients):
        """Test analyze_unused_permissions method."""
        mock_sso_admin = Mock()
        mock_cloudtrail = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.cloudtrail = mock_cloudtrail
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        # Mock permission set policies
        mock_sso_admin.get_inline_policy_for_permission_set.return_value = {
            "InlinePolicy": ""
        }
        mock_sso_admin.list_managed_policies_in_permission_set.return_value = {
            "AttachedManagedPolicies": [
                {
                    "Name": "PowerUserAccess",
                    "Arn": "arn:aws:iam::aws:policy/PowerUserAccess",
                }
            ]
        }
        mock_sso_admin.list_customer_managed_policy_references_in_permission_set.return_value = {
            "CustomerManagedPolicyReferences": []
        }

        # Mock CloudTrail response (no recent activity)
        mock_cloudtrail.lookup_events.return_value = {"Events": []}

        # Create test data
        users = [User(id="user1", name="john.doe", email="john@example.com")]
        assignments = [
            {
                "account_id": "123456789012",
                "permission_set_arn": "arn:aws:sso:::permissionSet/ps-123",
                "principal_type": "USER",
                "principal_id": "user1",
            }
        ]

        analyzer = PermissionAnalyzer()
        unused = analyzer.analyze_unused_permissions(users, assignments, days=90)

        # Should return list of potentially unused permissions
        assert isinstance(unused, list)

    @patch("src.permission_analyzer.aws_clients")
    def test_get_permission_boundaries(self, mock_aws_clients):
        """Test get_permission_boundaries method."""
        mock_sso_admin = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        permission_set_arn = "arn:aws:sso:::permissionSet/ps-123"

        # Mock permissions boundary response
        mock_sso_admin.get_permissions_boundary_for_permission_set.return_value = {
            "PermissionsBoundary": {
                "ManagedPolicyArn": "arn:aws:iam::123456789012:policy/DeveloperBoundary"
            }
        }

        analyzer = PermissionAnalyzer()
        boundary = analyzer.get_permission_boundaries(permission_set_arn)

        assert boundary is not None
        assert "ManagedPolicyArn" in boundary

    @patch("src.permission_analyzer.aws_clients")
    def test_get_permission_boundaries_none(self, mock_aws_clients):
        """Test get_permission_boundaries method when no boundary exists."""
        mock_sso_admin = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        permission_set_arn = "arn:aws:sso:::permissionSet/ps-123"

        # Mock no permissions boundary response
        from botocore.exceptions import ClientError

        mock_sso_admin.get_permissions_boundary_for_permission_set.side_effect = (
            ClientError(
                {"Error": {"Code": "ResourceNotFoundException"}},
                "GetPermissionsBoundaryForPermissionSet",
            )
        )

        analyzer = PermissionAnalyzer()
        boundary = analyzer.get_permission_boundaries(permission_set_arn)

        assert boundary is None

    def test_global_instance_exists(self):
        """Test that global permission_analyzer instance exists."""
        assert permission_analyzer is not None
        assert isinstance(permission_analyzer, PermissionAnalyzer)

    @patch("src.permission_analyzer.aws_clients")
    def test_error_handling(self, mock_aws_clients):
        """Test error handling in permission analysis."""
        mock_sso_admin = Mock()
        mock_aws_clients.sso_admin = mock_sso_admin
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-123"

        # Mock AWS API error
        from botocore.exceptions import ClientError

        mock_sso_admin.get_inline_policy_for_permission_set.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "GetInlinePolicyForPermissionSet",
        )

        analyzer = PermissionAnalyzer()

        # Should handle errors gracefully
        policies = analyzer.get_permission_set_policies(
            "arn:aws:sso:::permissionSet/ps-123"
        )

        # Should return empty or default structure on error
        assert isinstance(policies, dict)
