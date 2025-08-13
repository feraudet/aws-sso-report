# AWS Security Analysis Report

**Generated:** 2025-08-13 14:20:28
**Analysis Method:** Configuration-driven scoring v2.0

## 🎯 Role Summary

| Property | Value |
|----------|-------|
| **Name** | `NetworkAdminRole` |
| **ARN** | `arn:aws:sso:::permissionSet/ssoins-123/ps-networkadmin` |
| **Access Level** | **Admin** |
| **Risk Level** | **CRITICAL** |

## 📊 Security Scores

| Score Type | Value | Description |
|------------|-------|-------------|
| **Read Score** | 10 | Read-only access capabilities |
| **Write Score** | 10 | Write/modify capabilities |
| **Admin Score** | 10 | Administrative privileges |

**Justification:** Analysis of 8 actions. Access level: Admin. High-risk actions: 3. Detailed breakdown: ec2:CreateVpc: Service-specific scoring: Can create new VPCs (network isolation). Risk level: CRITICAL (score: 10). CRITICAL: Full administrative privileges - can escalate permissions or compromise security.; ec2:AuthorizeSecurityGroupIngress: Service-specific scoring: Can open firewall ports (security risk). Risk level: CRITICAL (score: 10). CRITICAL: Full administrative privileges - can escalate permissions or compromise security.; ec2:CreateSecurityGroup: Service-specific scoring: Can create new security groups. Risk level: HIGH (score: 8). HIGH: Significant write/modify permissions - can alter system state.; ec2:DescribeInstances: Service-specific scoring: Can list EC2 instances (read-only). Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk.; cloudtrail:DescribeTrails: Service-specific scoring: Can list audit trails (read-only). Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk. ... and 3 more actions.

## 🔍 Risk Analysis

**Total Actions:** 8
**High-Risk Actions:** 3

### Risk Distribution

| Risk Level | Count | Actions |
|------------|-------|----------|
| 🔴 **CRITICAL** | 2 | `ec2:CreateVpc`, `ec2:AuthorizeSecurityGroupIngress` |
| 🟠 **HIGH** | 1 | `ec2:CreateSecurityGroup` |
| 🟢 **LOW** | 5 | `ec2:DescribeInstances`, `cloudtrail:DescribeTrails`, `iam:ListRoles` ... and 2 more |

## 📋 Detailed Action Analysis

### 🔴 CRITICAL Risk Actions

**`ec2:CreateVpc`**
*Scores:* Read=10, Write=10, Admin=10
*Justification:* Service-specific scoring: Can create new VPCs (network isolation). Risk level: CRITICAL (score: 10). CRITICAL: Full administrative privileges - can escalate permissions or compromise security.

**`ec2:AuthorizeSecurityGroupIngress`**
*Scores:* Read=10, Write=10, Admin=10
*Justification:* Service-specific scoring: Can open firewall ports (security risk). Risk level: CRITICAL (score: 10). CRITICAL: Full administrative privileges - can escalate permissions or compromise security.

### 🟠 HIGH Risk Actions

**`ec2:CreateSecurityGroup`**
*Scores:* Read=8, Write=8, Admin=4
*Justification:* Service-specific scoring: Can create new security groups. Risk level: HIGH (score: 8). HIGH: Significant write/modify permissions - can alter system state.

### 🟢 LOW Risk Actions

**`ec2:DescribeInstances`**
*Scores:* Read=3, Write=0, Admin=0
*Justification:* Service-specific scoring: Can list EC2 instances (read-only). Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk.

**`cloudtrail:DescribeTrails`**
*Scores:* Read=3, Write=0, Admin=0
*Justification:* Service-specific scoring: Can list audit trails (read-only). Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk.

**`iam:ListRoles`**
*Scores:* Read=3, Write=0, Admin=0
*Justification:* Service-specific scoring: Can list IAM roles (read-only). Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk.

**`s3:GetObject`**
*Scores:* Read=3, Write=0, Admin=0
*Justification:* Service-specific scoring: Can read S3 objects. Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk.

**`guardduty:GetDetector`**
*Scores:* Read=3, Write=0, Admin=0
*Justification:* Service-specific scoring: Can read threat detection configuration. Risk level: LOW (score: 3). LOW: Read-only access - minimal security risk.

## 🛡️ Security Recommendations

1. 🔴 URGENT: 2 critical risk actions detected. Immediate review required for privilege escalation and security bypass capabilities.

2. ⚠️ ADMIN ACCESS: Full administrative privileges detected. Ensure this role is assigned only to authorized personnel with MFA enabled.

## ⚖️ Compliance Issues

### 🟠 ISO 27001: Network Security Controls

**Description:** Critical network modification capabilities detected

**Affected Actions:** `ec2:CreateVpc`, `ec2:AuthorizeSecurityGroupIngress`

## 🔴 Overall Risk Assessment: **CRITICAL**

⚠️ **IMMEDIATE ACTION REQUIRED** - This role poses significant security risks and requires urgent review.
