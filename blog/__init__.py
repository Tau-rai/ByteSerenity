"""This module defines the database conection and creates the app"""
import click
import os
from flask import Flask, g
from flask.cli import with_appcontext
from markupsafe import Markup
from .dbase import db
from .models import Comment, PostTag, Tag, User
import secrets

# Database credentials
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

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

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(16),
        SQLALCHEMY_DATABASE_URI=f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER='/home/tau_rai/ByteSerenity/blog/static/public'  # Set the upload folder path
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
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

    return app
