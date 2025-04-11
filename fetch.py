# This code fetches all completed courses after updated_after timestamp from Studytube and converts results to match Solaforce's requirements.
# Fetching "time_spent" from Studytube doesn't work, at the moment time spent (trainingHours) is calculated based on the difference between start and end times.
# Training hours are rounded up to the nearest 0.25 hours, as required by Solaforce.
# Saves the processed data in CSV & Excel
# Stores the last successful fetch timestamp in last_checked_timestamp.txt to prevent duplicate processing.

import requests
import os
import json
import math
import re
from datetime import datetime, timezone
from dateutil import parser
import logging

logging.getLogger('azure').setLevel(logging.WARNING)

# Default values
DEFAULT_PROVIDER = "Halton Academy(ST)"
DEFAULT_CATEGORY = "Internal"

# Studytube -> Solaforce training type mapping
TRAINING_TYPE_MAPPING = {
    "course": "Online Class",
    "blog_article": "Material",
    "video": "Video",
    "document": "Curriculum"
}

# Studytube content types
TRAINING_TYPES = [
    ("users/courses", "course", "course"),
    ("users/blog-articles", "blog_article", "blog_article"),
    ("users/videos", "video", "video"),
    ("users/documents", "document", "document")
]

# --- Helper Functions ---


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


def format_date(date_str):
    """Convert date format to YYYY-MM-DD and remove timezone/milliseconds"""
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = re.sub(r"\+\d{2}:\d{2}$", "", date_str)
    date_str = re.sub(r"\.\d{3}", "", date_str)
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return None


def calculate_time_spent(start_date, finish_date):
    try:
        start = parser.isoparse(start_date)
        end = parser.isoparse(finish_date)
        return (end - start).total_seconds()
    except (ValueError, TypeError):
        return 0


def convert_seconds_to_hours_rounded(seconds):
    if not seconds or seconds <= 0:
        return "0.25"
    return str(round((seconds / 3600) * 4) / 4)


def fetch_studytube_items(access_token, users_courses_url, last_checked_timestamp):
    """Fetch items of a given training type from the API"""
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"updated_after": last_checked_timestamp, "completed": True}

    try:
        response = requests.get(
            users_courses_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logging.error(f"ERROR fetching {users_courses_url}: {err}")
        return []


def convert_training_type(studytube_type):
    return TRAINING_TYPE_MAPPING.get(studytube_type, "Unknown")


def build_training_record(user, item, studytube_type, wrapper):
    start_date = item.get("start_date")
    finish_date = item.get("finish_date")
    seconds = calculate_time_spent(start_date, finish_date)
    training_type = convert_training_type(studytube_type)

    try:
        return {
            "employeeNumber": user.get("employee_number", "Unknown"),
            "trainingCategory": DEFAULT_CATEGORY,
            "trainingTypeStr": item.get(wrapper, {}).get("title") or item.get("course", {}).get("name", "Unknown"),
            "trainingType": training_type,
            "trainingProvider": DEFAULT_PROVIDER,
            "startDate": format_date(start_date),
            "endDate": format_date(finish_date),
            "trainingHours": str(convert_seconds_to_hours_rounded(seconds)),
            "expirationDate": item.get("deadline_at")
        }
    except Exception as e:
        logging.error(f"Skipped record due to error: {e}")
        return None


def fetch(client_id, client_secret, token_url, users_courses_url, blob_client):
    access_token = get_access_token(client_id, client_secret, token_url)
    if not access_token:
        return []

    completed_trainings = []

    last_checked_timestamp = blob_client.download_blob().readall().decode(
        'utf-8') if blob_client.exists() and blob_client.download_blob().readall().decode(
        'utf-8') != "" else None

    # Loop through all training types and collect completed trainings
    for endpoint, wrapper, studytube_type in TRAINING_TYPES:
        data = fetch_studytube_items(
            access_token, users_courses_url, last_checked_timestamp)
        for item in data:
            if item.get("learning_status") == "completed":
                record = build_training_record(
                    item.get("user", {}), item, studytube_type, wrapper)
                if record:
                    completed_trainings.append(record)

    if completed_trainings:
        blob_client.upload_blob(
            datetime.now(timezone.utc).isoformat(), overwrite=True)
        return {"trainings": completed_trainings}
    else:
        print("No new trainings to export.")
        return {}
