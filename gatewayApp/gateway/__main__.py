"""
Sanic app.
"""
import argparse

import sanic
from sanic import response, request

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

def attach_endpoints(app):
    """Attach endpoints to the app."""
    @app.route('/')
    async def index(request: request.Request):
        return response.json('Hello, world!')

def create_app(arguments):
    "Sanic app factory."
    app = sanic.Sanic("Application")
    app.ctx.args = arguments

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
