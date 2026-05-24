from app import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1–5, optional
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
