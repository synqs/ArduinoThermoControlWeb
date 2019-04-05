import unittest
from app import db, create_app
from config import TestConfig
from app.main.models import User

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.socketio, self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

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
        db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    unittest.main(verbosity=2)
