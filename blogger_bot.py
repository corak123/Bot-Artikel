from blogger_auth import get_authenticated_service

st.title("🤖 Bot Artikel Blogger Otomatis")

if "credentials" not in st.session_state:
    get_authenticated_service()

# Setelah login berhasil
creds = st.session_state["credentials"]
email = st.session_state["user_email"]
name = st.session_state["user_name"]
picture = st.session_state.get("user_picture")

st.success(f"Hai, {name}!")
st.image(picture, width=100)
