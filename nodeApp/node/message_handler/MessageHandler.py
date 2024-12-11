
import sys
from .ExitHandler import ExitHandler
from .PingHandler import PingHandler
from .ErrorHandler import ErrorHandler
from .AbstractHandler import AbstractHandler

sys.path.insert(0, '../../../Message')
from Message import Message, Type


class MessageHandler:

    handlers: dict[Type, AbstractHandler] = {
        Type.PING: PingHandler,
        Type.EXIT: ExitHandler,
    }

    @classmethod
    def handle(self, message: Message) -> Message:
        """Handles a message.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Return message.
        """
        return self.handlers.get(message.get_type(), ErrorHandler).handle(message)
