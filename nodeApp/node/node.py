
import socket
import threading
from gateway_connection_server import GatewayConnectionServer
from user_regitry_interface import *

from logger import logger

__version__ = "1.0.0"

# TODO: replace with actual address
HOST: str = '127.0.0.1'
PORT: int = 65432
BACKLOG: int = 5

client_handlers: list[GatewayConnectionServer] = []
client_threads: list[threading.Thread] = []

def node() -> None:
    print(rf"""{'\033[95m'}
           __ _  __
          / /(_)/ _| ___  ___ _   _ _ __ ___
         / / | | |_ / _ \/ __| | | | '_ ` _ \
        / /__| |  _|  __/\__ \ |_| | | | | | |
        \____/_|_|  \___||___/\__,_|_| |_| |_|
        {'\033[32m'}Welcome to the Node. {'\033[93m'}{__version__}{'\033[0m'}
    """)

    try:
        blockchain_interface = UserRegistryInterface()
    except Exception as ex:
        # TODO : handle exceptions
        logger.error(ex)

    try:
        # Start listening for connections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(BACKLOG)
        logger.info("Server listening...")

        while server_socket.fileno() != -1:
            gateway_socket, client_address = server_socket.accept()
            logger.access(f"Connection from {client_address}.")

            gateway_handler: GatewayConnectionServer = GatewayConnectionServer(gateway_socket, blockchain_interface)
            client_handlers.append(gateway_handler)

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=gateway_handler.handle_client, name=str(client_address), args=())
            client_threads.append(client_thread)
            client_thread.start()
    except Exception as e:
        logger.error(f"Error in main server loop: {e}.")
    finally:
        server_socket.close()

        for handler in client_handlers:
            try:
                handler.exit()
            except Exception as e:
                logger.error(f"Error terminating handler: {e}.")
        client_handlers.clear()

        for thread in client_threads:
            if thread.is_alive():
                thread.join(timeout=1)

        logger.info("Server stopped.")

if __name__ == "__main__":
    node()
