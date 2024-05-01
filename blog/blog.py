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
        .filter(Post.status == 'published')
        .group_by(Post.id)
        .order_by(Post.created.desc())
        .all()
    )
    return render_template('index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post"""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags = request.form.getlist('tags')
        new_tag_name = request.form.get('newTag')
        image = request.files.get('image')
        action = request.form['action']
        created = datetime.now()
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            if g.user is None:
                flash('You need to be logged in to create a post.')
                return redirect(url_for('auth.login'))

            status = 'published' if action == 'Publish' else 'draft'
            post = Post(title=title, body=body, author_id=g.user.id, status=status)
            db.session.add(post)
            db.session.commit()

            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join('/home/tau_rai/ByteSerenity/blog/static/public/', filename))
                post.image = 'public/' + filename

            if tags:
                for tag in tags:
                    existing_tag = Tag.query.filter_by(name=tag).first()
                    if not existing_tag:
                        new_tag = Tag(name=tag)
                        db.session.add(new_tag)
                        db.session.commit()
                        post_tag = PostTag(post_id=post.id, tag_id=new_tag.id)
                    else:
                        post_tag = PostTag(post_id=post.id, tag_id=existing_tag.id)
                    db.session.add(post_tag)

            if new_tag_name:  # Check if 'newTag' field is not empty
                existing_tag = Tag.query.filter_by(name=new_tag_name).first()
                if not existing_tag:
                    new_tag = Tag(name=new_tag_name)
                    db.session.add(new_tag)
                    db.session.commit()
                    post_tag = PostTag(post_id=post.id, tag_id=new_tag.id)
                else:
                    post_tag = PostTag(post_id=post.id, tag_id=existing_tag.id)
                db.session.add(post_tag)

            db.session.commit()

            if action == 'Publish':
                return redirect(url_for('blog.index'))
            else:
                return redirect(url_for('blog.profile'))

    return render_template('writeblog.html')

@bp.route('/<int:id>/post_detail', methods=('GET',))
def post_detail(id):
    """Shows post details"""
    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id=id).all()
    tags = [tag.name for tag in post.tags]
    return render_template('viewblog.html', post=post, comments=comments, tags=tags)

@bp.route('/search')
def search():
    """Searches for posts or categories"""
    query = request.args.get('q', '').strip()
    if query == '':
        return render_template('blog/search.html', posts=[])
    else:
        posts = (
            db.session.query(
                Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username,
                db.func.group_concat(Tag.name).label('tags'), Post.image
            )
            .join(User, Post.author_id == User.id)
            .outerjoin(PostTag, Post.id == PostTag.post_id)
            .outerjoin(Tag, PostTag.tag_id == Tag.id)
            .filter(
                db.or_(
                    Post.title.like('%' + query + '%'),
                    Post.body.like('%' + query + '%'),
                    Tag.name.like('%' + query + '%')
                )
            )
            .group_by(Post.id)
            .order_by(Post.created.desc())
            .all()
        )
        return render_template('search.html', posts=posts)

@login_required
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    """Updates a post"""
    post = Post.query.get(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        image = request.files['image']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join('/home/tau_rai/ByteSerenity/blog/static/public/', filename))
                post.image = 'public/' + filename
            post.title = title
            post.body = body
            post.status = 'published'
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('update.html', post=post)

@bp.route('/tags/<tag_name>')
def tag(tag_name):
    """Shows tags"""
    posts = (
        db.session.query(Post.id, Post.title)
        .join(PostTag, Post.id == PostTag.post_id)
        .join(Tag, PostTag.tag_id == Tag.id)
        .filter(Tag.name == tag_name)
        .all()
    )
    return render_template('tag.html', posts=posts, tag_name=tag_name)

@login_required
@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    """Deletes a post"""
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/comment', methods=('GET', 'POST'))
def comment(id):
    """Create a new comment"""
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Comment body is required.'

        if g.user is None:
            error = 'You must be logged in to add a comment.'

        if error is not None:
            flash(error, 'error')
        else:
            # Create a new Comment object
            comment = Comment(post_id=id, body=body, author_id=g.user.id)

            # Add the new comment to the session
            db.session.add(comment)

            # Commit the session to save the changes in the database
            db.session.commit()

            return redirect(url_for('blog.detail', id=id))
        
    return render_template('viewcomments.html')

@bp.route('/privacy-policy')
def privacy():
    """Shows site privacy policy"""
    return render_template('privacy.html')

@bp.route('/terms-of-service')
def terms_of_service():
    """Shows site terms of service"""
    return render_template('terms_of_service.html')

# Regular expression for validating an Email
email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Updates user profile"""
    user = g.user  # Fetch the current logged-in user object
    posts = Post.query.filter_by(author_id=user.id, status='published').all()  
    drafts = Post.query.filter_by(author_id=user.id, status='draft').all()  

    if request.method == 'POST':
        # Fetch form data
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.date_of_birth = request.form.get('date_of_birth')
        user.bio = request.form.get('bio')
        user.email = request.form.get('email')

        # Fetch profile picture
        avatar = request.files.get('avatar')
        if avatar:
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join('/home/tau_rai/try/blogA/static/public', filename))
            user.avatar = 'public/' + filename  # Update the user's avatar path

        # Validate email format
        if not re.fullmatch(email_regex, user.email):
            flash('Invalid email address.')
        else:
            # Check if email already exists in the database
            existing_user = User.query.filter(User.email == user.email, User.id != user.id).first()
            if existing_user:
                flash('Email address already in use.')
            else:
                try:
                    # Update user details in the database
                    db.session.commit()
                    flash('Profile updated successfully!')
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while updating the profile.')

    return render_template('profile.html', user=user, posts=posts, drafts=drafts)