"""
Sanic app.
"""
import argparse
import hashlib
import random
import warnings

import sanic
from sanic import response
from sanic import request
from sanic_jwt import exceptions
from sanic_jwt import initialize
from sanic_jwt.decorators import protected

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from .node_connection import user_exists
from .node_connection import add_public_key
from .node_connection import get_public_key

__version__ = '1.0.0'

def get_args():
    """ Parse command line arguments. """
    argument_parser = argparse.ArgumentParser(description='Sanic app')
    argument_parser.add_argument('-i', '--ip', type=str, default='127.0.0.1',
                                 help='ip address to bind to')
    argument_parser.add_argument('-p', '--port', type=int, default=1234, help='port number')
    argument_parser.add_argument('-d', '--daemonize', action='store_true', help='run as daemon')
    argument_parser.add_argument('--version', action='version', version=f'app {__version__}')

    return argument_parser.parse_args()

def register(request):
    """
    Register a new user with user_id and his public key.
    """
    user_id = request.json.get("user_id")
    public_key_pem = request.json.get("public_key")

    if not user_id or not public_key_pem:
        return response.json({"error": "user_id and public_key are required."}, status=400)

    if user_exists(user_id):
        return response.json({"error": "User ID already exists."}, status=400)

    try:
        public_key = load_pem_public_key(public_key_pem.encode())
        add_public_key(user_id, public_key)
    except (ValueError, InvalidKey):
        return response.json({"error": "Invalid public key format"}, status=400)

    return response.json({"message": "User registered successfully."}, status=201)


def generate_challenge(request):
    """
    Generate a challenge for a given user_id.
    Store the challenge in the app context.
    Respond with the challenge and user_id.
    """
    user_id = request.json.get("user_id", None)
    if not user_id:
        return response.json({"error": "Missing user_id."})

    if not user_exists(user_id):
        return response.json({"error": "User not found."})

    challenge = hashlib.sha256(str(random.randint(0, 1_000_000)).encode()).digest()
    request.app.ctx.challenges[user_id] = challenge

    return response.json({"challenge": challenge.hex(), "user_id": user_id})

def authenticate(request, *args, **kwargs):
    """
    Authenticate a user by verifying the signed challenge.
    This function is called automatically by the sanic-jwt middleware on /auth endpoint.
    When passed user can access endpoints protected by the @protected decorator
    by providing a valid JWT token in the Authorization header.
    """
    user_id = request.json.get("user_id")
    signed_challenge = bytes.fromhex(request.json.get("signed_challenge"))

    challenge = request.app.ctx.challenges.pop(user_id, None)
    if not challenge:
        raise exceptions.AuthenticationFailed("Challenge not found for user.")

    public_key = get_public_key(user_id)
    if not public_key:
        raise exceptions.AuthenticationFailed("User's public key not found.")

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
    except Exception as exc:
        raise exceptions.AuthenticationFailed("Challenge verification failed.") from exc
    return {"user_id": user_id}

def attach_endpoints(app):
    """Attach endpoints to the app."""
    @app.route('/')
    def index(request: request.Request):
        return response.text(r"""
           __ _  __
          / /(_)/ _| ___  ___ _   _ _ __ ___
         / / | | |_ / _ \/ __| | | | '_ ` _ \
        / /__| |  _|  __/\__ \ |_| | | | | | |
        \____/_|_|  \___||___/\__,_|_| |_| |_|
        Welcome to the Gateway.
        """
        + f"Version: {__version__}\n"
        )


    @app.route('/register', methods=["POST"])
    def handle_register(request):
        return register(request)

    @app.route('/challenge', methods=["POST"])
    def handle_challenge(request):
        return generate_challenge(request)

    @app.route('/protected')
    @protected()
    def protected_endpoint(request):
        return response.json({"message": "This is a protected endpoint."})


def create_app(arguments):
    "Sanic app factory."
    app = sanic.Sanic("Gateway")
    app.ctx.args = arguments
    app.ctx.challenges = {}
    app.config.SANIC_JWT_SECRET = "secret" #TODO: change this to a more secure secret

    with warnings.catch_warnings(): # We have no event loop
        warnings.simplefilter("ignore", category=DeprecationWarning)
        initialize(app,
            authenticate=authenticate)

    attach_endpoints(app)
    return app

def main(arguments):
    """Main entry point."""
    app = create_app(arguments)
    app.run(host=arguments.ip, port=arguments.port, single_process=True, debug=True)

if __name__ == '__main__':
    args = get_args()
    #TODO add deamonize support
    main(args)
