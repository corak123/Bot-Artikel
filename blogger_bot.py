import streamlit as st
from blogger_auth import get_authenticated_service

st.title("🤖 Bot Artikel Blogger Otomatis")

if "credentials" not in st.session_state:
    get_authenticated_service()

# Setelah login berhasil
creds = st.session_state["credentials"]
email = st.session_state["user_email"]
name = st.session_state.get("user_name", "kamu")
picture = st.session_state.get("user_picture")
if picture:
    st.image(picture, width=100)


st.success(f"Hai, {name}!")
st.image(picture, width=100)

# --- LOGOUT
if st.button("🔓 Logout"):
    for key in ["credentials", "user_email", "user_name", "user_picture"]:
        st.session_state[key] = None
    st.success("✅ Kamu berhasil logout.")
    st.rerun()
