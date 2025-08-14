#!/bin/bash

# AWS SSO Report - Quick Quality Test
# A lightweight version that just runs pre-commit hooks with venv activation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

print_status "Quick quality test for AWS SSO Report"

# Activate venv if it exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
fi

# Run pre-commit hooks
print_status "Running pre-commit hooks..."
if pre-commit run --all-files; then
    print_success "✅ All pre-commit hooks passed!"
else
    print_status "Some hooks made changes, re-running..."
    pre-commit run --all-files
    print_success "✅ Pre-commit hooks now pass!"
fi

echo -e "\n${GREEN}🚀 Quick test completed!${NC}"
