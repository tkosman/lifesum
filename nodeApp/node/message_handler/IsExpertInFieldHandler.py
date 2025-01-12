
import json
import os
import sys
from .AbstractHandler import AbstractHandler

from ..logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Message')))
from Message import Message, Type

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))
from blockchain_manager import BlockchainManager

class IsExpertInFieldHandler(AbstractHandler):

    @classmethod
    def handle(self, message: Message, blockchain_manager: BlockchainManager) -> Message | None:
        """Handles messages of type BECOMEEXPERT.

        Args:
            message (Message): The message to handle.

        Returns:
            Message: Becoming expert status.
        """
        # ! not the final implementation
        try:
            blockchain_manager.open_expert_case(**json.loads(message.get_payload()))
            return Message(type=Type.RETURN, status=200, payload='{ "pub_key": "Field succesfully added to user." }')
        except Exception as e:
            return Message(type=Type.RETURN, status=500, payload='{ "pub_key": "Field succesfully added to user." }')

