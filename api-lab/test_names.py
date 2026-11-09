# The names endpoint returns JSON containing Margherita.
def test_names_are_listed(api):
    res = api.get("/api/names")
    assert res.status_code == 200
    assert "application/json" in res.headers["Content-Type"]
    assert "Margherita" in res.json()["names"]
