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

## Usage

1. **Configure AWS authentication** (SSO, profile, env vars, etc). Example for SSO:
   ```bash
   aws sso login --profile <your-profile>
   export AWS_PROFILE=<your-profile>
   ```
2. **Run the script:**
   ```bash
   ./iam.py
   # ou
   python iam.py
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

Cyril Feraudet <cyril.feraudet@nuagic.com>

## Development & Maintenance
- Code is formatted with [Black](https://github.com/psf/black)
- Linting with [Flake8](https://flake8.pycqa.org/)
- CI via GitHub Actions (see `.github/workflows/python.yml`)
- Issues and PRs welcome

## License

This project is licensed under the GPL v3. See [LICENSE](LICENSE) for details.

---

*For more details, see the script header or contact the maintainer.*
