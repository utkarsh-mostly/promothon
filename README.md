#Promothon project
# Promothon - Image Cataloger and Product Catalog Generator

Promothon is a Python-based product catalog generation tool designed to manage and catalog product images and related data efficiently. This repository contains scripts and resources to upload, update, and maintain a product image catalog with associated metadata stored in a database.

## Features
- Upload and manage product images.
- Generate product catalogs with detailed metadata.
- Update existing product entries in the catalog.
- Store product information in a JSON file and SQLite database.
- Modular scripts for data handling, image processing, and database operations.

## Repository Structure
- `app.py` - Main web application script (Flask).
- `app.cpython-312.pyc` - Compiled Python file for `app.py`.
- `basecheck.py` - Base script for validation and checks.
- `prompt.py` - Handles user prompts and input.
- `database.py` - Database interaction module (SQLite).
- `del.py` - Script to delete product entries.
- `get.py` - Retrieve and display product data.
- `getspci.py` - Specialized product catalog retrieval.
- `put_update.py` - Update product data in the catalog.
- `upload.py` - Upload new product images and data.
- `product_data.json` - Sample JSON dataset of product metadata.
- `products.db` - SQLite database file storing product details.
- `my-project-folder/` - Additional project files and resources.
- `static/` - Static files such as images, CSS, JavaScript for the web app.
- `templates/` - HTML templates for rendering web pages.
- `README.md` - Project documentation.

## Installation
1. Clone the repository:
git clone https://github.com/utkarsh-mostly/promothon.git

text
2. Navigate into the project directory:
cd promothon

text
3. Install required dependencies (add specific dependencies if applicable):
pip install -r requirements.txt

text

## Usage
- Run the web application:
python app.py

text
- Use the web interface to upload, update, view, and delete product entries.
- Alternatively, use scripts like `upload.py`, `put_update.py`, `get.py`, and `del.py` for command-line operations.

## Contributing
Contributions are welcome! Please open issues or submit pull requests for bug fixes and feature requests.

## License
This project is open source and available under the MIT License.

---

For questions or support, contact the repository owner [utkarsh-mostly].
