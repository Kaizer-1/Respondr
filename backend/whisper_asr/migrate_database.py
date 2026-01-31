"""
Database Migration Script
Run this ONCE to add missing columns to your existing database
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/respondr.db")

def migrate_database():
    """Add missing columns to existing database"""
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if columns exist and add them if they don't
    columns_to_add = [
        ("status", "TEXT DEFAULT 'new'"),
        ("assigned_unit", "TEXT"),
        ("dispatched_at", "TEXT"),
        ("created_at", "TEXT DEFAULT (datetime('now'))")
    ]
    
    # Get existing columns
    cur.execute("PRAGMA table_info(calls)")
    existing_columns = [row[1] for row in cur.fetchall()]
    
    for column_name, column_def in columns_to_add:
        if column_name not in existing_columns:
            try:
                cur.execute(f"ALTER TABLE calls ADD COLUMN {column_name} {column_def}")
                print(f"✅ Added column: {column_name}")
            except Exception as e:
                print(f"⚠️  Column {column_name} might already exist: {e}")
        else:
            print(f"✓ Column {column_name} already exists")
    
    conn.commit()
    conn.close()
    
    print("✅ Database migration completed!")

if __name__ == "__main__":
    migrate_database()
