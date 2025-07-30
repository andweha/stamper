import pytest
from flask import url_for

def test_comment_form_validation(client, app):
    with app.app_context():
        res = client.post("/movie/123", data={
            "timestamp": "00:02:10",
            "content": "Nice!",
            "gif_url": ""
        }, follow_redirects=True)
        assert res.status_code in [200, 302]

def login(client, username="tester", password="Password@123"):
    client.post("/register", data={"username": username, "password": password, "confirm_password": password})
    client.post("/login", data={"username": username, "password": password})

def test_comment_submission(client, app):
    with app.app_context():
        login(client)
        res = client.post("/movie/123", data={
            "timestamp": "00:00:05",
            "content": "This scene is great!",
            "gif_url": "https://media.tenor.com/fake.gif"
        }, follow_redirects=True)
        assert b"This scene is great!" in res.data
        assert b'<img src="https://media.tenor.com/fake.gif"' in res.data
