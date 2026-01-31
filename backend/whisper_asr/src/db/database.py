# src/db/database.py

import sqlite3
from pathlib import Path

DB_PATH = Path("data/respondr.db")

def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        phone_number TEXT,
        audio_path TEXT,
        language TEXT,
        transcript TEXT,
        emergency_type TEXT,
        priority TEXT,
        confidence REAL,
        keywords TEXT,
        location_text TEXT,
        latitude REAL,
        longitude REAL
    )
    """)

    conn.commit()
    conn.close()