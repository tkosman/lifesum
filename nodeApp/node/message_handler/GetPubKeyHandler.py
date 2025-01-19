
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class GetPubKeyHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type GETPUBKEY.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Public key for user.
        """

        try:
            pub_key = blockchain_manager.get_user_public_key(**json.loads(message.get_payload()))

            data = {
                "pub_key": pub_key
            }

            payload = json.dumps(data)

            return Message(type=Type.RETURN, status=200, payload=payload)
        except Exception as ex:
            return Message(type=Type.RETURN, status=500)

