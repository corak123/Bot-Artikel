import streamlit as st
from blogger_auth import get_authenticated_service

st.set_page_config(page_title="Bot Artikel Blogger Otomatis", page_icon="🤖")
st.title("🤖 Bot Artikel Blogger Otomatis")

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
