"""Configuration file"""

import os
import secrets


# Database credentials
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

class Config:
    SECRET_KEY = secrets.token_hex(16)
    SESSION_COOKIE_SECURE=True
    SESSION_PERMANENT = False  # Sessions are not permanent
    SESSION_USE_SIGNER = True  # Sign the session cookie
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    # Add database configuration
    SQLALCHEMY_DATABASE_URI=f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER='/home/tau_rai/ByteSerenity/static/public',  # Upload folder
    MAIL_SERVER=os.environ.get('MAIL_SERVER')
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
