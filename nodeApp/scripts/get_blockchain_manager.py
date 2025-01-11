from blockchain_manager import BlockchainManager

def get_blockchain_manager():
    # Define the contract addresses
    USER_REGISTRY_ADDRESS = "0xEcF02e840D457edc1880B73FAcB4bCC7A2a9D3E7"
    EXPERT_CASE_MANAGER_ADDRESS = "0x2E0EB9CBB827c4FAe9e249A750Ac893d3e446336"
    ITEM_REGISTRY_ADDRESS = "0xd98974323547C3d2288ae63676539fD85748F10D"
    REPUTATION_MANAGER_ADDRESS = "0xFD96e13a1fE066B3C3F48013237B6b3CB084E345"

    # Initialize and return the BlockchainManager object
    return BlockchainManager(
        USER_REGISTRY_ADDRESS,
        EXPERT_CASE_MANAGER_ADDRESS,
        ITEM_REGISTRY_ADDRESS,
        REPUTATION_MANAGER_ADDRESS
    )
# usage:
# blockchain_manager = get_blockchain_manager()
