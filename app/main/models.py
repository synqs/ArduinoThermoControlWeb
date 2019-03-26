from flask_login import UserMixin
from app import db

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    
class User(UserMixin, db.Model):
    # ...
