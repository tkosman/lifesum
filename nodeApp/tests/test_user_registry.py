import pytest
from ape import project, accounts
from ape.exceptions import ContractLogicError

@pytest.fixture
def user_registry():
    return project.UserRegistry.deploy(sender=accounts[2])

def test_register_user(user_registry):
    nick = "Alice"
    public_key = "alice_public_key"
    additional_data = "Additional info about Alice"
    is_bot = False

    # Register user with public key
    receipt = user_registry.registerUser(nick, public_key, additional_data, is_bot, sender=accounts[2])
    assert len(receipt.events["RegisterSuccess"]) > 0

    # Try to register the same nick (should fail)
    with pytest.raises(ContractLogicError, match="nick_already_taken"):
        user_registry.registerUser(nick, public_key, "Other data", is_bot, sender=accounts[2])

    # Try to register the same public key with a different nick (should fail)
    with pytest.raises(ContractLogicError, match="address_already_registered"):
        user_registry.registerUser("Alice2", public_key, "Other data", is_bot, sender=accounts[2])

def test_get_user_info(user_registry):
    nick = "Bob"
    public_key = "bob_public_key"
    additional_data = "Additional info about Bob"
    is_bot = True

    user_registry.registerUser(nick, public_key, additional_data, is_bot, sender=accounts[2])

    # Retrieve and check user info
    public_key_returned, expert_fields, additional_data_returned, is_bot_returned = user_registry.getUserInfo(nick)

    assert public_key_returned == public_key  # Check the public key
    assert additional_data_returned == additional_data
    assert is_bot_returned == is_bot

def test_add_expert_field(user_registry):
    nick = "Charlie"
    public_key = "charlie_public_key"
    user_registry.registerUser(nick, public_key, "Data", False, sender=accounts[2])

    # Add expert field 1
    user_registry.addExpertField(nick, 1, sender=accounts[2])
    _, expert_fields, _, _ = user_registry.getUserInfo(nick)

    assert expert_fields == [1]

    # Add expert field 2
    user_registry.addExpertField(nick, 2, sender=accounts[2])
    _, expert_fields, _, _ = user_registry.getUserInfo(nick)

    assert expert_fields == [1, 2]

    # Try to add the same expert field again (should fail)
    with pytest.raises(ContractLogicError, match="field_already_added"):
        user_registry.addExpertField(nick, 1, sender=accounts[2])