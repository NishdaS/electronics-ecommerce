class Product:
    def __init__(self, product_id, name, price, stock, category, description=""):
        # Initialize a new product with basic attributes
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.description = description

    def to_dict(self):
        return {
            # Convert the product instance into a dictionary for easy serialization
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data):
        return Product(
            data["product_id"],
            data["name"],
            data["price"],
            data["stock"],
            data.get("category", "Uncategorized"),
            data.get("description", "")
        )

    def reduce_stock(self, quantity_sold):
        # Decrease stock by quantity sold; raise error if insufficient stock
        if quantity_sold > self.stock:
            raise ValueError("Not enough stock available to complete the sale")
        self.stock -= quantity_sold
