
from enum import Enum

class Type(Enum):
    """Type enum for categorising Messages."""

    ERROR = 'error'
    EXIT = 'exit'
    RETURN = 'return'
    REQUEST = 'request'

