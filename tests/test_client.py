import unittest
from app import db, create_app
from config import TestConfig
from app.main.models import User
import re

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.socketio, self.app = create_app(TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_empty_db(self):
        """Start with a blank database."""

        rv = self.client.get('/')
        assert b'Login to add new devices' in rv.data

    def test_password_hashing(self):
        user = User(username='susan')
        user.set_password('cat')
        self.assertFalse(user.check_password('dog'))
        self.assertTrue(user.check_password('cat'))

    def test_register_and_login(self):
        # register a new account
        response = self.client.post('/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertEqual(response.status_code, 302)

        # login with the new account
        response = self.client.post('/login', data={
            'username': 'john',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200);

        self.assertTrue(re.search('Logout',
                                  response.get_data(as_text=True)))

        # log out
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login' in response.get_data(as_text=True))

        # test double registering
        response = self.client.post('/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertEqual(response.status_code, 200)
