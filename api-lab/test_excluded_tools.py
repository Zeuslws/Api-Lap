import pytest


# Excluding zero, one or two tools must leave an allowed tool in the pizza.
@pytest.mark.parametrize("excluded", [[], ["Knife"], ["Scissors"], ["Knife", "Scissors"]],
                         ids=["zero", "one-knife", "one-scissors", "two"])
def test_excluded_tool_is_not_used(api, auth, excluded):
    res = api.post("/api/pizza", json={"excludedTools": excluded}, headers=auth)
    assert res.status_code == 200
    assert res.json()["pizza"]["tool"] not in excluded


# An impossible restriction must return 400 with a nonempty JSON error.
@pytest.mark.xfail(reason="Defect 1: excluding all tools returns 500 with an empty body", strict=True)
def test_excluding_all_tools_is_bad_request(api, auth):
    res = api.post("/api/pizza", json={"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}, headers=auth)
    assert res.status_code == 400
    body = res.json()
    assert isinstance(body.get("error"), str) and body["error"].strip()
