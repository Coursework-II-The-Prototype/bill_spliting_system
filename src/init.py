import os
from os.path import abspath
from tinydb import TinyDB, Query

base_path = abspath("databases")
db_names = ["household", "order", "preparation", "supermarket"]

QUERY = Query()
dbs = {}
for f in db_names:
    dbs[f] = TinyDB(os.path.join(base_path, f + ".json"))
    dbs[f].truncate()

# household database example
# creates 2 household (id: 1, 2), 4 users (id: 1, 2, 3, 4)

db = dbs["household"]
db.insert({"user_id": 1, "household_id": 1})
db.insert({"user_id": 2, "household_id": 1})
db.insert({"user_id": 3, "household_id": 2})
db.insert({"user_id": 4, "household_id": 2})

# order database example

db = dbs["order"]

# insert an initialized order
db.insert({"order_id": 1, "users": [], "items": [], "isReset": False})

# insert 2 users (id: 1, 2) into order with id 1
db.update(
    {"users": [{"user_id": 1, "isReady": False}, {"user_id": 2, "isReady": False}]},
    QUERY.order_id == 1,
)

# insert 10 items with item_id 1 owned by user_id 1 that is private
db.update(
    {"items": [{"item_id": 1, "quantity": 10, "user_id": 1, "isPublic": False}]},
    QUERY.order_id == 1,
)

# insert 1 item with item_id 2 owned by user_id 2 that is public
current_items = db.search(QUERY.order_id == 1)[0]["items"]
new_item = {"item_id": 2, "quantity": 1, "user_id": 2, "isPublic": True}
current_items.append(new_item)
db.update({"items": current_items}, QUERY.order_id == 1)

# supermarket database example
# creates 2 items (id: 1, 2)

db = dbs["supermarket"]
db.insert({"item_id": 1, "name": "example1", "price": 10})
db.insert({"item_id": 2, "name": "example2", "price": 20})

# preparation database exmaple
# move order with id 1 from the order database
# !!! demo purpose only, need to remove the original order from the order database as well !!!

db = dbs["preparation"]
order = dbs["order"].search(QUERY.order_id == 1)[0]
db.insert(order)
