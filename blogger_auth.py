import os
import pickle
import json
import requests
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from drive_token_utils import upload_token_to_drive, get_user_folder_id

SCOPES = ['https://www.googleapis.com/auth/blogger', 'https://www.googleapis.com/auth/drive.file']

CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]  # misalnya: "https://your-streamlit-app-url/"

# Fungsi untuk membuat authorization URL
def get_auth_url():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    st.session_state.flow = flow  # simpan flow sementara
    return auth_url

# Fungsi untuk menyimpan kredensial user ke Google Drive
def save_credentials_to_drive(creds, email):
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.json"
    json_str = json.dumps(token_data)
    user_folder_id = get_user_folder_id(email)
    upload_token_to_drive(json_str.encode(), filename, user_folder_id)

# Fungsi untuk ambil email user dari akses token
def get_user_info(creds):
    response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'access_token': creds.token}
    ).json()
    return {
        "email": response.get("email", "unknown_user"),
        "name": response.get("name", "Unknown Name"),
        "picture": response.get("picture", None)
    }

# Fungsi untuk menyelesaikan proses login dari URL callback
def handle_auth_callback(code):
    flow = st.session_state.flow
    flow.fetch_token(code=code)
    creds = flow.credentials
    user_info = get_user_info(creds)

    # Simpan ke session dan Google Drive
    st.session_state.credentials = creds
    st.session_state.user_email = user_info["email"]
    st.session_state.user_name = user_info["name"]
    st.session_state.user_picture = user_info["picture"]
    save_credentials_to_drive(creds, user_info["email"])
    return True
