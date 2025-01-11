import os
import sys
import json

from .node_connection_client import NodeConnectionClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

"""
This module is a mock of the NODE service. It stores public keys of users.
"""

public_keys = {}

def add_public_key(node_connection_client: NodeConnectionClient, user_id, public_key):
    """Adds a user's public key to the NODE service if it doesn't already exist."""
    node_connection_client.send(Message(type=Type.ADDPUBKEY, payload=str(user_id)))

    response = node_connection_client.receive().to_json()
    print(response)

    if user_id in public_keys:
        raise ValueError("User ID already exists.")
    public_keys[user_id] = public_key

def get_public_key(node_connection_client: NodeConnectionClient, user_id) -> str | None:
    """Retrieve the public key of a given user_id."""
    node_connection_client.send(Message(type=Type.GETPUBKEY, payload=str('{ "address": "' + user_id+ '"}')))
    response: Message = node_connection_client.receive()

    if response.get_status() != 200:
        return None

    try:
        return json.loads(response.get_payload()).get("pub_key")
    except json.JSONDecodeError:
        return None

# def user_exists(node_connection_client: NodeConnectionClient, user_id) -> str | None:
#     """Retrieve the public key of a given user_id."""
#     node_connection_client.send(Message(type=Type.GETPUBKEY, payload=str('{ "address": "' + user_id+ '"}')))
#     response: Message = node_connection_client.receive()

#     if response.get_status() != 200:
#         return None

#     print(response.to_json())

#     try:
#         return json.loads(response.get_payload()).get("pub_key")
#     except json.JSONDecodeError:
#         return None

def user_exists(node_connection_client: NodeConnectionClient, user_id) -> bool | None:
    """Check if a user_id exists in NODE."""
    node_connection_client.send(Message(type=Type.USREXISTS, payload=str('{ "address": "' + user_id+ '"}')))
    response: Message = node_connection_client.receive()

    if response.get_status() != 200:
        return None

    try:
        return _check_key_value(response, "user_exists", True)
    except json.JSONDecodeError:
        return None

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

def _check_key_value(response: Message, key: str, expected_value) -> bool:
    """
    Checks if a specific key in the JSON payload has the expected value.

    Parameters:
        response (Message): Object with a method `get_payload()` that returns a string.
        key (str): The key to check in the JSON payload.
        expected_value (any): The value to check against.

    Returns:
        bool: True if the key exists and its value matches `expected_value`, False otherwise.
    """
    payload = response.get_payload()
    data = json.loads(payload)
    return data.get(key) == expected_value
