from app import db
from datetime import datetime

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(64))
    thumbnail_url = db.Column(db.String(256))
    build_path = db.Column(db.String(512))     # path to Unity WebGL build
    download_path = db.Column(db.String(512))  # path to downloadable package
    plays = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship('Comment', backref='game', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def avg_rating(self):
        ratings = [c.rating for c in self.comments if c.rating is not None]
        return round(sum(ratings) / len(ratings), 1) if ratings else None

    @property
    def comment_count(self):
        return self.comments.count()
