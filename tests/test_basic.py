import json
from pathlib import Path

def test_json_output():
    data = json.loads(Path('iam_identity_center_report.json').read_text())
    assert isinstance(data, list)
    assert all('User' in row for row in data)
