import streamlit as st
import time
import json
import pandas as pd
from hash_utils import HashTable
from binary_utils import binary_search, binary_search_steps

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Pencarian Tercepat",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "custom_items" not in st.session_state:
    st.session_state.custom_items = []

# ── Load Data ─────────────────────────────────────────────────
with open("sample_data.json") as f:
    raw_data = json.load(f)
base_items = raw_data["items"]

def get_all_items():
    return base_items + st.session_state.custom_items

def rebuild():
    all_items = get_all_items()
    si = sorted(all_items, key=lambda x: x["name"].lower())
    sn = [i["name"] for i in si]
    ht = HashTable(size=101)
    for item in all_items:
        ht.insert(item["name"], item)
    return all_items, si, sn, ht

items, sorted_items, sorted_names, ht = rebuild()

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def partial_search(query):
    q = query.lower()
    return [i for i in get_all_items() if q in i["name"].lower()]

def do_hash(q):
    start = time.perf_counter()
    result = ht.search(q)
    elapsed = (time.perf_counter() - start) * 1000
    steps, chain = ht.search_steps(q)
    return result, elapsed, steps, chain

def do_binary(q):
    start = time.perf_counter()
    idx = binary_search(sorted_names, q)
    elapsed = (time.perf_counter() - start) * 1000
    result = sorted_items[idx] if idx != -1 else None
    bsteps = binary_search_steps(sorted_names, q)
    return result, elapsed, bsteps, idx

def add_history(q, method, found, h_ms=None, b_ms=None):
    st.session_state.history.insert(0, {
        "keyword": q,
        "method": method,
        "found": "✅ Ya" if found else "❌ Tidak",
        "hash_ms": f"{h_ms:.5f}" if h_ms is not None else "—",
        "binary_ms": f"{b_ms:.5f}" if b_ms is not None else "—",
    })
    if len(st.session_state.history) > 15:
        st.session_state.history.pop()

