"""
Add these routes to your app.py Flask application
to enable the frontend dashboard to work.

Just copy and paste this into your app.py file.
"""

from flask import jsonify
from flask_cors import CORS
from src.db.call_repository import get_calls, dispatch_call, resolve_call

# Add CORS to your Flask app (add this near the top after app = Flask(__name__))
CORS(app)

# --------------------------------------------------
# Dashboard API Endpoints
# --------------------------------------------------

@app.route("/api/calls", methods=["GET"])
def api_get_calls():
    """
    Get all calls or filter by status
    Example: /api/calls?status=new
    """
    status = request.args.get("status")
    
    try:
        rows = get_calls(status)
        
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
                "keywords": row[9],
                "location_text": row[10],
                "latitude": row[11],
                "longitude": row[12],
                "status": row[13] if len(row) > 13 else "new",
                "assigned_unit": row[14] if len(row) > 14 else None,
                "dispatched_at": row[15] if len(row) > 15 else None
            })
        
        return jsonify(calls), 200
        
    except Exception as e:
        print(f"Error fetching calls: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/calls/<int:call_id>/dispatch", methods=["POST"])
def api_dispatch_call(call_id):
    """
    Dispatch a call to a unit
    Body: { "unit": "Unit-A1" }
    """
    try:
        data = request.get_json()
        unit = data.get("unit", "Unknown Unit")
        
        dispatch_call(call_id, unit)
        
        return jsonify({"message": "Call dispatched successfully"}), 200
        
    except Exception as e:
        print(f"Error dispatching call: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/calls/<int:call_id>/resolve", methods=["POST"])
def api_resolve_call(call_id):
    """
    Mark a call as resolved
    """
    try:
        resolve_call(call_id)
        
        return jsonify({"message": "Call resolved successfully"}), 200
        
    except Exception as e:
        print(f"Error resolving call: {e}")
        return jsonify({"error": str(e)}), 500
