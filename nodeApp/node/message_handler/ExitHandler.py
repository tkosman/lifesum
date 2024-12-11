
import sys
from .AbstractHandler import AbstractHandler

sys.path.insert(0, '../../../Message')
from Message import Message, Type


class ExitHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message) -> Message | None:
        """Handles messages of type EXIT.

        Args:
            message (Message): The message to handle.

        Returns:
            None: Shutting down, no message to send.
        """
        return None