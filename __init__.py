"""This module defines the database conection and creates the app"""
import click
import os
from flask import Flask, g
from .config import Config
from flask.cli import with_appcontext
from flask_mail import Mail
from markupsafe import Markup
import logging
from logging.handlers import RotatingFileHandler
from .dbase import db
from .models import Comment, PostTag, Tag, User

# Initialize mail
mail = Mail()

# Custom Jinja filter for converting newline characters to HTML <br> tags
def nl2br(value):
    """Handles page breaks on the post body"""
    return Markup(value.replace('\n', '<br>\n'))

def get_db():
    """Initializes a database connection"""
    if 'db' not in g:
        g.db = db
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.session.remove()

def init_db():
    """creates all tables in the database"""
    db = get_db()
    db.create_all()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask: The Flask application instance.
    """
    # Create and configure the Flask application
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object(Config)

    # Initialize mail with the Flask app
    mail.init_app(app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    db.init_app(app)

    # Register blueprints
    from . import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='blog.index')

    # Register custom Jinja filter
    app.jinja_env.filters['nl2br'] = nl2br

    # Initialize the database command
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/geekzen.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('GeekZen startup')
    
    return app
