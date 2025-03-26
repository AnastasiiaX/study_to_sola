import requests
import logging


def get_access_token(user_name, user_key, token_url):
    """Fetch OAuth 2.0 access token from Solaforce API"""
    headers = {
        "Authorization": f"SOLAFORCE-HMAC-SHA256 User={user_name},Key={user_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(token_url, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as err:
        logging.error(f"ERROR: Access token retrieval failed - {err}")
        return None


def push(user_name, user_key, token_url):
    print(get_access_token(user_name, user_key, token_url))
