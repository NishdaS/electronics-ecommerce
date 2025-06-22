class User:
    def __init__(self, username, email, password, role="customer", phone_number=None, address=None):
        # Initialize user attributes
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.phone_number = phone_number
        self.address = address  

    def to_dict(self):
        return {
            # Convert the user instance into a dictionary for easy serialization
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "phone_number": self.phone_number,
            "address": self.address  
        }

    @staticmethod
    def from_dict(data):
        # Create User instance from a dictionary
        return User(
            data["username"],
            data["email"],
            data["password"],
            data.get("role", "customer"), # Default role is 'customer'
            data.get("phone_number"),
            data.get("address")  
        )
