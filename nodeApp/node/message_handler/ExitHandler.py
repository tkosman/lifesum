
import sys
from .AbstractHandler import AbstractHandler

sys.path.insert(0, '../../../Message')
from Message import Message, Type


class ExitHandler(AbstractHandler):

    @classmethod
    def handle(self, Message: Message) -> Message:
        """Handles messages of type EXIT.

        Args:
            message (Message): The message to handle.

        Returns:
            Message|None: Return message; *None* if a *KeyError* occurs.
        """
        ...