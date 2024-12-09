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

def want_to_become_expert_in_field(user_id, field):
    """Send request to become expert in a given field."""

    # Return True - if request succesffully sent to NODE
    # Return False - if request failed
    return True #TODO Dobrek - implement this

def check_expert_in_field(user_id, field):
    """Check if user is an expert in a given field."""

    # Return True - if user is an expert in the given field
    # Return False - if user is not an expert in the given field
    return True #TODO Dobrek - implement this

def open_expert_case(user_id, case_name):
    """Open a case for an expert."""

    # Return True - if case was opened successfully
    # Return False - if case opening failed
    return True #TODO Dobrek - implement this

def get_open_expert_cases(user_id):
    """Get all open cases for an expert."""

    # Return list of open cases for given user_id
    return [] #TODO Dobrek - implement this

def add_item(category, itemInfo, owner_public_key):
    """Add an item to the NODE service."""
    # Add the item to the NODE service
    # Return True - if item was added successfully
    # Return False - if item addition failed
    return True #TODO Dobrek - implement this

def get_items():
    """Get all items from the NODE service."""
    return ["item1", "item2", "item3"] #TODO Dobrek - implement this