def render_table(data_list):
    if not data_list:
        return
    df = pd.DataFrame(data_list)[["id","name","category","nilai"]]
    df.columns = ["ID","Nama Produk","Kategori","Harga (Rp)"]
    df["Harga (Rp)"] = df["Harga (Rp)"].apply(lambda x: f"Rp {x:,}")
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_hash_steps(steps, chain, q):
    with st.expander("🔵 Detail Langkah — Hash Search", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Hash Value", steps["hash_value"])
        c2.metric("Bucket Index", steps["bucket_index"])
        c3.metric("Chain Length", len(chain))
        st.markdown("---")
        if not chain:
            st.info("Bucket kosong — data tidak ada.")
            return
        for i, node in enumerate(chain):
            found = node["name"].lower() == q.lower()
            color = "#22c55e" if found else "#475569"
            icon  = "✅" if found else "⏭️"
            label = "<b style='color:#22c55e'>→ KETEMU!</b>" if found else "<span style='color:#64748b'>→ lanjut</span>"
            st.markdown(
                f"<div class='step-box' style='border-left:4px solid {color}'>"
                f"{icon} <b>Step {i+1}</b>: periksa <code>{node['name']}</code> {label}"
                f"</div>", unsafe_allow_html=True)

def render_binary_steps(bsteps, arr_len, q):
    with st.expander("🟠 Detail Langkah — Binary Search", expanded=True):
        st.markdown(f"**Array size**: `{arr_len}` &nbsp;|&nbsp; **Total iterasi**: `{len(bsteps)}`")
        st.markdown("---")
        for s in bsteps:
            if s["found"]:
                color, icon, arah = "#22c55e", "✅", "<b style='color:#22c55e'>KETEMU!</b>"
            elif s["go"] == "left":
                color, icon, arah = "#f59e0b", "⬅️", "<span style='color:#fcd34d'>geser KIRI</span>"
            else:
                color, icon, arah = "#3b82f6", "➡️", "<span style='color:#93c5fd'>geser KANAN</span>"
            st.markdown(
                f"<div class='step-box' style='border-left:4px solid {color}'>"
                f"{icon} <b>Step {s['step']}</b> &nbsp; lo=<code>{s['lo']}</code> "
                f"hi=<code>{s['hi']}</code> mid=<code>{s['mid']}</code><br>"
                f"&nbsp;&nbsp;&nbsp;cek → <code>{s['value']}</code> {arah}"
                f"</div>", unsafe_allow_html=True)

def complexity_card(title, color, best, avg, worst):
    st.markdown(f"""
    <div class='complexity-section'>
        <div class='complexity-title'>{title}</div>
        <div class='complexity-grid'>
            <div class='complexity-item'>
                <div class='complexity-case'>Best Case</div>
                <div class='complexity-val green'>{best}</div>
            </div>
            <div class='complexity-item'>
                <div class='complexity-case'>Average Case</div>
                <div class='complexity-val yellow'>{avg}</div>
            </div>
            <div class='complexity-item'>
                <div class='complexity-case'>Worst Case</div>
                <div class='complexity-val red'>{worst}</div>
            </div>
            <div class='complexity-item'>
                <div class='complexity-case'>Space</div>
                <div class='complexity-val yellow'>O(n)</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-box">
    <span class="trophy">🏆</span>
    <div>
        <h1>Pencarian Tercepat</h1>
        <p>Visualisasi Interaktif Hash Search &amp; Binary Search</p>
    </div>
    <div class="badge-group">
        <span class="badge blue">Hash O(1)</span>
        <span class="badge orange">Binary O(log n)</span>
        <span class="badge green">30+ Data</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Mode Pencarian")
    method = st.radio(
        "Pilih metode",
        ["🔵 Hash Search", "🟠 Binary Search", "⚡ Bandingkan Keduanya"],
        index=2,
    )
    st.divider()

    # Tambah Data
    st.markdown("## ➕ Tambah Data Baru")
    new_name = st.text_input("Nama Produk", key="add_name")
    new_cat  = st.selectbox("Kategori", ["Elektronik","Aksesoris","Audio","Storage",
                                          "Hardware","Jaringan","Mobile","Kamera","Wearable","Lainnya"])
    new_val  = st.number_input("Harga (Rp)", min_value=0, step=50000, value=500000)
    if st.button("➕ Tambah Data", use_container_width=True):
        if new_name.strip():
            new_id = f"{len(get_all_items())+1:03d}"
            st.session_state.custom_items.append({
                "id": new_id, "name": new_name.strip(),
                "category": new_cat, "nilai": int(new_val)
            })
            items, sorted_items, sorted_names, ht = rebuild()
            st.success(f"✅ '{new_name}' ditambahkan!")
            st.rerun()
        else:
            st.warning("Nama produk tidak boleh kosong!")

    if st.session_state.custom_items:
        st.divider()
        st.markdown("## 🗑️ Hapus Data Custom")
        del_name = st.selectbox("Pilih", [i["name"] for i in st.session_state.custom_items])
        if st.button("🗑️ Hapus", use_container_width=True):
            st.session_state.custom_items = [
                i for i in st.session_state.custom_items if i["name"] != del_name
            ]
            items, sorted_items, sorted_names, ht = rebuild()
            st.success(f"🗑️ '{del_name}' dihapus!")
            st.rerun()

    st.divider()
    # Stats Hash Table
    stats = ht.stats()
    st.markdown("## 📊 Statistik Hash Table")
    st.markdown(f"""
    <div class='stats-card'>
        <div class='stats-row'><span class='stats-label'>Ukuran Table</span><span class='stats-value'>{stats['size']}</span></div>
        <div class='stats-row'><span class='stats-label'>Bucket Terisi</span><span class='stats-value'>{stats['filled_buckets']}/{stats['size']}</span></div>
        <div class='stats-row'><span class='stats-label'>Max Chain</span><span class='stats-value'>{stats['max_chain']}</span></div>
        <div class='stats-row'><span class='stats-label'>Load Factor</span><span class='stats-value'>{stats['load_factor']}</span></div>
        <div class='stats-row'><span class='stats-label'>Total Item</span><span class='stats-value'>{len(items)}</span></div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("## 📋 Daftar Data")
    show_all = st.checkbox("Tampilkan semua", value=False)
    preview = items if show_all else items[:10]
    for it in preview:
        st.markdown(
            f"<div class='data-pill'>{it['name']}<span>#{it['id']}</span></div>",
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab_cari, tab_hist, tab_data, tab_info = st.tabs([
    "🔍 Pencarian", "📜 Riwayat", "📦 Semua Data", "📚 Info Algoritma"
])

# ─────────────────────────────────────────────────────────────
# TAB 1 — PENCARIAN
# ─────────────────────────────────────────────────────────────
with tab_cari:
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        query = st.text_input(
            "keyword",
            placeholder="🔍  Ketik nama produk … (bisa sebagian kata, tidak perlu persis)",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("Cari 🔍", use_container_width=True, type="primary")

    if search_clicked and query.strip():
        q = query.strip()
        items, sorted_items, sorted_names, ht = rebuild()

        # Partial match
        partial = partial_search(q)
        if partial:
            st.markdown(f"### 💡 Ditemukan **{len(partial)}** item mengandung kata *'{q}'*")
            render_table(partial)
            st.divider()
        else:
            st.warning(f"⚠️ Tidak ada data yang mengandung kata **'{q}'**.")

        st.markdown("### 🎯 Exact Match Search")

        # ── HASH ONLY ─────────────────────────────────────────
        if "Hash" in method:
            result, elapsed, steps, chain = do_hash(q)
            add_history(q, "Hash Search", result is not None, h_ms=elapsed)
            col_r, col_t = st.columns([3,1])
            with col_r:
                if result:
                    st.success(f"✅ **'{result['name']}'** ditemukan via Hash Search!")
                    render_table([result])
                else:
                    st.error("❌ Exact match tidak ditemukan di Hash Table.")
            with col_t:
                st.markdown(f"""<div class='time-card blue'>
                    <div class='time-label'>🔵 Hash Search</div>
                    <div class='time-val'>{elapsed:.4f}</div>
                    <div class='time-sub'>ms &nbsp;|&nbsp; O(1) avg</div>
                </div>""", unsafe_allow_html=True)
            render_hash_steps(steps, chain, q)

        # ── BINARY ONLY ───────────────────────────────────────
        elif "Binary" in method:
            result, elapsed, bsteps, idx = do_binary(q)
            add_history(q, "Binary Search", result is not None, b_ms=elapsed)
            col_r, col_t = st.columns([3,1])
            with col_r:
                if result:
                    st.success(f"✅ **'{result['name']}'** ditemukan via Binary Search!")
                    render_table([result])
                else:
                    st.error("❌ Exact match tidak ditemukan (Binary Search).")
            with col_t:
                st.markdown(f"""<div class='time-card orange'>
                    <div class='time-label'>🟠 Binary Search</div>
                    <div class='time-val'>{elapsed:.4f}</div>
                    <div class='time-sub'>ms &nbsp;|&nbsp; {len(bsteps)} iterasi</div>
                </div>""", unsafe_allow_html=True)
            render_binary_steps(bsteps, len(sorted_names), q)

        # ── COMPARE KEDUANYA ──────────────────────────────────
        else:
            hr, he, hsteps, hchain = do_hash(q)
            br, be, bsteps, bidx   = do_binary(q)
            add_history(q, "Keduanya", hr is not None or br is not None, h_ms=he, b_ms=be)

            winner = "🔵 Hash Search" if he <= be else "🟠 Binary Search"
            selisih = abs(he - be)
            st.markdown(f"""<div class='winner-banner'>
                ⚡ <b>{winner}</b> lebih cepat &nbsp;·&nbsp;
                selisih: <b>{selisih:.5f} ms</b>
            </div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""<div class='time-card blue'>
                    <div class='time-label'>🔵 Hash Search</div>
                    <div class='time-val'>{he:.4f}</div>
                    <div class='time-sub'>ms &nbsp;|&nbsp; O(1) average</div>
                </div>""", unsafe_allow_html=True)
                if hr:
                    st.success(f"✅ {hr['name']}")
                    render_table([hr])
                else:
                    st.error("❌ Tidak ditemukan")
                render_hash_steps(hsteps, hchain, q)

            with col2:
                st.markdown(f"""<div class='time-card orange'>
                    <div class='time-label'>🟠 Binary Search</div>
                    <div class='time-val'>{be:.4f}</div>
                    <div class='time-sub'>ms &nbsp;|&nbsp; {len(bsteps)} iterasi</div>
                </div>""", unsafe_allow_html=True)
                if br:
                    st.success(f"✅ {br['name']}")
                    render_table([br])
                else:
                    st.error("❌ Tidak ditemukan")
                render_binary_steps(bsteps, len(sorted_names), q)

            # ── Bar Chart ─────────────────────────────────────
            st.markdown("### 📊 Grafik Perbandingan Waktu (ms)")
            chart_df = pd.DataFrame({
                "Metode": ["Hash Search", "Binary Search"],
                "Waktu (ms)": [round(he, 6), round(be, 6)],
            })
            st.bar_chart(chart_df.set_index("Metode"), color=["#6366f1"])

    elif search_clicked:
        st.warning("⚠️ Masukkan kata kunci pencarian terlebih dahulu.")
    else:
        # Placeholder saat belum search
        st.markdown("""
        <div style='text-align:center; padding: 3rem 0; color: #334155;'>
            <div style='font-size:4rem'>🔍</div>
            <div style='font-size:1.1rem; margin-top:0.5rem'>Ketik kata kunci dan tekan <b>Cari</b></div>
            <div style='font-size:0.85rem; margin-top:0.3rem'>Pencarian parsial didukung — tidak perlu nama lengkap</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 2 — RIWAYAT
# ─────────────────────────────────────────────────────────────
with tab_hist:
    st.markdown("### 📜 Riwayat Pencarian (15 terakhir)")
    if st.session_state.history:
        col_a, col_b = st.columns([4,1])
        with col_b:
            if st.button("🗑️ Hapus Semua", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        df_h = pd.DataFrame(st.session_state.history)
        df_h.columns = ["Keyword","Metode","Ditemukan","Hash (ms)","Binary (ms)"]
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:2rem; color:#334155;'>
            <div style='font-size:3rem'>📭</div>
            <div>Belum ada riwayat pencarian.</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — SEMUA DATA
# ─────────────────────────────────────────────────────────────
with tab_data:
    items_now = get_all_items()
    st.markdown(f"### 📦 Semua Data — {len(items_now)} Item")

    # Filter kategori
    cats = ["Semua"] + sorted(list(set(i["category"] for i in items_now)))
    sel_cat = st.selectbox("Filter Kategori", cats)
    filtered = items_now if sel_cat == "Semua" else [i for i in items_now if i["category"] == sel_cat]

    render_table(filtered)
    st.caption(f"Menampilkan {len(filtered)} dari {len(items_now)} item.")

# ─────────────────────────────────────────────────────────────
# TAB 4 — INFO ALGORITMA
# ─────────────────────────────────────────────────────────────
with tab_info:
    st.markdown("### 📚 Penjelasan Algoritma")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔵 Hash Search")
        st.markdown("""
        **Hash Table** menyimpan data menggunakan *hash function* yang mengubah key
        menjadi index bucket. Pencarian dilakukan langsung ke bucket yang dituju
        tanpa perlu memeriksa data lain.

        **Cara kerja:**
        1. Hitung hash value dari key
        2. Langsung akses bucket di index tersebut
        3. Jika terjadi *collision*, cek chain (Separate Chaining)
        4. Cocokkan key → data ditemukan

        **Keunggulan:** Sangat cepat untuk pencarian tepat (exact match).
        """)
        complexity_card("🔵 Hash Search", "blue", "O(1)", "O(1)", "O(n)")

    with col2:
        st.markdown("#### 🟠 Binary Search")
        st.markdown("""
        **Binary Search** bekerja pada data yang **sudah diurutkan**.
        Algoritma membagi array menjadi dua bagian, lalu memilih sisi
        yang kemungkinan mengandung data target.

        **Cara kerja:**
        1. Tentukan lo, hi, dan mid
        2. Bandingkan data[mid] dengan target
        3. Jika target < mid → geser hi ke mid-1
        4. Jika target > mid → geser lo ke mid+1
        5. Ulangi sampai ditemukan atau lo > hi

        **Keunggulan:** Efisien untuk data besar yang sudah terurut.
        """)
        complexity_card("🟠 Binary Search", "orange", "O(1)", "O(log n)", "O(log n)")

    st.divider()
    st.markdown("### ⚡ Kapan Pakai Masing-Masing?")
    c1, c2 = st.columns(2)
    with c1:
        st.info("""
        **Gunakan Hash Search ketika:**
        - Butuh pencarian sangat cepat (real-time)
        - Data sering berubah (insert/delete)
        - Mencari berdasarkan key yang tepat
        - Memory tidak terlalu jadi masalah
        """)
    with c2:
        st.warning("""
        **Gunakan Binary Search ketika:**
        - Data sudah terurut dan jarang berubah
        - Memory terbatas (tidak butuh hash table)
        - Butuh pencarian range (misalnya antara A-Z)
        - Struktur data sudah berbentuk array
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align:center; color:#334155; font-size:0.85rem; padding:0.5rem 0;'>
    🏆 <b>Pencarian Tercepat</b> &nbsp;|&nbsp; Hash Search + Binary Search &nbsp;|&nbsp; Struktur Data & Algoritma
</div>""", unsafe_allow_html=True)
