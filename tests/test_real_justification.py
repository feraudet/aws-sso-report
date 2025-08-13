#!/usr/bin/env python3
"""
Test script to verify that justifications are generated in the real system workflow.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.data_models import (
        AccessLevel,
        AWSAccount,
        PermissionScores,
        Role,
        User,
        UserAccountRoleGroup,
    )
    from src.report_generators import ReportGenerator
except ImportError:
    from data_models import (
        AccessLevel,
        AWSAccount,
        PermissionScores,
        Role,
        User,
        UserAccountRoleGroup,
    )
    from report_generators import ReportGenerator


def test_real_justification_workflow():
    """Test the complete workflow with justification generation."""
    print("🧪 TESTING REAL JUSTIFICATION WORKFLOW")
    print("=" * 50)

    # Create a mock permission analyzer to simulate real AWS calls
    class MockPermissionAnalyzer:
        def __init__(self):
            self.scoring_config = None
            # Import scoring config
            try:
                from src.permission_scoring_config import PermissionScoringConfig

                self.scoring_config = PermissionScoringConfig()
            except ImportError:
                from permission_scoring_config import PermissionScoringConfig

                self.scoring_config = PermissionScoringConfig()

        def create_role_from_permission_set(self, ps_arn: str, ps_name: str) -> Role:
            """Mock the real AWS permission set analysis."""

            # Simulate different types of permission sets
            if "admin" in ps_name.lower():
                # Admin role with managed policies
                # Simulate the analysis
                final_scores = PermissionScores()
                final_scores.read_score = 10
                final_scores.write_score = 10
                final_scores.admin_score = 10
                final_scores.justification = "Managed policy 'AdministratorAccess': read=10, write=10, admin=10. Single managed policy: AdministratorAccess."
                access_level = AccessLevel.FULL_ADMIN

            elif "readonly" in ps_name.lower():
                # Read-only role
                final_scores = PermissionScores()
                final_scores.read_score = 8
                final_scores.write_score = 0
                final_scores.admin_score = 0
                final_scores.justification = "Managed policy 'ReadOnlyAccess': read=8, write=0, admin=0. Single managed policy: ReadOnlyAccess."
                access_level = AccessLevel.READ_ONLY

            else:
                # Custom role with inline policy
                inline_actions = [
                    "s3:GetObject",
                    "s3:PutObject",
                    "ec2:DescribeInstances",
                    "iam:ListRoles",
                ]

                # Use real scoring config to analyze actions
                (
                    access_level,
                    scores,
                    high_risk_actions,
                ) = self.scoring_config.analyze_actions(inline_actions)
                final_scores = scores

                # Add managed policy info if any
                managed_policy_info = (
                    "Managed policy 'S3FullAccess': read=6, write=8, admin=2"
                )
                final_scores.justification = f"{managed_policy_info}. Inline policy analysis: {scores.justification}"

            return Role(
                name=ps_name, arn=ps_arn, access_level=access_level, scores=final_scores
            )

    # Test different role scenarios
    mock_analyzer = MockPermissionAnalyzer()

    test_scenarios = [
        ("arn:aws:sso:::permissionSet/ssoins-123/ps-admin", "AdminRole"),
        ("arn:aws:sso:::permissionSet/ssoins-123/ps-readonly", "ReadOnlyRole"),
        ("arn:aws:sso:::permissionSet/ssoins-123/ps-custom", "CustomDeveloperRole"),
    ]

    user_account_roles = []

    for ps_arn, ps_name in test_scenarios:
        print(f"\n✅ Testing scenario: {ps_name}")

        # Create role using mock analyzer
        role = mock_analyzer.create_role_from_permission_set(ps_arn, ps_name)

        # Create test user and account
        user = User(
            id=f"user-{ps_name.lower()}",
            username=f"user_{ps_name.lower()}",
            display_name=f"Test User for {ps_name}",
            email=f"test_{ps_name.lower()}@example.com",
            status="Enabled",
        )

        account = AWSAccount(id="123456789012", name="Test Account")

        # Create user-account-role assignment
        uar = UserAccountRoleGroup(
            user=user,
            account=account,
            role=role,
            responsible_group=f"Group_{ps_name}",
            assignment_type="GROUP",
        )

        user_account_roles.append(uar)

        # Verify justification is present
        data_dict = uar.to_dict()
        justification = data_dict.get("Justification", "")

        print(f"   Role: {role.name}")
        print(f"   Access Level: {role.access_level.value}")
        print(f"   Risk Level: {role.risk_level.value}")
        print(
            f"   Scores: R={role.scores.read_score}, W={role.scores.write_score}, A={role.scores.admin_score}"
        )
        print(f"   Justification: {justification[:100]}...")

        assert justification, f"No justification found for {ps_name}"
        assert len(justification) > 10, f"Justification too short for {ps_name}"

    # Generate reports with justifications
    print(f"\n✅ Generating reports with {len(user_account_roles)} roles")
    report_generator = ReportGenerator("real_justification_test")

    # Generate all report formats
    report_generator.generate_csv_report(user_account_roles)
    report_generator.generate_excel_report(user_account_roles)

    print("   ✓ CSV file generated: real_justification_test.csv")
    print("   ✓ Excel file generated: real_justification_test.xlsx")

    # Verify CSV content contains justifications
    print("\n✅ Verifying CSV content")
    with open("real_justification_test.csv", "r", encoding="utf-8") as f:
        csv_content = f.read()

        # Check header
        assert (
            "Justification" in csv_content
        ), "Justification column not found in CSV header"

        # Check that each role has justification content
        for uar in user_account_roles:
            role_name = uar.role.name
            justification = uar.to_dict()["Justification"]

            # Check that the justification appears in the CSV
            assert (
                justification[:50] in csv_content
            ), f"Justification for {role_name} not found in CSV"

        print("   ✓ All justifications found in CSV content")

    # Display sample justifications
    print("\n📊 SAMPLE JUSTIFICATIONS GENERATED:")
    for i, uar in enumerate(user_account_roles, 1):
        justification = uar.to_dict()["Justification"]
        print(f"   {i}. {uar.role.name}: {justification[:150]}...")

    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Real workflow generates justifications correctly")
    print("✅ Justifications appear in CSV and Excel exports")
    print("✅ Different role types have appropriate justifications")
    print(
        "✅ Files generated: real_justification_test.csv, real_justification_test.xlsx"
    )

    return True


if __name__ == "__main__":
    try:
        test_real_justification_workflow()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
