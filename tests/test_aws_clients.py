"""
Tests for AWS Clients module.

These tests use mocks to avoid real AWS connections.
"""

from unittest.mock import Mock, patch

from src.aws_clients import AWSClients, aws_clients


class TestAWSClients:
    """Test AWS clients initialization and configuration."""

    @patch("src.aws_clients.boto3.Session")
    def test_aws_clients_initialization(self, mock_session):
        """Test AWSClients initialization."""
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        clients = AWSClients()

        assert clients.session == mock_session_instance
        assert clients._sso_admin is None
        assert clients._identitystore is None
        assert clients._organizations is None

    @patch("src.aws_clients.boto3.Session")
    def test_sso_admin_client_lazy_loading(self, mock_session):
        """Test SSO Admin client is created lazily."""
        mock_session_instance = Mock()
        mock_sso_client = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.return_value = mock_sso_client

        clients = AWSClients()

        # First access should create the client
        result = clients.sso_admin
        assert result == mock_sso_client
        mock_session_instance.client.assert_called_once_with("sso-admin")

        # Second access should return cached client
        result2 = clients.sso_admin
        assert result2 == mock_sso_client
        # Should still be called only once (cached)
        mock_session_instance.client.assert_called_once()

    @patch("src.aws_clients.boto3.Session")
    def test_identitystore_client_lazy_loading(self, mock_session):
        """Test Identity Store client is created lazily."""
        mock_session_instance = Mock()
        mock_identity_client = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.return_value = mock_identity_client

        clients = AWSClients()

        result = clients.identitystore
        assert result == mock_identity_client
        mock_session_instance.client.assert_called_once_with("identitystore")

    @patch("src.aws_clients.boto3.Session")
    def test_organizations_client_lazy_loading(self, mock_session):
        """Test Organizations client is created lazily."""
        mock_session_instance = Mock()
        mock_orgs_client = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.return_value = mock_orgs_client

        clients = AWSClients()

        result = clients.organizations
        assert result == mock_orgs_client
        mock_session_instance.client.assert_called_once_with("organizations")

    @patch("src.aws_clients.boto3.Session")
    def test_cloudtrail_client_lazy_loading(self, mock_session):
        """Test CloudTrail client is created lazily."""
        mock_session_instance = Mock()
        mock_cloudtrail_client = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.return_value = mock_cloudtrail_client

        clients = AWSClients()

        result = clients.cloudtrail
        assert result == mock_cloudtrail_client
        mock_session_instance.client.assert_called_once_with("cloudtrail")

    @patch("src.aws_clients.boto3.Session")
    def test_instance_arn_property(self, mock_session):
        """Test instance ARN property retrieval."""
        mock_session_instance = Mock()
        mock_sso_client = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.return_value = mock_sso_client

        # Mock the list_instances response
        mock_sso_client.list_instances.return_value = {
            "Instances": [
                {
                    "InstanceArn": "arn:aws:sso:::instance/ssoins-1234567890abcdef",
                    "IdentityStoreId": "d-1234567890",
                }
            ]
        }

        clients = AWSClients()

        result = clients.instance_arn
        assert result == "arn:aws:sso:::instance/ssoins-1234567890abcdef"
        mock_sso_client.list_instances.assert_called_once()

    @patch("src.aws_clients.boto3.Session")
    def test_identity_store_id_property(self, mock_session):
        """Test identity store ID property retrieval."""
        mock_session_instance = Mock()
        mock_sso_client = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.return_value = mock_sso_client

        # Mock the list_instances response
        mock_sso_client.list_instances.return_value = {
            "Instances": [
                {
                    "InstanceArn": "arn:aws:sso:::instance/ssoins-1234567890abcdef",
                    "IdentityStoreId": "d-1234567890",
                }
            ]
        }

        clients = AWSClients()

        result = clients.identity_store_id
        assert result == "d-1234567890"
        mock_sso_client.list_instances.assert_called_once()

    @patch("src.aws_clients.boto3.Session")
    def test_global_instance_exists(self, mock_session):
        """Test that global aws_clients instance exists."""
        from src.aws_clients import _AWSClientsProxy

        assert aws_clients is not None
        assert isinstance(aws_clients, _AWSClientsProxy)

        # Test that the proxy can access AWSClients methods
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        # This should work through the proxy
        assert hasattr(aws_clients, "session")
