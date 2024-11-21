import base64
import socket
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import threading
import sys

sys.path.insert(0, '../../Message')
from Message import *


# TODO: replace with actual address
HOST = '127.0.0.1'
PORT = 65432
BACKLOG = 5

client_sockets = []
client_threads = []
server_socket = None

# Helper functions for sending/receiving data
def send_data(sock, data):
    sock.send(len(data).to_bytes(4, 'big'))
    sock.sendall(data)

def receive_data(sock):
    data_length = int.from_bytes(sock.recv(4), 'big')
    data = b""
    while len(data) < data_length:
        packet = sock.recv(data_length - len(data))
        if not packet:
            raise ConnectionError(f"Socket connection with {threading.current_thread().name} broken")
        data += packet
    return data

def handle_client(client_socket):
    try:
        # Generate new DH parameters for this connection
        parameters = dh.generate_parameters(generator=2, key_size=2048)
        dh_parameters_pem = parameters.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3
        )

        # Send the DH parameters to the client
        send_data(client_socket, dh_parameters_pem)
        print(f"Sent new DH parameters to {threading.current_thread().name}")

        # Generate server's private and public keys
        server_private_key = parameters.generate_private_key()
        server_public_key = server_private_key.public_key()

        # Send server's public key to the client
        server_public_key_pem = server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        send_data(client_socket, server_public_key_pem)

        # Receive client's public key
        client_public_key_pem = receive_data(client_socket)
        client_public_key = serialization.load_pem_public_key(client_public_key_pem)

        # Generate shared secret
        shared_key = server_private_key.exchange(client_public_key)

        # Derive AES key
        aes_key = HKDF(
            algorithm=SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)

        print(f"Shared AES key established with {threading.current_thread().name}")

        # Communication loop for this client
        while True:
            encrypted_message = receive_data(client_socket)

            # Decrypt the message
            iv = encrypted_message[:16]
            ciphertext = encrypted_message[16:]
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            decryptor = cipher.decryptor()
            decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

            # Parse and process the message
            message = Message.from_json(decrypted_message)
            if message.get_payload():
                print(f"Received message from {threading.current_thread().name}: {message.get_payload()}")
            else:
                print(f"Received message from {threading.current_thread().name}: {message.get_type().value}")
            
            if message.get_type() == Type.EXIT:
                print(f"Connection ended by {threading.current_thread().name}")
                break
            
            try:
                # Respond to the client
                response = Message(type=Type.RETURN, status=200, payload=message.get_payload())
                response_json = response.to_bytes()

                # Encrypt the response
                iv = os.urandom(16)
                cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
                encryptor = cipher.encryptor()
                encrypted_response = iv + encryptor.update(response_json) + encryptor.finalize()

                # Send the encrypted response back to the client
                send_data(client_socket, encrypted_response)
            except ValueError as ex:
                print(ex)
                #TODO: ask for resend
                continue
            
    # except Exception as e:
    #     print(f"Error handling {threading.current_thread().name}: {e}")
    finally:
        print(f"Closing socket for connection with {threading.current_thread().name}")
        client_socket.close()

def main():
    global server_socket, client_sockets, client_threads

    try:
        # Start listening for connections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(BACKLOG)
        print("Server listening...")

        while server_socket.fileno() != -1:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            client_sockets.append(client_socket)

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, name=str(client_address), args=(client_socket,))
            client_threads.append(client_thread)
            client_thread.start()

    except Exception as e:
        print(f"Error in main server loop: {e}")
    finally:
        server_socket.close()

        for sock in client_sockets:
            try:
                sock.close()
            except Exception as e:
                print(f"Error closing client socket: {e}")
        client_sockets.clear()
        
        for thread in client_threads:
            if thread.is_alive():
                thread.join(timeout=1)
                
        print("Server stopped.")
        
        
if __name__ == "__main__":
    main()