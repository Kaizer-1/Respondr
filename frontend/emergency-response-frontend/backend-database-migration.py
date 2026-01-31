"""
DATABASE MIGRATION SCRIPT
Run this ONCE to add missing columns to your database.

How to use:
1. Save this file in your project root
2. Run: python backend-database-migration.py
3. It will add the missing columns: status, assigned_unit, dispatched_at, created_at
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/respondr.db")

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("🔧 Starting database migration...")
    
    # Check if columns exist and add them if needed
    columns_to_add = [
        ("status", "TEXT DEFAULT 'new'"),
        ("assigned_unit", "TEXT"),
        ("dispatched_at", "TEXT"),
        ("created_at", "TEXT DEFAULT (datetime('now'))")
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cur.execute(f"ALTER TABLE calls ADD COLUMN {column_name} {column_def}")
            print(f"✅ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"⏭️  Column {column_name} already exists, skipping")
            else:
                print(f"❌ Error adding {column_name}: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate_database()
