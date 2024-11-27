import os
from tinydb import TinyDB, Query
from tabulate import tabulate

current_dir = os.path.dirname(__file__)
supermarket_db_path = os.path.join(
    current_dir, '../databases/supermarket.json')
supermarket = TinyDB(supermarket_db_path)
Item = Query()

household_db_path = os.path.join(current_dir, '../databases/household.json')
household_and_user = TinyDB(household_db_path)
household = Query()


def id_check():
    input1 = input("Enter your house hold id please: ")
    house_id_input = int(input1)
    house = household_and_user.get(household.house_id == house_id_input)

    if house:
        print("House found! ")
        input2 = input("Enter your student id: ")
        student_id_input = int(input2)
        student_ids = house.get("student_id", [])

        if student_id_input in student_ids:
            print("Student id found! ")
            return house, student_ids, True
        else:
            return 0, 0, False
    else:
        print("Cannot found house or student id, check your input")
        return 0, 0, False


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

