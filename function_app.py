import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
from fetch import fetch
from push import push

# Load environment variables
load_dotenv()

# API Credentials
STUDYTUBE_CLIENT_ID = os.getenv("STUDYTUBE_CLIENT_ID")
STUDYTUBE_CLIENT_SECRET = os.getenv("STUDYTUBE_CLIENT_SECRET")
STUDYTUBE_TOKEN_URL = os.getenv("STUDYTUBE_TOKEN_URL")
STUDYTUBE_USERS_COURSES_URL = os.getenv("STUDYTUBE_USERS_COURSES_URL")

SOLAFORCE_USER_ID = os.getenv("SOLAFORCE_USER_ID")
SOLAFORCE_USER_KEY = os.getenv("SOLAFORCE_USER_KEY")
SOLAFORCE_API_URL = os.getenv("SOLAFORCE_API_URL")

STORAGE_ACC_CONN_STRING = os.getenv("STORAGE_ACC_CONN_STRING")
STORAGE_ACC_CONT_NAME = os.getenv("STORAGE_ACC_CONT_NAME")
STORAGE_ACC_BLOB_NAME = os.getenv("STORAGE_ACC_BLOB_NAME")

app = func.FunctionApp()


@app.function_name(name="studyToSola")
@app.timer_trigger(schedule="*/30 * * * * *", arg_name="studyToSola", run_on_startup=False, use_monitor=False)
def timer_trigger(studyToSola: func.TimerRequest) -> None:
    blob_service_client = BlobServiceClient.from_connection_string(
        STORAGE_ACC_CONN_STRING)

    container_client = blob_service_client.get_container_client(
        STORAGE_ACC_CONT_NAME)

    if not container_client.exists():
        container_client.create_container()

    blob_client = container_client.get_blob_client("last_checked.txt")

    completed_trainings = fetch(STUDYTUBE_CLIENT_ID, STUDYTUBE_CLIENT_SECRET,
                                STUDYTUBE_TOKEN_URL, STUDYTUBE_USERS_COURSES_URL, blob_client)

    push(SOLAFORCE_USER_ID, SOLAFORCE_USER_KEY,
         SOLAFORCE_API_URL, completed_trainings, blob_client)
