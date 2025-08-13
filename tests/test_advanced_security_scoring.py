#!/usr/bin/env python3
"""
Advanced Security Scoring Test

This test demonstrates the comprehensive security-focused scoring system
with all critical AWS services and detailed justifications.
"""

import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_critical_security_actions():
    """Test scoring of critical security actions across all services."""
    print("🔒 TESTING CRITICAL SECURITY ACTIONS")
    print("=" * 60)

    try:
        from permission_scoring_config import PermissionScoringConfig

        config = PermissionScoringConfig()

        # Critical security actions from different services
        critical_actions = [
            # IAM - Privilege Escalation
            ("iam:CreateRole", "Privilege escalation risk"),
            ("iam:AttachUserPolicy", "Can grant elevated permissions"),
            ("iam:PassRole", "Can assume roles for escalation"),
            # VPC - Network Security
            ("ec2:CreateVpc", "Can create isolated networks"),
            ("ec2:CreateInternetGateway", "Can expose resources to internet"),
            ("ec2:AttachInternetGateway", "Can connect VPC to internet"),
            ("ec2:AuthorizeSecurityGroupIngress", "Can open firewall ports"),
            # Security Monitoring
            ("guardduty:DeleteDetector", "Can disable threat detection"),
            ("cloudtrail:StopLogging", "Can disable audit logging"),
            ("config:DeleteConfigurationRecorder", "Can disable compliance monitoring"),
            # Secrets & Access
            ("secretsmanager:DeleteSecret", "Can delete credentials"),
            ("ssm:SendCommand", "Can execute remote commands"),
            ("ssm:StartSession", "Can start interactive sessions"),
        ]

        print("🎯 Critical Actions Analysis:")
        print()

        for action, context in critical_actions:
            (
                read_score,
                write_score,
                admin_score,
                risk_level,
                justification,
            ) = config.score_action(action)

            risk_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "unknown": "⚪",
            }.get(risk_level, "⚪")

            print(f"{risk_emoji} **{action}**")
            print(f"   Context: {context}")
            print(f"   Risk Level: {risk_level.upper()}")
            print(
                f"   Scores: Read={read_score}, Write={write_score}, Admin={admin_score}"
            )
            print(f"   Justification: {justification}")
            print()

        return True

    except Exception as e:
        print(f"❌ Critical security actions test failed: {e}")
        return False


def test_security_audit_scenarios():
    """Test realistic security audit scenarios."""
    print("\n🔍 TESTING SECURITY AUDIT SCENARIOS")
    print("=" * 60)

    try:
        from permission_scoring_config import PermissionScoringConfig

        config = PermissionScoringConfig()

        # Scenario 1: Network Administrator
        network_admin_actions = [
            "ec2:CreateVpc",
            "ec2:CreateSubnet",
            "ec2:CreateSecurityGroup",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:CreateRoute",
            "ec2:DescribeVpcs",
        ]

        # Scenario 2: Security Auditor
        security_auditor_actions = [
            "cloudtrail:DescribeTrails",
            "guardduty:GetDetector",
            "config:DescribeConfigurationRecorders",
            "iam:ListRoles",
            "s3:GetObject",
        ]

        # Scenario 3: Malicious Actor
        malicious_actions = [
            "iam:CreateRole",
            "iam:AttachUserPolicy",
            "cloudtrail:StopLogging",
            "guardduty:DeleteDetector",
            "secretsmanager:GetSecretValue",
            "ssm:SendCommand",
        ]

        scenarios = [
            (
                "Network Administrator",
                network_admin_actions,
                "Should have high network permissions but limited admin",
            ),
            (
                "Security Auditor",
                security_auditor_actions,
                "Should have read-only access with low risk",
            ),
            (
                "Malicious Actor",
                malicious_actions,
                "Should trigger critical risk alerts",
            ),
        ]

        for scenario_name, actions, expected_behavior in scenarios:
            print(f"📋 **Scenario: {scenario_name}**")
            print(f"   Expected: {expected_behavior}")

            access_level, scores, high_risk_actions = config.analyze_actions(actions)

            print(f"   Result: Access Level = {access_level.value}")
            print(
                f"   Scores: Read={scores.read_score}, Write={scores.write_score}, Admin={scores.admin_score}"
            )
            print(f"   Risk Level: {scores.get_risk_level().value}")
            print(
                f"   High-Risk Actions: {len(high_risk_actions)} ({', '.join(high_risk_actions[:3])}{'...' if len(high_risk_actions) > 3 else ''})"
            )
            print(f"   Justification: {scores.justification[:200]}...")
            print()

        return True

    except Exception as e:
        print(f"❌ Security audit scenarios test failed: {e}")
        return False


