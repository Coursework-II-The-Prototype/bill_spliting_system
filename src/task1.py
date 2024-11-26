import os
from tinydb import TinyDB, Query

db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'household.json')

db = TinyDB(db_path)

# db.insert({"household_id": "house1", "user_ids": ["user1", "user2", "user3", "user4"]})
# db.insert({"household_id": "house2", "user_ids": ["user5", "user6", "user7", "user8"]})

current_dir = os.path.dirname(__file__)
order_path = os.path.join(current_dir, '../databases/order.json')

order = TinyDB(order_path)
order_list = Query()

order.insert({'type': 'order', 'user_id': 1, 'item': 'Laptop', 'quantity': 1})
order.insert({'type': 'order', 'user_id': 2, 'item': 'Mouse', 'quantity': 2})


def add_order(order_id, users, items):
    if not users or not items:
        return False
    order.insert({'order_id': order_id, 'users': users,
                  'items': items, 'isReset': False})
    return True


def find_orders_by_item(item_name):
    return order.search(order_list.item == item_name)


def update_order(order_id, update_dict):
    order.update(update_dict, order_list.order_id == order_id)


def delete_order(order_id):
    order.remove(order_list.order_id == order_id)

def is_user_active(user_id):
    active_orders = order.search((order_list.users.any(user_id)) & (order_list.isActive == True))
    return len(active_orders) > 0