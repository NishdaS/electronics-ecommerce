from models.user import User
from utils.storage import load_data, save_data
from werkzeug.security import generate_password_hash

import json

def register_user(username, password, role="customer"):
    # Load existing users from JSON file
    users = load_data("data/users.json")
    
    # Check if username already exists in users list
    if any(u["username"] == username for u in users):
        return False, "Username already exists."
    
    # Hash the password for secure storage
    hashed_password = generate_password_hash(password)
    
    # Create new User instance with hashed password and role
    new_user = User(username, hashed_password, role)
    
    # Append new user data to users list and save back to file
    users.append(new_user.to_dict())
    save_data("data/users.json", users)
    
    return True, "Registration successful."

def get_user_by_username(username):
    # Open users JSON file and load data
    with open('data/users.json') as f:
        users = json.load(f)
    
    # Find user dictionary matching the given username
    user_data = next((u for u in users if u["username"] == username), None)
    
    # If found, return User instance constructed from dictionary
    if user_data:
        return User(**user_data)
    
    # Return None if user not found
    return None

def update_user(username, updated_fields):
    # Load all users from JSON file
    users = load_data("data/users.json")
    user_found = False

    # Iterate through users to find the matching username
    for user in users:
        if user["username"] == username:
            # Update each field provided in updated_fields dict if value is not None
            for key, value in updated_fields.items():
                if value is not None:
                    user[key] = value
            user_found = True
            break

    # If user not found, return failure message
    if not user_found:
        return False, "User not found."

    # Save updated users list back to JSON file
    save_data("data/users.json", users)
    return True, "User profile updated successfully."
