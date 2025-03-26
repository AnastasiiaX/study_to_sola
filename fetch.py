# This code fetches all completed courses after updated_after timestamp from Studytube and converts results to match Solaforce's requirements.
# Fetching "time_spent" from Studytube doesn't work, at the moment time spent (trainingHours) is calculated based on the difference between start and end times.
# Training hours are rounded up to the nearest 0.25 hours, as required by Solaforce.
# Saves the processed data in CSV & Excel
# Stores the last successful fetch timestamp in last_checked_timestamp.txt to prevent duplicate processing.

import requests
import logging
import re
import math
import pandas as pd
from datetime import datetime, timezone

LAST_CHECKED_FILE = "last_checked_timestamp.txt"

# Default values
DEFAULT_PROVIDER = "Halton Academy (ST)"
DEFAULT_CATEGORY = "INTERNAL"

# Training types with their API endpoints, data wrapper, and training type label
TRAINING_TYPES = [
    ("users/courses", "course", "Online Course"),
    ("users/blog-articles", "blog_article", "Blog"),
    ("users/videos", "video", "Video"),
    ("users/documents", "document", "Document")
]


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
        logging.error(f"ERROR: Access token retrieval failed - {err}")
        return None


def get_last_checked_time():
    """Retrieve the last timestamp when data was successfully fetched"""
    try:
        with open(LAST_CHECKED_FILE, "r") as file:
            last_checked = file.read().strip()
            return last_checked
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
        logging.warning(f"WARNING: Date conversion failed ({date_str})")
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
        logging.warning(
            f"WARNING: Time calculation failed for start: {start_date}, finish: {finish_date}")
        return 0


def convert_seconds_to_hours_rounded(seconds):
    """Convert seconds to hours and round to the nearest 0.25."""
    if not seconds or seconds <= 0:
        return 0.0  # Default to 0 if no time spent
    hours = seconds / 3600  # Convert seconds to hours
    return math.ceil(hours * 4) / 4  # Round to nearest 0.25


def fetch_studytube_items(access_token, users_courses_url):
    """Fetch items of a given training type from the API"""
    updated_after = get_last_checked_time()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"updated_after": updated_after, "completed": True}

    try:
        response = requests.get(
            users_courses_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logging.error(f"ERROR fetching {users_courses_url}: {err}")
        return []


def build_training_record(user, item, item_type, wrapper):
    """Convert API training record"""
    start_date = item.get("start_date")
    finish_date = item.get("finish_date")
    seconds = calculate_time_spent(start_date, finish_date)

    try:
        return {
            "employeeNumber": user.get("employee_number", "Unknown"),
            "trainingCategory": DEFAULT_CATEGORY,
            "trainingTitle": item.get(wrapper, {}).get("title") or item.get("course", {}).get("name", "Unknown"),
            "trainingTypeStr": item_type,
            "trainingProvider": DEFAULT_PROVIDER,
            "startDate": format_date(start_date),
            "endDate": format_date(finish_date),
            "trainingHours": convert_seconds_to_hours_rounded(seconds),
            "expirationDate": item.get("deadline_at"),
        }
    except Exception as e:
        logging.error(f"Skipped record due to error: {e}")
        return None


def fetch(client_id, client_secret, token_url, users_courses_url):
    access_token = get_access_token(client_id, client_secret, token_url)
    if not access_token:
        return

    completed_trainings = []

    # Loop through all training types and collect completed trainings
    for endpoint, wrapper, training_type in TRAINING_TYPES:
        data = fetch_studytube_items(access_token, users_courses_url)
        for item in data:
            if item.get("learning_status") == "completed":
                record = build_training_record(
                    item.get("user", {}), item, training_type, wrapper)
                if record:
                    completed_trainings.append(record)

    # Export results if any trainings found
    if completed_trainings:
        df = pd.DataFrame(completed_trainings)
        df.to_csv("completed_trainings_all.csv",
                  index=False, encoding="utf-8-sig")
        df.to_excel("completed_trainings_all.xlsx", index=False)
        print("Trainings exported successfully.")
        update_last_checked_time()
    else:
        print("No completed trainings to export.")
