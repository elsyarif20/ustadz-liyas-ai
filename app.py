import streamlit as st
from google import genai
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Ustadz Liyas Syarifudin", page_icon="👳‍♂️")
st.title("👳‍♂️ Ustadz Liyas Syarifudin")
st.markdown("*Teman diskusi, analisis, dan curhat yang bijak.*")

# --- SIDEBAR (API KEY & NAMA) ---
with st.sidebar:
    st.header("Pengaturan")
    api_key = st.text_input("Gemini API Key", type="password")
    user_name = st.text_input("Siapa nama kamu?", value="Saudaraku")
    st.divider()
    # Tombol "+" di sidebar untuk upload file agar chat tetap bersih
    st.write("📁 **Tambah Lampiran (+)**")
    uploaded_file = st.file_uploader("Unggah Gambar, Dokumen, atau Kode", type=['jpg', 'jpeg', 'png', 'pdf', 'txt', 'py', 'cpp', 'js'])

# --- INISIALISASI SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "file_info" in message:
            st.caption(f"📎 Lampiran: {message['file_info']}")

# --- LOGIKA CHAT ---
if prompt := st.chat_input("Ketik pesan atau tanya apa saja ke Ustadz..."):
    if not api_key:
        st.error("Masukkan API Key dulu di sidebar, Bro!")
    else:
        client = genai.Client(api_key=api_key)
        
        # 1. Tampilkan pesan user di UI
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 2. Persiapkan input untuk AI
        inputs = [f"Nama user: {user_name}. Konteks: {prompt}"]
        file_info = None

        # 3. Jika ada file yang diunggah
        if uploaded_file:
            with st.spinner("Mengunggah file..."):
                # Simpan sementara
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Upload ke Google File API
                g_file = client.files.upload(path=uploaded_file.name)
                inputs.append(g_file)
                file_info = uploaded_file.name
                os.remove(uploaded_file.name) # Bersihkan local storage

        # Tambahkan ke riwayat chat
        st.session_state.messages.append({"role": "user", "content": prompt, "file_info": file_info})

        # 4. Respon AI
        with st.chat_message("assistant"):
            with st.spinner("Ustadz sedang berpikir..."):
                persona = (
                    "Kamu adalah Ustadz Liyas Syarifudin. Kamu bijak, memotivasi, dan menghibur. "
                    "Jika user mengirim gambar wajah, analisis auranya dengan positif. "
                    "Jika user mengirim kode atau file, bantu jelaskan atau perbaiki dengan bahasa yang mudah dimengerti. "
                    "Jangan lebay, tetap santai tapi berwibawa."
                )
                
                try:
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=[persona] + inputs
                    )
                    ai_text = response.text
                    st.markdown(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                except Exception as e:
                    st.error(f"Waduh, ada kendala: {e}")

# --- RESET FILE UPLOADER ---
if uploaded_file:
    st.sidebar.info("File siap dikirim bersama pesan chat!")