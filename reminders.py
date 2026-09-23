from datetime import datetime, date
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from models import db
from models.user import User
from models.patient import Patient
from models.reminder import Reminder
from models.alert import Alert
from . import login_required

reminders_bp = Blueprint('reminders', __name__)

def get_current_patient_id():
    pid = session.get('patient_id')
    if pid:
        return pid
    uid = session.get('user_id')
    if uid:
        u = User.query.get(uid)
        if u and u.patient_profile:
            return u.patient_profile.id
    first = Patient.query.first()
    return first.id if first else 1

@reminders_bp.route('/reminders')
@login_required()
def reminders_page():
    pid = get_current_patient_id()
    patient = Patient.query.get(pid)
    reminders = Reminder.query.filter_by(patient_id=pid).order_by(Reminder.reminder_time.asc()).all()
    
    # Check if any past time reminders are still pending and mark missed/trigger alert
    return render_template(
        'reminders.html',
        patient=patient,
        reminders=reminders
    )

# REST API Endpoints
@reminders_bp.route('/api/reminders', methods=['GET'])
@login_required()
def api_get_reminders():
    pid = request.args.get('patient_id', type=int) or get_current_patient_id()
    reminders = Reminder.query.filter_by(patient_id=pid).order_by(Reminder.reminder_time.asc()).all()
    return jsonify([r.to_dict() for r in reminders]), 200

@reminders_bp.route('/api/reminders', methods=['POST'])
@login_required()
def api_create_reminder():
    data = request.get_json() or {}
    pid = data.get('patient_id') or get_current_patient_id()
    rem_type = data.get('type', 'activity')
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    reminder_time = data.get('reminder_time', '10:00 AM').strip()
    frequency = data.get('frequency', 'Daily')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    try:
        rem = Reminder(
            patient_id=pid,
            type=rem_type,
            title=title,
            description=description,
            reminder_time=reminder_time,
            frequency=frequency,
            status='pending',
            date_scheduled=date.today()
        )
        db.session.add(rem)
        db.session.commit()
        return jsonify({'message': 'Reminder created', 'reminder': rem.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@login_required()
def api_update_reminder(reminder_id):
    rem = Reminder.query.get_or_404(reminder_id)
    data = request.get_json() or {}

    if 'status' in data:
        rem.status = data['status']
        if data['status'] == 'completed':
            rem.completed_at = datetime.now()
    if 'title' in data:
        rem.title = data['title']
    if 'description' in data:
        rem.description = data['description']
    if 'reminder_time' in data:
        rem.reminder_time = data['reminder_time']

    db.session.commit()
    return jsonify({'message': 'Reminder updated', 'reminder': rem.to_dict()}), 200

@reminders_bp.route('/api/reminders/<int:reminder_id>/toggle', methods=['POST'])
@login_required()
def api_toggle_reminder(reminder_id):
    rem = Reminder.query.get_or_404(reminder_id)
    if rem.status == 'completed':
        rem.status = 'pending'
        rem.completed_at = None
    else:
        rem.status = 'completed'
        rem.completed_at = datetime.now()
    
    db.session.commit()
    return jsonify({'message': 'Status toggled', 'reminder': rem.to_dict()}), 200

@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@login_required()
def api_delete_reminder(reminder_id):
    rem = Reminder.query.get_or_404(reminder_id)
    db.session.delete(rem)
    db.session.commit()
    return jsonify({'message': 'Reminder deleted'}), 200
