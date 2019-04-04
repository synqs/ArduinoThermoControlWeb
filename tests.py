import unittest
from app import db, create_app
from config import Config
from app.main.models import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class FirstTestCase(unittest.TestCase):
    def setUp(self):
        self.socketio, self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
