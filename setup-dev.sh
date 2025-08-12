#!/bin/bash

# Setup development environment for AWS SSO Report project
echo "🔧 Setting up development environment..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: This script must be run from the root of a git repository"
    exit 1
fi

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -r requirements.txt

# Install pre-commit
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to check current state
echo "🔍 Running pre-commit checks on all files..."
pre-commit run --all-files

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  make format          - Format code with black and isort"
echo "  make lint            - Run all linters (flake8, mypy, bandit, pylint)"
echo "  make test            - Run tests"
echo "  make pre-commit-run  - Run pre-commit on all files"
echo "  make clean           - Clean up generated files"
echo ""
echo "Pre-commit hooks are now installed and will run automatically on git commit."
echo "To skip pre-commit hooks temporarily, use: git commit --no-verify"
