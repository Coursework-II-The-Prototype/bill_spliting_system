import os
import pytest
from unittest.mock import patch
from tinydb import Query

QUERY = Query()

current_dir = os.path.dirname(__file__)
mock_dir = f"{current_dir}/databases"


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", lambda _: mock_dir)
    from utils import get_db
    from src.shopping import (
        get_order,
        get_personal_table,
        get_public_table,
        insert,
    )

    order_db = get_db("order")
    order_db.truncate()

    return {
        "order_db": order_db,
        "get_order": get_order,
        "get_personal_table": get_personal_table,
        "get_public_table": get_public_table,
        "insert": insert,
    }


def test_supermarket_database():
    from utils import get_db, check_fields, type_check

    supermarket_db = get_db("supermarket")
    all_products = supermarket_db.all()
    check_fields(
        all_products, ["item_id", "name", "price"], "supermarket database"
    )
    for p in all_products:
        type_check(p["item_id"], str, "`item_id`")
        type_check(p["name"], str, "`name`")
        type_check(p["price"], float, "`price`")


def test_get_order(mock_db):
    order_db = mock_db["order_db"]
    get_order = mock_db["get_order"]

    order_db.insert({"order_id": "-"})
    order_db.insert({"order_id": ":)"})
    assert not get_order("1")

    id = "myorder"
    order_db.insert({"order_id": id})
    order_db.insert({"order_id": ":("})
    assert get_order(id)["order_id"] == id


def test_print(mock_db):
    order_db = mock_db["order_db"]
    get_order = mock_db["get_order"]
    get_personal_table = mock_db["get_personal_table"]
    get_public_table = mock_db["get_public_table"]

    order_db.insert(
        {
            "order_id": "1",
            "users": ["1", "2"],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "1",
                },
                {
                    "item_id": "3",
                    "quantity": 4,
                    "isPublic": True,
                    "user_id": "1",
                },
                {
                    "item_id": "2",
                    "quantity": 3,
                    "isPublic": False,
                    "user_id": "2",
                },
                {
                    "item_id": "4",
                    "quantity": 2,
                    "isPublic": True,
                    "user_id": "2",
                },
            ],
            "isReset": False,
        }
    )
    order = get_order("1")

    t1 = get_personal_table(order["items"], "1")
    assert len(t1) == 1
    assert t1[0][0] == "a"
    assert t1[0][1] == 4
    assert t1[0][2] == 1

    t2 = get_public_table(order["items"])
    assert len(t2) == 2
    assert t2[0][0] == "c"
    assert t2[0][1] == 3
    assert t2[0][2] == 4
    assert t2[0][3] == "1"

    assert t2[1][0] == "d"
    assert t2[1][1] == 1.5
    assert t2[1][2] == 2
    assert t2[1][3] == "2"


def test_create_new_order(mock_db):
    order_db = mock_db["order_db"]
    insert = mock_db["insert"]

    user = "user"
    order_db.insert(
        {
            "order_id": "1",
            "users": [{"user_id": user, "isReady": True}],
            "items": [],
            "isReset": False,
        }
    )
    item_id = "2"
    amount = "4"
    public = "yes"
    with patch("builtins.input", side_effect=[item_id, amount, public]):
        insert(user, "1")

    order = order_db.all()[0]
    assert len(order["items"]) == 1
    item = order["items"][0]
    assert item["item_id"] == item_id
    assert item["quantity"] == int(amount)
    assert item["isPublic"] == True
    assert item["user_id"] == user
