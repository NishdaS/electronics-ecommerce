# app.py
from flask import (
    Flask, render_template, request, redirect, session,
    url_for, flash, jsonify, send_from_directory
)
import os
import json
import re
from datetime import datetime, timedelta
from collections import namedtuple
from werkzeug.security import check_password_hash, generate_password_hash

# App services
from services.user_manager import (
    register_user, get_user_by_username, update_user
)
from services.auth_service import authenticate
from services.product_manager import add_product, list_products
from services import product_manager  # If needed for other direct calls
from services.shopping_cart_service import add_to_cart, calculate_cart_total
from services.order_service import create_order
from services.report_generator import ReportGenerator

# Utility functions
from utils.storage import load_data, save_data

# Models
from models.user import User

# Flask app config
app = Flask(__name__)
app.secret_key = 'awe-secret-key'  # Required for session management

# File paths
PRODUCTS_FILE = 'data/products.json'
ORDERS_FILE = 'orders.json'

"""
    Authenticate user by comparing provided credentials
    with stored user data using hashed passwords.
"""
def authenticate(username, password):
    # Load users and check if credentials match
    with open('data/users.json') as f:
        users = json.load(f)
    for user in users:
        if user['username'] == username and check_password_hash(user['password'], password):
            return User(**user)
    return None

"""
    Check if username is valid: only letters, up to 20 characters.
"""
def is_valid_username(username):
    # Letters only, max 20 chars
    return bool(re.fullmatch(r"[A-Za-z]{1,20}", username))

"""
    Validate password strength:
    - At least 8 characters
    - Includes uppercase, lowercase, number, and special character
"""
def is_strong_password(password):
    # 8+ chars, uppercase, lowercase, digit, special char
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True

"""
    Returns a filtered list of products based on optional filters:
    - category: exact match
    - price_min: minimum price
    - price_max: maximum price
    - keyword: case-insensitive keyword match in product name
"""
def list_products_filtered(category=None, price_min=None, price_max=None, keyword=None):
    products = list_products()
    if category:
        products = [p for p in products if p.category == category]
    if price_min:
        products = [p for p in products if p.price >= price_min]
    if price_max:
        products = [p for p in products if p.price <= price_max]
    if keyword:
        keyword_lower = keyword.lower()
        products = [p for p in products if keyword_lower in p.name.lower()]
    return products

"""
    Loads and returns JSON data from a file.
    Returns an empty list if the file does not exist.
"""
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return empty list if file not found

"""
    Saves data to a JSON file with indentation.
"""
def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

"""
    Filters orders that were placed on or after the given start_date.
    - start_date should be a datetime object.
"""
def filter_orders_by_timeframe(orders, start_date):
    filtered = []
    for order in orders:
        order_date = datetime.strptime(order["date"], "%Y-%m-%d %H:%M:%S")
        if order_date >= start_date:
            filtered.append(order)
    return filtered

"""
    Calculates total quantity sold and total profit for each product.
    Returns a dictionary keyed by product_id.
"""
def calculate_stats(products, orders):
    stats = {p["product_id"]: {"sold": 0, "profit": 0.0} for p in products}
    product_map = {p["product_id"]: p for p in products}

    for order in orders:
        for item in order["items"]:
            pid = item["product_id"]
            qty = item["quantity"]
            if pid in product_map:
                price = product_map[pid]["price"]
                stats[pid]["sold"] += qty
                stats[pid]["profit"] += price * qty
    return stats

# Redirect root URL to login page
@app.route('/')
def home():
    return redirect('/login')

# Login route: Handles both GET and POST methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Attempt to retrieve user by username
        user = get_user_by_username(request.form['username'])
        # Check if user exists and password matches
        if user and check_password_hash(user.password, request.form['password']):
            # Set session with user info and enable expiration
            session.permanent = True
            session['user'] = {
                'username': user.username,
                'role': user.role
            }
            # Redirect based on role
            return redirect('/admin' if user.role == 'admin' else '/products')
        
        # If credentials are invalid, show error
        return render_template('login.html', error="Invalid credentials")

    # If GET request, show login page
    return render_template('login.html')


