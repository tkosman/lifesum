
import os
import sys
from .AbstractHandler import AbstractHandler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class PingHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type PING.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Ping message.
        """
        return Message(type=Type.PING)