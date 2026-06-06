import os
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.utils import login_required

bp = Blueprint('users', __name__)

AVATARS_BASE = '/app/storage/avatars'
ALLOWED_IMG  = {'jpg', 'jpeg', 'png', 'webp', 'gif'}


def save_avatar(file, user_id):
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_IMG:
        return None
    folder = os.path.join(AVATARS_BASE, str(user_id))
    os.makedirs(folder, exist_ok=True)
    filename = f'avatar.{ext}'
    file.save(os.path.join(folder, filename))
    return f'/storage/avatars/{user_id}/{filename}'


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'avatar':
            f = request.files.get('avatar_file')
            if f and f.filename:
                url = save_avatar(f, user.id)
                if url:
                    user.avatar_url = url
                    db.session.commit()
                    session['avatar_url'] = url
                    flash('Avatar updated', 'success')
                else:
                    flash('Unsupported file type', 'error')
            return redirect(url_for('users.profile'))

        if action == 'info':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            bio = request.form.get('bio', '').strip()

            if username and username != user.username:
                if User.query.filter_by(username=username).first():
                    flash('Username already taken', 'error')
                    return redirect(url_for('users.profile'))
                user.username = username

            if email and email != user.email:
                if User.query.filter_by(email=email).first():
                    flash('Email already in use', 'error')
                    return redirect(url_for('users.profile'))
                user.email = email

            user.bio = bio
            db.session.commit()

            session['username'] = user.username
            flash('Profile updated', 'success')

        elif action == 'bio':
            user.bio = request.form.get('bio', '').strip()
            db.session.commit()
            flash('Bio updated', 'success')

        elif action == 'apply':
            from app.models.notification import Notification
            from app.routes.notifications import send_notifications
            role_req = request.form.get('role_request', '')

            if role_req == 'developer' and user.role == 'player':
                user.role = 'developer'
                session['role'] = 'developer'
                db.session.commit()
                flash('You are now a Developer! You can publish games.', 'success')

            elif role_req == 'moderator' and user.role in ('player', 'developer'):
                recipients = User.query.filter(
                    User.role.in_(['admin', 'moderator']),
                    User.id != user.id
                ).all()
                send_notifications(
                    [r.id for r in recipients],
                    type='mod_request',
                    message=f'{user.username} is requesting the Moderator role.',
                    link=f'/notifications',
                    extra_user_id=user.id,
                )
                db.session.commit()
                flash('Moderator application sent! Waiting for admin approval.', 'success')

            else:
                flash('You are not eligible for this role upgrade.', 'error')

        elif action == 'password':
            current = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            if not user.check_password(current):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('users.profile'))
            if len(new_pw) < 6:
                flash('New password must be at least 6 characters', 'error')
                return redirect(url_for('users.profile'))
            user.set_password(new_pw)
            db.session.commit()
            flash('Password changed', 'success')

        return redirect(url_for('users.profile'))

    from app.models.play_history import PlayHistory
    recently_played = (
        PlayHistory.query
        .filter_by(user_id=user.id)
        .order_by(PlayHistory.played_at.desc())
        .limit(6)
        .all()
    )
    stats = {
        'comments': user.comments.count(),
        'games_published': user.games.filter_by(is_published=True).count() if user.is_developer else 0,
    }
    return render_template('profile.html', user=user, stats=stats,
                           recently_played=recently_played)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'username':
            username = request.form.get('username', '').strip()
            if not username:
                flash('Username cannot be empty', 'error')
            elif username == user.username:
                flash('That is already your username', 'info')
            elif User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
            else:
                user.username = username
                session['username'] = username
                db.session.commit()
                flash('Username updated', 'success')

        elif action == 'email':
            email = request.form.get('email', '').strip()
            if not email:
                flash('Email cannot be empty', 'error')
            elif email == user.email:
                flash('That is already your email', 'info')
            elif User.query.filter_by(email=email).first():
                flash('Email already in use', 'error')
            else:
                user.email = email
                db.session.commit()
                flash('Email updated', 'success')

        elif action == 'password':
            current = request.form.get('current_password', '')
            new_pw  = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            if not user.check_password(current):
                flash('Current password is incorrect', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters', 'error')
            elif new_pw != confirm:
                flash('Passwords do not match', 'error')
            else:
                user.set_password(new_pw)
                db.session.commit()
                flash('Password changed', 'success')

        elif action == 'privacy':
            user.is_public = 'is_public' in request.form
            db.session.commit()
            flash('Privacy setting saved', 'success')

        elif action == 'delete':
            confirm_text = request.form.get('confirm_text', '').strip()
            if confirm_text != user.username:
                flash('Type your username exactly to confirm deletion', 'error')
            else:
                db.session.delete(user)
                db.session.commit()
                session.clear()
                flash('Account deleted', 'success')
                return redirect(url_for('main.index'))

        return redirect(url_for('users.settings'))

    return render_template('settings.html', user=user)


@bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Account deleted', 'success')
    return redirect(url_for('main.index'))
