from ape import accounts, project, networks

class BlockchainManager:
    def __init__(self, user_registry_address, expert_case_manager_address, item_registry_address, reputation_manager_address):
        self.user_registry = project.UserRegistry.at(user_registry_address)
        self.expert_case_manager = project.ExpertCaseManager.at(expert_case_manager_address)
        self.item_registry = project.ItemRegistry.at(item_registry_address)
        self.reputation_manager = project.ReputationManager.at(reputation_manager_address)

    def register_user(self, nick, public_key, additional_data, is_bot):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.user_registry.registerUser(nick, public_key, additional_data, is_bot, sender=sender)
            tx.wait_for_confirmation()
            return tx.return_value

    def add_expert_field(self, nick, field_id):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.user_registry.addExpertField(nick, field_id, sender=sender)
            tx.wait_for_confirmation()

    def get_user_info(self, nick):
        with networks.ethereum.sepolia.use_provider("infura"):
            return self.user_registry.getUserInfo(nick)

    def get_nick_by_address(self, address):
        with networks.ethereum.sepolia.use_provider("infura"):
            return self.user_registry.getNickByAddress(address)

    def open_expert_case(self, item_id, field_id, min_reputation, public_key, bot_allowed, ec_info):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.expert_case_manager.openExpertCase(item_id, field_id, min_reputation, public_key, bot_allowed, ec_info, sender=sender)
            tx.wait_for_confirmation()
            return tx.return_value

    def cast_vote(self, ec_id, option, public_key):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.expert_case_manager.castVote(ec_id, option, public_key, sender=sender)
            tx.wait_for_confirmation()

    def close_expert_case(self, ec_id):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.expert_case_manager.closeExpertCase(ec_id, sender=sender)
            tx.wait_for_confirmation()

    def get_expert_case(self, ec_id):
        with networks.ethereum.sepolia.use_provider("infura"):
            return self.expert_case_manager.getExpertCase(ec_id)

    def add_item(self, category, item_info, public_key):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.item_registry.addItem(category, item_info, public_key, sender=sender)
            tx.wait_for_confirmation()
            return tx.return_value

    def get_item(self, item_id):
        with networks.ethereum.sepolia.use_provider("infura"):
            return self.item_registry.getItem(item_id)

    def update_reputation(self, user, field_id, score):
        with networks.ethereum.sepolia.use_provider("infura"):
            sender = accounts.load("my_account")
            tx = self.reputation_manager.updateReputation(user, field_id, score, sender=sender)
            tx.wait_for_confirmation()

    def get_reputation(self, user, field_id):
        with networks.ethereum.sepolia.use_provider("infura"):
            return self.reputation_manager.getReputation(user, field_id)