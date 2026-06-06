from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('main.index', modal='login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('user_id'):
                return redirect(url_for('main.index', modal='login'))
            if session.get('role') not in roles:
                return redirect(url_for('main.index')), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
