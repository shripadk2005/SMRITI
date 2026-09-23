from datetime import datetime, timezone
from . import db

def utc_now():
    return datetime.now(timezone.utc)

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('caregivers.id', ondelete='CASCADE'), nullable=True, index=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'missed_medicine', 'inactivity', 'appointment', 'low_engagement'
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread')  # 'unread', 'read', 'acknowledged'
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    patient = db.relationship('Patient', back_populates='alerts')
    caregiver = db.relationship('Caregiver', back_populates='alerts')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.user.name if self.patient and self.patient.user else 'Unknown',
            'caregiver_id': self.caregiver_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

class SyncQueue(db.Model):
    __tablename__ = 'sync_queue'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # 'game_result', 'reminder_completion'
    data = db.Column(db.Text, nullable=False)  # JSON payload
    synced = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    patient = db.relationship('Patient', back_populates='sync_items')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'data_type': self.data_type,
            'data': self.data,
            'synced': self.synced,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
