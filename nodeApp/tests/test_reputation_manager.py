import pytest
from brownie import ReputationManager, accounts

@pytest.fixture
def reputation_manager():
    return ReputationManager.deploy({'from': accounts[0]})

def test_update_and_get_reputation(reputation_manager, accounts):
    user = accounts[1]
    field_id = 1
    score = 1

    tx = reputation_manager.updateReputation(user, field_id, score, {'from': accounts[0]})
    assert tx.events['ReputationUpdated']['user'] == user
    assert tx.events['ReputationUpdated']['fieldId'] == field_id
    assert tx.events['ReputationUpdated']['score'] == score

    average_score = reputation_manager.getReputation(user, field_id)
    assert average_score == 1

    reputation_manager.updateReputation(user, field_id, 1, {'from': accounts[0]})
    average_score = reputation_manager.getReputation(user, field_id)
    assert average_score == 1

    reputation_manager.updateReputation(user, field_id, 0, {'from': accounts[0]})
    average_score = reputation_manager.getReputation(user, field_id)
    assert average_score == (1 + 1 + 0) // 3
