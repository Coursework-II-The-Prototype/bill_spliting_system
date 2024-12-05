import os
from tinydb import TinyDB, Query


current_dir = os.path.dirname(__file__)
order = TinyDB(os.path.join(current_dir, "../databases/order.json"))
household_db = TinyDB(os.path.join(current_dir, "../databases/household.json"))

QUERY = Query()


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
    return order.search(QUERY.item == item_name)


def update_order(order_id, update_dict):
    order.update(update_dict, QUERY.order_id == order_id)


def delete_order(order_id):
    order.remove(QUERY.order_id == order_id)


def is_user_active(user_id):
    active_orders = order.search(
        (QUERY.users.any(user_id)) & (QUERY.isActive == True)
    )
    return len(active_orders) > 0


def create_new_order(user_id):
    if order.search((QUERY.users.any(user_id)) & (QUERY.isReset == False)):
        return False

    user_household = household_db.search(QUERY.user_ids.any(user_id))
    if not user_household:
        return False

    household_id = user_household[0]["household_id"]

    household_users = household_db.search(QUERY.household_id == household_id)
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
