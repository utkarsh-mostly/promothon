import requests

product_id = 2  # Change this to the product ID you want to delete
url = f"http://127.0.0.1:5000/product/{product_id}"

response = requests.delete(url)

if response.status_code == 200:
    print(f"Product with ID {product_id} deleted successfully!")
else:
    print(f"Failed to delete product. Status code: {response.status_code}")
