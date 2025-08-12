"""
Permission Analyzer

This module handles the analysis of IAM Permission Sets to determine
access levels and calculate permission scores.
"""

import json
from typing import Tuple
from .aws_clients import aws_clients
from .data_models import AccessLevel, PermissionScores, Role


class PermissionAnalyzer:
    """Analyzes Permission Sets to determine access levels and scores."""

    def __init__(self):
        self.sso_admin = aws_clients.sso_admin
        self.instance_arn = aws_clients.instance_arn
        self._cache = {}

    def analyze_permission_set(
        self, permission_set_arn: str
    ) -> Tuple[AccessLevel, PermissionScores]:
        """
        Analyze a Permission Set to determine its access level and scores.

        Returns:
            Tuple of (access_level, permission_scores)
        """
        if permission_set_arn in self._cache:
            return self._cache[permission_set_arn]

        try:
            # Get managed policies
            managed_policies = self._get_managed_policies(permission_set_arn)

            # Get inline policy
            inline_policy = self._get_inline_policy(permission_set_arn)

            # Analyze policies
            access_level, scores = self._analyze_policies(
                managed_policies, inline_policy
            )

            # Cache result
            result = (access_level, scores)
            self._cache[permission_set_arn] = result

            return result

        except Exception as e:
            print(
                f"Warning: Could not analyze permissions for {permission_set_arn}: {e}"
            )
            return AccessLevel.UNKNOWN, PermissionScores()

    def _get_managed_policies(self, permission_set_arn: str) -> list:
        """Get managed policies attached to a Permission Set."""
        managed_policies = []
        paginator = self.sso_admin.get_paginator(
            "list_managed_policies_in_permission_set"
        )

        for page in paginator.paginate(
            InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
        ):
            managed_policies.extend(page["AttachedManagedPolicies"])

        return managed_policies

    def _get_inline_policy(self, permission_set_arn: str) -> str:
        """Get inline policy for a Permission Set."""
        try:
            resp = self.sso_admin.get_inline_policy_for_permission_set(
                InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
            )
            return resp.get("InlinePolicy")
        except self.sso_admin.exceptions.ResourceNotFoundException:
            return None

    def _analyze_policies(
        self, managed_policies: list, inline_policy: str
    ) -> Tuple[AccessLevel, PermissionScores]:
        """Analyze managed and inline policies to determine access level and scores."""
        scores = PermissionScores()
        has_write_actions = False
        has_admin_actions = False
        has_wildcard_actions = False

        # Analyze managed policies
        for policy in managed_policies:
            policy_name = policy["Name"]

            # Known admin policies
            admin_policies = [
                "AdministratorAccess",
                "PowerUserAccess",
                "IAMFullAccess",
                "OrganizationsFullAccess",
            ]

            if any(admin_policy in policy_name for admin_policy in admin_policies):
                has_admin_actions = True
                scores.admin_score = 10
                scores.write_score = 10
                scores.read_score = 10
                break

            # Check for read-only policies
            if "ReadOnly" in policy_name or "ViewOnly" in policy_name:
                scores.read_score = max(scores.read_score, 8)
                continue
            else:
                # Other policies likely have write permissions
                has_write_actions = True
                scores.read_score = max(scores.read_score, 6)
                scores.write_score = max(scores.write_score, 6)

        # Analyze inline policy
        if inline_policy:
            write_actions, admin_actions, wildcard_actions = (
                self._analyze_inline_policy(inline_policy)
            )

            if wildcard_actions:
                has_wildcard_actions = True
                has_admin_actions = True
                scores.admin_score = 10
                scores.write_score = 10
                scores.read_score = 10
            elif admin_actions:
                has_admin_actions = True
                scores.admin_score = max(scores.admin_score, 8)
                scores.write_score = max(scores.write_score, 8)
                scores.read_score = max(scores.read_score, 8)
            elif write_actions:
                has_write_actions = True
                scores.write_score = max(scores.write_score, 7)
                scores.read_score = max(scores.read_score, 5)
            else:
                scores.read_score = max(scores.read_score, 4)

        # Ensure minimum scores based on detected actions
        if has_admin_actions or has_wildcard_actions:
            scores.admin_score = max(scores.admin_score, 8)
            scores.write_score = max(scores.write_score, 8)
            scores.read_score = max(scores.read_score, 8)
        elif has_write_actions:
            scores.write_score = max(scores.write_score, 6)
            scores.read_score = max(scores.read_score, 5)
        elif scores.read_score == 0:
            scores.read_score = 3

        # Determine access level
        if has_admin_actions or has_wildcard_actions:
            access_level = AccessLevel.FULL_ADMIN
        elif has_write_actions:
            access_level = AccessLevel.READ_WRITE
        else:
            access_level = AccessLevel.READ_ONLY

        return access_level, scores

    def _analyze_inline_policy(self, inline_policy: str) -> Tuple[bool, bool, bool]:
        """Analyze inline policy JSON to detect action types."""
        has_write_actions = False
        has_admin_actions = False
        has_wildcard_actions = False

        try:
            policy_doc = json.loads(inline_policy)
            statements = policy_doc.get("Statement", [])

            if isinstance(statements, dict):
                statements = [statements]

            for statement in statements:
                if isinstance(statement, dict):
                    actions = statement.get("Action", [])
                    if isinstance(actions, str):
                        actions = [actions]

                    for action in actions:
                        if action == "*" or action.endswith(":*"):
                            has_wildcard_actions = True
                            break
                        elif any(
                            admin_action in action.lower()
                            for admin_action in ["*", "admin", "full", "manage"]
                        ):
                            has_admin_actions = True
                        elif any(
                            write_action in action.lower()
                            for write_action in [
                                "create",
                                "delete",
                                "put",
                                "update",
                                "modify",
                                "attach",
                                "detach",
                            ]
                        ):
                            has_write_actions = True

                    if has_wildcard_actions:
                        break

        except (json.JSONDecodeError, KeyError):
            pass

        return has_write_actions, has_admin_actions, has_wildcard_actions

    def create_role_from_permission_set(
        self, permission_set_arn: str, permission_set_name: str
    ) -> Role:
        """Create a Role object from a Permission Set with analysis."""
        access_level, scores = self.analyze_permission_set(permission_set_arn)

        return Role(
            name=permission_set_name,
            arn=permission_set_arn,
            access_level=access_level,
            scores=scores,
        )


# Global instance for convenience
permission_analyzer = PermissionAnalyzer()
