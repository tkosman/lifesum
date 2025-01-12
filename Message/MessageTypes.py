
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
    BECOMEEXPERT = 'become_expert'
    ISEXPERTINFIELD = 'is_expert_in_field'
    OPENEXPERTCASE = 'open_expert_case'
    GETOPENEXPERTCASES = 'get_open_expert_cases'
    ADDITEM = 'add_item'
    GETITEMS = 'get_items'
