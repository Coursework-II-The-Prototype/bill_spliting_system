import os
from tinydb import TinyDB, Query


current_dir = os.path.dirname(__file__)
order = TinyDB(os.path.join(current_dir, "../databases/order.json"))
household_db = TinyDB(os.path.join(current_dir, "../databases/household.json"))

QUERY = Query()


def find_order(user_id):
    return order.get(QUERY.users.any(QUERY.user_id == user_id))


def create_new_order(user_id):
    if find_order(user_id):
        return False

    user_household = household_db.search(QUERY.user_ids.any(user_id))
    if not user_household:
        return False

    household_id = user_household[0]["household_id"]

    household_users = household_db.search(QUERY.household_id == household_id)
    user_ids = [uid for user in household_users for uid in user["user_ids"]]

    id = household_id + "ODB"
    new_order = {
        # "type": "order",
        # "order_id": max(order.all(), key=lambda x: x["order_id"])["order_id"]
        # + 1,
        "order_id": id,
        "users": [{"user_id": id, "isReady": False} for id in user_ids],
        "items": [],
        "isReset": False,
    }
    order.insert(new_order)
    print("New order created!")
    return id
