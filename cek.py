from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import requests
import re
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import streamlit as st

# Ganti dengan API Key kamu
GEMINI_API_KEY = "AIzaSyDVK91bWgrKz3UenMOMPLIKUeKpI-i3vwM"

# Inisialisasi client
client = genai.Client(api_key=GEMINI_API_KEY)

# Path ke file service account JSON
SERVICE_ACCOUNT_FILE = "credentials.json"

# Scope akses ke Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


# Endpoint untuk mendapatkan access token baru
TOKEN_URL = "https://oauth2.googleapis.com/token"

def get_access_token():
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    
    response = requests.post(TOKEN_URL, data=data)
    token_info = response.json()
    
    if "access_token" in token_info:
        return token_info["access_token"]
    else:
        raise Exception(f"Error getting access token: {token_info}")


# Autentikasi dengan service account
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build("drive", "v3", credentials=creds)
print("Autentikasi berhasil!")

# ID folder tujuan di Google Drive
FOLDER_ID = "1mn0Xd2zsU7DUsSaJp-D8-FbxhsTN78fk"

# ID Blog untuk posting
BLOG_ID = "6869652925231981095"

# Token akses Blogger API
#BLOGGER_ACCESS_TOKEN = access_token



def post_to_blogger_with_creds(title, content, categories, creds):
    try:
        service = build('blogger', 'v3', credentials=creds)
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


def format_content(article_text):
    # Pisahkan artikel berdasarkan baris dan hapus 5 baris pertama
    lines = article_text.split("\n")
    article_text = "\n".join(lines[3:]).strip()  # Ambil baris ke-4 dan seterusnya

    # Gantilah **teks** dengan <strong>teks</strong> tanpa terkena indentasi
    def replace_bold(match):
        return f"<strong style='display: inline;'>{match.group(1)}</strong>"

    formatted_text = re.sub(r"\*\*(.*?)\*\*", replace_bold, article_text)

    def replace_italic(match):
        return f"<em style='display: inline;'>{match.group(1)}</em>"

    # Kemudian ganti *italic*
    formatted_text = re.sub(r"\*(.*?)\*", replace_italic, formatted_text)

    # Bold nomor di awal kalimat (contoh: "1. ", "2) ")
    def replace_numbering(match):
        return f"<strong style='display: inline;'>{match.group(1)}</strong>{match.group(2)}"

    formatted_text = re.sub(r"^(\d+[.)])(\s+)", replace_numbering, formatted_text, flags=re.MULTILINE)


    # Konversi bullet list dengan `*` di awal baris menjadi `•` atau <ul><li>
    paragraphs = formatted_text.split("\n")
    formatted_paragraphs = []
    in_list = False  # Menandai apakah sedang berada dalam daftar

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue  # Lewati baris kosong

        if p.startswith("*"):  # Jika dimulai dengan '*', ubah ke bullet list
            if not in_list:
                formatted_paragraphs.append("<ul style='margin-left: 1rem;'>")  # Mulai daftar
                in_list = True
            formatted_paragraphs.append(f"<li>{p[1:].strip()}</li>")  # Simpan sebagai list item
        else:
            if in_list:
                formatted_paragraphs.append("</ul>")  # Tutup daftar jika sebelumnya dalam daftar
                in_list = False
            
            # Hapus indentasi jika paragraf diawali <strong>
            if re.match(r"^\s*<strong", p):  
                formatted_paragraphs.append(f"<p style='margin-bottom: 1em;'>{p}</p>")
            else:
                formatted_paragraphs.append(f"<p style='margin-bottom: 1em; text-indent: 2rem;'>{p}</p>")

    if in_list:
        formatted_paragraphs.append("</ul>")  # Pastikan daftar ditutup

    return "".join(formatted_paragraphs)



def extract_title(article_text):
    # Pisahkan artikel berdasarkan baris
    lines = article_text.split("\n")
    
    # Ambil baris pertama sebagai judul (baris pertama setelah menghapus 5 baris pertama)
    title = lines[2].split(":")[0].strip()  # Ambil judul dari baris ke-6
    return title

def get_unique_filename(base_name, extension):
    counter = 1
    file_name = f"{base_name}{extension}"
    while os.path.exists(file_name):
        file_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return file_name

def ensure_landscape(image):
    width, height = image.size
    if height > width:
        image = image.rotate(90, expand=True)
    return image

