import pytest
from ape import project, accounts
from ape.exceptions import ContractLogicError

@pytest.fixture
def reputation_manager():
    return project.ReputationManager.deploy(sender=accounts[2])

@pytest.fixture
def user_registry():
    return project.UserRegistry.deploy(sender=accounts[2])

@pytest.fixture
def expert_case_manager(reputation_manager, user_registry):
    return project.ExpertCaseManager.deploy(
        reputation_manager.address,
        user_registry.address,
        sender=accounts[2]
    )

def test_open_and_vote_expert_case(reputation_manager, user_registry, expert_case_manager):
    public_key = "user_public_key_1"
    
    # Register user
    user_registry.registerUser("ExpertUser", public_key, "Expert data", False, sender=accounts[2])
    user_registry.addExpertField("ExpertUser", 1, sender=accounts[2])
    
    # Update reputation
    reputation_manager.updateReputation(public_key, 1, 5, sender=accounts[2])

    # Open Expert Case
    receipt = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        public_key, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        sender=accounts[2]
    )
    event = list(receipt.events["ExpertCaseOpened"])[0]
    ECId = event["ECId"]

    # Cast Vote
    expert_case_manager.castVote(ECId, 1, public_key, sender=accounts[2])

    # Attempt to cast the same vote again (should fail)
    with pytest.raises(ContractLogicError, match="already_voted"):
        expert_case_manager.castVote(ECId, 1, public_key, sender=accounts[2])

def test_vote_with_low_reputation(reputation_manager, user_registry, expert_case_manager):
    public_key = "user_public_key_2"
    
    # Register user
    user_registry.registerUser("LowRepUser", public_key, "Data", False, sender=accounts[2])
    user_registry.addExpertField("LowRepUser", 1, sender=accounts[2])
    
    # Update reputation to low value
    reputation_manager.updateReputation(public_key, 1, 2, sender=accounts[2])

    # Open Expert Case
    receipt = expert_case_manager.openExpertCase(
        1,          # itemId
        1,          # fieldId
        3,          # minReputation
        public_key, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        sender=accounts[2]
    )
    event = list(receipt.events["ExpertCaseOpened"])[0]
    ECId = event["ECId"]

    # Attempt to cast vote with low reputation (should fail)
    with pytest.raises(ContractLogicError, match="reputation_too_low"):
        expert_case_manager.castVote(ECId, 1, public_key, sender=accounts[2])

def test_user_with_multiple_expert_fields(reputation_manager, user_registry, expert_case_manager):
    public_key = "user_public_key_3"
    
    # Register user
    user_registry.registerUser("MultiExpert", public_key, "Expert data", False, sender=accounts[2])
    user_registry.addExpertField("MultiExpert", 1, sender=accounts[2])
    user_registry.addExpertField("MultiExpert", 2, sender=accounts[2])
    
    # Update reputations for multiple fields
    reputation_manager.updateReputation(public_key, 1, 5, sender=accounts[2])
    reputation_manager.updateReputation(public_key, 2, 7, sender=accounts[2])

    # Open Expert Case for fieldId 2
    receipt = expert_case_manager.openExpertCase(
        1,          # itemId
        2,          # fieldId
        5,          # minReputation
        public_key, # publicKey (as string)
        False,      # botAllowed
        "EC Info",  # ECInfo
        sender=accounts[2]
    )
    event = list(receipt.events["ExpertCaseOpened"])[0]
    ECId = event["ECId"]

    # Cast Vote
    expert_case_manager.castVote(ECId, 1, public_key, sender=accounts[2])

def test_close_expert_case(reputation_manager, user_registry, expert_case_manager):
    public_key_1 = "user_public_key_4"
    public_key_2 = "user_public_key_5"
    
    # Register experts
    user_registry.registerUser("Expert1", public_key_1, "Data1", False, sender=accounts[2])
    user_registry.registerUser("Expert2", public_key_2, "Data2", False, sender=accounts[2])
    user_registry.addExpertField("Expert1", 1, sender=accounts[2])
    user_registry.addExpertField("Expert2", 1, sender=accounts[2])
    
    # Update reputations
    reputation_manager.updateReputation(public_key_1, 1, 5, sender=accounts[2])
    reputation_manager.updateReputation(public_key_2, 1, 5, sender=accounts[2])

    # Open Expert Case
    receipt = expert_case_manager.openExpertCase(
        1,             # itemId
        1,             # fieldId
        3,             # minReputation
        public_key_1,  # publicKey (as string)
        False,         # botAllowed
        "EC Info",     # ECInfo
        sender=accounts[2]
    )
    event = list(receipt.events["ExpertCaseOpened"])[0]
    ECId = event["ECId"]

    # Cast Votes
    expert_case_manager.castVote(ECId, 1, public_key_1, sender=accounts[2])
    expert_case_manager.castVote(ECId, 2, public_key_2, sender=accounts[2])

    # Close Expert Case
    expert_case_manager.closeExpertCase(ECId, sender=accounts[2])

    # Verify reputations after closing
    rep1 = reputation_manager.getReputation(public_key_1, 1)
    rep2 = reputation_manager.getReputation(public_key_2, 1)

    assert rep1 == 7
    assert rep2 == 4