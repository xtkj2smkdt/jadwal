in(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    uid, uname, role, pw_hash = row
    if pw_hash == hash_pw(password):
        return {"id": uid, "username": uname, "role": role}
    return None

def get_jadwal_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM jadwal ORDER BY id", conn)
    conn.close()
    return df

def add_jadwal(hari, jam, mata, guru, ruangan, ket):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO jadwal (hari,jam,mata_pelajaran,guru,ruangan,keterangan) VALUES (?,?,?,?,?,?)",
                (hari, jam, mata, guru, ruangan, ket))
    conn.commit()
    conn.close()

def update_jadwal(_id, hari, jam, mata, guru, ruangan, ket):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""UPDATE jadwal SET hari=?, jam=?, mata_pelajaran=?, guru=?, ruangan=?, keterangan=? WHERE id=?""",
                (hari, jam, mata, guru, ruangan, ket, _id))
    conn.commit()
    conn.close()

def delete_jadwal(_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM jadwal WHERE id=?", (_id,))
    conn.commit()
    conn.close()

# --- Streamlit UI ---
st.set_page_config(page_title="Aplikasi Jadwal Pelajaran", layout="wide")
st.title("📚 Aplikasi Jadwal Pelajaran — Streamlit")

# -- Authentication (simple)
if "user" not in st.session_state:
    st.session_state["user"] = None

col1, col2 = st.columns([2,1])
with col1:
    st.markdown("Silakan login untuk melihat / mengelola jadwal.")
with col2:
    if st.session_state["user"]:
        st.write(f"Login sebagai: **{st.session_state['user']['username']}** ({st.session_state['user']['role']})")
        if st.button("Logout"):
            st.session_state["user"] = None

if not st.session_state["user"]:
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            info = check_login(username.strip(), password)
            if info:
                st.session_state["user"] = info
                st.success(f"Sukses login sebagai {info['username']} ({info['role']})")
                st.experimental_rerun()
            else:
                st.error("Login gagal — periksa username / password.")

# Main content
st.markdown("---")
df = get_jadwal_df()

if st.session_state["user"] is None:
    st.subheader("Jadwal (hanya tampilan)")
    if df.empty:
        st.info("Belum ada data jadwal.")
    else:
        st.dataframe(df.drop(columns=["id"]).rename(columns={
            "hari":"Hari",
            "jam":"Jam",
            "mata_pelajaran":"Mata Pelajaran",
            "guru":"Guru",
            "ruangan":"Ruangan",
            "keterangan":"Keterangan"
        }))
else:
    role = st.session_state["user"]["role"]
    st.subheader("Jadwal")
    if df.empty:
        st.info("Belum ada data jadwal.")
    else:
        st.dataframe(df.drop(columns=[]).rename(columns={
            "id":"ID",
            "hari":"Hari",
            "jam":"Jam",
            "mata_pelajaran":"Mata Pelajaran",
            "guru":"Guru",
            "ruangan":"Ruangan",
            "keterangan":"Keterangan"
        }))

    if role == "ketua":
        st.markdown("### ✏️ Tambah / Edit Jadwal (Akses untuk Ketua)")
        with st.expander("Tambah Jadwal Baru"):
            with st.form("tambah_form"):
                hari = st.selectbox("Hari", ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"])
                jam = st.text_input("Jam (contoh: 07:00-08:30)")
                mata = st.text_input("Mata Pelajaran")
                guru = st.text_input("Guru")
                ruangan = st.text_input("Ruangan")
                ket = st.text_area("Keterangan (opsional)")
                tambah = st.form_submit_button("Tambah Jadwal")
                if tambah:
                    if not mata or not jam:
                        st.error("Jam dan Mata Pelajaran harus diisi.")
                    else:
                        add_jadwal(hari, jam, mata, guru, ruangan, ket)
                        st.success("Jadwal ditambahkan.")
                        st.experimental_rerun()
        st.markdown("#### Edit / Hapus")
        with st.expander("Pilih baris untuk edit / hapus"):
            st.write("Pilih ID jadwal yang ingin diedit atau dihapus.")
            ids = df["id"].tolist()
            if not ids:
                st.info("Belum ada data untuk diedit.")
            else:
                sel = st.selectbox("Pilih ID", ids)
                row = df[df["id"]==sel].iloc[0]
                with st.form("edit_form"):
                    hari_e = st.selectbox("Hari", ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"], index=["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"].index(row["hari"]) if row["hari"] in ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"] else 0)
                    jam_e = st.text_input("Jam", value=row["jam"])
                    mata_e = st.text_input("Mata Pelajaran", value=row["mata_pelajaran"])
                    guru_e = st.text_input("Guru", value=(row["guru"] or ""))
                    ruangan_e = st.text_input("Ruangan", value=(row["ruangan"] or ""))
                    ket_e = st.text_area("Keterangan", value=(row["keterangan"] or ""))
                    update_btn = st.form_submit_button("Simpan Perubahan")
                    delete_btn = st.form_submit_button("Hapus Jadwal")
                    if update_btn:
                        update_jadwal(sel, hari_e, jam_e, mata_e, guru_e, ruangan_e, ket_e)
                        st.success("Perubahan tersimpan.")
                        st.experimental_rerun()
                    if delete_btn:
                        delete_jadwal(sel)
                        st.success("Jadwal dihapus.")
                        st.experimental_rerun()
    else:
        st.info("Anda login sebagai viewer — hanya dapat melihat jadwal.")

    # Export
    st.markdown("---")
    st.subheader("Export / Unduh")
    df_export = get_jadwal_df()
    if not df_export.empty:
        csv = df_export.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="jadwal.csv", mime="text/csv")
        # small preview
        st.dataframe(df_export.rename(columns={
            "hari":"Hari","jam":"Jam","mata_pelajaran":"Mata Pelajaran","guru":"Guru","ruangan":"Ruangan","keterangan":"Keterangan"
        }))

st.markdown("---")
st.caption("Aplikasi sederhana: otentikasi lokal, simpan ke file SQLite `jadwal.db`. Untuk produksi gunakan sistem auth yang lebih aman.")
README.md
