import google.generativeai as genai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st
import pickle
import os
import requests
import re
from PIL import Image
from io import BytesIO

# Konfigurasi Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Scope akses ke Drive & Blogger
SCOPES = [
    "https://www.googleapis.com/auth/blogger",
    "https://www.googleapis.com/auth/drive"
]

# Folder Drive untuk menyimpan token
folder_id = "1d3NFHLCxqVWJpGGO4dwbPmDok4vrkIX2"
# Folder Drive untuk upload gambar
GDRIVE_IMAGE_FOLDER_ID = "1mn0Xd2zsU7DUsSaJp-D8-FbxhsTN78fk"
# Blog ID tujuan posting
BLOG_ID = "6869652925231981095"


# ==== CREDENTIALS & SERVICE SETUP ====

def create_drive_service_from_secrets():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return creds, service


def save_credentials_to_drive(creds, drive_service, drive_folder_id, filename="user_token.pkl"):
    with open(filename, "wb") as token_file:
        pickle.dump(creds, token_file)
    upload_token_to_drive(drive_service, filename, drive_folder_id, filename)
    os.remove(filename)


def upload_token_to_drive(service, file_path, folder_id, filename):
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="application/octet-stream")
    service.files().create(body=file_metadata, media_body=media).execute()


# ==== FORMATTER ====

def extract_title(article_text):
    lines = article_text.split("\n")
    title = lines[2].split(":")[0].strip()
    return title


def format_content(article_text):
    lines = article_text.split("\n")
    article_text = "\n".join(lines[3:]).strip()

    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", article_text)
    formatted_text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", formatted_text)

    paragraphs = formatted_text.split("\n")
    html = ""
    in_list = False
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith("*"):
            if not in_list:
                html += "<ul>"
                in_list = True
            html += f"<li>{p[1:].strip()}</li>"
        else:
            if in_list:
                html += "</ul>"
                in_list = False
            html += f"<p style='text-indent: 2rem; margin-bottom: 1em;'>{p}</p>"
    if in_list:
        html += "</ul>"

    return html


# ==== IMAGE & DRIVE ====

def ensure_landscape(image):
    width, height = image.size
    return image.rotate(90, expand=True) if height > width else image


def upload_image_to_drive(service, file_path, file_name):
    file_metadata = {'name': file_name, 'parents': [GDRIVE_IMAGE_FOLDER_ID]}
    media = MediaFileUpload(file_path, mimetype='image/png')
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    file_id = file['id']
    service.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()
    return f"https://lh3.googleusercontent.com/d/{file_id}=s0"


# ==== POSTING BLOGGER ====

def post_to_blogger_with_creds(title, content, categories, credentials):
    try:
        service = build('blogger', 'v3', credentials=credentials)
        user_info = service.users().get(userId='self').execute()
        blog_id = service.blogs().listByUser(userId='self').execute()['items'][0]['id']

        post = {
            "title": title,
            "content": content,
            "labels": categories
        }
        response = service.posts().insert(blogId=blog_id, body=post, isDraft=False).execute()
        return True, response['url']
    except Exception as e:
        return False, str(e)


# ==== GENERATE KONTEN ====

def generate_article_and_image(prompt_text, image_prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(
            f"Tulis artikel 850 kata dengan bahasa yang santai, human like, SEO-Friendly tentang: {prompt_text}"
        )
        article_text = response.text
        return article_text
    except Exception as e:
        st.error(f"Gagal generate artikel: {e}")
        return None


# ==== STREAMLIT UI ====

def main():
    st.title("📝 Auto Blogger dengan Gemini + Google API")

    prompt = st.text_input("Masukkan topik artikel:")
    image_prompt = st.text_input("Masukkan keyword untuk gambar (opsional):")

    if st.button("🔄 Generate dan Posting"):
        with st.spinner("Menghasilkan konten..."):
            creds, drive_service = create_drive_service_from_secrets()
            article = generate_article_and_image(prompt, image_prompt)

            if article:
                title = extract_title(article)
                html_content = format_content(article)

                # Simpan dan upload gambar dummy (nanti diganti dengan image AI jika tersedia)
                dummy_image = Image.new("RGB", (1280, 720), color="lightblue")
                dummy_image = ensure_landscape(dummy_image)
                image_path = "thumbnail.png"
                dummy_image.save(image_path)

                img_url = upload_image_to_drive(drive_service, image_path, "thumbnail.png")

                # Tambahkan gambar di atas artikel
                final_html = f"<img src='{img_url}' style='width: 100%; border-radius: 1rem;' /><br>{html_content}"

                ok, url_or_error = post_to_blogger_with_creds(
                    title=title,
                    content=final_html,
                    categories=["Teknologi", "AI"],
                    credentials=creds
                )

                if ok:
                    st.success(f"✅ Berhasil diposting! [Lihat di sini]({url_or_error})")
                else:
                    st.error(f"Gagal posting: {url_or_error}")

                os.remove(image_path)


if __name__ == "__main__":
    main()
