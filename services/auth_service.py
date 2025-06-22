from models.user import User
from utils.storage import load_data
from werkzeug.security import check_password_hash
import json  # Needed for json.load()

def authenticate(username, password):
    # Open the users data file and load the list of users
    with open('data/users.json') as f:
        users = json.load(f)
    # Loop through each user dictionary in the users list
    for user in users:
        # Check if username matches and password hash matches the provided password
        if user['username'] == username and check_password_hash(user['password'], password):
             # If match, create and return a User object using the user data
            return User(**user)
    # If no matching user found, return None
    return None
