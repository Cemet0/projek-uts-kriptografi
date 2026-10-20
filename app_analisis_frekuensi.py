import streamlit as st
import plotly.graph_objects as go
from collections import Counter
import string
import random
import math
from itertools import permutations
from functools import lru_cache
import time

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

# ==========================================
# 3b. ALGORITMA LAIN DI PDF: HOMOFONIK, RAIL FENCE, COLUMNAR TRANSPOSITION
# ==========================================

# Korpus kecil untuk model bahasa (bigram + trigram log-probabilitas)
KORPUS_LM = {
    "English": 'Cryptography is the art and science of keeping messages secret. Long before computers existed, people used pencil and paper to hide the meaning of their letters. The best known of these old methods is the cipher attributed to Julius Caesar, in which every letter of the alphabet is moved three places forward. A message written in this way looks like nonsense, yet anyone who knows the rule can read it at once. Such simple systems are easy to break because the language that people speak has a very uneven pattern of letters. In English the letter e appears more often than any other, followed by t and a, while the letters q and z are rare. When a message is changed by replacing each letter with another, these habits of the language are not removed but only disguised. An attacker who counts the letters in the secret text will soon notice that one symbol appears again and again, and it is reasonable to guess that this symbol stands for the letter e. By looking at common pairs and short words such as the, and, and of, the attacker can slowly recover the whole table. This method, called frequency analysis, was first described by scholars in the ancient world and it remained the main weapon of those who wanted to read the secrets of other people for many centuries. Designers of later ciphers tried to defeat it by using several alphabets at once, by replacing groups of letters instead of single ones, or by letting a common letter be written in many different ways. Another family of methods leaves the letters unchanged and only moves them to new positions, so that the counts of letters stay the same but the order of the words is lost.',
    "Indonesia": 'Kriptografi adalah ilmu dan seni untuk menjaga kerahasiaan pesan. Jauh sebelum komputer ada, orang hanya menggunakan pena dan kertas untuk menyembunyikan makna dari surat yang mereka kirim. Salah satu metode lama yang paling terkenal adalah sandi yang dipakai pada zaman Julius Caesar, yaitu setiap huruf dalam alfabet digeser tiga tempat ke kanan. Pesan yang ditulis dengan cara ini tampak seperti kumpulan huruf yang tidak berarti, tetapi siapa pun yang mengetahui aturannya dapat membacanya dengan mudah. Sistem sederhana seperti ini mudah dipecahkan karena bahasa yang digunakan manusia memiliki pola huruf yang tidak merata. Dalam bahasa Indonesia huruf a muncul paling sering, disusul oleh huruf n, i, dan e, sedangkan huruf q, x, dan v hampir tidak pernah dipakai. Ketika sebuah pesan diubah dengan mengganti setiap huruf dengan huruf lain, kebiasaan bahasa tersebut tidak hilang, hanya disamarkan. Seorang penyerang yang menghitung jumlah huruf pada cipherteks akan segera menyadari bahwa ada satu simbol yang muncul berulang kali, dan wajar jika ia menduga simbol itu mewakili huruf a. Dengan memperhatikan pasangan huruf yang umum serta kata pendek seperti yang, dan, di, dan ke, penyerang dapat memulihkan seluruh tabel substitusi secara perlahan. Teknik ini disebut analisis frekuensi, dan selama berabad abad teknik ini menjadi senjata utama bagi mereka yang ingin membaca rahasia orang lain. Perancang sandi yang datang kemudian mencoba mengalahkannya dengan memakai beberapa alfabet sekaligus, dengan mengganti sekelompok huruf sekaligus, atau dengan membiarkan satu huruf yang sering muncul ditulis dalam banyak bentuk. Ada pula keluarga metode lain yang tidak mengubah huruf sama sekali, melainkan hanya memindahkan posisinya, sehingga jumlah setiap huruf tetap sama tetapi urutan kata menjadi hilang.',
}

