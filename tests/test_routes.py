import pytest

def test_catalogue_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Featured Movies" in res.data

def test_profile_requires_login(client):
    res = client.get("/profile")
    assert res.status_code == 302  # redirect to login

def test_invalid_movie_page(client):
    res = client.get("/movie/999999999")
    assert res.status_code == 404 or b"not found" in res.data.lower()
