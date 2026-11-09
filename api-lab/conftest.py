import uuid

import pytest
import requests

SITE = "https://quickpizza.grafana.com"


class QuickPizza(requests.Session):
    """Keep load-balancer cookies and prepend the API host."""

    def request(self, method, url, *args, **kwargs):
        kwargs.setdefault("timeout", 30)
        return super().request(method, SITE + url, *args, **kwargs)


@pytest.fixture(scope="session")
def api():
    with QuickPizza() as session:
        yield session


def log_in_new_user(api):
    user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201, res.text
    res = api.post("/api/users/token/login", json=user)
    assert res.status_code == 200, res.text
    return {"Authorization": "token " + res.json()["token"]}


@pytest.fixture
def auth(api):
    header = log_in_new_user(api)
    yield header
    # Remove only this test user's ratings, including unexpectedly accepted inputs.
    res = api.get("/api/ratings", headers=header)
    assert res.status_code == 200, res.text
    for saved in res.json()["ratings"]:
        deleted = api.delete(f"/api/ratings/{saved['id']}", headers=header)
        assert deleted.status_code == 204, deleted.text


@pytest.fixture
def pizza_id(api, auth):
    res = api.post("/api/pizza", json={}, headers=auth)
    assert res.status_code == 200, res.text
    return res.json()["pizza"]["id"]


@pytest.fixture
def rating(api, auth, pizza_id):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=auth)
    assert res.status_code == 201, res.text
    # The auth fixture removes remaining ratings after the test, even on failure.
    return res.json()


@pytest.fixture
def other_auth(api):
    return log_in_new_user(api)
