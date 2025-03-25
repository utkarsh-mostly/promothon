import requests

url = "http://127.0.0.1:5000/products"

response = requests.get(url)

if response.status_code == 200:
    print("All Products:")
    print(response.json())  # Prints the list of all products
else:
    print(f"Failed to fetch products. Status code: {response.status_code}")
