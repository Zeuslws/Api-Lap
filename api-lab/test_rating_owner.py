# A different user cannot read a rating, and the owner's copy stays unchanged.
def test_other_user_cannot_read(api, auth, other_auth, rating, record_property):
    path = f"/api/ratings/{rating['id']}"
    res = api.get(path, headers=other_auth)
    record_property("other_user_status", res.status_code)
    assert 400 <= res.status_code <= 499
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == rating


# A different user cannot change a rating, and the original stars remain saved.
def test_other_user_cannot_update(api, auth, other_auth, rating, record_property):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": 5}, headers=other_auth)
    record_property("other_user_status", res.status_code)
    assert 400 <= res.status_code <= 499
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == rating


# A different user cannot delete a rating, and its owner can still read it.
def test_other_user_cannot_delete(api, auth, other_auth, rating, record_property):
    path = f"/api/ratings/{rating['id']}"
    res = api.delete(path, headers=other_auth)
    record_property("other_user_status", res.status_code)
    assert 400 <= res.status_code <= 499
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == rating
