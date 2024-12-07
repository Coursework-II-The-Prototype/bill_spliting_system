import os
import random
import pytest
from tests.utils import check_fields, type_check

from tinydb import TinyDB, Query

QUERY = Query()

all_households = TinyDB("databases/household.json").all()

current_dir = os.path.dirname(__file__)
mock_dir = f"{current_dir}/databases"


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(os.path, "dirname", lambda _: mock_dir)
    from utils import get_db
    from src.task1 import create_new_order

    order_db = get_db("order")
    order_db.truncate()

    return {
        "order_db": order_db,
        "create_new_order": create_new_order,
    }


def test_household_db():
    assert isinstance(all_households, list)
    assert len(all_households) > 0
    check_fields(
        all_households, ["user_ids", "household_id"], "household database"
    )
    for obj in all_households:
        type_check(
            obj["household_id"],
            str,
            "`household_id`",
        )
        type_check(
            obj["user_ids"],
            [str],
            "`user_ids`",
        )


def test_create_new_order(mock_db):
    order_db = mock_db["order_db"]
    create_new_order = mock_db["create_new_order"]

    users = random.choice(all_households)["user_ids"]
    user = random.choice(users)

    assert (
        create_new_order(user) != False
    ), "expect function create_new_order to return True but get False"

    all_orders = order_db.all()

    check_fields(
        all_orders, ["order_id", "users", "items", "isReset"], "order database"
    )
    for obj in all_orders:
        type_check(obj["users"], [dict], "`users`")
        check_fields(obj["users"], ["user_id", "isReady"], "`users`")

    assert set(map(lambda o: o["user_id"], all_orders[0]["users"])) == set(
        users
    ), "the `user_ids` and `users` are not matching"

    assert all_orders[0]["isReset"] == False, "expect `isReset` to be False"
    assert (
        len(all_orders[0]["items"]) == 0
    ), "expect `items` to be an empty list"

    assert (
        create_new_order(user) == False
    ), "expect function create_new_order to return False but get True"
