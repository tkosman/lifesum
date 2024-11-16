from brownie import ItemTracking, accounts, reverts
import pytest

def test_create_item():
    # Arrange
    owner = accounts[0]
    item_tracking = ItemTracking.deploy({'from': owner})
    item_id = 1

    # Act
    tx = item_tracking.createItem(item_id, {'from': owner})

    # Assert
    id, owner_address, history, exists = item_tracking.getItem(item_id)
    assert id == item_id                # id
    assert owner_address == owner.address          # owner
    assert exists == True                   # exists

def test_check_item_history():
    # Arrange
    owner = accounts[0]
    item_tracking = ItemTracking.deploy({'from': owner})
    item_id = 1
    item_tracking.createItem(item_id, {'from': owner})

    # Act
    history = item_tracking.checkItemHistory(item_id)

    # Assert
    assert len(history) == 0

def test_request_change():
    # Arrange
    client = accounts[1]
    owner = accounts[0]
    item_tracking = ItemTracking.deploy({'from': owner})
    item_id = 1
    item_tracking.createItem(item_id, {'from': owner})
    new_info = "Change Info"

    # Act
    tx = item_tracking.requestChange(item_id, new_info, {'from': client})

    # Assert
    request_id = item_tracking.requestCounter()
    request = item_tracking.getRequest(request_id)
    assert request[0] == request_id          # id
    assert request[1] == item_id             # itemId
    assert request[2] == client.address      # requester
    assert request[3] == new_info            # newInfo
    assert request[4] == 0                   # approvalCount
    assert request[5] == False               # executed

def test_request_expert_role():
    # Arrange
    applicant = accounts[1]
    owner = accounts[0]
    item_tracking = ItemTracking.deploy({'from': owner})
    minimum_stake = item_tracking.minimumStake()

    # Act
    tx = item_tracking.requestExpertRole({'from': applicant, 'value': minimum_stake})

    # Assert
    expert = item_tracking.experts(applicant.address)
    assert expert[0] == applicant.address    # addr
    assert expert[2] == minimum_stake        # stake
    assert expert[3] == True                 # exists

def test_approve_request():
    # Arrange
    owner = accounts[0]
    expert = accounts[1]
    client = accounts[2]
    item_tracking = ItemTracking.deploy({'from': owner})
    # Add expert
    item_tracking.addExpert(expert.address, 1e18)
    item_id = 1
    item_tracking.createItem(item_id, {'from': owner})
    new_info = "Update Info"
    item_tracking.requestChange(item_id, new_info, {'from': client})
    request_id = item_tracking.requestCounter()

    # Act
    item_tracking.approveRequest(request_id, {'from': expert})

    # Assert
    request = item_tracking.getRequest(request_id)
    assert request[4] == 1                   # approvalCount

def test_approve_request_threshold():
    # Arrange
    owner = accounts[0]
    expert1 = accounts[1]
    expert2 = accounts[2]
    client = accounts[3]
    item_tracking = ItemTracking.deploy({'from': owner})
    # Add experts
    item_tracking.addExpert(expert1.address, 1e18)
    item_tracking.addExpert(expert2.address, 1e18)
    item_id = 1
    item_tracking.createItem(item_id, {'from': owner})
    new_info = "Update Info"
    item_tracking.requestChange(item_id, new_info, {'from': client})
    request_id = item_tracking.requestCounter()

    # Act
    item_tracking.approveRequest(request_id, {'from': expert1})
    item_tracking.approveRequest(request_id, {'from': expert2})

    # Assert
    request = item_tracking.getRequest(request_id)
    assert request[4] == 2                   # approvalCount
    assert request[5] == True                # executed
    history = item_tracking.checkItemHistory(item_id)
    assert history[0] == new_info

def test_open_expert_case():
    # Arrange
    owner = accounts[0]
    expert = owner
    item_tracking = ItemTracking.deploy({'from': owner})
    item_tracking.addExpert(expert.address, 1e18)
    item_id = 1
    item_tracking.createItem(item_id, {'from': owner})
    new_info = "Expert Case Info"

    # Act
    item_tracking.openExpertCase(item_id, new_info, {'from': expert})

    # Assert
    request_id = item_tracking.requestCounter()
    request = item_tracking.getRequest(request_id)
    assert request[0] == request_id          # id
    assert request[1] == item_id             # itemId
    assert request[2] == expert.address      # requester
    assert request[3] == new_info            # newInfo
