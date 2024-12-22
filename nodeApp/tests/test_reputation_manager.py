import pytest
from ape import project, accounts
from ape.exceptions import ContractLogicError

@pytest.fixture
def reputation_manager():
    return project.ReputationManager.deploy(sender=accounts[2])

def test_update_and_get_reputation(reputation_manager):
    user = "user_public_key_1"
    field_id = 1
    score = 1

    # Update reputation
    receipt = reputation_manager.updateReputation(user, field_id, score, sender=accounts[2])
    event = receipt.events["ReputationUpdated"][0]

    assert event['user'] == user
    assert event['fieldId'] == field_id
    assert event['score'] == score

    # Get reputation
    recent_score = reputation_manager.getReputation(user, field_id)
    assert recent_score == 1

    # Increment reputation
    reputation_manager.updateReputation(user, field_id, 1, sender=accounts[2])
    recent_score = reputation_manager.getReputation(user, field_id)
    assert recent_score == 2

    # Decrement reputation
    reputation_manager.updateReputation(user, field_id, -1, sender=accounts[2])
    recent_score = reputation_manager.getReputation(user, field_id)
    assert recent_score == 1