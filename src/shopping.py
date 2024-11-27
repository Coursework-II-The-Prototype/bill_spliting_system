import os
from tinydb import TinyDB, Query
from tabulate import tabulate

current_dir = os.path.dirname(__file__)
supermarket_db_path = os.path.join(
    current_dir, '../databases/supermarket.json')
order_db_path = os.path.join(current_dir, '../databases/order.json')

supermarket = TinyDB(supermarket_db_path)
order_db = TinyDB(order_db_path)
Item = Query()


def show_supermarket():
    items = supermarket.all()

    table = [[item['item_id'], item['name'], item['price']] for item in items]
    headers = ["Item ID", "Name", "Price £"]

    print("\nAvailable products: ")
    print(tabulate(table, headers=headers, tablefmt="grid"))


def chose_item():
    show_supermarket()

    user_input_item_id = input("\nEnter the item id to chose the item: ")
    item_id = int(user_input_item_id)
    user_input_amount = input("\nHow many do you want? ")
    amount = int(user_input_amount)
    user_input_isPublic = input("\nIs this a public item?(yes/no): ")
    if user_input_isPublic == "yes":
        isPublic = True
    else:
        isPublic = False

    item = supermarket.get(Item.item_id == item_id)
    item_name = item.get('name', 'Unknown')
    item_price = item.get('price', 0.0)

    return item_id, item_name, item_price, amount, isPublic


def insert(user_id, order_id):
    order = order_db.get(Item.order_id == order_id)

    if not order:
        return "Order not found, check input"

    item_id, item_name, item_price, amount, isPublic = chose_item()

    new_item = {
        "item_id": item_id,
        "price": item_price,
        "quantity": amount,
        "isPublic": isPublic,
        "user_id": user_id
    }

    items = order.get("items", [])
    items.append(new_item)

    order_db.update({"items": items}, Item.order_id == order_id)
    return "Item added to order"


def update(user_id, order_id):
    order = order_db.get(Item.order_id == order_id)

    if not order:
        return "Order not found, check input"

    item_id_input = int(input("Enter the item id you want to modify"))

    items = order.get("items", [])
    user_input_item = None

    for item in items:
        if item["item_id"] == item_id_input and item["user_id"] == user_id:
            user_input_item = item
            break

    if not user_input_item:
        return "No such item, please add the item with correct command"

    print("Please enter following info of the item: ")
    quantity = int(input("How many of this item you want now: "))
    input1 = input("Is this a public item now? (yes/no): ")

    if input1 == "yes":
        isPublic = True
    else:
        isPublic = False

    user_input_item["quantity"] = quantity
    user_input_item["isPublic"] = isPublic

    order_db.update({"items": items}, Item.order_id == order_id)
    return f"Item {item_id_input} has been updated! "

