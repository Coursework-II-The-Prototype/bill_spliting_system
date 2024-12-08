import os
import pytest
import random
from tinydb import TinyDB
from unittest.mock import patch

current_dir = os.path.dirname(__file__)
mock_dir = f"{current_dir}/databases"

all_households = TinyDB("databases/household.json").all()


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", lambda _: mock_dir)
    from utils import get_db
    from src.app import main

    order_db = get_db("order")
    order_db.truncate()

    return {
        "main": main,
        "order_db": order_db,
    }


def test_app_exit(mock_db, capsys):
    main = mock_db["main"]

    users = random.choice(all_households)["user_ids"]
    user = random.choice(users)

    with patch("builtins.input", side_effect=[user, "q"]):
        main()
    capsys.readouterr()


def test_app_new_order(mock_db, capsys):
    main = mock_db["main"]
    order_db = mock_db["order_db"]

    users = random.choice(all_households)["user_ids"]
    user = random.choice(users)

    with patch("builtins.input", side_effect=[user, "n", "q"]):
        main()
    capsys.readouterr()

    assert len(order_db.all()) == 1

    # basic actions
    with patch(
        "builtins.input",
        side_effect=[
            user,
            "a",
            "1",
            "1",
            "yes",
            "e",
            "1",
            "2",
            "no",
            "p",
            "r",
            "yes",
            "q",
        ],
    ):
        main()
    capsys.readouterr()

    order = order_db.all()[0]
    for u in order["users"]:
        if u["user_id"] == user:
            assert u["isReady"]

    assert len(order["items"]) == 1
    item = order["items"][0]
    assert item["item_id"] == "1"
    assert item["isPublic"] == False
    assert item["quantity"] == 2
