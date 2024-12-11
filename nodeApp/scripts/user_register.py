from ape import project, accounts, networks

def register_user():
    with networks.ethereum.sepolia.use_provider("infura"):
        deployer = accounts[0]
        user_registry = project.UserRegistry.at("c406212e17e862c285386406c1307d34cd26d50D")

        # tx = user_registry.registerUser("Alice", "2345g2524523f6j58k38q673456", "Test user", False, sender=deployer)
        # print(f"User registration tx: {tx.txn_hash}")

        # public_key, expert_fields, additional_data, is_bot = user_registry.getUserInfo("Alice")
        # print("User info:", public_key, expert_fields, additional_data, is_bot)

        nick = user_registry.getNickByAddress("2345g2524523f6j58k38q673456")
        print("Nick from address:", nick)
