import streamlit as st
import plotly.graph_objects as go
from collections import Counter
import string

st.set_page_config(
    page_title="Analisis Frekuensi - Kriptografi",
    layout="wide"
)

frekuensi_inggris = {
    'A': 8.17, 'B': 1.49, 'C': 2.78, 'D': 4.25, 'E': 12.70,
    'F': 2.23, 'G': 2.02, 'H': 6.09, 'I': 6.97, 'J': 0.15,
    'K': 0.77, 'L': 4.03, 'M': 2.41, 'N': 6.75, 'O': 7.51,
    'P': 1.93, 'Q': 0.10, 'R': 5.99, 'S': 6.33, 'T': 9.06,
    'U': 2.76, 'V': 0.98, 'W': 2.36, 'X': 0.15, 'Y': 1.97,
    'Z': 0.07
}

if "mapping" not in st.session_state:
    st.session_state.mapping = {ch: ch for ch in string.ascii_uppercase}

for ch in string.ascii_uppercase:
    if f"map_{ch}" not in st.session_state:
        st.session_state[f"map_{ch}"] = st.session_state.mapping[ch]

def update_mapping(new_map):
    st.session_state.mapping = new_map.copy()
    for ch, val in new_map.items():
        st.session_state[f"map_{ch}"] = val

def ubah_dropdown(ch):
    st.session_state.mapping[ch] = st.session_state[f"map_{ch}"]

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

st.title("Program Kriptanalisis: Analisis Frekuensi")
st.write("Membongkar cipherteks substitusi dengan memetakan probabilitas kemunculan karakter secara otomatis.")
st.divider()

kolom_kiri, kolom_kanan = st.columns([1.1, 1.9], gap="large")

with kolom_kiri:
    st.subheader("Input Cipherteks")
    ciphertext = st.text_area(
        "Masukkan Cipherteks:",
        value="",
        placeholder="Tempel cipherteks di sini...",
        height=230
    )

    freq_cipher, total_huruf = hitung_frekuensi(ciphertext)
    st.caption(f"Total huruf dianalisis: {total_huruf}")

    st.subheader("Hasil Dekripsi")
    tempat_dekripsi = st.empty()

with kolom_kanan:
    st.subheader("Grafik Frekuensi Huruf")

    k1, k2 = st.columns([1, 1])
    with k1:
        urutkan = st.radio("Urutan Grafik:", ["A - Z", "Persentase Tertinggi"], horizontal=True)
    with k2:
        if st.button("Jalankan Algoritma Pemetaan Otomatis"):
            urut_cipher = sorted(freq_cipher.keys(), key=lambda x: freq_cipher[x], reverse=True)
            urut_inggris = sorted(frekuensi_inggris.keys(), key=lambda x: frekuensi_inggris[x], reverse=True)
            update_mapping(dict(zip(urut_cipher, urut_inggris)))
            st.rerun()

    if urutkan == "A - Z":
        sumbu_x = list(string.ascii_uppercase)
    else:
        sumbu_x = sorted(freq_cipher.keys(), key=lambda x: freq_cipher[x], reverse=True)

    y_atas = [freq_cipher[ch] for ch in sumbu_x]
    huruf_terpeta = [st.session_state.mapping[ch] for ch in sumbu_x]
    y_bawah = [-frekuensi_inggris[m] for m in huruf_terpeta]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sumbu_x,
        y=y_atas,
        name="Cipherteks",
        marker_color="#ff9900"
    ))
    fig.add_trace(go.Bar(
        x=sumbu_x,
        y=y_bawah,
        name="Standar Bahasa Inggris",
        marker_color="#1f77b4",
        customdata=huruf_terpeta,
        hovertemplate="Peta ke: %{customdata}<br>Frekuensi: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        barmode="relative",
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(
            title="Frekuensi (%)",
            tickvals=[-12, -8, -4, 0, 4, 8, 12],
            ticktext=["12%", "8%", "4%", "0%", "4%", "8%", "12%"]
        ),
        legend=dict(orientation="h", y=1.1)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Penyesuaian Manual (Pemetaan Huruf)")
    b1, _ = st.columns([1, 4])
    with b1:
        if st.button("Reset Algoritma"):
            update_mapping({ch: ch for ch in string.ascii_uppercase})
            st.rerun()

    alfabet = list(string.ascii_uppercase)

    baris1 = st.columns(13)
    for i in range(13):
        ch = alfabet[i]
        with baris1[i]:
            st.selectbox(
                label=ch,
                options=alfabet,
                key=f"map_{ch}",
                on_change=ubah_dropdown,
                args=(ch,)
            )

    baris2 = st.columns(13)
    for i in range(13, 26):
        ch = alfabet[i]
        with baris2[i - 13]:
            st.selectbox(
                label=ch,
                options=alfabet,
                key=f"map_{ch}",
                on_change=ubah_dropdown,
                args=(ch,)
            )

hasil_akhir = substitusi_teks(ciphertext, st.session_state.mapping)
tempat_dekripsi.text_area("Plainteks:", value=hasil_akhir, height=230)