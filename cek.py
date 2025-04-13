import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
import json
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


def logout():
    for key in ["credentials", "user_email", "user_name", "user_picture", "code"]:
        if key in st.session_state:
            del st.session_state[key]
            st.markdown(
                '<meta http-equiv="refresh" content="0;url=https://bot-artikel-auto.streamlit.app/">',
                unsafe_allow_html=True
            )
            st.stop()
    st.rerun()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
# Inisialisasi client
client = genai.Client(api_key=GEMINI_API_KEY)
FOLDER_ID = st.secrets["google_drive"]["FOLDER_ID"]
# Autentikasi dengan service account
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_FILE = st.secrets["gcp_service_account"]
creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build("drive", "v3", credentials=creds)

def get_unique_filename(base_name, extension):
    counter = 1
    file_name = f"{base_name}{extension}"
    while os.path.exists(file_name):
        file_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return file_name

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

def extract_title(article_text):
    # Pisahkan artikel berdasarkan baris
    lines = article_text.split("\n")
    
    # Ambil baris pertama sebagai judul (baris pertama setelah menghapus 5 baris pertama)
    title = lines[2].split(":")[0].strip()  # Ambil judul dari baris ke-6
    return title

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


def ensure_landscape(image):
    width, height = image.size
    if height > width:
        image = image.rotate(90, expand=True)
    return image

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


def UI():
    st.title("🤖 Auto Posting ke Blogger dengan Gemini AI")
    st.markdown("""
    Masukkan topik artikel dan prompt untuk Gemini AI. Bot ini akan:
    1. Menghasilkan artikel otomatis
    2. Menghasilkan gambar otomatis
    3. Artikel SEO Firendly
    4. Posting langsung ke Blogger melalui API
    """)
    
    user_input = st.text_input("Masukkan judul artikel:")
    user_input_2 = st.text_area("Masukkan keyword gambar:", height=100)
    #creds = st.session_state.credentials
    
    def submit_button():
        col1, col2 = st.columns(2)
    
        with col1:
            generate_clicked = st.button("🚀 Generate & Posting")
    
        with col2:
            cancel_clicked = st.button("❌ Batal")
    
        # Jika user klik batal
        if cancel_clicked:
            st.session_state["cancelled"] = True
            st.warning("🚫 Pembuatan artikel dibatalkan.")
            return  # Stop fungsi agar tidak lanjut ke bawah
    
        # Jika user klik generate
        if generate_clicked:
            # Cek apakah user sebelumnya sudah klik batal
            if st.session_state.get("cancelled"):
                st.warning("Aksi dibatalkan. Silakan klik Generate lagi jika ingin memulai.")
                # Reset cancelled flag agar bisa jalan lagi
                st.session_state["cancelled"] = False
                return
    
            if not user_input or not user_input_2:
                st.warning("Harap isi Topik dan Keyword terlebih dahulu.")
            # elif not selected_categories:
            #     st.warning("Pilih minimal satu kategori untuk postingan.")
            else:
                with st.spinner("Sedang memproses artikel dan memposting ke Blogger..."):
                    try:
                        title, content = generate_article_and_image(user_input, user_input_2)
                        success, result = post_to_blogger_with_creds(user_input, content, selected_categories, st.session_state.credentials)
                        st.info("Berhasil cuyyy.")
    
                        if success:
                            st.success("✅ Artikel berhasil diposting!")
                            # st.write(f"**Link Posting:** [Lihat artikel]({result})")
                            st.session_state["cancelled"] = False  # Reset batal setelah berhasil
                        else:
                            st.error(f"❌ Gagal posting: {result}")
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan: {e} silahkan coba lagi...")

    submit_button()
    if st.button("🔓 Logout"):
        logout()
