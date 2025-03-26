import logging
import azure.functions as func
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

SOLAFORCE_CLIENT_ID = os.getenv("SOLAFORCE_CLIENT_ID")
SOLAFORCE_CLIENT_SECRET = os.getenv("SOLAFORCE_CLIENT_SECRET")
SOLAFORCE_TOKEN_URL = os.getenv("SOLAFORCE_TOKEN_URL")

app = func.FunctionApp()


@app.function_name(name="studyToSola")
@app.timer_trigger(schedule="0 0 0 29 2 *", arg_name="studyToSola", run_on_startup=True, use_monitor=False)
def timer_trigger(studyToSola: func.TimerRequest) -> None:
    fetch(STUDYTUBE_CLIENT_ID, STUDYTUBE_CLIENT_SECRET,
          STUDYTUBE_TOKEN_URL, STUDYTUBE_USERS_COURSES_URL)

    # push(SOLAFORCE_CLIENT_ID, SOLAFORCE_CLIENT_SECRET, SOLAFORCE_TOKEN_URL)
