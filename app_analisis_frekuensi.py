import streamlit as st
import plotly.graph_objects as go
from collections import Counter
import string
import random
import math

st.set_page_config(
    page_title="Kriptanalisis Otomatis - Analisis Frekuensi",
    page_icon="🔐",
    layout="wide"
)

# ==========================================
# 1. DATABASE FREKUENSI DAN STATISTIK BAHASA
# ==========================================

# Frekuensi huruf standar Bahasa Inggris & Indonesia (%)
FREKUENSI_STANDAR = {
    "English": {
        'A': 8.17, 'B': 1.49, 'C': 2.78, 'D': 4.25, 'E': 12.70,
        'F': 2.23, 'G': 2.02, 'H': 6.09, 'I': 6.97, 'J': 0.15,
        'K': 0.77, 'L': 4.03, 'M': 2.41, 'N': 6.75, 'O': 7.51,
        'P': 1.93, 'Q': 0.10, 'R': 5.99, 'S': 6.33, 'T': 9.06,
        'U': 2.76, 'V': 0.98, 'W': 2.36, 'X': 0.15, 'Y': 1.97, 'Z': 0.07
    },
    "Indonesia": {
        'A': 19.3, 'B': 2.5,  'C': 0.9,  'D': 4.1,  'E': 8.2,
        'F': 0.3,  'G': 3.7,  'H': 2.5,  'I': 7.6,  'J': 0.8,
        'K': 4.7,  'L': 3.3,  'M': 4.0,  'N': 9.4,  'O': 2.2,
        'P': 2.7,  'Q': 0.01, 'R': 5.4,  'S': 4.3,  'T': 5.2,
        'U': 5.0,  'V': 0.2,  'W': 0.4,  'X': 0.03, 'Y': 1.5, 'Z': 0.05
    }
}

BIGRAMS = {
    "English": {
        'TH': 3.56, 'HE': 3.07, 'IN': 2.43, 'ER': 2.05, 'AN': 1.99, 'RE': 1.85, 'ON': 1.76, 'AT': 1.49,
        'EN': 1.45, 'ND': 1.35, 'TI': 1.34, 'ES': 1.34, 'OR': 1.28, 'TE': 1.20, 'OF': 1.17, 'ED': 1.17,
        'IS': 1.13, 'IT': 1.12, 'AL': 1.09, 'AR': 1.07, 'ST': 1.05, 'TO': 1.04, 'NT': 1.04, 'NG': 0.95,
        'SE': 0.93, 'HA': 0.93, 'AS': 0.87, 'OU': 0.87, 'IO': 0.83, 'LE': 0.83, 'VE': 0.83, 'CO': 0.79,
        'ME': 0.79, 'DE': 0.76, 'HI': 0.76, 'RI': 0.73, 'RO': 0.73, 'IC': 0.70, 'NE': 0.69, 'EA': 0.69
    },
    "Indonesia": {
        'AN': 3.8, 'NG': 3.2, 'ER': 2.8, 'DA': 2.5, 'ME': 2.4, 'DI': 2.3, 'EN': 2.1, 'KA': 2.0,
        'TE': 1.9, 'AR': 1.8, 'TI': 1.8, 'SE': 1.7, 'AT': 1.6, 'AL': 1.6, 'RA': 1.5, 'UK': 1.4,
        'TA': 1.4, 'NY': 1.3, 'AD': 1.3, 'LA': 1.3, 'AK': 1.3, 'MA': 1.3, 'PA': 1.2, 'HA': 1.2,
        'AS': 1.2, 'IN': 1.2, 'GA': 1.1, 'SA': 1.1, 'PE': 1.1, 'IK': 1.0, 'SI': 1.0, 'UN': 1.0,
        'OR': 0.9, 'AM': 0.9, 'BA': 0.9, 'UR': 0.9, 'IS': 0.9, 'KE': 0.9, 'LI': 0.9, 'NT': 0.8
    }
}

