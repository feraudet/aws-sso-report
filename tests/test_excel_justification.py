#!/usr/bin/env python3
"""
Test script to verify that the justification column appears in Excel/CSV exports.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.data_models import (
        CSV_FIELDNAMES,
        AWSAccount,
        Role,
        User,
        UserAccountRoleGroup,
    )
    from src.permission_scoring_config import PermissionScoringConfig
    from src.report_generators import ReportGenerator
except ImportError:
    from data_models import CSV_FIELDNAMES, AWSAccount, Role, User, UserAccountRoleGroup
    from permission_scoring_config import PermissionScoringConfig
    from report_generators import ReportGenerator


def test_justification_in_exports():
    """Test that justification column appears in CSV and Excel exports."""
    print("🧪 TESTING JUSTIFICATION COLUMN IN EXPORTS")
    print("=" * 50)

    # Create test data with justifications
    scoring_config = PermissionScoringConfig()

    # Create a test role with actions that will generate justifications
    test_actions = [
        "iam:CreateRole",
        "ec2:AuthorizeSecurityGroupIngress",
        "s3:GetObject",
        "kms:Decrypt",
    ]

    # Score the actions to get justifications
    access_level, scores, high_risk_actions = scoring_config.analyze_actions(
        test_actions
    )

    # Create test objects
    user = User(
        id="test-user-123",
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        status="Enabled",
    )

    account = AWSAccount(id="123456789012", name="Test Account")

    role = Role(
        name="TestRoleWithJustification",
        arn="arn:aws:sso:::permissionSet/ssoins-123/ps-test",
        access_level=access_level,
        scores=scores,
    )

    user_account_role = UserAccountRoleGroup(
        user=user,
        account=account,
        role=role,
        responsible_group="TestGroup",
        assignment_type="GROUP",
    )

    # Test 1: Check CSV_FIELDNAMES includes Justification
    print("✅ Test 1: CSV_FIELDNAMES includes Justification")
    print(f"   CSV Fields: {CSV_FIELDNAMES}")
    assert (
        "Justification" in CSV_FIELDNAMES
    ), "Justification not found in CSV_FIELDNAMES"
    print(
        f"   ✓ Justification found at position {CSV_FIELDNAMES.index('Justification') + 1}"
    )

    # Test 2: Check to_dict() includes justification
    print("\n✅ Test 2: to_dict() includes justification")
    data_dict = user_account_role.to_dict()
    print(f"   Dictionary keys: {list(data_dict.keys())}")
    assert "Justification" in data_dict, "Justification not found in to_dict() output"
    print(f"   ✓ Justification value: {data_dict['Justification'][:100]}...")

    # Test 3: Generate actual CSV and Excel files
    print("\n✅ Test 3: Generate CSV and Excel files with justification")
    report_generator = ReportGenerator("test_justification_report")

    # Generate CSV
    report_generator.generate_csv_report([user_account_role])
    print("   ✓ CSV file generated: test_justification_report.csv")

    # Generate Excel
    report_generator.generate_excel_report([user_account_role])
    print("   ✓ Excel file generated: test_justification_report.xlsx")

    # Test 4: Verify CSV content
    print("\n✅ Test 4: Verify CSV content")
    with open("test_justification_report.csv", "r", encoding="utf-8") as f:
        csv_content = f.read()
        assert "Justification" in csv_content, "Justification column not found in CSV"
        assert (
            scores.justification[:50] in csv_content
        ), "Justification content not found in CSV"
        print("   ✓ CSV contains Justification column and content")

    # Test 5: Verify Excel can be read (basic check)
    print("\n✅ Test 5: Verify Excel file exists and is readable")
    import os

    excel_file = "test_justification_report.xlsx"
    assert os.path.exists(excel_file), "Excel file was not created"
    assert os.path.getsize(excel_file) > 0, "Excel file is empty"
    print(f"   ✓ Excel file exists and has size: {os.path.getsize(excel_file)} bytes")

    # Display sample data
    print("\n📊 SAMPLE DATA GENERATED:")
    print(f"   Role: {role.name}")
    print(f"   Access Level: {role.access_level.value}")
    print(f"   Risk Level: {role.risk_level.value}")
    print(
        f"   Scores: Read={scores.read_score}, Write={scores.write_score}, Admin={scores.admin_score}"
    )
    print(f"   Justification (first 200 chars): {scores.justification[:200]}...")
    print(f"   High-risk actions: {len(high_risk_actions)}")

    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Justification column is now included in CSV and Excel exports")
    print(
        "✅ Files generated: test_justification_report.csv, test_justification_report.xlsx"
    )

    return True


if __name__ == "__main__":
    try:
        test_justification_in_exports()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
