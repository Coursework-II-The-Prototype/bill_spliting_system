import os
from tinydb import TinyDB, Query

# Dynamically get the project root directory
current_dir = os.path.dirname(__file__)
db_path = os.path.join(current_dir, '../databases/supermarket.json')

# Open the database
db = TinyDB(db_path)

# Ensure no duplicates by checking before inserting
Item = Query()

# List of items to insert
items = [
    {'item_id': 0, 'name': 'delievry service', 'price': 4.00},
    {'item_id': 1, 'name': 'soap', 'price': 5.00},
    {'item_id': 2, 'name': 'toilet paper', 'price': 3.00},
    {'item_id': 3, 'name': 'milk', 'price': 2.30},
    {'item_id': 4, 'name': 'apples', 'price': 1.40},
    {'item_id': 5, 'name': 'kitchen roll', 'price': 3.20},
    {'item_id': 6, 'name': 'wash up liquid', 'price': 4.80},
    {'item_id': 7, 'name': 'all purpose cloths', 'price': 6.30},
    {'item_id': 8, 'name': 'napkin paper', 'price': 10.45},
    {'item_id': 9, 'name': 'paper towel', 'price': 6.60},
    {'item_id': 10, 'name': 'toilet cleaning', 'price': 2.40},
    {'item_id': 11, 'name': 'tooth brush', 'price': 1.10},
    {'item_id': 12, 'name': 'crisps', 'price': 1.66},
    {'item_id': 13, 'name': 'cleaning spray', 'price': 2.99},
    {'item_id': 14, 'name': 'flower', 'price': 14.69},
    {'item_id': 15, 'name': 'cutting board', 'price': 14.60},
    {'item_id': 16, 'name': 'shampoo', 'price': 2.20},
    {'item_id': 17, 'name': 'body wash', 'price': 3.28},
    {'item_id': 18, 'name': 'Bread', 'price': 1.00},
    {'item_id': 19, 'name': 'Eggs', 'price': 4.50},
    {'item_id': 20, 'name': 'Laundry detergent', 'price': 15.00}
]

# Insert items only if they don't already exist
for item in items:
    if not db.contains(Item.item_id == item['item_id']):
        db.insert(item)

# Print all data in the database for verification
print(db.all())
