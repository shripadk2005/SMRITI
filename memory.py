"""
SMRITI – Personal Memory Vault Model
Stores patient-specific family members, photos, addresses, favorite shows,
and life trivia used to personalize cognitive recall games.
"""

from datetime import datetime
from . import db

class PersonalMemory(db.Model):
    __tablename__ = 'personal_memories'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(30), nullable=False) # 'family', 'address', 'favorite_show', 'custom'
    title = db.Column(db.String(120), nullable=False)   # e.g., 'Sunita Sharma', 'Ramayan', 'Zoo Road Home'
    relationship_or_type = db.Column(db.String(80), nullable=False) # e.g., 'Daughter', 'Favorite Serial', 'Home'
    image_url = db.Column(db.String(255), nullable=True) # Avatar or photo URL
    details = db.Column(db.Text, nullable=True)         # Clue or description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'category': self.category,
            'title': self.title,
            'relationship_or_type': self.relationship_or_type,
            'image_url': self.image_url,
            'details': self.details,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

    def __repr__(self):
        return f"<PersonalMemory {self.id}: {self.title} ({self.category})>"
