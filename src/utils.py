"""
Utilities

This module contains utility functions and helpers used across the application.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """Save data to JSON file."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_from_json(filename: str) -> List[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        path = Path(filename)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def format_timestamp(timestamp: Optional[datetime]) -> str:
    """Format timestamp to ISO string."""
    if timestamp is None:
        return "N/A"
    return timestamp.isoformat()


def validate_email(email: Optional[str]) -> bool:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False

    # Basic email validation regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Check length (reasonable limit)
    if len(email) > 254:
        return False

    # Check for spaces
    if " " in email:
        return False

    return bool(re.match(pattern, email))
