from datetime import datetime, timezone
from . import db

def utc_now():
    return datetime.now(timezone.utc)

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'memory-cards', 'object-recall'
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'Memory', 'Attention', 'Pattern', 'Daily Routine', etc.
    difficulty = db.Column(db.String(20), nullable=False, default='EASY')  # 'EASY', 'MEDIUM', 'HARD'
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='fa-puzzle-piece')

    results = db.relationship('GameResult', back_populates='game', cascade="all, delete-orphan", lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'category': self.category,
            'difficulty': self.difficulty,
            'description': self.description,
            'icon': self.icon
        }

class GameResult(db.Model):
    __tablename__ = 'game_results'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    accuracy = db.Column(db.Float, nullable=False, default=100.0)  # percentage 0-100
    completion_time = db.Column(db.Float, nullable=False, default=0.0)  # in seconds
    attempts = db.Column(db.Integer, default=1)
    difficulty = db.Column(db.String(20), nullable=False, default='EASY')
    played_at = db.Column(db.DateTime, default=utc_now, index=True)

    patient = db.relationship('Patient', back_populates='game_results')
    game = db.relationship('Game', back_populates='results')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'game_id': self.game_id,
            'game_name': self.game.name if self.game else 'Cognitive Game',
            'game_slug': self.game.slug if self.game else '',
            'score': self.score,
            'accuracy': round(self.accuracy, 1),
            'completion_time': round(self.completion_time, 1),
            'attempts': self.attempts,
            'difficulty': self.difficulty,
            'played_at': self.played_at.isoformat() if self.played_at else None
        }
