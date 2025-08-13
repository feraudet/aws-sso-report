"""
Permission Analyzer V2 - Configuration-Driven

This module handles the analysis of IAM Permission Sets using a flexible
configuration system for accurate risk assessment and scoring.
"""

import json
from typing import List, Tuple

from .aws_clients import aws_clients
from .data_models import AccessLevel, PermissionScores, Role
from .permission_scoring_config import get_scoring_config


class PermissionAnalyzerV2:
    """Analyzes Permission Sets using configuration-driven scoring."""

    def __init__(self):
        self.sso_admin = aws_clients.sso_admin
        self.instance_arn = aws_clients.instance_arn
        self._cache = {}
        self.scoring_config = get_scoring_config()

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

            # Analyze policies using configuration
            access_level, scores = self._analyze_policies_v2(
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

    def _get_managed_policies(self, permission_set_arn: str) -> List[dict]:
        """Get managed policies attached to a Permission Set."""
        try:
            paginator = self.sso_admin.get_paginator(
                "list_managed_policies_in_permission_set"
            )
            policies = []

            for page in paginator.paginate(
                InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
            ):
                policies.extend(page["AttachedManagedPolicies"])

            return policies
        except Exception:
            return []

    def _get_inline_policy(self, permission_set_arn: str) -> str:
        """Get inline policy for a Permission Set."""
        try:
            resp = self.sso_admin.get_inline_policy_for_permission_set(
                InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
            )
            return resp.get("InlinePolicy")
        except self.sso_admin.exceptions.ResourceNotFoundException:
            return None

    def _analyze_policies_v2(
        self, managed_policies: List[dict], inline_policy: str
    ) -> Tuple[AccessLevel, PermissionScores]:
        """Analyze policies using configuration-driven approach."""

        # Initialize scores
        final_scores = PermissionScores()
        all_actions = []
        access_level = AccessLevel.READ_ONLY
        justification_parts = []

        # Analyze managed policies
        for policy in managed_policies:
            policy_name = policy["Name"]
            (
                read_score,
                write_score,
                admin_score,
            ) = self.scoring_config.score_managed_policy(policy_name)

            # Update scores (take maximum)
            final_scores.read_score = max(final_scores.read_score, read_score)
            final_scores.write_score = max(final_scores.write_score, write_score)
            final_scores.admin_score = max(final_scores.admin_score, admin_score)

            # Add managed policy justification
            if read_score > 0 or write_score > 0 or admin_score > 0:
                justification_parts.append(
                    f"Managed policy '{policy_name}': read={read_score}, write={write_score}, admin={admin_score}"
                )

            print(
                f"Managed policy '{policy_name}': read={read_score}, write={write_score}, admin={admin_score}"
            )

        # Analyze inline policy
        if inline_policy:
            inline_actions = self._extract_actions_from_policy(inline_policy)
            all_actions.extend(inline_actions)

            if inline_actions:
                (
                    inline_access_level,
                    inline_scores,
                    high_risk_actions,
                ) = self.scoring_config.analyze_actions(inline_actions)

                # Update scores (take maximum)
                final_scores.read_score = max(
                    final_scores.read_score, inline_scores.read_score
                )
                final_scores.write_score = max(
                    final_scores.write_score, inline_scores.write_score
                )
                final_scores.admin_score = max(
                    final_scores.admin_score, inline_scores.admin_score
                )

                # Add inline policy justification (use the detailed justification from analyze_actions)
                if inline_scores.justification:
                    justification_parts.append(
                        f"Inline policy analysis: {inline_scores.justification}"
                    )

                # Update access level (take highest)
                if inline_access_level.value == "Admin":
                    access_level = AccessLevel.FULL_ADMIN
                elif (
                    inline_access_level.value == "Read Write"
                    and access_level != AccessLevel.FULL_ADMIN
                ):
                    access_level = AccessLevel.READ_WRITE

                # Log high-risk actions for monitoring
                if high_risk_actions:
                    print(f"High-risk actions detected: {high_risk_actions}")

        # If we only have managed policies and no inline policy, generate a basic justification
        if not all_actions and managed_policies:
            policy_names = [p["Name"] for p in managed_policies]
            if len(policy_names) == 1:
                justification_parts.append(f"Single managed policy: {policy_names[0]}")
            else:
                justification_parts.append(
                    f"Multiple managed policies: {', '.join(policy_names[:3])}"
                )
                if len(policy_names) > 3:
                    justification_parts.append(f"... and {len(policy_names) - 3} more")

        # Determine final access level based on scores
        if final_scores.admin_score >= 5:
            access_level = AccessLevel.FULL_ADMIN
        elif final_scores.write_score >= 5:
            access_level = AccessLevel.READ_WRITE
        elif final_scores.read_score > 0:
            access_level = AccessLevel.READ_ONLY
        else:
            access_level = AccessLevel.UNKNOWN

        # Create a human-readable justification
        if justification_parts:
            # For admin roles with managed policies, create a clear summary
            if any("AdministratorAccess" in part for part in justification_parts):
                final_scores.justification = (
                    "Full administrative access via AdministratorAccess managed policy"
                )
                if any("Inline policy" in part for part in justification_parts):
                    final_scores.justification += " plus additional inline permissions"
            elif any("ReadOnlyAccess" in part for part in justification_parts):
                # Check if there are additional permissions beyond ReadOnlyAccess
                has_additional_permissions = (
                    final_scores.write_score > 0 or final_scores.admin_score > 0
                )

                if has_additional_permissions:
                    # List additional permission sources
                    additional_sources = []
                    for part in justification_parts:
                        if "ReadOnlyAccess" not in part:
                            if "Managed policy" in part:
                                policy_name = (
                                    part.split("'")[1]
                                    if "'" in part
                                    else "managed policy"
                                )
                                additional_sources.append(
                                    f"'{policy_name}' managed policy"
                                )
                            elif "Inline policy" in part:
                                additional_sources.append("inline policy")

                    if additional_sources:
                        final_scores.justification = (
                            f"Read-only access via ReadOnlyAccess managed policy, "
                            f"plus write/admin permissions from {', '.join(additional_sources)}"
                        )
                    else:
                        final_scores.justification = (
                            "Read-only access via ReadOnlyAccess managed policy, "
                            "plus additional write/admin permissions"
                        )
                else:
                    final_scores.justification = (
                        "Read-only access via ReadOnlyAccess managed policy"
                    )
            elif (
                len(justification_parts) == 1
                and "Single managed policy" in justification_parts[0]
            ):
                # Extract policy name for single managed policy
                policy_name = (
                    justification_parts[0].split(": ")[1]
                    if ": " in justification_parts[0]
                    else "managed policy"
                )
                final_scores.justification = (
                    f"Permissions granted via {policy_name} managed policy"
                )
            else:
                # For complex cases, create a readable summary
                managed_policies = [
                    p for p in justification_parts if "Managed policy" in p
                ]
                inline_policies = [
                    p for p in justification_parts if "Inline policy" in p
                ]

                if managed_policies and inline_policies:
                    final_scores.justification = f"Combined permissions from {len(managed_policies)} managed policy(ies) and custom inline policy"
                elif managed_policies:
                    final_scores.justification = (
                        f"Permissions from {len(managed_policies)} managed policy(ies)"
                    )
                elif inline_policies:
                    final_scores.justification = "Custom permissions via inline policy"
                else:
                    final_scores.justification = "Mixed permission sources"
        else:
            final_scores.justification = (
                f"Access level: {access_level.value} - No detailed analysis available"
            )

        return access_level, final_scores

    def _extract_actions_from_policy(self, policy_json: str) -> List[str]:
        """Extract all actions from an inline policy JSON."""
        actions = []

        try:
            policy_doc = json.loads(policy_json)
            statements = policy_doc.get("Statement", [])

            if isinstance(statements, dict):
                statements = [statements]

            for statement in statements:
                if isinstance(statement, dict):
                    # Only process Allow statements
                    effect = statement.get("Effect", "").lower()
                    if effect != "allow":
                        continue

                    statement_actions = statement.get("Action", [])
                    if isinstance(statement_actions, str):
                        statement_actions = [statement_actions]

                    actions.extend(statement_actions)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse inline policy: {e}")

        return actions

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

    def get_detailed_analysis(self, permission_set_arn: str) -> dict:
        """Get detailed analysis including risk explanations."""
        try:
            managed_policies = self._get_managed_policies(permission_set_arn)
            inline_policy = self._get_inline_policy(permission_set_arn)

            analysis = {
                "permission_set_arn": permission_set_arn,
                "managed_policies": [],
                "inline_actions": [],
                "high_risk_actions": [],
                "risk_explanations": {},
            }

            # Analyze managed policies
            for policy in managed_policies:
                policy_name = policy["Name"]
                (
                    read_score,
                    write_score,
                    admin_score,
                ) = self.scoring_config.score_managed_policy(policy_name)

                analysis["managed_policies"].append(
                    {
                        "name": policy_name,
                        "arn": policy.get("Arn", ""),
                        "scores": {
                            "read": read_score,
                            "write": write_score,
                            "admin": admin_score,
                        },
                    }
                )

            # Analyze inline policy
            if inline_policy:
                actions = self._extract_actions_from_policy(inline_policy)
                analysis["inline_actions"] = actions

                for action in actions:
                    _, _, _, risk_level = self.scoring_config.score_action(action)
                    if risk_level in ["critical", "high"]:
                        analysis["high_risk_actions"].append(action)

                    analysis["risk_explanations"][
                        action
                    ] = self.scoring_config.get_risk_explanation(action)

            return analysis

        except Exception as e:
            return {"error": f"Could not analyze permission set: {e}"}


# Global instance for convenience (lazy initialization)
_permission_analyzer_v2_instance = None


def get_permission_analyzer_v2() -> PermissionAnalyzerV2:
    """Get or create the global permission analyzer V2 instance."""
    global _permission_analyzer_v2_instance
    if _permission_analyzer_v2_instance is None:
        _permission_analyzer_v2_instance = PermissionAnalyzerV2()
    return _permission_analyzer_v2_instance


# For backward compatibility, create a proxy class
class _PermissionAnalyzerV2Proxy:
    """Proxy class to provide backward compatibility for permission_analyzer global."""

    def __getattr__(self, name):
        return getattr(get_permission_analyzer_v2(), name)


permission_analyzer_v2 = _PermissionAnalyzerV2Proxy()
