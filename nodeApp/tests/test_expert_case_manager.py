import pytest
from brownie import (
    ReputationManager,
    UserRegistry,
    ExpertCaseManager,
    accounts,
    reverts,
)

@pytest.fixture
def reputation_manager():
    return ReputationManager.deploy({'from': accounts[0]})

@pytest.fixture
def user_registry():
    return UserRegistry.deploy({'from': accounts[0]})

@pytest.fixture
def expert_case_manager(reputation_manager, user_registry):
    return ExpertCaseManager.deploy(
        reputation_manager.address,
        user_registry.address,
        {'from': accounts[0]}
    )

def test_open_and_vote_expert_case(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    nick = "ExpertUser"
    user_registry.registerUser(nick, "Expert data", False, {'from': accounts[1]})
    user_registry.addExpertField(nick, 1, {'from': accounts[1]})

    reputation_manager.updateReputation(accounts[1], 1, 5, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    expert_case_manager.castVote(ECId, 1, {'from': accounts[1]})

    with reverts("already_voted"):
        expert_case_manager.castVote(ECId, 1, {'from': accounts[1]})

def test_vote_with_low_reputation(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    nick = "LowRepUser"
    user_registry.registerUser(nick, "Data", False, {'from': accounts[2]})
    user_registry.addExpertField(nick, 1, {'from': accounts[2]})
    reputation_manager.updateReputation(accounts[2], 1, 2, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    with reverts("reputation_too_low"):
        expert_case_manager.castVote(ECId, 1, {'from': accounts[2]})

def test_user_with_multiple_expert_fields(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    nick = "MultiExpert"
    user_registry.registerUser(nick, "Expert data", False, {'from': accounts[5]})
    user_registry.addExpertField(nick, 1, {'from': accounts[5]})
    user_registry.addExpertField(nick, 2, {'from': accounts[5]})

    reputation_manager.updateReputation(accounts[5], 1, 5, {'from': accounts[0]})
    reputation_manager.updateReputation(accounts[5], 2, 7, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        2,          # fieldId
        5,          # minReputation
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    expert_case_manager.castVote(ECId, 1, {'from': accounts[5]})

def test_close_expert_case(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    nick1 = "Expert1"
    nick2 = "Expert2"
    user_registry.registerUser(nick1, "Data1", False, {'from': accounts[6]})
    user_registry.registerUser(nick2, "Data2", False, {'from': accounts[7]})
    user_registry.addExpertField(nick1, 1, {'from': accounts[6]})
    user_registry.addExpertField(nick2, 1, {'from': accounts[7]})

    reputation_manager.updateReputation(accounts[6], 1, 5, {'from': accounts[0]})
    reputation_manager.updateReputation(accounts[7], 1, 5, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    expert_case_manager.castVote(ECId, 1, {'from': accounts[6]})
    expert_case_manager.castVote(ECId, 2, {'from': accounts[7]})

    expert_case_manager.closeExpertCase(ECId, {'from': accounts[0]})

    rep1 = reputation_manager.getReputation(accounts[6], 1)
    rep2 = reputation_manager.getReputation(accounts[7], 1)


    assert rep1 == 3

    assert rep2 == 5
