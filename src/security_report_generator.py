"""
Security Report Generator

This module generates comprehensive security reports with detailed justifications
for AWS permission scoring and risk assessment.
"""

import csv
import json
from datetime import datetime
from typing import Dict, List

# Try relative import first, fallback to absolute import
try:
    from .data_models import AccessLevel, PermissionScores, RiskLevel, Role
    from .permission_scoring_config import PermissionScoringConfig
except ImportError:
    try:
        from data_models import AccessLevel, PermissionScores, RiskLevel, Role
        from permission_scoring_config import PermissionScoringConfig
    except ImportError:
        # Define minimal classes for standalone usage

        from enum import Enum

        class AccessLevel(Enum):
            READ_ONLY = "Read Only"
            READ_WRITE = "Read Write"
            FULL_ADMIN = "Full Admin"
            UNKNOWN = "Unknown"

        class RiskLevel(Enum):
            LOW = "LOW"
            MEDIUM = "MEDIUM"
            HIGH = "HIGH"
            CRITICAL = "CRITICAL"


class SecurityReportGenerator:
    """Generates comprehensive security reports with justifications."""

    def __init__(self):
        """Initialize the report generator."""
        self.scoring_config = PermissionScoringConfig()
        self.report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_role_security_report(self, role: Role, actions: List[str]) -> Dict:
        """
        Generate a detailed security report for a single role.

        Args:
            role: The role to analyze
            actions: List of AWS actions for this role

        Returns:
            Dictionary containing comprehensive security analysis
        """
        # Analyze all actions
        access_level, scores, high_risk_actions = self.scoring_config.analyze_actions(
            actions
        )

        # Get detailed action analysis
        action_details = []
        for action in actions:
            (
                read_score,
                write_score,
                admin_score,
                risk_level,
                justification,
            ) = self.scoring_config.score_action(action)
            action_details.append(
                {
                    "action": action,
                    "risk_level": risk_level,
                    "read_score": read_score,
                    "write_score": write_score,
                    "admin_score": admin_score,
                    "justification": justification,
                    "is_high_risk": action in high_risk_actions,
                }
            )

        # Categorize actions by risk level
        risk_categories = {
            "critical": [a for a in action_details if a["risk_level"] == "critical"],
            "high": [a for a in action_details if a["risk_level"] == "high"],
            "medium": [a for a in action_details if a["risk_level"] == "medium"],
            "low": [a for a in action_details if a["risk_level"] == "low"],
            "unknown": [a for a in action_details if a["risk_level"] == "unknown"],
        }

        # Generate security recommendations
        recommendations = self._generate_security_recommendations(
            risk_categories, access_level
        )

        # Compliance assessment
        compliance_issues = self._assess_compliance_issues(action_details)

        return {
            "role_info": {
                "name": role.name,
                "arn": role.arn,
                "access_level": access_level.value,
                "risk_level": scores.get_risk_level().value,
            },
            "scores": {
                "read_score": scores.read_score,
                "write_score": scores.write_score,
                "admin_score": scores.admin_score,
                "justification": scores.justification,
            },
            "action_analysis": {
                "total_actions": len(actions),
                "high_risk_actions": len(high_risk_actions),
                "risk_distribution": {
                    "critical": len(risk_categories["critical"]),
                    "high": len(risk_categories["high"]),
                    "medium": len(risk_categories["medium"]),
                    "low": len(risk_categories["low"]),
                    "unknown": len(risk_categories["unknown"]),
                },
                "actions_by_risk": risk_categories,
            },
            "security_assessment": {
                "recommendations": recommendations,
                "compliance_issues": compliance_issues,
                "overall_risk": self._calculate_overall_risk(
                    scores, len(high_risk_actions)
                ),
            },
            "metadata": {
                "report_timestamp": self.report_timestamp,
                "scoring_version": "2.0",
                "analysis_method": "configuration-driven",
            },
        }

    def _generate_security_recommendations(
        self, risk_categories: Dict, access_level: AccessLevel
    ) -> List[str]:
        """Generate security recommendations based on risk analysis."""
        recommendations = []

        if len(risk_categories["critical"]) > 0:
            recommendations.append(
                f"🔴 URGENT: {len(risk_categories['critical'])} critical risk actions detected. "
                "Immediate review required for privilege escalation and security bypass capabilities."
            )

        if len(risk_categories["high"]) > 3:
            recommendations.append(
                f"🟠 HIGH PRIORITY: {len(risk_categories['high'])} high-risk actions present. "
                "Consider implementing additional approval workflows for these permissions."
            )

        if access_level == AccessLevel.FULL_ADMIN:
            recommendations.append(
                "⚠️ ADMIN ACCESS: Full administrative privileges detected. "
                "Ensure this role is assigned only to authorized personnel with MFA enabled."
            )

        if len(risk_categories["unknown"]) > 0:
            recommendations.append(
                f"📋 REVIEW NEEDED: {len(risk_categories['unknown'])} actions not in scoring database. "
                "Manual review recommended to assess security implications."
            )

        # Service-specific recommendations
        critical_actions = [a["action"] for a in risk_categories["critical"]]
        if any("iam:" in action for action in critical_actions):
            recommendations.append(
                "🔐 IAM RISK: IAM privilege escalation capabilities detected. "
                "Implement strict approval process and regular access reviews."
            )

        if any("cloudtrail:" in action for action in critical_actions):
            recommendations.append(
                "📊 AUDIT RISK: CloudTrail modification capabilities detected. "
                "This poses compliance risks for audit trail integrity."
            )

        return recommendations

    def _assess_compliance_issues(self, action_details: List[Dict]) -> List[Dict]:
        """Assess compliance issues based on actions."""
        compliance_issues = []

        # Check for audit trail risks
        audit_actions = [
            a
            for a in action_details
            if "cloudtrail:" in a["action"] and a["risk_level"] in ["critical", "high"]
        ]
        if audit_actions:
            compliance_issues.append(
                {
                    "regulation": "SOX/GDPR",
                    "issue": "Audit Trail Integrity Risk",
                    "description": "Actions that can modify or disable audit logging detected",
                    "affected_actions": [a["action"] for a in audit_actions],
                    "severity": "Critical",
                }
            )

        # Check for data protection risks
        secrets_actions = [
            a
            for a in action_details
            if "secretsmanager:" in a["action"] or "ssm:" in a["action"]
        ]
        if secrets_actions:
            compliance_issues.append(
                {
                    "regulation": "PCI-DSS",
                    "issue": "Sensitive Data Access",
                    "description": "Access to secrets and configuration parameters detected",
                    "affected_actions": [a["action"] for a in secrets_actions],
                    "severity": "Medium",
                }
            )

        # Check for network security risks
        network_actions = [
            a
            for a in action_details
            if "ec2:" in a["action"] and a["risk_level"] == "critical"
        ]
        if network_actions:
            compliance_issues.append(
                {
                    "regulation": "ISO 27001",
                    "issue": "Network Security Controls",
                    "description": "Critical network modification capabilities detected",
                    "affected_actions": [a["action"] for a in network_actions],
                    "severity": "High",
                }
            )

        return compliance_issues

    def _calculate_overall_risk(
        self, scores: PermissionScores, high_risk_count: int
    ) -> str:
        """Calculate overall risk assessment."""
        if scores.admin_score >= 8 or high_risk_count >= 5:
            return "CRITICAL"
        elif scores.admin_score >= 5 or high_risk_count >= 3:
            return "HIGH"
        elif scores.write_score >= 5 or high_risk_count >= 1:
            return "MEDIUM"
        else:
            return "LOW"

    def export_to_csv(self, report_data: Dict, filename: str) -> None:
        """Export security report to CSV format."""
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Header information
            writer.writerow(["AWS Security Analysis Report"])
            writer.writerow(["Generated:", self.report_timestamp])
            writer.writerow([])

            # Role summary
            role_info = report_data["role_info"]
            writer.writerow(["Role Information"])
            writer.writerow(["Name", role_info["name"]])
            writer.writerow(["ARN", role_info["arn"]])
            writer.writerow(["Access Level", role_info["access_level"]])
            writer.writerow(["Risk Level", role_info["risk_level"]])
            writer.writerow([])

            # Scores with justification
            scores = report_data["scores"]
            writer.writerow(["Security Scores"])
            writer.writerow(["Read Score", scores["read_score"]])
            writer.writerow(["Write Score", scores["write_score"]])
            writer.writerow(["Admin Score", scores["admin_score"]])
            writer.writerow(["Justification", scores["justification"]])
            writer.writerow([])

            # Action analysis
            writer.writerow(["Action Analysis"])
            writer.writerow(
                [
                    "Action",
                    "Risk Level",
                    "Read Score",
                    "Write Score",
                    "Admin Score",
                    "Justification",
                ]
            )

            for risk_level in ["critical", "high", "medium", "low", "unknown"]:
                actions = report_data["action_analysis"]["actions_by_risk"][risk_level]
                for action_data in actions:
                    writer.writerow(
                        [
                            action_data["action"],
                            action_data["risk_level"].upper(),
                            action_data["read_score"],
                            action_data["write_score"],
                            action_data["admin_score"],
                            action_data["justification"],
                        ]
                    )

            writer.writerow([])

            # Recommendations
            writer.writerow(["Security Recommendations"])
            for rec in report_data["security_assessment"]["recommendations"]:
                writer.writerow([rec])

            writer.writerow([])

            # Compliance issues
            writer.writerow(["Compliance Issues"])
            writer.writerow(
                ["Regulation", "Issue", "Description", "Severity", "Affected Actions"]
            )
            for issue in report_data["security_assessment"]["compliance_issues"]:
                writer.writerow(
                    [
                        issue["regulation"],
                        issue["issue"],
                        issue["description"],
                        issue["severity"],
                        "; ".join(issue["affected_actions"]),
                    ]
                )

    def export_to_markdown(self, report_data: Dict, filename: str) -> None:
        """Export security report to Markdown format."""
        with open(filename, "w", encoding="utf-8") as mdfile:
            role_info = report_data["role_info"]
            scores = report_data["scores"]
            analysis = report_data["action_analysis"]
            assessment = report_data["security_assessment"]

            # Header
            mdfile.write("# AWS Security Analysis Report\n\n")
            mdfile.write(f"**Generated:** {self.report_timestamp}  \n")
            mdfile.write("**Analysis Method:** Configuration-driven scoring v2.0\n\n")

            # Role summary
            mdfile.write("## 🎯 Role Summary\n\n")
            mdfile.write("| Property | Value |\n")
            mdfile.write("|----------|-------|\n")
            mdfile.write(f"| **Name** | `{role_info['name']}` |\n")
            mdfile.write(f"| **ARN** | `{role_info['arn']}` |\n")
            mdfile.write(f"| **Access Level** | **{role_info['access_level']}** |\n")
            mdfile.write(f"| **Risk Level** | **{role_info['risk_level']}** |\n\n")

            # Security scores
            mdfile.write("## 📊 Security Scores\n\n")
            mdfile.write("| Score Type | Value | Description |\n")
            mdfile.write("|------------|-------|-------------|\n")
            mdfile.write(
                f"| **Read Score** | {scores['read_score']} | Read-only access capabilities |\n"
            )
            mdfile.write(
                f"| **Write Score** | {scores['write_score']} | Write/modify capabilities |\n"
            )
            mdfile.write(
                f"| **Admin Score** | {scores['admin_score']} | Administrative privileges |\n\n"
            )

            mdfile.write(f"**Justification:** {scores['justification']}\n\n")

            # Risk distribution
            mdfile.write("## 🔍 Risk Analysis\n\n")
            risk_dist = analysis["risk_distribution"]
            mdfile.write(f"**Total Actions:** {analysis['total_actions']}  \n")
            mdfile.write(f"**High-Risk Actions:** {analysis['high_risk_actions']}\n\n")

            mdfile.write("### Risk Distribution\n\n")
            mdfile.write("| Risk Level | Count | Actions |\n")
            mdfile.write("|------------|-------|----------|\n")

            for risk_level, count in risk_dist.items():
                if count > 0:
                    emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                        "unknown": "⚪",
                    }[risk_level]
                    actions = analysis["actions_by_risk"][risk_level]
                    action_list = ", ".join([f"`{a['action']}`" for a in actions[:3]])
                    if len(actions) > 3:
                        action_list += f" ... and {len(actions) - 3} more"
                    mdfile.write(
                        f"| {emoji} **{risk_level.upper()}** | {count} | {action_list} |\n"
                    )

            mdfile.write("\n")

            # Detailed action analysis
            mdfile.write("## 📋 Detailed Action Analysis\n\n")

            for risk_level in ["critical", "high", "medium", "low"]:
                actions = analysis["actions_by_risk"][risk_level]
                if actions:
                    emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }[risk_level]
                    mdfile.write(f"### {emoji} {risk_level.upper()} Risk Actions\n\n")

                    for action_data in actions:
                        mdfile.write(f"**`{action_data['action']}`**  \n")
                        mdfile.write(
                            f"*Scores:* Read={action_data['read_score']}, Write={action_data['write_score']}, Admin={action_data['admin_score']}  \n"
                        )
                        mdfile.write(
                            f"*Justification:* {action_data['justification']}\n\n"
                        )

            # Security recommendations
            mdfile.write("## 🛡️ Security Recommendations\n\n")
            for i, rec in enumerate(assessment["recommendations"], 1):
                mdfile.write(f"{i}. {rec}\n\n")

            # Compliance issues
            if assessment["compliance_issues"]:
                mdfile.write("## ⚖️ Compliance Issues\n\n")
                for issue in assessment["compliance_issues"]:
                    severity_emoji = {
                        "Critical": "🔴",
                        "High": "🟠",
                        "Medium": "🟡",
                        "Low": "🟢",
                    }[issue["severity"]]
                    mdfile.write(
                        f"### {severity_emoji} {issue['regulation']}: {issue['issue']}\n\n"
                    )
                    mdfile.write(f"**Description:** {issue['description']}\n\n")
                    mdfile.write(
                        f"**Affected Actions:** {', '.join([f'`{a}`' for a in issue['affected_actions']])}\n\n"
                    )

            # Overall assessment
            overall_risk = assessment["overall_risk"]
            risk_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}[
                overall_risk
            ]
            mdfile.write(
                f"## {risk_emoji} Overall Risk Assessment: **{overall_risk}**\n\n"
            )

            if overall_risk == "CRITICAL":
                mdfile.write(
                    "⚠️ **IMMEDIATE ACTION REQUIRED** - This role poses significant security risks and requires urgent review.\n\n"
                )
            elif overall_risk == "HIGH":
                mdfile.write(
                    "🔍 **HIGH PRIORITY REVIEW** - This role should be reviewed and potentially restricted.\n\n"
                )
            elif overall_risk == "MEDIUM":
                mdfile.write(
                    "📋 **STANDARD REVIEW** - This role should be included in regular access reviews.\n\n"
                )
            else:
                mdfile.write(
                    "✅ **LOW RISK** - This role appears to have appropriate permissions for its function.\n\n"
                )

    def export_to_json(self, report_data: Dict, filename: str) -> None:
        """Export security report to JSON format."""
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(report_data, jsonfile, indent=2, ensure_ascii=False)