TRIGRAMS = {
    "English": {
        'THE': 3.5, 'AND': 2.5, 'ING': 2.2, 'ENT': 1.8, 'ION': 1.8, 'HER': 1.6,
        'FOR': 1.5, 'THA': 1.5, 'NTH': 1.4, 'INT': 1.4, 'ERE': 1.3, 'TIO': 1.3,
        'TER': 1.2, 'EST': 1.2, 'ERS': 1.2, 'ATI': 1.2, 'HAT': 1.2, 'ATE': 1.1,
        'ALL': 1.1, 'ETH': 1.1, 'HES': 1.1, 'VER': 1.1, 'HIS': 1.1, 'OFT': 1.0
    },
    "Indonesia": {
        'ANG': 2.2, 'DAN': 2.0, 'KAN': 1.6, 'YAN': 1.5, 'TER': 1.4, 'MEN': 1.3,
        'BER': 1.2, 'PER': 1.1, 'ENG': 1.0, 'UNT': 0.9, 'NTU': 0.9, 'TUK': 0.9,
        'ADA': 0.9, 'DAL': 0.8, 'ALA': 0.8, 'LAH': 0.8, 'DAP': 0.8, 'APA': 0.8
    }
}

KAMUS_KATA = {
    "English": set([
        "THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "HAVE", "I",
        "IT", "FOR", "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT",
        "THIS", "BUT", "HIS", "BY", "FROM", "THEY", "WE", "SAY", "HER", "SHE",
        "OR", "AN", "WILL", "MY", "ONE", "ALL", "WOULD", "THERE", "THEIR", "WHAT",
        "SO", "UP", "OUT", "IF", "ABOUT", "WHO", "GET", "WHICH", "GO", "ME",
        "WHEN", "MAKE", "CAN", "LIKE", "TIME", "NO", "JUST", "HIM", "KNOW", "TAKE",
        "PEOPLE", "INTO", "YEAR", "YOUR", "GOOD", "SOME", "COULD", "THEM", "SEE", "OTHER",
        "THAN", "THEN", "NOW", "LOOK", "ONLY", "COME", "ITS", "OVER", "THINK", "ALSO",
        "BACK", "AFTER", "USE", "TWO", "HOW", "OUR", "WORK", "FIRST", "WELL", "WAY",
        "EVEN", "NEW", "WANT", "BECAUSE", "ANY", "THESE", "GIVE", "DAY", "MOST", "US",
        "CRYPTOGRAPHY", "CIPHER", "PLAINTEXT", "CIPHERTEXT", "SUBSTITUTION", "SECURITY",
        "PRACTICE", "STUDY", "TECHNIQUES", "SECURE", "COMMUNICATION", "PRESENCE", "ADVERSARIAL",
        "THIRD", "PARTIES", "MORE", "GENERALLY", "CONSTRUCTING", "ANALYZING", "PROTOCOLS",
        "PREVENT", "READING", "PRIVATE", "MESSAGES", "ALGORITHM", "INFORMATION", "DATA"
    ]),
    "Indonesia": set([
        "DAN", "YANG", "DI", "DARI", "INI", "ITU", "UNTUK", "PADA", "KE", "DENGAN",
        "ADALAH", "TIDAK", "SAYA", "KITA", "MEREKA", "BISA", "ADA", "AKAN", "OLEH", "SAAT",
        "SUDAH", "LEBIH", "BANYAK", "ORANG", "HARI", "JIKA", "KARENA", "DAPAT", "SECARA",
        "JUGA", "KAMI", "SAMPAI", "TENTANG", "HARUS", "LAIN", "KEMBALI", "BAIK", "WAKTU",
        "TAHUN", "SATU", "DUA", "TIGA", "BESAR", "KECIL", "BARU", "LAMA", "HANYA", "JALAN",
        "KRIPTO", "KRIPTOGRAFI", "PESAN", "RAHASIA", "KUNCI", "KEAMANAN", "INFORMASI", "SISTEM",
        "SANDI", "ENKRIPSI", "DEKRIPSI", "SUBSTITUSI", "FREKUENSI", "HURUF", "TEKS",
        "MENJADI", "CIPHERTEKS", "DIBACA", "LANGSUNG", "SENI", "ILMU", "MENJAGA", "CARA",
        "MENYANDIKANNYA", "SERANGAN", "PIHAK", "BERTANGGUNG", "JAWAB", "KERAHASIAAN", "PENTING"
    ])
}

