import socket
import time
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Message')))
from Message import Message, Type

class NodeConnectionClient():
    """A class for handling connection between the Gateway and a Node"""
    def __init__(self):
        # TODO replace with actual address
        self.HOST: str = '127.0.0.1'
        self.PORT: int = 65432
        self.node_socket: socket = None

        self.__aes_key = None

        self.ATTEMPTS: int = 3
        self.REFRACTORY_PERIOD: int = 1 #[s]
        self.TIMEOUT: int = 3 #[s]
        self.PING_INTERVAL: int = 120 #[s]

        self.running = True


    def send(self, message: Message) -> None:
        """Sends data to Node

        Args:
            data (bytes): Data to send.
        """
        try:
            encrypted_message: bytes = self.__encrypt(message)
            # Send the length of the data (4 bytes, big-endian)
            self.node_socket.send(len(encrypted_message).to_bytes(4, 'big'))
            # Send the actual data
            self.node_socket.sendall(encrypted_message)
        except Exception as e:
            print(e)
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

        decrypted_message = self.__decrypt(data)
        return Message.from_json(decrypted_message)


    def __send_data(self, data: bytes) -> None:
        """Sends data to Node

        Args:
            data (bytes): Data to send.
        """
        try:
            # Send the length of the data (4 bytes, big-endian)
            self.node_socket.send(len(data).to_bytes(4, 'big'))
            # Send the actual data
            self.node_socket.sendall(data)
        except Exception as e:
            print(e)
            raise

    def __receive_data(self) -> bytes:
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

    def __decrypt(self, encrypted_message: bytes) -> str:
        """__decrypts message using AES key.

        Args:
            encrypted_message (bytes): Message to decrypt.

        Returns:
            str: Decrytped message.
        """
        iv = encrypted_message[:16]
        ciphertext = encrypted_message[16:]
        cipher = Cipher(algorithms.AES(self.__aes_key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def __encrypt(self, message: Message) -> bytes:
        """__encrypts message using AES key.

        Args:
            message (Message): Message to __encrypt.

        Returns:
            bytes: __encrypted message.
        """
        message_json = message.to_bytes()

        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.__aes_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        return iv + encryptor.update(message_json) + encryptor.finalize()

    # TODO: change the DH to more secure version
    def __DH_exchange(self) -> bytes:
        """Executes Diffie-Hellman key exchange and establishes connection
        between Gateway and Node.

        Returns:
            bytes: AES key.
        """
        try:
            self.node_socket.connect((self.HOST, self.PORT))
            print("Connected to the server.")
            print("Initiating DH exchange.")

            # Receive the DH parameters (this is just the parameters, not a private key)
            dh_parameters_pem: bytes = self.__receive_data()
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
            self.__send_data(client_public_key_pem)
            print("Key pem send")

            # Receive server's public key
            server_public_key_pem: bytes = self.__receive_data()
            server_public_key = serialization.load_pem_public_key(server_public_key_pem)
            print("Key pem received")

            # Perform Diffie-Hellman key exchange
            shared_key: bytes = client_private_key.exchange(server_public_key)

            # Derive AES key
            self.__aes_key: bytes = HKDF(
                algorithm=SHA256(),
                length=32,
                salt=None,
                info=b'handshake data'
            ).derive(shared_key)

            return self.__aes_key
        except Exception as e:
            print(e)
            return None

    def __establish_connection(self) -> bytes:
        """Establishes connection with Node.

        Raises:
            ConnectionError: Couldn't connect to Node.

        Returns:
            bytes: AES key.
        """
        for attempt in range(self.ATTEMPTS):
                try:
                    self.__aes_key = self.__DH_exchange()
                    if self.__aes_key:
                        print("Connection established.")
                        return self.__aes_key
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")

                time.sleep(self.REFRACTORY_PERIOD)

                if attempt == self.ATTEMPTS - 1:
                    print("All connection attempts failed. Exiting...")
                    raise ConnectionError("Error trying to connect with Node")

    def connection_manager(self):
        """Manages connection between Gateway and Node.

        Raises:
            ConnectionError: Error during Diffie-Hellman exchange.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:

            self.node_socket = node_socket

            # Establishing connection and common key
            self.__aes_key = self.__establish_connection()

            if self.__aes_key:
                print(f"Shared AES key established with the Node")
            else:
                raise ConnectionError("Error during DH exchange. Terminating connection...")

            self.node_socket.settimeout(self.TIMEOUT)

            next_ping_time = time.time()

            try:
                while self.running:
                    # Ping the Node
                    current_time = time.time()
                    if current_time >= next_ping_time:
                        self.send(Message(Type.PING))
                        t = time.time_ns()
                        next_ping_time = current_time + self.PING_INTERVAL

                        try:
                            response = self.receive()

                            if response.get_type() == Type.PING:
                                print(f"Ping {(time.time_ns() - t) * 10e-6}ms")
                            else:
                                print(f"Wrong response type {response.get_type()}")
                                break
                        except ValueError as ex:
                            print(f"Checksum error: {ex}")
                        except socket.timeout:
                            print("Socket timeout.")
                            break
            except Exception as ex:
                print(f"Unexpected error: {ex}")
            finally:
                self.node_socket.close()

    def exit(self) -> None:
        """Sends message to the Node to gracefully close connection and closes socket."""
        self.send(Message(Type.EXIT))
        self.running = False
        self.node_socket.close()

