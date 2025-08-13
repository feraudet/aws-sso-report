"""
Tests for Report Generators module.

These tests verify report generation works correctly without AWS connections.
"""

import json
import os
import tempfile

import pytest

from src.data_models import (
    AWSAccount,
    PermissionScores,
    Role,
    User,
    UserAccountRoleGroup,
    UserSummary,
)
from src.report_generators import ReportGenerator


class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_report_generator_initialization(self):
        """Test ReportGenerator initialization."""
        generator = ReportGenerator()

        assert generator is not None

    def test_generate_csv_report(self):
        """Test CSV report generation."""
        # Create test data
        user = User(
            id="user1",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        account = AWSAccount(id="123456789012", name="Production")
        role = Role(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123")
        role.scores = PermissionScores(read_score=5, write_score=7, admin_score=9)

        user_account_roles = [
            UserAccountRoleGroup(
                user=user,
                account=account,
                role=role,
                responsible_group="DevOps Team",
                assignment_type="GROUP",
            )
        ]

        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                generator = ReportGenerator(output_prefix="test_report")
                generator.generate_csv_report(user_account_roles)

                # Verify file was created and has content
                csv_file = "test_report.csv"
                assert os.path.exists(csv_file)

                with open(csv_file, "r") as f:
                    content = f.read()
                    # Check for expected content based on actual CSV structure
                    assert "User" in content
                    assert "john.doe" in content or "John Doe" in content
                    assert "Production" in content
                    assert "AdminRole" in content

            finally:
                os.chdir(original_cwd)

    def test_generate_excel_report(self):
        """Test Excel report generation."""
        # Create test data
        user = User(
            id="user1",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        account = AWSAccount(id="123456789012", name="Production")
        role = Role(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123")
        role.scores = PermissionScores(read_score=5, write_score=7, admin_score=9)

        user_account_roles = [
            UserAccountRoleGroup(
                user=user,
                account=account,
                role=role,
                responsible_group="DevOps Team",
                assignment_type="GROUP",
            )
        ]

        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                generator = ReportGenerator(output_prefix="test_report")
                generator.generate_excel_report(user_account_roles)

                # Verify file was created
                excel_file = "test_report.xlsx"
                assert os.path.exists(excel_file)
                assert os.path.getsize(excel_file) > 0  # File should have content

            finally:
                os.chdir(original_cwd)

    def test_generate_json_report(self):
        """Test JSON report generation."""
        # Create test data
        user = User(
            id="user1",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        user_summaries = [
            UserSummary(
                user=user, accounts=[{"id": "123456789012", "name": "Production"}]
            )
        ]

        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                generator = ReportGenerator(output_prefix="test_report")
                generator.generate_json_report(user_summaries)

                # Verify file was created and has valid JSON
                json_file = "test_report.json"
                assert os.path.exists(json_file)

                with open(json_file, "r") as f:
                    data = json.load(f)
                    assert isinstance(data, list)
                    assert len(data) == 1
                    # Check for expected keys based on actual to_dict structure
                    assert "User" in data[0]
                    assert "AWS Accounts" in data[0]

            finally:
                os.chdir(original_cwd)

    def test_generate_html_report(self):
        """Test HTML report generation."""
        # Create test data
        user = User(
            id="user1",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )
        account = AWSAccount(id="123456789012", name="Production")
        role = Role(name="AdminRole", arn="arn:aws:sso:::permissionSet/ps-123")
        role.scores = PermissionScores(read_score=5, write_score=7, admin_score=9)

        user_account_roles = [
            UserAccountRoleGroup(
                user=user,
                account=account,
                role=role,
                responsible_group="DevOps Team",
                assignment_type="GROUP",
            )
        ]

        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                generator = ReportGenerator(output_prefix="test_report")
                generator.generate_html_report(user_account_roles)

                # Verify file was created and has HTML content
                html_file = "test_report.html"
                assert os.path.exists(html_file)

                with open(html_file, "r") as f:
                    content = f.read()
                    assert "<html" in content  # More flexible check for HTML tag
                    assert "<table" in content  # More flexible check for table tag
                    # Check for user data
                    assert "john.doe" in content or "John Doe" in content
                    assert "Production" in content
                    assert "AdminRole" in content

            finally:
                os.chdir(original_cwd)

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        # Test with empty lists - should not raise exceptions
        empty_user_account_roles = []

        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                generator = ReportGenerator(output_prefix="test_empty")
                generator.generate_csv_report(empty_user_account_roles)

                csv_file = "test_empty.csv"
                assert os.path.exists(csv_file)

            finally:
                os.chdir(original_cwd)

    def test_data_validation(self):
        """Test data validation in report generation."""
        generator = ReportGenerator()

        # Test with None data
        with pytest.raises((TypeError, AttributeError)):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as temp_file:
                temp_path = temp_file.name
            try:
                generator.generate_csv_report(None, temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

    def test_file_path_handling(self):
        """Test file path handling in report generation."""
        # Create test data
        user = User(
            id="user1",
            username="john.doe",
            email="john@example.com",
            display_name="John Doe",
        )

        user_summaries = [
            UserSummary(
                user=user, accounts=[{"id": "123456789012", "name": "Production"}]
            )
        ]

        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                generator = ReportGenerator(output_prefix="test_path")
                generator.generate_json_report(user_summaries)

                json_file = "test_path.json"
                assert os.path.exists(json_file)

            finally:
                os.chdir(original_cwd)
