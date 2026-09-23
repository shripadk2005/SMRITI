from datetime import datetime, timezone
from . import db

def utc_now():
    return datetime.now(timezone.utc)

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('caregivers.id', ondelete='SET NULL'), nullable=True)
    emergency_contact = db.Column(db.String(120), nullable=True)
    region = db.Column(db.String(100), nullable=False, default='Assam')  # NER state
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    user = db.relationship('User', back_populates='patient_profile')
    caregiver = db.relationship('Caregiver', back_populates='patients', foreign_keys=[caregiver_id])
    game_results = db.relationship('GameResult', back_populates='patient', cascade="all, delete-orphan", lazy='dynamic')
    reminders = db.relationship('Reminder', back_populates='patient', cascade="all, delete-orphan", lazy='dynamic')
    appointments = db.relationship('Appointment', back_populates='patient', cascade="all, delete-orphan", lazy='dynamic')
    alerts = db.relationship('Alert', back_populates='patient', cascade="all, delete-orphan", lazy='dynamic')
    sync_items = db.relationship('SyncQueue', back_populates='patient', cascade="all, delete-orphan", lazy='dynamic')
    personal_memories = db.relationship('PersonalMemory', backref='patient', cascade="all, delete-orphan", lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else 'Unknown',
            'age': self.user.age if self.user else None,
            'gender': self.user.gender if self.user else None,
            'phone': self.user.phone if self.user else None,
            'email': self.user.email if self.user else None,
            'language': self.user.language if self.user else 'en',
            'caregiver_id': self.caregiver_id,
            'caregiver_name': self.caregiver.user.name if self.caregiver and self.caregiver.user else None,
            'emergency_contact': self.emergency_contact,
            'region': self.region,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
