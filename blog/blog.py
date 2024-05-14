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
    """
    Returns the home page with published posts.

    This function queries the database to retrieve all published posts.
    The posts are joined with the User table to get the author's username.
    The posts are also joined with the PostTag and Tag tables to get the tags.
    The posts are ordered by their creation date in descending order.

    Returns:
        Rendered template 'index.html' with the posts.
    """
    # Query all published posts
    posts = (
        db.session.query(
            Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username,
            db.func.group_concat(Tag.name).label('tags'), Post.image
        )
        .join(User, Post.author_id == User.id)  # Join the User table to get the author's username
        .outerjoin(PostTag, Post.id == PostTag.post_id)  # Join the post_tags table
        .outerjoin(Tag, PostTag.tag_id == Tag.id)  # Join the tags table
        .filter(Post.status == 'published')  # Filter by published posts
        .group_by(Post.id)  # Group the posts by id
        .order_by(Post.created.desc())  # Order the posts by creation date in descending order
        .all()
    )
    return render_template('index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """
    Create a new post.

    This function handles the GET and POST requests to create a new post.
    If the request method is GET, it renders the create.html template with
    all tags from the database. If the request method is POST, it creates a
    new post with the provided title, body, and image.

    Returns:
        flask.Response: The rendered create.html template or a redirect to
                        the index page if the post is published. Otherwise,
                        a redirect to the profile page.
    """
    # Query all tags from the database
    tags = Tag.query.all()

    if request.method == 'POST':
        # Get the form data
        title = request.form['title']
        body = request.form['body']
        selected_tags = request.form.getlist('tags')
        image = request.files.get('image')
        action = request.form['action']
        created = datetime.now()
        error = None

        # Validate the form data
        if not title:
            error = 'Title is required.'

        if error is not None:
            # Flash the error message
            flash(error)
        else:
            if g.user is None:
                # Flash an error message
                flash('You need to be logged in to create a post.')
                return redirect(url_for('auth.login'))

            # Create a new post
            status = 'published' if action == 'Publish' else 'draft'
            post = Post(title=title, body=body, author_id=g.user.id, status=status)
            db.session.add(post)
            db.session.commit()

            # Save the image if provided
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join('/home/tau_rai/ByteSerenity/blog/static/public', filename))
                post.image = 'public/' + filename

            # Associate the post with selected tags
            if selected_tags:
                for tag_name in selected_tags:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if tag:
                        post_tag = PostTag(post_id=post.id, tag_id=tag.id)
                    else:  # If the tag doesn't exist, create a new one
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        db.session.commit()  # Commit the new tag creation

                    post_tag = PostTag(post_id=post.id, tag_id=tag.id)  # Create the post_tag association
                    db.session.add(post_tag)  # Add the association to the session
                db.session.commit()  # Commit the post_tag associations

            # Redirect to the index page if the post is published,
            # otherwise redirect to the profile page
            if action == 'Publish':
                return redirect(url_for('blog.index'))
            else:
                return redirect(url_for('blog.profile'))

    # Pass the tags to the template
    return render_template('create.html', tags=tags)



@bp.route('/<int:id>/post_detail', methods=('GET',))
def post_detail(id):
    """
    Shows post details.

    This function retrieves the post with the given ID and its corresponding
    comments and tags. It also retrieves the like count of the post. The
    retrieved information is then rendered in the 'post_detail.html' template.

    Args:
        id (int): The ID of the post to show details for.

    Returns:
        Rendered template 'post_detail.html' with the post, comments, tags, and like count.
    """
    # Retrieve the post with the given ID
    post = Post.query.get(id)

    # Retrieve all comments for the post
    comments = Comment.query.filter_by(post_id=id).all()

    # Retrieve all tags for the post
    tags = [tag.name for tag in post.tags]

    # Retrieve the like count of the post
    like_count = post.like_count

    # Render the template with the post, comments, tags, and like count
    return render_template('post_detail.html', post=post, comments=comments, tags=tags, like_count=like_count)

@bp.route('/search')
def search():
    """
    Searches for posts or categories.

    This function handles the search request. It retrieves the search query
    from the request arguments and performs a search in the database.
    If the query is empty, it renders the search.html template with an empty
    list of posts. Otherwise, it performs a database query to retrieve the
    matching posts. The query includes joins and filters the results based on
    the search query. The results are ordered by the post creation date in
    descending order.

    Returns:
        Rendered template 'search.html' with the posts and the search query.
    """
    # Retrieve the search query from the request arguments
    query = request.args.get('q', '').strip()

    if query == '':
        # If the query is empty, render the search template with an empty list of posts
        return render_template('search.html', posts=[])
    else:
        # Perform a database query to retrieve the matching posts
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

        # Render the search template with the matching posts
        return render_template('search.html', posts=posts)

@login_required
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update_post(id):
    """
    Update a post.

    This function handles the GET and POST requests to update a post.
    If the request method is GET, it renders the update_post.html template
    with the post object. If the request method is POST, it updates the post
    with the provided title, body, and image.

    Args:
        id (int): The id of the post to update.

    Returns:
        flask.Response: The rendered update_post.html template or a redirect
                        to the index page.
    """
    # Query the post from the database
    post = Post.query.get(id)

    if request.method == 'POST':
        # Get the form data
        title = request.form['title']
        body = request.form['body']
        image = request.files['image']
        error = None

        # Validate the form data
        if not title:
            error = 'Title is required.'

        if error is not None:
            # Flash the error message
            flash(error)
        else:
            # Update the post with the new data
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join('/home/tau_rai/ByteSerenity/blog/static/public/', filename))
                post.image = 'public/' + filename
            post.title = title
            post.body = body
            post.status = 'published'
            db.session.commit()
            # Redirect to the index page
            return redirect(url_for('blog.index'))

    # Render the update_post.html template with the post object
    return render_template('update_post.html', post=post)

@bp.route('/tags/<tag_name>')
def tag(tag_name):
    """
    Shows posts associated with a specific tag.

    This function queries the database to find all posts associated with the given tag.
    The posts are rendered in the 'tag.html' template.

    Args:
        tag_name (str): The name of the tag to show posts for.

    Returns:
        Rendered template 'tag.html' with the posts and the tag name.
    """
    # Query the database to find all posts associated with the tag
    posts = (
        db.session.query(Post.id, Post.title)  # Only select the post ID and title
        .join(PostTag, Post.id == PostTag.post_id)  # Join the post_tags table
        .join(Tag, PostTag.tag_id == Tag.id)  # Join the tags table
        .filter(Tag.name == tag_name)  # Filter by the given tag name
        .all()
    )

    # Render the template with the posts and the tag name
    return render_template('tag.html', posts=posts, tag_name=tag_name)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """
    Deletes a post.

    This function handles the HTTP POST request to delete a post. The post is identified by the 'id'
    parameter in the URL. The function first queries the database to find the post with the given id
    and then deletes it. After deleting the post, the function commits the changes to the database.
    Finally, the function redirects the user back to the index page.

    Args:
        id (int): The id of the post to delete.

    Returns:
        Response: A redirect response to the index page.
    """
    # Query the database to find the post with the given id
    post_to_delete = db.session.query(Post).filter(Post.id == id).one_or_none()

    # If the post exists, delete its comments first
    if post_to_delete:
        comments_to_delete = db.session.query(Comment).filter(Comment.post_id == id).all()
        for comment in comments_to_delete:
            db.session.delete(comment)

        # Then delete the post
        db.session.delete(post_to_delete)
        db.session.commit()

    # Redirect the user back to the index page
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/comment', methods=('GET', 'POST'))
def comment(id):
    """
    Create a new comment.

    Args:
        id (int): The id of the post to comment on.

    Returns:
        Rendered template for comments.html with comments and error messages if any.
    """
    if request.method == 'POST':
        # Get the comment body
        body = request.form['body']
        error = None

        # Validate the comment body
        if not body:
            error = 'Comment body is required.'

        # Check if user is logged in
        if g.user is None:
            error = 'You must be logged in to add a comment.'

        # Handle validation error
        if error is not None:
            flash(error, 'error')
        else:
            # Create a new Comment object
            comment = Comment(post_id=id, body=body, author_id=g.user.id)

            # Add the new comment to the session
            db.session.add(comment)

            # Commit the session to save the changes in the database
            db.session.commit()

            # Redirect to post detail page
            return redirect(url_for('blog.post_detail', id=id))
    
    # Query all comments for the post
    comments = Comment.query.filter_by(post_id=id).all()
        
    # Render the template with comments
    return render_template('comments.html', comments=comments)

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

@bp.route('/profile')
@login_required
def profile():
    """
    Shows user profile

    This function retrieves the current user object and queries the database for all published posts
    and drafts written by the user. It then renders the profile.html template with the user object,
    published posts, and drafts.

    Returns:
        flask.Response: The rendered profile.html template.
    """
    # Get the current user object
    user = g.user 

    # Query the database for all published posts and drafts written by the user
    posts = Post.query.filter_by(author_id=user.id, status='published').all() 
    drafts = Post.query.filter_by(author_id=user.id, status='draft').all() 

    # Render the profile.html template with the user object, published posts, and drafts
    return render_template('profile.html', user=user, posts=posts, drafts=drafts)

@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """
    Updates user profile

    This function handles the update of the user's profile information. It retrieves the user's
    first name, last name, date of birth, and bio from the request form and assigns them to the
    corresponding fields of the user object. If an avatar is provided, the function saves it to
    the static folder and assigns the public path to the user's avatar field. It also checks if the
    user's email is valid and if there is already a user with the same email. If any error occurs,
    the function rolls back the changes and displays an appropriate error message. Finally, it
    redirects the user to their profile page.

    Returns:
        flask.redirect: Redirects the user to the profile page.
    """
    # Get the current user object
    user = g.user 

    # Update user fields with data from the form
    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.date_of_birth = request.form.get('date_of_birth')
    user.bio = request.form.get('bio')

    # If an avatar is provided, save it to the static folder and assign the public path to the user's avatar field
    avatar = request.files.get('avatar')
    if avatar:
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join('/home/tau_rai/ByteSerenity/blog/static/public/', filename))
        user.avatar = 'public/' + filename 

    # Check if the user's email is valid and if there is already a user with the same email
    if user.email and isinstance(user.email, str) and not re.fullmatch(email_regex, user.email):
        flash('Invalid email address.')
    else:
        existing_user = User.query.filter(User.email == user.email, User.id != user.id).first()
        if existing_user:
            flash('Email address already in use.')
        else:
            try:
                # Commit the changes to the database
                db.session.commit()
                flash('Profile updated successfully!')
            except Exception as e:
                # Roll back the changes if an error occurs
                db.session.rollback()
                flash('An error occurred while updating the profile.')
            finally:
                # Refresh the user object with the latest data from the database
                user = User.query.get(g.user.id)

    # Redirect the user to their profile page
    return redirect(url_for('blog.profile'))

@bp.route('/about')
def about_us():
    """Shows the site about us section"""
    return render_template('about_us.html')

@bp.route('/contact-us')
def contact_us():
    """Shows the site about us section"""
    return render_template('contact_us.html')

@bp.route('/like_post/<int:id>', methods=['POST'])
def like_post(id):
    """
    Enables users to like posts.
    
    Args:
        id (int): The id of the post to like.
    
    Returns:
        json: A JSON object containing the new like count for the post.
    """
    # Get the post with the given id
    post = Post.query.get(id)
    
    # Increment the like count by 1
    post.like_count += 1
    
    # Save the changes to the database
    db.session.commit()
    
    # Return the new like count as a JSON object
    return jsonify({'like_count': post.like_count})
