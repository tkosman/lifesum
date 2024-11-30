import socket
import threading
import time
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import sys

from sanic.log import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

class NodeConnectionClient():
    """A class for handling connection between the Gateway and a Node."""
    # TODO replace with actual address
    HOST: str = '127.0.0.1'
    PORT: int = 65432
    ATTEMPTS: int = 3
    REFRACTORY_PERIOD: int = 1 #[s]
    TIMEOUT: int = 3 #[s]
    PING_INTERVAL: int = 120 #[s]

    def __init__(self) -> None:
        self.node_socket: socket.socket = None
        self._aes_key: bytes = None
        self._running: bool = False


    def send(self, message: Message) -> None:
        """Sends data to Node.

        Args:
            data (bytes): Data to send.
        """
        try:
            encrypted_message: bytes = self._encrypt(message)
            # Send the length of the data (4 bytes, big-endian)
            self.node_socket.send(len(encrypted_message).to_bytes(4, 'big'))
            # Send the actual data
            self.node_socket.sendall(encrypted_message)
        except Exception as e:
            logger.error(e)
            raise

    def receive(self) -> Message:
        """Retrieves message from Node.

        Raises:
            ConnectionError: Connection with Node broken.

        Returns:
            Message: Decoded message.
        """
        data_length: int = int.from_bytes(self.node_socket.recv(4), 'big')
        data: bytes = b""
        while len(data) < data_length:
            packet: bytes = self.node_socket.recv(data_length - len(data))
            if not packet:
                raise ConnectionError("Socket connection broken")
            data += packet

        decrypted_message = self._decrypt(data)
        return Message.from_json(decrypted_message)


    def _send_data(self, data: bytes) -> None:
        """Sends data to Node.

        Args:
            data (bytes): Data to send.
        """
        try:
            # Send the length of the data (4 bytes, big-endian)
            self.node_socket.send(len(data).to_bytes(4, 'big'))
            # Send the actual data
            self.node_socket.sendall(data)
        except Exception as e:
            logger.error(e)
            raise

    def _receive_data(self) -> bytes:
        """Retrieves data from Node.

        Raises:
            ConnectionError: Connection with Node broken.

        Returns:
            bytes: Recieved data.
        """
        data_length: int = int.from_bytes(self.node_socket.recv(4), 'big')
        data: bytes = b""
        while len(data) < data_length:
            packet: bytes = self.node_socket.recv(data_length - len(data))
            if not packet:
                raise ConnectionError("Socket connection broken")
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

        Returns:
            bytes: AES key.
        """
        try:
            self.node_socket.connect((NodeConnectionClient.HOST, NodeConnectionClient.PORT))
            logger.info("Connected to the server.")
            logger.info("Initiating DH exchange.")

            # Receive the DH parameters (this is just the parameters, not a private key)
            dh_parameters_pem: bytes = self._receive_data()
            logger.info("DH parameters received")

            # Load DH parameters
            parameters = serialization.load_pem_parameters(dh_parameters_pem)

            #! private key will be predetermined
            # Generate the client's private key using the received parameters
            client_private_key = parameters.generate_private_key()

            # Generate the client's public key
            client_public_key = client_private_key.public_key()
            logger.info("Key pair generated")

            # Send client's public key to the server
            client_public_key_pem: bytes = client_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self._send_data(client_public_key_pem)
            logger.info("Key pem send")

            # Receive server's public key
            server_public_key_pem: bytes = self._receive_data()
            server_public_key = serialization.load_pem_public_key(server_public_key_pem)
            logger.info("Key pem received")

            # Perform Diffie-Hellman key exchange
            shared_key: bytes = client_private_key.exchange(server_public_key)

            # Derive AES key
            self._aes_key = HKDF(
                algorithm=SHA256(),
                length=32,
                salt=None,
                info=b'handshake data'
            ).derive(shared_key)

            return self._aes_key
        except Exception as e:
            logger.error(e)
            return None

    def _establish_connection(self) -> bytes:
        """Establishes connection with Node.

        Raises:
            ConnectionError: Couldn't connect to Node.

        Returns:
            bytes: AES key.
        """
        for attempt in range(NodeConnectionClient.ATTEMPTS):
            try:
                self._aes_key = self._DH_exchange()
                if self._aes_key:
                    logger.info("Connection established.")
                    return self._aes_key
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")

            time.sleep(NodeConnectionClient.REFRACTORY_PERIOD)

            if attempt == NodeConnectionClient.ATTEMPTS - 1:
                logger.fatal("All connection attempts failed.")
                return None

    def connection_manager(self) -> None:
        """Manages connection between Gateway and Node.

        Raises:
            ConnectionError: Error during Diffie-Hellman exchange.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:

            self.node_socket = node_socket

            # Establishing connection and common key
            self._aes_key = self._establish_connection()

            if self._aes_key:
                logger.info(f"Shared AES key established with the Node")
                self._running = True
            else:
                logger.fatal("No aes key. Exiting...")
                self.exit()
                return

            self.node_socket.settimeout(NodeConnectionClient.TIMEOUT)

            next_ping_time = time.time()

            try:
                while self._running:
                    # Ping the Node
                    current_time = time.time()
                    if current_time >= next_ping_time:
                        self.send(Message(Type.PING))
                        t = time.time_ns()
                        next_ping_time = current_time + NodeConnectionClient.PING_INTERVAL

                        try:
                            response = self.receive()

                            if response.get_type() == Type.PING:
                                logger.info(f"Ping {(time.time_ns() - t) * 10e-6}ms")
                            else:
                                logger.error(f"Wrong response type {response.get_type()}")
                                break
                        except ValueError as ex:
                            logger.error(f"Checksum error: {ex}")
                        except socket.timeout:
                            logger.error("Socket timeout.")
                            break
            except Exception as ex:
                logger.error(f"Unexpected error: {ex}")
            finally:
                self.exit()

    def exit(self) -> None:
        """Sends message to the Node to gracefully close connection and closes socket."""
        if self._running:
            self.send(Message(Type.EXIT))
            self._running = False
        self.node_socket.close()
