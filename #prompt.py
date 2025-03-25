import google.generativeai as genai
import json
from PIL import Image

# ✅ Set Google Gemini API Key
GEMINI_API_KEY = "AIzaSyCFaDi2l4hbbdwnJ-kkoDA5Og8TJ6SSDDI"  # 🔹 Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Load Product Image from Local File (Replace with your image path)
image_path = r"C:\Users\ashis\Downloads\WhatsApp Image 2025-03-24 at 3.13.11 PM.jpeg"# 🔹 Replace with the actual image file path
image = Image.open(image_path)

# ✅ Load Google Gemini Model
model = genai.GenerativeModel("gemini-1.5-pro")  # 🔹 Use gemini-1.5-pro for better accuracy

# ✅ Define the Prompt (Forces AI to Fill Missing Fields)
prompt = """
Extract product details from this image and return them in JSON format.
Ensure the output is a **valid JSON object** with these fields:
- "product_name": If the exact product name is missing, **infer it from the image and brand**.
- "brand": Extract the brand name.
- "price": If visible, extract the price. **If missing, estimate the price based on similar models.**
- "features": List **at least 4 features**. If some are missing, **generate reasonable features for this type of product.**
- "dimensions": If not visible, **estimate based on similar models in the same category.**

🚨 **Important Rules:**
1️⃣ **If the product name is missing, generate a likely name based on brand and category.**  
2️⃣ **If price is missing, estimate it based on similar products.**  
3️⃣ **If dimensions are missing, return an estimated size based on category.**  
4️⃣ **Ensure JSON format is correct.**  

### Example JSON Output Format:
```json
{
    "product_name": "Motorola Moto G Power (2023)",
    "brand": "Motorola",
    "price": "₹12,999",
    "features": [
        "50MP Quad Pixel camera",
        "5000mAh battery",
        "6.5-inch HD+ display",
        "Fast charging support"
    ],
    "dimensions": "167.3 x 76.4 x 9.3 mm"
}
"""

# ✅ Send Image to Google Gemini for Processing
response = model.generate_content([prompt, image])

# ✅ Extract Only JSON from AI Response
try:
    raw_output = response.text.strip()  # Remove extra spaces
    start = raw_output.find("{")
    end = raw_output.rfind("}") + 1
    json_text = raw_output[start:end]  # Extract only JSON part
    product_json = json.loads(json_text)  # Convert to JSON
except json.JSONDecodeError:
    print("Error: Could not convert AI output to JSON.")
    product_json = {"error": "AI response was not in JSON format."}

# ✅ Save Extracted Details to JSON File
with open("product_data.json", "w") as file:
    json.dump(product_json, file, indent=4)

# ✅ Print Final JSON Output
print("\nFinal Extracted Product Details:")
print(json.dumps(product_json, indent=4))