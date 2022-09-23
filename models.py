"""SQLAlchemy model for Locked In Gaming"""

from datetime import datetime 

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy 

bcrypt = Bcrypt()
db = SQLAlchemy()



class Follows(db.Model):
    """Connection of a follower and followed user"""
    __tablename__ = 'follows'

    user_being_followed_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)

class GameStatus(db.Model):
    """model for games to be liked, played, or locked in"""
    __tablename__ = 'gamestatus'

    id = db.Column(db.Integer, primary_key = True)
    game_title = db.Column(db.Text, nullable = False)
    status = db.Column(db.String, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable= False)

    user = db.relationship('User')

class Favorites(db.Model):
    """Maps user favorites to gamestatus"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    gamestatus_id = db.Column(db.Integer, db.ForeignKey('gamestatus.id', ondelete = 'cascade'))

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, nullable = False, unique = True)
    profile_picture = db.Column(db.Text, default="/static/images/default-profile-picture.jpg")
    banner_picture = db.Column(db.Text, default="/static/images/default-banner.jpg")
    bio = db.Column(db.Text)
    location = db.Column(db.Text)

    gamestatus = db.relationship('GameStatus')
    favorites = db.relationship('GameStatus', secondary='favorites')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )
    following = db.relationship(
        "User",
        secondary = "follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by 'other_user'?"""
        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following 'other_user'?"""
        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod 
    def signup(cls, username, email, password):
        """Signup user hashes password and adds user to system"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email = email,
            username = username,
            password = hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod 
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'"""
        user = cls.query.filter_by(username = username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user 

        return False 

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app 
    db.init_app(app)