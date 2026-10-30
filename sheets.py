import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("Expenses Tracker").sheet1
    return sheet


def append_expense(data):
    sheet = get_sheet()
    all_rows = sheet.get_all_values()

    today = data["date"]
    current_month = today[:7]

    today_total = 0
    month_total = 0
    last_date = None

    for row in all_rows[1:]:
        if len(row) < 2:
            continue

        row_date = row[0]
        raw_amount = row[1]

        try:
            clean_amount = raw_amount.replace("₹", "").replace(",", "").strip()
            amount = float(clean_amount)
        except:
            continue

        last_date = row_date

        # Month total accumulates everything in same month
        if row_date.startswith(current_month):
            month_total += amount

        # Today total only accumulates same date
        if row_date == today:
            today_total += amount

    # Add current entry
    today_total += data["amount"]
    month_total += data["amount"]

    # Insert blank row if new day
    if last_date and last_date != today:
        sheet.append_row(["", "", "", "", ""])

    sheet.append_row([
        today,
        data["amount"],
        data["description"],
        today_total,
        month_total
    ])
