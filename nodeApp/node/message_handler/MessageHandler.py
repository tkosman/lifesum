
import sys
from .ExitHandler import ExitHandler
from .AbstractHandler import AbstractHandler

sys.path.insert(0, '../../../Message')
from Message import Message, Type


class MessageHandler(AbstractHandler):

    handlers: dict[Type, AbstractHandler] = {
        Type.EXIT: ExitHandler,
    }

    @classmethod
    def handle(self, message: Message) -> Message | None:
        """Handles a message.

        Args:
            message (Message): The message to handle.

        Returns:
            Message|None: Return message; *None* if a *KeyError* occurs.
        """
        try:
            return_message: Message = self.handlers.get(Message.get_type()).handle(message)
        except KeyError as ex:
            print(ex)
            return None

        return return_message
