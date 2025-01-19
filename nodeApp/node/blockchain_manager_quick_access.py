import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from blockchain_manager import BlockchainManager
from get_blockchain_manager import get_blockchain_manager

bm = get_blockchain_manager()
print(bm.get_item(2))
a = bm.add_item("test", "test", bm.get_user_public_key("a"))
print(a)