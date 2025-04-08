import streamlit as st
from cek import generate_article_and_image, get_blog_categories, post_to_blogger_with_creds
from blogger_auth import get_authenticated_service, save_credentials_to_pickle, get_user_info

#st.set_page_config(page_title="Auto Posting Blogger Bot", layout="centered")
#st.title("🤖 Auto Posting ke Blogger dengan Gemini AI")

# 2. Setelah login, tampilkan interface utama
st.markdown("""
Masukkan topik artikel dan prompt untuk Gemini AI. Bot ini akan:
1. Menghasilkan artikel otomatis
2. Menghasilkan gambar otomatis
3. Artikel SEO Firendly
4. Posting langsung ke Blogger melalui API
""")


user_input = st.text_input("Masukkan judul artikel:")
user_input_2 = st.text_area("Masukkan keyword gambar:", height=100)

categories = get_blog_categories()
selected_categories = st.multiselect("Pilih kategori untuk postingan:", options=categories)

def submit_button():
    col1, col2 = st.columns(2)

    with col1:
        generate_clicked = st.button("🚀 Generate & Posting")

    with col2:
        cancel_clicked = st.button("❌ Batal")

    # Jika user klik batal
    if cancel_clicked:
        st.session_state["cancelled"] = True
        st.warning("🚫 Pembuatan artikel dibatalkan.")
        return  # Stop fungsi agar tidak lanjut ke bawah

    # Jika user klik generate
    if generate_clicked:
        # Cek apakah user sebelumnya sudah klik batal
        if st.session_state.get("cancelled"):
            st.warning("Aksi dibatalkan. Silakan klik Generate lagi jika ingin memulai.")
            # Reset cancelled flag agar bisa jalan lagi
            st.session_state["cancelled"] = False
            return

        if not user_input or not user_input_2:
            st.warning("Harap isi Topik dan Keyword terlebih dahulu.")
        elif not selected_categories:
            st.warning("Pilih minimal satu kategori untuk postingan.")
        else:
            with st.spinner("Sedang memproses artikel dan memposting ke Blogger..."):
                try:
                    title, content = generate_article_and_image(user_input, user_input_2)
                    success, result = post_to_blogger_with_creds(user_input, content, selected_categories, st.session_state.credentials)

                    if success:
                        st.success("✅ Artikel berhasil diposting!")
                        st.write(f"**Link Posting:** [Lihat artikel]({result})")
                        st.session_state["cancelled"] = False  # Reset batal setelah berhasil
                    else:
                        st.error(f"❌ Gagal posting: {result}")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e} silahkan coba lagi...")


# Tombol Logout
def logout():
    """Fungsi logout dan tandai bahwa user baru logout"""
    st.session_state.pop("credentials", None)
    st.session_state.just_logged_out = True
    st.rerun()

# 🔧 CSS untuk mengatur lebar sidebar
st.markdown("""
    <style>
        /* Ubah ukuran sidebar sebenarnya */
        section[data-testid="stSidebar"] {
            min-width: 0px;
            max-width: 200px;
            width: 200px;
        }

        /* Supaya kontennya ikut muat */
        section[data-testid="stSidebar"] > div:first-child {
            width: 200px;
        }

        /* (Opsional) agar konten utama tidak terlalu sempit */
        div[data-testid="stAppViewContainer"] > div:nth-child(1) {
            margin-left: 320px;
        }
    </style>
""", unsafe_allow_html=True)



# 🖼️ Sidebar Profil
def sidebar_profile():
    with st.sidebar:
        st.markdown("## 👤 Profil")
        if "user_picture" in st.session_state and st.session_state.user_picture:
            st.image(st.session_state.user_picture, width=80)
        if "user_name" in st.session_state:
            st.markdown(f"**{st.session_state.user_name}**")
        if "user_email" in st.session_state:
            st.caption(st.session_state.user_email)
        st.markdown("---")
        if st.button("🚪 Logout", key="sidebar_logout"):
            logout()

# def show_login_prompt():
#     st.info("🚪 Anda telah logout.")
#     st.write("🔐 Klik tombol di bawah untuk login dengan Google")

#     if st.button("Login dengan Google"):
#         credentials = get_authenticated_service()

#         if credentials:
#             st.write("🔐 berhasil kredensial")
#             try:
#                 user_info = get_user_info(credentials)
#                 st.session_state.credentials = credentials
#                 st.session_state.user_email = user_info["email"]
#                 st.session_state.user_name = user_info["name"]
#                 st.session_state.user_picture = user_info["picture"]
#                 save_credentials_to_pickle(credentials, user_info["email"])
#                 st.session_state.pop("just_logged_out", None)
#                 st.success("✅ Login berhasil!")
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"Gagal ini login: {e}")
#         else:
#             st.warning("🕒 Menunggu kode otentikasi dari Google...")



# ✅ Cek apakah user baru logout
if st.session_state.get("just_logged_out"):
    #show_login_prompt()
    st.stop()

# ✅ Jika belum login
# if "credentials" not in st.session_state:
#     st.info("🔐 Silakan login terlebih dahulu.")
#     if st.button("🔐 Login dengan Google"):
#         try:
#             credentials  = get_authenticated_service()
#             user_info = get_user_info(credentials )
#             st.session_state.credentials = credentials 
#             st.session_state.user_email = user_info["email"]
#             st.session_state.user_name = user_info["name"]
#             st.session_state.user_picture = user_info["picture"]
#             save_credentials_to_pickle(credentials , user_info["email"])
#             st.success("✅ Login berhasil!")
#             st.rerun()
#         except Exception as e:
#             st.error(f"Gagal sihh login: {e}")
#     st.stop()

# ✅ Jika sudah login, tampilkan konten dan tombol logout
# st.success("✅ Selamat datang! Anda sudah login.")
#sidebar_profile()
#submit_button()
if st.button("🚪 Logout"):  
    logout()

st.markdown("---")
st.caption("Made with ❤️ by Corak_Desain")
