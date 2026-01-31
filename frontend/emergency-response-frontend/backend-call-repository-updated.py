"""
UPDATED call_repository.py with all methods needed for the dashboard API

Replace your existing src/db/call_repository.py with this code.
"""

from src.db.database import get_connection
from datetime import datetime
import json

# -----------------------------
# Save new call (already working)
# -----------------------------
def save_call(call_data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO calls (
            timestamp,
            phone_number,
            audio_path,
            language,
            transcript,
            emergency_type,
            priority,
            confidence,
            keywords,
            location_text,
            latitude,
            longitude,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        call_data.get("phone_number"),
        call_data.get("audio_path"),
        call_data.get("language"),
        call_data.get("transcript"),
        call_data["analysis"].get("type"),
        call_data["analysis"].get("priority"),
        call_data["analysis"].get("confidence"),
        json.dumps(call_data["analysis"].get("keywords")),
        call_data["analysis"].get("location", {}).get("text")
            if call_data["analysis"].get("location") else None,
        call_data["analysis"].get("geo", {}).get("lat")
            if call_data["analysis"].get("geo") else None,
        call_data["analysis"].get("geo", {}).get("lng")
            if call_data["analysis"].get("geo") else None,
        "new",
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


# -----------------------------
# NEW: Get all calls
# -----------------------------
def get_all_calls():
    """Get all calls with all fields"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM calls
        ORDER BY created_at DESC
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# -----------------------------
# NEW: Get calls by status
# -----------------------------
def get_calls_by_status(status: str):
    """Get calls filtered by status (new, dispatched, resolved)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM calls
        WHERE status = ?
        ORDER BY created_at DESC
    """, (status,))
    
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# -----------------------------
# NEW: Get single call by ID
# -----------------------------
def get_call(call_id: int):
    """Get a specific call by ID"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM calls WHERE id = ?", (call_id,))
    row = cur.fetchone()
    conn.close()
    
    return dict(row) if row else None


# -----------------------------
# NEW: Update call status
# -----------------------------
def update_call_status(call_id: int, status: str):
    """Update the status of a call"""
    conn = get_connection()
    cur = conn.cursor()
    
    update_fields = {"status": status}
    
    if status == "dispatched":
        update_fields["dispatched_at"] = datetime.utcnow().isoformat()
    
    set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
    values = list(update_fields.values()) + [call_id]
    
    cur.execute(f"""
        UPDATE calls
        SET {set_clause}
        WHERE id = ?
    """, values)
    
    conn.commit()
    conn.close()


# -----------------------------
# UPDATED: Dispatch a call
# -----------------------------
def dispatch_call(call_id: int, unit: str = "Unit-A1"):
    """Dispatch a call to a unit"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE calls
        SET status = 'dispatched',
            assigned_unit = ?,
            dispatched_at = ?
        WHERE id = ?
    """, (unit, datetime.utcnow().isoformat(), call_id))

    conn.commit()
    conn.close()


# -----------------------------
# UPDATED: Resolve a call
# -----------------------------
def resolve_call(call_id: int):
    """Mark a call as resolved"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE calls
        SET status = 'resolved'
        WHERE id = ?
    """, (call_id,))

    conn.commit()
    conn.close()


# Add import at the top
import sqlite3
