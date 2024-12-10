import os
import random
import pytest
from tests.utils import mock_dir, check_db
from hypothesis import given, strategies as st
from deepdiff import DeepDiff

from tinydb import TinyDB, Query

household_db = TinyDB("databases/household.json")


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", lambda _: mock_dir)
    from utils import get_db
    from src.task1 import find_order, create_new_order

    order_db = get_db("order")
    order_db.truncate()

    return {
        "order_db": order_db,
        "find_order": find_order,
        "create_new_order": create_new_order,
    }


def test_household_db():
    assert len(household_db.all()) > 0
    check_db(
        household_db,
        {
            "household_id": {"type": "string"},
            "user_ids": {
                "type": "list",
                "schema": {"type": "string"},
            },
        },
    )


def test_find_order(mock_db):
    order_db = mock_db["order_db"]
    find_order = mock_db["find_order"]

    @given(st.text())
    def invalid_id(id):
        assert not find_order(id)

    invalid_id()

    order_db.insert(
        {"order_id": "1", "users": [{"user_id": "1"}, {"user_id": "2"}]}
    )
    assert find_order("1")
    assert not find_order("3")

    invalid_id()


def test_create_new_order(mock_db):
    order_db = mock_db["order_db"]
    create_new_order = mock_db["create_new_order"]
    all_households = household_db.all()

    @given(st.text())
    def invalid_usr(id):
        assert not create_new_order(
            id
        ), "expect order not to be created when user_id is invalid"

    invalid_usr()

    users = random.choice(all_households)["user_ids"]
    user = random.choice(users)

    order_id = create_new_order(user)
    assert order_id, "expect new order to be created"

    assert DeepDiff(
        order_db.get(Query().order_id == order_id),
        {
            "order_id": order_id,
            "users": map(lambda id: {"user_id": id, "isReady": False}, users),
            "items": [],
            "isReset": False,
        },
        ignore_order=True,
    )

    assert not create_new_order(
        user
    ), "expect same user to have only 1 concurrent order"

    invalid_usr()
