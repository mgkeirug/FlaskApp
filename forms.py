from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo, Optional
from FlaskApp.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):   #im not using this
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class StatsForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    height = FloatField('Height', validators=[Optional()])
    height_feet = FloatField('Height', validators=[Optional()])
    height_inches = FloatField('Height(in)', validators=[Optional()])
    starting_weight = FloatField('Starting Weight', validators=[Optional()])
    current_weight = FloatField('Current Weight', validators=[Optional()])
    goal_weight = FloatField('Goal Weight', validators=[Optional()])
    starting_bf_percentage = FloatField('Starting Bodyfat %', validators=[Optional()])
    current_bf_percentage = FloatField('Current Bodyfat %', validators=[Optional()])
    goal_bf_percentage = FloatField('Goal Bodyfat %', validators=[Optional()])
    submit = SubmitField('Submit')

class UpdateForm(FlaskForm):
    current_weight = FloatField('Current Weight', validators=[Optional()])
    current_bf_percentage = FloatField('Current Bodyfat %', validators=[Optional()])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')