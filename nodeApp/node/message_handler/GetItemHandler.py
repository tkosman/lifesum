
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class GetItemHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type GETITEM.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Registry status.
        """

        try:
            item_info = blockchain_manager.get_item(**json.loads(message.get_payload()))

            logger.info(item_info)

            payload = json.dumps(item_info)

            return Message(type=Type.RETURN, status=200, payload=payload)
        except Exception as ex:
            logger.error(ex)
            return Message(type=Type.RETURN, status=500)
