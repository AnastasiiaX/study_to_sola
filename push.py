import requests
import logging
import json


def push(user_id, user_key, api_url, completed_trainings):
    if completed_trainings:
        try:
            headers = {
                "Authorization": f"SOLAFORCE-HMAC-SHA256 User={user_id},Key={user_key}",
                "Content-Type": "application/json"
            }

            post_response = requests.post(
                api_url, headers=headers, json=json.dumps(completed_trainings))

            logging.info(f"Status code: {post_response.status_code}")
            logging.info(f"Response: {post_response.text}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Error pushing trainings: {err}")
    else:
        print("No data to send.")
