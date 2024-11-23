import socket
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
def send_data(sock:  socket, data: bytes) -> None:
    """Sends data to Gateway

    Args:
        sock (socket): Socket for communication
        data (bytes): Data to send.
    """
    sock.send(len(data).to_bytes(4, 'big'))
    sock.sendall(data)

def receive_data(sock: socket) -> bytes:
    """Retrieves message from Gateway.

    Args:
        sock (socket): Socket for communication.

    Raises:
        ConnectionError: Connection with Gateway broken.

    Returns:
        bytes: Encoded message.
    """
    data_length = int.from_bytes(sock.recv(4), 'big')
    data = b""
    while len(data) < data_length:
        packet = sock.recv(data_length - len(data))
        if not packet:
            raise ConnectionError(f"Socket connection with {threading.current_thread().name} broken")
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
        # Generate new DH parameters for this connection
        parameters = dh.generate_parameters(generator=2, key_size=2048)
        dh_parameters_pem = parameters.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3
        )

        # Send the DH parameters to the client
        send_data(socket, dh_parameters_pem)
        print(f"Sent new DH parameters to {threading.current_thread().name}")

        # Generate server's private and public keys
        server_private_key = parameters.generate_private_key()
        server_public_key = server_private_key.public_key()

        # Send server's public key to the client
        server_public_key_pem = server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        send_data(socket, server_public_key_pem)

        # Receive client's public key
        client_public_key_pem = receive_data(socket)
        client_public_key = serialization.load_pem_public_key(client_public_key_pem)

        # Generate shared secret
        shared_key = server_private_key.exchange(client_public_key)

        # Derive AES key
        return HKDF(
            algorithm=SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)
    except Exception as e:
        print(e)
        return None
        
def handle_message(message: Message, gateway_socket: socket , aes_key: bytes) -> None:
    """Handles message received from Gateway

    Args:
        message (Message): Message to handle.
        gateway_socket (socket): Client's socket for sending response.
        aes_key (bytes): Encryption key.

    Raises:
        ConnectionAbortedError: Gateway broke connection.
    """
    match message.get_type():
        case Type.REQUEST:
            print(f"Received message from {threading.current_thread().name}: {message.get_payload()}")
            response = Message(type=Type.RETURN, status=200, payload=message.get_payload())
            encrypted_response = encrypt(response, aes_key)

            send_data(gateway_socket, encrypted_response)

        case Type.EXIT:
            print(f"Connection ended by {threading.current_thread().name}")
            raise ConnectionAbortedError
        
        case Type.ERROR:
            if message.get_status() >= 400 and message.get_status() < 500:
                # TODO: deal with "unrecognized message type" error
                print(f"Error message: {message.to_json()}")
            elif message.get_status() >= 500 and message.get_status() < 600:
                # TODO: resend last message
                print(f"Error message: {message.to_json()}")

        case _:
            #! Bad request 400
            response = Message(type=Type.ERROR, status=400, payload=f"Unrecognized message type: {message.get_type()}")
            encrypted_response = encrypt(response, aes_key)

            send_data(gateway_socket, encrypted_response)
            
def handle_client(gateway_socket):
    """Executed in new thread to handle comunication between Gateway nad Node.

    Args:
        gateway_socket (_type_): Socket for communication.

    Raises:
        ConnectionError: Error during Diffie-Hellman exchange.
    """
    try:
        aes_key = DH_exchange(gateway_socket)

        if aes_key:
            print(f"Shared AES key established with {threading.current_thread().name}")
        else:
            raise ConnectionError("Error during DH exchange. Terminating connection...")
            
        # Communication loop for this client
        while True:
            encrypted_message = receive_data(gateway_socket)
            
            decrypted_message = decrypt(encrypted_message, aes_key)

            # Parse and process the message
            try:
                message = Message.from_json(decrypted_message)
            except ValueError as ex:
                #! Checksum error 500
                print(ex)
                
                response = Message(type=Type.ERROR, status=500, payload=str(ex))
                encrypted_response = encrypt(response, aes_key)

                send_data(gateway_socket, encrypted_response)

                continue
            
            # Handle message
            try:
                handle_message(message, gateway_socket, aes_key)
            except ConnectionAbortedError as ex:
                break
    except Exception as e:
        print(f"Error handling {threading.current_thread().name}: {e}")
    finally:
        print(f"Closing socket for connection with {threading.current_thread().name}")
        gateway_socket.close()

def main():
    """Main thread receiving new connection requests and delegating 
    their handling to new threads.
    """
    global server_socket, client_sockets, client_threads

    try:
        # Start listening for connections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(BACKLOG)
        print("Server listening...")

        while server_socket.fileno() != -1:
            gateway_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            client_sockets.append(gateway_socket)

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, name=str(client_address), args=(gateway_socket,))
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
    try:
        main()
    except Exception as e:
        print(e)
