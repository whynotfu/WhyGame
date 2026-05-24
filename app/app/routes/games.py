from flask import Blueprint, render_template, redirect, url_for, request, session, flash, abort
from app import db
from app.models.game import Game
from app.models.comment import Comment
import re

bp = Blueprint('games', __name__, url_prefix='/games')

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

@bp.route('/')
def catalog():
    genre = request.args.get('genre')
    sort = request.args.get('sort', 'plays')
    q = request.args.get('q', '').strip()

    query = Game.query.filter_by(is_published=True)
    if genre:
        query = query.filter_by(genre=genre)
    if q:
        query = query.filter(Game.title.ilike(f'%{q}%'))
    if sort == 'new':
        query = query.order_by(Game.created_at.desc())
    else:
        query = query.order_by(Game.plays.desc())

    games = query.all()
    return render_template('games/catalog.html', games=games, genre=genre, sort=sort, q=q)

@bp.route('/<slug>')
def detail(slug):
    game = Game.query.filter_by(slug=slug, is_published=True).first_or_404()
    game.plays += 1
    db.session.commit()
    comments = Comment.query.filter_by(game_id=game.id).order_by(Comment.created_at.desc()).all()
    return render_template('games/detail.html', game=game, comments=comments)

@bp.route('/<slug>/comment', methods=['POST'])
def comment(slug):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    game = Game.query.filter_by(slug=slug).first_or_404()
    body = request.form.get('body', '').strip()
    rating = request.form.get('rating')
    if body:
        c = Comment(body=body, author_id=session['user_id'], game_id=game.id,
                    rating=int(rating) if rating else None)
        db.session.add(c)
        db.session.commit()
    return redirect(url_for('games.detail', slug=slug))
