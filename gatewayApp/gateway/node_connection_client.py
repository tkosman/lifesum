import socket
import time
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import sys

import node_connection

sys.path.insert(0, '../../Message')
from Message import *

# TODO: replace with actual address
HOST = '127.0.0.1'
PORT = 65432

ATTEMPTS = 3
REFRACTORY_PERIOD = 1 #[s]

# Helper functions for sending/receiving data
def send_data(socket: socket, data: bytes) -> None:
    """Sends data to Node

    Args:
        sock (socket): Socket for communication
        data (bytes): Data to send.
    """
    try:
        # Send the length of the data (4 bytes, big-endian)
        socket.send(len(data).to_bytes(4, 'big'))
        # Send the actual data
        socket.sendall(data)
    except Exception as e:
        print(e)
        raise

def receive_data(socket: socket) -> bytes:
    """Retrieves message from Node.

    Args:
        sock (socket): Socket for communication.

    Raises:
        ConnectionError: Connection with Node broken.

    Returns:
        bytes: Encoded message.
    """
    data_length: int = int.from_bytes(socket.recv(4), 'big')
    data: bytes = b""
    while len(data) < data_length:
        packet: bytes = socket.recv(data_length - len(data))
        if not packet:
            raise ConnectionError("Socket connection broken")
        data += packet
    return data

def decrypt(encrypted_message: bytes, aes_key: bytes) -> str:
    """Decrypts message using AES key.

    Args:
        encrypted_message (bytes): Message to decrypt.
        aes_key (bytes): AES key.

    Returns:
        str: Decrytped message.
    """
    iv = encrypted_message[:16]
    ciphertext = encrypted_message[16:]
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt(message: Message, aes_key: bytes) -> bytes:
    """Encrypts message using AES key.

    Args:
        message (Message): Message to encrypt.
        aes_key (bytes): AES key.

    Returns:
        bytes: Encrypted message.
    """
    message_json = message.to_bytes()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    return iv + encryptor.update(message_json) + encryptor.finalize()

# TODO: change the DH to more secure version
def DH_exchange(socket: socket) -> bytes:
    """Executes Diffie-Hellman key exchange and establishes connection
    between Gateway and Node.

    Args:
        socket (socket): Socket for communication.

    Returns:
        bytes: AES key.
    """
    try:
        socket.connect((HOST, PORT))
        print("Connected to the server.")
        print("Initiating DH exchange.")

        # Receive the DH parameters (this is just the parameters, not a private key)
        dh_parameters_pem: bytes = receive_data(socket)
        print("DH parameters received")

        # Load DH parameters
        parameters = serialization.load_pem_parameters(dh_parameters_pem)

        #! private key will be predetermined
        # Generate the client's private key using the received parameters
        client_private_key = parameters.generate_private_key()

        # Generate the client's public key
        client_public_key = client_private_key.public_key()
        print("Key pair generated")

        # Send client's public key to the server
        client_public_key_pem: bytes = client_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        send_data(socket, client_public_key_pem)
        print("Key pem send")

        # Receive server's public key
        server_public_key_pem: bytes = receive_data(socket)
        server_public_key = serialization.load_pem_public_key(server_public_key_pem)
        print("Key pem received")

        # Perform Diffie-Hellman key exchange
        shared_key: bytes = client_private_key.exchange(server_public_key)

        # Derive AES key
        aes_key: bytes = HKDF(
            algorithm=SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)

        return aes_key
    except Exception as e:
        print(e)
        return None

def establish_connection(node_socket: socket) -> bytes:
    """Establishes connection with Node.

    Args:
        node_socket (socket): Socket for communication.

    Raises:
        ConnectionError: Couldn't connect to Node.

    Returns:
        bytes: AES key.
    """
    for attempt in range(ATTEMPTS):
            try:
                aes_key = DH_exchange(node_socket)
                if aes_key:
                    print("Connection established.")
                    return aes_key
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")

            time.sleep(REFRACTORY_PERIOD)

            if attempt == ATTEMPTS - 1:
                print("All connection attempts failed. Exiting...")
                raise ConnectionError("Error trying to connect with Node")

def process_message(message: Message) -> None:
    """Processes message.

    Args:
        message (Message): Message to process.
    """
    print(f"Return message: {message.get_payload()}")

def handle_message(message: Message, node_socket: socket , aes_key: bytes) -> None:
    """Handles message received from Gateway

    Args:
        message (Message): Message to handle.
        node_socket (socket): Client's socket for sending response.
        aes_key (bytes): Encryption key.

    Raises:
        ConnectionAbortedError: Gateway broke connection.
    """
    match message.get_type():
        case Type.RETURN:
            process_message(message)

        case Type.ERROR:
            if message.get_status() >= 400 and message.get_status() < 500:
                # TODO: deal with "unrecognized message type" error
                print(f"Erroe message: {message.to_json()}")
            elif message.get_status() >= 500 and message.get_status() < 600:
                # TODO: resend last message
                print(f"Error message: {message.to_json()}")

        case _:
            #! Bad request 400
            response = Message(type=Type.ERROR, status=400, payload=f"Unrecognized message type: {message.get_type()}")
            encrypted_response = encrypt(response, aes_key)

            send_data(node_socket, encrypted_response)

def main():
    """Manages connection between Gateway and Node.

    Raises:
        ConnectionError: Error during Diffie-Hellman exchange.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:

        # Establishing connection and common key
        aes_key = establish_connection(node_socket)

        if aes_key:
            print(f"Shared AES key established with the Node")
        else:
            raise ConnectionError("Error during DH exchange. Terminating connection...")

        # Connection loop
        while True:
            input_message: str = input("Enter message payload (or type 'exit' to disconnect): ")

            # Prepare message
            if input_message != "exit":
                message: Message = Message(type=Type.REQUEST, payload=input_message)
            else:
                message: Message = Message(type=Type.EXIT)

            encrypted_message = encrypt(message, aes_key)

            send_data(node_socket, encrypted_message)

            #! Handle EXIT
            if input_message == "exit":
                print("Closing connection")
                node_socket.close()
                break

            # Receive encrypted response
            encrypted_response: bytes = receive_data(node_socket)
            decrypted_response: Message = decrypt(encrypted_response, aes_key)

            try:
                response = Message.from_json(decrypted_response)
            except ValueError as ex:
                #! Checksum error 500
                print(ex)

                response = Message(type=Type.ERROR, status=500, payload=str(ex))
                encrypted_response = encrypt(response, aes_key)

                send_data(node_socket, encrypted_response)

                continue

            handle_message(response, node_socket, aes_key)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
