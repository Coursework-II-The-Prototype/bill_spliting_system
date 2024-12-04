import os
from tinydb import TinyDB, Query

db_path = os.path.join(
    os.path.dirname(__file__), "..", "databases", "household.json"
)

db = TinyDB(db_path)

current_dir = os.path.dirname(__file__)
order_path = os.path.join(current_dir, "../databases/order.json")

order = TinyDB(order_path)
order_list = Query()


def add_order(order_id, users, items):
    if not users or not items:
        return False
    order.insert(
        {
            "order_id": order_id,
            "users": users,
            "items": items,
            "isReset": False,
        }
    )
    return True


def find_orders_by_item(item_name):
    return order.search(order_list.item == item_name)


def update_order(order_id, update_dict):
    order.update(update_dict, order_list.order_id == order_id)


def delete_order(order_id):
    order.remove(order_list.order_id == order_id)


def is_user_active(user_id):
    active_orders = order.search(
        (order_list.users.any(user_id)) & (order_list.isActive == True)
    )
    return len(active_orders) > 0


household_db = TinyDB(
    os.path.join(os.path.dirname(__file__), "../databases/household.json")
)
household_query = Query()


def create_new_order(user_id):
    if order.search(
        (order_list.users.any(user_id)) & (order_list.isReset == False)
    ):
        return False

    user_household = household_db.search(household_query.user_ids.any(user_id))
    if not user_household:
        return False

    household_id = user_household[0]["household_id"]

    household_users = household_db.search(
        household_query.household_id == household_id
    )
    user_ids = [uid for user in household_users for uid in user["user_ids"]]

    new_order = {
        # "type": "order",
        # "order_id": max(order.all(), key=lambda x: x["order_id"])["order_id"]
        # + 1,
        "order_id": household_id + "ODB",
        "users": user_ids,
        "items": [],
        "isReset": False,
    }
    order.insert(new_order)
    return True