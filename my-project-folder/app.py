from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import sqlite3
from PIL import Image
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure Google Gemini API Key
GEMINI_API_KEY = "AIzaSyA8Z8HrMG5DNuDPlKxtH90BxZxAbcRXfjY"
genai.configure(api_key=GEMINI_API_KEY)

# Database Configuration
DATABASE = 'products.db'

def init_db():
    """Initialize the database with required tables"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            brand TEXT,
            price TEXT,
            features TEXT,  -- Will store JSON array
            dimensions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

# Initialize database when the app starts
init_db()

# Product Extraction Prompt
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

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_features(features):
    """Ensure features are always a list"""
    if isinstance(features, str):
        try:
            # Try to parse as JSON first
            features = json.loads(features)
            if not isinstance(features, list):
                features = [features]
        except json.JSONDecodeError:
            # Fallback to comma-separated string
            features = [f.strip() for f in features.split(",") if f.strip()]
    elif not isinstance(features, list):
        features = [str(features)]
    return features

@app.route('/')
def home():
    return "Flask is running! Use the /upload endpoint to upload an image."

@app.route('/web')
def web_interface():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Initialize connection as None at the start
    conn = None
    
    try:
        # Validate image upload
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Verify image
        try:
            image = Image.open(image_file)
            image.verify()
            image = Image.open(image_file)  # Reopen after verify
        except Exception as e:
            return jsonify({"error": f"Invalid image: {str(e)}"}), 400

        # Process with Gemini
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content([prompt, image])
            raw_output = response.text.strip()
            
            # Parse response
            try:
                product_data = json.loads(raw_output)
            except json.JSONDecodeError:
                # Try to extract JSON from text
                start = raw_output.find('{')
                end = raw_output.rfind('}') + 1
                if start == -1 or end == 0:
                    return jsonify({
                        "error": "AI returned text instead of JSON",
                        "raw_text": raw_output[:200] + "..."
                    }), 400
                product_data = json.loads(raw_output[start:end])
            
            # Validate product data
            product_data = {
                "product_name": product_data.get("product_name", "Unknown Product"),
                "brand": product_data.get("brand", "Unknown Brand"),
                "price": product_data.get("price", "Not available"),
                "features": product_data.get("features", []),
                "dimensions": product_data.get("dimensions", "Not available")
            }
            
        except Exception as e:
            return jsonify({
                "error": f"AI processing failed: {str(e)}",
                "raw_response": raw_output[:200] + "..." if 'raw_output' in locals() else None
            }), 500

        # Only now establish database connection
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO products (product_name, brand, price, features, dimensions)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                product_data["product_name"],
                product_data["brand"],
                product_data["price"],
                json.dumps(product_data["features"]),
                product_data["dimensions"]
            ))
            conn.commit()
            
            # Get the inserted product
            cursor.execute("SELECT * FROM products WHERE id = last_insert_rowid()")
            product = cursor.fetchone()
            
            return jsonify({
                "message": "Product details extracted successfully",
                "product": dict(product) if product else product_data
            }), 200

        except sqlite3.Error as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if conn:  # Only try to close if connection was established
            conn.close()

def extract_from_text(text):
    """Create basic product data from text description"""
    return {
        "product_name": text.split('.')[0] if '.' in text else text[:50],
        "brand": extract_brand(text),
        "price": "",
        "features": [f.strip() for f in text.split('.')[:3] if f.strip()],
        "dimensions": ""
    }

def extract_brand(text):
    """Try to extract brand from text"""
    brands = ["boAt", "iPhone", "Samsung", "Motorola", "Nike"]  # Add your common brands
    for brand in brands:
        if brand.lower() in text.lower():
            return brand
    return "Unknown"

def validate_product_data(data):
    """Ensure product data has required structure"""
    if not isinstance(data, dict):
        data = {}
    
    required = {
        "product_name": "Unknown Product",
        "brand": "Unknown Brand",
        "price": "Not available",
        "features": [],
        "dimensions": "Not available"
    }
    
    for key, default in required.items():
        if key not in data:
            data[key] = default
        elif key == "features" and not isinstance(data[key], list):
            data[key] = [str(data[key])]
    
    return data

@app.route('/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        products = []
        
        for product in cursor.fetchall():
            product_dict = dict(product)
            product_dict["features"] = json.loads(product_dict["features"])
            products.append(product_dict)
            
        return jsonify(products)
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if product:
            product_dict = dict(product)
            product_dict["features"] = json.loads(product_dict["features"])
            return jsonify(product_dict)
        else:
            return jsonify({"error": "Product not found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        features = normalize_features(data.get("features", []))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE products 
        SET product_name = ?, brand = ?, price = ?, features = ?, dimensions = ?
        WHERE id = ?
        ''', (
            data.get("product_name"),
            data.get("brand"),
            data.get("price"),
            json.dumps(features),
            data.get("dimensions"),
            product_id
        ))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify({"message": "Product updated successfully!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify({"message": "Product deleted successfully!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True, port=5000)