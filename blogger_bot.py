import streamlit as st
from blogger_auth import get_auth_url, handle_auth_callback

st.set_page_config(page_title="Bot Blogger Otomatis", page_icon="🤖")

# Jika user belum login
if "credentials" not in st.session_state:
    st.title("🤖 Bot Artikel dan Posting Blogger Otomatis")
    st.info("🔐 Silakan login dengan Google terlebih dahulu.")

    # Tangani redirect URL (callback setelah login)
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        with st.spinner("Sedang menyelesaikan proses login..."):
            try:
                code = query_params["code"][0]
                if handle_auth_callback(code):
                    st.success("✅ Login berhasil!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Gagal login: {e}")

    # Tampilkan tombol login jika belum ada kode
    else:
        if st.button("Login dengan Google"):
            auth_url = get_auth_url()
            st.markdown(f"[Klik di sini untuk login]({auth_url})")
        st.stop()

# Jika user sudah login
else:
    st.success(f"Selamat datang, {st.session_state.user_name} 👋")
    st.image(st.session_state.user_picture, width=100)
    st.write(f"📧 Email: {st.session_state.user_email}")

    st.write("---")
    st.subheader("✅ Bot Siap Digunakan")

    # Di sini kamu bisa menambahkan logika upload artikel, posting ke Blogger, dsb
    st.write("Silakan lanjutkan fitur bot kamu di sini... 🚀")
