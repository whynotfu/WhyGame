from app import db
from datetime import datetime

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.Text)          # comma-separated, e.g. "Action,RPG"
    bg_color = db.Column(db.String(7), default='#0d1a45')
    thumbnail_url = db.Column(db.String(256))
    iframe_url = db.Column(db.String(512))
    game_url = db.Column(db.String(512))         # external link: itch.io, Steam, etc.
    build_path = db.Column(db.String(512))
    download_path = db.Column(db.String(512))
    social_telegram = db.Column(db.String(256))
    social_youtube = db.Column(db.String(256))
    social_instagram = db.Column(db.String(256))
    social_twitter = db.Column(db.String(256))
    social_custom_url = db.Column(db.String(256))
    social_custom_label = db.Column(db.String(64))
    plays = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship('Comment', backref='game', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def bg_is_dark(self):
        c = self.bg_color or '#0B1538'
        if len(c) != 7:
            return True
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        return (0.2126*r + 0.7152*g + 0.0722*b)/255 < 0.35

    @property
    def bg_thumb(self):
        c = self.bg_color or '#0B1538'
        if len(c) != 7:
            return '#060f2a'
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        return f'#{int(r*.6):02x}{int(g*.6):02x}{int(b*.6):02x}'

    @property
    def first_genre(self):
        return (self.genre or '').split(',')[0].strip()

    @property
    def avg_rating(self):
        from sqlalchemy import func
        from app.models.comment import Comment as C
        result = db.session.query(func.avg(C.rating)).filter(
            C.game_id == self.id, C.rating.isnot(None)
        ).scalar()
        return round(float(result), 1) if result else None

    @property
    def comment_count(self):
        return self.comments.count()
