import os
from tinydb import TinyDB, Query
from tabulate import tabulate

current_dir = os.path.dirname(__file__)
supermarket_db_path = os.path.join(
    current_dir, "../databases/supermarket.json"
)
order_db_path = os.path.join(current_dir, "../databases/order.json")

supermarket = TinyDB(supermarket_db_path)
order_db = TinyDB(order_db_path)
Item = Query()
Product = Query()


def show_supermarket():
    items = supermarket.all()

    table = [[item["item_id"], item["name"], item["price"]] for item in items]
    return table


def get_order(id):
    return order_db.get(Item.order_id == id)


def reset_ready(order_id):
    order = get_order(order_id)

    if not order:
        return False

    users = order.get("users", [])

    for user in users:
        user["isReady"] = False

    order_db.update(
        {"users": users, "isReset": True}, Item.order_id == order_id
    )

    return True
    # return "isReady and isReset have been updated"


def insert(user_id, order_id):
    order = get_order(order_id)

    if not order:
        return False
        # return "Order not found, check input"

    headers = ["Item ID", "Name", "Price £"]

    print("\nAvailable products: ")
    print(tabulate(show_supermarket(), headers=headers, tablefmt="grid"))

    user_input_item_id = input("\nEnter the item id to chose the item: ")
    item_id = user_input_item_id
    user_input_amount = input("\nHow many do you want? ")
    amount = int(user_input_amount)
    user_input_isPublic = input("\nIs this a public item?(yes/no): ")
    if user_input_isPublic == "yes":
        isPublic = True
        reset_ready(order_id)
    else:
        isPublic = False

    new_item = {
        "item_id": item_id,
        "quantity": amount,
        "isPublic": isPublic,
        "user_id": user_id,
    }

    items = order.get("items", [])
    items.append(new_item)

    order_db.update({"items": items}, Item.order_id == order_id)
    return True
    # return "Item added to order"


def update(user_id, order_id):
    order = get_order(order_id)

    if not order:
        return False
        # return "Order not found, check input"

    item_id_input = input("Enter the item id you want to modify")

    items = order.get("items", [])
    user_input_item = None

    for item in items:
        if item["item_id"] == item_id_input and item["user_id"] == user_id:
            user_input_item = item
            break

    if not user_input_item:
        return False
        # return "No such item, please add the item with correct command"

    print("Please enter following info of the item: ")
    quantity = int(input("How many of this item you want now: "))
    input1 = input("Is this a public item now? (yes/no): ")

    if input1 == "yes":
        isPublic = True
        reset_ready(order_id)
    else:
        isPublic = False

    user_input_item["quantity"] = quantity
    user_input_item["isPublic"] = isPublic

    order_db.update({"items": items}, Item.order_id == order_id)

    return True
    # return f"Item {item_id_input} has been updated! "


def setReady(user_id, order_id):
    user_input = input("Are you ready for placing this order? (yes/no)")
    if user_input != "yes":
        return

    order = get_order(order_id)
    users = order.get("users", [])

    for user in users:
        if user["user_id"] == user_id:
            user["isReady"] = True
            break

    order_db.update({"users": users}, Item.order_id == order_id)


def get_item_detail(id, keys):
    item = supermarket.get(Product.item_id == id)
    ls = []
    for k in keys:
        ls.append(item[k])
    return ls


def get_public_table(items):
    public_items = [item for item in items if item["isPublic"]]
    public_table = [
        get_item_detail(item["item_id"], ["name", "price"])
        + [item["quantity"], item["user_id"]]
        for item in public_items
    ]
    return public_table


def get_personal_table(items, user_id):
    personal_items = [
        item
        for item in items
        if not item["isPublic"] and item["user_id"] == user_id
    ]
    personal_table = [
        get_item_detail(item["item_id"], ["name", "price"])
        + [item["quantity"]]
        for item in personal_items
    ]
    return personal_table


def print_table(user_id, order_id):
    order = get_order(order_id)
    if not order:
        return False
        # return "No exsisting order found. Please create an order first!"

    items = order.get("items", [])
    if not items:
        return False
        # return "no item in order list!"

    headers = ["Items", "Price", "Amount"]
    headers_public = ["Items", "Price", "Amount", "Addor's ID"]

    print("\nPublic Items: ")
    print(tabulate(get_public_table(items), headers_public, tablefmt="grid"))
    print("\nPersonal Items: ")
    print(
        tabulate(get_personal_table(items, user_id), headers, tablefmt="grid")
    )

    return True
    # return public_table, personal_table, headers, headers_public


def create_new_order_status(isCreated, order_id):
    if isCreated:
        return "New order has been created"
    else:
        return f"{order_id} is existed, please work on this order"
