# services/cart_service.py
from models.product import Product
from services.product_manager import get_product_by_id

def add_to_cart(cart, product_id, quantity):
    # Check if product already exists in cart and increase quantity if found
    for item in cart:
        if item['product_id'] == product_id:  # match by product ID string
            item['quantity'] += quantity
            return cart

    # If product not in cart, fetch product details by ID
    product = get_product_by_id(product_id)
    if product:
        # Create a copy of the product's attributes as a dictionary
        product_dict = product.__dict__.copy()
        # Add quantity field to the product dictionary
        product_dict['quantity'] = quantity
        # Append the product to the cart
        cart.append(product_dict)

    return cart

def calculate_cart_total(cart):
    # Calculate and return the total price of all items in the cart
    return sum(item["price"] * item["quantity"] for item in cart)
