# This code fetches all completed courses after updated_after timestamp from Studytube and converts results to match Solaforce's requirements.
# Fetching "time_spent" from Studytube doesn't work, at the moment time spent (trainingHours) is calculated based on the difference between start and end times.
# Training hours are rounded up to the nearest 0.25 hours, as required by Solaforce.
# Saves the processed data in CSV & Excel
# Stores the last successful fetch timestamp in last_checked_timestamp.txt to prevent duplicate processing.

import requests
import re
import math
import pandas as pd
from datetime import datetime, timezone

LAST_CHECKED_FILE = "last_checked_timestamp.txt"


def get_access_token(client_id, client_secret, token_url):
    """Fetch OAuth 2.0 access token from Studytube API"""
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as err:
        print(f"ERROR: Access token retrieval failed - {err}")
        return None


def get_last_checked_time():
    """Retrieve the last timestamp when data was successfully fetched"""
    try:
        with open(LAST_CHECKED_FILE, "r") as file:
            last_checked = file.read().strip()
            return last_checked if last_checked else None
    except FileNotFoundError:
        return None  # If file doesn't exist, fetch all available data


def update_last_checked_time():
    """Update the last successful data fetch timestamp"""
    current_time = datetime.now(timezone.utc).isoformat(
    )  # Format: YYYY-MM-DDTHH:MM:SS.sssZ
    with open(LAST_CHECKED_FILE, "w") as file:
        file.write(current_time)


def format_date(date_str):
    """Convert date format to YYYY-MM-DD and remove timezone/milliseconds"""
    if not date_str or not isinstance(date_str, str):
        return None  # Return None if value is missing or not a string

    # Remove timezone (e.g., +02:00)
    date_str = re.sub(r"\+\d{2}:\d{2}$", "", date_str)
    # Remove milliseconds (.000)
    date_str = re.sub(r"\.\d{3}", "", date_str)

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        print(f"WARNING: Date conversion failed ({date_str})")
        return None


def calculate_time_spent(start_date, finish_date):
    """Calculate time spent in seconds based on start and finish times"""
    if not start_date or not finish_date:
        return 0  # Return 0 if any date is missing

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        finish_dt = datetime.strptime(finish_date, "%Y-%m-%dT%H:%M:%S.%f%z")

        time_spent_seconds = (finish_dt - start_dt).total_seconds()
        return time_spent_seconds
    except ValueError:
        print(
            f"WARNING: Time calculation failed for start: {start_date}, finish: {finish_date}")
        return 0


def convert_seconds_to_hours_rounded(seconds):
    """Convert seconds to hours and round to the nearest 0.25."""
    if not seconds or seconds <= 0:
        return 0.0  # Default to 0 if no time spent
    hours = seconds / 3600  # Convert seconds to hours
    return math.ceil(hours * 4) / 4  # Round to nearest 0.25


def fetch(client_id, client_secret, token_url, users_courses_url):
    """Fetch completed trainings from Studytube and convert them into Solaforce format."""
    access_token = get_access_token(client_id, client_secret, token_url)
    if not access_token:
        print("ERROR: Access token missing.")
        return

    # Fetch last timestamp to get only new updates
    updated_after = get_last_checked_time()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    params = {
        "updated_after": updated_after,  # Fetch only new or updated records
        "completed": True  # Only fetch completed trainings
    }

    try:
        response = requests.get(
            users_courses_url, headers=headers, params=params)
        response.raise_for_status()
        all_courses = response.json()

        if not all_courses:
            print("No new completed trainings retrieved from API.")
            return

        completed_trainings = []

        for record in all_courses:
            user = record.get("user", {})
            course = record.get("course", {})
            learning_status = record.get("learning_status", "").lower()

            if learning_status == "completed":  # Fetch only completed trainings
                # Calculate time spent if missing
                time_spent_seconds = record.get("time_spent", 0)
                if time_spent_seconds == 0:
                    time_spent_seconds = calculate_time_spent(
                        record.get("start_date"), record.get("finish_date"))

                training_data = {
                    "employeeNumber": user.get("employee_number", "Unknown ID"),
                    "rainingCategory": "INTERNAL",  # Default value, can be modified later
                    "trainingTypeStr": course.get("name", "Unknown Course"),
                    "trainingProvider": "Halton Academy (ST)",
                    "startDate": format_date(record.get("start_date")),
                    "endDate": format_date(record.get("finish_date")),
                    "trainingHours": convert_seconds_to_hours_rounded(time_spent_seconds),
                    "expirationDate": record.get("deadline_at"),
                }

                completed_trainings.append(training_data)

        if not completed_trainings:
            print("No new completed trainings found.")
            return

        # Convert to DataFrame
        df_completed_trainings = pd.DataFrame(completed_trainings)

        # Save CSV
        csv_filename = "completed_trainings.csv"
        df_completed_trainings.to_csv(
            csv_filename, index=False, encoding="utf-8-sig")

        # Save Excel
        excel_filename = "completed_trainings.xlsx"
        df_completed_trainings.to_excel(excel_filename, index=False)

        print(
            f"Completed trainings data saved to:\n - {csv_filename}\n - {excel_filename}")

        # Update last checked timestamp to avoid duplicate fetches
        update_last_checked_time()

    except requests.exceptions.RequestException as err:
        print(f"ERROR: Failed to fetch course data - {err}")
