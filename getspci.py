import requests

# Ask the user for product ID
product_id = input("Enter Product ID: ")

url = f"http://127.0.0.1:5000/product/{product_id}"

response = requests.get(url)

if response.status_code == 200:
    print(f"Product with ID {product_id}:")
    print(response.json())  # Prints the product details
else:
    print(f"Failed to fetch product. Status code: {response.status_code}")
