import streamlit as st

def UI():
    st.title("🤖 Auto Posting ke Blogger dengan Gemini AI")
    st.markdown("""
    Masukkan topik artikel dan prompt untuk Gemini AI. Bot ini akan:
    1. Menghasilkan artikel otomatis
    2. Menghasilkan gambar otomatis
    3. Artikel SEO Firendly
    4. Posting langsung ke Blogger melalui API
    """)
    
    user_input = st.text_input("Masukkan judul artikel:")
    user_input_2 = st.text_area("Masukkan keyword gambar:", height=100)
    creds = st.session_state.credentials
    
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
            # elif not selected_categories:
            #     st.warning("Pilih minimal satu kategori untuk postingan.")
            else:
                with st.spinner("Sedang memproses artikel dan memposting ke Blogger..."):
                    try:
                        # title, content = generate_article_and_image(user_input, user_input_2)
                        # success, result = post_to_blogger_with_creds(user_input, content, selected_categories, st.session_state.credentials)
                        st.info("Berhasil cuyyy.")
    
                        if success:
                            st.success("✅ Artikel berhasil diposting!")
                            # st.write(f"**Link Posting:** [Lihat artikel]({result})")
                            st.session_state["cancelled"] = False  # Reset batal setelah berhasil
                        else:
                            st.error(f"❌ Gagal posting: {result}")
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan: {e} silahkan coba lagi...")
