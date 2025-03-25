import requests
import json

product_id = 1  # Change this to the product ID you want to update
url = f"http://127.0.0.1:5000/product/{product_id}"

updated_product_data = {
    "product_name": "Updated Product Name",
    "brand": "Updated Brand",
    "price": "$199.99",
    "features": "Updated features",
    "dimensions": "100mm x 200mm"
}

response = requests.put(url, json=updated_product_data)

if response.status_code == 200:
    print("Product updated successfully!")
    print(response.json())  # Prints success message
else:
    print(f"Failed to update product. Status code: {response.status_code}")
