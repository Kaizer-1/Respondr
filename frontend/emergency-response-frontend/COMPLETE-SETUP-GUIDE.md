# Complete Emergency Response System Setup Guide

## Backend Setup (Python/Flask)

### Step 1: Database Migration
Run this ONCE to add required columns to your database:

```bash
python backend-database-migration.py
```

This adds: `status`, `assigned_unit`, `dispatched_at`, `created_at` columns.

### Step 2: Update call_repository.py
Replace your `src/db/call_repository.py` with the code from `backend-call-repository-updated.py`

This adds the required methods:
- `get_all_calls()`
- `get_calls_by_status(status)`
- `get_call(call_id)`
- `update_call_status(call_id, status)`

### Step 3: Install Flask-CORS
```bash
pip install flask-cors
```

### Step 4: Update Your app.py
Add these lines to your `app.py`:

```python
from flask_cors import CORS
from src.db.call_repository import (
    get_all_calls, 
    get_calls_by_status, 
    get_call, 
    update_call_status
)
import sqlite3

# After app = Flask(__name__)
CORS(app)

# Add these API routes (copy from backend-api-routes.py):

@app.route('/api/calls', methods=['GET'])
def api_get_calls():
    status = request.args.get('status')
    try:
        if status:
            calls = get_calls_by_status(status)
        else:
            calls = get_all_calls()
        
        return jsonify({
            'success': True,
            'calls': calls,
            'count': len(calls)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calls/<int:call_id>/dispatch', methods=['POST'])
def api_dispatch_call(call_id):
    try:
        call = get_call(call_id)
        if not call:
            return jsonify({'success': False, 'error': 'Call not found'}), 404
        
        update_call_status(call_id, 'dispatched')
        return jsonify({'success': True, 'message': 'Call dispatched'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calls/<int:call_id>/resolve', methods=['POST'])
def api_resolve_call(call_id):
    try:
        call = get_call(call_id)
        if not call:
            return jsonify({'success': False, 'error': 'Call not found'}), 404
        
        update_call_status(call_id, 'resolved')
        return jsonify({'success': True, 'message': 'Call resolved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Step 5: Run Backend
```bash
python app.py
```

Backend should now be running on `http://127.0.0.1:8080` with all API endpoints ready!

---

## Frontend Setup (Next.js)

### Step 1: Install Dependencies
```bash
npm install
```

### Step 2: Run Frontend
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

---

## Testing the System

### 1. Make a test call to your Twilio number
Your backend will process it and save to database with status="new"

### 2. Open Operator Dashboard
Navigate to `http://localhost:3000/operator`
- You should see the new emergency call
- Click "Dispatch" to send it to field units

### 3. Open Station Dashboard
Navigate to `http://localhost:3000/station`
- You should see the dispatched emergency
- Click "Mark Resolved" when complete

### 4. Check Database
```bash
sqlite3 data/respondr.db
SELECT id, emergency_type, priority, status, phone_number FROM calls;
```

---

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/calls` | GET | Get all calls |
| `/api/calls?status=new` | GET | Get new calls only |
| `/api/calls?status=dispatched` | GET | Get dispatched calls |
| `/api/calls/<id>/dispatch` | POST | Dispatch a call |
| `/api/calls/<id>/resolve` | POST | Resolve a call |

---

## Troubleshooting

**Backend not starting?**
- Check if port 8080 is available
- Verify all imports are correct
- Run migration script first

**Frontend can't connect?**
- Verify backend is running on port 8080
- Check browser console for CORS errors
- Make sure flask-cors is installed

**No calls showing?**
- Make a test call to Twilio number
- Check database: `sqlite3 data/respondr.db` then `SELECT * FROM calls;`
- Verify status column exists in database
