
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
        # pub_key = json.loads(blockchain_manager.get_nick_by_address(**json.loads(message.get_payload()))).get("pub_key")
        pub_key = json.loads(blockchain_manager.get_user_info("Alice")).get("pub_key")
        # ! check how it looks
        if  pub_key != "":
            return Message(type=Type.RETURN, status=200, payload='{ "pub_key": ' + pub_key + '" }')
        else:
            return Message(type=Type.RETURN, status=500, payload='{ "pub_key": null" }')
