import requests
import logging
import json
from datetime import datetime, timezone


def push(user_id, user_key, api_url, completed_trainings, blob_client):
    if completed_trainings:
        try:
            headers = {
                "Authorization": f"SOLAFORCE-HMAC-SHA256 User={user_id},Key={user_key}",
                "Content-Type": "application/json"
            }

            post_response = requests.post(
                api_url, headers=headers, json=completed_trainings)

            logging.info(f"Status code: {post_response.status_code}")
            logging.info(f"Response: {post_response.text}")

            if post_response.status_code >= 200 and post_response.status_code < 300:
                blob_client.upload_blob(
                    datetime.now(timezone.utc).isoformat(), overwrite=True)
        except requests.exceptions.RequestException as err:
            logging.error(f"Error pushing trainings: {err}")
    else:
        blob_client.upload_blob(
            datetime.now(timezone.utc).isoformat(), overwrite=True)
        logging.info("No data to send. Timestamp upated.")
