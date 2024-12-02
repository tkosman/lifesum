
from abc import ABC, abstractmethod
import sys

sys.path.insert(0, '../../../Message')
from Message import Message

class AbstractHandler(ABC):
    """Abstract message handler."""
    @classmethod
    @abstractmethod
    def handle(self, message: Message) -> Message | None:
        """Handles a message.

        Args:
            message (Message): The message to handle.

        Returns:
            Message|None: Return message; *None* if a *KeyError* occurs.
        """
        raise NotImplementedError("Method not implemented: handle.")
