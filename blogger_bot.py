import streamlit as st
from blogger_auth import get_authenticated_service

st.set_page_config(page_title="Bot Artikel Blogger Otomatis", page_icon="🤖")
st.title("🤖 Bot Artikel Blogger Otomatis")

def login():
    # Simulasi proses login dengan tombol
    if st.button("Login"):
        # Biasanya, di sini proses autentikasi, misalnya dengan OAuth atau mekanisme login lainnya
        # Ini misalnya kode yang didapat setelah login
        st.session_state.code = code  # Simpan code di session_state agar tetap ada selama sesi
        st.success("Login berhasil!")
        return code
    return None

# Fungsi Logout
def logout():
    for key in ["credentials", "user_email", "user_name", "user_picture"]:
        if key in st.session_state:
            del st.session_state[key]
            st.session_state.code = None  # Kosongkan code
    st.success("✅ Kamu berhasil logout.")
    st.rerun()

if "credentials" not in st.session_state:
    st.info("Silakan login dulu ya.")
    get_authenticated_service()

# Jika sudah login
if "credentials" in st.session_state:
    creds = st.session_state["credentials"]
    name = st.session_state.get("user_name", "kamu")
    email = st.session_state.get("user_email")
    picture = st.session_state.get("user_picture")

    st.success(f"Hai, {name}!")
    if picture:
        st.image(picture, width=100)

    if st.button("🔓 Logout"):
        logout()
