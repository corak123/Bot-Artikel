import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
import streamlit as st



#CREDENTIALS_FILE = 'client_secret.json'  # Ganti sesuai file kamu

# Fungsi untuk mendapatkan email user
def get_user_email(credentials):
    response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'access_token': creds.token}
    ).json()
    return response.get("email", "unknown_user")

def get_user_info(credentials):
    response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'access_token': creds.token}
    ).json()

    return {
        "email": response.get("email", "unknown_user"),
        "name": response.get("name", "Unknown Name"),
        "picture": response.get("picture", None)
    }


# Fungsi untuk menyimpan kredensial
def save_credentials_to_pickle(credentials, email):
    token_dir = "tokens"
    os.makedirs(token_dir, exist_ok=True)

    safe_email = email.replace("@", "_").replace(".", "_")
    token_path = os.path.join(token_dir, f"token_{safe_email}.pkl")
    
    with open(token_path, 'wb') as token_file:
        pickle.dump(creds, token_file)

# Fungsi untuk mendapatkan kredensial yang terautentikasi
def get_authenticated_service():
    creds = None
    token_dir = "tokens"
    os.makedirs(token_dir, exist_ok=True)

    # Cek token yang sudah ada
    for token_file in os.listdir(token_dir):
        with open(os.path.join(token_dir, token_file), 'rb') as token:
            temp_creds = pickle.load(token)
            if temp_creds and temp_creds.valid:
                return temp_creds
            elif temp_creds and temp_creds.expired and temp_creds.refresh_token:
                temp_creds.refresh(Request())
                return temp_creds

    # Jalankan login console
    st.warning("🔐 Salin dan buka link login Google di terminal. Setelah login, tempel kode otentikasi.")
    client_config = {
    "installed": {
        "client_id": st.secrets["google_oauth"]["client_id"],
        "client_secret": st.secrets["google_oauth"]["client_secret"],
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}
    
    scopes = ["https://www.googleapis.com/auth/blogger"]
    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
    credentials = flow.run_console()



    return credentials


# Streamlit bagian login
if "credentials" not in st.session_state:
    st.title("🤖 Bot Artikel dan Posting Blogger Otomatis")
    st.info("🔐 Silakan login dulu untuk mulai menggunakan bot ini.")
    if st.button("Login dengan Google"):
        try:
            creds = get_authenticated_service()  # Mendapatkan kredensial dari fungsi
            st.session_state.credentials = creds
            # Mendapatkan email dari kredensial
            user_info = get_user_info(creds)
            st.session_state.user_email = user_info["email"]
            st.session_state.user_name = user_info["name"]
            st.session_state.user_picture = user_info["picture"]
            save_credentials_to_pickle(creds, user_info["email"])

            st.success("✅ Berhasil login!")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal login: {e}")
    st.stop()
else:
    # Jika sudah login, tampilkan tombol logout
    st.write("✅ Anda sudah login!")
    
