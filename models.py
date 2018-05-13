from werkzeug.security import generate_password_hash, check_password_hash
from FlaskApp import db, login
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
from time import time
import jwt
from FlaskApp import app

##remember to migrate the db after you edit any of these!!  delete and redo if you have to

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic') #dont think i use
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(64), default='New User')
    height = db.Column(db.Float(64), default=0)
    starting_weight = db.Column(db.Float(64), default=0)
    current_weight = db.Column(db.Float(64), default=0)
    goal_weight = db.Column(db.Float(64), default=0)
    starting_bf_percentage = db.Column(db.Float(64), default=0)
    current_bf_percentage = db.Column(db.Float(64), default=0)
    goal_bf_percentage = db.Column(db.Float(64), default=0)
    total_weight_lost = db.Column(db.Float(64), default=0)
    total_weight_gained = db.Column(db.Float(64), default=0)
    starting_fat_pounds = db.Column(db.Float(64), default=0)
    current_fat_pounds = db.Column(db.Float(64), default=0)
    goal_fat_pounds = db.Column(db.Float(64), default=0)
    fat_lost = db.Column(db.Float(64), default=0)
    starting_lean_bodymass = db.Column(db.Float(64), default=0)
    current_lean_bodymass = db.Column(db.Float(64), default=0)
    goal_lean_bodymass = db.Column(db.Float(64), default=0)
    bmi = db.Column(db.Float(64), default=0)
    nonfat_lost = db.Column(db.Float(64), default=0)
    goal_fat_loss = db.Column(db.Float(64), default=0)
    goal_weight_auto = db.Column(db.Float(64), default=0)
    goal_fat_loss_auto = db.Column(db.Float(64), default=0)
    goal_muscle_gain = db.Column(db.Float(64), default=0)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.String(64), index=True) #, unique=True <--used to be in there with index=True
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) #not sure i need this bc of timestamp
    name = db.Column(db.String(64))
    height = db.Column(db.Float(64))
    starting_weight = db.Column(db.Float(64))
    current_weight = db.Column(db.Float(64))
    goal_weight = db.Column(db.Float(64))
    starting_bf_percentage = db.Column(db.Float(64))
    current_bf_percentage = db.Column(db.Float(64))
    goal_bf_percentage = db.Column(db.Float(64))
    total_weight_lost = db.Column(db.Float(64))
    total_weight_gained = db.Column(db.Float(64))
    starting_fat_pounds = db.Column(db.Float(64))
    current_fat_pounds = db.Column(db.Float(64))
    goal_fat_pounds = db.Column(db.Float(64))
    fat_lost = db.Column(db.Float(64))
    starting_lean_bodymass = db.Column(db.Float(64))
    current_lean_bodymass = db.Column(db.Float(64))
    goal_lean_bodymass = db.Column(db.Float(64))
    bmi = db.Column(db.Float(64))
    nonfat_lost = db.Column(db.Float(64))
    goal_fat_loss = db.Column(db.Float(64))
    goal_weight_auto = db.Column(db.Float(64))
    goal_fat_loss_auto = db.Column(db.Float(64))
    goal_muscle_gain = db.Column(db.Float(64))

    def __repr__(self):
        return '<Post {}>'.format(self.id) #not sure what self.? should be
