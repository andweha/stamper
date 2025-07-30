import pytest

def test_api_search(client):
    res = client.get("/api/search?q=Inception")
    assert res.status_code == 200
    assert res.is_json

def test_comment_timestamps_api(client):
    res = client.get("/api/comments/123")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
