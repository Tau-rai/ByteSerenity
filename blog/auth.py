"""This modules has the authorization routes and methods"""
import functools
import re
import os
from .dbase import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
from flask_mail import Message
from . import mail
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')
s = URLSafeTimedSerializer('Thisisasecret!')


@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    """
    Registers a new user.

    If the request method is POST, it handles the form submission.
    It checks if the username, email, and password are provided.
    It also validates the email format.
    If the passwords do not match, it sets an error message.
    If no error occurs, it checks if the username or email already exist in the database.
    If not, it creates a new user object and adds it to the database.
    Finally, it redirects to the login page.

    If the request method is GET, it renders the signup.html template.
    """
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        # Email validation regex
        email_regex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        # Check if required fields are provided
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
            # Check if the username or email already exist
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

    # Render the signup.html template
    return render_template('signup.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Logs in the user.

    If the request method is POST, it handles the form submission.
    It checks if the email and password are provided.
    If the user exists and the password is correct, it clears the session,
    sets the user id in the session, and redirects to the blog index page.
    If the user does not exist or the password is incorrect, it sets an error message.

    If the request method is GET, it renders the login.html template.
    """
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
                # Log the error `e` here

            if user is None:
                error = 'Incorrect email or password.'
            elif not check_password_hash(user.password, password):
                error = 'Incorrect email or password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('blog.index'))
        else:
            flash(error)

    return render_template('login.html')


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handles the forgot password form submission.

    If the request method is GET, it renders the forgot_password.html template.
    If the request method is POST, it validates the email and sends a password reset link.

    Returns:
        If the request method is GET, it renders the forgot_password.html template.
        If the request method is POST and the email is not provided, it returns a JSON response with an error message.
        If the request method is POST and the email does not exist in the database, it returns a JSON response with an error message.
        If the request method is POST, it generates a token and sends a password reset link via email.
        It returns a JSON response with a success message.
    """
    if request.method == 'GET':
        return render_template('forgot_password.html')

    # Get email from form data
    email = request.form.get('email')

    # Check if email is provided
    if not email:
        return jsonify({'message': 'Email is required.'}), 400

    # Verify if the email exists in the database
    user = db.session.query(User).filter_by(email=email).first()

    # Check if the email exists in the database
    if not user:
        return jsonify({'message': 'Email does not exist.'}), 400

    # If the email exists, generate a token and send a password reset link
    token = s.dumps(email, salt='email-confirm-salt')

    # Send password reset link via email
    msg = Message('Password Reset Request', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
    link = url_for('auth.reset_password', token=token, _external=True)
    msg.body = 'Your link to reset your password is {}'.format(link)
    mail.send(msg)

    # Return a success message
    return jsonify({'message': 'Please check your email for a password reset link.'}), 200

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Handles the password reset form submission.

    If the request method is GET, it renders the reset_password.html template.
    If the request method is POST, it validates the password and updates the user's password in the database.

    Returns:
        If the request method is GET, it renders the reset_password.html template.
        If the request method is POST and the password is not provided, it returns a JSON response with an error message.
        If the request method is POST, it updates the user's password and returns a JSON response with a success message.
    """
    try:
        # Load the email from the token
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)
    except SignatureExpired:
        # Return an error message if the token has expired
        return jsonify({'message': 'The password reset link is expired.'}), 400

    # Query the user by email
    user = db.session.query(User).filter_by(email=email).first()

    # Return an error message if the user does not exist
    if user is None:
        return jsonify({'message': 'Email does not exist.'}), 400

    if request.method == 'GET':
        # Render the reset_password.html template
        return render_template('reset_password.html', email=email, token=token)
    
    if request.method == 'POST':
        # Get the new password from the form data
        new_password = request.form.get('password')

        # Return an error message if the password is not provided
        if new_password is None:
            return jsonify({'message': 'Password is required.'}), 400

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update the user's password
        user.password = hashed_password
        db.session.commit()

        # Return a success message
        return jsonify({'message': 'Password has been reset successfully, please login.'}), 200

@bp.before_app_request
def load_logged_in_user():
    """
    Load the user from the database before each request.

    This function is registered as a before_app_request hook in the auth blueprint.
    It checks if the user_id is present in the session. If it is, it queries the database
    to get the corresponding user object and stores it in the g (app global) object.
    If the user_id is not present, it sets g.user to None.

    This function is necessary to make the currently logged in user accessible in templates.
    """
    # Get the user_id from the session
    user_id = session.get('user_id')

    if user_id is None:
        # If user_id is not present, set g.user to None
        g.user = None
    else:
        # If user_id is present, query the database to get the user object
        g.user = User.query.get(user_id)

def login_required(view):
    """
    Decorator for views that require the user to be logged in.

    Args:
        view (function): The view function to be wrapped.

    Returns:
        function: The wrapped view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """
        Wrapped view function that checks if the user is logged in.

        If the user is not logged in, it redirects to the login page.
        Otherwise, it calls the original view function.

        Args:
            **kwargs: Keyword arguments passed to the view function.

        Returns:
            The return value of the original view function.
        """
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/logout')
def logout():
    """
    Logs the user out by clearing the session and redirecting to the blog index page.

    Returns:
        redirect: Redirects to the blog index page.
    """
    # Clear the session to log the user out
    session.clear()
    
    # Redirect to the blog index page
    return redirect(url_for('blog.index'))
