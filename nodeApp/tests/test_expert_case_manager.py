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
    # Use a public key as string to identify users
    public_key = "user_public_key_1"
    user_registry.registerUser("ExpertUser", public_key, "Expert data", False, {'from': accounts[0]})
    user_registry.addExpertField("ExpertUser", 1, {'from': accounts[0]})

    reputation_manager.updateReputation(public_key, 1, 5, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        public_key, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    expert_case_manager.castVote(ECId, 1, public_key, {'from': accounts[0]})

    with reverts("already_voted"):
        expert_case_manager.castVote(ECId, 1, public_key, {'from': accounts[0]})

def test_vote_with_low_reputation(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    # Use a public key as string to identify users
    public_key = "user_public_key_2"
    user_registry.registerUser("LowRepUser", public_key, "Data", False, {'from': accounts[0]})
    user_registry.addExpertField("LowRepUser", 1, {'from': accounts[0]})
    reputation_manager.updateReputation(public_key, 1, 2, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        public_key, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    with reverts("reputation_too_low"):
        expert_case_manager.castVote(ECId, 1, public_key, {'from': accounts[0]})

def test_user_with_multiple_expert_fields(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    # Use a public key as string to identify users
    public_key = "user_public_key_3"
    user_registry.registerUser("MultiExpert", public_key, "Expert data", False, {'from': accounts[0]})
    user_registry.addExpertField("MultiExpert", 1, {'from': accounts[0]})
    user_registry.addExpertField("MultiExpert", 2, {'from': accounts[0]})

    reputation_manager.updateReputation(public_key, 1, 5, {'from': accounts[0]})
    reputation_manager.updateReputation(public_key, 2, 7, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        2,          # fieldId
        5,          # minReputation
        public_key, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    expert_case_manager.castVote(ECId, 1, public_key, {'from': accounts[0]})

def test_close_expert_case(
    reputation_manager,
    user_registry,
    expert_case_manager,
    accounts
):
    # Use public keys as string to identify users
    public_key_1 = "user_public_key_4"
    public_key_2 = "user_public_key_5"
    user_registry.registerUser("Expert1", public_key_1, "Data1", False, {'from': accounts[0]})
    user_registry.registerUser("Expert2", public_key_2, "Data2", False, {'from': accounts[0]})
    user_registry.addExpertField("Expert1", 1, {'from': accounts[0]})
    user_registry.addExpertField("Expert2", 1, {'from': accounts[0]})

    reputation_manager.updateReputation(public_key_1, 1, 5, {'from': accounts[0]})
    reputation_manager.updateReputation(public_key_2, 1, 5, {'from': accounts[0]})

    tx = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        public_key_1, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        {'from': accounts[0]}
    )
    ECId = tx.return_value

    expert_case_manager.castVote(ECId, 1, public_key_1, {'from': accounts[0]})
    expert_case_manager.castVote(ECId, 2, public_key_2, {'from': accounts[0]})

    expert_case_manager.closeExpertCase(ECId, {'from': accounts[0]})

    rep1 = reputation_manager.getReputation(public_key_1, 1)
    rep2 = reputation_manager.getReputation(public_key_2, 1)

    assert rep1 == 7
    assert rep2 == 4
