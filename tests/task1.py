import random
from tests.utils import get_db, check_fields, type_check

from tinydb import Query
from src.task1 import create_new_order

QUERY = Query()


household_db = get_db("household")
all_households = household_db.all()

order_db = get_db("order")


def test_household_db():
    check_fields(
        all_households, ["user_ids", "household_id"], "household database"
    )
    for obj in all_households:
        type_check(
            obj["household_id"],
            str,
            "field `household_id` should be in type string",
        )
        type_check(
            obj["user_ids"],
            [str],
            "field `user_ids` should be an array of strings",
        )


def test_create_new_order():
    order_db.truncate()
    users = random.choice(all_households)["user_ids"]
    user = random.choice(users)
    assert create_new_order(
        user
    ), "expect function create_new_order to return True but get False"
    all_orders = order_db.all()

    check_fields(
        all_orders, ["order_id", "users", "items", "isReset"], "order database"
    )
    for obj in all_orders:
        type_check(
            obj["users"], [str], "field `users` should be an array of strings"
        )

    assert set(all_orders[0]["users"]) == set(
        users
    ), "the `user_ids` and `users` are not matching"

    assert all_orders[0]["isReset"] == False, "expect `isReset` to be False"
    assert (
        len(all_orders[0]["items"]) == 0
    ), "expect `items` to be an empty list"
