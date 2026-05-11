from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random, string

db = SQLAlchemy()

def generate_unique_id():
    return 'NEX-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

friends = db.Table('friends',
    db.Column('user_id',   db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    nexchat_id    = db.Column(db.String(20), unique=True, nullable=False, default=generate_unique_id)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar        = db.Column(db.String(10), default='👤')
    photo         = db.Column(db.String(255), default=None)
    bio           = db.Column(db.String(200), default='')
    status        = db.Column(db.String(20), default='online')
    theme         = db.Column(db.String(10), default='dark')
    is_online     = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    friends_list = db.relationship('User', secondary=friends,
        primaryjoin=(friends.c.user_id == id),
        secondaryjoin=(friends.c.friend_id == id),
        lazy='dynamic')

    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

    def add_friend(self, user):
        if not self.is_friend(user):
            self.friends_list.append(user)
            user.friends_list.append(self)

    def remove_friend(self, user):
        if self.is_friend(user):
            self.friends_list.remove(user)
            user.friends_list.remove(self)

    def is_friend(self, user):
        return self.friends_list.filter(friends.c.friend_id == user.id).count() > 0

    def get_photo_url(self):
        if self.photo:
            return f'/static/uploads/{self.photo}'
        return None

    def to_dict(self):
        return {
            'id': self.id, 'nexchat_id': self.nexchat_id,
            'username': self.username, 'avatar': self.avatar,
            'photo': self.get_photo_url(), 'bio': self.bio,
            'status': self.status, 'is_online': self.is_online, 'theme': self.theme
        }


class Room(db.Model):
    __tablename__ = 'rooms'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), default='')
    is_private  = db.Column(db.Boolean, default=False)
    created_by  = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    members     = db.relationship('RoomMember', backref='room', lazy=True)


class RoomMember(db.Model):
    __tablename__ = 'room_members'
    id        = db.Column(db.Integer, primary_key=True)
    room_id   = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'messages'
    id              = db.Column(db.Integer, primary_key=True)
    sender_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_name       = db.Column(db.String(100), nullable=False)
    content         = db.Column(db.Text, nullable=False)
    msg_type        = db.Column(db.String(20), default='text')
    disappear_after = db.Column(db.Integer, default=0)
    seen_at         = db.Column(db.DateTime, default=None)
    is_deleted      = db.Column(db.Boolean, default=False)
    timestamp       = db.Column(db.DateTime, default=datetime.utcnow)
    reactions       = db.relationship('Reaction', backref='message', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        reaction_map = {}
        for r in self.reactions:
            reaction_map[r.emoji] = reaction_map.get(r.emoji, 0) + 1
        return {
            'id': self.id, 'sender_id': self.sender_id,
            'sender': self.sender.username,
            'avatar': self.sender.photo and f'/static/uploads/{self.sender.photo}' or self.sender.avatar,
            'is_photo_avatar': bool(self.sender.photo),
            'room_name': self.room_name, 'message': self.content,
            'msg_type': self.msg_type,
            'disappear_after': self.disappear_after,
            'is_deleted': self.is_deleted,
            'timestamp': self.timestamp.strftime('%H:%M'),
            'reactions': reaction_map
        }


class Reaction(db.Model):
    __tablename__ = 'reactions'
    id         = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emoji      = db.Column(db.String(10), nullable=False)
    __table_args__ = (db.UniqueConstraint('message_id', 'user_id'),)