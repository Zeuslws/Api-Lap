import uuid


def new_user():
    return {"username": "lab-" + uuid.uuid4().hex[:12], "password": "Pizza-2026"}


# Registering an already registered username is refused.
def test_duplicate_username_is_refused(api):
    user = new_user()
    assert api.post("/api/users", json=user).status_code == 201
    res = api.post("/api/users", json=user)
    assert res.status_code == 400
    assert res.json() == {"error": "username already taken"}


# A registered user cannot log in with an incorrect password.
def test_wrong_password_is_refused(api):
    user = new_user()
    assert api.post("/api/users", json=user).status_code == 201
    res = api.post("/api/users/token/login", json={**user, "password": "wrong-password"})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}


# An empty username is rejected with a specific validation message.
def test_empty_username_is_refused(api):
    res = api.post("/api/users", json={"username": "", "password": "Pizza-2026"})
    assert res.status_code == 400
    assert res.json() == {"error": "username field is empty"}
