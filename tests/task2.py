import os
import pytest
from unittest.mock import patch
from utils import check_fields, type_check
from tinydb import Query

QUERY = Query()

current_dir = os.path.dirname(__file__)
mock_dir = f"{current_dir}/databases"


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", lambda _: mock_dir)
    from utils import get_db
    from src.task2 import (
        get_order,
        get_personal_table,
        get_public_table,
        print_order,
        insert,
        update,
        reset_ready,
        setReady,
    )

    order_db = get_db("order")
    order_db.truncate()

    return {
        "order_db": order_db,
        "get_order": get_order,
        "get_personal_table": get_personal_table,
        "get_public_table": get_public_table,
        "print_order": print_order,
        "insert": insert,
        "update": update,
        "reset_ready": reset_ready,
        "setReady": setReady,
    }


def test_supermarket_database():
    from utils import get_db

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


def test_get_table(mock_db):
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
                    "user_id": "user1",
                },
                {
                    "item_id": "3",
                    "quantity": 4,
                    "isPublic": True,
                    "user_id": "user1",
                },
                {
                    "item_id": "2",
                    "quantity": 3,
                    "isPublic": False,
                    "user_id": "user2",
                },
                {
                    "item_id": "4",
                    "quantity": 2,
                    "isPublic": True,
                    "user_id": "user2",
                },
            ],
            "isReset": False,
        }
    )
    order = get_order("1")

    t1 = get_personal_table(order["items"], "user1")
    assert len(t1) == 1
    assert t1[0][0] == "a"
    assert t1[0][1] == 4
    assert t1[0][2] == 1

    t2 = get_public_table(order["items"])
    assert len(t2) == 2
    assert t2[0][0] == "c"
    assert t2[0][1] == 3
    assert t2[0][2] == 4
    assert t2[0][3] == "user1"

    assert t2[1][0] == "d"
    assert t2[1][1] == 1.5
    assert t2[1][2] == 2
    assert t2[1][3] == "user2"


def test_print_order(mock_db):
    order_db = mock_db["order_db"]
    print_order = mock_db["print_order"]

    order_db.insert(
        {
            "order_id": "1",
            "users": ["1", "2"],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user2",
                },
            ],
            "isReset": False,
        }
    )
    assert not print_order("user1", "1")

    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": ["1", "2"],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                },
            ],
            "isReset": False,
        }
    )
    assert print_order("user1", "1")

    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": ["1", "2"],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": True,
                    "user_id": "user2",
                },
            ],
            "isReset": False,
        }
    )
    assert print_order("user1", "1")


def test_insert(mock_db, capsys):
    order_db = mock_db["order_db"]
    insert = mock_db["insert"]

    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [],
            "isReset": False,
        }
    )

    inputs = [
        {"u": "user1", "i": "1", "a": "2", "p": "no"},
        {"u": "user3", "i": "2", "a": "4", "p": "yes"},
        {"u": "user2", "i": "3", "a": "6", "p": "no"},
    ]
    for index, inp in enumerate(inputs):
        with patch(
            "builtins.input", side_effect=[inp["i"], inp["a"], inp["p"]]
        ):
            assert insert(inp["u"], "1")
        capsys.readouterr()

        order = order_db.all()[0]
        item = order["items"][-1]
        assert item["item_id"] == inp["i"]
        assert item["quantity"] == int(inp["a"])
        assert item["isPublic"] == (inp["p"] == "yes")
        assert item["user_id"] == inp["u"]
        if index < 1:
            assert (
                order["isReset"] == False
            ), "isReset should be unchanged if order is not public"
        else:
            assert order["isReset"] == True

    order = order_db.all()[0]
    items = order["items"]
    assert len(items) == 3

    check_fields(
        items, ["item_id", "quantity", "isPublic", "user_id"], "`items`"
    )

    for item in items:
        type_check(item["item_id"], str, "`item_id`")
        type_check(item["quantity"], int, "`quantity`")
        type_check(item["isPublic"], bool, "`isPublic`")
        type_check(item["user_id"], str, "`user_id`")

    # check invalid input
    with patch("builtins.input", side_effect=["99"]):
        assert not insert("user1", "1")
    capsys.readouterr()

    with patch("builtins.input", side_effect=["1", "0"]):
        assert not insert("user1", "1")
    capsys.readouterr()

    # check same id increment
    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                }
            ],
            "isReset": False,
        }
    )
    with patch("builtins.input", side_effect=["1", "2", "yes"]):
        assert insert("user1", "1")
    capsys.readouterr()

    assert len(order_db.all()[0]["items"]) == 2
    assert order_db.all()[0]["items"][1]["quantity"] == 2

    with patch("builtins.input", side_effect=["1", "2", "no"]):
        assert insert("user1", "1")
    capsys.readouterr()

    assert len(order_db.all()[0]["items"]) == 2
    assert order_db.all()[0]["items"][0]["quantity"] == 3


