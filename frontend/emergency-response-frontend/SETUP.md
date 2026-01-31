# Emergency Response System - Frontend Setup Guide

## Overview

This is a real-time emergency response dashboard system that connects to your Whisper ASR backend. The system includes two main views:

1. **Operator Dashboard** - For emergency operators to view live calls and dispatch them
2. **Station Dashboard** - For emergency responders to view dispatched calls and mark them as resolved

## Prerequisites

- Node.js 18+ installed
- Your backend Flask server running on port 8080
- The backend should have the API routes from `backend-api-routes.py` integrated

## Backend Setup (REQUIRED FIRST)

### Step 1: Add API Routes to Your Backend

Open your backend's `app.py` and add the Flask-CORS package and the API routes:

```bash
# In your backend directory (whisper_asr)
pip install flask-cors
```

Then add these lines to your `app.py`:

```python
from flask_cors import CORS

# After creating your Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
```

Copy all the routes from `backend-api-routes.py` (provided separately) into your `app.py` file.

### Step 2: Update CallRepository

Make sure your `src/db/call_repository.py` has these methods:

```python
def get_all_calls(self):
    """Get all calls from database"""
    query = "SELECT * FROM calls ORDER BY timestamp DESC"
    return self.execute_query(query)

def get_calls_by_status(self, status):
    """Get calls filtered by status"""
    query = "SELECT * FROM calls WHERE status = ? ORDER BY timestamp DESC"
    return self.execute_query(query, (status,))

def get_call(self, call_id):
    """Get a specific call by ID"""
    query = "SELECT * FROM calls WHERE id = ?"
    results = self.execute_query(query, (call_id,))
    return results[0] if results else None

def update_call_status(self, call_id, status):
    """Update call status"""
    query = "UPDATE calls SET status = ? WHERE id = ?"
    self.execute_query(query, (status, call_id))
```

### Step 3: Start Your Backend

```bash
cd /path/to/whisper_asr
python app.py
```

Your backend should now be running on http://127.0.0.1:8080

## Frontend Setup

### Step 1: Install Dependencies

```bash
npm install
```

This will install all required packages including:
- Next.js 15
- React 19
- Leaflet (for maps)
- shadcn/ui components
- Tailwind CSS v4

### Step 2: Start Development Server

```bash
npm run dev
```

The frontend will start on http://localhost:3000

### Step 3: Access the Dashboards

- **Operator Dashboard**: http://localhost:3000/operator
- **Station Dashboard**: http://localhost:3000/station
- **Home**: http://localhost:3000 (redirects to operator)

## Features

### Operator Dashboard
- View all new emergency calls in real-time
- See emergency details: transcript, location, priority, keywords
- Dispatch calls to emergency responders
- Interactive map showing all emergency locations
- Auto-refresh every 3 seconds
- Color-coded priorities (Critical=Red, High=Orange, Medium=Yellow, Low=Blue)

### Station Dashboard
- View all dispatched emergencies
- See full emergency details
- Mark emergencies as resolved
- Interactive map of dispatched locations
- Auto-refresh every 3 seconds

### Map Features
- OpenStreetMap integration
- Custom markers based on emergency type (Fire=🔥, Ambulance=🚑, Police=🚔)
- Color-coded markers by priority
- Click markers to see details
- Auto-zoom to fit all emergencies

## API Endpoints Used

The frontend connects to these backend endpoints:

- `GET /api/calls?status=new` - Get new emergency calls
- `GET /api/calls?status=dispatched` - Get dispatched calls
- `GET /api/calls/<id>` - Get specific call details
- `POST /api/calls/<id>/dispatch` - Dispatch a call
- `POST /api/calls/<id>/resolve` - Resolve a call
- `GET /api/stats` - Get dashboard statistics

## Environment Variables

You can optionally set the backend URL:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8080
```

Default is `http://127.0.0.1:8080` if not set.

## Troubleshooting

### "Failed to load emergencies"
- Make sure your backend is running on port 8080
- Check if CORS is enabled in your Flask app
- Verify the API routes are added to app.py

### No emergencies showing up
- Check if your database has calls with `status='new'` or `status='dispatched'`
- Run a test call through your Twilio integration
- Check browser console for errors

### Map not loading
- Check internet connection (map tiles load from OpenStreetMap)
- Verify Leaflet CSS is loading (check browser console)
- Make sure latitude/longitude values are valid

### CORS errors
- Add `flask-cors` to your backend
- Make sure `CORS(app)` is called in app.py

## Database Schema

Expected `calls` table structure:

```sql
CREATE TABLE calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_sid TEXT,
    caller_phone TEXT,
    transcript TEXT,
    emergency_type TEXT,
    priority TEXT,
    keywords TEXT,
    location_text TEXT,
    latitude REAL,
    longitude REAL,
    confidence REAL,
    status TEXT DEFAULT 'new',
    timestamp TEXT
);
```

## Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui components
- Leaflet (maps)
- Sonner (notifications)

**Backend:**
- Flask
- SQLite
- Whisper ASR
- NLP Pipeline
- Location Extraction

## Support

If you encounter any issues:
1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify API endpoints are responding correctly
4. Make sure database has the correct schema

## Production Deployment

For production deployment:

1. Update API URL in environment variables
2. Enable HTTPS for both frontend and backend
3. Configure proper CORS origins (don't use `CORS(app)` without origins)
4. Use a production database (PostgreSQL recommended)
5. Deploy frontend to Vercel
6. Deploy backend to a cloud service (AWS, GCP, Azure)
