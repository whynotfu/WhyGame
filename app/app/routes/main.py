from flask import Blueprint, render_template
from app.models.game import Game

bp = Blueprint('main', __name__)

GENRES = ['Action', 'Adventure', 'Puzzle', 'RPG', 'Platformer', 'Shooter', 'Strategy', 'Indie', 'Horror', 'Arcade']

PLACEHOLDER_GAMES = [
    {'title': 'Neon Drift',      'genre': 'Racing',    'plays': 14820, 'author': 'speeddev',   'gradient': 'linear-gradient(135deg,#1a1a2e,#e94560)'},
    {'title': 'Pixel Dungeon X', 'genre': 'RPG',       'plays': 9310,  'author': 'rpgforge',   'gradient': 'linear-gradient(135deg,#0f3460,#533483)'},
    {'title': 'Sky Jumper',      'genre': 'Platformer', 'plays': 7640,  'author': 'jumpstudio', 'gradient': 'linear-gradient(135deg,#16213e,#0f9b58)'},
    {'title': 'Dark Puzzle',     'genre': 'Puzzle',    'plays': 5200,  'author': 'mindgames',  'gradient': 'linear-gradient(135deg,#2c003e,#8b00ff)'},
    {'title': 'Void Shooter',    'genre': 'Shooter',   'plays': 21000, 'author': 'voidlabs',   'gradient': 'linear-gradient(135deg,#000428,#004e92)'},
    {'title': 'Forest Run',      'genre': 'Indie',     'plays': 3800,  'author': 'greenbit',   'gradient': 'linear-gradient(135deg,#134e5e,#71b280)'},
    {'title': 'Cyber Strike',    'genre': 'Action',    'plays': 17500, 'author': 'cyberx',     'gradient': 'linear-gradient(135deg,#0b0c10,#45a29e)'},
    {'title': 'Lost Temple',     'genre': 'Adventure', 'plays': 6100,  'author': 'adventures', 'gradient': 'linear-gradient(135deg,#4a3000,#c9a227)'},
    {'title': 'Ice Tower',       'genre': 'Arcade',    'plays': 11300, 'author': 'frostdev',   'gradient': 'linear-gradient(135deg,#2980b9,#6dd5fa)'},
    {'title': 'Shadow Realm',    'genre': 'Horror',    'plays': 8900,  'author': 'darkarts',   'gradient': 'linear-gradient(135deg,#200122,#6f0000)'},
    {'title': 'Star Command',    'genre': 'Strategy',  'plays': 4400,  'author': 'galactic',   'gradient': 'linear-gradient(135deg,#000000,#434343)'},
    {'title': 'Bloom Garden',    'genre': 'Indie',     'plays': 2700,  'author': 'petalpix',   'gradient': 'linear-gradient(135deg,#a8e063,#56ab2f)'},
]

@bp.route('/')
def index():
    featured  = Game.query.filter_by(is_published=True).order_by(Game.plays.desc()).first()
    new_games = Game.query.filter_by(is_published=True).order_by(Game.created_at.desc()).limit(12).all()
    popular   = Game.query.filter_by(is_published=True).order_by(Game.plays.desc()).limit(12).all()
    return render_template('index.html',
                           featured=featured,
                           new_games=new_games,
                           popular=popular,
                           placeholders=PLACEHOLDER_GAMES,
                           genres=GENRES,
                           active_genre=None)

@bp.route('/genre/<genre>')
def genre(genre):
    games = Game.query.filter_by(is_published=True, genre=genre).order_by(Game.plays.desc()).all()
    return render_template('index.html',
                           featured=None,
                           new_games=games,
                           popular=[],
                           placeholders=PLACEHOLDER_GAMES,
                           genres=GENRES,
                           active_genre=genre)
