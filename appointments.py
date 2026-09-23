from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from models import db
from models.user import User
from models.patient import Patient
from models.reminder import Appointment
from . import login_required

appointments_bp = Blueprint('appointments', __name__)

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

@appointments_bp.route('/appointments')
@login_required()
def appointments_page():
    pid = get_current_patient_id()
    patient = Patient.query.get(pid)
    appointments = Appointment.query.filter_by(patient_id=pid).order_by(Appointment.appointment_date.asc()).all()
    return render_template(
        'appointments.html',
        patient=patient,
        appointments=appointments
    )

@appointments_bp.route('/api/appointments', methods=['GET'])
@login_required()
def api_get_appointments():
    pid = request.args.get('patient_id', type=int) or get_current_patient_id()
    appointments = Appointment.query.filter_by(patient_id=pid).order_by(Appointment.appointment_date.asc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200

@appointments_bp.route('/api/appointments', methods=['POST'])
@login_required()
def api_create_appointment():
    data = request.get_json() or {}
    pid = data.get('patient_id') or get_current_patient_id()
    doctor = data.get('doctor', '').strip()
    hospital = data.get('hospital', '').strip()
    appointment_date = data.get('appointment_date', '').strip()
    appointment_time = data.get('appointment_time', '').strip()
    notes = data.get('notes', '').strip()

    if not doctor or not hospital or not appointment_date or not appointment_time:
        return jsonify({'error': 'Doctor, hospital, date, and time are required'}), 400

    try:
        app = Appointment(
            patient_id=pid,
            doctor=doctor,
            hospital=hospital,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            status='scheduled'
        )
        db.session.add(app)
        db.session.commit()
        return jsonify({'message': 'Appointment scheduled', 'appointment': app.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
