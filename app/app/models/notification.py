from app import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(32))       # mod_request | new_game | role_update | game_removed
    message = db.Column(db.String(512))
    link = db.Column(db.String(256))
    extra_user_id = db.Column(db.Integer)  # for mod_request: the applicant's id
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
