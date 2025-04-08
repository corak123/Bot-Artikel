import streamlit as st
from cek import generate_article_and_image, post_to_blogger_with_creds, create_drive_service_from_secrets, save_credentials_to_drive
from blogger_auth import get_authenticated_service, save_credentials_to_pickle, get_user_info
from drive_token_utils import upload_token_to_drive, download_token_from_drive

st.markdown("""
Masukkan topik artikel dan prompt untuk Gemini AI. Bot ini akan:
1. Menghasilkan artikel otomatis
2. Menghasilkan gambar otomatis
3. Artikel SEO Friendly
4. Posting langsung ke Blogger melalui API
""")

user_input = st.text_input("Masukkan judul artikel:")
user_input_2 = st.text_area("Masukkan keyword gambar:", height=100)

folder_id = "1d3NFHLCxqVWJpGGO4dwbPmDok4vrkIX2"  # ID folder token di Google Drive

# Fungsi tombol utama
def submit_button():
    col1, col2 = st.columns(2)

    with col1:
        generate_clicked = st.button("🚀 Generate & Posting")

    with col2:
        cancel_clicked = st.button("❌ Batal")

    if cancel_clicked:
        st.session_state["cancelled"] = True
        st.warning("🚫 Pembuatan artikel dibatalkan.")
        return

    if generate_clicked:
        if st.session_state.get("cancelled"):
            st.warning("Aksi dibatalkan. Silakan klik Generate lagi jika ingin memulai.")
            st.session_state["cancelled"] = False
            return

        if not user_input or not user_input_2:
            st.warning("Harap isi Topik dan Keyword terlebih dahulu.")
        else:
            with st.spinner("Sedang memproses artikel dan memposting ke Blogger..."):
                try:
                    title, content = generate_article_and_image(user_input, user_input_2)
                    success, result = post_to_blogger_with_creds(user_input, content, ["Teknologi"], st.session_state.credentials)

                    if success:
                        st.success("✅ Artikel berhasil diposting!")
                        st.write(f"**Link Posting:** [Lihat artikel]({result})")
                        st.session_state["cancelled"] = False
                    else:
                        st.error(f"❌ Gagal posting: {result}")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e} silahkan coba lagi...")

# Tombol Logout
def logout():
    st.session_state.pop("credentials", None)
    st.session_state.just_logged_out = True
    st.rerun()

# CSS
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            min-width: 0px;
            max-width: 200px;
            width: 200px;
        }
        section[data-testid="stSidebar"] > div:first-child {
            width: 200px;
        }
        div[data-testid="stAppViewContainer"] > div:nth-child(1) {
            margin-left: 320px;
        }
    </style>
""", unsafe_allow_html=True)

# Autentikasi dan token
creds, drive_service = create_drive_service_from_secrets()

if "credentials" not in st.session_state:
    st.info("🔐 Silakan login terlebih dahulu.")
    if st.button("🔐 Login dengan Google"):
        try:
            credentials = get_authenticated_service()
            user_info = get_user_info(credentials)
            st.session_state.credentials = credentials
            st.session_state.user_email = user_info["email"]
            st.session_state.user_name = user_info["name"]
            st.session_state.user_picture = user_info["picture"]
            save_credentials_to_pickle(credentials, user_info["email"])
            upload_token_to_drive(drive_service, credentials, user_info["email"], folder_id)
            st.success("✅ Login berhasil!")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal login: {e}")
    st.stop()

# Sidebar profil
with st.sidebar:
    st.markdown("## 👤 Profil")
    if "user_picture" in st.session_state:
        st.image(st.session_state.user_picture, width=80)
    if "user_name" in st.session_state:
        st.markdown(f"**{st.session_state.user_name}**")
    if "user_email" in st.session_state:
        st.caption(st.session_state.user_email)
    st.markdown("---")
    if st.button("🚪 Logout", key="sidebar_logout"):
        logout()

submit_button()

if st.button("🚪 Logout Bawah"):
    logout()

st.markdown("---")
st.caption("Made with ❤️ by Corak_Desain")
