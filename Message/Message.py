
import hashlib
import json

from MessageTypes import Type

class Message():
    """Message class.

    Args:
        type (Type, optional): Type of the message. Defaults to None.
        status (int, optional): Returning status. Defaults to None.
        payload (str, optional): Data to send. Defaults to None.
    """

    def __init__(self, type: Type = None, status: int = None, payload: str = None) -> None:
        self.__type: Type = type
        self.__status: int = status
        self.__payload: str = payload
        self.__checksum: str = self.__generate_checksum() if payload else None


    def set_type(self, type: Type) -> None:
        self.__type = type

    def get_type(sefl) -> Type:
        return sefl.__type

    def set_status(self, status: int) -> None:
        self.__status = status

    def get_status(sefl) -> int:
        return sefl.__status

    def set_payload(self, payload: str) -> None:
        self.__payload = payload

    def get_payload(sefl) -> str:
        return sefl.__payload

    def __generate_checksum(self) -> None:
        """Generate a SHA-256 checksum for the given data."""
        return hashlib.sha256(self.__payload.encode('utf-8')).hexdigest()

    def check_checksum(self, checksum: str) -> bool:
        """Verifies message checksum.

        Args:
            checksum (str): Checksum to verify against.

        Returns:
            bool: Verification resoult.
        """
        return self.__checksum == checksum

    def to_json(self) -> str:
        """Convert the message to a JSON string.

        Returns:
            str: Json dump of this Message.
        """
        return json.dumps({
            'type': self.__type.value,
            'status': self.__status,
            'payload': self.__payload,
            'checksum': self.__checksum
        })

    def to_bytes(self) -> bytes:
        """Convert the message to bytes using UTF-8 encoding.

        Returns:
            bytes: Json dump of this Message encoded in utf-8.
        """
        return self.to_json().encode('utf-8')


    @classmethod
    def from_json(cls, json_string: str) -> "Message":
        """Create an instance from a JSON string.

        Args:
            json_string (str): Serialized Message object.

        Raises:
            ValueError: Checksum mismatch.

        Returns:
            Message: Deserialized Message object.
        """
        data = json.loads(json_string)
        message = cls(type=Type(data['type']), status=data['status'], payload=data['payload'])

        if message.check_checksum(data['checksum']):
            return message
        else:
            raise ValueError("Checksum not matching, message corrupted")