def test_update(mock_db, capsys):
    order_db = mock_db["order_db"]
    update = mock_db["update"]

    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                },
                {
                    "item_id": "1",
                    "quantity": 2,
                    "isPublic": False,
                    "user_id": "user2",
                },
                {
                    "item_id": "2",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                },
            ],
            "isReset": False,
        }
    )

    with patch("builtins.input", side_effect=["1", "2", "no"]):
        assert update("user1", "1")
    capsys.readouterr()

    item = order_db.all()[0]["items"][0]
    assert item["item_id"] == "1"
    assert item["quantity"] == 2
    assert item["isPublic"] == False
    assert item["user_id"] == "user1"
    assert order_db.all()[0]["isReset"] == False

    with patch("builtins.input", side_effect=["1", "4", "yes"]):
        assert update("user2", "1")
    capsys.readouterr()

    item = order_db.all()[0]["items"][1]
    assert item["item_id"] == "1"
    assert item["quantity"] == 4
    assert item["isPublic"] == True
    assert item["user_id"] == "user2"
    assert order_db.all()[0]["isReset"] == True

    with patch("builtins.input", side_effect=["99", "1", "yes"]):
        assert not update("user1", "1")
    capsys.readouterr()

    # exit early if empty
    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [],
            "isReset": False,
        }
    )
    assert not update("user1", "1")
    capsys.readouterr()

    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": True,
                    "user_id": "user2",
                },
            ],
            "isReset": False,
        }
    )
    assert not update("user1", "1")
    capsys.readouterr()

    # check and same public personal order
    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                },
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": True,
                    "user_id": "user1",
                },
                {
                    "item_id": "2",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                },
                {
                    "item_id": "2",
                    "quantity": 1,
                    "isPublic": True,
                    "user_id": "user1",
                },
            ],
            "isReset": False,
        }
    )

    with patch("builtins.input", side_effect=["1", "public", "2", "yes"]):
        assert update("user1", "1")
    capsys.readouterr()

    items = order_db.all()[0]["items"]
    assert items[0]["quantity"] == 1
    assert items[1]["quantity"] == 2

    # check isPublic change increment
    with patch("builtins.input", side_effect=["1", "public", "3", "no"]):
        assert update("user1", "1")
    capsys.readouterr()
    with patch("builtins.input", side_effect=["2", "personal", "2", "yes"]):
        assert update("user1", "1")
    capsys.readouterr()

    items = order_db.all()[0]["items"]
    assert len(items) == 2
    assert items[0]["quantity"] == 4
    assert items[1]["quantity"] == 3

    # check amount 0 remove order
    order_db.truncate()
    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                }
            ],
            "isReset": False,
        }
    )

    with patch("builtins.input", side_effect=["1", "0"]):
        assert update("user1", "1")
    capsys.readouterr()

    items = order_db.all()[0]["items"]
    assert len(items) == 0


def test_reset_ready(mock_db):
    order_db = mock_db["order_db"]
    reset_ready = mock_db["reset_ready"]

    order_db.insert(
        {
            "order_id": "1",
            "users": [
                {"user_id": "user1", "isReady": True},
            ],
            "items": [],
            "isReset": False,
        }
    )
    order_db.insert(
        {
            "order_id": "2",
            "users": [
                {"user_id": "user2", "isReady": True},
                {"user_id": "user3", "isReady": False},
                {"user_id": "user4", "isReady": True},
            ],
            "items": [],
            "isReset": False,
        },
    )
    reset_ready("2")
    for u in order_db.all()[1]["users"]:
        assert u["isReady"] == False
    order_db.all()[0]["isReset"] == False
    order_db.all()[1]["isReset"] == True


def test_setReady(mock_db):
    order_db = mock_db["order_db"]
    setReady = mock_db["setReady"]

    order_db.insert(
        {
            "order_id": "1",
            "users": [
                {"user_id": "user1", "isReady": False},
                {"user_id": "user2", "isReady": False},
            ],
            "items": [],
            "isReset": False,
        }
    )

    with patch("builtins.input", side_effect=["no"]):
        setReady("user1", "1")

    assert order_db.all()[0]["users"][0]["isReady"] == False

    with patch("builtins.input", side_effect=["yes"]):
        setReady("user1", "1")

    assert order_db.all()[0]["users"][0]["isReady"] == True
    assert order_db.all()[0]["users"][1]["isReady"] == False

    with patch("builtins.input", side_effect=["no"]):
        setReady("user1", "1")

    assert order_db.all()[0]["users"][0]["isReady"] == False
    assert order_db.all()[0]["users"][1]["isReady"] == False
