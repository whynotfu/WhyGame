from app import db
from datetime import datetime

class PlayHistory(db.Model):
    __tablename__ = 'play_history'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id   = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)

    game = db.relationship('Game')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_id', name='uq_play_history'),
    )
