"""User View tests"""
# Run tests with: FLASK_ENV=production python -m unittest test_user_views.py
import os 
from unittest import TestCase 
from models import db, connect_db, GameStatus, User, Favorites, Follows 
from bs4 import BeautifulSoup
#setup env variable to use dif database for tests before importing our app
os.environ['DATABASE_URL'] = "postgresql:///lockedingaming-test"
from app import CURR_USER_KEY, app

db.create_all()
app.config['WTF_CSRF_ENABLED']= False 

class GameStatusViewTestCase(TestCase):
    """Test views for GameStatus"""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.testuser = User.signup(
            email="test@test.com",
            username = "testuser",
            password="testpassword"
        )
        self.testuser_id = 4029
        self.testuser.id = self.testuser_id 

        self.u1 = User.signup("test1@test.com", "abc", "password")
        self.u1_id = 123
        self.u1.id = self.u1_id 
        self.u2 = User.signup("test2@test.com", "efg", "password")
        self.u2_id = 456
        self.u2.id = self.u2_id 
        self.u3 = User.signup("test3@test.com", "hij", "password")
        self.u4 = User.signup("test4@test.com", "tester", "password")

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp 

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("testuser", str(resp.data))
            self.assertIn("abc", str(resp.data))
            self.assertIn("efg", str(resp.data))
            self.assertIn("hij", str(resp.data))
            self.assertIn("tester", str(resp.data))

    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("testuser", str(resp.data))
            self.assertIn("tester", str(resp.data))
            self.assertNotIn("abc", str(resp.data))
            self.assertNotIn("efg", str(resp.data))
            self.assertNotIn("hij", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(resp.status_code, 200)

            self.assertIn("testuser", str(resp.data))

    def setup_favorites(self):
        g1 = GameStatus(game_title="Fall Guys", status="Lots of beans", user_id=self.testuser_id)
        g2 = GameStatus(game_title="Lost Ark", status="Lots of microtransactions", user_id=self.testuser_id)
        g3 = GameStatus(id = 1234, game_title="League of Legends", status="Lots of toxicity", user_id=self.u1_id)
        db.session.add_all([g1, g2, g3])
        db.session.commit()

        f1 = Favorites(user_id=self.testuser_id, gamestatus_id = 1234)
        db.session.add(f1)
        db.session.commit()

    def test_user_show_with_favorites(self):
        self.setup_favorites()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            #test for count of 2 game statuses
            self.assertIn("2", found[0].text)

            #Test for count of 0 followers
            self.assertIn("0", found[1].text)

            #test for count of 0 following
            self.assertIn("0", found[2].text)

            #Test for count of 1 favorite
            self.assertIn("1", found[3].text)

    def test_add_favorite(self):
        g = GameStatus(id = 1995, game_title="Pong", status="First game ever!", user_id = self.u1_id)
        db.session.add(g)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id 

            resp = c.post("/gamestatus/1995/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            favorites = Favorites.query.filter(Favorites.gamestatus_id == 1995).all()
            self.assertEqual(len(favorites), 1)
            self.assertEqual(favorites[0].user_id, self.testuser_id)

    def test_remove_favorite(self):
        self.setup_favorites()

        g = GameStatus.query.filter(GameStatus.status == "Lots of toxicity").one()
        self.assertIsNotNone(g)
        self.assertNotEqual(g.user_id, self.testuser_id)

        f = Favorites.query.filter(
            Favorites.user_id == self.testuser_id and Favorites.gamestatus_id == g.id
        ).one()

        #Now we are confident testuser likes the messsage "Lots of toxicity"
        self.assertIsNotNone(f)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/gamestatus/{g.id}/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            favorites = Favorites.query.filter(Favorites.gamestatus_id == g.id).all()
            # the favorite has been removed
            self.assertEqual(len(favorites), 0)

    def test_unauthenticated_favorite(self):
        self.setup_favorites()

        g = GameStatus.query.filter(GameStatus.status == "Lots of toxicity").one()
        self.assertIsNotNone(g)

        favorites_count = Favorites.query.count()

        with self.client as c:
            resp = c.post(f"/gamestatus/{g.id}/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))
            #The number of favorites has not changed since making the request
            self.assertEqual(favorites_count, Favorites.query.count())

    def setup_followers(self):
        f1 = Follows(user_being_followed_id = self.u1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id = self.u2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id = self.testuser_id, user_following_id=self.u1_id)
        
        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def test_user_show_with_follows(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            #test for a count of 0 Game Statuses
            self.assertIn("0", found[0].text)
            
            #Test for count of 2 following
            self.assertIn("2", found[1].text)

            #Test for a count of 1 follower
            self.assertIn("1", found[2].text)

            #Test for a count of 0 favorites
            self.assertIn("0", found[3].text)

    def test_show_following(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id 
            
            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("abc", str(resp.data))
            self.assertIn("efg", str(resp.data))
            self.assertIn("hij", str(resp.data))
            self.assertIn("tester", str(resp.data))

    def test_show_followers(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id 
            
            resp = c.get(f"/users/{self.testuser_id}/followers")
            self.assertIn("abc", str(resp.data))
            self.assertIn("efg", str(resp.data))
            self.assertIn("hij", str(resp.data))
            self.assertIn("tester", str(resp.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("abc", str(resp.data))
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_unauthorized_followers_page_access(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("abc", str(resp.data))
            self.assertIn("Access unauthorized.", str(resp.data))