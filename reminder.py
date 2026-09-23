from datetime import datetime, date, timezone
from . import db

def utc_now():
    return datetime.now(timezone.utc)

class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(30), nullable=False)  # 'medicine', 'hydration', 'activity'
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)  # e.g. dosage, instructions
    reminder_time = db.Column(db.String(20), nullable=False)  # e.g. "10:00 AM" or "14:30"
    frequency = db.Column(db.String(50), default='Daily')
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'missed'
    date_scheduled = db.Column(db.Date, default=date.today)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    patient = db.relationship('Patient', back_populates='reminders')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'reminder_time': self.reminder_time,
            'frequency': self.frequency,
            'status': self.status,
            'date_scheduled': self.date_scheduled.isoformat() if self.date_scheduled else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    doctor = db.Column(db.String(120), nullable=False)
    hospital = db.Column(db.String(150), nullable=False)
    appointment_date = db.Column(db.String(30), nullable=False)  # 'YYYY-MM-DD'
    appointment_time = db.Column(db.String(20), nullable=False)  # '10:30 AM'
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=utc_now)

    patient = db.relationship('Patient', back_populates='appointments')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor': self.doctor,
            'hospital': self.hospital,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