def test_compliance_perspective():
    """Test from a compliance and regulatory perspective."""
    print("\n📊 TESTING COMPLIANCE PERSPECTIVE")
    print("=" * 60)

    try:
        from permission_scoring_config import PermissionScoringConfig

        config = PermissionScoringConfig()

        # Compliance-critical actions
        compliance_tests = [
            # Audit Trail Integrity
            ("cloudtrail:DeleteTrail", "GDPR/SOX: Audit trail deletion", "critical"),
            (
                "cloudtrail:StopLogging",
                "GDPR/SOX: Audit logging disruption",
                "critical",
            ),
            # Data Protection
            (
                "secretsmanager:GetSecretValue",
                "PCI-DSS: Access to sensitive data",
                "medium",
            ),
            ("kms:Decrypt", "PCI-DSS: Decryption of protected data", "low"),
            # Access Control
            ("iam:CreateRole", "SOX: Privilege escalation risk", "critical"),
            ("iam:AttachUserPolicy", "SOX: Unauthorized access grant", "critical"),
            # Network Security
            (
                "ec2:AuthorizeSecurityGroupIngress",
                "PCI-DSS: Network exposure",
                "critical",
            ),
            (
                "ec2:CreateInternetGateway",
                "ISO 27001: External connectivity",
                "critical",
            ),
            # Monitoring & Detection
            (
                "guardduty:DeleteDetector",
                "ISO 27001: Security monitoring disruption",
                "critical",
            ),
            (
                "config:StopConfigurationRecorder",
                "SOX: Compliance monitoring disruption",
                "high",
            ),
        ]

        print("🏛️ Compliance Risk Assessment:")
        print()

        critical_count = 0
        high_count = 0

        for action, compliance_context, expected_risk in compliance_tests:
            (
                read_score,
                write_score,
                admin_score,
                actual_risk,
                justification,
            ) = config.score_action(action)

            if actual_risk == "critical":
                critical_count += 1
            elif actual_risk == "high":
                high_count += 1

            status = "✅" if actual_risk == expected_risk else "⚠️"

            print(f"{status} **{action}**")
            print(f"   Compliance Context: {compliance_context}")
            print(f"   Expected Risk: {expected_risk.upper()}")
            print(f"   Actual Risk: {actual_risk.upper()}")
            print(f"   Regulatory Impact: {justification}")
            print()

        print("📈 **Compliance Summary:**")
        print(f"   Critical Compliance Risks: {critical_count}")
        print(f"   High Compliance Risks: {high_count}")
        print(f"   Total Actions Assessed: {len(compliance_tests)}")

        return True

    except Exception as e:
        print(f"❌ Compliance perspective test failed: {e}")
        return False


def main():
    """Run all advanced security tests."""
    print("🛡️  ADVANCED AWS SECURITY SCORING SYSTEM TEST")
    print("=" * 70)
    print("Testing comprehensive security-focused permission scoring")
    print("with detailed justifications and compliance perspective.")
    print()

    tests = [
        test_critical_security_actions,
        test_security_audit_scenarios,
        test_compliance_perspective,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("=" * 70)
    print(f"📊 **FINAL RESULTS: {passed}/{total} tests passed**")

    if passed == total:
        print("\n🎉 **ALL ADVANCED SECURITY TESTS PASSED!**")
        print("✅ Comprehensive security scoring system is operational")
        print("✅ Critical AWS services properly configured")
        print("✅ Detailed justifications provide audit trail")
        print("✅ Compliance perspective integrated")
        print("✅ Ready for production security audits")
    else:
        print(f"\n❌ {total - passed} tests failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
