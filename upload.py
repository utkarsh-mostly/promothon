import requests

# ✅ Flask API URL
url = "http://127.0.0.1:5000/upload"

# ✅ Image File to Upload (Replace with your actual image path)
image_path = r"C:\Users\ashis\Downloads\your_image.jpg"

print("🔹 Opening image:", image_path)

# ✅ Open the Image and Send the Request
try:
    with open(image_path, "rb") as img:
        files = {"image": img}
        print("🔹 Sending request to Flask API...")
        response = requests.post(url, files=files)
        print("🔹 Response received from API:", response.status_code)

        # ✅ Print JSON response (if successful)
        try:
            response_json = response.json()  # Convert response to JSON
            print("🔹 Extracted Product Details:")
            print(response_json)
        except requests.exceptions.JSONDecodeError:
            print("❌ API did not return JSON. Response text:", response.text)

except Exception as e:
    print("❌ Exception Occurred:", e)