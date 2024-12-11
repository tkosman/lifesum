
from enum import Enum

class Type(Enum):
    """Enum for categorising Messages."""

    ERROR = 'error'
    EXIT = 'exit'
    RETURN = 'return'
    REQUEST = 'request'
    PING = 'ping'
    REGISTER = 'register'

