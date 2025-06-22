# AWE Electronics Online Store

AWE Electronics is a web-based online store built using Python and Flask. It allows customers to register, browse products, manage their shopping cart, and place orders. Admin users can manage product listings and generate reports on inventory and sales.

---

## Features

* User Registration and Login with validation
* Password hashing using Werkzeug
* Role-based access control for Customers and Admins
* Shopping cart functionality with checkout flow
* Order receipt generation
* Product management (add, update, delete)
* Reporting for financials and stock levels
* JSON-based data persistence
* Responsive UI built with Bootstrap 5

---

## Development and Execution Details

* **Operating System**: Windows 11
* **IDE Used**: Visual Studio Code with Python extension
* **Language**: Python 3.11+
* **Framework**: Flask (v2.x)
* **Frontend Tools**: HTML, CSS (Bootstrap 5), JavaScript
* **Data Storage**: JSON files used as flat-file storage for users, products, and orders

---

## Installation Instructions

1. **Check Python version**
   Ensure Python 3.10.11 or later is installed:

   ```bash
   python --version
   ```

2. **Install required packages**
   Install Flask and Werkzeug:

   ```bash
   pip install flask
   pip install werkzeug
   ```

3. **Run the application**
   In the project root directory, start the server:

   ```bash
   python app.py
   ```

4. **Open in your browser**
   Visit the following URL to use the app:

   ```
   http://127.0.0.1:5000/
   ```

---

### How to Deploy and Run

* Download or clone the repository
* Navigate to the project directory in your terminal
* Install dependencies using `pip`
* Run `python app.py`
* Access the application via `http://127.0.0.1:5000/` in your browser

---

## Coding Standards and Practices

This project follows **Python's PEP 8** guidelines to ensure readable, maintainable, and consistent code.

### Key Practices Followed

- **PEP 8 Compliant Code**  
  - Uses `snake_case` for functions, variables, and file names  
  - Class names follow `PascalCase` for consistency across the codebase
  - Indentation: 4 spaces
  - Maximum line length: 79 characters (when practical)

- **Secure Coding**  
  - Passwords are hashed using `werkzeug.security.generate_password_hash()` before being  stored in `users.json`
  - Login uses secure hash comparison via `check_password_hash()`
  - Session management is handled via Flask’s built-in `session` object

- **Validation and Error Handling**  
  - All form inputs are validated (e.g., required fields, password length, correct formats)
  - Graceful error messages are shown for invalid registration/login attempts

- **Modular Project Structure**  
  - Separated into `models/`, `services/`, `utils/`, and `templates/` for clarity and scalability
  - Reusable service logic is extracted (e.g., `auth_service.py`, `report_generator.py`)

- **Readable, Documented Code**  
  - Clear inline comments explain key logic blocks
  - Logical grouping and separation of responsibilities per file/module

---

### Naming Conventions

| Element           | Convention Used | Example                     
| ----------------- | --------------- | --------------------------- 
| Class             | PascalCase      | `ShoppingCartService`       
| Function / Method | snake_case      | `add_product()`             
| Variable          | snake_case      | `cart_items`, `total_price` 
| File Name         | snake_case      | `user_manager.py`           

---

## Project Structure

Project Structure
├── app.py                       # Main Flask application entry point
├── models/
│   ├── user.py                  # User class model
│   └── product.py               # Product class model
├── services/
│   ├── auth_service.py          # Login authentication logic
│   ├── shopping_cart_service.py # Shopping cart logic
│   ├── order_service.py         # Order processing logic
│   ├── report_generator.py      # Financial and stock report generation
│   ├── user_manager.py          # User CRUD functions
│   └── product_manager.py       # Product CRUD functions
├── utils/
│   └── storage.py               # JSON file I/O utilities
├── data/
│   ├── users.json               # User data store
│   ├── products.json            # Product data store
│   ├── orders.json              # Orders data store
│   └── id_tracker.json          # Tracks last used IDs for entities
├── templates/
│   ├── login.html               # Login form
│   ├── register.html            # User registration form
│   ├── list_products.html       # Product listing for users
│   ├── product_detail.html      # Individual product details
│   ├── cart.html                # Shopping cart view
│   ├── checkout.html            # Checkout page
│   ├── your_orders.html         # User order history
│   ├── receipt.html             # Order receipt
│   ├── edit_user.html           # Customer: edit user form
│   ├── edit_product.html        # Admin: edit product form
│   ├── admin_dashboard.html     # Admin dashboard overview
│   ├── stock_report.html        # Admin: stock report
│   └── financial_report.html    # Admin: financial report
├── static/
│   ├── global.css               # Common styles (Customer view)
│   └── admin_dashboard.css      # Admin dashboard specific styles
└── README.md                    # Project documentation

---

## References
- PEP 8 – Style Guide for Python Code
  https://peps.python.org/pep-0008/

- Flask Documentation
  https://flask.palletsprojects.com/en/stable/
