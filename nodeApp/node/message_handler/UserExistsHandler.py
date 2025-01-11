
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class UserExistsHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type USREXISTS.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Bool value whether user exists.
        """

        if blockchain_manager.get_nick_by_address(**json.loads(message.get_payload())) != "":
            return Message(type=Type.RETURN, status=200, payload='{ "user_exists": True" }')
        else:
            return Message(type=Type.RETURN, status=200, payload='{ "user_exists": False" }')
