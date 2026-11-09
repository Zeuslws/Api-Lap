# A vegetarian recommendation has a name and only vegetarian ingredients.
def test_vegetarian_pizza(api):
    res = api.post("/api/pizza", json={"mustBeVegetarian": True},
                   headers={"Authorization": "token abcdef0123456789"})
    assert res.status_code == 200
    pizza = res.json()["pizza"]
    assert pizza["name"]
    assert pizza["ingredients"]
    for ingredient in pizza["ingredients"]:
        assert ingredient["vegetarian"] is True, ingredient["name"]


# Requests without a token are refused with an authentication error.
def test_pizza_without_token_is_refused(api):
    res = api.post("/api/pizza", json={"mustBeVegetarian": True})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
