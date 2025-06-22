# services/report_generator.py
import json
from datetime import datetime
from collections import defaultdict

class ReportGenerator:
    def __init__(self, orders_path='data/orders.json', products_path='data/products.json'):
        # Initialize with file paths for orders and products JSON data
        self.orders_path = orders_path
        self.products_path = products_path

    def load_orders(self):
        # Load and return orders data from JSON file
        with open(self.orders_path, 'r') as f:
            return json.load(f)

    def load_products(self):
        # Load and return products data from JSON file
        with open(self.products_path, 'r') as f:
            return json.load(f)

    def generate_financial_report(self):
        # Generate financial summary including total revenue and sales grouped by date
        
        orders = self.load_orders()
        total_revenue = 0.0
        sales_by_date = defaultdict(float)  # Dictionary to accumulate sales per day

        for order in orders:
            total = order.get('total', 0.0)  # Get order total amount, default 0.0 if missing
            date = order.get('date', 'unknown')[:10]  # Extract date part YYYY-MM-DD from full timestamp string
            total_revenue += total  # Accumulate total revenue
            sales_by_date[date] += total  # Accumulate sales for this specific date

        # Return summary data as dictionary
        return {
            "total_revenue": total_revenue,
            "total_orders": len(orders),
            "sales_by_date": dict(sales_by_date)  # Convert defaultdict to regular dict
        }

    def generate_stock_report(self):
        # Generate a stock summary report listing product IDs, names, and current stock
        
        products = self.load_products()
        stock_summary = []

        for p in products:
            # Append summary info for each product
            stock_summary.append({
                "product_id": p.get("product_id"),
                "name": p.get("name"),
                "stock": p.get("stock", 0)  # Default to 0 if no stock info present
            })

        return stock_summary
