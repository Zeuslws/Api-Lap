import pytest

STARS_ERROR = "number of stars must be between 1 and 5 (inclusive)"


# Base choice uses integer 3, an existing pizza, and the owner's valid token.
def test_base_choice_is_saved(api, auth, pizza_id):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=auth)
    assert res.status_code == 201
    assert res.json()["stars"] == 3
    assert res.json()["pizza_id"] == pizza_id


# C1 non-base blocks reject star counts below 1 and above 5.
@pytest.mark.parametrize("stars", [0, 6])
def test_stars_out_of_range(api, auth, pizza_id, stars):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": stars}, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": STARS_ERROR}


# C2 rejects decimal and text values while the other inputs remain valid.
@pytest.mark.parametrize("stars, error", [
    (3.5, "json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int"),
    ("3", "json: cannot unmarshal string into Go struct field Rating.stars of type int"),
], ids=["decimal", "text"])
def test_invalid_star_type(api, auth, pizza_id, stars, error):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": stars}, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": error}


# C2's missing block rejects a request without the stars field.
def test_missing_stars(api, auth, pizza_id):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id}, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": STARS_ERROR}


# C3 rejects a nonexistent pizza while the stars and token stay at base.
def test_nonexistent_pizza(api, auth):
    res = api.post("/api/ratings", json={"pizza_id": 999999999, "stars": 3}, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": "pizza ID 999999999 not found"}


# C4 rejects missing and wrong-length tokens with otherwise valid inputs.
@pytest.mark.parametrize("header", [{}, {"Authorization": "token short"}], ids=["none", "short"])
def test_invalid_token(api, auth, pizza_id, header):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=header)
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
