import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from blockchain_manager import BlockchainManager
from get_blockchain_manager import get_blockchain_manager



bm = get_blockchain_manager()
print(bm.get_item(20))
ec = bm.open_expert_case(20, 1, 0, 'some_key', True, "zmiana opisu", "", "nowiutki opis", 0, 1)
#print(ec)
#bm.add_expert_field(bm.get_nick_by_address('some_key'), 1)
bm.cast_vote(ec, 0, 'some_key')
bm.close_expert_case(ec)
print(bm.get_item(20))