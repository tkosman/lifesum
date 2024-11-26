import os
import sys

from .node_connection_client import NodeConnectionClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

"""
This module is a mock of the NODE service. It stores public keys of users.
"""

public_keys = {}

def add_public_key(node_connection_client: NodeConnectionClient, user_id, public_key):
    """Adds a user's public key to the NODE service if it doesn't already exist."""
    node_connection_client.send(Message(type=Type.REQUEST, payload=str(user_id)))

    response = node_connection_client.receive().to_json()
    print(response)

    if user_id in public_keys:
        raise ValueError("User ID already exists.")
    public_keys[user_id] = public_key

def get_public_key(node_connection_client: NodeConnectionClient, user_id):
    """Retrieve the public key of a given user_id."""
    node_connection_client.send(Message(type=Type.REQUEST, payload=str(user_id)))
    response = node_connection_client.receive().to_json()
    print(response)

    return response
    # return public_keys.get(user_id, None)

def user_exists(node_connection_client: NodeConnectionClient, user_id):
    """Check if a user_id exists in NODE."""
    node_connection_client.send(Message(type=Type.REQUEST, payload=str(user_id)))
    response = node_connection_client.receive().to_json()
    print(response)

    return response
    # return user_id in public_keys
