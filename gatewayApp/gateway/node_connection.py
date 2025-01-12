import os
import sys
import json

from cryptography.hazmat.primitives import serialization

from .node_connection_client import NodeConnectionClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

"""
This module is a mock of the NODE service. It stores public keys of users.
"""

def add_public_key(node_connection_client: NodeConnectionClient, user_id, public_key):
    """Adds a user's public key to the NODE service if it doesn't already exist."""

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    public_key_str = public_key_pem.decode('utf-8')

    data = {
        "nick": user_id,
        "public_key": public_key_str,
        "additional_data": "a",
        "is_bot": False
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.ADDPUBKEY, payload=payload))

    response = node_connection_client.receive()

    if response.get_status() != 200:
        return NameError("User ID already exists.")

def get_public_key(node_connection_client: NodeConnectionClient, user_id) -> str | None:
    """Retrieve the public key of a given user_id."""

    data = {
        "nick": user_id
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.GETPUBKEY, payload=payload))
    response: Message = node_connection_client.receive()

    if response.get_status() != 200:
        return None

    try:
        return json.loads(response.get_payload()).get("pub_key")
    except json.JSONDecodeError:
        return None

def user_exists(node_connection_client: NodeConnectionClient, user_id) -> bool | None:
    """Check if a user_id exists in NODE."""

    data = {
        "nick": user_id
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.USREXISTS, payload=payload))
    response: Message = node_connection_client.receive()

    return _check_key_value(response, "user_exists", "True")

def want_to_become_expert_in_field(node_connection_client: NodeConnectionClient, user_id, field):
    """Send request to become expert in a given field."""

    data = {
        "field": field,
        "min_reputation": -1,
        "bot_allowed": True,
        "nick": user_id,
        "test_answers": "passed",
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.BECOMEEXPERT, payload=payload))
    response: Message = node_connection_client.receive()

    if response.get_status() != 200:
        return False
    return True

def check_expert_in_field(node_connection_client: NodeConnectionClient, user_id, field):
    """Check if user is an expert in a given field."""

    data = {
        "nick": user_id
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.ISEXPERTINFIELD, payload=payload))
    response: Message = node_connection_client.receive()

    expert_in = json.loads(response.get_payload())

    # ! temp to check
    print(expert_in)

    if field in expert_in:
        return True
    else :
        return False

def open_expert_case(node_connection_client: NodeConnectionClient, data: dict, case_type: str):
    """Open a case for an expert."""
    print(data)
   #TODO Add a check for the case type
    return True

def vote_expert_case(node_connection_client: NodeConnectionClient, case_id, option, public_key):
    """Vote for an expert case."""

    return True

# ! there is only a function to get details of an expert case and it takes ec_id
def get_open_expert_cases(node_connection_client: NodeConnectionClient, user_id):
    """Get all open cases for an expert."""

    data = {
        "nick": user_id
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.GETOPENEXPERTCASES, payload=payload))
    response: Message = node_connection_client.receive()

    if response.get_status() != 200:
        return None

    # TODO check if it is a list
    return json.loads(response.get_payload())

def add_item(node_connection_client: NodeConnectionClient, category, itemInfo, owner_public_key):
    """Add an item to the NODE service."""

    data = {
        "category": category,
        "itemInfo": itemInfo,
        "owner_public_key": owner_public_key
    }

    payload = json.dumps(data)

    node_connection_client.send(Message(type=Type.ADDITEM, payload=payload))
    response: Message = node_connection_client.receive()

    # ? return item_id
    if response.get_status() != 200:
        return None
    return True

# ! there is only a function to get specific item and it takes item_id
def get_item_by_id(node_connection_client: NodeConnectionClient, item_id: int):
    """Get all items from the NODE service."""
    #TODO Add limit on the number of items

    node_connection_client.send(Message(type=Type.GETITEMS))
    response: Message = node_connection_client.receive()

    if response.get_status() != 200:
        return None

    # TODO check if the case is working
    return list(json.loads(response.get_payload()).get("cases"))


def _check_key_value(response: Message, key: str, expected_value: str) -> bool:
    """
    Checks if a specific key in the JSON payload has the expected string value.

    Parameters:
        response (Message): Object with a method `get_payload()` that returns a string.
        key (str): The key to check in the JSON payload.
        expected_value (any): The value to check against.

    Returns:
        bool: True if the key exists and its value matches `expected_value`, False otherwise.
    """
    payload = response.get_payload()
    data = json.loads(payload)

    return str(data.get(key)) == expected_value