def upload_to_drive(file_path, file_name):
    # Metadata file yang akan diupload
    file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
    media = MediaFileUpload(file_path, mimetype='image/png')

    # Mengunggah file ke Google Drive
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    
    # Mendapatkan ID file yang baru diupload
    file_id = file.get('id')
    print(f"File berhasil diunggah ke Google Drive dengan ID: {file_id}")
    
    # Menambahkan izin akses publik (bisa dibaca oleh siapa saja)
    service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()
    print(f"File {file_name} sekarang dapat diakses secara publik.")
    
    # Mengembalikan direct link yang bisa digunakan di <img>
    direct_link = f"https://lh3.googleusercontent.com/d/{file_id}=s0"
    return direct_link

def get_blog_categories():
    if "credentials" not in st.session_state:
        st.error("Anda harus login terlebih dahulu.")
        return []
    
    creds = st.session_state.credentials
    access_token = creds.token

    # Ambil blog ID user yang sedang login
    user_info_url = "https://www.googleapis.com/blogger/v3/users/self/blogs"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)

    if user_response.status_code != 200:
        st.error("Gagal mengambil informasi blog user.")
        return []

    blogs = user_response.json().get("items", [])
    if not blogs:
        st.warning("User ini belum punya blog.")
        return []

    # Ambil blog ID pertama dari daftar blog user
    blog_id = blogs[0]["id"]

    # Lanjutkan ambil kategori dari blog tersebut
    posts_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?maxResults=10"
    posts_response = requests.get(posts_url, headers=headers)

    if posts_response.status_code == 200:
        posts = posts_response.json().get("items", [])
        labels = set()
        for post in posts:
            if "labels" in post:
                labels.update(post["labels"])
        return list(labels)
    else:
        st.error("Gagal mengambil postingan blog.")
        return []


def post_to_blogger(title, content, selected_categories):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {BLOGGER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Format artikel agar setiap baris menjadi paragraf
    formatted_content = "".join(f"<p>{line}</p>" for line in content.split("\n") if line.strip())

    data = {
        "kind": "blogger#post",
        "title": title,
        "content": formatted_content,
        "labels": selected_categories
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        post_url = result.get("url", "#")
        return True, post_url
    else:
        return False, response.text




def generate_article_and_image(user_input, user_input_2):
    try:
        # Generate artikel
        article_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Tulis artikel 850 kata dengan bahasa yang santai, human like, tentang: {user_input} . Artikel harus SEO-Friendly"
        )
        article_text = article_response.text
        formatted_content = "".join(f"<p>{line}</p>" for line in article_text.split("\n") if line.strip())
    except Exception as e:
        raise RuntimeError(f"Gagal generate artikel: {e}")

    image_url_1 = None
    image_url_2 = None

    try:
        # Generate gambar pertama
        image_prompt_1 = f"Buat gambar wide aspect ratio 16:9 berdasarkan keyword: {user_input_2}"
        image_response_1 = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=image_prompt_1,
            config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
        )
        image_path_1 = get_unique_filename("generated_image_1", ".png")
        for part in image_response_1.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image = Image.open(BytesIO(part.inline_data.data))
                image = ensure_landscape(image)
                image.save(image_path_1)
                image_url_1 = upload_to_drive(image_path_1, os.path.basename(image_path_1))
                break  # Stop setelah gambar pertama ditemukan
        if not image_url_1:
            raise ValueError("Gambar pertama tidak ditemukan di response Gemini.")
    except Exception as e:
        raise RuntimeError(f"Gagal generate gambar pertama: {e}")

    try:
        # Generate gambar kedua
        image_prompt_2 = f"Buat gambar wide aspect ratio 16:9 yang lain berdasarkan keyword: {user_input_2}"
        image_response_2 = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=image_prompt_2,
            config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
        )
        image_path_2 = get_unique_filename("generated_image_2", ".png")
        for part in image_response_2.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image = Image.open(BytesIO(part.inline_data.data))
                image = ensure_landscape(image)
                image.save(image_path_2)
                image_url_2 = upload_to_drive(image_path_2, os.path.basename(image_path_2))
                break
        if not image_url_2:
            raise ValueError("Gambar kedua tidak ditemukan di response Gemini.")
    except Exception as e:
        raise RuntimeError(f"Gagal generate gambar kedua: {e}")

    try:
        # Siapkan konten untuk Blogger
        title = extract_title(article_text)
        formatted_content = format_content(article_text)
        blogger_content = f"""
        <h1 style='text-align: center;'>{user_input}</h1>
        <br>
        <img src='{image_url_1}' alt='{user_input}' style='margin-bottom: 1rem;'>
        <br>
        {formatted_content}
        <img src='{image_url_2}' alt='{user_input_2}' style='margin-bottom: 1rem;'>
        <br>
        """
        return title, blogger_content
    except Exception as e:
        raise RuntimeError(f"Gagal menyiapkan konten Blogger: {e}")


if __name__ == "__main__":
    generate_article_and_image(user_input, user_input_2)
