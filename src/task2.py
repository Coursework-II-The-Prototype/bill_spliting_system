import os
from tinydb import TinyDB, Query
from tabulate import tabulate

from src.logger import time_def, log_error, called_with, logger, log_user_input

current_dir = os.path.dirname(__file__)
supermarket_db_path = os.path.join(
    current_dir, "../databases/supermarket.json"
)
order_db_path = os.path.join(current_dir, "../databases/order.json")

supermarket = TinyDB(supermarket_db_path)
order_db = TinyDB(order_db_path)
QUERY = Query()


def show_supermarket():
    items = supermarket.all()

    table = [[item["item_id"], item["name"], item["price"]] for item in items]
    return table


def get_order(order_id):
    called_with(order_id)
    order = time_def(order_db.get, [QUERY.order_id == order_id])
    if not order:
        log_error(f"can't find order with order_id {order_id}")
    return order


def reset_ready(order_id):
    called_with(order_id)
    order = get_order(order_id)

    if not order:
        return False

    users = order.get("users", [])

    for user in users:
        user["isReady"] = False

    order_db.update(
        {"users": users, "isReset": True}, QUERY.order_id == order_id
    )

    logger.info(f"ready state of users of order {order_id} reset")
    return True


def isExisted(order_id, user_id, item_id, isPublic):
    orders = get_order(order_id)
    for item in orders.get("items", []):
        if (
            item["item_id"] == item_id
            and item["user_id"] == user_id
            and item["isPublic"] == isPublic
        ):
            return True
    return False


def insert(user_id, order_id):
    called_with([user_id, order_id])
    order = get_order(order_id)

    if not order:
        return False

    headers = ["Item ID", "Name", "Price £"]
    print("Available products: ")
    time_def(
        print, [tabulate(show_supermarket(), headers=headers, tablefmt="grid")]
    )

    item_id = input("Enter the item id to chose the item: ")
    log_user_input(item_id)

    if not time_def(supermarket.get, [QUERY.item_id == item_id]):
        print("Invalid item id!")
        return False

    amount = int(input("How many do you want? "))
    log_user_input(amount)
    user_input_isPublic = input("Is this a public item?(yes/no): ")
    log_user_input(user_input_isPublic)

    if user_input_isPublic == "yes":
        isPublic = True
        time_def(reset_ready, [order_id])
    else:
        isPublic = False

    def add_item():
        if isExisted(order_id, user_id, item_id, isPublic):
            items = order.get("items", [])
            for item in items:
                if item["item_id"] == item_id and item["user_id"] == user_id:
                    input_item = item
                    break
            new_amount = input_item["quantity"] + amount
            input_item["quantity"] = new_amount
            order_db.update({"items": items}, QUERY.order_id == order_id)
            logger.info(
                f"item {item_id} owned by user {user_id} increased to \
{new_amount} in order {order_id}"
            )
        else:
            new_item = {
                "item_id": item_id,
                "quantity": amount,
                "isPublic": isPublic,
                "user_id": user_id,
            }

            items = order.get("items", [])
            items.append(new_item)
            logger.info(f"{new_item} added to order {order_id}")

        order_db.update({"items": items}, QUERY.order_id == order_id)

    time_def(add_item)

    print("Item added to order!")
    return True


