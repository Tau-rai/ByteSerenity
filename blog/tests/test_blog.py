import unittest
from flask import Flask, render_template
from __init__ import create_app, db
from models import Post, User, Tag, PostTag

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

if __name__ == '__main__':
    unittest.main()
