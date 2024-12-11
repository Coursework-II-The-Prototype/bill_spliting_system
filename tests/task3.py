import os
import pytest
from utils import mock_dir, check_db


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", lambda _: mock_dir)
    from utils import get_db
    from src.task3 import move_orders, calc_cost, daily_job

    order_db = get_db("order")
    order_db.truncate()
    preparation_db = get_db("preparation")
    preparation_db.truncate()

    return {
        "order_db": order_db,
        "preparation_db": preparation_db,
        "move_orders": move_orders,
        "calc_cost": calc_cost,
        "daily_job": daily_job,
    }


def test_move_orders(mock_db):
    preparation_db = mock_db["preparation_db"]
    move_orders = mock_db["move_orders"]

    move_orders([])
    move_orders(
        [
            {
                "order_id": "1",
                "users": [{"user_id": "user1", "isReady": False}],
                "items": [
                    {
                        "item_id": "1",
                        "quantity": 1,
                        "isPublic": True,
                        "user_id": "user1",
                    }
                ],
                "isReset": False,
            },
            {
                "order_id": "2",
                "users": [],
                "items": [],
                "isReset": False,
            },
        ]
    )
    assert len(preparation_db.all()) == 2

    check_db(
        preparation_db,
        {
            "order_id": {"type": "string"},
            "items": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "item_id": {"type": "string"},
                        "quantity": {"type": "integer"},
                        "isPublic": {"type": "boolean"},
                        "user_id": {"type": "string"},
                    },
                },
            },
        },
    )


def test_calc_cost(mock_db):
    calc_cost = mock_db["calc_cost"]

    assert (
        calc_cost(
            [
                {
                    "item_id": "1",
                    "quantity": 1,
                    "isPublic": False,
                    "user_id": "1",
                },
                {
                    "item_id": "2",
                    "quantity": 2,
                    "isPublic": False,
                    "user_id": "2",
                },
                {
                    "item_id": "3",
                    "quantity": 3,
                    "isPublic": True,
                    "user_id": "1",
                },
                {
                    "item_id": "4",
                    "quantity": 4,
                    "isPublic": True,
                    "user_id": "2",
                },
            ],
            "1",
            2,
        )
    ) == 140


def test_daily_job(mock_db):
    order_db = mock_db["order_db"]
    preparation_db = mock_db["preparation_db"]
    daily_job = mock_db["daily_job"]

    def repeat(orders, callback):
        order_db.truncate()
        preparation_db.truncate()
        order_db.insert_multiple(orders)
        daily_job()
        callback()

    def allReset():
        for o in order_db.all():
            assert o["isReset"] == False

    def moved():
        assert len(order_db.all()) == 0
        assert len(preparation_db.all()) == 1

    def not_moved():
        assert len(order_db.all()) == 1
        assert len(preparation_db.all()) == 0

    repeat(
        [
            {
                "order_id": "1",
                "users": [{"user_id": "1", "isReady": False}],
                "items": [],
                "isReset": False,
            },
            {
                "order_id": "2",
                "users": [{"user_id": "2", "isReady": False}],
                "items": [],
                "isReset": True,
            },
        ],
        allReset,
    )

    repeat(
        [
            {
                "order_id": "1",
                "users": [
                    {"user_id": "1", "isReady": True},
                    {"user_id": "2", "isReady": True},
                ],
                "items": [
                    {
                        "item_id": "1",
                        "quantity": 25,
                        "isPublic": False,
                        "user_id": "1",
                    },
                    {
                        "item_id": "2",
                        "quantity": 2,
                        "isPublic": True,
                        "user_id": "2",
                    },
                ],
                "isReset": True,
            },
        ],
        not_moved,
    )

    repeat(
        [
            {
                "order_id": "1",
                "users": [
                    {"user_id": "1", "isReady": True},
                    {"user_id": "2", "isReady": True},
                ],
                "items": [
                    {
                        "item_id": "1",
                        "quantity": 4,
                        "isPublic": False,
                        "user_id": "1",
                    },
                    {
                        "item_id": "3",
                        "quantity": 1,
                        "isPublic": True,
                        "user_id": "1",
                    },
                    {
                        "item_id": "2",
                        "quantity": 2,
                        "isPublic": True,
                        "user_id": "2",
                    },
                ],
                "isReset": True,
            },
        ],
        moved,
    )