# Registration route: Handles new user signups
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        role = request.form.get('role')

        # Load existing users
        users = load_data("data/users.json")

        # Username validation
        if not is_valid_username(username):
            error = "Username must be alphabetic only and max 20 characters."
            return render_template('register.html', error=error, form=request.form)

        # Check if username exists
        if any(u["username"].lower() == username.lower() for u in users):
            error = "Username already exists."
            return render_template('register.html', error=error, form=request.form)

        # Check if email exists
        if any(u["email"].lower() == email for u in users):
            error = "Email already in use."
            return render_template('register.html', error=error, form=request.form)

        # Validate phone number
        if not re.fullmatch(r"\+?[0-9\s\-]{7,15}", phone_number):
            error = "Please enter a valid phone number."
            return render_template('register.html', error=error, form=request.form)

        # Password match check
        if password != confirm:
            error = "Passwords do not match."
            return render_template('register.html', error=error, form=request.form)

        # Validate password strength
        if not is_strong_password(password):
            error = "Password must be 8+ chars, with uppercase, lowercase, number, and special character."
            return render_template('register.html', error=error, form=request.form)

        # Check for valid role
        if role not in ['customer', 'admin']:
            error = "Please select a valid role."
            return render_template('register.html', error=error, form=request.form)

        # Create and save new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role,
            phone_number=phone_number  
        )
        users.append(new_user.to_dict())
        save_data("data/users.json", users)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))

    # Show registration page
    return render_template('register.html')

# GET route to show user edit form
@app.route('/edit-user/<username>', methods=['GET'])
def edit_user(username):
    # Check if user is logged in
    logged_in_user = session.get("user")
    if not logged_in_user:
        flash("Please log in to access this page.")
        return redirect("/login")

    # Allow only self or admin to edit
    if logged_in_user["username"] != username and logged_in_user["role"] != "admin":
        flash("Access denied.")
        return redirect("/")

    # Fetch user to edit
    user = get_user_by_username(username)
    if not user:
        flash("User not found.")
        return redirect("/")
    return render_template("edit_user.html", user=user)

# POST route to update user profile
@app.route('/edit-user/<username>', methods=['POST'])
def update_user_profile(username):
    # Ensure user is logged in
    logged_in_user = session.get("user")
    if not logged_in_user:
        flash("Please log in to access this page.")
        return redirect("/login")

    # Allow only self or admin to submit updates
    if logged_in_user["username"] != username and logged_in_user["role"] != "admin":
        flash("Access denied.")
        return redirect("/")

    # Prepare updated fields
    updated_fields = {
        "email": request.form.get("email"),
        "phone_number": request.form.get("phone_number"),
        "address": request.form.get("address")
    }
    # Apply update
    success, message = update_user(username, updated_fields)
    # Update session data if user edited own profile
    if success and logged_in_user["username"] == username:
        for key in updated_fields:
            session["user"][key] = updated_fields[key]
    flash(message)
    return redirect("/")

# List all products with filtering, pagination, and category options
@app.route('/products')
def products():
    page = int(request.args.get('page', 1)) # Current page number
    per_page = 3 # Items per page

    # Optional filters
    category = request.args.get('category')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    keyword = request.args.get('keyword')
    
    # Filter and paginate products
    filtered_products = list_products_filtered(category, price_min, price_max, keyword)
    total = len(filtered_products)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered_products[start:end]
    total_pages = (total + per_page - 1) // per_page

    # Get unique categories for the filter dropdown
    all_products = list_products()
    categories = sorted(set(p.category for p in all_products))

    # Render product list
    return render_template(
        'list_products.html',
        products=paginated,
        page=page,
        total_pages=total_pages,
        categories=categories,
        selected_category=category or '',
        price_min=price_min or '',
        price_max=price_max or '',
        keyword=keyword or ''
    )

# Show individual product details
@app.route('/product/<product_id>')
def product_detail(product_id):
    def products():
        # Load products from JSON using absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'data', 'products.json')
        with open(json_path) as f:
            return json.load(f)

    # Find the product by ID
    product = next((p for p in products() if p["product_id"] == product_id), None)
    if not product:
        abort(404)
    return render_template('product_detail.html', product=product)

