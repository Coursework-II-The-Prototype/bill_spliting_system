from tinydb import TinyDB

dbs = {
    '_default': TinyDB('orders.json'),
    'preparation': TinyDB('preparation.json')
}

def insert(database, order):
    database.insert(order)


def move_orders_to_preparation():
    order_db = dbs['_default']
    preparation_db = dbs['preparation']
    all_orders = order_db.all()

    for order in all_orders:
        users = order['users']
        if all(user['isReady'] for user in users):
            order.pop('isReset', None)
            for user in users:
                user.pop('isReady', None)

            insert(preparation_db, order)


import os
from tinydb import TinyDB, Query

current_dir = os.path.dirname(__file__)
order_db_path = os.path.join(current_dir, '../databases/order.json')

order_db = TinyDB(order_db_path)
User = Query()

student_balance = 100
delivery_fee = 10

# Process orders
for order in order_db.all():
    users = order.get('users', [])
    
    # Check if all users are ready
    if all(user.get('isReady', False) for user in users):
        # 如果所有用户都 isReady，重置 isReset 状态为 False
        order_db.update({'isReset': False}, User.id == order.get('id'))

def number_of_students(order_db):
    total_users = 0
    for order in order_db.all():
        users = order.get('users', [])
        total_users += len(users)
    return total_users