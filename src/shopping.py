import os
from tinydb import TinyDB, Query
from tabulate import tabulate

current_dir = os.path.dirname(__file__)
db_path = os.path.join(current_dir, '../databases/supermarket.json')

supermarket = TinyDB(db_path)
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

    return item_name, item_price, amount, isPublic

