from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='patient')  # 'patient', 'caregiver', 'admin'
    language = db.Column(db.String(20), nullable=False, default='en')
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    patient_profile = db.relationship('Patient', back_populates='user', uselist=False, cascade="all, delete-orphan")
    caregiver_profile = db.relationship('Caregiver', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
