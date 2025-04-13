import streamlit as st
from blogger_auth import get_authenticated_service, serial_number, get_user_info
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from cek import UI


#st.set_page_config(page_title="Bot Artikel Blogger Otomatis", page_icon="🤖")
st.title("🤖 Bot Artikel Blogger Otomatis")

# --- Inisialisasi session state ---
if "serial_verified" not in st.session_state:
    st.session_state.serial_verified = False

# Fungsi Logout
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


if "credentials" not in st.session_state:
    SCOPES = [
        "https://www.googleapis.com/auth/blogger",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    
    # Ambil client_id dan client_secret dari st.secrets
    CLIENT_ID = st.secrets["google_oauth"]["client_id"]
    CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
    
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["https://bot-artikel-auto.streamlit.app/"]
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri="https://bot-artikel-auto.streamlit.app/"
    )
    query_params = st.query_params
    code = query_params.get("code")
    if code:
        flow.fetch_token(code=code)
        creds = flow.credentials
        st.session_state["credentials"] = creds
        user_info = get_user_info(creds)
        # Simpan di session
        st.session_state["credentials"] = creds
        st.session_state["user_email"] = user_info["email"]
        st.session_state["user_name"] = user_info["name"]
        st.session_state["user_picture"] = user_info["picture"]
        st.session_state["serial_verified"] = True  # <--- Tambahkan ini      
    else:
        st.info("Silakan login dulu ya.")
        serial_number()

# Jika sudah login
if "credentials" in st.session_state:
    creds = st.session_state["credentials"]
    name = st.session_state.get("user_name", "kamu")
    email = st.session_state.get("user_email")
    picture = st.session_state.get("user_picture")

    st.success(f"Hai, {name}!")
    if picture:
        st.image(picture, width=100)

    UI()
    if st.button("🔓 Logout"):
        logout()

