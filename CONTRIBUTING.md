# 🤝 Contributing Guide

Thank you for your interest in contributing to the **AWS SSO Report** project! This guide explains how to participate effectively in the development.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Environment Setup](#development-environment-setup)
- [Development Conventions](#development-conventions)
- [Contribution Process](#contribution-process)
- [Testing and Validation](#testing-and-validation)
- [Documentation](#documentation)
- [Getting Help](#getting-help)

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- **Respectful**: Treat all participants with respect and courtesy
- **Inclusive**: Welcome contributions from everyone, regardless of their experience level
- **Constructive**: Provide constructive and helpful feedback
- **Professional**: Maintain a professional and welcoming environment

## 🚀 How to Contribute

### Types of Accepted Contributions

- 🐛 **Bug fixes**: Report and fix issues
- ✨ **New features**: Propose and implement new capabilities
- 📚 **Documentation**: Improve existing documentation
- 🧪 **Tests**: Add or improve tests
- 🔧 **Optimizations**: Improve performance or maintainability
- 🎨 **User interface**: Improve user experience

### Before You Start

1. **Check existing issues** to avoid duplicates
2. **Create an issue** to discuss major changes
3. **Read the documentation** to understand the project architecture

## ⚙️ Development Environment Setup

### Prerequisites

- **Python 3.8+** (recommended: 3.12)
- **Git**
- **Docker** (for testing with act)
- **AWS CLI** configured (for integration tests)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/aws-sso-report.git
cd aws-sso-report

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Set up pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# 5. Verify installation
python -m pytest tests/
pre-commit run --all-files
```

### 🛠️ Local Testing Script

We provide a convenient script that automatically activates the virtual environment and runs tests:

```bash
# Make the script executable (first time only)
chmod +x scripts/test-local.sh

# Run all tests
./scripts/test-local.sh

# Run specific test suites
./scripts/test-local.sh tests      # Python tests only
./scripts/test-local.sh precommit  # Pre-commit hooks only
./scripts/test-local.sh quality    # Code quality checks only
./scripts/test-local.sh act        # Test workflows with act

# Show help
./scripts/test-local.sh help
```

**Note:** Always ensure your virtual environment is activated before running commands manually:
```bash
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### AWS Configuration (Optional)

```bash
# For AWS integration tests
aws configure sso
# or
aws configure
```

## 📝 Development Conventions

### Project Structure

```
aws-sso-report/
├── src/                    # Main source code
│   ├── data_models.py     # Data models
│   ├── data_collector.py  # AWS data collection
│   ├── report_generators.py # Report generation
│   └── __version__.py     # Version information
├── tests/                 # Unit and integration tests
├── scripts/               # Utility scripts
├── .github/               # GitHub Actions workflows
└── docs/                  # Documentation
```

### Naming Conventions

#### Branches
```bash
feature/short-description     # New features
bugfix/bug-description        # Bug fixes
hotfix/urgent-description     # Urgent fixes
chore/task-description        # Maintenance, dependencies
```

#### Commit Messages
Use **Conventional Commits**:

```bash
feat: add support for multiple AWS accounts
fix: resolve timeout issue in data collection
docs: update API documentation
test: add unit tests for report generation
chore: update dependencies to latest versions
```

**Available Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, style
- `refactor`: Refactoring
- `perf`: Performance improvement
- `test`: Tests
- `chore`: Maintenance
- `ci`: Continuous integration

### Code Standards

#### Python
- **Formatting**: Black (max line length 88 characters)
- **Imports**: isort with Black profile
- **Linting**: flake8, pylint
- **Type hints**: Required for public functions
- **Docstrings**: Google Style format

```python
def collect_user_data(account_id: str, region: str = "us-east-1") -> List[User]:
    """Collect user data from AWS SSO.
    
    Args:
        account_id: AWS account identifier
        region: AWS region (default: us-east-1)
        
    Returns:
        List of User objects containing SSO data
        
    Raises:
        AWSError: If AWS API call fails
        ValidationError: If account_id is invalid
    """
    # Implementation here
    pass
```

#### Tests
- **Framework**: pytest
- **Coverage**: Minimum 80%
- **Naming**: `test_function_name_scenario`
- **Structure**: Arrange, Act, Assert

```python
def test_collect_user_data_with_valid_account():
    # Arrange
    account_id = "123456789012"
    expected_users = [User(id="user1", username="test")]
    
    # Act
    result = collect_user_data(account_id)
    
    # Assert
    assert len(result) > 0
    assert result[0].username == "test"
```

## 🔄 Contribution Process

### 1. Preparation

```bash
# Create a branch for your contribution
git checkout -b feature/my-new-feature

# Keep your branch up to date
git fetch origin
git rebase origin/main
```

### 2. Development

```bash
# Make your changes
# ...

# Use the local testing script (recommended)
./scripts/test-local.sh

# Or manually activate virtual environment and test
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pre-commit run --all-files
python -m pytest tests/

# Test with act (optional)
act --container-architecture linux/amd64 -j quick-validation
```

### 3. Commit and Push

```bash
# Commit with conventional message
git add .
git commit -m "feat: add support for cross-account reporting"

# Push your branch
git push origin feature/my-new-feature
```

### 4. Pull Request

1. **Create a Pull Request** from your fork
2. **Fill out the template** with all required information
3. **Wait for review** and automatic validations
4. **Respond to comments** and make requested changes

### Acceptance Criteria

✅ **All tests pass**
✅ **Code coverage ≥ 80%**
✅ **Pre-commit hooks pass**
✅ **Documentation updated**
✅ **Conventional commit messages**
✅ **Review approved**

## 🧪 Testing and Validation

### Local Testing

```bash
# Always activate virtual environment first
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Tests with coverage
python -m pytest --cov=src tests/

# Performance tests
python -m pytest tests/performance/ -m performance
```

### Validation with act

```bash
# Quick validation
act --container-architecture linux/amd64 -j quick-validation

# Complete validation
act --container-architecture linux/amd64 -j quality-checks

# Release workflow test
act --container-architecture linux/amd64 -j release
```

### Types of Tests

- **Unit tests**: Tests of individual functions
- **Integration tests**: Tests with AWS (requires configuration)
- **Performance tests**: Performance and load tests
- **Security tests**: Security tests with bandit

## 📚 Documentation

### Documentation Updates

- **README.md**: General information and installation
- **API docs**: Docstrings in code
- **CHANGELOG.md**: Generated automatically
- **Guides**: User documentation in `/docs`

### Documentation Generation

```bash
# Generate API documentation
python -m pydoc -w src/

# Check links
python -m pytest tests/docs/
```

## 🆘 Getting Help

### Communication Channels

- **GitHub Issues**: Technical questions and bugs
- **Discussions**: General questions and ideas
- **Email**: Direct contact for sensitive questions

### Useful Resources

- [AWS SSO Documentation](https://docs.aws.amazon.com/singlesignon/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Style Guide](https://pep8.org/)
- [pytest Documentation](https://docs.pytest.org/)

### FAQ

**Q: How to test with a real AWS account?**
A: Configure AWS CLI with `aws configure sso` and use integration tests.

**Q: My tests fail locally but pass in CI?**
A: Check Python and dependency versions. Use `act` to reproduce the CI environment.

**Q: How to add a major new feature?**
A: First create an issue to discuss the approach, then follow the contribution process.

## 🎉 Recognition

All contributors are recognized in:
- **CONTRIBUTORS.md**: List of contributors
- **Releases**: Mentions in release notes
- **README.md**: Acknowledgments section

Thank you for contributing to improve AWS SSO Report! 🚀

---

*For any questions, feel free to create an issue or contact us directly.*
