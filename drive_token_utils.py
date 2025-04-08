import io
import pickle
import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials

# Ambil drive_folder_id dari st.secrets
DRIVE_FOLDER_ID = st.secrets["google_drive"]["folder_id"]

# Inisialisasi Google Drive API pakai kredensial app
def get_drive_service():
    creds = Credentials.from_authorized_user_info(info=st.secrets["google_oauth"], scopes=["https://www.googleapis.com/auth/drive"])
    return build('drive', 'v3', credentials=creds)

# Simpan token user ke Google Drive
def upload_token_to_drive(creds, email):
    service = get_drive_service()
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"

    # Serialize token
    token_bytes = pickle.dumps(creds)
    media = MediaIoBaseUpload(io.BytesIO(token_bytes), mimetype='application/octet-stream')

    # Cek apakah file sudah ada
    query = f"name='{filename}' and '{DRIVE_FOLDER_ID}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = results.get('files', [])

    if files:
        # Replace existing file
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Upload baru
        file_metadata = {
            'name': filename,
            'parents': [DRIVE_FOLDER_ID]
        }
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Ambil token user dari Google Drive
def download_token_from_drive(email):
    service = get_drive_service()
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"

    query = f"name='{filename}' and '{DRIVE_FOLDER_ID}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = results.get('files', [])

    if not files:
        return None

    file_id = files[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    return pickle.load(fh)
