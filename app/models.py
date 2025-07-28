from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_pic_url = db.Column(db.String(200), nullable=True, default=None)

    def __repr__(self):
        return f"User('{self.username}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    episode_id = db.Column(db.Integer, nullable=False)
    gif_url = db.Column(db.Text)

    user = db.relationship("User", backref="comments")

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'media_id'),)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    media_type = db.Column(db.String(50), nullable=False) # movie,tv,or anime
    media_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    poster_url = db.Column(db.String(255))
    watched_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="history_entries")

    def __repr__(self):
        return f"History(User: {self.user_id}, Media: {self.title}, Type: {self.media_type}, Watched: {self.watched_at})"