import os
from tinydb import TinyDB

current_dir = os.path.dirname(__file__)
order_db_path = os.path.join(current_dir, '../databases/order.json')
order_db = TinyDB(order_db_path)

order_db.insert({
    "order_id": 1001,
    "users": [{"user_id": 123, "isReady": False}, 
              {"user_id": 456, "isReady": False}],
    "items": [
        {
            "item_id": 1,
            "price": 5.0,
            "quantity": 2,
            "isPublic": True,
            "user_id": 123
        }
    ],
    "isReset": False
})