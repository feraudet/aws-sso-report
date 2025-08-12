"""
Report Generators

This module handles the generation of various report formats (CSV, Excel, HTML, JSON)
from the collected IAM Identity Center data.
"""

import csv
import json
from datetime import datetime
from typing import List

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .data_models import CSV_FIELDNAMES, UserAccountRoleGroup, UserSummary


class ReportGenerator:
    """Generates reports in multiple formats."""

    def __init__(self, output_prefix: str = "iam_identity_center_report"):
        self.output_prefix = output_prefix
        self.start_time = datetime.now()

    def generate_all_reports(
        self,
        user_account_roles: List[UserAccountRoleGroup],
        user_summaries: List[UserSummary],
    ):
        """Generate all report formats."""
        print("Generating reports...")

        self.generate_csv_report(user_account_roles)
        self.generate_excel_report(user_account_roles)
        self.generate_html_report(user_account_roles)
        self.generate_json_report(user_summaries)

        self._print_completion_summary()

    def generate_csv_report(self, user_account_roles: List[UserAccountRoleGroup]):
        """Generate CSV report."""
        filename = f"{self.output_prefix}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

            for uar in user_account_roles:
                row = uar.to_dict()
                # Filter only CSV fields
                csv_row = {k: v for k, v in row.items() if k in CSV_FIELDNAMES}
                writer.writerow(csv_row)

        print(f"CSV file {filename} generated.")

    def generate_excel_report(self, user_account_roles: List[UserAccountRoleGroup]):
        """Generate Excel report with formatting."""
        filename = f"{self.output_prefix}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "IAM Identity Center"

        # Add headers
        ws.append(CSV_FIELDNAMES)

        # Add data rows
        for uar in user_account_roles:
            row_data = uar.to_dict()
            ws.append([row_data.get(col, "") for col in CSV_FIELDNAMES])

        # Apply formatting
        self._format_excel_worksheet(ws)

        wb.save(filename)
        print(f"XLSX file {filename} generated.")

    def generate_html_report(self, user_account_roles: List[UserAccountRoleGroup]):
        """Generate interactive HTML report."""
        filename = f"{self.output_prefix}.html"

        # Prepare data for HTML
        html_rows = []
        for uar in user_account_roles:
            row_data = uar.to_dict()
            html_row = {}

            for col in CSV_FIELDNAMES:
                val = row_data.get(col, "")
                if isinstance(val, str):
                    html_row[col] = val.replace("\n", "<br>")
                else:
                    html_row[col] = val

            html_rows.append(html_row)

        # Create DataFrame
        df = pd.DataFrame(html_rows, columns=CSV_FIELDNAMES)

        # Apply string replacements only to text columns
        text_columns = [
            "User",
            "Responsible Group",
            "Assignment Type",
            "AWS Account",
            "Role Name",
            "Access Level",
            "Risk Level",
        ]

        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace("\n", "<br>", regex=False)

        # Generate HTML table
        html_table = df.to_html(
            index=False, escape=False, classes="display nowrap", border=0
        )

        # Create complete HTML document
        html_content = self._create_html_template(html_table)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML file {filename} generated.")

    def generate_json_report(self, user_summaries: List[UserSummary]):
        """Generate JSON report."""
        filename = f"{self.output_prefix}.json"

        json_data = [summary.to_dict() for summary in user_summaries]

        with open(filename, "w", encoding="utf-8") as jf:
            json.dump(json_data, jf, ensure_ascii=False, indent=2)

        print(f"JSON file {filename} generated.")

    def _format_excel_worksheet(self, ws):
        """Apply formatting to Excel worksheet."""
        # Header formatting
        header_fill = PatternFill(
            start_color="4472C4", end_color="4472C4", fill_type="solid"
        )

        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill

        # Auto-width columns and wrap text
        for col_idx, col in enumerate(CSV_FIELDNAMES, 1):
            max_length = len(col)

            for row_cells in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
                for cell in row_cells:
                    if cell.value:
                        cell_length = len(str(cell.value))
                        if cell_length > max_length:
                            max_length = cell_length

                    # Enable text wrapping
                    try:
                        cell.alignment = cell.alignment.copy(wrapText=True)
                    except AttributeError:
                        from openpyxl.styles import Alignment

                        cell.alignment = Alignment(wrapText=True)

            # Set column width (max 50 characters)
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[get_column_letter(col_idx)].width = adjusted_width

        # Freeze panes (first row and first column)
        ws.freeze_panes = ws.cell(row=2, column=2)

    def _create_html_template(self, html_table: str) -> str:
        """Create complete HTML template with DataTables."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AWS IAM Identity Center Report</title>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<style>
table.dataTable thead th {{
    background-color: #4F81BD;
    color: white;
    font-weight: bold;
}}
table.dataTable tbody tr:nth-child(even) {{
    background-color: #f9f9f9;
}}
table.dataTable tbody tr:hover {{
    background-color: #e6f3ff;
}}
.container {{
    margin: 20px;
}}
h1 {{
    color: #4F81BD;
    font-family: Arial, sans-serif;
}}
</style>
</head>
<body>
<div class="container">
<h1>AWS IAM Identity Center Report</h1>
<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
{html_table}
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script>
$(document).ready(function() {{
    $('.display').DataTable({{
        "pageLength": 25,
        "lengthMenu": [10, 25, 50, 100, -1],
        "order": [[ 0, "asc" ]],
        "columnDefs": [
            {{ "width": "15%", "targets": 0 }},
            {{ "width": "15%", "targets": 1 }},
            {{ "width": "20%", "targets": 2 }},
            {{ "width": "10%", "targets": 3 }},
            {{ "width": "15%", "targets": 4 }},
            {{ "width": "10%", "targets": 5 }},
            {{ "width": "5%", "targets": 6 }},
            {{ "width": "5%", "targets": 7 }},
            {{ "width": "5%", "targets": 8 }},
            {{ "width": "10%", "targets": 9 }}
        ]
    }});
}});
</script>
</body>
</html>
"""

    def _print_completion_summary(self):
        """Print completion summary with timing."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print(f"Script started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Script ended at:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration:    {duration:.2f} seconds")
