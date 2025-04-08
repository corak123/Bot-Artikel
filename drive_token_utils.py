from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import pickle
import os
import io

def upload_token_to_drive(service, creds, email, folder_id):
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"
    
    with open(filename, "wb") as f:
        pickle.dump(creds, f)

    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }
    media = MediaFileUpload(filename, mimetype="application/octet-stream")
    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    os.remove(filename)


def download_token_from_drive(service, email, folder_id):
    safe_email = email.replace("@", "_").replace(".", "_")
    filename = f"token_{safe_email}.pkl"

    query = f"name = '{filename}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id)").execute()
    items = results.get("files", [])

    if not items:
        return None

    file_id = items[0]["id"]
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    return pickle.load(fh)
