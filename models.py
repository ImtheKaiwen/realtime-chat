from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import hmac
import datetime

db = SQLAlchemy()

user_group = db.Table('user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    groups = db.relationship('Group', secondary=user_group, back_populates='members')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if self.password.startswith(('scrypt:', 'pbkdf2:')):
            return check_password_hash(self.password, password)

        # Backward-compatible upgrade path for legacy plaintext rows.
        if hmac.compare_digest(self.password, password):
            self.set_password(password)
            return True
        return False

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    members = db.relationship('User', secondary=user_group, back_populates='groups')
    messages = db.relationship('Message', backref='group', lazy=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    author = db.relationship('User', backref='messages')

