"""SQLAlchemy model for QuickStick"""

from datetime import datetime 

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy 

bcrypt = Bcrypt()
db = SQLAlchemy()

class Follows(db.Model):
    """Connection of a follower <-> followed_user"""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(db.Integer, db.ForeignKet('users.id', ondelete="cascade"), primary_key=True)

    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)

class Likes(db.Model):
    """Mapping user likes to QuickStick"""

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    trail_id = db.Column(db.Integer, db.ForeignKey('trails.id', ondelete='cascade'), unique=True)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

