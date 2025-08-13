"""
Simplified tests for Data Collector module.

These tests verify basic functionality without AWS connections.
"""

from unittest.mock import Mock, patch

from src.data_collector import DataCollector


class TestDataCollectorSimple:
    """Test DataCollector class with simplified mocking."""

    @patch("src.data_collector.aws_clients")
    def test_data_collector_initialization(self, mock_aws_clients):
        """Test DataCollector initialization with mocked clients."""
        # Mock all AWS clients and properties
        mock_aws_clients.sso_admin = Mock()
        mock_aws_clients.identitystore = Mock()
        mock_aws_clients.organizations = Mock()
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-test"
        mock_aws_clients.identity_store_id = "d-test123"

        collector = DataCollector()

        assert collector.instance_arn == "arn:aws:sso:::instance/ssoins-test"
        assert collector.identity_store_id == "d-test123"
        assert collector._users_cache is None
        assert collector._accounts_cache is None
        assert collector._permission_sets_cache is None

    @patch("src.data_collector.aws_clients")
    def test_caching_behavior(self, mock_aws_clients):
        """Test that caching works properly."""
        # Mock all AWS clients and properties
        mock_aws_clients.sso_admin = Mock()
        mock_aws_clients.identitystore = Mock()
        mock_aws_clients.organizations = Mock()
        mock_aws_clients.instance_arn = "arn:aws:sso:::instance/ssoins-test"
        mock_aws_clients.identity_store_id = "d-test123"

        # Mock paginator for users
        mock_paginator = Mock()
        mock_aws_clients.identitystore.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {
                "Users": [
                    {
                        "UserId": "user1",
                        "UserName": "test.user",
                        "DisplayName": "Test User",
                        "Emails": [{"Value": "test@example.com", "Primary": True}],
                    }
                ]
            }
        ]

        collector = DataCollector()

        # First call should populate cache
        users1 = collector.get_users()
        assert len(users1) == 1
        assert collector._users_cache is not None

        # Second call should use cache
        users2 = collector.get_users()
        assert users1 == users2

        # Should only call AWS API once due to caching
        mock_aws_clients.identitystore.get_paginator.assert_called_once()

    @patch("src.data_collector.get_data_collector")
    def test_global_instance_proxy_exists(self, mock_get_data_collector):
        """Test that global data_collector proxy exists."""
        from src.data_collector import _DataCollectorProxy, data_collector

        # Mock the get_data_collector function to avoid AWS connections
        mock_collector = Mock()
        mock_get_data_collector.return_value = mock_collector

        assert data_collector is not None
        assert isinstance(data_collector, _DataCollectorProxy)

        # Test that the proxy has the expected methods
        assert hasattr(data_collector, "get_users")
        assert hasattr(data_collector, "get_accounts")
        assert hasattr(data_collector, "get_permission_sets")
        assert hasattr(data_collector, "collect_all_data")
