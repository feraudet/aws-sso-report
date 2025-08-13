# AWS IAM Identity Center (SSO) Reporting Script

[![Build Status](https://github.com/feraudet/aws-sso-report/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/feraudet/aws-sso-report/actions/workflows/python.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python 3.12](https://img.shields.io/badge/python-3.12%2B-blue)

Generate detailed reports of AWS IAM Identity Center (AWS SSO) users, groups, roles, and account access in CSV, Excel, HTML, and JSON formats.

## Features
- Exports user/group/account/role mapping to CSV, Excel (.xlsx), HTML (with filters), and JSON
- **Role permission analysis**: Automatically classifies each role as `read-only`, `read-write`, or `full-admin`
- Handles direct and group-based assignments
- Optimized API usage with caching
- Progress and timing information
- Modern, readable output (auto-width, colors, filters, wrap, etc)
- Compatible with all AWS authentication methods supported by boto3 (env vars, SSO, profiles, etc)
- Output ready for Excel, web, and automation

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/feraudet/aws-sso-report.git
   cd aws-sso-report
   ```
2. **Create and activate a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## AWS Requirements

⚠️ **Important**: This script must be executed from the **AWS Organization management account** (root account) where IAM Identity Center is configured.

### Minimal IAM Policy

The user or role executing this script requires the following minimal permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "IAMIdentityCenterRead",
            "Effect": "Allow",
            "Action": [
                "sso-admin:ListInstances",
                "sso-admin:ListPermissionSets",
                "sso-admin:DescribePermissionSet",
                "sso-admin:ListAccountAssignments",
                "sso-admin:ListManagedPoliciesInPermissionSet",
                "sso-admin:GetInlinePolicyForPermissionSet"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IdentityStoreRead",
            "Effect": "Allow",
            "Action": [
                "identitystore:ListUsers",
                "identitystore:ListGroups",
                "identitystore:ListGroupMemberships"
            ],
            "Resource": "*"
        },
        {
            "Sid": "OrganizationsRead",
            "Effect": "Allow",
            "Action": [
                "organizations:ListAccounts",
                "organizations:DescribeAccount"
            ],
            "Resource": "*"
        }
    ]
}
```

### AWS Account Context

- **Management Account**: Script must run from the AWS Organization's management account
- **IAM Identity Center**: Must be enabled in the organization
- **Permissions**: The executing user/role needs the above minimal policy attached

## Development Setup

### Quick Setup
```bash
# Setup development environment with pre-commit hooks
./setup-dev.sh
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Available Development Commands
```bash
make format          # Format code with black and isort
make lint            # Run all linters (flake8, mypy, bandit, pylint)
make test            # Run tests
make pre-commit-run  # Run pre-commit on all files
make clean           # Clean up generated files
make setup-dev       # Complete development setup
```

### Code Quality Tools
This project uses several code quality tools:
- **Black**: Code formatter (88 char line length)
- **isort**: Import sorter (compatible with Black)
- **flake8**: Linting with additional plugins (docstrings, import order, bugbear)
- **mypy**: Type checking
- **bandit**: Security linting
- **pylint**: Additional linting (minimal config)

Pre-commit hooks will automatically run these tools on git commit.

## Usage

1. **Configure AWS authentication** (SSO, profile, env vars, etc). Example for SSO:
   ```bash
   aws sso login --profile <your-profile>
   export AWS_PROFILE=<your-profile>
   ```
2. **Run the script:**
   ```bash
   ./main.py
   # or
   python main.py
   ```
3. **Output files:**
   - `iam_identity_center_report.csv` (spreadsheet)
   - `iam_identity_center_report.xlsx` (Excel)
   - `iam_identity_center_report.html` (interactive web table, **with filters/search/sort on every column**)
   - `iam_identity_center_report.json` (structured data with role permission analysis)

## Output Example

### CSV/Excel/HTML Format:
| User | Groups | AWS Accounts |
|------|--------|--------------|
| user@example.com | Group1, Group2 | Account1 (role1, role2) |

### JSON Format (with role analysis):
```json
{
  "User": "user@example.com",
  "Groups": ["Group1", "Group2"],
  "AWS Accounts": [
    {
      "account_name": "Production Account",
      "account_id": "123456789012",
      "roles": [
        {
          "name": "AdminRole",
          "access_level": "full-admin"
        },
        {
          "name": "ReadOnlyRole",
          "access_level": "read-only"
        }
      ]
    }
  ]
}
```

**Role Access Levels:**
- `read-only`: Only read/list/describe permissions
- `read-write`: Read + write/modify permissions, but not administrative
- `full-admin`: Administrative access or wildcard permissions

## Testing

Unit tests are in the `tests/` folder. Example:

```python
# tests/test_basic.py
import json
from pathlib import Path

def test_json_output():
    data = json.loads(Path('iam_identity_center_report.json').read_text())
    assert isinstance(data, list)
    assert all('User' in row for row in data)
```

To run all tests:
```bash
pytest
```

## Screenshots

*To be added: screenshots of Excel and HTML output here.*

## Author

Cyril Feraudet <cyril@feraudet.com>

## Development & Maintenance
- Code is formatted with [Black](https://github.com/psf/black)
- Linting with [Flake8](https://flake8.pycqa.org/)
- CI via GitHub Actions (see `.github/workflows/python.yml`)
- Issues and PRs welcome

## License

This project is licensed under the GPL v3. See [LICENSE](LICENSE) for details.

---

*For more details, see the script header or contact the maintainer.*
