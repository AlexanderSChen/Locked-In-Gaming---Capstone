from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for signing up users"""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min = 6)])

class LoginForm(FlaskForm):
    """Form for logging in users"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for logged in user to edit information"""


    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    profile_picture = StringField('Profile Picture')
    banner_picture = StringField('Banner Picture')
    bio = StringField('Bio')
    location = StringField('Location')

    password = PasswordField('Password', validators=[Length(min = 6)])

class GameStatusForm(FlaskForm):
    """Form for user to update game status"""
    
    game_title = StringField('Game Title', validators=[DataRequired()])
    status = StringField('How do you feel about the game?', validators=[DataRequired()])