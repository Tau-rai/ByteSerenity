"""This modules has the authorization routes and methods"""
import functools
import re
import os
from dbase import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, current_app as app
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import mail, login_manager
from models import User
from werkzeug.security import check_password_hash, generate_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')
s = URLSafeTimedSerializer('Thisisasecret!')


@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    """Registers a new user"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        # Email validation regex
        email_regex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not re.match(email_regex, email):
            error = 'Invalid email address.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password: 
            error = 'Passwords do not match.'

        if error is None:
            # Check if the username or email already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                error = f"User {username} or email {email} is already registered."
            else:
                # Create a new user object and add it to the database
                new_user = User(username=username, email=email, password=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('signup.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Logs in the user."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        error = None


        if not email or not password:
            error = 'Email and password are required.'
        else:
            try:
                user = User.query.filter_by(email=email).first()
            except Exception as e:
                error = 'Database error occurred.'

            if user is None:
                error = 'Incorrect email or password.'
            elif not check_password_hash(user.password, password):
                error = 'Incorrect email or password.'

        if error is None:
            login_user(user)
            return redirect(url_for('blog.index'))
        else:
            flash(error)

    return render_template('login.html')

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')

    email = request.form.get('email')

    if not email:
        return jsonify({'message': 'Email is required.'}), 400

    # Verify if the email exists in your database
    user = db.session.query(User).filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'Email does not exist.'}), 400

    # If it does, proceed to generate a token and send the email
    token = s.dumps(email, salt='email-confirm-salt')

    msg = Message('Password Reset Request', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    link = url_for('auth.reset_password', token=token, _external=True)
    msg.body = 'Your link to reset your password is {}'.format(link)
    mail.send(msg)

    return jsonify({'message': 'Please check your email for a password reset link.'}), 200

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({'message': 'The password reset link is expired.'}), 400

    user = db.session.query(User).filter_by(email=email).first()

    if user is None:
        return jsonify({'message': 'Email does not exist.'}), 400

    if request.method == 'GET':
        return render_template('reset_password.html', email=email, token=token)

    if request.method == 'POST':
        new_password = request.form.get('password')
        if new_password is None:
            return jsonify({'message': 'Password is required.'}), 400

        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        db.session.commit()

        # Notify user
        return jsonify({'message': 'Password has been reset successfully, please login.'}), 200


@login_manager.user_loader
def load_user(user_id):
    """Loads the user object from the database"""
    return User.query.get(int(user_id))

@bp.route('/logout')
@login_required
def logout():
    """logs the user out"""
    logout_user()
    return redirect(url_for('blog.index'))
