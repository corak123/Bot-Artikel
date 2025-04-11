import streamlit as st
from blogger_auth import get_auth_url, handle_auth_callback, get_drive_service
from drive_token_utils import save_credentials_to_drive
from cek import generate_article_and_image, post_to_blogger_with_creds

st.set_page_config(page_title="Bot Blogger Otomatis", page_icon="🤖")

if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_picture" not in st.session_state:
    st.session_state.user_picture = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

for key in ["user_email", "user_name", "user_picture"]:
    if key not in st.session_state:
        st.session_state[key] = None


# Jika user belum login
if "credentials" not in st.session_state:
    st.title("🤖 Bot Artikel dan Posting Blogger Otomatis")
    st.info("🔐 Silakan login dengan Google terlebih dahulu.")

    # Tangani redirect URL
    query_params = st.query_params
    if "code" in query_params:
        with st.spinner("Sedang menyelesaikan proses login..."):
            try:
                code = query_params["code"][0]
                if handle_auth_callback(code):
                    # Simpan token ke Google Drive
                    try:
                        drive_service = get_drive_service()
                        save_credentials_to_drive(
                            credentials=st.session_state.credentials,
                            user_email=st.session_state.user_email,
                            drive_service=drive_service
                        )
                        st.success("✅ Token berhasil disimpan di Google Drive!")
                    except Exception as e:
                        st.warning(f"⚠️ Token tidak berhasil disimpan: {e}")
                    # Simpan ke lokal
                    try:
                        save_credentials_to_local(
                            credentials=st.session_state.credentials,
                            user_email=st.session_state.user_email
                        )
                        st.success("✅ Token juga disimpan di komputer lokal!")
                    except Exception as e:
                        st.warning(f"⚠️ Gagal simpan token ke lokal: {e}")
                    st.success("✅ Login berhasil!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Gagal login: {e}")
    else:
        if st.button("Login dengan Google"):
            auth_url = get_auth_url()
            st.markdown(f"[Klik di sini untuk login]({auth_url})")
        st.stop()

# Jika user sudah login
else:
    st.success(f"Selamat datang, {st.session_state.user_name} 👋")
    #st.image(st.session_state.user_picture, width=100)
    st.write(f"📧 Email: {st.session_state.user_email}")
    st.write("---")
    creds = st.session_state.credentials

    st.subheader("✅ Bot Siap Digunakan")
    st.write("Silakan lanjutkan fitur bot kamu di sini... 🚀")
    st.subheader("✅ Bot Siap Digunakan")

    # Input dari user
    judul = st.text_input("Masukkan topik artikel", placeholder="Contoh: Teknologi Masa Depan")
    
    # Tombol generate
    if st.button("🚀 Generate Artikel dan Gambar") and judul:
        title, content = generate_article_and_image(judul, judul)
        st.markdown(content, unsafe_allow_html=True)

