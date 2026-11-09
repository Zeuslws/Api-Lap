# A new rating returns its generated id, requested stars and pizza.
def test_create_rating(api, auth, pizza_id):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 5}, headers=auth)
    assert res.status_code == 201
    body = res.json()
    assert body["stars"] == 5
    assert body["pizza_id"] == pizza_id
    assert type(body["id"]) is int


# The owner can read back the complete saved rating.
def test_read_rating(api, auth, rating):
    res = api.get(f"/api/ratings/{rating['id']}", headers=auth)
    assert res.status_code == 200
    assert res.json() == rating


# Updating a rating returns the requested new star count.
def test_update_rating(api, auth, rating):
    res = api.put(f"/api/ratings/{rating['id']}", json={"stars": 4}, headers=auth)
    assert res.status_code == 200
    assert res.json()["stars"] == 4


# Deleting a rating returns no content and makes it unavailable.
def test_delete_rating(api, auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.delete(path, headers=auth)
    assert res.status_code == 204
    assert res.content == b""
    res = api.get(path, headers=auth)
    assert res.status_code == 404
