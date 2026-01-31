from src.db.database import get_connection
from datetime import datetime
import json

# -----------------------------
# Save new call (already used)
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
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        "new"
    ))

    conn.commit()
    conn.close()


def get_all_calls():
    """Get all calls from the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id, timestamp, phone_number, audio_path, language,
            transcript, emergency_type, priority, confidence,
            keywords, location_text, latitude, longitude, status
        FROM calls
        ORDER BY timestamp DESC
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    # Convert to list of dicts
    calls = []
    for row in rows:
        calls.append({
            "id": row[0],
            "timestamp": row[1],
            "phone_number": row[2],
            "audio_path": row[3],
            "language": row[4],
            "transcript": row[5],
            "emergency_type": row[6],
            "priority": row[7],
            "confidence": row[8],
            "keywords": json.loads(row[9]) if row[9] else [],
            "location_text": row[10],
            "latitude": row[11],
            "longitude": row[12],
            "status": row[13]
        })
    
    return calls


def get_calls_by_status(status: str):
    """Get calls filtered by status"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id, timestamp, phone_number, audio_path, language,
            transcript, emergency_type, priority, confidence,
            keywords, location_text, latitude, longitude, status
        FROM calls
        WHERE status = ?
        ORDER BY timestamp DESC
    """, (status,))
    
    rows = cur.fetchall()
    conn.close()
    
    # Convert to list of dicts
    calls = []
    for row in rows:
        calls.append({
            "id": row[0],
            "timestamp": row[1],
            "phone_number": row[2],
            "audio_path": row[3],
            "language": row[4],
            "transcript": row[5],
            "emergency_type": row[6],
            "priority": row[7],
            "confidence": row[8],
            "keywords": json.loads(row[9]) if row[9] else [],
            "location_text": row[10],
            "latitude": row[11],
            "longitude": row[12],
            "status": row[13]
        })
    
    return calls


def get_call(call_id: int):
    """Get a single call by ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id, timestamp, phone_number, audio_path, language,
            transcript, emergency_type, priority, confidence,
            keywords, location_text, latitude, longitude, status
        FROM calls
        WHERE id = ?
    """, (call_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "timestamp": row[1],
        "phone_number": row[2],
        "audio_path": row[3],
        "language": row[4],
        "transcript": row[5],
        "emergency_type": row[6],
        "priority": row[7],
        "confidence": row[8],
        "keywords": json.loads(row[9]) if row[9] else [],
        "location_text": row[10],
        "latitude": row[11],
        "longitude": row[12],
        "status": row[13]
    }


def update_call_status(call_id: int, new_status: str):
    """Update the status of a call"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE calls
        SET status = ?
        WHERE id = ?
    """, (new_status, call_id))
    
    conn.commit()
    conn.close()


# -----------------------------
# Legacy functions (keeping for compatibility)
# -----------------------------
def get_calls(status=None):
    """Legacy function - use get_all_calls or get_calls_by_status instead"""
    if status:
        return get_calls_by_status(status)
    return get_all_calls()


def dispatch_call(call_id: int, unit: str = None):
    """Legacy function - use update_call_status instead"""
    update_call_status(call_id, "dispatched")


def resolve_call(call_id: int):
    """Legacy function - use update_call_status instead"""
    update_call_status(call_id, "resolved")
