import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/blogger",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


def save_credentials_to_pickle(creds, email):
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"
    with open(filename, "wb") as token:
        pickle.dump(creds, token)


def load_credentials_from_pickle(email):
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"
    if os.path.exists(filename):
        with open(filename, "rb") as token:
            creds = pickle.load(token)
        return creds
    return None


def get_user_info(creds):
    oauth2_service = build("oauth2", "v2", credentials=creds)
    user_info = oauth2_service.userinfo().get().execute()
    return user_info