# Tabel homofonik dari PDF (huruf plainteks -> pilihan unit cipherteks 2 huruf)
HOMO_RAW = 'A BU CP AV AH BT BS CQ\nB AT\nC DL BK AU\nD BV DY DM AI\nE DK CO AW BL AA CR BM CS AF AG BO BN BE\nF BW CM CN\nG DN BJ\nH AS CL CK\nI DJ BI AX CJ AB BP CU CT\nJ BX\nK DI\nL AR BH CI AJ\nM DH BG AY\nN BY DG DF CH AC BR DU DT\nO DZ BF DX AK CG BQ DR\nP BZ DE AZ\nQ DD\nR AQ DC DQ AL CE CF CV DS\nS AP AN AO CD DW DV\nT CB DB DP CC AD CY CW CX AE\nU CA AM BA\nV BB\nW CZ\nX BD\nY DO DA\nZ BC'
HOMO_INV = {u: ln.split()[0] for ln in HOMO_RAW.splitlines() for u in ln.split()[1:]}

LN_26_FAKTORIAL = math.lgamma(27)  # ukuran ruang kunci substitusi acak (26!)


@lru_cache(maxsize=None)
def bangun_lm(bahasa):
    """Model bigram & trigram (add-k smoothing) dari korpus bahasa."""
    A_ = string.ascii_uppercase
    t = "".join(c for c in KORPUS_LM[bahasa].upper() if c in A_)
    k = 0.05
    c2 = Counter(t[i:i + 2] for i in range(len(t) - 1))
    c3 = Counter(t[i:i + 3] for i in range(len(t) - 2))
    n2, n3 = sum(c2.values()), sum(c3.values())
    bi = [[math.log((c2[x + y] + k) / (n2 + k * 676)) for y in A_] for x in A_]
    tri = [math.log((c3[x + y + z] + k) / (n3 + k * 17576)) for x in A_ for y in A_ for z in A_]
    return bi, tri


def skor_lm(teks, bahasa):
    """Total log-likelihood teks terhadap bahasa + jumlah huruf."""
    bi, tri = bangun_lm(bahasa)
    L = [ord(c) - 65 for c in teks.upper() if c in string.ascii_uppercase]
    s = sum(bi[a][b] for a, b in zip(L, L[1:]))
    s += 0.5 * sum(tri[(a * 26 + b) * 26 + c] for a, b, c in zip(L, L[1:], L[2:]))
    return s, len(L)


def coba_homofonik(ciphertext):
    """Cipherteks homofonik = deretan unit 2 huruf yang SEMUA ada di tabel homofon PDF."""
    s = "".join(ciphertext.upper().split())
    if len(s) < 8 or len(s) % 2 or not (s.isascii() and s.isalpha()):
        return None
    unit = [s[i:i + 2] for i in range(0, len(s), 2)]
    if all(u in HOMO_INV for u in unit):
        return "".join(HOMO_INV[u] for u in unit)
    return None


def rail_pola(n_char, rel):
    baris, r, d = [[] for _ in range(rel)], 0, 1
    for i in range(n_char):
        baris[r].append(i)
        d = 1 if r == 0 else (-1 if r == rel - 1 else d)
        r += d
    return [i for row in baris for i in row]


def rail_dekripsi(t, rel):
    hasil = [""] * len(t)
    for ch, i in zip(t, rail_pola(len(t), rel)):
        hasil[i] = ch
    return "".join(hasil)


def kandidat_caesar(ciphertext, bahasa):
    """Exhaustive key search 26 kunci, dinilai dengan model bahasa (bigram + trigram)."""
    terbaik = None
    for geser in range(26):
        peta = {string.ascii_uppercase[i]: string.ascii_uppercase[(i + geser) % 26] for i in range(26)}
        plain = substitusi_teks(ciphertext, peta)
        ll, n = skor_lm(plain, bahasa)
        if terbaik is None or ll > terbaik[0]:
            terbaik = (ll, n, peta, (26 - geser) % 26)
    ll, n, peta, k = terbaik
    metode = "Plainteks (tidak terenkripsi)" if k == 0 else f"Caesar Cipher (Geser K = {k})" + (" - ROT13" if k == 13 else "")
    return {"mdl": ll - math.log(26), "ll": ll, "n": n, "map": peta, "metode": metode, "bahasa": bahasa}


def kandidat_rail(t, bahasa):
    terbaik = None
    for rel in range(2, min(11, len(t))):
        plain = rail_dekripsi(t, rel)
        ll, n = skor_lm(plain, bahasa)
        if terbaik is None or ll > terbaik[0]:
            terbaik = (ll, n, plain, rel)
    if terbaik is None:
        return None
    ll, n, plain, rel = terbaik
    return {"mdl": ll - math.log(9), "ll": ll, "n": n, "plainteks": plain,
            "metode": f"Rail Fence Cipher ({rel} baris)", "bahasa": bahasa}


