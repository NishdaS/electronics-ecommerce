import uuid
from models.product import Product
from utils.storage import load_data, save_data
import json

PRODUCTS_FILE = "data/products.json"
TRACKER_FILE = "data/id_tracker.json"

def get_next_product_id():
    # Read the last product ID from the tracker file
    with open(TRACKER_FILE, 'r') as f:
        tracker = json.load(f)

    # Increment the last product ID and format it as 'P###'
    tracker['last_product_id'] += 1
    next_id = f"P{tracker['last_product_id']:03}"

    # Save the updated tracker back to file
    with open(TRACKER_FILE, 'w') as f:
        json.dump(tracker, f, indent=4)

    return next_id

def list_products():
    # Load all products from the JSON file and convert to Product objects
    data = load_data(PRODUCTS_FILE)
    return [Product.from_dict(p) for p in data]

def add_product(name, price, stock, category, description):
    # Load existing products
    products = load_data(PRODUCTS_FILE)

    # Generate new product ID
    product_id = get_next_product_id()

    # Create new Product instance
    new_product = Product(product_id, name, price, stock, category, description)

    # Add new product dict to products list and save
    products.append(new_product.to_dict())
    save_data(PRODUCTS_FILE, products)

    return new_product

def update_product_stock(product_id, new_stock):
    # Load products and update stock for matching product ID
    products = load_data(PRODUCTS_FILE)
    for product in products:
        if product["product_id"] == product_id:
            product["stock"] = new_stock
            save_data(PRODUCTS_FILE, products)
            return True
    return False  # Product not found

def get_product_by_id(product_id):
    # Find and return Product object for given product ID
    products = load_data(PRODUCTS_FILE)
    for p in products:
        if p["product_id"] == product_id:
            return Product.from_dict(p)
    return None  # Not found

def list_products_paginated(page=1, per_page=3):
    # Get all products and return a page of products with total count
    all_products = list_products()
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_products[start:end]
    total = len(all_products)
    return paginated, total

def increase_stock(product_id, quantity):
    # Increase stock of product by quantity
    products = load_data(PRODUCTS_FILE)
    for product in products:
        if product['product_id'] == product_id:
            product['stock'] += quantity
            save_data(PRODUCTS_FILE, products)
            return True, "Stock increased"
    return False, "Product not found"

def reduce_stock(product_id, quantity):
    # Reduce stock of product by quantity if enough stock exists
    products = load_data(PRODUCTS_FILE)
    for product in products:
        if product['product_id'] == product_id:
            if product['stock'] < quantity:
                return False, "Insufficient stock"
            product['stock'] -= quantity
            save_data(PRODUCTS_FILE, products)
            return True, "Stock updated"
    return False, "Product not found"

def edit_product(product_id, **kwargs):
    # Update specified fields for product with matching ID
    products = load_data(PRODUCTS_FILE)
    for product in products:
        if product['product_id'] == product_id:
            for field in ['name', 'price', 'stock', 'category', 'description']:
                if field in kwargs:
                    product[field] = kwargs[field]
            save_data(PRODUCTS_FILE, products)
            return True, "Product updated"
    return False, "Product not found"

def remove_product(product_id):
    # Remove product with matching product ID from list and save
    products = load_data(PRODUCTS_FILE)
    updated_products = [p for p in products if p["product_id"] != product_id]
    if len(products) == len(updated_products):
        return False, "Product not found"  # No product removed
    save_data(PRODUCTS_FILE, updated_products)
    return True, "Product removed"
