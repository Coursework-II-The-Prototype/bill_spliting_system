import os
import pytest
from unittest.mock import patch
from hypothesis import given, strategies as st
from utils import check_db
from deepdiff import DeepDiff
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
        calc_bill,
        insert,
        update,
        reset_ready,
        setReady,
    )

    order_db = get_db("order")
    supermarket_db = get_db("supermarket")
    order_db.truncate()

    return {
        "order_db": order_db,
        "supermarket_db": supermarket_db,
        "get_order": get_order,
        "get_personal_table": get_personal_table,
        "get_public_table": get_public_table,
        "print_order": print_order,
        "calc_bill": calc_bill,
        "insert": insert,
        "update": update,
        "reset_ready": reset_ready,
        "setReady": setReady,
    }


def test_supermarket_database():
    from utils import get_db

    supermarket_db = get_db("supermarket")
    check_db(
        supermarket_db,
        {
            "item_id": {"type": "string"},
            "name": {"type": "string"},
            "price": {"type": "number"},
        },
    )


def test_get_order(mock_db):
    order_db = mock_db["order_db"]
    get_order = mock_db["get_order"]

    @given(st.text())
    def get_rand(ord):
        get_order(ord)

    get_rand()

    assert not get_order("order1")

    id = "myorder"
    order_db.insert({"order_id": id})
    assert get_order(id)["order_id"] == id

    get_rand()


def test_get_table(mock_db):
    order_db = mock_db["order_db"]
    get_order = mock_db["get_order"]
    get_personal_table = mock_db["get_personal_table"]
    get_public_table = mock_db["get_public_table"]

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
    assert DeepDiff(t1, [["a", 10, 1]]) == {}

    t2 = get_public_table(order["items"])
    assert DeepDiff(t2, [["c", 30, 4, "user1"], ["d", 40, 2, "user2"]]) == {}


def test_print_order(mock_db):
    order_db = mock_db["order_db"]
    print_order = mock_db["print_order"]

    base_items = [
        {
            "item_id": "1",
            "quantity": 1,
            "isPublic": False,
            "user_id": "user2",
        }
    ]
    order_db.insert(
        {
            "order_id": "1",
            "users": [],
            "items": base_items,
            "isReset": False,
        }
    )

    assert not print_order("user1", "1")

    base_items[0]["user_id"] = "user1"
    order_db.update(
        {"items": base_items},
        QUERY.order_id == "1",
    )
    assert print_order("user1", "1")

    base_items[0]["isPublic"] = True
    base_items[0]["user_id"] = "user2"
    order_db.update(
        {"items": base_items},
        QUERY.order_id == "1",
    )
    assert print_order("user1", "1")


def test_calc_bill(mock_db):
    order_db = mock_db["order_db"]
    calc_bill = mock_db["calc_bill"]

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
                    "item_id": "2",
                    "quantity": 1,
                    "isPublic": True,
                    "user_id": "user2",
                },
            ],
            "isReset": False,
        }
    )

    assert calc_bill("user1", order_db.all()[0]["items"]) == 17.5


def test_insert(mock_db):
    order_db = mock_db["order_db"]
    supermarket_db = mock_db["supermarket_db"]
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
        ["user1", "1", "2", "no"],
        ["user3", "2", "4", "yes"],
        ["user2", "3", "6", "no"],
    ]
    for index, enter in enumerate(inputs):
        with patch(
            "builtins.input", side_effect=[enter[1], enter[2], enter[3]]
        ):
            assert insert(enter[0], "1")

    items = order_db.all()[0]["items"]
    assert len(items) == 3
    assert (
        DeepDiff(
            items,
            list(
                map(
                    lambda enter: {
                        "item_id": enter[1],
                        "quantity": int(enter[2]),
                        "isPublic": enter[3] == "yes",
                        "user_id": enter[0],
                    },
                    inputs,
                )
            ),
            ignore_order=True,
        )
        == {}
    )

    # check same id increment
    order_db.update(
        {
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                }
            ],
        },
        QUERY.order_id == "1",
    )
    with patch("builtins.input", side_effect=["1", "2", "yes"]):
        assert insert("user1", "1")

    with patch("builtins.input", side_effect=["1", "2", "no"]):
        assert insert("user1", "1")

    assert (
        DeepDiff(
            list(order_db.all()[0]["items"]),
            [
                {
                    "item_id": "1",
                    "quantity": 3,
                    "isPublic": False,
                    "user_id": "user1",
                },
                {
                    "item_id": "1",
                    "quantity": 2,
                    "isPublic": True,
                    "user_id": "user1",
                },
            ],
        )
        == {}
    )

    @given(st.text(), st.characters(), st.text())
    def rand_inp(s1, s2, s3):
        with patch("builtins.input", side_effect=[s1, s2, s3]):
            assert (
                insert("user1", "1")
                == (len(supermarket_db.search(QUERY.item_id == s1)) > 0)
                & s2.isdigit()
            )

    rand_inp()


