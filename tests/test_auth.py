import unittest
from flask import Flask, session
from werkzeug.security import generate_password_hash, check_password_hash
from .. import create_app
from ..dbase import db
from ..models import User

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_signup(self):
        response = self.client.post('/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(User.query.filter_by(username='testuser').first())

    def test_signup_existing_user(self):
        existing_user = User(username='existinguser', email='existing@example.com', password='existingpassword')
        db.session.add(existing_user)
        db.session.commit()

        response = self.client.post('/signup', data={
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'testpassword'
        })
        self.assertIn(b"User existinguser or email existing@example.com is already registered.", response.data)

    def test_login(self):
        user = User(username='testuser', email='test@example.com', password=generate_password_hash('testpassword'))
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(session.get('user_id'), user.id)

    def test_login_incorrect_email(self):
        response = self.client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'testpassword'
        })
        self.assertIn(b"Incorrect email or password.", response.data)

    def test_login_incorrect_password(self):
        user = User(username='testuser', email='test@example.com', password=generate_password_hash('testpassword'))
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertIn(b"Incorrect email or password.", response.data)

    def test_logout(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(session.get('user_id'))

if __name__ == '__main__':
    unittest.main()
