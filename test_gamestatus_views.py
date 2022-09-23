"""Gamestatus View tests.
Run Tests with: FLASK_ENV=production python -m unittest test_gamestatus_views.py"""
import os
from unittest import TestCase 

from models import db, connect_db, GameStatus, User

#Before importing app, setup environmental variable to use a different database for the tests.
# Need to do this before importing the app, since that is already connected to the database.
os.environ['DATABASE_URL'] = "postgresql:///lockedingaming-test"

#Now import app
from app import app, CURR_USER_KEY

#Create our tables
db.create_all()

#Don't have WTForms use CSRF b/c it's hard to test
app.config['WTF_CSRF_ENABLED'] = False 

class GameStatusViewTestCase(TestCase):
    """Test views for GameStatus."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(email="test@test.com",
                                    username="test",
                                    password="password")
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id 
        db.session.commit()

    def test_add_gamestatus(self):
        """Can we add a game status?"""
        #since we need to change the session to mimic logging in, we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id 

            # Now that the session setting is saved, we can have the rest of our tests
            resp = c.post("/gamestatus/new", data={"game_title": "Lost Ark", "status": "Great Game!"})

            #Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            status = GameStatus.query.one()
            self.assertEqual(status.game_title, "Lost Ark")
            self.assertEqual(status.status, "Great Game!")

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/gamestatus/new", data={"game_title": "Diablo: Immortal", "status": "Lots of microtransactions"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 751892

            resp = c.post("/gamestatus/new", data={"game_title": "Fall Guys", "status": "Lots of beans!"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_gamestatus_show(self):
        g = GameStatus(
            id = 1234,
            game_title = "League of Legends",
            status = "Toxic game!",
            user_id=self.testuser_id
        )

        db.session.add(g)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            g = GameStatus.query.get(1234)

            resp = c.get(f'/gamestatus/{g.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(g.game_title, str(resp.data))
            self.assertIn(g.status, str(resp.data))

    def test_invalid_gamestatus_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/gamestatus/999999')

            self.assertEqual(resp.status_code, 404)

    def test_gamestatus_delete(self):
        g = GameStatus(
            id = 1234,
            game_title="test title",
            status= "test status",
            user_id = self.testuser_id
        )
        db.session.add(g)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/gamestatus/1234/delete', follow_redirects = True)
            self.assertEqual(resp.status_code, 200)

            g = GameStatus.query.get(1234)
            self.assertIsNone(g)

    def test_unauthorized_gamestatus_delete(self):
        # Second User that will attempt to delete gamestatus
        u = User.signup(email = "unauthorized@test.com",
                        username="unauthorized-user",
                        password="password")
        u.id = 54353

        # Game Status owned by test user
        g = GameStatus(
            id=1234,
            game_title="test title",
            status = "test status",
            user_id = self.testuser_id
        )
        db.session.add_all([u, g])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 54353
            
            resp = c.post('/gamestatus/1234/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

            g = GameStatus.query.get(1234)
            self.assertIsNotNone(g)

    def test_gamestatus_delete_no_authentication(self):
        g = GameStatus(
            id=1234,
            game_title="test title",
            status = "test status",
            user_id = self.testuser_id
        )
        db.session.add(g)
        db.session.commit()

        with self.client as c:
            resp = c.post("/gamestatus/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            g = GameStatus.query.get(1234)
            self.assertIsNotNone(g)

