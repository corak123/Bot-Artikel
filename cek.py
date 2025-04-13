import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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
                        # success, result = post_to_blogger_with_creds(user_input, content, selected_categories, st.session_state.credentials)
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
