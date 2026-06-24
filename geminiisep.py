import streamlit as st

# ==============================================================================
# 1. VERIFIKASI INSTALASI LIBRARY PENDUKUNG
# ==============================================================================
try:
    from google import genai
    from google.genai import types
    LIBRARY_AMAN = True
except ImportError:
    LIBRARY_AMAN = False

# ==============================================================================
# 2. SETTING HALAMAN & STYLE DESAIN MODERN ELEGAN (HIJAU EMERALD & EMAS)
# ==============================================================================
st.set_page_config(
    page_title="Hidayah AI - Maharah Kitabah",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi CSS agar tampilan visual anggun dan cocok untuk MA
st.markdown("""
    <style>
    .stApp { background-color: #f6f8f6; }
    .main-title { color: #1b4d3e; font-family: 'Poppins', sans-serif; font-weight: 700; text-align: center; margin-top: -20px; margin-bottom: 5px; }
    .subtitle { color: #666666; text-align: center; margin-bottom: 35px; font-size: 1.1rem; }
    div.stButton > button:first-child { background-color: #1b4d3e; color: white; border-radius: 8px; border: 1px solid #d4af37; font-weight: bold; }
    div.stButton > button:first-child:hover { background-color: #153c30; color: #d4af37; }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

if not LIBRARY_AMAN:
    st.error("❌ Komponen Sistem Belum Lengkap!")
    st.info("Buka Terminal/CMD Anda terlebih dahulu, lalu ketik perintah berikut:\n\n`pip install google-genai streamlit` \n\nSetelah selesai instalasi, silakan jalankan kembali aplikasinya.")
    st.stop()

# ==============================================================================
# 3. MANAJEMEN MEMORI SESI (PREVENTING UNDEFINED STATE ERRORS)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_persona" not in st.session_state:
    st.session_state.current_persona = ""
if "current_materi" not in st.session_state:
    st.session_state.current_materi = ""
if "active_model" not in st.session_state:
    st.session_state.active_model = "gemini-2.5-flash"  # Default model

# ==============================================================================
# 4. GERBANG MASUK (HALAMAN LOGIN VALIDASI DENGAN SMART FALLBACK)
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>✨ HIDAYAH AI ✨</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Aplikasi Pembelajaran Mandiri Interaktif • Khusus Maharah Kitabah Kelas XI Madrasah Aliyah</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.write("### 🔑 Validasi Akses Siswa")
        username = st.text_input("Nama Lengkap Siswa", placeholder="Masukkan nama Anda...")
        api_key = st.text_input("Google AI Studio API Key", type="password", placeholder="Masukkan kunci AIzaSy...")
        
        st.markdown("---")
        if st.button("Masuk Ke Ruang Belajar 🚀", use_container_width=True):
            if username.strip() and api_key.strip():
                # --- PROSES VALIDASI SMART FALLBACK ---
                sukses_koneksi = False
                client_test = genai.Client(api_key=api_key)
                
                # Cek Model Utama (Gemini 2.5 Flash)
                try:
                    client_test.models.generate_content(model='gemini-2.5-flash', contents='Ping')
                    st.session_state.active_model = 'gemini-2.5-flash'
                    sukses_koneksi = True
                except Exception:
                    # Jika model utama gagal, otomatis coba Model Cadangan (Gemini 1.5 Flash)
                    try:
                        client_test.models.generate_content(model='gemini-1.5-flash', contents='Ping')
                        st.session_state.active_model = 'gemini-1.5-flash'
                        sukses_koneksi = True
                    except Exception:
                        sukses_koneksi = False

                if sukses_koneksi:
                    st.session_state.username = username
                    st.session_state.api_key = api_key
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    # Pesan jika kedua model gagal (kemungkinan besar API Key salah salin atau mati)
                    st.error("❌ Validasi Gagal! Periksa kembali API Key Anda dari Google AI Studio. Pastikan tidak ada spasi di awal atau akhir kunci.")
            else:
                st.warning("⚠️ Harap lengkapi Nama Anda dan API Key terlebih dahulu!")
    st.stop()

# ==============================================================================
# 5. INTEGRASI API GOOGLE & PANEL SIDEBAR (PILIHAN TOPIK & PERSONA)
# ==============================================================================
client = genai.Client(api_key=st.session_state.api_key)

with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: bold;'>🕌 Hidayah AI</h2>", unsafe_allow_html=True)
    st.write(f"Siswa aktif: **{st.session_state.username}**")
    st.caption(f"🤖 Engine: `{st.session_state.active_model}`")
    st.markdown("---")
    
    ustadz_pilihan = st.radio("🎙️ Pilih Guru Pendamping:", ["Ustadz Salman", "Ustadzah Halimah"])
    materi_pilihan = st.selectbox(
        "📖 Pilih Materi Pembelajaran:",
        [
            "التسوق (At-Tasawuq / Berbelanja)",
            "في السوق (Fissuqi / Di Pasar)",
            "الهواية (Al-Hiwayah / Hobi)"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 Keluar Sesi", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if st.session_state.current_persona != ustadz_pilihan or st.session_state.current_materi != materi_pilihan:
    st.session_state.current_persona = ustadz_pilihan
    st.session_state.current_materi = materi_pilihan
    st.session_state.chat_history = [] 

instruksi_sistem = f"""
Anda adalah {ustadz_pilihan}, seorang pendidik bahasa Arab yang sangat penyabar dan ramah di Madrasah Aliyah Kelas XI. 
Fokus materi Anda saat ini adalah mengajarkan Keterampilan Menulis (Maharah Kitabah) dengan topik khusus: {materi_pilihan}.
Mulailah percakapan menggunakan salam Islami. Berikan siswa instruksi latihan menulis bahasa Arab terstruktur secara bertahap. 
Koreksi harakat atau penulisan kata siswa secara detail dan berikan pujian Islami seperti ممتاز atau بارك الله فيك.
"""

# ==============================================================================
# 6. PANEL CHAT UTAMA & RIWAYAT PERCAKAPAN (CONVERSATION HISTORY)
# ==============================================================================
st.markdown(f"## 🏛️ Kelas Virtual: {materi_pilihan}")
st.write(f"Bersama: **{ustadz_pilihan}**")

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if len(st.session_state.chat_history) == 0:
    if ustadz_pilihan == "Ustadz Salman":
        salam_pembuka = f"Assalamu'alaikum wr. wb. Selamat datang di kelas bahasa Arab, Ananda **{st.session_state.username}**. Bersama Ustadz Salman di sini, mari kita asah kemampuan menulis (*Maharah Kitabah*) kita bertemakan **{materi_pilihan}**. Ketik 'Siap Ustadz' jika Ananda sudah siap menerima latihan menulis pertama hari ini."
    else:
        salam_pembuka = f"Assalamu'alaikum wr. wb. Halo anakku yang shalih/shalihah, **{st.session_state.username}**! Senang sekali bisa berjumpa dengan Ustadzah Halimah di ruang belajar ini. Kita akan belajar merangkai kalimat bahasa Arab dengan seru untuk materi **{materi_pilihan}**. Sapa Ustadzah sekarang untuk memulai latihannya ya!"
        
    st.session_state.chat_history.append({"role": "assistant", "content": salam_pembuka})
    st.rerun()

if pesan_user := st.chat_input("Ketik tanggapan atau latihan menulis Arab Anda di sini..."):
    with st.chat_message("user"):
        st.markdown(pesan_user)
    st.session_state.chat_history.append({"role": "user", "content": pesan_user})

    if pesan_user.lower() in ['exit', 'quit', 'keluar']:
        st.session_state.clear()
        st.rerun()

    payload_konten = []
    for msg in st.session_state.chat_history:
        peran_api = "user" if msg["role"] == "user" else "model"
        payload_konten.append(
            types.Content(role=peran_api, parts=[types.Part.from_text(text=msg["content"])])
        )

    try:
        with st.spinner(f"{ustadz_pilihan} sedang membaca tulisan Anda..."):
            respons_api = client.models.generate_content(
                model=st.session_state.active_model,
                contents=payload_konten,
                config=types.GenerateContentConfig(
                    system_instruction=instruksi_sistem,
                    temperature=0.6,
                )
            )
            
            teks_balasan = respons_api.text
            with st.chat_message("assistant"):
                st.markdown(teks_balasan)
            st.session_state.chat_history.append({"role": "assistant", "content": teks_balasan})
            
    except Exception as error_sistem:
        st.error(f"⚠️ Terjadi gangguan interaksi sistem: {str(error_sistem)}")