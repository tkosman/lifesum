from ape import accounts, project, networks

class BlockchainManager:
    """
    A manager class to interact with deployed Ethereum smart contracts related to user registration,
    expert case management, item registry, and reputation management.
    """

    def __init__(
        self,
        user_registry_address,
        expert_case_manager_address,
        item_registry_address,
        reputation_manager_address
    ):
        """
        Initializes the BlockchainManager with the addresses of deployed contracts.

        !!! But use get_blockchain_manager !!!

        Args:
            user_registry_address (str): The deployed address of the UserRegistry contract.
            expert_case_manager_address (str): The deployed address of the ExpertCaseManager contract.
            item_registry_address (str): The deployed address of the ItemRegistry contract.
            reputation_manager_address (str): The deployed address of the ReputationManager contract.

        Example:
            manager = BlockchainManager(
                "0xUserRegistryAddress",
                "0xExpertCaseManagerAddress",
                "0xItemRegistryAddress",
                "0xReputationManagerAddress"
            )
        """
        with networks.ethereum.sepolia.use_provider("infura"):
            self.user_registry = project.UserRegistry.at(user_registry_address)
            self.expert_case_manager = project.ExpertCaseManager.at(expert_case_manager_address)
            self.item_registry = project.ItemRegistry.at(item_registry_address)
            self.reputation_manager = project.ReputationManager.at(reputation_manager_address)

    def register_user(self, nick, public_key, additional_data, is_bot):
        """
        Registers a new user in the UserRegistry contract.

        Args:
            nick (str): The nickname of the user.
            public_key (str): The public key of the user.
            additional_data (str): Additional data associated with the user.
            is_bot (bool): Indicates whether the user is a bot.

        Returns:
            str: "register_success" if the registration is successful.

        Raises:
            Exception: If the nickname is already taken or the public key is already registered.
                "nick_already_taken"
                "address_already_registered"

        Example:
            try:
                result = manager.register_user("Alice", "0xPublicKeyHere", "Additional Info", False)
                if result == "register_success":
                    print("User registered successfully!")
            except Exception as e:
                print(f"Registration failed: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.user_registry.registerUser(nick, public_key, additional_data, is_bot, sender=sender)
                tx.wait_for_confirmation()
                return tx.return_value
        except Exception as e:
            error_message = str(e)
            if "nick_already_taken" in error_message:
                raise Exception("Registration failed: Nickname is already taken.")
            elif "address_already_registered" in error_message:
                raise Exception("Registration failed: Public key is already registered.")
            else:
                raise Exception(f"Registration failed: {e}")

    def add_expert_field(self, nick, field_id):
        """
        Adds a new expert field to a user's profile in the UserRegistry contract.

        Args:
            nick (str): The nickname of the user.
            field_id (int): The ID of the expert field to add.

        Returns:
            str: "field_added_successfully" if the operation is successful.

        Raises:
            Exception: If the user does not exist or the field is already added.
                "user_not_exist"
                "field_already_added"

        Example:
            try:
                result = manager.add_expert_field("Alice", 101)
                if result == "field_added_successfully":
                    print("Expert field added successfully!")
            except Exception as e:
                print(f"Failed to add expert field: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.user_registry.addExpertField(nick, field_id, sender=sender)
                tx.wait_for_confirmation()
                return "field_added_successfully"
        except Exception as e:
            error_message = str(e)
            if "user_not_exist" in error_message:
                raise Exception("Add Expert Field failed: User does not exist.")
            elif "field_already_added" in error_message:
                raise Exception("Add Expert Field failed: Field is already added.")
            else:
                raise Exception(f"Add Expert Field failed: {e}")

    def modify_user_additional_data(self, nick, new_data):
        """
        Modifies the additional data of an existing user in the UserRegistry contract.

        Args:
            nick (str): The nickname of the user.
            new_data (str): The new additional data to set.

        Returns:
            str: "modify_success" if the operation is successful.

        Raises:
            Exception: If the user does not exist.
                "user_not_exist"

        Example:
            try:
                result = manager.modify_user_additional_data("Alice", "Updated Info")
                if result == "modify_success":
                    print("Additional data updated successfully!")
            except Exception as e:
                print(f"Failed to modify additional data: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.user_registry.modifyUserAdditionalData(nick, new_data, sender=sender)
                tx.wait_for_confirmation()
                return "modify_success"
        except Exception as e:
            error_message = str(e)
            if "user_not_exist" in error_message:
                raise Exception("Modify Additional Data failed: User does not exist.")
            else:
                raise Exception(f"Modify Additional Data failed: {e}")

    def get_user_info(self, nick):
        """
        !!! Don't use this function, use get_user_public_key instead !!!
        Retrieves information about a specific user from the UserRegistry contract.

        Args:
            nick (str): The nickname of the user.

        Returns:
            tuple: A tuple containing the user's public key, list of expert fields, additional data, and bot status.

        Example:
            try:
                user_info = manager.get_user_info("Alice")
                print(f"Public Key: {user_info[0]}")
                print(f"Expert Fields: {user_info[1]}")
                print(f"Additional Data: {user_info[2]}")
                print(f"Is Bot: {user_info[3]}")
            except Exception as e:
                print(f"Failed to retrieve user info: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                return self.user_registry.getUserInfo(nick)
        except Exception as e:
            raise Exception(f"Get User Info failed: {e}")

    def get_user_public_key(self, nick):
        """
        Retrieves the public key of a specific user from the UserRegistry contract.

        Args:
            nick (str): The nickname of the user.

        Returns:
            str: The public key associated with the given nickname.

        Raises:
            Exception: If the user does not exist.
                "user_not_exist"

        Example:
            try:
                public_key = manager.get_user_public_key("Alice")
                print(f"Alice's Public Key: {public_key}")
            except Exception as e:
                print(f"Failed to retrieve public key: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                return self.user_registry.getUserPublicKey(nick)
        except Exception as e:
            error_message = str(e)
            if "user_not_exist" in error_message:
                raise Exception("Get User Public Key failed: User does not exist.")
            else:
                raise Exception(f"Get User Public Key failed: {e}")

    def get_nick_by_address(self, address):
        """
        Retrieves a user's nickname based on their public address from the UserRegistry contract.

        Args:
            address (str): The public address of the user.

        Returns:
            str: The nickname associated with the given address.

        Example:
            try:
                nick = manager.get_nick_by_address("0xPublicAddressHere")
                print(f"Nickname: {nick}")
            except Exception as e:
                print(f"Failed to retrieve nickname: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                return self.user_registry.getNickByAddress(address)
        except Exception as e:
            raise Exception(f"Get Nick by Address failed: {e}")

    def open_expert_case(self, item_id, field_id, min_reputation, public_key, bot_allowed, ec_info, nick_to_change, uni_string_to_modify, field_id_to_add, flag):
        """
        Opens a new expert case in the ExpertCaseManager contract.

        Args:
            item_id (int): The ID of the item associated with the case.
            field_id (int): The ID of the field relevant to the case.
            min_reputation (int): The minimum reputation required to participate.
            public_key (str): The public key of the user opening the case.
            bot_allowed (bool): Indicates whether bots are allowed to participate.
            ec_info (str): Additional information about the expert case.
            nick_to_change (str): The nickname to change, based on the flag.
            uni_string_to_modify (str): The string to modify, based on the flag.
            field_id_to_add (int): The field ID to add if flag is set accordingly.
            flag (int): Determines the action to be taken after case closure.

        Returns:
            int: The ID of the newly created expert case.

        Raises:
            Exception: If opening the expert case fails due to contract constraints.

        Example:
            try:
                ec_id = manager.open_expert_case(
                    5001, 101, 50, "0xPublicKeyHere", False, "Case Info",
                    "Bob", "New Data", 202, 1
                )
                print(f"Expert case opened successfully with ID: {ec_id}")
            except Exception as e:
                print(f"Failed to open expert case: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.expert_case_manager.openExpertCase(
                    item_id,
                    field_id,
                    min_reputation,
                    public_key,
                    bot_allowed,
                    ec_info,
                    nick_to_change,
                    uni_string_to_modify,
                    field_id_to_add,
                    flag,
                    sender=sender
                )
                tx.wait_for_confirmation()
                return tx.return_value
        except Exception as e:
            raise Exception(f"Open Expert Case failed: {e}")

    def cast_vote(self, ec_id, option, public_key):
        """
        Casts a vote in an existing expert case.

        Args:
            ec_id (int): The ID of the expert case.
            option (int): The option the user is voting for.
            public_key (str): The public key of the voter.

        Returns:
            str: "vote_cast_successfully" if the vote is successfully cast.

        Raises:
            Exception: If voting fails due to contract constraints.
                "EC_not_exist"
                "EC_closed"
                "user_not_registered"
                "bots_not_allowed"
                "not_expert_in_field"
                "reputation_too_low"
                "already_voted"

        Example:
            try:
                result = manager.cast_vote(1, 2, "0xVoterPublicKey")
                if result == "vote_cast_successfully":
                    print("Vote cast successfully!")
            except Exception as e:
                print(f"Failed to cast vote: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.expert_case_manager.castVote(ec_id, option, public_key, sender=sender)
                tx.wait_for_confirmation()
                return "vote_cast_successfully"
        except Exception as e:
            error_message = str(e)
            if "EC_not_exist" in error_message:
                raise Exception("Cast Vote failed: Expert case does not exist.")
            elif "EC_closed" in error_message:
                raise Exception("Cast Vote failed: Expert case is closed.")
            elif "user_not_registered" in error_message:
                raise Exception("Cast Vote failed: User is not registered.")
            elif "bots_not_allowed" in error_message:
                raise Exception("Cast Vote failed: Bots are not allowed to participate.")
            elif "not_expert_in_field" in error_message:
                raise Exception("Cast Vote failed: User is not an expert in the required field.")
            elif "reputation_too_low" in error_message:
                raise Exception("Cast Vote failed: User's reputation is too low.")
            elif "already_voted" in error_message:
                raise Exception("Cast Vote failed: User has already voted.")
            else:
                raise Exception(f"Cast Vote failed: {e}")

    def close_expert_case(self, ec_id):
        """
        Closes an open expert case and processes the results.

        Args:
            ec_id (int): The ID of the expert case to close.

        Returns:
            str: "expert_case_closed_successfully" if the expert case is successfully closed.

        Raises:
            Exception: If closing the case fails due to contract constraints.
                "EC_not_exist"
                "EC_already_closed"

        Example:
            try:
                result = manager.close_expert_case(1)
                if result == "expert_case_closed_successfully":
                    print("Expert case closed successfully!")
            except Exception as e:
                print(f"Failed to close expert case: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.expert_case_manager.closeExpertCase(ec_id, sender=sender)
                tx.wait_for_confirmation()
                return "expert_case_closed_successfully"
        except Exception as e:
            error_message = str(e)
            if "EC_not_exist" in error_message:
                raise Exception("Close Expert Case failed: Expert case does not exist.")
            elif "EC_already_closed" in error_message:
                raise Exception("Close Expert Case failed: Expert case is already closed.")
            else:
                raise Exception(f"Close Expert Case failed: {e}")

    def get_expert_case(self, ec_id):
        """
        Retrieves details of a specific expert case from the ExpertCaseManager contract.

        Args:
            ec_id (int): The ID of the expert case.

        Returns:
            tuple: A tuple containing itemId, fieldId, minReputation, botAllowed, ECInfo, and isOpen status.

        Example:
            try:
                expert_case = manager.get_expert_case(1)
                print(f"Item ID: {expert_case[0]}")
                print(f"Field ID: {expert_case[1]}")
                print(f"Minimum Reputation: {expert_case[2]}")
                print(f"Bots Allowed: {expert_case[3]}")
                print(f"Expert Case Info: {expert_case[4]}")
                print(f"Is Open: {expert_case[5]}")
            except Exception as e:
                print(f"Failed to retrieve expert case: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                return self.expert_case_manager.getExpertCase(ec_id)
        except Exception as e:
            raise Exception(f"Get Expert Case failed: {e}")

    def add_item(self, category, item_info, public_key):
        """
        Adds a new item to the ItemRegistry contract.

        Args:
            category (str): The category of the item.
            item_info (str): Information/details about the item.
            public_key (str): The public key of the user adding the item.

        Returns:
            int: The ID of the newly added item.

        Raises:
            Exception: If adding the item fails due to contract constraints.

        Example:
            try:
                item_id = manager.add_item("Electronics", "Smartphone Model X", "0xUserPublicKey")
                print(f"Item added successfully with ID: {item_id}")
            except Exception as e:
                print(f"Failed to add item: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.item_registry.addItem(category, item_info, public_key, sender=sender)
                tx.wait_for_confirmation()
                return tx.return_value
        except Exception as e:
            raise Exception(f"Add Item failed: {e}")

    def get_item(self, item_id):
        """
        Retrieves information about a specific item from the ItemRegistry contract.

        Args:
            item_id (int): The ID of the item.

        Returns:
            tuple: A tuple containing category, itemInfo, and owner.

        Example:
            try:
                item = manager.get_item(5001)
                print(f"Category: {item[0]}")
                print(f"Item Info: {item[1]}")
                print(f"Owner: {item[2]}")
            except Exception as e:
                print(f"Failed to retrieve item: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                return self.item_registry.getItem(item_id)
        except Exception as e:
            raise Exception(f"Get Item failed: {e}")

    def update_reputation(self, user, field_id, score):
        """
        Updates a user's reputation in a specific field using the ReputationManager contract.

        Args:
            user (str): The nickname of the user.
            field_id (int): The ID of the field.
            score (int): The score to adjust the user's reputation by.

        Returns:
            str: "reputation_updated_successfully" if the reputation is successfully updated.

        Raises:
            Exception: If updating reputation fails due to contract constraints.

        Example:
            try:
                result = manager.update_reputation("Alice", 101, 5)
                if result == "reputation_updated_successfully":
                    print("Reputation updated successfully!")
            except Exception as e:
                print(f"Failed to update reputation: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                sender = accounts.load("my_account")
                tx = self.reputation_manager.updateReputation(user, field_id, score, sender=sender)
                tx.wait_for_confirmation()
                return "reputation_updated_successfully"
        except Exception as e:
            raise Exception(f"Update Reputation failed: {e}")

    def get_reputation(self, user, field_id):
        """
        Retrieves a user's reputation for a specific field from the ReputationManager contract.

        !!! But use 

        Args:
            user (str): The nickname of the user.
            field_id (int): The ID of the field.

        Returns:
            int: The user's reputation score in the specified field.

        Example:
            try:
                reputation = manager.get_reputation("Alice", 101)
                print(f"Alice's Reputation in Field 101: {reputation}")
            except Exception as e:
                print(f"Failed to retrieve reputation: {e}")
        """
        try:
            with networks.ethereum.sepolia.use_provider("infura"):
                return self.reputation_manager.getReputation(user, field_id)
        except Exception as e:
            raise Exception(f"Get Reputation failed: {e}")