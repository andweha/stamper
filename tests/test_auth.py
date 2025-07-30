import pytest

def test_register_login_logout(client):
    # Register
    res = client.post("/register", data={
        "username": "testuser",
        "password": "Password@123",
        "confirm_password": "Password@123"
    }, follow_redirects=True)
    assert b"Account created" in res.data

    # Login
    res = client.post("/login", data={
        "username": "testuser",
        "password": "Password@123"
    }, follow_redirects=True)
    assert b"Looking for the next thing" in res.data

    # Logout
    res = client.get("/logout", follow_redirects=True)
    assert b"Login" in res.data

def test_duplicate_username(client):
    client.post("/register", data={"username": "testuser", "password": "Abc@1234", "confirm_password": "Abc@1234"})
    res = client.post("/register", data={"username": "testuser", "password": "Abc@1234", "confirm_password": "Abc@1234"})
    assert b"Username already exists" in res.data
