
import os
import sys
from .AbstractHandler import AbstractHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))

from user_register import register_user # type: ignore

class UserRegisterHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message) -> Message | None:
        """Handles messages of type PING.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Ping message.
        """
        register_user()

        return Message(type=Type.RETURN, status=200, payload="User registered succesfully.")