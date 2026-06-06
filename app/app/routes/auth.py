from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form['email']
        user = User.query.filter(
            (User.email == login_val) | (User.username == login_val)
        ).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['avatar_url'] = user.avatar_url
            return redirect(url_for('users.profile'))
        flash('Invalid credentials', 'error')
        return redirect(url_for('main.index', modal='login'))
    return redirect(url_for('main.index', modal='login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already taken', 'error')
            return redirect(url_for('main.index', modal='register'))
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered', 'error')
            return redirect(url_for('main.index', modal='register'))
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            role='player'
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['avatar_url'] = user.avatar_url
        return redirect(url_for('users.profile'))
    return redirect(url_for('main.index', modal='register'))

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