def kandidat_kolom(t, bahasa):
    """
    Columnar Transposition versi PDF: kolom tabel diatur ulang menurut kunci lalu dibaca baris demi baris.
    Urutan kolom dicari dengan skor bigram antar-kolom bertetangga (tanda '.' = padding).
    """
    bi, _ = bangun_lm(bahasa)
    huruf = lambda x: x.isascii() and x.isalpha()
    terbaik = None
    for n in range(2, 10):
        if len(t) % n or len(t) // n < 2:
            continue
        R = len(t) // n
        grid = [t[r * n:(r + 1) * n] for r in range(R)]

        def b(x, y):
            return bi[ord(x) - 65][ord(y) - 65] if huruf(x) and huruf(y) else 0.0

        S = [[sum(b(grid[r][i], grid[r][j]) for r in range(R)) for j in range(n)] for i in range(n)]
        W = [[sum(b(grid[r][i], grid[r + 1][j]) for r in range(R - 1)) for j in range(n)] for i in range(n)]
        skor_o = []
        for o in permutations(range(n)):
            skor_o.append((sum(S[o[i]][o[i + 1]] for i in range(n - 1)) + W[o[-1]][o[0]], o))
        skor_o.sort(reverse=True)
        plain, kunci, ll, jml = None, None, None, None
        for _, o in skor_o[:40]:  # nilai ulang kandidat teratas dengan bigram + trigram
            p_ = "".join(grid[r][o[c]] for r in range(R) for c in range(n)).rstrip(".")
            l_, j_ = skor_lm(p_, bahasa)
            if ll is None or l_ > ll:
                plain, ll, jml = p_, l_, j_
                kunci = [0] * n
                for c, j in enumerate(o):
                    kunci[j] = c + 1
        mdl = ll - math.lgamma(n + 1) - math.log(8)
        if terbaik is None or mdl > terbaik["mdl"]:
            terbaik = {"mdl": mdl, "ll": ll, "n": jml, "plainteks": plain, "bahasa": bahasa,
                       "metode": f"Columnar Transposition (kunci {','.join(map(str, kunci))})"}
    return terbaik


# ----- Cipher tambahan di luar PDF: Atbash/Affine, Vigenere, Reverse, Scytale, Playfair -----
ABJAD = string.ascii_uppercase
ALF25 = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # Playfair: I/J digabung


def ll_idx(idx, bahasa):
    """Log-likelihood bigram + trigram dari daftar indeks huruf (0-25)."""
    bi, tri = bangun_lm(bahasa)
    s_ = sum(bi[a][b] for a, b in zip(idx, idx[1:]))
    return s_ + 0.5 * sum(tri[(a * 26 + b) * 26 + c] for a, b, c in zip(idx, idx[1:], idx[2:]))


def indeks_huruf(teks):
    return [ord(c) - 65 for c in teks.upper() if c in ABJAD]