def test_update(mock_db):
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

    with patch("builtins.input", side_effect=["1", "4", "yes"]):
        assert update("user2", "1")

    assert (
        DeepDiff(
            list(order_db.all()[0]["items"]),
            [
                {
                    "item_id": "1",
                    "quantity": 2,
                    "isPublic": False,
                    "user_id": "user1",
                },
                {
                    "item_id": "1",
                    "quantity": 4,
                    "isPublic": True,
                    "user_id": "user2",
                },
                {
                    "item_id": "2",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "user1",
                },
            ],
        )
        == {}
    )

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

    order_db.update(
        {
            "items": [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": True,
                    "user_id": "user2",
                },
            ],
        },
        QUERY.order_id == "1",
    )
    assert not update("user1", "1")

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

    # check isPublic change increment
    with patch("builtins.input", side_effect=["1", "public", "3", "no"]):
        assert update("user1", "1")
    with patch("builtins.input", side_effect=["2", "personal", "2", "yes"]):
        assert update("user1", "1")

    assert (
        DeepDiff(
            list(order_db.all()[0]["items"]),
            [
                {
                    "item_id": "1",
                    "quantity": 4,
                    "isPublic": False,
                    "user_id": "user1",
                },
                {
                    "item_id": "2",
                    "quantity": 3,
                    "isPublic": True,
                    "user_id": "user1",
                },
            ],
        )
        == {}
    )

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

    items = order_db.all()[0]["items"]
    assert len(items) == 0

    # check amount 0 same public personal order
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
            ],
            "isReset": False,
        }
    )

    with patch("builtins.input", side_effect=["1", "public", "0"]):
        assert update("user1", "1")

    items = order_db.all()[0]["items"]
    assert len(items) == 1
    assert items[0]["isPublic"] == False

    @given(st.text(), st.integers(), st.text())
    def rand_inp1(s1, s2, s3):
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
                        "item_id": "2",
                        "quantity": 1,
                        "isPublic": True,
                        "user_id": "user1",
                    },
                ],
                "isReset": False,
            }
        )
        with patch("builtins.input", side_effect=[s1, s2, s3]):
            assert update("user1", "1") == ((s1 == "1") & s2 > 0)

    rand_inp1()

    @given(st.text(), st.integers(), st.text())
    def rand_inp2(s1, s2, s3):
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
                ],
                "isReset": False,
            }
        )
        with patch(
            "builtins.input",
            side_effect=["1", s1, s2] + ([s3] if s2 > 0 else []),
        ):
            assert update("user1", "1")

    rand_inp2()


def test_reset_ready(mock_db):
    order_db = mock_db["order_db"]
    reset_ready = mock_db["reset_ready"]

    order_db.insert_multiple(
        [
            {
                "order_id": "1",
                "users": [
                    {"user_id": "user1", "isReady": True},
                ],
                "items": [],
                "isReset": False,
            },
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
        ]
    )
    reset_ready("2")

    assert (
        DeepDiff(
            list(map(lambda o: dict(o), order_db.all())),
            [
                {
                    "order_id": "1",
                    "users": [
                        {"user_id": "user1", "isReady": True},
                    ],
                    "items": [],
                    "isReset": False,
                },
                {
                    "order_id": "2",
                    "users": [
                        {"user_id": "user2", "isReady": False},
                        {"user_id": "user3", "isReady": False},
                        {"user_id": "user4", "isReady": False},
                    ],
                    "items": [],
                    "isReset": True,
                },
            ],
        )
        == {}
    )


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

    assert (
        DeepDiff(
            list(order_db.all()[0]["users"]),
            [
                {"user_id": "user1", "isReady": False},
                {"user_id": "user2", "isReady": False},
            ],
        )
        == {}
    )

    with patch("builtins.input", side_effect=["yes"]):
        setReady("user1", "1")

    assert (
        DeepDiff(
            list(order_db.all()[0]["users"]),
            [
                {"user_id": "user1", "isReady": True},
                {"user_id": "user2", "isReady": False},
            ],
        )
        == {}
    )

    with patch("builtins.input", side_effect=["no"]):
        setReady("user1", "1")
    with patch("builtins.input", side_effect=["yes"]):
        setReady("user2", "1")

    assert (
        DeepDiff(
            list(order_db.all()[0]["users"]),
            [
                {"user_id": "user1", "isReady": False},
                {"user_id": "user2", "isReady": True},
            ],
        )
        == {}
    )

    @given(st.text())
    def rand_inp(s):
        with patch("builtins.input", side_effect=[s]):
            assert setReady("user1", "1")

    rand_inp()
