import pickle
import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import streamlit as st

# Folder Google Drive untuk menyimpan token
DRIVE_FOLDER_NAME = "blogger_tokens"

def get_drive_service():
    drive_creds = Credentials.from_authorized_user_info(st.secrets["gcp_service_account"])
    service = build("drive", "v3", credentials=drive_creds)
    return service

def save_credentials_to_drive(credentials, user_email, drive_service):
    """
    Simpan credentials Google OAuth ke Google Drive user
    """
    creds_json = credentials.to_json()

    file_metadata = {
        'name': f'token_{user_email}.json',
        'parents': [TOKEN_FOLDER_ID],  # folder ID kamu
        'mimeType': 'application/json'
    }

    media = MediaInMemoryUpload(creds_json.encode('utf-8'), mimetype='application/json')

    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ Token berhasil disimpan untuk {user_email}")

def find_or_create_folder(service):
    # Cek apakah folder sudah ada
    query = f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])

    if items:
        return items[0]["id"]  # return folder ID
    else:
        # Jika belum ada, buat folder baru
        file_metadata = {
            "name": DRIVE_FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = service.files().create(body=file_metadata, fields="id").execute()
        return folder["id"]

def upload_token_to_drive(email, creds):
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"

    # Serialize credentials
    creds_bytes = pickle.dumps(creds)
    fh = io.BytesIO(creds_bytes)

    service = get_drive_service()
    folder_id = find_or_create_folder(service)

    # Cek apakah file sudah ada
    query = f"name='{filename}' and '{folder_id}' in parents and trashed = false"
    result = service.files().list(q=query, fields="files(id)").execute()
    items = result.get("files", [])

    media = MediaIoBaseUpload(fh, mimetype="application/octet-stream")

    if items:
        # Replace existing file
        file_id = items[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Upload new file
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        service.files().create(body=file_metadata, media_body=media).execute()

def load_token_from_drive(email):
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"

    service = get_drive_service()
    folder_id = find_or_create_folder(service)

    query = f"name='{filename}' and '{folder_id}' in parents and trashed = false"
    result = service.files().list(q=query, fields="files(id)").execute()
    items = result.get("files", [])

    if not items:
        return None

    file_id = items[0]["id"]
    fh = io.BytesIO()
    request = service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    creds = pickle.load(fh)
    return creds
