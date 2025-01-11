
import os
import sys
from .ExitHandler import ExitHandler
from .PingHandler import PingHandler
from .ErrorHandler import ErrorHandler
from .UserRegisterHandler import UserRegisterHandler
from .AbstractHandler import AbstractHandler
from .UserExistsHandler import UserExistsHandler
from .GetPubKeyHandler import GetPubKeyHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class MessageHandler:

    handlers: dict[Type, AbstractHandler] = {
        Type.PING: PingHandler,
        Type.EXIT: ExitHandler,
        Type.REGISTER: UserRegisterHandler,
        Type.USREXISTS: UserExistsHandler,
        Type.GETPUBKEY: GetPubKeyHandler,
    }

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message:
        """Handles a message.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Return message.
        """
        # Default to ErrorHandler if message type not recognized
        return self.handlers.get(message.get_type(), ErrorHandler).handle(message, blockchain_manager)
