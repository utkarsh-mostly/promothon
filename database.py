import sqlite3
import json

# Connect to SQLite Database (Creates file if not exists)
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

print("🔹 Connected to SQLite database.")

# Create Table for Storing Product Data with improved schema
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

print("✅ Table 'products' created (or already exists) with improved schema.")

# Add index for better performance
cursor.execute('''
CREATE INDEX IF NOT EXISTS idx_product_id ON products (id)
''')

print("✅ Added index on product ID for faster queries.")

# Commit and Close
conn.commit()
conn.close()

print("✅ Database setup complete!")