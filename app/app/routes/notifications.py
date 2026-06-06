from flask import Blueprint, render_template, redirect, url_for, session, flash, abort
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.utils import login_required, role_required

bp = Blueprint('notifications', __name__)


def send_notifications(user_ids, type, message, link=None, extra_user_id=None):
    for uid in user_ids:
        db.session.add(Notification(
            user_id=uid, type=type, message=message,
            link=link, extra_user_id=extra_user_id,
        ))


@bp.route('/notifications')
@login_required
def index():
    notifs = Notification.query.filter_by(user_id=session['user_id'])\
        .order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(user_id=session['user_id'], is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)


@bp.route('/notifications/<int:nid>/delete', methods=['POST'])
@login_required
def delete(nid):
    n = Notification.query.get_or_404(nid)
    if n.user_id != session['user_id']:
        abort(403)
    db.session.delete(n)
    db.session.commit()
    return redirect(url_for('notifications.index'))


@bp.route('/admin/approve-moderator/<int:user_id>', methods=['POST'])
@role_required('admin')
def approve_moderator(user_id):
    user = User.query.get_or_404(user_id)
    user.role = 'moderator'
    send_notifications(
        [user.id], 'role_update',
        'Your Moderator application was approved! You now have moderation powers.'
    )
    db.session.commit()
    flash(f'{user.username} is now a Moderator', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/admin/reject-moderator/<int:user_id>', methods=['POST'])
@role_required('admin')
def reject_moderator(user_id):
    user = User.query.get_or_404(user_id)
    send_notifications(
        [user.id], 'role_update',
        'Your Moderator application was reviewed and not approved at this time.'
    )
    db.session.commit()
    flash(f'Application for {user.username} rejected', 'info')
    return redirect(url_for('notifications.index'))
