import pytest
from app.models import db, User

def test_user_model(app):
    with app.app_context():
        user = User(username="abc", password="abcDEF@123")
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(username="abc").first() is not None
