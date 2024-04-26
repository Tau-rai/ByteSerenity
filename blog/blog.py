"""This module contains main routes and methods of the app"""
import os
import re
from datetime import datetime
from flask import Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename
from .auth import login_required
from .dbase import db
from .models import Comment, Post, PostTag, Tag, User


bp = Blueprint('blog', __name__, url_prefix='/blog')

@bp.route('/')
def index():
    """Returns the home page"""
    posts = (
        db.session.query(
            Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username,
            db.func.group_concat(Tag.name).label('tags'), Post.image
        )
        .join(User, Post.author_id == User.id)
        .outerjoin(PostTag, Post.id == PostTag.post_id)
        .outerjoin(Tag, PostTag.tag_id == Tag.id)
        .group_by(Post.id)
        .order_by(Post.created.desc())
        .all()
    )
    return render_template('blog/index.html', posts=posts)

@bp.route('/privacy-policy')
def privacy():
    """Shows site privacy policy"""
    return render_template('blog/privacy.html')

@bp.route('/terms-of-service')
def terms_of_service():
    """Shows site terms of service"""
    return render_template('blog/terms_of_service.html')