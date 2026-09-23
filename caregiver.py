from datetime import datetime, timezone
from . import db

def utc_now():
    return datetime.now(timezone.utc)

class Caregiver(db.Model):
    __tablename__ = 'caregivers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    relationship_to_patient = db.Column(db.String(50), default='Family/Nurse')
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    user = db.relationship('User', back_populates='caregiver_profile')
    patients = db.relationship('Patient', back_populates='caregiver', foreign_keys='Patient.caregiver_id')
    alerts = db.relationship('Alert', back_populates='caregiver', cascade="all, delete-orphan", lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else 'Unknown',
            'phone': self.user.phone if self.user else None,
            'email': self.user.email if self.user else None,
            'assigned_patients_count': len(self.patients) if self.patients else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
