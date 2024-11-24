import os
from queue import Queue
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

"""
This module is a mock of the NODE service. It stores public keys of users.
"""
#TODO [Dobrosław] - here should be connection to the NODE service

public_keys = {}

def send(queue: Queue, message: Message):
    """Passes the message to node_communication_client
    and sends it.

    Args:
        queue (Queue): Message queue.
        message (Message): Message to send.
    """
    queue.put(message)

def add_public_key(queue: Queue, user_id, public_key):
    """Adds a user's public key to the NODE service if it doesn't already exist."""
    send(queue, Message(type=Type.REQUEST, payload=str(user_id)))

    if user_id in public_keys:
        raise ValueError("User ID already exists.")
    public_keys[user_id] = public_key

def get_public_key(queue: Queue, user_id):
    """Retrieve the public key of a given user_id."""
    send(queue, Message(type=Type.REQUEST, payload=str(user_id)))

    return public_keys.get(user_id, None)

def user_exists(queue: Queue, user_id):
    """Check if a user_id exists in NODE."""
    send(queue, Message(type=Type.REQUEST, payload=str(user_id)))

    return user_id in public_keys