# Log out current user by clearing the session
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Add a product to the shopping cart
@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_product_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    quantity = int(request.form['quantity'])

    products = list_products()
    product = next((p for p in products if p.product_id == product_id), None)
    if not product:
        flash("Product not found")
        return redirect('/products')

    cart = session['cart']
    # Update quantity if product already in cart
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        # Add new item to cart
        cart.append({
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "quantity": quantity
        })

    session['cart'] = cart
    flash(f"Added {quantity} x {product.name} to cart")
    return redirect('/products')

# Remove a product from the shopping cart
@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    flash("Item removed from cart")
    return redirect('/cart')

# View the current shopping cart and total
@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = calculate_cart_total(cart)
    return render_template('cart.html', cart=cart, total=total)

# Checkout route - confirm and place the order
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']['username']
    cart = session.get('cart', [])
    total = calculate_cart_total(cart)

    if request.method == 'POST':
        if not cart:
            flash("Your cart is empty.")
            return redirect('/products')
        # Create order and clear cart
        order_id = create_order(username, cart)
        session['cart'] = []  
        return redirect(url_for('view_receipt', order_id=order_id))

    # GET: Show confirmation page
    user = get_user_by_username(username)  # Make sure this is defined/imported
    return render_template('checkout.html', cart=cart, total=total, user=user)

# Admin dashboard for managing products
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    products = load_json(PRODUCTS_FILE)
    products = product_manager.list_products()
    if request.method == 'POST':
        # Get product info from form
        new_product = {
            "product_id": request.form['product_id'],
            "name": request.form['name'],
            "price": float(request.form['price']),
            "stock": int(request.form['stock'])
        }
        # Simple check: don't add duplicates
        if any(p['product_id'] == new_product['product_id'] for p in products):
            pass  # Could flash message about duplicate id
        else:
            products.append(new_product)
            save_json(PRODUCTS_FILE, products)
        # Redirect to refresh view
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_dashboard.html', products=products)

# Route to handle adding a new product from the admin panel
@app.route('/add-product', methods=['POST'])
def add_product_route():
    name = request.form['name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    category = request.form.get('category', 'Uncategorized')
    description = request.form.get('description', '')

    # Delegate to product manager to handle logic
    product_manager.add_product(name, price, stock, category, description)
    return redirect('/admin') # Redirect back to admin dashboard after adding

# Helper function to filter orders based on a given start date
def filter_orders_by_timeframe(orders, start_date):
    filtered = []
    for order in orders:
        try:
            # Print debug info
            print("Checking order:", order["order_id"], order["date"])
            # Parse the date string from order
            order_date = datetime.strptime(order["date"], "%Y-%m-%d %H:%M:%S")
            print("Parsed date:", order_date, "Start date:", start_date)
            
            # Include order if it falls within the timeframe
            if order_date >= start_date:
                print("Included")
                filtered.append(order)
            else:
                print("Excluded")
        except ValueError as e:
            # Handle date format errors gracefully
            print(f"Date parsing error: {e} in order {order}")
    print("Total filtered orders:", len(filtered))
    return filtered

# Calculate total units sold and profit per product based on filtered orders
def calculate_stats(products, orders):
     # Initialize stats dictionary for each product
    stats = {p["product_id"]: {"sold": 0, "profit": 0.0} for p in products}
    product_map = {p["product_id"]: p for p in products}

    for order in orders:
        for item in order["items"]:
            pid = item["product_id"]
            qty = item["quantity"]
            price = item.get("price")

            # If product wasn't initialized in stats, add it (failsafe)
            if pid not in stats:
                stats[pid] = {"sold": 0, "profit": 0.0}
             
            # If price is missing, fall back to product price
            if price is None and pid in product_map:
                price = product_map[pid]["price"]

            # Accumulate sales and profit if price is available
            if price is not None:
                stats[pid]["sold"] += qty
                stats[pid]["profit"] += price * qty
    return stats

# API endpoint to return sales stats for the specified timeframe
@app.route('/api/stats')
def api_stats():
    try:
        # Get timeframe from query string
        timeframe = request.args.get("timeframe", "month")
        now = datetime.now()
        # Determine start date based on timeframe
        if timeframe == "day":
            start_date = now - timedelta(days=1)
        elif timeframe == "week":
            start_date = now - timedelta(weeks=1)
        elif timeframe == "month":
            start_date = now - timedelta(days=30)
        elif timeframe == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)

        # Load product and order data
        products = load_json(PRODUCTS_FILE)
        orders = load_json(ORDERS_FILE)
        # Filter and compute stats
        filtered_orders = filter_orders_by_timeframe(orders, start_date)
        stats = calculate_stats(products, filtered_orders)
        # Debugging output
        print("Filtered Orders:", filtered_orders)
        print("Start Date:", start_date)
        # Return stats as JSON
        return jsonify(stats)
    except Exception as e:
        # Return error message with 500 status code
        print("Error in /api/stats:", e)
        return jsonify({"error": str(e)}), 500

