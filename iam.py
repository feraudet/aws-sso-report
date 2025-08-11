#!/usr/bin/env python3
"""
AWS IAM Identity Center (SSO) Reporting Script
Copyright (C) 2025 Cyril Feraudet, Nuagic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

See README.md for full usage and documentation.
"""
__author__ = "Cyril Feraudet"
import boto3
import csv
from datetime import datetime
from openpyxl import Workbook

# Set the AWS profile to use
# Utilise la configuration d'authentification par défaut de boto3
# (variables d'env, AWS_PROFILE, SSO, etc)
session = boto3.Session()

# Required clients
esso_admin = session.client("sso-admin")
identitystore = session.client("identitystore")

start_time = datetime.now()
print(f"Script started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print("Fetching IAM Identity Center instance...")
# Get the Identity Center (SSO) instance
response = esso_admin.list_instances()
if not response["Instances"]:
    raise Exception("No IAM Identity Center instance found.")
instance = response["Instances"][0]
instance_arn = instance["InstanceArn"]
identity_store_id = instance["IdentityStoreId"]

# --- Caching Section ---

# Cache all users
print("Listing all users...")
users = []
paginator = identitystore.get_paginator("list_users")
for page in paginator.paginate(IdentityStoreId=identity_store_id):
    users.extend(page["Users"])
print(f"Found {len(users)} users.")

# Cache all groups and group memberships
print("Listing all groups and memberships...")
groups = []
group_id_to_name = {}
group_id_to_members = {}
paginator = identitystore.get_paginator("list_groups")
for page in paginator.paginate(IdentityStoreId=identity_store_id):
    groups.extend(page["Groups"])
for group in groups:
    group_id = group["GroupId"]
    group_id_to_name[group_id] = group["DisplayName"]
    group_id_to_members[group_id] = set()
    # Cache all members of the group
    paginator = identitystore.get_paginator("list_group_memberships")
    for page in paginator.paginate(IdentityStoreId=identity_store_id, GroupId=group_id):
        for membership in page["GroupMemberships"]:
            member = membership["MemberId"]
            if "UserId" in member:
                group_id_to_members[group_id].add(member["UserId"])
print(f"Found {len(groups)} groups.")

# Cache all AWS accounts
print("Listing all AWS accounts...")
org_client = session.client("organizations")
org_paginator = org_client.get_paginator("list_accounts")
all_accounts = []
account_id_to_name = {}
for page in org_paginator.paginate():
    all_accounts.extend(page["Accounts"])
for account in all_accounts:
    account_id_to_name[account["Id"]] = account["Name"]
print(f"Found {len(all_accounts)} accounts.")

# Cache all PermissionSets
print("Listing all PermissionSets...")
ps_paginator = esso_admin.get_paginator("list_permission_sets")
permission_sets = []
permission_set_arn_to_name = {}
for page in ps_paginator.paginate(InstanceArn=instance_arn):
    permission_sets.extend(page["PermissionSets"])
for arn in permission_sets:
    resp = esso_admin.describe_permission_set(
        InstanceArn=instance_arn, PermissionSetArn=arn
    )
    permission_set_arn_to_name[arn] = resp["PermissionSet"]["Name"]
print(f"Found {len(permission_sets)} PermissionSets.")

# Cache all assignments for each (account, permission_set)
print("Caching all assignments for each account and PermissionSet...")
assignments = {}  # (account_id, permission_set_arn) -> list of assignments
for permission_set_arn in permission_sets:
    for account in all_accounts:
        account_id = account["Id"]
        key = (account_id, permission_set_arn)
        assignments[key] = []
        assign_paginator = esso_admin.get_paginator("list_account_assignments")
        for page in assign_paginator.paginate(
            InstanceArn=instance_arn,
            AccountId=account_id,
            PermissionSetArn=permission_set_arn,
        ):
            assignments[key].extend(page["AccountAssignments"])
print("Assignment cache built.")

# --- Helper functions using cache ---


def get_user_groups(user_id):
    user_groups = []
    for group_id, members in group_id_to_members.items():
        if user_id in members:
            user_groups.append(group_id_to_name[group_id])
    return user_groups


def get_user_account_roles(user_id):
    user_accounts = set()
    user_roles = set()
    user_groups = set()
    for group_id, members in group_id_to_members.items():
        if user_id in members:
            user_groups.add(group_id)
    for (account_id, permission_set_arn), assigns in assignments.items():
        for assignment in assigns:
            if (
                assignment["PrincipalType"] == "USER"
                and assignment["PrincipalId"] == user_id
            ):
                user_accounts.add(account_id)
                user_roles.add(permission_set_arn)
            if (
                assignment["PrincipalType"] == "GROUP"
                and assignment["PrincipalId"] in user_groups
            ):
                user_accounts.add(account_id)
                user_roles.add(permission_set_arn)
    return user_accounts, user_roles


def get_permission_set_name(permission_set_arn):
    return permission_set_arn_to_name.get(permission_set_arn, permission_set_arn)


def get_account_name(account_id):
    return account_id_to_name.get(account_id, account_id)


print("Generating CSV and XLSX report...")
fieldnames = ["User", "Groups", "AWS Accounts"]
rows = []
for idx, user in enumerate(users, 1):
    user_id = user["UserId"]
    username = user.get("UserName", user.get("DisplayName", user_id))
    print(f"[{idx}/{len(users)}] Processing user: {username}")
    groups = get_user_groups(user_id)
    # Build accounts and roles per account for this user
    accounts_roles = {}
    # Pass 1: collect all assignments (direct and via groups)
    user_accounts = set()
    user_groups_ids = set()
    for group_id, members in group_id_to_members.items():
        if user_id in members:
            user_groups_ids.add(group_id)
    for (account_id, permission_set_arn), assigns in assignments.items():
        for assignment in assigns:
            if (
                assignment["PrincipalType"] == "USER"
                and assignment["PrincipalId"] == user_id
            ) or (
                assignment["PrincipalType"] == "GROUP"
                and assignment["PrincipalId"] in user_groups_ids
            ):
                if account_id not in accounts_roles:
                    accounts_roles[account_id] = set()
                accounts_roles[account_id].add(permission_set_arn)
    # Format AWS Accounts column: one line per account, with roles in
    # parentheses
    aws_accounts_lines = []
    for acc_id in sorted(accounts_roles.keys(), key=lambda x: get_account_name(x)):
        acc_name = get_account_name(acc_id)
        role_names = [
            get_permission_set_name(arn) for arn in sorted(accounts_roles[acc_id])
        ]
        aws_accounts_lines.append(f"{acc_name} ({', '.join(role_names)})")
    # Format Groups with line separator
    groups_str = "\n".join(groups)
    aws_accounts_str = "\n".join(aws_accounts_lines)
    if username == "cyril.feraudet@nuant.com":
        print("[DEBUG] --- Cyril account/role mapping ---")
        for acc_id, role_arns in accounts_roles.items():
            roles = [get_permission_set_name(arn) for arn in role_arns]
            print(
                f"[DEBUG] Cyril: AccountId={acc_id}, "
                f"AccountName={get_account_name(acc_id)}, "
                f"Roles={roles}"
            )
        print("[DEBUG] --- All known accounts ---")
        for acc_id in sorted(account_id_to_name.keys()):
            print(
                f"[DEBUG] Known: AccountId={acc_id}, "
                f"AccountName={account_id_to_name[acc_id]}"
            )
        print(f"[DEBUG] Cyril - Final CSV Accounts: " f"{aws_accounts_lines}")
    # Structure pour JSON : comptes avec rôles en listes
    aws_accounts_json = []
    for acc_id in sorted(accounts_roles.keys(), key=lambda x: get_account_name(x)):
        acc_name = get_account_name(acc_id)
        role_names = [
            get_permission_set_name(arn) for arn in sorted(accounts_roles[acc_id])
        ]
        aws_accounts_json.append(
            {"account_name": acc_name, "account_id": acc_id, "roles": role_names}
        )

    row = {
        "User": username,
        "Groups": groups_str,
        "AWS Accounts": aws_accounts_str,
        "_groups_list": groups,  # pour JSON
        "_aws_accounts_json": aws_accounts_json,  # pour JSON avec structure
    }
    rows.append(row)

# Write CSV
with open(
    "iam_identity_center_report.csv", "w", newline="", encoding="utf-8"
) as csvfile:
    fieldnames = ["User", "Groups", "AWS Accounts"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        # Ne garder que les champs du CSV (exclure les champs internes
        # pour JSON)
        csv_row = {k: v for k, v in row.items() if k in fieldnames}
        writer.writerow(csv_row)

# Write XLSX

from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "IAM Identity Center"
ws.append(fieldnames)
# Ajout des lignes de données après l'en-tête
for row in rows:
    ws.append([row[col] for col in fieldnames])
# Style titres : gras, fond bleu clair, texte blanc
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
for cell in ws[1]:
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = header_fill
# Largeur auto, wrapText et gel de la première ligne/colonne
ws.freeze_panes = ws[2][1]  # freeze first row and first column
for col_idx, col in enumerate(fieldnames, 1):
    max_length = len(col)
    for row_cells in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
        for cell in row_cells:
            cell.alignment = cell.alignment.copy(wrapText=True)
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[get_column_letter(col_idx)].width = min(max_length + 2, 50)
# WrapText aussi sur les titres
for cell in ws[1]:
    cell.alignment = cell.alignment.copy(wrapText=True)
# Filtre automatique
ws.auto_filter.ref = ws.dimensions
wb.save("iam_identity_center_report.xlsx")

# Write HTML with DataTables
import pandas as pd

# Remplacer '\n' par '<br>' dans les cellules pour HTML
html_rows = []
for row in rows:
    html_row = {}
    for col in fieldnames:
        val = row[col]
        if isinstance(val, str):
            html_row[col] = val.replace("\n", "<br>")
        else:
            html_row[col] = val
    html_rows.append(html_row)
df = pd.DataFrame(html_rows, columns=fieldnames)
for col in fieldnames:
    df[col] = df[col].str.replace("\n", "<br>", regex=False)
html_table = df.to_html(index=False, escape=False, classes="display nowrap", border=0)
html_template = f"""
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
td, th {{
    white-space: pre-line;
    word-break: break-word;
}}
table {{ width: 100%; }}
</style>
</head>
<body>
<h2>AWS IAM Identity Center Report</h2>
{html_table}
<script src="https://code.jquery.com/jquery-3.7.0.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script>
$(document).ready(function() {{
    $('table.display').DataTable({{
        scrollX: true,
        paging: true,
        autoWidth: false,
        fixedHeader: true
    }});
}});
</script>
</body>
</html>
"""
with open("iam_identity_center_report.html", "w", encoding="utf-8") as f:
    f.write(html_template)

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()
print("CSV file iam_identity_center_report.csv generated.")
print("XLSX file iam_identity_center_report.xlsx generated.")
print(f"Script started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Script ended at:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total duration:    {duration:.2f} seconds")

# Write JSON output

import json

json_rows = []
for row in rows:
    # Pour JSON, 'Groups' et 'AWS Accounts' sont des listes/objets
    # structurés
    json_row = {
        "User": row["User"],
        "Groups": row.get("_groups_list", []),
        "AWS Accounts": row.get("_aws_accounts_json", []),
    }
    json_rows.append(json_row)
with open("iam_identity_center_report.json", "w", encoding="utf-8") as jf:
    json.dump(json_rows, jf, ensure_ascii=False, indent=2)
print("JSON file iam_identity_center_report.json generated.")
