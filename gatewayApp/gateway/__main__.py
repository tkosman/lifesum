"""
Sanic app.
"""
import argparse
import os
from queue import Queue
import sys
from threading import Thread
import time

import sanic
from sanic import response, request
from sanic_ext import openapi
from sanic_ext import validate
from sanic_ext.exceptions import ValidationError

from .auth import protected
from .auth import authenticate
from .auth import register
from .auth import generate_challenge

from .valid_schemas import ValidUser
from .valid_schemas import ValidChallengeRequest
from .valid_schemas import ValidAuthRequest

from .daemonize import daemonize

from .node_connection_client import NodeConnectionClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

__version__ = '1.0.0'

def get_args():
    """ Parse command line arguments. """
    argument_parser = argparse.ArgumentParser(description='Sanic app')
    argument_parser.add_argument('-i', '--ip', type=str, default='127.0.0.1',
                                 help='ip address to bind to')
    argument_parser.add_argument('-p', '--port', type=int, default=1234, help='port number')
    argument_parser.add_argument('-bg', '--background', action='store_true', help='run as deamon')
    argument_parser.add_argument('--version', action='version', version=f'app {__version__}')

    return argument_parser.parse_args()


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
    @openapi.definition(
        body=ValidUser,
        summary="Register a new user with user_id and public key.",
        response={
            201: {"description": "User registered successfully."},
            400: {"description": "Error due to missing user_id or public_key."}
        }
    )
    @validate(json=ValidUser)
    def handle_register(request, body: ValidUser):
        return register(app.ctx.message_queue, body)

    @app.route('/challenge', methods=["POST"])
    @openapi.definition(
        body=ValidChallengeRequest,
        summary="Generate a challenge for a given user_id.",
        response={
            200: {"description": "Challenge generated successfully."},
            400: {"description": "Error due to missing user_id."}
        }
    )
    @validate(json=ValidChallengeRequest)
    def handle_challenge(request, body: ValidChallengeRequest):
        return generate_challenge(app.ctx.message_queue, request, body)

    @app.route('/auth', methods=["POST"])
    @openapi.definition(
        body=ValidAuthRequest,
        summary="Authenticate a user and retrieve access and refresh tokens.",
        response={
            200: {"description": "Authentication successful, returns access and refresh tokens."},
            400: {"description": "Error due to missing credentials."},
            401: {"description": "Unauthorized, invalid username or password."}
        }
    )
    @validate(json=ValidAuthRequest)
    def handle_authentication(request, body: ValidAuthRequest):
        return authenticate(app.ctx.message_queue, request, body)

    @app.exception(ValidationError)
    def handle_invalid_request(request, exception):
        return response.json(
            {
                "error": "ValidationError",
                "message": exception.message
            },
            status=exception.status_code
        )

    @app.route('/protected')
    @openapi.definition(
        summary="Protected test endpoint.",
        response={
            200: {"description": "This is a protected endpoint."}
        }
    )
    @protected
    def protected_endpoint(request):
        return response.json({"message": "This is a protected endpoint."})

def background_connection_worker(queue: Queue):
    try:
        node_connection_client = NodeConnectionClient(queue)
    except ConnectionError as e:
        # TODO : handle error
        print(e)

def create_app(arguments):
    "Sanic app factory."
    app = sanic.Sanic("Gateway")
    app.ctx.args = arguments
    app.ctx.challenges = {}
    app.config.SECRET = "secret" #TODO: change this to a more secure secret

    app.ctx.message_queue = Queue()

    @app.before_server_start()
    async def node_connection_manager(app):
        app.ctx.bg_thread = Thread(target=background_connection_worker, args=(app.ctx.message_queue,))
        app.ctx.bg_thread.daemon = True
        app.ctx.bg_thread.start()

    @app.before_server_stop
    async def stop_background_thread(app, loop):
        print("Stopping Node connection manager thread...")
        app.ctx.message_queue.put(Message(type=Type.EXIT))
        app.ctx.bg_thread.join()
        print("Node connection manager thread stopped.")

    attach_endpoints(app)
    return app

def main(arguments):
    """Main entry point."""
    app = create_app(arguments)
    app.run(host=arguments.ip, port=arguments.port, single_process=True, debug=True)

if __name__ == '__main__':
    args = get_args()
    if args.background:
        daemonize()
    main(args)
