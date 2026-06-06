import os
import re
import zipfile
import shutil
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, abort, make_response)
from werkzeug.utils import secure_filename
from app import db
from app.models.game import Game
from app.models.comment import Comment
from app.models.user import User
from app.utils import login_required, role_required


def _notify_moderators_new_game(game):
    from app.models.notification import Notification
    mods = User.query.filter(User.role.in_(['admin', 'moderator'])).all()
    author_name = game.author.username if game.author else 'unknown'
    for mod in mods:
        db.session.add(Notification(
            user_id=mod.id,
            type='new_game',
            message=f'New game "{game.title}" by {author_name} was published. Review for content.',
            link=f'/games/{game.slug}',
        ))

bp = Blueprint('games', __name__, url_prefix='/games')

GENRES = ['Action','Adventure','Puzzle','RPG','Platformer',
          'Shooter','Strategy','Indie','Horror','Arcade']
ALLOWED_EXTENSIONS = {'zip', 'rar', '7z'}
ALLOWED_IMG = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
STORAGE_BASE = '/app/storage/games'
THUMBS_BASE  = '/app/storage/thumbnails'


def slugify(text):
    # try latin-only slug first
    latin = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    if latin:
        return latin
    # fallback: keep unicode word chars (cyrillic, etc.)
    return re.sub(r'[^\w]+', '-', text.lower(), flags=re.UNICODE).strip('-') or 'game'

