
from enum import Enum

class Type(Enum):
    """Type enum for categorising Messages."""
    
    EXIT = 'exit'
    RETURN = 'return'
    REQUEST = 'request'

