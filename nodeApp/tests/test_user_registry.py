import pytest
from brownie import UserRegistry, accounts, exceptions

def test_user_registration():
    dev = accounts[0]
    user_registry = UserRegistry.deploy({'from': dev})

    # Successful registration
    user_registry.registerUser("test_user", "public_key_test", {'from': dev})

    # Check that the user information is correctly stored
    nickname, public_key = user_registry.getUser(dev.address)
    assert nickname == "test_user"
    assert public_key == "public_key_test"

def test_retrieve_user_info():
    dev = accounts[0]
    user_registry = UserRegistry.deploy({'from': dev})
    user_registry.registerUser("test_user", "public_key_test", {'from': dev})

    # Retrieve the user information for the registered user
    nickname, public_key = user_registry.getUser(dev.address)
    assert nickname == "test_user"
    assert public_key == "public_key_test"

def test_retrieve_unregistered_user_info():
    dev = accounts[0]
    user_registry = UserRegistry.deploy({'from': dev})

    # Attempt to retrieve user information for an unregistered user
    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        user_registry.getUser(accounts[1].address)

    # Assert that the error message indicates the user is not registered
    assert "User not registered" in str(excinfo.value)
