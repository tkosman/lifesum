
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class UserRegisterHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type REGISTER.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Registry status.
        """
        # ! change check
        if blockchain_manager.register_user(**json.loads(message.get_payload())):
            return Message(type=Type.RETURN, status=200, payload="User registered succesfully.")
        else:
            return Message(type=Type.RETURN, status=500, payload="Error during user registration.")
