"""
Test script to compare old vs new permission scoring systems.

This demonstrates the improvements in the new configuration-driven approach.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from permission_scoring_config import get_scoring_config


def test_kms_decrypt_scoring():
    """Test that kms:Decrypt is correctly scored as read-only."""
    print("=== Testing kms:Decrypt Scoring ===")

    config = get_scoring_config()

    # Test kms:Decrypt - should be read-only, not write
    read_score, write_score, admin_score, risk_level = config.score_action(
        "kms:Decrypt"
    )

    print("kms:Decrypt scoring:")
    print(f"  Read Score: {read_score}")
    print(f"  Write Score: {write_score}")
    print(f"  Admin Score: {admin_score}")
    print(f"  Risk Level: {risk_level}")
    print(f"  Explanation: {config.get_risk_explanation('kms:Decrypt')}")

    # Assertions
    assert write_score == 0, f"kms:Decrypt should have write_score=0, got {write_score}"
    assert read_score > 0, f"kms:Decrypt should have read_score>0, got {read_score}"
    assert risk_level == "low", f"kms:Decrypt should be low risk, got {risk_level}"

    print("✅ kms:Decrypt correctly scored as read-only")
    print()


def test_iam_escalation_scoring():
    """Test that IAM escalation actions get high scores."""
    print("=== Testing IAM Escalation Scoring ===")

    config = get_scoring_config()

    escalation_actions = [
        "iam:AttachUserPolicy",
        "iam:CreateRole",
        "iam:PassRole",
        "iam:PutUserPolicy",
    ]

    for action in escalation_actions:
        read_score, write_score, admin_score, risk_level = config.score_action(action)

        print(f"{action}:")
        print(f"  Read Score: {read_score}")
        print(f"  Write Score: {write_score}")
        print(f"  Admin Score: {admin_score}")
        print(f"  Risk Level: {risk_level}")
        print(f"  Explanation: {config.get_risk_explanation(action)}")

        # These should be critical risk
        assert (
            risk_level == "critical"
        ), f"{action} should be critical risk, got {risk_level}"
        assert (
            admin_score >= 8
        ), f"{action} should have high admin score, got {admin_score}"

        print(f"✅ {action} correctly scored as critical risk")
        print()


def test_service_context_awareness():
    """Test that the same action name is scored differently based on service."""
    print("=== Testing Service Context Awareness ===")

    config = get_scoring_config()

    # Compare delete actions across services
    delete_actions = [
        "s3:DeleteObject",  # Medium risk - just deleting a file
        "iam:DeleteRole",  # High risk - deleting IAM role
        "ec2:DeleteSecurityGroup",  # High risk - network security
    ]

    for action in delete_actions:
        read_score, write_score, admin_score, risk_level = config.score_action(action)

        print(f"{action}:")
        print(f"  Risk Level: {risk_level}")
        print(f"  Scores: read={read_score}, write={write_score}, admin={admin_score}")
        print(f"  Explanation: {config.get_risk_explanation(action)}")
        print()

    # s3:DeleteObject should be medium risk
    s3_scores = config.score_action("s3:DeleteObject")
    assert s3_scores[3] == "medium", "s3:DeleteObject should be medium risk"

    # iam:DeleteRole should be high risk
    iam_scores = config.score_action("iam:DeleteRole")
    assert iam_scores[3] == "high", "iam:DeleteRole should be high risk"

    print("✅ Service context correctly differentiates risk levels")
    print()


def test_managed_policy_scoring():
    """Test managed policy scoring."""
    print("=== Testing Managed Policy Scoring ===")

    config = get_scoring_config()

    policies = [
        ("AdministratorAccess", "critical"),
        ("ReadOnlyAccess", "low"),
        ("EC2FullAccess", "high"),
        ("AmazonS3ReadOnlyAccess", "medium"),
    ]

    for policy_name, expected_risk in policies:
        read_score, write_score, admin_score = config.score_managed_policy(policy_name)

        print(f"{policy_name}:")
        print(f"  Scores: read={read_score}, write={write_score}, admin={admin_score}")

        if expected_risk == "critical":
            assert admin_score >= 8, f"{policy_name} should have high admin score"
        elif expected_risk == "low":
            assert (
                write_score == 0 and admin_score == 0
            ), f"{policy_name} should be read-only"

        print(f"✅ {policy_name} correctly scored")
        print()


def test_action_analysis():
    """Test comprehensive action analysis."""
    print("=== Testing Action Analysis ===")

    config = get_scoring_config()

    # Mix of actions with different risk levels
    test_actions = [
        "s3:GetObject",  # Low risk - read
        "s3:PutObject",  # Medium risk - write
        "iam:CreateRole",  # Critical risk - escalation
        "kms:Decrypt",  # Low risk - read (despite "decrypt")
        "ec2:TerminateInstances",  # High risk - destructive
    ]

    access_level, scores, high_risk_actions = config.analyze_actions(test_actions)

    print("Action Analysis Results:")
    print(f"  Access Level: {access_level}")
    print(
        f"  Scores: read={scores.read_score}, write={scores.write_score}, admin={scores.admin_score}"
    )
    print(f"  Risk Level: {scores.get_risk_level()}")
    print(f"  High Risk Actions: {high_risk_actions}")

    # Should detect admin access due to iam:CreateRole
    assert (
        access_level.value == "Admin"
    ), f"Should detect admin access, got {access_level}"
    assert (
        "iam:CreateRole" in high_risk_actions
    ), "Should identify iam:CreateRole as high risk"

    print("✅ Action analysis correctly identified admin access and high-risk actions")
    print()


def demonstrate_improvements():
    """Demonstrate key improvements over the old system."""
    print("=== SCORING SYSTEM IMPROVEMENTS DEMONSTRATION ===")
    print()

    print("🎯 KEY IMPROVEMENTS:")
    print("1. kms:Decrypt correctly classified as READ-ONLY (not write)")
    print("2. IAM escalation actions get CRITICAL risk scores")
    print("3. Service context awareness (s3:Delete vs iam:Delete)")
    print("4. Configurable via YAML (no more hardcoded logic)")
    print("5. Detailed risk explanations for each action")
    print()

    # Run all tests
    test_kms_decrypt_scoring()
    test_iam_escalation_scoring()
    test_service_context_awareness()
    test_managed_policy_scoring()
    test_action_analysis()

    print("\n🎉 ALL SCORING COMPARISON TESTS PASSED!")
    print()
    print("The new configuration-driven scoring system provides:")
    print("✅ More accurate risk assessment")
    print("✅ Better context awareness")
    print("✅ Configurable and maintainable logic")


if __name__ == "__main__":
    demonstrate_improvements()
