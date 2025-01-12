"""
Sanic app.
"""
import argparse
from threading import Thread

import sanic
from sanic import response, request
from sanic.exceptions import ServerError

from sanic_ext import openapi
from sanic_ext import validate
from sanic_ext.exceptions import ValidationError
from sanic.log import logger

from .auth import protected
from .auth import authenticate
from .auth import register
from .auth import generate_challenge

from .valid_schemas import ValidUser
from .valid_schemas import GetUserInfo
from .valid_schemas import ValidChallengeRequest
from .valid_schemas import ValidAuthRequest
from .valid_schemas import ValidVoteExpertCase
from .valid_schemas import ValidExpertBecomeCheck
from .valid_schemas import ValidItemAdd

from .daemonize import daemonize

from .node_connection import open_expert_case, want_to_become_expert_in_field
from .node_connection import check_expert_in_field
from .node_connection import get_open_expert_cases
from .node_connection import vote_expert_case
from .node_connection import add_item
from .node_connection import get_item_by_id

from .node_connection_client import NodeConnectionClient


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
    app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="bearer",
        bearer_format="JWT",
    )


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


    # Authentication and registration
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
        return register(app.ctx.node_connection_client, body)


    @app.route('/get-user-info', methods=["POST"])
    @openapi.definition(
        body=GetUserInfo,
        summary="Get user info by user_id.",
        response={
            200: {"description": "User info retrieved successfully."},
            400: {"description": "Error due to missing user_id."}
        }
    )
    @validate(json=GetUserInfo)
    def handle_get_user_info(req, body: GetUserInfo):
        return response.json({"user_info": app.ctx.node_connection_client.get_user_info(body.user_id)})

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
        return generate_challenge(app.ctx.node_connection_client, request, body)

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
        return authenticate(app.ctx.node_connection_client, request, body)

    # Becoming expert
    @app.post('/expert/become')
    # @protected
    @openapi.definition(
        body=ValidExpertBecomeCheck,
        summary="Request to become an expert in a specific field.",
        response={
            200: {"description": "Request successful."},
            400: {"description": "Error due to missing user_id or field."}
        }
    )
    @validate(json=ValidExpertBecomeCheck)
    def handle_become_expert(request, body: ValidExpertBecomeCheck):
        user_id = body.user_id
        field = body.field
        if not user_id or not field:
            raise ServerError("Missing user_id or field.")
        return response.json({"success": want_to_become_expert_in_field(app.ctx.node_connection_client, user_id, field)})

    @app.post('/expert/check')
    # @protected
    @openapi.definition(
        body=ValidExpertBecomeCheck,
        summary="Check if a user is an expert in a specific field.",
        response={
            200: {"description": "Check successful."},
            400: {"description": "Error due to missing user_id or field."}
        }
    )
    @validate(json=ValidExpertBecomeCheck)
    def handle_check_expert(request, body: ValidExpertBecomeCheck):
        user_id = body.user_id
        field = body.field
        if not user_id or not field:
            raise ServerError("Missing user_id or field.")
        return response.json({"is_expert": check_expert_in_field(app.ctx.node_connection_client, user_id, field)})

    # Expert cases
    @app.post('/expert/case/open/<case_type>')
    @openapi.definition(
        body=ValidExpertBecomeCheck,
        summary="Open a case for an expert.",
        response={
            200: {"description": "Case opened successfully."},
            400: {"description": "Error due to missing user_id or field."}
        })
    # @protected
    def handle_open_expert_case(request, case_type):
        data = request.json
        return response.json({"success": open_expert_case(app.ctx.node_connection_client, data, case_type)})

    # @app.get('/expert/case/all')
    # # @protected
    # def handle_get_expert_cases(request):
    #     user_id = request.json.get("user_id", None)
    #     if not user_id:
    #         raise ServerError("Missing user_id.")
    #     open_cases = get_open_expert_cases(app.ctx.node_connection_client, user_id)
    #     return response.json({"open_cases": open_cases})

    @app.post('expert/case/vote')
    @openapi.definition(
        body=ValidVoteExpertCase,
        summary="Vote for an expert case.",
        response={
            200: {"description": "Vote successful."},
            400: {"description": "Error due to missing case_id, option or public_key."}
        })
    @protected
    @validate(json=ValidVoteExpertCase)
    def handle_expert_case_vote(request, body: ValidVoteExpertCase):
        ec_id = body.case_id
        option = body.option
        public_key = body.public_key
        if not ec_id or not option or not public_key:
            raise ServerError("Missing case_id, option or public_key.")
        return response.json({"success": vote_expert_case(app.ctx.node_connection_client, ec_id, option, public_key)})

    # Item registry
    @app.post('/items/add')
    @openapi.definition(
        body=ValidItemAdd,
        summary="Add an item to the registry.",
        response={
            200: {"description": "Item added successfully."},
            400: {"description": "Error due to missing category, item_info or owner_public_key."}
        })
    # @protected
    @validate(json=ValidItemAdd)
    def handle_add_item(request, body: ValidItemAdd):
        category = body.category
        item_info = body.item_info
        public_key = body.public_key
        if not category or not item_info or not public_key:
            raise ServerError("Missing category, item_info or owner_public_key.")

        result = add_item(app.ctx.node_connection_client, category, item_info, public_key)
        if result is None:
            raise ServerError("Error adding item.")
        return response.json({"item_id": result})

    @app.get('/items/<item_id:int>')
    @openapi.definition(
        summary="Get an item by its ID.",
        response={
            200: {"description": "Item retrieved successfully."},
            400: {"description": "Error due to missing item_id."}
        })
    # @protected
    def handle_get_item_by_id(request, item_id):
        item = get_item_by_id(app.ctx.node_connection_client, item_id)
        return response.json({"item": item})


    # Exception handling
    @app.exception(ValidationError)
    def handle_invalid_request(request, exception):
        return response.json(
            {
                "error": "ValidationError",
                "message": exception.message
            },
            status=exception.status_code
        )

    @app.exception(ServerError)
    def handle_server_error(request, exception):
        return response.json(
            {
                "error": "ServerError",
                "message": exception.args[0] if exception.args
                    else "An internal server error occurred."
            },
            status=500
        )


def create_app(arguments):
    "Sanic app factory."
    app = sanic.Sanic("Gateway")
    app.ctx.args = arguments
    app.ctx.challenges = {}
    app.config.SECRET = "secret" #TODO: change this to a more secure secret

    app.ctx.node_connection_client = NodeConnectionClient()

    @app.before_server_start()
    async def node_connection_manager(app):
        # Thread for creating and maintaining connection with Node
        app.ctx.bg_connection_thread = Thread(target=app.ctx.node_connection_client.connection_manager, args=())
        app.ctx.bg_connection_thread.daemon = True
        app.ctx.bg_connection_thread.start()

    @app.before_server_stop
    async def stop_background_thread(app, loop):
        # Garefully close connection with Node
        logger.info("Stopping Node connection manager thread...")
        app.ctx.node_connection_client.exit()
        app.ctx.bg_connection_thread.join()
        logger.info("Node connection manager thread stopped.")

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
