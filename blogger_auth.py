import json
import requests
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

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

# Fungsi untuk ambil info user dari token
def get_user_info(creds):
    response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'access_token': creds.token}
    ).json()

    return {
        "email": response.get("email", "unknown_user"),
        "name": response.get("name", "Unknown Name"),
        "picture": response.get("picture", None)
    }

# Fungsi login dan ambil credentials
def get_authenticated_service():
    creds = None
    code = None

    # Cek apakah sudah ada auth code dari URL
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri="https://bot-artikel-auto.streamlit.app/"
    )
    query_params = st.query_params
    code = query_params.get("code")
    st.write("Isi kode:", code)

    if code:
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            user_info = get_user_info(creds)

            # Simpan di session
            st.session_state["credentials"] = creds
            st.session_state["user_email"] = user_info["email"]
            st.session_state["user_name"] = user_info["name"]
            st.session_state["user_picture"] = user_info["picture"]

            st.success("✅ Login berhasil!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Gagal login: {e}")
            st.stop()
    else:
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        # st.markdown(f"[🔐 Klik di sini untuk login Google]({auth_url})", unsafe_allow_html=True)
        # st.stop()
        st.markdown("""
            <style>
            .hover-scale:hover {
                transform: scale(1.2);
                transition: transform 0.3s ease;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <a href="{auth_url}" target="_blank">
                <button class="hover-scale" style="
                    background-color: #4285F4;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    cursor: pointer;
                ">
                    🔐 Login dengan Google
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )



