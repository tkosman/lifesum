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
class ValidChallengeRequest:
    """ Schema for the challenge generation request."""
    user_id: str

@dataclass
class ValidAuthRequest:
    """ Schema for the authentication request."""
    user_id: str
    signed_challenge: str
