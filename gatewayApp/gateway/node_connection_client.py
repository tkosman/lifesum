import base64
import socket
import json
import hashlib
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

# Helper functions for sending/receiving data
def send_data(socket: socket, data: bytes) -> None:
    try:
        # Send the length of the data (4 bytes, big-endian)
        socket.send(len(data).to_bytes(4, 'big'))
        # Send the actual data
        socket.sendall(data)
    except Exception as e:
        print(e)
        raise


def receive_data(socket: socket) -> bytes:
    data_length: int = int.from_bytes(socket.recv(4), 'big')
    data: bytes = b""
    while len(data) < data_length:
        packet: bytes = socket.recv(data_length - len(data))
        if not packet:
            raise ConnectionError("Socket connection broken")
        data += packet
    return data

def initiate_connection(socket: socket) -> bytes:
    try:
        socket.connect((HOST, PORT))
        print("Connected to the server.")

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

def process_message():
    ...

def handle_response(response: Message):
    print(f"Server responsponded with code: {response.get_status()}")
    print(f"Message payload: {response.get_payload()}")


def main():
    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        
        # Establishing connection and common key
        for attempt in range(ATTEMPTS):
            try:
                aes_key = initiate_connection(client_socket)
                if aes_key:
                    print("Connection established.")
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
            if attempt == ATTEMPTS - 1:
                print("All connection attempts failed. Exiting...")
                raise ConnectionError("Error trying to connect with Node")

        print("Shared AES key established with server.")

        # Connection loop
        while True:
            message: str = input("Enter JSON message (or type 'exit' to disconnect): ")

            # Prepare the message as a JSON object
            if message != "exit":
                message_json: bytes = Message(type=Type.REQUEST, payload=message).to_bytes()
            else: 
                message_json: bytes = Message(type=Type.EXIT).to_bytes()

            # Encrypt the message
            iv: bytes = os.urandom(16)
            cipher: Cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            encryptor = cipher.encryptor()
            encrypted_message: bytes = iv + encryptor.update(message_json) + encryptor.finalize()

            # Send the encrypted message directly
            send_data(client_socket, encrypted_message)
    
            if message == "exit":
                print("Closing connection")
                client_socket.close()
                break

            # Receive the server's encrypted response
            encrypted_response: bytes = receive_data(client_socket)

            # Decrypt the response
            iv: bytes = encrypted_response[:16]
            ciphertext: bytes = encrypted_response[16:]
            cipher: Cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            decryptor = cipher.decryptor()
            decrypted_response: bytes = decryptor.update(ciphertext) + decryptor.finalize()

            # Verify checksum
            response = Message.from_json(decrypted_response)
            handle_response(response)
            

if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except Exception as e:
    #     print(e)