def update(user_id, order_id):
    called_with([user_id, order_id])
    order = get_order(order_id)

    if not order:
        return False

    items = order.get("items", [])
    table = get_filtered_table(
        items,
        lambda item: item["user_id"] == user_id,
        ["id", "quantity", "isPublic"],
    )
    if len(table) == 0:
        print("No item in order list!")
        return False

    headers = ["Item ID", "Name", "Price £", "Amount", "Public item"]
    print("Available products: ")
    time_def(
        print,
        [
            tabulate(
                table,
                headers=headers,
                tablefmt="grid",
            )
        ],
    )

    item_id_input = input("Enter the item id you want to modify: ")
    log_user_input(item_id_input)
    user_input_item = None

    # this is used for check if an item exsist in both
    # personal list and public order list
    if isExisted(order_id, user_id, item_id_input, True) and isExisted(
        order_id, user_id, item_id_input, False
    ):
        print("Item id you entered have both a public and personal item")
        input_public_or_personal = input(
            "Please state which one you want to modify(public/personal): "
        )
        log_user_input(input_public_or_personal)

        if input_public_or_personal == "public":
            input_isPublic = True
        else:
            input_isPublic = False
        for item in items:
            # if indeed can be found in both lists,
            # ask user whether they want to modify peronal list or public list
            if (
                item["item_id"] == item_id_input
                and item["user_id"] == user_id
                and item["isPublic"] == input_isPublic
            ):
                user_input_item = item
                break
    else:
        # used to find item just according to item_id and user_id.
        for item in items:
            if item["item_id"] == item_id_input and item["user_id"] == user_id:
                user_input_item = item
                break

    if not user_input_item:
        print("Invalid item id!")
        return False

    print("Please enter following info of the item: ")
    quantity = int(input("How many of this item you want now: "))
    log_user_input(quantity)

    if quantity <= 0:
        items = [
            item
            for item in items
            if not (
                item["item_id"] == item_id_input and item["user_id"] == user_id
            )
        ]
        time_def(
            order_db.update, [{"items": items}, QUERY.order_id == order_id]
        )
        print("Removed it! ")
        logger.info(
            f"item {item_id_input} owned by user {user_id} in order \
{order_id} is removed"
        )
        return True

    input1 = input("Is this a public item now? (yes/no): ")
    log_user_input(input1)

    if input1 == "yes":
        isPublic = True
        time_def(reset_ready, [order_id])
    else:
        isPublic = False

    user_input_item["quantity"] = quantity
    user_input_item["isPublic"] = isPublic

    def edit_order():
        unique_item = {}
        for item in items:
            key = (item["item_id"], item["user_id"], item["isPublic"])
            if key in unique_item:
                unique_item[key]["quantity"] += item["quantity"]
                item["quantity"] = 0
            else:
                unique_item[key] = item

        order["items"] = list(unique_item.values())
        order_db.update({"items": order["items"]}, QUERY.order_id == order_id)

    time_def(edit_order)

    print("Item has been updated!")
    logger.info(
        f"item {item_id_input} owned by user {user_id} in order {order_id} \
now has quantity of {quantity} and is {"public" if isPublic else "personal"}"
    )
    return True


def setReady(user_id, order_id):
    called_with([user_id, order_id])

    user_input = input("Are you ready for placing this order? (yes/no): ")
    if user_input == "yes":
        isReady = True
    else:
        isReady = False

    order = get_order(order_id)
    if not order:
        return

    users = order.get("users", [])

    def set_ready():
        for user in users:
            if user["user_id"] == user_id:
                user["isReady"] = isReady
                break

        order_db.update({"users": users}, QUERY.order_id == order_id)

    time_def(set_ready)

    print("Ready for the order!" if isReady else "Ready unset!")
    logger.info(
        f"ready state of user {user_id} is set to {isReady} \
in order {order_id}"
    )


def get_item_detail(id, keys):
    item = supermarket.get(QUERY.item_id == id)
    ls = []
    for k in keys:
        ls.append(item[k])
    return ls


def get_filtered_table(items, predict, keys):
    i_list = [item for item in items if predict(item)]
    table = [
        (
            ([item["item_id"]] if "id" in keys else [])
            + get_item_detail(item["item_id"], ["name", "price"])
            + list(map(lambda key: item[key], [k for k in keys if k != "id"]))
        )
        for item in i_list
    ]
    return table


def get_public_table(items):
    return get_filtered_table(
        items, lambda item: item["isPublic"], ["quantity", "user_id"]
    )


def get_personal_table(items, user_id):
    return get_filtered_table(
        items,
        lambda item: not item["isPublic"] and item["user_id"] == user_id,
        ["quantity"],
    )


def print_order(user_id, order_id):
    called_with([user_id, order_id])

    order = get_order(order_id)
    if not order:
        return False

    items = order.get("items", [])

    headers = ["Name", "Price £", "Amount"]
    headers_public = headers + ["Addor's ID"]

    t1 = get_public_table(items)
    if len(t1) > 0:
        print("Public Items: ")
        print(tabulate(t1, headers_public, tablefmt="grid"))

    t2 = get_personal_table(items, user_id)
    if len(t2) > 0:
        print("Personal Items: ")
        print(tabulate(t2, headers, tablefmt="grid"))

    if len(t1) + len(t2) == 0:
        print("No item in order list!")
        return False

    return True
