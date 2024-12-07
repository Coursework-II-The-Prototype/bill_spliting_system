import os
from tinydb import TinyDB, Query


QUERY = Query()

current_dir = os.path.dirname(__file__)
order_path = os.path.join(current_dir, "../databases/order.json")
preparation_path = os.path.join(current_dir, "../databases/preparation.json")
supermarket_path = os.path.join(current_dir, "../databases/supermarket.json")

order_db = TinyDB(order_path)
preparation_db = TinyDB(preparation_path)
supermarket_db = TinyDB(supermarket_path)

BALANCE = 100
DELIVERY_FEE = 10


def move_orders(orders):
    for order in orders:
        order.pop("isReset", None)
        order.pop("users", None)
        preparation_db.insert(order)
        order_db.remove(QUERY.order_id == order["order_id"])


def get_price(item_id):
    return supermarket_db.get(QUERY.item_id == item_id)["price"]


def calc_cost(items, user_id, total_students):
    personal_items_cost = sum(
        get_price(item["item_id"]) * item["quantity"]
        for item in items
        if item["user_id"] == user_id and not item["isPublic"]
    )

    public_items_cost = sum(
        get_price(item["item_id"]) * item["quantity"]
        for item in items
        if item["isPublic"]
    )

    return (
        personal_items_cost
        + (DELIVERY_FEE + public_items_cost) / total_students
    )


def daily_job():
    ready = []

    for order in order_db.all():
        if all(user["isReady"] for user in order["users"]):
            total = len(order["users"])
            flag = True
            for user in order["users"]:
                if calc_cost(order["items"], user["user_id"], total) > BALANCE:
                    flag = False
                    break
            if flag:
                ready.append(order)

    move_orders(ready)

    for record in order_db.all():
        order_db.update({"isReset": False}, doc_ids=[record.doc_id])
