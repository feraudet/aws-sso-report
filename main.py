#!/usr/bin/env python3
"""
AWS IAM Identity Center Reporting Tool - Main Entry Point

This is the main entry point for the modularized AWS IAM Identity Center
reporting application.

Usage:
    python main.py
    ./main.py

Author: Cyril Feraudet <cyril.feraudet@nuant.com>
License: GPL v3
"""

import signal
import sys

from src.data_collector import data_collector
from src.report_generators import ReportGenerator
from src.utils import handle_keyboard_interrupt, validate_aws_credentials


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    handle_keyboard_interrupt()


def main():
    """Main application entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("AWS IAM Identity Center Reporting Tool")
    print("=" * 50)

    # Validate AWS credentials
    if not validate_aws_credentials():
        sys.exit(1)

    try:
        # Collect data from AWS
        user_account_roles, user_summaries = data_collector.collect_all_data()

        # Generate reports
        report_generator = ReportGenerator()
        report_generator.generate_all_reports(user_account_roles, user_summaries)

        print("\n✅ All reports generated successfully!")

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
