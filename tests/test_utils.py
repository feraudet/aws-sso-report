"""
Tests for Utils module.

These tests verify utility functions work correctly without AWS connections.
"""

import json
import os
import tempfile

from src.utils import format_timestamp, load_from_json, save_to_json, validate_email


class TestUtilityFunctions:
    """Test utility functions."""

    def test_save_to_json(self):
        """Test save_to_json function."""
        test_data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"},
        ]

        # Use temporary file for testing
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            save_to_json(test_data, temp_path)

            # Verify file was created and has correct content
            assert os.path.exists(temp_path)

            with open(temp_path, "r") as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_from_json(self):
        """Test load_from_json function."""
        test_data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"},
        ]

        # Create temporary file with test data
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(test_data, temp_file)
            temp_path = temp_file.name

        try:
            result = load_from_json(temp_path)
            assert result == test_data

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_from_json_file_not_found(self):
        """Test load_from_json with file not found."""
        result = load_from_json("nonexistent_file_12345.json")

        assert result == []

    def test_format_timestamp(self):
        """Test format_timestamp function."""
        from datetime import datetime

        # Test with a specific timestamp
        test_timestamp = datetime(2024, 1, 15, 14, 30, 45)

        result = format_timestamp(test_timestamp)

        # Should return ISO format string
        assert result == "2024-01-15T14:30:45"

    def test_format_timestamp_none(self):
        """Test format_timestamp with None input."""
        result = format_timestamp(None)

        assert result == "N/A"

    def test_validate_email_valid(self):
        """Test validate_email with valid emails."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "firstname.lastname@company.com",
        ]

        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test validate_email with invalid emails."""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "",
            None,
        ]

        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_email_edge_cases(self):
        """Test validate_email with edge cases."""
        # Very long email
        long_email = "a" * 250 + "@example.com"
        assert validate_email(long_email) is False

        # Email with spaces
        assert validate_email("user @example.com") is False
        assert validate_email("user@ example.com") is False
