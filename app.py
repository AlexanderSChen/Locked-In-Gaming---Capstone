import os 

from secretskey import SECRET_API_KEY
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError 
from forms import UserAddForm, LoginForm, UserEditForm, GameStatusForm
from models import db, connect_db, User, Favorites, GameStatus, Follows
import requests


app= Flask(__name__)

API_BASE_URL = "https://free-to-play-games-database.p.rapidapi.com"
API_HEADERS = {'X-RapidAPI-Key': SECRET_API_KEY, 'X-RapidAPI-Host': "free-to-play-games-database.p.rapidapi.com"}

CURR_USER_KEY = "curr_user"

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///lockedingaming'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "supersecretkeysecret")

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None 

def do_login(user):
    """Log in User"""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def check_user():
    """Check if authorized user is logged in, if not then user is redirected to homepage"""
    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect("/")
        

            
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup. Creates new user, adds to DB, redirect to Home page.
    If form invalid, present form. If already a user with username, flash message and represent form"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username = form.username.data,
                password = form.password.data,
                email = form.email.data
            )
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form = form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form = form)


@app.route('/')
def home_page():
    """Home Page"""
    res = requests.request("GET", f"{API_BASE_URL}/api/games", headers = API_HEADERS)
    games = res.json()
    return render_template('games/all_games.html', games = games)

@app.route('/login', methods=['GET', "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, 
                                form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form = form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect('/login')

@app.route('/users')
def list_users():
    """Page with listing of users. Take 'q' param in querystring by that username"""
    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    return render_template('users/index.html', users = users)

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile"""

    user = User.query.get_or_404(user_id)

    gamestatus = (GameStatus.query.filter(GameStatus.user_id == user_id).order_by(GameStatus.timestamp.desc()).limit(100).all())

    favorites = [gamestatus.id for gamestatus in user.favorites]

    return render_template('/users/show.html', user = user, gamestatus = gamestatus, favorites = favorites)

@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people user is following"""
    check_user()

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)

@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers for the user"""
    check_user()

    user = User.query.get_or_404(user_id)
    return render_template("users/followers.html", user=user)

@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add follow for currently logged in user"""
    check_user()

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/followers")

@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently logged-in user stop following this user"""
    check_user()

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()
    return redirect(f"/users/{g.user.id}/following")

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def show_favorites(user_id):
    """Show favorited gamestatuses"""
    check_user()

    user = User.query.get_or_404(user_id)
    return render_template('users/favorites.html', user=user, favorites=user.favorites)

@app.route('/gamestatus/<int:gamestatus_id>/favorite', methods=['POST'])
def add_favorite(gamestatus_id):
    """Toggle a favorited gamestatus fpr the currently logged in user"""
    check_user()

    favorite_gamestatus = GameStatus.query.get_or_404(gamestatus_id)
    if favorite_gamestatus.user_id == g.user.id:
        return abort(403)

    user_favorites = g.user.favorites

    if favorite_gamestatus in user_favorites:
        g.user.favorites = [favorite for favorite in user_favorites if favorite != favorite_gamestatus]
    else:
        g.user.favorites.append(favorite_gamestatus)

    db.session.commit()

    return redirect(f"/users/{g.user.id}")

@app.route('/users/profile', methods=['GET', 'POST'])
def edit_profile():
    """Update profile for current user"""
    check_user()

    user = g.user
    form = UserEditForm(obj = user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.profile_picture = form.profile_picture.data or "/static/images/default-profile-picture.jpg"
            user.banner_picture = form.banner_picture.data or "/static/images/default-banner.jpg"
            user.bio = form.bio.data
            user.location = form.location.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('/users/edit.html', form = form, user_id = user.id)

@app.route('/users/delete', methods=['POST'])
def delete_user():
    """Delete user"""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")
##################################################################
# game routes:

@app.route('/games', methods=['GET'])
def show_games_list():
    """Displays all games"""
    res = requests.request("GET", f"{API_BASE_URL}/api/games", headers = API_HEADERS)
    games = res.json()
    return render_template("games/all_games.html", games = games)

@app.route('/game/<int:game_id>')
def show_game(game_id):
    """Show details about specific game"""
    res = requests.request("GET", f"{API_BASE_URL}/api/game", headers = API_HEADERS, params = {'id': f"{game_id}"})
    gamedb = res.json()
    gamestatus = GameStatus.query.all()
    user = g.user
    favorites = [gamestatus.id for gamestatus in user.favorites]
    # gamedb = game_data(game_id)

    return render_template("games/detail.html", game = gamedb, gamestatus = gamestatus, user = user, favorites = favorites) 

@app.route('/games/<string:game_category>')
def show_game_category(game_category):
    """Show games that match the category of its genre"""
    res = requests.request("GET", f"{API_BASE_URL}/api/games", headers = API_HEADERS, params={"category": f"{game_category}"})
    games = res.json()
    category = game_category
    
    return render_template("games/game_category.html", games = games, category = category)

###################################################################
# GameStatus routes:

@app.route('/gamestatus/<int:gamestatus_id>/favorite', methods=['POST'])
def favorite_gamestatus(gamestatus_id):
    """Toggle a favorite gamestatus for user if logged in"""

    check_user()

    fav_status = GameStatus.query.get_or_404(gamestatus_id)
    if fav_status.user_id == g.user.id:
        return abort(403)

    user_favorites = g.user.favorites

    if fav_status in user_favorites:
        g.user.favorites = [favorite for favorite in user_favorites if favorite != fav_status]
    else:
        g.user.append(fav_status)
    db.session.commit()

    return redirect(f"/user/{g.user.id}")



@app.route('/gamestatus/new', methods=['GET', 'POST'])
def gamestatus_add():
    """Add a game status: if GET show form. If valid existing message, update message and redirect to user page."""
    check_user()

    form = GameStatusForm()

    if form.validate_on_submit():
        gstat = GameStatus(game_title = form.game_title.data, status = form.status.data)
        g.user.gamestatus.append(gstat)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")
    return render_template('gamestatus/new.html', form = form)

@app.route('/gamestatus/<int:gamestatus_id>', methods=['GET'])
def gamestatus_show(gamestatus_id):
    """Show a gamestatus"""

    gstat = GameStatus.query.get_or_404(gamestatus_id)
    user = g.user
    return render_template('gamestatus/show.html', gamestatus = gstat)

@app.route('/gamestatus/<int:gamestatus_id>/edit', methods=["GET", "POST"])
def edit_gamestatus(gamestatus_id):
    """Update gamestatus if it belongs to the user."""

    check_user()

    user = g.user
    gstat = GameStatus.query.get(gamestatus_id)
    form = GameStatusForm(obj=gstat)

    if form.validate_on_submit():
        gstat.game_title = form.game_title.data
        gstat.status = form.status.data

        db.session.commit()
        return redirect(f"/users/{user.id}")

    return render_template('gamestatus/edit.html', form = form, gamestatus_id = gstat.id)
        

@app.route('/gamestatus/<int:gamestatus_id>/delete', methods = ['POST'])
def gamestatus_destroy(gamestatus_id):
    """Delete a gamestatus"""
    check_user()

    gstat = GameStatus.query.get_or_404(gamestatus_id)
    if gstat.user_id != g.user.id:
        flash("Access unauthorized.", 'danger')
        return redirect("/")

    db.session.delete(gstat)
    db.session.commit()
    return redirect(f"/users/{g.user.id}")

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404