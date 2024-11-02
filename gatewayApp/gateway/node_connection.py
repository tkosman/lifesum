"""
This module is a mock of the NODE service. It stores public keys of users.
"""
#TODO [Dobrosław] - here should be connection to the NODE service

public_keys = {}

def add_public_key(user_id, public_key):
    """Adds a user's public key to the NODE service if it doesn't already exist."""
    if user_id in public_keys:
        raise ValueError("User ID already exists.")
    public_keys[user_id] = public_key

def get_public_key(user_id):
    """Retrieve the public key of a given user_id."""
    return public_keys.get(user_id, None)

def user_exists(user_id):
    """Check if a user_id exists in NODE."""
    return user_id in public_keys
