
import os
import sys
from .ExitHandler import ExitHandler
from .PingHandler import PingHandler
from .ErrorHandler import ErrorHandler
from .UserRegisterHandler import UserRegisterHandler
from .AbstractHandler import AbstractHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type


class MessageHandler:

    handlers: dict[Type, AbstractHandler] = {
        Type.PING: PingHandler,
        Type.EXIT: ExitHandler,
        Type.REGISTER: UserRegisterHandler,
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
