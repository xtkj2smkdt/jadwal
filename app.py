db_init.py

#Jalankan sekali untuk membuat database contoh dan user awal.

import sqlite3
import hashlib
import os

DB = "jadwal.db"

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def init_db():
    if os.path.exists(DB):
        print(f"{DB} sudah ada. Menggunakan file yang ada.")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # table users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('ketua','viewer'))
    )
    """)

    # table schedule
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jadwal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hari TEXT NOT NULL,
        jam TEXT NOT NULL,
        mata_pelajaran TEXT NOT NULL,
        guru TEXT,
        ruangan TEXT,
        keterangan TEXT
    )
    """)

    # insert default users if not exists
    users = [
        ("ketua", hash_pw("ketua123"), "ketua"),
        ("andi", hash_pw("andi123"), "viewer"),
        ("sinta", hash_pw("sinta123"), "viewer"),
    ]
    for u, p, r in users:
        try:
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (u, p, r))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("Inisialisasi DB selesai. Default user: ketua/ketua123 (role ketua).")

if __name__ == "__main__":
    init_db()

app.py
