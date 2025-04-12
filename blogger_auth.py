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
                transform: scale(1.1);
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
        st.session_state.serial_verified = True
        st.stop()


# --- Daftar serial valid
VALID_SERIALS = ["ABC123", "XYZ789", "SN-2025-001"]

# # --- Cek status verifikasi serial
# if "serial_verified" not in st.session_state:
#     st.session_state.serial_verified = False

# --- CSS untuk styling
st.markdown("""
    <style>
    .serial-box {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 400px;
        margin: auto;
        text-align: center;
    }
    .serial-input input {
        padding: 0.75rem;
        font-size: 1rem;
        width: 100%;
        border: 1px solid #ccc;
        border-radius: 8px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .serial-btn {
        background-color: #4CAF50;
        color: white;
        padding: 0.6rem 1.5rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
        transition: 0.3s ease;
    }
    .serial-btn:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

def serial_number():
    # --- Tampilan form serial number
    if st.session_state.get("serial_verified") is False:
        st.markdown('<div class="serial-box">', unsafe_allow_html=True)
        st.markdown("### 🔒 Masukkan Serial Number")
    
        serial = st.text_input("", placeholder="Contoh: ABC123", key="serial", label_visibility="collapsed")
    
        if st.button("✅ Verifikasi", key="verify_btn"):
            if serial in VALID_SERIALS:
                st.session_state.serial_verified = True
                st.success("✅ Serial number valid. Silakan lanjut.")
                #st.rerun()
                get_authenticated_service()
            else:
                st.error("❌ Serial number tidak valid. Coba lagi.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Kalau sudah verified
    else:
        st.success("✅ Serial number terverifikasi. Akses diberikan!")
        # lanjut ke aplikasi utama kamu, misal login Google atau dashboard


