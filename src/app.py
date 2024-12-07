import os
import platform
import subprocess
import task1
import task2
from tinydb import TinyDB
from prometheus_client import start_http_server

from logger import logger, time_def, log_user_input

current_dir = os.path.dirname(__file__)
household_db = TinyDB(os.path.join(current_dir, "../databases/household.json"))
order_db = TinyDB(os.path.join(current_dir, "../databases/order.json"))


def get_all_demo_users():
    ls = []
    for h in household_db.all():
        ls += h["user_ids"]
    return ls


def my_cls():
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def main():
    print("Login as one of the users:")
    us = get_all_demo_users()
    print(us)
    u_id = ""
    while not (u_id in us):
        u_id = input("Login: ")
    logger.info(f"login as {u_id}")
    my_cls()

    o_id = time_def(task1.find_order, [u_id])

    if o_id:
        o_id = o_id["order_id"]
        logger.info(f"order {o_id}")

    code = ""
    while True:
        if not o_id:
            code = input("Action ([n]ew order, [q]uit): ")
            log_user_input(code)
            my_cls()
            match (code):
                case "n":
                    o_id = time_def(task1.create_new_order, [u_id])
                    logger.info(f"order {o_id}")
                case "q":
                    break
                case _:
                    print("No such action")
        else:
            code = input(
                "Action ([p]rint table, [a]dd item, [e]dit item, \
[r]eady to order, [q]uit): "
            )
            log_user_input(code)
            my_cls()
            match (code):
                case "a":
                    task2.insert(u_id, o_id)
                case "e":
                    task2.update(u_id, o_id)
                case "r":
                    task2.setReady(u_id, o_id)
                case "p":
                    time_def(task2.print_order, [u_id, o_id])
                case "q":
                    break
                case _:
                    print("No such action")


if __name__ == "__main__":
    start_http_server(8000)
    main()
