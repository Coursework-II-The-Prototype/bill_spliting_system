import os
from tinydb import TinyDB, Query

from src.logger import log_error, called_with

current_dir = os.path.dirname(__file__)
order = TinyDB(os.path.join(current_dir, "../databases/order.json"))
household_db = TinyDB(os.path.join(current_dir, "../databases/household.json"))

QUERY = Query()


def find_order(user_id):
    called_with(user_id)
    return order.get(QUERY.users.any(QUERY.user_id == user_id))


def create_new_order(user_id):
    called_with(user_id)
    if find_order(user_id):
        log_error(f"can't find order with user_id {user_id}")
        return False

    user_household = household_db.search(QUERY.user_ids.any(user_id))
    if not user_household:
        log_error(f"can't find household with user_id {user_id}")
        return False

    household_id = user_household[0]["household_id"]

    household_users = household_db.search(QUERY.household_id == household_id)
    user_ids = [uid for user in household_users for uid in user["user_ids"]]

    id = household_id + "ODB"
    new_order = {
        "order_id": id,
        "users": [{"user_id": id, "isReady": False} for id in user_ids],
        "items": [],
        "isReset": False,
    }
    order.insert(new_order)

    print("New order created!")
    return id