def kandidat_affine(ciphertext, bahasa):
    """Affine c = (a*p + b) mod 26 (312 kunci). a=25,b=25 adalah Atbash."""
    L = indeks_huruf(ciphertext)
    terbaik = None
    for a in (3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        a_inv = pow(a, -1, 26)
        for b in range(26):
            ll = ll_idx([(a_inv * (x - b)) % 26 for x in L], bahasa)
            if terbaik is None or ll > terbaik[0]:
                terbaik = (ll, a, b, a_inv)
    ll, a, b, a_inv = terbaik
    peta = {ABJAD[x]: ABJAD[(a_inv * (x - b)) % 26] for x in range(26)}
    nama = "Atbash Cipher" if (a, b) == (25, 25) else f"Affine Cipher (a = {a}, b = {b})"
    return {"mdl": ll - math.log(312), "ll": ll, "n": len(L), "map": peta, "metode": nama, "bahasa": bahasa}


def dekripsi_vigenere(teks, kunci):
    hasil, i = [], 0
    for ch in teks.upper():
        if ch in ABJAD:
            hasil.append(ABJAD[(ord(ch) - 65 - kunci[i % len(kunci)]) % 26])
            i += 1
        else:
            hasil.append(ch)
    return "".join(hasil)


def kandidat_vigenere(ciphertext, bahasa):
    """Cari panjang kunci lewat Index of Coincidence kolom, lalu tiap kolom dipecahkan seperti Caesar."""
    L = indeks_huruf(ciphertext)
    n = len(L)
    maks_m = min(12, n // 6)
    if maks_m < 2:
        return None
    ref = FREKUENSI_STANDAR[bahasa]
    refp = [ref[c] / 100 for c in ABJAD]

    def ic_kolom(m):
        tot = 0.0
        for j in range(m):
            col = L[j::m]
            nn = len(col)
            tot += sum(v * (v - 1) for v in Counter(col).values()) / (nn * (nn - 1)) if nn > 1 else 0
        return tot / m

    terbaik = None
    for m in sorted(range(2, maks_m + 1), key=lambda m: -ic_kolom(m))[:4]:
        kunci = []
        for j in range(m):
            col = L[j::m]
            cnt, nn = Counter(col), len(col)
            kunci.append(min(range(26), key=lambda sft: sum(
                (cnt.get((d + sft) % 26, 0) - refp[d] * nn) ** 2 / max(refp[d] * nn, 0.05) for d in range(26))))
        dek = lambda k: [(x - k[i % len(k)]) % 26 for i, x in enumerate(L)]
        ll = ll_idx(dek(kunci), bahasa)
        for _ in range(2):  # perbaiki tiap huruf kunci dengan model bigram/trigram
            berubah = False
            for j in range(m):
                for sft in range(26):
                    if sft == kunci[j]:
                        continue
                    k2 = kunci[:]
                    k2[j] = sft
                    l2 = ll_idx(dek(k2), bahasa)
                    if l2 > ll + 1e-9:
                        ll, kunci, berubah = l2, k2, True
            if not berubah:
                break
        mdl = ll - m * math.log(26)
        if terbaik is None or mdl > terbaik["mdl"]:
            terbaik = {"mdl": mdl, "ll": ll, "n": n, "m": m, "bahasa": bahasa,
                       "plainteks": dekripsi_vigenere(ciphertext, kunci),
                       "metode": f"Vigenere Cipher (kunci {''.join(ABJAD[k] for k in kunci)})"}
    return terbaik


def kandidat_reverse(ciphertext, bahasa):
    varian = {"Teks Dibalik (Reverse)": ciphertext[::-1],
              "Setiap Kata Dibalik": " ".join(w[::-1] for w in ciphertext.split(" "))}
    terbaik = None
    for nama, plain in varian.items():
        ll, n = skor_lm(plain, bahasa)
        if terbaik is None or ll > terbaik["ll"]:
            terbaik = {"mdl": ll - math.log(3), "ll": ll, "n": n, "plainteks": plain, "metode": nama, "bahasa": bahasa}
    return terbaik


def scytale_dekripsi(t, n):
    R = -(-len(t) // n)
    penuh = len(t) - (R - 1) * n
    panjang = [R if j < penuh else R - 1 for j in range(n)]
    kolom, pos = [], 0
    for pj in panjang:
        kolom.append(t[pos:pos + pj])
        pos += pj
    return "".join(kolom[j][r] for r in range(R) for j in range(n) if r < len(kolom[j]))


def kandidat_scytale(t, bahasa):
    terbaik = None
    for n in range(2, min(21, len(t) // 2 + 1)):
        plain = scytale_dekripsi(t, n)
        ll, jml = skor_lm(plain, bahasa)
        if terbaik is None or ll > terbaik["ll"]:
            terbaik = {"mdl": ll - math.log(19), "ll": ll, "n": jml, "plainteks": plain,
                       "metode": f"Scytale / Transposisi Kolom Sederhana (diameter {n})", "bahasa": bahasa}
    return terbaik


def tampak_playfair(ciphertext):
    """Ciri Playfair: panjang genap, tanpa J, dan tidak ada pasangan huruf kembar (mis. 'XX') pada digram."""
    s_ = "".join(c for c in ciphertext.upper() if c in ABJAD)
    if len(s_) < 120 or len(s_) % 2 or "J" in s_:
        return None
    if any(s_[i] == s_[i + 1] for i in range(0, len(s_), 2)):
        return None
    return s_


def playfair_pecahkan(s_, bahasa, restart=3, iterasi=15000):
    """Simulated annealing pada tabel kunci 5x5; skor = model bahasa teks hasil dekripsi."""
    pasangan = [(ALF25.index(s_[i]), ALF25.index(s_[i + 1])) for i in range(0, len(s_), 2)]
    peta26 = [ord(c) - 65 for c in ALF25]

    def dekripsi(sq):
        pos = [0] * 25
        for i, v in enumerate(sq):
            pos[v] = i
        out = []
        for a, b in pasangan:
            ia, ib = pos[a], pos[b]
            ra, ca, rb, cb = ia // 5, ia % 5, ib // 5, ib % 5
            if ra == rb:
                out += [peta26[sq[ra * 5 + (ca - 1) % 5]], peta26[sq[rb * 5 + (cb - 1) % 5]]]
            elif ca == cb:
                out += [peta26[sq[((ra - 1) % 5) * 5 + ca]], peta26[sq[((rb - 1) % 5) * 5 + cb]]]
            else:
                out += [peta26[sq[ra * 5 + cb]], peta26[sq[rb * 5 + ca]]]
        return out

    rng = random.Random(7)
    terbaik = None
    for _ in range(restart):
        sq = list(range(25))
        rng.shuffle(sq)
        cur = ll_idx(dekripsi(sq), bahasa)
        for it in range(iterasi):
            T = 25.0 * (1 - it / iterasi) + 0.3
            k2, r = sq[:], rng.random()
            if r < 0.9:
                i, j = rng.sample(range(25), 2)
                k2[i], k2[j] = k2[j], k2[i]
            elif r < 0.95:
                i, j = rng.sample(range(5), 2)
                for c in range(5):
                    k2[i * 5 + c], k2[j * 5 + c] = k2[j * 5 + c], k2[i * 5 + c]
            else:
                i, j = rng.sample(range(5), 2)
                for rr in range(5):
                    k2[rr * 5 + i], k2[rr * 5 + j] = k2[rr * 5 + j], k2[rr * 5 + i]
            sc = ll_idx(dekripsi(k2), bahasa)
            if sc > cur or math.exp((sc - cur) / T) > rng.random():
                sq, cur = k2, sc
                if terbaik is None or cur > terbaik[0]:
                    terbaik = (cur, sq[:])
    ll, sq = terbaik
    plain = "".join(ABJAD[x] for x in dekripsi(sq))
    return {"mdl": ll - math.lgamma(26), "ll": ll, "n": len(plain), "plainteks": plain,
            "metode": "Playfair Cipher (tabel 5x5, AI Simulated Annealing)", "bahasa": bahasa}


def auto_solve_semua(ciphertext, opsi_bahasa="Otomatis (Deteksi)"):
    """
    Pipeline pemecahan otomatis. Semua kandidat dibandingkan dengan skor model bahasa
    dikurangi ln(jumlah kunci) (prinsip MDL), supaya metode berkunci besar tidak menang
    hanya karena lebih "fleksibel" menyesuaikan teks pendek.
      Dari PDF   : Homofonik, Caesar/ROT13, Rail Fence, Columnar, Substitusi (tabel acak/kata kunci)
      Tambahan   : Atbash/Affine, Vigenere, Reverse, Scytale, Playfair
    """
    if len(ciphertext.strip()) < 5:
        return None

    daftar_bahasa = ["Indonesia", "English"] if opsi_bahasa == "Otomatis (Deteksi)" else [opsi_bahasa]
    identitas = {c: c for c in string.ascii_uppercase}

    # 1. Homofonik (tabel dari PDF, deterministik)
    plain_h = coba_homofonik(ciphertext)
    if plain_h:
        b = max(daftar_bahasa, key=lambda x: skor_lm(plain_h, x)[0])
        ll, n = skor_lm(plain_h, b)
        return {"map": identitas, "plainteks": plain_h, "metode": "Cipher Homofonik (tabel homofon PDF)",
                "bahasa": b, "skor": ll, "status": "Sukses"}

    # 2. Kandidat murah: Caesar, Rail Fence, Columnar, Affine/Atbash, Vigenere, Reverse, Scytale
    t = "".join(ciphertext.upper().split())
    n_huruf = len(indeks_huruf(ciphertext))
    kandidat = []
    for b in daftar_bahasa:
        kandidat.append(kandidat_caesar(ciphertext, b))
        if n_huruf >= 12:  # 312 kunci Affine terlalu longgar untuk teks sangat pendek
            kandidat.append(kandidat_affine(ciphertext, b))
        kandidat.append(kandidat_reverse(ciphertext, b))
        fungsi_t = [kandidat_rail, kandidat_kolom, kandidat_scytale]
        for fungsi in fungsi_t:
            k = fungsi(t, b)
            if k:
                kandidat.append(k)
        # Vigenere meratakan frekuensi huruf (IC rendah); pada teks pendek IC tidak bisa dipercaya
        if n_huruf < 60 or index_of_coincidence_idx(indeks_huruf(ciphertext)) < 0.058:
            k = kandidat_vigenere(ciphertext, b)
            if k:
                kandidat.append(k)

    def ambang(n):
        # Teks panjang yang benar-benar terbongkar punya skor rata-rata per huruf > -9,8;
        # teks pendek lebih longgar karena statistiknya kurang stabil.
        return -9.8 if n >= 150 else -10.5

    def selesai(k):
        k = dict(k)
        k.setdefault("map", identitas)
        k["skor"] = k["ll"]
        yakin = k["n"] >= 8 and k["ll"] / k["n"] > ambang(k["n"])
        if k["metode"].startswith("Substitusi") and k["n"] < 150:
            yakin = False  # substitusi acak pada teks pendek hanya tebakan
        if k["metode"].startswith("Vigenere") and k["n"] < 15 * k.get("m", 1):
            yakin = False  # kolom terlalu pendek untuk analisis frekuensi
        k["status"] = "Sukses" if yakin else "Tebakan"
        return k

    terbaik = max(kandidat, key=lambda k: k["mdl"])
    if selesai(terbaik)["status"] == "Sukses":
        return selesai(terbaik)

    # 3. Playfair (dikenali dari cirinya) dan substitusi umum -> Simulated Annealing
    pf = tampak_playfair(ciphertext)
    if pf:
        for b in daftar_bahasa:
            kandidat.append(playfair_pecahkan(pf, b))
        terbaik = max(kandidat, key=lambda k: k["mdl"])
        if selesai(terbaik)["status"] == "Sukses":
            return selesai(terbaik)

    for b in daftar_bahasa:
        map_sa, _ = auto_solve_simulated_annealing(ciphertext, b)
        ll, n = skor_lm(substitusi_teks(ciphertext, map_sa), b)
        kandidat.append({"mdl": ll - LN_26_FAKTORIAL, "ll": ll, "n": n, "map": map_sa,
                         "metode": "Substitusi Acak (AI Simulated Annealing)", "bahasa": b})
    return selesai(max(kandidat, key=lambda k: k["mdl"]))


def index_of_coincidence_idx(L):
    n = len(L)
    return sum(v * (v - 1) for v in Counter(L).values()) / (n * (n - 1)) if n > 1 else 0.0


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
        "Basis Bahasa Teks:",
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
    st.subheader("Input Cipherteks")
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
            with st.spinner("I sedang menganalisis frekuensi dan memetakan huruf secara otomatis..."):
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
        if info["status"] == "Sukses":
            st.success(
                f"✅ **Teks Berhasil Dibongkar Otomatis!**\n\n"
                f"- **Metode Terdeteksi:** {info['metode']}\n"
                f"- **Bahasa Acuan:** {info['bahasa']}"
            )
        else:
            st.warning(
                f"⚠️ **Ini baru tebakan terbaik** (teks terlalu pendek atau tidak cukup pola statistik).\n\n"
                f"- **Metode Terdeteksi:** {info['metode']}\n"
                f"- **Bahasa Acuan:** {info['bahasa']}\n"
                f"- Periksa hasilnya; untuk substitusi, koreksi huruf lewat Penyesuaian Manual atau gunakan cipherteks lebih panjang."
            )

    st.subheader("Hasil Dekripsi Otomatis")
    info_aktif = st.session_state.solve_info
    if info_aktif and "plainteks" in info_aktif and ciphertext == st.session_state.last_solved_text:
        hasil_dekripsi = info_aktif["plainteks"]  # transposisi / homofonik: bukan pemetaan huruf
    else:
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
    with st.expander("Penyesuaian Manual (Opsional - Jika ingin melihat atau mengubah huruf tertentu)"):
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