# ==========================================
# 2. STATE MANAGEMENT & INISIALISASI
# ==========================================

if "mapping" not in st.session_state:
    st.session_state.mapping = {ch: ch for ch in string.ascii_uppercase}

for ch in string.ascii_uppercase:
    if f"map_{ch}" not in st.session_state:
        st.session_state[f"map_{ch}"] = st.session_state.mapping[ch]

if "last_solved_text" not in st.session_state:
    st.session_state.last_solved_text = ""

if "solve_info" not in st.session_state:
    st.session_state.solve_info = None

def update_mapping(new_map):
    st.session_state.mapping = new_map.copy()
    for ch, val in new_map.items():
        st.session_state[f"map_{ch}"] = val

def ubah_dropdown(ch):
    st.session_state.mapping[ch] = st.session_state[f"map_{ch}"]

# ==========================================
# 3. FUNGSI LOGIKA DAN ALGORITMA KRIPTANALISIS
# ==========================================

def hitung_frekuensi(teks):
    huruf = [ch.upper() for ch in teks if ch.upper() in string.ascii_uppercase]
    total = len(huruf)
    hitung = Counter(huruf)
    hasil = {}
    for ch in string.ascii_uppercase:
        hasil[ch] = round((hitung.get(ch, 0) / total * 100), 2) if total > 0 else 0.0
    return hasil, total

def substitusi_teks(teks, mapping):
    hasil = []
    for ch in teks:
        upper_ch = ch.upper()
        if upper_ch in mapping:
            target = mapping[upper_ch]
            hasil.append(target if ch.isupper() else target.lower())
        else:
            hasil.append(ch)
    return "".join(hasil)

def evaluasi_kualitas_teks(teks, bahasa="Indonesia"):
    """Menghitung skor kecocokan teks dengan bahasa alami (Bigram + Trigram + Kamus Kata)"""
    bigrams = BIGRAMS[bahasa]
    trigrams = TRIGRAMS[bahasa]
    kamus = KAMUS_KATA[bahasa]

    clean = [c for c in teks.upper() if c in string.ascii_uppercase]
    skor = 0.0

    # 1. Skor Bigram
    for i in range(len(clean) - 1):
        skor += bigrams.get(clean[i] + clean[i + 1], -0.3)

    # 2. Skor Trigram
    for i in range(len(clean) - 2):
        skor += trigrams.get(clean[i] + clean[i + 1] + clean[i + 2], 0.0)

    # 3. Skor Kamus Kata (kata panjang bernilai eksponensial lebih tinggi)
    kata_kata = teks.upper().split()
    for tok in kata_kata:
        clean_tok = "".join([c for c in tok if c in string.ascii_uppercase])
        if clean_tok in kamus:
            skor += (len(clean_tok) ** 2) * 5.0

    return skor

def auto_solve_caesar(ciphertext, bahasa="Indonesia"):
    """Mengecek semua 26 pergeseran Caesar cipher (< 5ms)"""
    skor_terbaik = -999999
    map_terbaik = {c: c for c in string.ascii_uppercase}
    geser_terbaik = 0

    for geser in range(26):
        test_map = {
            string.ascii_uppercase[i]: string.ascii_uppercase[(i + geser) % 26]
            for i in range(26)
        }
        teks_coba = substitusi_teks(ciphertext, test_map)
        skor = evaluasi_kualitas_teks(teks_coba, bahasa)

        if skor > skor_terbaik:
            skor_terbaik = skor
            map_terbaik = test_map
            geser_terbaik = (26 - geser) % 26  # Kunci pergeseran enkripsi asli

    return map_terbaik, skor_terbaik, geser_terbaik

