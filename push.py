import requests
import logging


def push(user_id, user_key, api_url, completed_trainings):

    if completed_trainings:
        headers = {
            "Authorization": f"SOLAFORCE-HMAC-SHA256 User={user_id},Key={user_key}",
            "Content-Type": "application/json"
        }

        try:
            Postresponse = requests.post(
                api_url, headers=headers, json={"trainings": completed_trainings})

            # Jos 200, menee läpi, jos 401, ei pääsyä
            print("Status code:", Postresponse.status_code)
            print("Response:", Postresponse.text)
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to post to Solaforce: {err}")
            print(f"Error posting to Solaforce: {err}")
    else:
        print("Ei dataa lähetettäväksi.")
