"""
This module contains the authentication logic for the gateway service.
"""
import random
from datetime import datetime
from functools import wraps
import jwt

from sanic import response

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from .node_connection import user_exists
from .node_connection import add_public_key
from .node_connection import get_public_key

def check_token(request):
    """ Check if the request has a valid JWT token."""
    if not request.token:
        return False

    try:
        jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True

def protected(wrapped):
    """ Decorator to protect endpoints with JWT token."""
    def decorator(f):
        @wraps(f)
        def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)

            if is_authenticated:
                resp = f(request, *args, **kwargs)
                return resp
            else:
                return response.json({"error": "You are unauthorized."}, status=401)

        return decorated_function

    return decorator(wrapped)

def register(queue, request_body):
    """
    Register a new user with user_id and his public key.
    """
    user_id = request_body.user_id
    public_key_pem = request_body.public_key

    if not user_id or not public_key_pem:
        return response.json({"error": "user_id and public_key are required."}, status=400)

    if user_exists(queue, user_id):
        return response.json({"error": "User ID already exists."}, status=400)

    try:
        public_key = load_pem_public_key(public_key_pem.encode())
        add_public_key(queue, user_id, public_key)
    except (ValueError, InvalidKey):
        return response.json({"error": "Invalid public key format"}, status=400)

    return response.json({"message": "User registered successfully."}, status=201)


def generate_challenge(queue, request, request_body):
    """
    Generate a challenge for a given user_id.
    Fetch the user's public key and encrypt the challenge with it.
    Store the challenge in the app context for validation.
    Respond with the encrypted challenge and user_id.
    """
    user_id = request_body.user_id

    if not user_id:
        return response.json({"error": "Missing user_id."})

    if not user_exists(queue, user_id):
        return response.json({"error": "User not found."})

    nonce = str(random.randint(0, 1_000_000))
    timestamp = datetime.utcnow().isoformat()
    challenge = f"LOGIN_REQUEST|{nonce}|{timestamp}"

    request.app.ctx.challenges[user_id] = challenge.encode()

    try:
        public_key = get_public_key(queue, user_id)
        encrypted_challenge = public_key.encrypt(
            challenge.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return response.json({"user_id": user_id, "challenge": encrypted_challenge.hex()})

    except Exception as e:
        return response.json({"error": f"Failed to generate challenge: {str(e)}"})



def authenticate(queue, request, body):
    """
    Authenticate a user by verifying the signed challenge.
    This function is called automatically by the sanic-jwt middleware on /auth endpoint.
    When passed user can access endpoints protected by the @protected decorator
    by providing a valid JWT token in the Authorization header.
    """
    user_id = body.user_id
    signed_challenge = bytes.fromhex(body.signed_challenge)

    challenge = request.app.ctx.challenges.pop(user_id, None)
    if not challenge:
        return response.json({"eror": "Challenge not found for user."})

    public_key = get_public_key(queue, user_id)
    if not public_key:
        return response.json({"eror:": "User's public key not found."})

    try:
        public_key.verify(
            signed_challenge,
            challenge,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception:
        return response.json({"eror:": "Challenge verification failed."})
    return response.json({"access_token": jwt.encode({}, request.app.config.SECRET)})
