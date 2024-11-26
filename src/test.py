from src.shopping import chose_item

name, price, amount, isPublic = chose_item()

print(f"{name}, £{price}, x{amount} has been added to the basket,")
print(f"is it for public {isPublic}")

# basic test passed