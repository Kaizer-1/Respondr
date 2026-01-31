from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import os
import requests

from src.pipeline.process_call import CallProcessor
from src.db.call_repository import (
    save_call,
    get_all_calls,
    get_calls_by_status,
    get_call,
    update_call_status
)

# --------------------------------------------------
# App + Pipeline
# --------------------------------------------------

app = Flask(__name__)
CORS(app)  # 🔓 Allow frontend (Next.js) to access backend

# ⚠️ IMPORTANT: Create CallProcessor ONCE (prevents Whisper reload)
processor = CallProcessor()

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# --------------------------------------------------
# Twilio credentials (ENV ONLY — NEVER HARDCODE)
# --------------------------------------------------

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise RuntimeError(
        "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set as environment variables"
    )

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def download_recording(url: str, path: str):
    """
    Download Twilio recording using HTTP Basic Auth
    """
    r = requests.get(
        url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        timeout=30
    )
    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)

# --------------------------------------------------
# Voice webhook (Twilio entry)
# --------------------------------------------------

@app.route("/voice", methods=["POST"])
def voice():
    print("📞 Incoming call")
    
    caller_number = request.form.get("From", "Unknown")
    print(f"📱 Caller: {caller_number}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        Please explain your emergency after the beep.
    </Say>

    <Record
        recordingStatusCallback="/recording?from={caller_number}"
        recordingStatusCallbackMethod="POST"
        maxLength="120"
        playBeep="true"
    />

    <Say voice="alice">
        Thank you. Help is being arranged.
    </Say>
</Response>
"""
    return Response(twiml, mimetype="text/xml")

# --------------------------------------------------
# Recording callback (Twilio → ASR → NLP → DB)
# --------------------------------------------------

@app.route("/recording", methods=["POST"])
def recording():
    print("🎧 Recording callback received")
    print("Form:", dict(request.form))
    print("Args:", dict(request.args))

    recording_url = request.form.get("RecordingUrl")
    recording_sid = request.form.get("RecordingSid")

    if not recording_url:
        return "No recording", 400

    wav_url = recording_url + ".wav"
    local_path = os.path.join(RECORDINGS_DIR, f"{recording_sid}.wav")

    try:
        print(f"⬇️ Downloading: {wav_url}")
        download_recording(wav_url, local_path)
        print(f"✅ Saved: {local_path}")

        print("🧠 Running ASR + NLP pipeline...")
        result = processor.process(local_path)

        phone_number = request.args.get("from")
        if not phone_number:
            phone_number = request.form.get("From")
        if not phone_number:
            phone_number = "Unknown"
        
        print(f"📱 Phone number captured: {phone_number}")

        call_data = {
            "phone_number": phone_number,
            "audio_path": local_path,
            "language": result["language"],
            "transcript": result["transcript"],
            "analysis": result["analysis"]
        }

        save_call(call_data)

        print("\n🚨 NEW CALL ANALYSIS")
        print(result)

    except Exception:
        import traceback
        traceback.print_exc()

    return "OK", 200

# --------------------------------------------------
# API ROUTES (FOR FRONTEND DASHBOARD)
# --------------------------------------------------

@app.route("/api/calls", methods=["GET"])
def api_get_calls():
    status = request.args.get("status")
    try:
        calls = get_calls_by_status(status) if status else get_all_calls()
        return jsonify({
            "success": True,
            "calls": calls,
            "count": len(calls)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/calls/<int:call_id>/dispatch", methods=["POST"])
def api_dispatch_call(call_id):
    call = get_call(call_id)
    if not call:
        return jsonify({"success": False, "error": "Call not found"}), 404

    update_call_status(call_id, "dispatched")
    return jsonify({"success": True})


@app.route("/api/calls/<int:call_id>/resolve", methods=["POST"])
def api_resolve_call(call_id):
    call = get_call(call_id)
    if not call:
        return jsonify({"success": False, "error": "Call not found"}), 404

    update_call_status(call_id, "resolved")
    return jsonify({"success": True})

# --------------------------------------------------
# Run (NO DEBUG, NO AUTO-RELOAD)
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False
    )
