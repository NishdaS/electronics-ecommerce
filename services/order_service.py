import uuid
from datetime import datetime
from utils.storage import load_data, save_data
from services.product_manager import increase_stock, reduce_stock

ORDERS_FILE = "data/orders.json"

def load_orders():
    # Load all orders from JSON file; return empty list if file not found
    try:
        return load_data(ORDERS_FILE)
    except FileNotFoundError:
        return []

def save_orders(orders):
    # Save the list of orders back to the JSON file
    save_data(ORDERS_FILE, orders)

def create_order(username, cart):
    orders = load_orders()
    products = load_data("data/products.json")

    # Check stock availability for each item in the cart
    for item in cart:
        product = next((p for p in products if p["product_id"] == item["product_id"]), None)
        if not product:
            raise Exception(f"Product ID {item['product_id']} not found.")
        if product["stock"] < item["quantity"]:
            raise Exception(f"Insufficient stock for product {product['name']}")

    # Reduce stock quantity for each product in the cart
    for item in cart:
        success, msg = reduce_stock(item['product_id'], item['quantity'])
        if not success:
            raise Exception(f"Order failed: {msg}")
    
    # Calculate total price for the order
    total = sum(item['quantity'] * item['price'] for item in cart)

    # Prepare order items for saving
    order_items = []
    for item in cart:
        order_items.append({
            "product_id": item["product_id"],
            "name": item.get("name"),
            "quantity": item["quantity"],
            "price": item.get("price")
        })

    # Create order dictionary with unique ID and timestamp
    order = {
        "order_id": str(uuid.uuid4()),
        "username": username,
        "items": order_items,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active",
         "total": total 
    }

    # Add order to the list and save
    orders.append(order)
    save_orders(orders)
    return order["order_id"]

def get_orders_for_user(username):
    # Return list of orders filtered by username
    orders = load_orders()
    return [order for order in orders if order["username"] == username]

def cancel_order(order_id):
    orders = load_orders()
    updated_orders = []
    canceled_order = None

    for order in orders:
        if order['order_id'] == order_id:
            # If already canceled, return failure message
            if order.get('status') == 'canceled':
                return False, "Order already canceled"

            # Restore stock for all items in this order
            for item in order['items']:
                increase_stock(item['product_id'], item['quantity'])

            # Mark order status as canceled
            order['status'] = 'canceled'
            canceled_order = order  # Keep a reference for UI
            continue  # Skip adding canceled order to updated_orders (removes it from active orders)
        
        # Keep active orders
        updated_orders.append(order)

    # Save updated orders list without the canceled one
    save_orders(updated_orders)
    
    # Return success flag and canceled order info for UI or False with message if not found
    if canceled_order:
        return True, canceled_order
    
    return False, "Order not found"