# Route to display orders for the logged-in user
@app.route('/orders')
def your_orders():
    if 'user' not in session:
        return redirect('/login') # Require login to view orders

    username = session['user']['username']
    from services.order_service import get_orders_for_user
    orders = get_orders_for_user(username) # Fetch orders by username
    return render_template('your_orders.html', orders=orders)

# Route to serve the raw JSON file of all orders (for admin or API use)
@app.route('/orders.json')
def orders_json():
    return send_from_directory('data', 'orders.json') 

# Route to handle cancel order requests by order_id
@app.route('/cancel_order/<order_id>', methods=['POST'])
def cancel_order_route(order_id):
    from services.order_service import cancel_order
    success = cancel_order(order_id) # Call service to cancel order
    
    if success:
        flash(' Order canceled successfully.')
    else:
        flash(' Failed to cancel the order.')
    return redirect(url_for('your_orders'))

# Route to display receipt page for a specific order
@app.route('/receipt/<order_id>')
def view_receipt(order_id):
    orders = load_data("data/orders.json")
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return "Receipt not found", 404 # Show 404 if not found
    return render_template("receipt.html", order=order)

# Route to update product stock after a sale (manual sale via admin panel)
@app.route('/sell-product', methods=['POST'])
def sell_product():
    product_id = request.form['product_id']
    quantity_sold = int(request.form['quantity'])

    # Update the stock using product manager logic
    message = product_manager.update_stock_after_sale(product_id, quantity_sold)
    if message == "Stock updated successfully":
        return redirect('/admin')
    else:
        # Show error page with message
        return render_template('error.html', message=message)


# Edit product details via admin panel
@app.route('/edit-product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    products = load_json(PRODUCTS_FILE)
    product = next((p for p in products if p['product_id'] == product_id), None)

    if not product:
        flash('Product not found.')
        return redirect('/admin')

    if request.method == 'POST':
        # Update fields from form
        product['name'] = request.form['name']
        product['price'] = float(request.form['price'])
        product['stock'] = int(request.form['stock'])
        product['category'] = request.form.get('category', 'Uncategorized')
        product['description'] = request.form.get('description', '')

        save_json(PRODUCTS_FILE, products)
        flash('Product updated successfully.')
        return redirect('/admin')
    return render_template('edit_product.html', product=product)

# Route to delete a product from the system
@app.route('/delete-product/<product_id>', methods=['POST'])
def delete_product(product_id):
    products = load_json(PRODUCTS_FILE)
    updated_products = [p for p in products if p['product_id'] != product_id]

    if len(products) == len(updated_products):
        flash('Product not found.')
    else:
        save_json(PRODUCTS_FILE, updated_products)
        flash('Product deleted successfully.')
    return redirect('/admin')

# Admin view for generating and displaying a financial report
@app.route('/admin/reports/financial')
def financial_report():
    report_gen = ReportGenerator()
    report = report_gen.generate_financial_report()
    return render_template('financial_report.html', report=report)

# Admin view for generating and displaying a stock report
@app.route('/admin/reports/stock')
def stock_report():
    report_gen = ReportGenerator()
    report = report_gen.generate_stock_report()
    return render_template('stock_report.html', stock=report)

# Start the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)