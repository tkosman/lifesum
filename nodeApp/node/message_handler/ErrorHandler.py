
import os
import sys
from .AbstractHandler import AbstractHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type


class ErrorHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message) -> Message | None:
        """Handles messages of type ERROR.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Error with status 500 for unknown message type.
        """
        return Message(type=Type.ERROR, status=500, payload=f"Unknown message type: {message.get_type()}")
