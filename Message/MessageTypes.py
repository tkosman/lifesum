
from enum import Enum

class Type(Enum):
    """Enum for categorising Messages."""

    ERROR = 'error'
    EXIT = 'exit'
    RETURN = 'return'
    PING = 'ping'

    USREXISTS = 'user_exists'
    REGISTER = 'register'
    GETPUBKEY = 'get_public_key'
    ADDPUBKEY = 'add_public_key'
