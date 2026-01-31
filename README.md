# Respondr — Real-Time Emergency Response System

Respondr is an end-to-end emergency response platform that converts live distress calls into structured incidents and routes them through an operator–station workflow. Incoming calls are transcribed, analyzed for intent, priority, and location, and surfaced on real-time dashboards to enable faster, informed dispatch decisions.

---

## What the System Does

1. A caller places an emergency phone call  
2. The call audio is recorded and processed automatically  
3. Speech is transcribed and analyzed for:
   - Emergency type (fire, medical, police)
   - Priority level
   - Location cues from speech
4. The incident appears instantly on the **Operator Dashboard**
5. Operators dispatch incidents to stations
6. Dispatched cases appear on the **Station Dashboard** for resolution

---

## Dashboards Overview

### Operator Dashboard
- Live incoming emergency calls
- Caller number
- Full call transcript
- Automatically detected emergency type & priority
- One-click dispatch to stations
- Clean, control-room style interface

### Station Dashboard
- View dispatched emergencies
- Caller details and transcript
- Emergency type, priority, and location context
- Track and resolve active incidents

The dashboards are designed to reflect real emergency control-room workflows, prioritizing clarity, urgency, and speed.

---

## Screenshots

### Operator Dashboard
![Operator Dashboard]((https://github.com/Kaizer-1/Respondr/blob/main/operator-dashboard.jpeg))

### Station Dashboard
![Station Dashboard](((https://github.com/Kaizer-1/Respondr/blob/main/station-dashboard.jpeg)))

---

## High-Level Architecture
Emergency Call
↓
Call Recording
↓
Speech Transcription
↓
Emergency Analysis (type, priority, location)
↓
Backend APIs
↓
Operator Dashboard → Dispatch
↓
Station Dashboard → Resolution

---

## Repository Structure
backend/   → Call processing, analysis pipeline, APIs, database
frontend/  → Operator and Station dashboards

---

## Running the Project Locally

> Note: Twilio credentials are required and must be set via environment variables. No secrets are stored in the repository.

---

### Backend Setup (macOS)

```bash
cd backend/whisper_asr
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio
pip install -U openai-whisper
brew install ffmpeg
pip install soundfile numpy scipy

export PYTHONPATH=$(pwd)
export TWILIO_ACCOUNT_SID=your_sid
export TWILIO_AUTH_TOKEN=your_token

python3 twilio_server/app.py
```
Backend runs at:
http://127.0.0.1:8080

---

### Backend Setup (Windows – PowerShell)

```bash
cd backend\whisper_asr
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install torch torchvision torchaudio
pip install -U openai-whisper
pip install soundfile numpy scipy

$env:PYTHONPATH=(Get-Location)
$env:TWILIO_ACCOUNT_SID="your_sid"
$env:TWILIO_AUTH_TOKEN="your_token"

python twilio_server/app.py
```

---

### Exposing the Backend with ngrok (Required for Calls)
Twilio needs a public HTTPS URL to send call and recording webhooks. Since the backend runs locally, ngrok is required.

Step 1: Install ngrok
macOS
```bash
brew install ngrok
```

Windows
	•	Download ngrok
	•	Add ngrok to PATH

Step 2: Start ngrok
```bash
ngrok http 8080
```
You’ll see output like:
```bash
Forwarding https://abcd-1234.ngrok-free.app -> http://localhost:8080
```

Step 3: Configure Twilio Webhooks
In the Twilio Console:
	•	Voice Webhook URL
  ```bash
  https://abcd-1234.ngrok-free.app/voice
  ```
  •	Recording Callback
  ```bash
  https://abcd-1234.ngrok-free.app/recording
  ```
ngrok URLs change every time you restart it. Update Twilio whenever ngrok restarts.

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
---

### Environment Variables

The following variables must be set before running the backend:
	•	TWILIO_ACCOUNT_SID
	•	TWILIO_AUTH_TOKEN

These are used only for call handling and recording.

---

### Project Scope & Intent

This project focuses on:
	•	Real-time systems engineering
	•	Speech-driven automation
	•	Applied AI for emergency response
	•	End-to-end pipeline ownership (audio → intelligence → action)

Respondr is not a UI-only demo — it models real-world emergency workflows with live calls, automated analysis, and operational dashboards.
