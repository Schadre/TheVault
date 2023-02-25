from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
import secrets

login_manager = LoginManager()
ma = Marshmallow()
db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    first = db.Column(db.String(150), nullable=True, default='')
    last = db.Column(db.String(150), nullable=True, default='')
    username = db.Column(db.String(150), nullable=True, default='')
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String, nullable=True, default='')
    g_auth_verify = db.Column(db.Boolean, default=False)
    token = db.Column(db.String, default='', unique=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    books = db.relationship('Book', backref='user', lazy=True)

    def __init__(self, first='', last='', username='', email='', password='', token='', g_auth_verify=False):
        self.id = self.set_id()
        self.first = first
        self.last = last
        self.username = username
        self.password = self.set_password(password)
        self.email = email
        self.token = self.set_token(24)
        self.g_auth_verify = g_auth_verify

    def set_token(self, length):
        return secrets.token_hex(length)

    def set_id(self):
        return str(uuid.uuid4())

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash

    def __repr__(self):
        return f'User {self.email} also know as {self.username} has been added to the database'

class Book(db.Model):
    isbn = db.Column(db.String(150), primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    cover_image_url = db.Column(db.String(225), nullable=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False, default='')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'Book {self.title} by {self.author} has been added to the database'
    

    def __init__(self, title, author, description, cover_image_url, isbn, user_id):
        self.title = title
        self.author = author
        self.description = description
        self.cover_image_url = cover_image_url
        self.isbn = isbn
        self.user_id = user_id

class BookSchema(ma.Schema):
    class Meta:
        fields = ['isbn','title', 'author', 'description', 'cover_image_url','user_id']

book_schema = BookSchema()
books_schema = BookSchema(many=True)