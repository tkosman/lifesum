
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
            user_info = blockchain_manager.get_user_info(**json.loads(message.get_payload()))

            expert_in = json.dumps(user_info[1])

            return Message(type=Type.RETURN, status=200, payload=expert_in)
        except Exception as e:
            return Message(type=Type.RETURN, status=500, payload='{ "result": "Failed to retrieve user info." }')

