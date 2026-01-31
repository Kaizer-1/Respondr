"""
Emergency Response Backend API Routes
Add these routes to your Flask app.py

INSTALLATION:
1. pip install flask-cors
2. Add 'from flask_cors import CORS' to your imports
3. Add 'CORS(app)' after creating your Flask app
4. Copy all these routes into your app.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from src.db.call_repository import CallRepository

# Add to your existing app.py after Flask app initialization
# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend

@app.route('/api/calls', methods=['GET'])
def get_calls():
    """
    Get all calls or filter by status
    Query params: status (optional) - 'new', 'dispatched', or 'resolved'
    """
    try:
        repo = CallRepository()
        status = request.args.get('status')
        
        if status:
            calls = repo.get_calls_by_status(status)
        else:
            calls = repo.get_all_calls()
        
        return jsonify({
            'success': True,
            'calls': calls,
            'count': len(calls)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calls/<int:call_id>', methods=['GET'])
def get_call(call_id):
    """Get a specific call by ID"""
    try:
        repo = CallRepository()
        call = repo.get_call(call_id)
        
        if not call:
            return jsonify({
                'success': False,
                'error': 'Call not found'
            }), 404
        
        return jsonify({
            'success': True,
            'call': call
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calls/<int:call_id>/dispatch', methods=['POST'])
def dispatch_call(call_id):
    """
    Dispatch a call to emergency responders
    Changes status from 'new' to 'dispatched'
    """
    try:
        repo = CallRepository()
        call = repo.get_call(call_id)
        
        if not call:
            return jsonify({
                'success': False,
                'error': 'Call not found'
            }), 404
        
        if call['status'] != 'new':
            return jsonify({
                'success': False,
                'error': f'Call already {call["status"]}'
            }), 400
        
        repo.update_call_status(call_id, 'dispatched')
        
        return jsonify({
            'success': True,
            'message': 'Call dispatched successfully',
            'call_id': call_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calls/<int:call_id>/resolve', methods=['POST'])
def resolve_call(call_id):
    """
    Resolve a dispatched call
    Changes status from 'dispatched' to 'resolved'
    """
    try:
        repo = CallRepository()
        call = repo.get_call(call_id)
        
        if not call:
            return jsonify({
                'success': False,
                'error': 'Call not found'
            }), 404
        
        if call['status'] != 'dispatched':
            return jsonify({
                'success': False,
                'error': f'Cannot resolve call with status: {call["status"]}'
            }), 400
        
        repo.update_call_status(call_id, 'resolved')
        
        return jsonify({
            'success': True,
            'message': 'Call resolved successfully',
            'call_id': call_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        repo = CallRepository()
        all_calls = repo.get_all_calls()
        
        stats = {
            'total': len(all_calls),
            'new': len([c for c in all_calls if c['status'] == 'new']),
            'dispatched': len([c for c in all_calls if c['status'] == 'dispatched']),
            'resolved': len([c for c in all_calls if c['status'] == 'resolved']),
            'by_type': {
                'ambulance': len([c for c in all_calls if c.get('emergency_type') == 'ambulance']),
                'fire': len([c for c in all_calls if c.get('emergency_type') == 'fire']),
                'police': len([c for c in all_calls if c.get('emergency_type') == 'police'])
            },
            'by_priority': {
                'critical': len([c for c in all_calls if c.get('priority') == 'critical']),
                'high': len([c for c in all_calls if c.get('priority') == 'high']),
                'medium': len([c for c in all_calls if c.get('priority') == 'medium']),
                'low': len([c for c in all_calls if c.get('priority') == 'low'])
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# IMPORTANT: Make sure your CallRepository has these methods:
# - get_all_calls()
# - get_calls_by_status(status)
# - get_call(call_id)
# - update_call_status(call_id, status)
