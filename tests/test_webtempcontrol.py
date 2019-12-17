import unittest
from app import db, create_app
from config import TestConfig
from app.main.models import User
import re

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True);
        response = self.client.post('/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_add_webtempcontrol(self):
        # register a new account
        response = self.client.post('/wtc/', data={
             'ip_adress': '127.0.0.1',
        #     'username': 'john',
        #     'password': 'cat',
        #     'password2': 'cat'
        })
        self.assertEqual(response.status_code, 302)
