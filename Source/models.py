from datetime import datetime
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from image import createImage
from faker import Faker


fake = Faker()

db = SQLAlchemy()

user_friend = db.Table('user_friend', 
    db.Column("friend_id", db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False),
    db.Column("user_id", db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False),
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    about = db.Column(db.String(500), nullable=True, default='Hey there, I am using Securitychat')
    publicKeyE = db.Column(db.String, nullable=False)
    publicKeyN = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(50), nullable=False)
    reg_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)


    friends = db.relationship("User",
        secondary = user_friend,
        primaryjoin = (id == user_friend.c.user_id),
        secondaryjoin = (id == user_friend.c.friend_id),
        backref = "friend_of",
    )


    messages = db.relationship('Message', backref='user')
    posts = db.relationship('Post', backref='user')

user_post = db.Table('user_post', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)
    send_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    attachement = db.Column(db.String(100), nullable=True)
    message = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Integer, nullable=True, default="sent")
    views = db.Column(db.Integer, nullable=True, default=0)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

def add_admin():
    for _ in range(1):
        names = "Administrator"
        user = User(
            name = names,
            email = "Administrator@gmail.com",
            password = generate_password_hash('12345'),
            publicKeyE = "XXXXXX",
            publicKeyN = "XXXXXX",
            image = createImage(names) 
        )
        db.session.add(user)
    db.session.commit()


def create_random_data():
    db.create_all()
    add_admin()
