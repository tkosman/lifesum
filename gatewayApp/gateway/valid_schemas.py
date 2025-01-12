"""
This module contains the valid schemas for the gateway service.
"""

from dataclasses import dataclass

@dataclass
class ValidUser:
    """ Schema for the user registration request."""
    user_id: str
    public_key: str

@dataclass
class GetUserInfo:
    """ Schema for the user info request."""
    user_id: str

@dataclass
class ValidChallengeRequest:
    """ Schema for the challenge generation request."""
    user_id: str

@dataclass
class ValidAuthRequest:
    """ Schema for the authentication request."""
    user_id: str
    signed_challenge: str

@dataclass
class ValidExpertBecomeCheck:
    """ Schema for the expert become request."""
    user_id: str
    field: str

@dataclass
class ValidVoteExpertCase:
    """ Schema for the expert case voting request."""
    ec_id: str
    option: str
    public_key: str

@dataclass
class ValidItemAdd:
    """ Schema for the item addition request."""
    category: str
    item_info: str
    public_key: str
