import socket
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import threading
import sys

from user_regitry_interface import UserRegistryInterface
from logger import logger

sys.path.insert(0, '../../Message')
from Message import Message, Type

class GatewayConnectionServer():
    """A class for handling connection between the Node and a Gateway"""
    # def __init__(self, gateway_socket: socket.socket, blockchain: UserRegistryInterface) -> None:
    #     self._gateway_socket: socket.socket = gateway_socket
    #     self._blockchain: UserRegistryInterface = blockchain
    #     self._aes_key: bytes = None
    #     self._running: bool = True

    def __init__(self, gateway_socket: socket.socket) -> None:
        self._gateway_socket: socket.socket = gateway_socket
        self._aes_key: bytes = None
        self._running: bool = True

    def _send(self, message: Message) -> None:
        """Sends data to Gateway.

        Args:
            data (bytes): Data to send.
        """
        try:
            encrypted_message: bytes = self._encrypt(message)
            # Send the length of the data (4 bytes, big-endian)
            self._gateway_socket.send(len(encrypted_message).to_bytes(4, 'big'))
            # Send the actual data
            self._gateway_socket.sendall(encrypted_message)
        except Exception as e:
            logger.error(e)
            raise

    def _receive(self) -> Message:
        """Retrieves message from Gateway.

        Raises:
            ConnectionError: Connection with Gateway broken.

        Returns:
            Message: Decoded message.
        """
        data_length: int = int.from_bytes(self._gateway_socket.recv(4), 'big')
        data: bytes = b""
        while len(data) < data_length:
            packet: bytes = self._gateway_socket.recv(data_length - len(data))
            if not packet:
                raise ConnectionError("Socket connection broken.")
            data += packet

        decrypted_message = self._decrypt(data)
        return Message.from_json(decrypted_message)

    def _send_data(self, data: bytes) -> None:
        """Sends data to Gateway.

        Args:
            data (bytes): Data to send.
        """
        try:
            # Send the length of the data (4 bytes, big-endian)
            self._gateway_socket.send(len(data).to_bytes(4, 'big'))
            # Send the actual data
            self._gateway_socket.sendall(data)
        except Exception as e:
            logger.error(e)
            raise

    def _receive_data(self) -> bytes:
        """Retrieves data from Gateway.

        Raises:
            ConnectionError: Connection with Wateway broken.

        Returns:
            bytes: Recieved data.
        """
        data_length: int = int.from_bytes(self._gateway_socket.recv(4), 'big')
        data: bytes = b""
        while len(data) < data_length:
            packet: bytes = self._gateway_socket.recv(data_length - len(data))
            if not packet:
                raise ConnectionError("Socket connection broken.")
            data += packet
        return data

    def _decrypt(self, encrypted_message: bytes) -> str:
        """Decrypts message using AES key.

        Args:
            encrypted_message (bytes): Message to decrypt.

        Returns:
            str: Decrytped message.
        """
        iv = encrypted_message[:16]
        ciphertext = encrypted_message[16:]
        cipher = Cipher(algorithms.AES(self._aes_key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def _encrypt(self, message: Message) -> bytes:
        """Encrypts message using AES key.

        Args:
            message (Message): Message to encrypt.

        Returns:
            bytes: Encrypted message.
        """
        message_json = message.to_bytes()

        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self._aes_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        return iv + encryptor.update(message_json) + encryptor.finalize()

    # TODO: change the DH to more secure version
    def _DH_exchange(self) -> bytes:
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
            self._send_data(dh_parameters_pem)
            logger.info(f"Sent new DH parameters to {threading.current_thread().name}.")

            # Generate server's private and public keys
            server_private_key = parameters.generate_private_key()
            server_public_key = server_private_key.public_key()

            # Send server's public key to the client
            server_public_key_pem = server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self._send_data(server_public_key_pem)

            # _receive client's public key
            client_public_key_pem = self._receive_data()
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
            logger.error(e)
            return None

    def _handle_message(self, message: Message) -> None:
        """Handles message received from Gateway

        Args:
            message (Message): Message to handle.
        """
        self._send(message)

    def handle_client(self) -> None:
        """Executed in new thread to handle comunication between Gateway nad Node.

        Raises:
            ConnectionError: Error during Diffie-Hellman exchange.
        """
        try:
            self._aes_key = self._DH_exchange()

            if self._aes_key:
                logger.info(f"Shared AES key established with {threading.current_thread().name}.")
            else:
                raise ConnectionError("Error during DH exchange. Terminating connection...")

            # Communication loop for this client
            while self._running:
                message: Message = self._receive()

                # Handle message
                try:
                    # ! update message handling
                    self._handle_message(message)
                except ConnectionAbortedError:
                    break
        except Exception as e:
            logger.error(f"Error handling {threading.current_thread().name}: {e}.")
        finally:
            logger.info(f"Closing socket for connection with {threading.current_thread().name}.")
            self._gateway_socket.close()

    def exit(self) -> None:
        """Gracefully close connection with Gateway."""
        self._running = False
        self._gateway_socket.close()
