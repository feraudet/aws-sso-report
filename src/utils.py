"""
Utilities

This module contains utility functions and helpers used across the application.
"""

import sys
from typing import Any, Dict


def print_progress(current: int, total: int, message: str = "Processing"):
    """Print progress information."""
    print(f"[{current}/{total}] {message}")


def print_debug(message: str, data: Any = None):
    """Print debug information."""
    print(f"[DEBUG] {message}")
    if data is not None:
        print(f"[DEBUG] Data: {data}")


def validate_aws_credentials():
    """Validate that AWS credentials are properly configured."""
    try:
        import boto3

        session = boto3.Session()
        # Try to get caller identity to validate credentials
        sts = session.client("sts")
        sts.get_caller_identity()
        return True
    except Exception as e:
        print(f"Error: AWS credentials not properly configured: {e}")
        print("Please run 'aws sso login' or configure your AWS credentials.")
        return False


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    return dictionary.get(key, default)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def handle_keyboard_interrupt():
    """Handle keyboard interrupt gracefully."""
    print("\n\nOperation cancelled by user.")
    sys.exit(1)
