from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('main.index'))
        flash('Invalid credentials', 'error')
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
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
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