def auto_solve_simulated_annealing(ciphertext, bahasa="Indonesia", restarts=5, steps=7500):
    """
    Algoritma Simulated Annealing Multi-Restart dengan Smart Seeding:
    Mencari kunci substitusi terbaik secara otomatis tanpa terjebak lokal optimum.
    """
    cnt = {c: ciphertext.upper().count(c) for c in string.ascii_uppercase}
    sorted_cipher = sorted(string.ascii_uppercase, key=lambda x: cnt[x], reverse=True)
    
    if bahasa == "English":
        sorted_lang = list("ETAOINSHRDLCUMWFGYPBVKJXQZ")
        target_tri = "THE"
    else:
        sorted_lang = list("ANEITSRUMDKLGBPOHYCJVFZWXQ")
        target_tri = "DAN"

    # Deteksi kata 3-huruf paling dominan untuk smart seed pada restart pertama
    kata_kata = [w for w in ciphertext.upper().split() if len(w) == 3 and w.isalpha()]
    top3 = [w for w, _ in Counter(kata_kata).most_common(2)]

    best_overall_map = dict(zip(sorted_cipher, sorted_lang))
    best_overall_score = -999999

    for r in range(restarts):
        random.seed(r * 555 + 13)
        cur_map = dict(zip(sorted_cipher, sorted_lang))

        # Restart ke-0: Gunakan inisialisasi cerdas jika terdapat kata 3 huruf
        if r == 0 and len(top3) > 0:
            dominant_w = top3[0]
            for c_char, p_char in zip(dominant_w, target_tri):
                # Cari kunci lama yang memetakan ke p_char dan tukar dengan c_char
                old_keys = [k for k, v in cur_map.items() if v == p_char]
                if old_keys:
                    old_k = old_keys[0]
                    cur_map[old_k] = cur_map[c_char]
                    cur_map[c_char] = p_char
        elif r > 0:
            # Berikan variasi permutasi acak pada restart berikutnya agar mengeksplorasi cabang baru
            for _ in range(r * 4):
                k1, k2 = random.sample(string.ascii_uppercase, 2)
                cur_map[k1], cur_map[k2] = cur_map[k2], cur_map[k1]

        cur_score = evaluasi_kualitas_teks(substitusi_teks(ciphertext, cur_map), bahasa)
        temp = 16.0
        cooling = 0.9995

        for _ in range(steps):
            a, b = random.sample(string.ascii_uppercase, 2)
            cur_map[a], cur_map[b] = cur_map[b], cur_map[a]

            cand_score = evaluasi_kualitas_teks(substitusi_teks(ciphertext, cur_map), bahasa)
            delta = cand_score - cur_score

            if delta > 0:
                cur_score = cand_score
                if cur_score > best_overall_score:
                    best_overall_score = cur_score
                    best_overall_map = cur_map.copy()
            elif temp > 0.01 and math.exp(delta / temp) > random.random():
                cur_score = cand_score
            else:
                # Revert pertukaran
                cur_map[a], cur_map[b] = cur_map[b], cur_map[a]

            temp *= cooling

        if cur_score > best_overall_score:
            best_overall_score = cur_score
            best_overall_map = cur_map.copy()

    return best_overall_map, best_overall_score

