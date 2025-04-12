import pickle
import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import streamlit as st

# Folder Google Drive untuk menyimpan token
DRIVE_FOLDER_NAME = "blogger_tokens"
TOKEN_FOLDER_ID = st.secrets["google_drive"]["folder_id"]

def get_drive_service():
    drive_creds = Credentials.from_authorized_user_info(st.secrets["gcp_service_account"])
    service = build("drive", "v3", credentials=drive_creds)
    return service


# ✅ Fungsi tambahan: Simpan token ke folder lokal
def save_credentials_to_local(credentials, folder="tokens"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"token.json")
    with open(file_path, "w") as f:
        f.write(credentials.to_json())




