import os
import pickle
import requests
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

# SCOPES untuk Blogger API
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_user_info(credentials):
    response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'access_token': credentials.token}
    ).json()

    return {
        "email": response.get("email", "unknown_user"),
        "name": response.get("name", "Unknown Name"),
        "picture": response.get("picture", None)
    }

def save_credentials_to_pickle(credentials, email):
    token_dir = "tokens"
    os.makedirs(token_dir, exist_ok=True)
    safe_email = email.replace("@", "_").replace(".", "_")
    token_path = os.path.join(token_dir, f"token_{safe_email}.pkl")
    
    with open(token_path, 'wb') as token_file:
        pickle.dump(credentials, token_file)

def get_authenticated_service():
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f"### 🔗 [Klik di sini untuk login dengan Google]({auth_url})")

    code = st.text_input("📋 Setelah login, tempelkan kode otentikasi di sini:")
    if code:
        try:
            flow.fetch_token(code=code)
            return flow.credentials
        except Exception as e:
            st.error(f"Gagal mengambil token: {e}")
            return None
    return None

# Bagian login Streamlit
def login_with_google():
    if "credentials" not in st.session_state:
        st.title("🤖 Bot Artikel Blogger")
        st.info("🔐 Silakan login untuk mulai menggunakan bot ini.")
        credentials = get_authenticated_service()
        if credentials:
            user_info = get_user_info(credentials)
            st.session_state.credentials = credentials
            st.session_state.user_email = user_info["email"]
            st.session_state.user_name = user_info["name"]
            st.session_state.user_picture = user_info["picture"]
            save_credentials_to_pickle(credentials, user_info["email"])
            st.success(f"✅ Berhasil login sebagai {user_info['email']}")
            st.rerun()
        st.stop()
    else:
        st.write(f"✅ Anda sudah login sebagai {st.session_state.user_email}")
