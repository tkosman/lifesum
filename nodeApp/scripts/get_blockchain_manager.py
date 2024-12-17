from blockchain_manager import BlockchainManager

def get_blockchain_manager():
    # Define the contract addresses
    USER_REGISTRY_ADDRESS = "0xc406212e17e862c285386406c1307d34cd26d50D"
    EXPERT_CASE_MANAGER_ADDRESS = "0xYourExpertCaseManagerContractAddress"
    ITEM_REGISTRY_ADDRESS = "0x8F5bC4A52A9B8569ca4980AB000ea3395CBf03C1"
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
