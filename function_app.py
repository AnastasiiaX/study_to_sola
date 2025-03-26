import logging
import azure.functions as func
import os
from dotenv import load_dotenv
from fetch import fetch

# Load environment variables
load_dotenv()

# API Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = os.getenv("TOKEN_URL")
USERS_COURSES_URL = os.getenv("USERS_COURSES_URL")

app = func.FunctionApp()


@app.function_name(name="studyToSola")
@app.timer_trigger(schedule="0 0 0 29 2 *", arg_name="studyToSola", run_on_startup=True, use_monitor=False)
def timer_trigger(studyToSola: func.TimerRequest) -> None:
    fetch(CLIENT_ID, CLIENT_SECRET, TOKEN_URL, USERS_COURSES_URL)
