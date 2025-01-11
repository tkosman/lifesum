
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class AddPublicKeyHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type ADDPUBKEY.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Registry status.
        """

        try:
            registry_status = str(blockchain_manager.register_user(**json.loads(message.get_payload())))

            if registry_status == "0":
                return Message(type=Type.RETURN, status=200, payload='{ "result": "register_success" }')
            else:
                return Message(type=Type.RETURN, status=500, payload='{ "result": "error during register" }')
        except Exception as ex:
            logger.error(ex)
            return Message(type=Type.RETURN, status=500, payload='{ "result": "error during register" }')
