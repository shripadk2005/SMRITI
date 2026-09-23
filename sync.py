import json
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User
from models.patient import Patient
from models.game import Game, GameResult
from models.reminder import Reminder
from models.alert import SyncQueue
from . import login_required

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/api/sync', methods=['POST'])
def api_sync_data():
    """
    Synchronizes offline game results, reminder completions, and activity logs
    stored in browser IndexedDB/localStorage while in offline mode.
    """
    payload = request.get_json() or {}
    items = payload.get('items', [])
    patient_id = payload.get('patient_id') or session.get('patient_id')

    if not patient_id:
        # If not in session, attempt to get default or first patient
        user_id = session.get('user_id')
        if user_id:
            u = User.query.get(user_id)
            if u and u.patient_profile:
                patient_id = u.patient_profile.id
        if not patient_id:
            p = Patient.query.first()
            patient_id = p.id if p else 1

    synced_results_count = 0
    synced_reminders_count = 0
    errors = []

    for item in items:
        data_type = item.get('type')
        data_content = item.get('data', {})

        try:
            # Store in SyncQueue audit log
            sync_log = SyncQueue(
                patient_id=patient_id,
                data_type=data_type,
                data=json.dumps(data_content),
                synced=True,
                created_at=datetime.now()
            )
            db.session.add(sync_log)

            if data_type == 'game_result':
                game_slug = data_content.get('game_slug')
                game = Game.query.filter_by(slug=game_slug).first() if game_slug else None
                game_id = game.id if game else int(data_content.get('game_id', 1))

                # Parse played_at timestamp if provided
                played_at_str = data_content.get('played_at')
                played_at = datetime.fromisoformat(played_at_str) if played_at_str else datetime.now()

                result = GameResult(
                    patient_id=patient_id,
                    game_id=game_id,
                    score=int(data_content.get('score', 0)),
                    accuracy=float(data_content.get('accuracy', 100.0)),
                    completion_time=float(data_content.get('completion_time', 30.0)),
                    attempts=int(data_content.get('attempts', 1)),
                    difficulty=data_content.get('difficulty', 'EASY'),
                    played_at=played_at
                )
                db.session.add(result)
                synced_results_count += 1

            elif data_type == 'reminder_status':
                rem_id = data_content.get('reminder_id')
                if rem_id:
                    reminder = Reminder.query.get(rem_id)
                    if reminder:
                        new_status = data_content.get('status', 'completed')
                        reminder.status = new_status
                        if new_status == 'completed':
                            reminder.completed_at = datetime.now()
                        synced_reminders_count += 1

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            errors.append(f"Error syncing item {data_type}: {str(e)}")

    return jsonify({
        'status': 'success',
        'synced_results': synced_results_count,
        'synced_reminders': synced_reminders_count,
        'total_synced': synced_results_count + synced_reminders_count,
        'errors': errors,
        'timestamp': datetime.now().isoformat()
    }), 200