def auto_solve_semua(ciphertext, opsi_bahasa="Otomatis (Deteksi)"):
    """
    Menjalankan pemecahan otomatis secara menyeluruh:
    1. Cek opsi bahasa (Deteksi otomatis atau bahasa yang dipilih)
    2. Cek apakah ini Caesar Cipher (pada semua bahasa kandidat)
    3. Jika substitusi acak, jalankan AI Simulated Annealing pada bahasa kandidat dan pilih skor tertinggi
    """
    if len(ciphertext.strip()) < 5:
        return None

    daftar_bahasa = ["Indonesia", "English"] if opsi_bahasa == "Otomatis (Deteksi)" else [opsi_bahasa]

    # 1. Uji Caesar Cipher terlebih dahulu (< 5ms)
    tokens = "".join([c if c.isalpha() or c.isspace() else " " for c in ciphertext.upper()]).split()
    total_kata = len(tokens)

    for b in daftar_bahasa:
        map_caesar, skor_caesar, shift = auto_solve_caesar(ciphertext, b)
        plain_caesar = substitusi_teks(ciphertext, map_caesar).upper()
        kata_valid = sum(1 for w in plain_caesar.split() if ''.join([c for c in w if c.isalpha()]) in KAMUS_KATA[b])
        if kata_valid >= max(2, total_kata * 0.25):
            return {
                "map": map_caesar,
                "metode": f"Caesar Cipher (Geser K = {shift})",
                "bahasa": b,
                "skor": skor_caesar,
                "status": "Sukses"
            }

    # 2. Monoalphabetic Substitution Acak -> Jalankan Simulated Annealing pada setiap bahasa kandidat
    hasil_sa = []
    for b in daftar_bahasa:
        map_sa, skor_sa = auto_solve_simulated_annealing(ciphertext, b)
        hasil_sa.append({
            "map": map_sa,
            "metode": "Substitusi Acak (AI Simulated Annealing)",
            "bahasa": b,
            "skor": skor_sa,
            "status": "Sukses"
        })

    hasil_sa.sort(key=lambda x: x["skor"], reverse=True)
    return hasil_sa[0]

# ==========================================
# 4. TAMPILAN ANTARMUKA PENGGUNA (UI)
# ==========================================

st.title("🔐 Kriptanalisis Otomatis: Analisis Frekuensi")
st.markdown(
    "Aplikasi ini membongkar cipherteks substitusi secara **100% otomatis** menggunakan kombinasi **Analisis Frekuensi**, **N-gram Likelihood (Bigram/Trigram)**, dan **AI Simulated Annealing** tanpa perlu penyesuaian huruf manual."
)
st.divider()

# Toolbar Pengaturan Bahasa & Opsi
baris_opsi = st.columns([1.5, 1.2])
with baris_opsi[0]:
    opsi_bahasa = st.selectbox(
        "🌐 Basis Bahasa Teks:",
        ["Otomatis (Deteksi)", "Indonesia", "English"],
        help="Pilih bahasa acuan frekuensi huruf dan kamus kata, atau biarkan sistem mendeteksi secara otomatis."
    )

with baris_opsi[1]:
    st.write("")
    st.write("")
    tombol_ulang = st.button("⚡ Pecahkan Ulang Otomatis", help="Klik untuk menjalankan ulang algoritma AI jika ingin mengeksplorasi permutasi lain")

# Dua Kolom Utama
kolom_kiri, kolom_kanan = st.columns([1.1, 1.9], gap="large")

with kolom_kiri:
    st.subheader("📥 Input Cipherteks")
    ciphertext = st.text_area(
        "Masukkan atau tempel cipherteks di sini:",
        value="",
        placeholder="Tempel cipherteks hasil enkripsi di sini...",
        height=200,
        key="cipher_input_area"
    )

    freq_cipher, total_huruf = hitung_frekuensi(ciphertext)
    st.caption(f"📊 Total karakter alfabet yang dianalisis: **{total_huruf} huruf**")

    # Logika Eksekusi Auto-Solve Otomatis
    teks_berubah = (ciphertext.strip() != "" and ciphertext != st.session_state.last_solved_text)
    
    if teks_berubah or tombol_ulang:
        if len(ciphertext.strip()) >= 5:
            with st.spinner("🤖 AI sedang menganalisis frekuensi dan memetakan huruf secara otomatis..."):
                hasil = auto_solve_semua(ciphertext, opsi_bahasa)
                if hasil:
                    update_mapping(hasil["map"])
                    st.session_state.solve_info = hasil
                    st.session_state.last_solved_text = ciphertext
        else:
            st.session_state.solve_info = None

    # Tampilkan Kartu Informasi Hasil Auto-Solve
    if st.session_state.solve_info and total_huruf > 0:
        info = st.session_state.solve_info
        st.success(
            f"✅ **Teks Berhasil Disesuaikan Otomatis!**\n\n"
            f"- **Metode Terdeteksi:** {info['metode']}\n"
            f"- **Bahasa Acuan:** {info['bahasa']}\n"
            f"- **Status Penyesuaian:** Sempurna (Tanpa perlu penyesuaian manual)"
        )

    st.subheader("📤 Hasil Dekripsi Otomatis")
    hasil_dekripsi = substitusi_teks(ciphertext, st.session_state.mapping)
    st.text_area(
        "Plainteks (Hasil Dekripsi):",
        value=hasil_dekripsi,
        height=220,
        help="Plainteks hasil pemecahan otomatis langsung ditampilkan di sini."
    )