def generate_sample_report():
    """Generate a sample security report for demonstration."""
    print("🛡️ GENERATING SAMPLE SECURITY REPORT")
    print("=" * 50)

    try:
        # Create sample role and actions
        from data_models import AccessLevel, PermissionScores, Role

        sample_role = Role(
            name="NetworkAdminRole",
            arn="arn:aws:sso:::permissionSet/ssoins-123/ps-networkadmin",
            access_level=AccessLevel.READ_WRITE,
            scores=PermissionScores(read_score=8, write_score=7, admin_score=3),
        )

        sample_actions = [
            "ec2:CreateVpc",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:CreateSecurityGroup",
            "ec2:DescribeInstances",
            "cloudtrail:DescribeTrails",
            "iam:ListRoles",
            "s3:GetObject",
            "guardduty:GetDetector",
        ]

        # Generate report
        generator = SecurityReportGenerator()
        report_data = generator.generate_role_security_report(
            sample_role, sample_actions
        )

        # Export to different formats
        generator.export_to_csv(report_data, "sample_security_report.csv")
        generator.export_to_markdown(report_data, "sample_security_report.md")
        generator.export_to_json(report_data, "sample_security_report.json")

        print("✅ Sample reports generated:")
        print("   - sample_security_report.csv")
        print("   - sample_security_report.md")
        print("   - sample_security_report.json")

        # Display summary
        print("\n📊 Report Summary:")
        print(f"   Role: {report_data['role_info']['name']}")
        print(f"   Access Level: {report_data['role_info']['access_level']}")
        print(f"   Risk Level: {report_data['role_info']['risk_level']}")
        print(f"   Total Actions: {report_data['action_analysis']['total_actions']}")
        print(
            f"   High-Risk Actions: {report_data['action_analysis']['high_risk_actions']}"
        )
        print(
            f"   Recommendations: {len(report_data['security_assessment']['recommendations'])}"
        )
        print(
            f"   Compliance Issues: {len(report_data['security_assessment']['compliance_issues'])}"
        )

        return True

    except Exception as e:
        print(f"❌ Failed to generate sample report: {e}")
        return False


if __name__ == "__main__":
    generate_sample_report()
