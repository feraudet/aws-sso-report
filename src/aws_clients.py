"""
AWS Clients Configuration and Management

This module handles the initialization and configuration of AWS clients
required for IAM Identity Center reporting.
"""

from typing import Any, Dict

import boto3


class AWSClients:
    """Manages AWS service clients for IAM Identity Center operations."""

    def __init__(self):
        """Initialize AWS clients using default session."""
        self.session = boto3.Session()
        self._sso_admin = None
        self._identitystore = None
        self._organizations = None
        self._instance_arn = None
        self._identity_store_id = None

    @property
    def sso_admin(self):
        """Get SSO Admin client."""
        if self._sso_admin is None:
            self._sso_admin = self.session.client("sso-admin")
        return self._sso_admin

    @property
    def identitystore(self):
        """Get Identity Store client."""
        if self._identitystore is None:
            self._identitystore = self.session.client("identitystore")
        return self._identitystore

    @property
    def organizations(self):
        """Get Organizations client."""
        if self._organizations is None:
            self._organizations = self.session.client("organizations")
        return self._organizations

    @property
    def cloudtrail(self):
        """Get CloudTrail client."""
        if not hasattr(self, "_cloudtrail") or self._cloudtrail is None:
            self._cloudtrail = self.session.client("cloudtrail")
        return self._cloudtrail

    @property
    def instance_arn(self) -> str:
        """Get SSO instance ARN."""
        if self._instance_arn is None:
            self._initialize_sso_instance()
        return self._instance_arn

    @property
    def identity_store_id(self) -> str:
        """Get Identity Store ID."""
        if self._identity_store_id is None:
            self._initialize_sso_instance()
        return self._identity_store_id

    def _initialize_sso_instance(self):
        """Initialize SSO instance ARN and Identity Store ID."""
        response = self.sso_admin.list_instances()
        if not response["Instances"]:
            raise ValueError("No SSO instances found")

        instance = response["Instances"][0]
        self._instance_arn = instance["InstanceArn"]
        self._identity_store_id = instance["IdentityStoreId"]

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about configured AWS clients."""
        return {
            "instance_arn": self.instance_arn,
            "identity_store_id": self.identity_store_id,
            "region": self.session.region_name or "us-east-1",
        }


# Global instance for backward compatibility (lazy initialization)
_aws_clients_instance = None


def get_aws_clients() -> AWSClients:
    """Get or create the global AWS clients instance."""
    global _aws_clients_instance
    if _aws_clients_instance is None:
        _aws_clients_instance = AWSClients()
    return _aws_clients_instance


# For backward compatibility, create a property-like access
class _AWSClientsProxy:
    """Proxy class to provide backward compatibility for aws_clients global."""

    def __getattr__(self, name):
        return getattr(get_aws_clients(), name)


aws_clients = _AWSClientsProxy()
