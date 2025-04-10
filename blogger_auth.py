import os
import pickle
import json
import requests
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from drive_token_utils import upload_token_to_drive, load_token_from_drive

SCOPES = ['https://www.googleapis.com/auth/blogger']

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


def get_auth_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

def handle_auth_callback(auth_code, flow):
    flow.fetch_token(code=auth_code)
    credentials = flow.credentials
    print(credentials.valid)  # True kalau masih aktif
    return credentials

def get_drive_service():
    return build("drive", "v3", credentials=st.session_state.credentials)

# Fungsi login dan ambil credentials
def get_authenticated_service():
    creds = None

    if "user_email" in st.session_state:
        creds = load_token_from_drive(st.session_state["user_email"])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    if not creds or not creds.valid:
        # Login OAuth
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='https://bot-artikel-auto.streamlit.app/'
        )
        query_params = st.query_params
        code = query_params.get("code")
        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.success("✅ Login Google berhasil!")
            return creds
        else:
            auth_url, _ = flow.authorization_url(
                prompt='consent',
                access_type='offline',
                include_granted_scopes='true'
            )
            st.markdown(f"[Klik di sini untuk login Google]({auth_url})", unsafe_allow_html=True)
            st.stop()

        flow.fetch_token(code=code)
        creds = flow.credentials
        st.success("✅ Login Google berhasil!")
        return creds
        # auth_url, _ = flow.authorization_url(
        #     access_type='offline',
        #     prompt='consent'
        # )

        # st.markdown(f"🔐 [Klik untuk login dengan Google]({auth_url})", unsafe_allow_html=True)
        # # st.stop()
        # code = st.text_input("Masukkan kode autentikasi Google di sini:")
        
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"][0]
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
        
                if creds and creds.valid:
                    user_info = get_user_info(creds)
                    st.session_state["credentials"] = creds
                    st.session_state["user_email"] = user_info["email"]
                    st.session_state["user_name"] = user_info["name"]
                    st.session_state["user_picture"] = user_info["picture"]
        
                    upload_token_to_drive(user_info["email"], creds)
                    save_credentials_to_local(creds, user_info["email"])
        
                    st.success("✅ Login berhasil!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Token tidak valid.")
            except Exception as e:
                st.error(f"❌ Gagal ambil token: {e}")

    return creds

# UI Login
if "credentials" not in st.session_state:
    st.title("🤖 Bot Artikel Blogger Otomatis")
    st.info("🔐 Silakan login untuk menggunakan aplikasi.")
    creds = get_authenticated_service()
    if creds:
        st.session_state["credentials"] = creds
        st.rerun()
    st.stop()
