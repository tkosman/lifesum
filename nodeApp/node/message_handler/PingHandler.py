
import sys
from .AbstractHandler import AbstractHandler

sys.path.insert(0, '../../../Message')
from Message import Message, Type


class PingHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message) -> Message | None:
        """Handles messages of type PING.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Ping message.
        """
        return Message(type=Type.PING)