import pytest
from brownie import UserRegistry, accounts, reverts

@pytest.fixture
def user_registry():
    return UserRegistry.deploy({'from': accounts[0]})

def test_register_user(user_registry, accounts):
    nick = "Alice"
    additional_data = "Additional info about Alice"
    is_bot = False

    tx = user_registry.registerUser(nick, additional_data, is_bot, {'from': accounts[1]})
    assert "register_success" in tx.return_value

    with reverts("nick_already_taken"):
        user_registry.registerUser(nick, "Other data", is_bot, {'from': accounts[2]})

    with reverts("address_already_registered"):
        user_registry.registerUser("Alice2", "Other data", is_bot, {'from': accounts[1]})

def test_get_user_info(user_registry, accounts):
    nick = "Bob"
    additional_data = "Additional info about Bob"
    is_bot = True

    user_registry.registerUser(nick, additional_data, is_bot, {'from': accounts[2]})

    (
        public_key,
        expert_fields,
        additional_data_returned,
        is_bot_returned
    ) = user_registry.getUserInfo(nick)

    assert public_key == accounts[2]
    assert additional_data_returned == additional_data
    assert is_bot_returned == is_bot

def test_add_expert_field(user_registry, accounts):
    nick = "Charlie"
    user_registry.registerUser(nick, "Data", False, {'from': accounts[3]})

    user_registry.addExpertField(nick, 1, {'from': accounts[3]})
    (
        _,
        expert_fields,
        _,
        _
    ) = user_registry.getUserInfo(nick)

    assert expert_fields == [1]

    user_registry.addExpertField(nick, 2, {'from': accounts[3]})
    (
        _,
        expert_fields,
        _,
        _
    ) = user_registry.getUserInfo(nick)

    assert expert_fields == [1, 2]

    with reverts("field_already_added"):
        user_registry.addExpertField(nick, 1, {'from': accounts[3]})
