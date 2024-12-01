from src.shopping import update, insert, setReady, print_all

input1 = input("Enter order Id: ")
order_id = int(input1)

input2 = input("Enter user_id: ")
user_id = int(input2)

# insert(user_id, order_id)
# print(update(user_id, order_id))
# setReady(user_id, order_id)
print(print_all(user_id, order_id))
