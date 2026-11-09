import pytest

STARS_ERROR = "number of stars must be between 1 and 5 (inclusive)"


# Boundary updates save 1 and 5, reject 0 and 6, and preserve rejected ratings.
@pytest.mark.parametrize("stars, expected_status", [(0, 400), (1, 200), (5, 200), (6, 400)])
def test_update_star_boundaries(api, auth, rating, stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == expected_status
    if expected_status == 200:
        assert res.json()["stars"] == stars
    else:
        assert res.json() == {"error": STARS_ERROR}
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    expected = {**rating, "stars": stars} if expected_status == 200 else rating
    assert saved.json() == expected
