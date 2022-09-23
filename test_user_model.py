"""User model tests."""
# run tests: python -m unittest test_user_model.py
import os
from unittest import TestCase 
from sqlalchemy import exc 
from models import db, User, GameStatus, Follows 
#Before importing app, setup env variable to use dif database for tests. Need to do this before importing app.
os.environ['DATABASE_URL'] = "postgresql:///lockedingaming-test"
#Now import app
from app import app 
#Crete tables
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for game statuses"""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1@email.com", "test1", "password")
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2@email.com", "test2", "password")
        uid2 = 2222
        u2.id = uid2 

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1 
        self.uid1 = uid1 

        self.u2 = u2 
        self.uid2 = uid2 

        self.client = app.test_client()
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res 

    def test_user_model(self):
        """Does basic user model work?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PWD"
        )
        db.session.add(u)
        db.session.commit()

        #User should have no messages, no followers, no following, and no game statuses
        self.assertEqual(len(u.gamestatus), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.gamestatus), 0)
        self.assertEqual(len(u.following), 0)

    # Following tests
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    # Signup Tests
    def test_valid_signup(self):
        u_test = User.signup("testuser", "testuser@test.com",  "password")
        uid = 12345
        u_test.id = uid 
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.email, "testuser@test.com")
        self.assertEqual(u_test.username, "testuser")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid_user = User.signup("test@test.com", None, "password")
        uid = 123456
        invalid_user.id = uid 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup(None, "testuser", "password")
        uid = 7564893
        invalid.id = uid 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testuser@test.com", "testuser", "")

        with self.assertRaises(ValueError) as context:
            User.signup("testuser@test.com", "testuser", None)

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("invaliduser", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "invalidpassword"))