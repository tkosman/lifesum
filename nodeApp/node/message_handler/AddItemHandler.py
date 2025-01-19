
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class AddItemHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type ADDPUBKEY.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Registry status.
        """

        # ! not the final implementation
        try:
            item_id = blockchain_manager.add_item(**json.loads(message.get_payload()))

            data = {
                "item_id": item_id
            }

            payload = json.dumps(data)

            return Message(type=Type.RETURN, status=200, payload=payload)
        except Exception as ex:
            logger.error(ex)
            return Message(type=Type.RETURN, status=500, payload='{ "result": "error during register" }')