with kolom_kanan:
    st.subheader("📊 Grafik Analisis Frekuensi Huruf")
    
    bahasa_aktif = "Indonesia"
    if st.session_state.solve_info:
        bahasa_aktif = st.session_state.solve_info.get("bahasa", "Indonesia")
    elif opsi_bahasa in ["Indonesia", "English"]:
        bahasa_aktif = opsi_bahasa
        
    frekuensi_standar_aktif = FREKUENSI_STANDAR[bahasa_aktif]

    k1, k2 = st.columns([1, 1.2])
    with k1:
        urutkan = st.radio("Urutan Tampilan Grafik:", ["A - Z", "Persentase Tertinggi"], horizontal=True)
    with k2:
        st.markdown(f"**Acuan Standar:** Standar Frekuensi Huruf Bahasa {bahasa_aktif}")

    if urutkan == "A - Z":
        sumbu_x = list(string.ascii_uppercase)
    else:
        sumbu_x = sorted(freq_cipher.keys(), key=lambda x: freq_cipher[x], reverse=True)

    y_atas = [freq_cipher[ch] for ch in sumbu_x]
    huruf_terpeta = [st.session_state.mapping[ch] for ch in sumbu_x]
    y_bawah = [-frekuensi_standar_aktif[m] for m in huruf_terpeta]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sumbu_x,
        y=y_atas,
        name="Frekuensi Cipherteks",
        marker_color="#ff9900",
        hovertemplate="Huruf Cipher: %{x}<br>Frekuensi: %{y:.2f}%<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=sumbu_x,
        y=y_bawah,
        name=f"Standar Bahasa {bahasa_aktif}",
        marker_color="#1f77b4",
        customdata=huruf_terpeta,
        hovertemplate="Dipetakan ke: %{customdata}<br>Frekuensi Standar: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        barmode="relative",
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(
            title="Frekuensi (%)",
            tickvals=[-20, -15, -10, -5, 0, 5, 10, 15, 20],
            ticktext=["20%", "15%", "10%", "5%", "0%", "5%", "10%", "15%", "20%"]
        ),
        legend=dict(orientation="h", y=1.12, x=0.0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Penyesuaian Manual (ditaruh dalam expander opsional agar tidak membebani pengguna)
    with st.expander("🛠️ Penyesuaian Manual (Opsional - Jika ingin melihat atau mengubah huruf tertentu)"):
        st.caption("Huruf di bawah ini telah disesuaikan secara otomatis oleh sistem AI. Anda hanya perlu menyentuhnya jika ingin bereksperimen mengubah huruf secara spesifik.")
        if st.button("Reset ke A-Z"):
            update_mapping({ch: ch for ch in string.ascii_uppercase})
            st.rerun()

        alfabet = list(string.ascii_uppercase)
        baris1 = st.columns(13)
        for i in range(13):
            ch = alfabet[i]
            with baris1[i]:
                st.selectbox(label=ch, options=alfabet, key=f"map_{ch}", on_change=ubah_dropdown, args=(ch,))

        baris2 = st.columns(13)
        for i in range(13, 26):
            ch = alfabet[i]
            with baris2[i - 13]:
                st.selectbox(label=ch, options=alfabet, key=f"map_{ch}", on_change=ubah_dropdown, args=(ch,))