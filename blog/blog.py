from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
from sqlalchemy import func, or_
from .auth import login_required
from .models import User, Post, Tag, PostTag, Comment  
from .dbase import db
from werkzeug.utils import secure_filename
import re
import os
from datetime import datetime

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
