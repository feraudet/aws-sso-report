"""
Data Collector

This module handles the collection of data from AWS services including
users, groups, accounts, permission sets, and assignments.
"""

from typing import Dict, List, Set, Tuple

from .aws_clients import aws_clients
from .data_models import AWSAccount, Role, User, UserAccountRoleGroup, UserSummary
from .permission_analyzer_v2 import permission_analyzer_v2


class DataCollector:
    """Collects data from AWS IAM Identity Center and Organizations."""

    def __init__(self):
        self.sso_admin = aws_clients.sso_admin
        self.identitystore = aws_clients.identitystore
        self.organizations = aws_clients.organizations
        self.instance_arn = aws_clients.instance_arn
        self.identity_store_id = aws_clients.identity_store_id

        # Caches
        self._users_cache = None
        self._groups_cache = None
        self._accounts_cache = None
        self._permission_sets_cache = None
        self._assignments_cache = None
        self._group_memberships_cache = None

    def collect_all_data(self) -> Tuple[List[UserAccountRoleGroup], List[UserSummary]]:
        """
        Collect all data and return user-account-role assignments and user summaries.

        Returns:
            Tuple of (user_account_roles, user_summaries)
        """
        print("Collecting AWS data...")

        # Load all base data
        users = self.get_users()
        accounts = self.get_accounts()
        permission_sets = self.get_permission_sets()
        assignments = self.get_assignments()
        group_memberships = self.get_group_memberships()

        print(
            f"Found {len(users)} users, {len(accounts)} accounts, {len(permission_sets)} permission sets"
        )

        # Process each user
        user_account_roles = []
        user_summaries = []

        for idx, user_data in enumerate(users, 1):
            # Get user's account-role assignments with responsible groups first
            temp_user = User(
                id=user_data["UserId"],
                username=user_data.get(
                    "UserName", user_data.get("DisplayName", user_data["UserId"])
                ),
                display_name=user_data.get("DisplayName"),
                groups=self._get_user_groups(user_data["UserId"], group_memberships),
            )

            user_assignments_with_groups = self._get_user_assignments_with_groups(
                temp_user, assignments, group_memberships
            )

            # Infer user status based on assignments
            user_status = "Enabled" if user_assignments_with_groups else "Disabled"

            # Extract primary email address
            user_email = self._get_user_primary_email(user_data)

            # Create final user object with inferred status
            user = User(
                id=user_data["UserId"],
                username=user_data.get(
                    "UserName", user_data.get("DisplayName", user_data["UserId"])
                ),
                display_name=user_data.get("DisplayName"),
                email=user_email,
                groups=self._get_user_groups(user_data["UserId"], group_memberships),
                status=user_status,
            )

            print(
                f"[{idx}/{len(users)}] Processing user: {user.name} (Status: {user.status})"
            )

            # Create UserAccountRoleGroup objects
            aws_accounts_json = []
            accounts_roles_for_json = {}

            for assignment_info in user_assignments_with_groups:
                account = accounts[assignment_info["account_id"]]
                role = permission_sets[assignment_info["role_arn"]]

                # Create UserAccountRoleGroup
                user_account_role_group = UserAccountRoleGroup(
                    user=user,
                    account=account,
                    role=role,
                    responsible_group=assignment_info["responsible_group"],
                    assignment_type=assignment_info["assignment_type"],
                )
                user_account_roles.append(user_account_role_group)

                # Build JSON structure (grouped by account for JSON export)
                account_id = assignment_info["account_id"]
                if account_id not in accounts_roles_for_json:
                    accounts_roles_for_json[account_id] = {
                        "account": account,
                        "roles": {},
                    }

                role_arn = assignment_info["role_arn"]
                if role_arn not in accounts_roles_for_json[account_id]["roles"]:
                    accounts_roles_for_json[account_id]["roles"][role_arn] = {
                        "name": role.name,
                        "access_level": role.access_level.value,
                        "read_score": role.scores.read_score,
                        "write_score": role.scores.write_score,
                        "admin_score": role.scores.admin_score,
                    }

            # Build JSON structure
            for account_data in accounts_roles_for_json.values():
                aws_accounts_json.append(
                    {
                        "account_name": account_data["account"].name,
                        "account_id": account_data["account"].id,
                        "roles": list(account_data["roles"].values()),
                    }
                )

            # Create user summary for JSON
            user_summary = UserSummary(user=user, accounts=aws_accounts_json)
            user_summaries.append(user_summary)

            # Handle users without roles
            if not user_assignments_with_groups:
                empty_user_account_role_group = UserAccountRoleGroup(
                    user=user,
                    account=AWSAccount(id="", name=""),
                    role=Role(name="", arn=""),
                    responsible_group="NONE",
                    assignment_type="NONE",
                )
                user_account_roles.append(empty_user_account_role_group)

        return user_account_roles, user_summaries

    def _get_user_primary_email(self, user_data: Dict) -> str:
        """
        Extract the primary email address from user data.

        Args:
            user_data: User data dictionary from AWS Identity Store

        Returns:
            Primary email address or "N/A" if not found
        """
        try:
            emails = user_data.get("Emails", [])

            if not emails:
                return "N/A"

            # Look for primary email first
            for email_obj in emails:
                if email_obj.get("Primary", False):
                    return email_obj.get("Value", "N/A")

            # If no primary email found, return the first email
            if emails:
                return emails[0].get("Value", "N/A")

            return "N/A"

        except (KeyError, TypeError, IndexError) as e:
            print(f"Warning: Could not extract email from user data: {e}")
            return "N/A"

    def get_users(self) -> List[Dict]:
        """Get all users from Identity Store."""
        if self._users_cache is not None:
            return self._users_cache

        users = []
        paginator = self.identitystore.get_paginator("list_users")

        for page in paginator.paginate(IdentityStoreId=self.identity_store_id):
            users.extend(page["Users"])

        self._users_cache = users
        return users

    def get_groups(self) -> List[Dict]:
        """Get all groups from Identity Store."""
        if self._groups_cache is not None:
            return self._groups_cache

        groups = []
        paginator = self.identitystore.get_paginator("list_groups")

        for page in paginator.paginate(IdentityStoreId=self.identity_store_id):
            groups.extend(page["Groups"])

        self._groups_cache = groups
        return groups

    def get_accounts(self) -> Dict[str, AWSAccount]:
        """Get all AWS accounts from Organizations."""
        if self._accounts_cache is not None:
            return self._accounts_cache

        accounts = {}
        paginator = self.organizations.get_paginator("list_accounts")

        for page in paginator.paginate():
            for account_data in page["Accounts"]:
                account = AWSAccount(id=account_data["Id"], name=account_data["Name"])
                accounts[account.id] = account

        self._accounts_cache = accounts
        return accounts

    def get_permission_sets(self) -> Dict[str, Role]:
        """Get all permission sets with analysis."""
        if self._permission_sets_cache is not None:
            return self._permission_sets_cache

        permission_sets = {}
        paginator = self.sso_admin.get_paginator("list_permission_sets")

        for page in paginator.paginate(InstanceArn=self.instance_arn):
            for ps_arn in page["PermissionSets"]:
                # Get permission set details
                ps_details = self.sso_admin.describe_permission_set(
                    InstanceArn=self.instance_arn, PermissionSetArn=ps_arn
                )
                ps_name = ps_details["PermissionSet"]["Name"]

                # Create role with analysis using new scoring system
                role = permission_analyzer_v2.create_role_from_permission_set(
                    ps_arn, ps_name
                )
                permission_sets[ps_arn] = role

        self._permission_sets_cache = permission_sets
        return permission_sets

    def get_assignments(self) -> Dict[Tuple[str, str], List[Dict]]:
        """Get all account assignments."""
        if self._assignments_cache is not None:
            return self._assignments_cache

        assignments = {}
        accounts = self.get_accounts()
        permission_sets = self.get_permission_sets()

        for account_id in accounts.keys():
            for ps_arn in permission_sets.keys():
                try:
                    paginator = self.sso_admin.get_paginator("list_account_assignments")

                    for page in paginator.paginate(
                        InstanceArn=self.instance_arn,
                        AccountId=account_id,
                        PermissionSetArn=ps_arn,
                    ):
                        if page["AccountAssignments"]:
                            key = (account_id, ps_arn)
                            assignments[key] = page["AccountAssignments"]

                except Exception:  # nosec B112
                    # Skip if no assignments for this combination
                    continue

        self._assignments_cache = assignments
        return assignments

    def get_group_memberships(self) -> Dict[str, Set[str]]:
        """Get all group memberships (group_id -> set of user_ids)."""
        if self._group_memberships_cache is not None:
            return self._group_memberships_cache

        group_memberships = {}
        groups = self.get_groups()

        for group in groups:
            group_id = group["GroupId"]
            members = set()

            paginator = self.identitystore.get_paginator("list_group_memberships")
            for page in paginator.paginate(
                IdentityStoreId=self.identity_store_id, GroupId=group_id
            ):
                for membership in page["GroupMemberships"]:
                    member = membership["MemberId"]
                    if member.get("UserId"):
                        members.add(member["UserId"])

            group_memberships[group_id] = members

        self._group_memberships_cache = group_memberships
        return group_memberships

    def _get_user_groups(
        self, user_id: str, group_memberships: Dict[str, Set[str]]
    ) -> List[str]:
        """Get groups for a specific user."""
        user_groups = []
        groups = self.get_groups()

        for group in groups:
            group_id = group["GroupId"]
            if user_id in group_memberships.get(group_id, set()):
                user_groups.append(group["DisplayName"])

        return user_groups

    def _get_user_assignments_with_groups(
        self, user: User, assignments: Dict, group_memberships: Dict
    ) -> List[Dict[str, str]]:
        """Get account-role assignments for a user with responsible group information."""
        user_assignments = []

        # Get user's group IDs and names mapping
        user_group_ids = {}  # group_id -> group_name
        groups = self.get_groups()
        for group in groups:
            group_id = group["GroupId"]
            if user.id in group_memberships.get(group_id, set()):
                user_group_ids[group_id] = group["DisplayName"]

        # Find assignments (direct and via groups)
        for (account_id, permission_set_arn), assigns in assignments.items():
            for assignment in assigns:
                # Direct user assignment
                if (
                    assignment["PrincipalType"] == "USER"
                    and assignment["PrincipalId"] == user.id
                ):
                    user_assignments.append(
                        {
                            "account_id": account_id,
                            "role_arn": permission_set_arn,
                            "responsible_group": "DIRECT",
                            "assignment_type": "USER",
                        }
                    )

                # Group-based assignment
                elif (
                    assignment["PrincipalType"] == "GROUP"
                    and assignment["PrincipalId"] in user_group_ids
                ):
                    group_name = user_group_ids[assignment["PrincipalId"]]
                    user_assignments.append(
                        {
                            "account_id": account_id,
                            "role_arn": permission_set_arn,
                            "responsible_group": group_name,
                            "assignment_type": "GROUP",
                        }
                    )

        return user_assignments


# Global instance for convenience (lazy initialization)
_data_collector_instance = None


def get_data_collector() -> DataCollector:
    """Get or create the global data collector instance."""
    global _data_collector_instance
    if _data_collector_instance is None:
        _data_collector_instance = DataCollector()
    return _data_collector_instance


# For backward compatibility, create a property-like access
class _DataCollectorProxy:
    """Proxy class to provide backward compatibility for data_collector global."""

    def __getattr__(self, name):
        return getattr(get_data_collector(), name)


data_collector = _DataCollectorProxy()
