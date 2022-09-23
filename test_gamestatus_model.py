"""GameStatus model tests."""

# python -m unittest test_gamestatus_model.py

import os 
from unittest import TestCase 
from sqlalchemy import exc 

from models import db, User, GameStatus, Follows, Favorites 

# Setup environmental variable to use a different database for tests 
# Need to do this before importing our app, since that will already be connected to the database

os.environ['DATABASE_URL'] = "postgresql:///lockedingaming-test"

# Now we can import the app

from app import app

#Create our tables, do this here so we only create the tables once for all tests.
# In each test, we'll delete the data and create fresh new clean test data.

db.create_all()

class userModelTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):
        """Create test client, add sample data"""
        db.drop_all()
        db.create_all()

        self.uid = 64209
        u = User.signup("test@test.com", "test", "password")
        u.id = self.uid 
        db.session.commit()
        
        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res 

    def test_gamestatus_model(self):
        """Does basic model work?"""

        g = GameStatus(
            game_title="Game Title",
            status = "a status",
            user_id = self.uid
        )

        db.session.add(g)
        db.session.commit()

        #User should have 1 game status
        self.assertEqual(len(self.u.gamestatus), 1)
        self.assertEqual(self.u.gamestatus[0].status, "a status")

    def test_gamestatus_favorites(self):
        g1 = GameStatus(
            game_title = "the game",
            status = "the status",
            user_id = self.uid
        )
        g2 = GameStatus(
            game_title = "another game",
            status="another status",
            user_id = self.uid
        )

        u = User.signup("test2@gmail.com", "test2", "password")
        uid = 69
        u.id = uid 
        db.session.add_all([g1, g2, u])
        db.session.commit()

        u.favorites.append(g1)
        db.session.commit()

        f = Favorites.query.filter(Favorites.user_id == uid).all()
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].gamestatus_id, g1.id)