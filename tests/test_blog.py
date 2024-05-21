import unittest
from flask import Flask, render_template, g, request, flash, redirect, url_for
from __init__ import create_app, db
from blog import bp
from models import Post, User, Tag, PostTag, Comment

class TestBlog(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        # Create sample posts and users
        user = User(username='testuser')
        post1 = Post(title='Post 1', body='Body 1', author=user)
        post2 = Post(title='Post 2', body='Body 2', author=user)
        db.session.add_all([user, post1, post2])
        db.session.commit()

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post 1", response.data)
        self.assertIn(b"Post 2", response.data)

    def test_privacy(self):
        response = self.client.get('/blog/privacy-policy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Privacy Policy", response.data)

    def test_terms_of_service(self):
        response = self.client.get('/blog/terms-of-service')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Terms of Service", response.data)

        """
        Test case for commenting on a post with valid input.
        """

    def test_comment_valid_input(self):
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = 1
            response = client.post('/1/comment', data={'body': 'Test comment'})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, 'http://localhost/1/post_detail')
            comments = Comment.query.filter_by(post_id=1).all()
            self.assertEqual(len(comments), 1)
            self.assertEqual(comments[0].body, 'Test comment')
            self.assertEqual(comments[0].author_id, 1)

    def test_comment_empty_input(self):
        """
        Test case for commenting on a post with empty input.
        """
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = 1
            response = client.post('/1/comment', data={'body': ''})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Comment body is required.', response.data)
            comments = Comment.query.filter_by(post_id=1).all()
            self.assertEqual(len(comments), 0)

    def test_comment_without_login(self):
        """
        Test case for commenting on a post without being logged in.
        """
        with self.app.test_client() as client:
            response = client.post('/1/comment', data={'body': 'Test comment'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You must be logged in to add a comment.', response.data)
            comments = Comment.query.filter_by(post_id=1).all()
            self.assertEqual(len(comments), 0)

if __name__ == '__main__':
    unittest.main()
