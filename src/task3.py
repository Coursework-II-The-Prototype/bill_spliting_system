from tinydb import TinyDB, Query
import os


dbs = {
    '_default': TinyDB('orders.json'),
    'preparation': TinyDB('preparation.json')
}


current_dir = os.path.dirname(__file__)
order_db_path = os.path.join(current_dir, '../databases/order.json')

order_db = TinyDB(order_db_path)
User = Query()

student_balance = 100
delivery_fee = 10


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


# Process orders
for order in order_db.all():
    users = order.get('users', [])
    
    # Check if all users are readyß
    if all(user.get('isReady', False) for user in users):
        # 如果所有用户都 isReady，重置 isReset 状态为 False
        order_db.update({'isReset': False}, User.id == order.get('id'))


def number_of_students(order_db):
    total_users = 0
    for order in order_db.all():
        users = order.get('users', [])
        total_users += len(users)
    return total_users


def calculate_total_cost(items, user_id, delivery_fee, total_students):
    # Calculate personal items cost for the given user
    personal_items_cost = sum(item['price'] * item['quantity'] 
                              for item in items if item['user_id'] == user_id 
                              and not item['isPublic'])
    
    # Calculate public items cost
    public_items_cost = sum(item['price'] * item['quantity'] 
                            for item in items if item['isPublic'])
    
    # Calculate total cost
    total_cost = personal_items_cost 
    + (delivery_fee + public_items_cost) / total_students

    return total_cost