def can_edit_game(game):
    return session.get('user_id') == game.author_id or session.get('role') == 'admin'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_game_file(file, game_id):
    folder = os.path.join(STORAGE_BASE, str(game_id))
    os.makedirs(folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file.save(os.path.join(folder, filename))
    return f'games/{game_id}/{filename}'

def extract_game_zip(file, game_id):
    """Extract ZIP to storage/games/<id>/, return URL to index.html."""
    folder = os.path.join(STORAGE_BASE, str(game_id))
    # wipe old build if re-uploading
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

    with zipfile.ZipFile(file, 'r') as zf:
        for member in zf.namelist():
            # prevent path traversal
            dest = os.path.realpath(os.path.join(folder, member))
            if not dest.startswith(os.path.realpath(folder)):
                continue
            zf.extract(member, folder)

    # find index.html (depth-first, prefer shallowest)
    best = None
    best_depth = 999
    for root, dirs, files in os.walk(folder):
        if 'index.html' in files:
            depth = root[len(folder):].count(os.sep)
            if depth < best_depth:
                best_depth = depth
                best = os.path.join(root, 'index.html')

    if best is None:
        return None
    rel = os.path.relpath(best, folder).replace(os.sep, '/')
    return f'/storage/games/{game_id}/{rel}'

def save_thumbnail(file, game_id):
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_IMG:
        return None
    folder = os.path.join(THUMBS_BASE, str(game_id))
    os.makedirs(folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file.save(os.path.join(folder, filename))
    return f'/storage/thumbnails/{game_id}/{filename}'

def parse_genres(form):
    return ','.join(form.getlist('genre')) or ''

def parse_socials(form):
    return {
        'social_telegram':     form.get('social_telegram', '').strip() or None,
        'social_youtube':      form.get('social_youtube', '').strip() or None,
        'social_instagram':    form.get('social_instagram', '').strip() or None,
        'social_twitter':      form.get('social_twitter', '').strip() or None,
        'social_custom_url':   form.get('social_custom_url', '').strip() or None,
        'social_custom_label': form.get('social_custom_label', '').strip() or None,
    }


# ── READ: catalog ──────────────────────────────────────────────────────────────
@bp.route('/')
def catalog():
    genre = request.args.get('genre')
    sort  = request.args.get('sort', 'plays')
    q     = request.args.get('q', '').strip()

    query = Game.query.filter_by(is_published=True)
    if genre:
        query = query.filter(Game.genre.contains(genre))
    if q:
        query = query.filter(Game.title.ilike(f'%{q}%'))
    query = query.order_by(Game.created_at.desc() if sort == 'new' else Game.plays.desc())

    games = query.all()
    return render_template('games/catalog.html', games=games, genre=genre, sort=sort, q=q)


# ── READ: detail ───────────────────────────────────────────────────────────────
@bp.route('/<slug>')
def detail(slug):
    uid  = session.get('user_id')
    role = session.get('role')
    if uid and role in ('developer', 'admin'):
        game = Game.query.filter_by(slug=slug).first_or_404()
        if not game.is_published and game.author_id != uid and role != 'admin':
            abort(404)
    else:
        game = Game.query.filter_by(slug=slug, is_published=True).first_or_404()

    game.plays += 1
    db.session.commit()
    comments = Comment.query.filter_by(game_id=game.id).order_by(Comment.created_at.desc()).all()
    genres = [g.strip() for g in (game.genre or '').split(',') if g.strip()]
    return render_template('games/detail.html', game=game, comments=comments, genres=genres)



# ── CREATE ─────────────────────────────────────────────────────────────────────
@bp.route('/publish', methods=['GET', 'POST'])
@role_required('developer', 'admin')
def publish():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required', 'error')
            return redirect(url_for('games.publish'))

        slug = slugify(title)
        if Game.query.filter_by(slug=slug).first():
            slug = f"{slug}-{session['user_id']}"

        thumb_url = request.form.get('thumbnail_url', '').strip() or None
        game = Game(
            title=title,
            slug=slug,
            description=request.form.get('description', '').strip(),
            genre=parse_genres(request.form),
            bg_color=request.form.get('bg_color', '#0d1a45') or '#0d1a45',
            thumbnail_url=thumb_url,
            iframe_url=request.form.get('iframe_url', '').strip() or None,
            game_url=request.form.get('game_url', '').strip() or None,
            is_published='is_published' in request.form,
            author_id=session['user_id'],
            **parse_socials(request.form),
        )
        db.session.add(game)
        db.session.flush()

        tf = request.files.get('thumbnail_file')
        if tf and tf.filename:
            saved = save_thumbnail(tf, game.id)
            if saved:
                game.thumbnail_url = saved

        zf = request.files.get('game_zip')
        if zf and zf.filename and allowed_file(zf.filename):
            url = extract_game_zip(zf, game.id)
            if url:
                game.iframe_url = url
            else:
                flash('ZIP uploaded but no index.html found inside', 'error')

        if game.is_published:
            _notify_moderators_new_game(game)
        db.session.commit()
        flash('Game published!' if game.is_published else 'Game saved as draft', 'success')
        return redirect(url_for('games.detail', slug=game.slug))

    return render_template('games/publish.html', genres=GENRES, game=None)


# ── UPDATE ─────────────────────────────────────────────────────────────────────
@bp.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not can_edit_game(game):
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required', 'error')
            return redirect(url_for('games.edit', slug=slug))

        new_slug = slugify(title)
        if new_slug != game.slug and Game.query.filter_by(slug=new_slug).first():
            new_slug = f"{new_slug}-{game.id}"

        game.title        = title
        game.slug         = new_slug
        game.description  = request.form.get('description', '').strip()
        game.genre        = parse_genres(request.form)
        game.bg_color     = request.form.get('bg_color', '#0d1a45') or '#0d1a45'
        game.iframe_url   = request.form.get('iframe_url', '').strip() or None
        game.game_url     = request.form.get('game_url', '').strip() or None
        was_published = game.is_published
        game.is_published = 'is_published' in request.form
        newly_published = game.is_published and not was_published
        for k, v in parse_socials(request.form).items():
            setattr(game, k, v)

        tf = request.files.get('thumbnail_file')
        if tf and tf.filename:
            saved = save_thumbnail(tf, game.id)
            if saved:
                game.thumbnail_url = saved
        else:
            game.thumbnail_url = request.form.get('thumbnail_url', '').strip() or game.thumbnail_url

        zf = request.files.get('game_zip')
        if zf and zf.filename and allowed_file(zf.filename):
            url = extract_game_zip(zf, game.id)
            if url:
                game.iframe_url = url
                flash('Game build extracted and ready to play!', 'success')
            else:
                flash('ZIP uploaded but no index.html found inside', 'error')

        if newly_published:
            _notify_moderators_new_game(game)
        db.session.commit()
        flash('Game updated', 'success')
        return redirect(url_for('games.detail', slug=game.slug))

    game_genres = [g.strip() for g in (game.genre or '').split(',') if g.strip()]
    return render_template('games/publish.html', genres=GENRES, game=game, game_genres=game_genres)


# ── UNPUBLISH (moderator / admin) ─────────────────────────────────────────────
@bp.route('/<slug>/unpublish', methods=['POST'])
@login_required
def unpublish(slug):
    if session.get('role') not in ('moderator', 'admin'):
        abort(403)
    game = Game.query.filter_by(slug=slug).first_or_404()
    game.is_published = False
    from app.models.notification import Notification
    db.session.add(Notification(
        user_id=game.author_id,
        type='game_removed',
        message=f'Your game "{game.title}" was removed from the catalog by a moderator for content review.',
        link=f'/games/{game.slug}',
    ))
    db.session.commit()
    flash('Game unpublished and author notified', 'success')
    return redirect(url_for('games.detail', slug=slug))


# ── DELETE game ────────────────────────────────────────────────────────────────
@bp.route('/<slug>/delete', methods=['POST'])
@login_required
def delete(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not can_edit_game(game):
        abort(403)
    db.session.delete(game)
    db.session.commit()
    flash('Game deleted', 'success')
    return redirect(url_for('games.catalog'))


# ── CREATE comment ─────────────────────────────────────────────────────────────
@bp.route('/<slug>/comment', methods=['POST'])
@login_required
def comment(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    body = request.form.get('body', '').strip()
    rating = request.form.get('rating')
    if body:
        c = Comment(body=body, author_id=session['user_id'], game_id=game.id,
                    rating=int(rating) if rating else None)
        db.session.add(c)
        db.session.commit()
    return redirect(url_for('games.detail', slug=slug))


# ── UPDATE comment ─────────────────────────────────────────────────────────────
@bp.route('/<slug>/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(slug, comment_id):
    c = Comment.query.get_or_404(comment_id)
    if c.author_id != session['user_id']:
        abort(403)
    body = request.form.get('body', '').strip()
    if body:
        c.body = body
        db.session.commit()
        flash('Comment updated', 'success')
    return redirect(url_for('games.detail', slug=slug))


# ── DELETE comment ─────────────────────────────────────────────────────────────
@bp.route('/<slug>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(slug, comment_id):
    c = Comment.query.get_or_404(comment_id)
    role = session.get('role')
    if c.author_id != session['user_id'] and role not in ('moderator', 'admin'):
        abort(403)
    db.session.delete(c)
    db.session.commit()
    flash('Comment deleted', 'success')
    return redirect(url_for('games.detail', slug=slug))
