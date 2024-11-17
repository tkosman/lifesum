import pytest
from brownie import ItemRegistry, accounts, reverts

@pytest.fixture
def item_registry():
    return ItemRegistry.deploy({'from': accounts[0]})

def test_add_item(item_registry, accounts):
    tx = item_registry.addItem("Electronics", "Smartphone", {'from': accounts[1]})
    itemId = tx.return_value

    assert 'ItemAdded' in tx.events
    assert tx.events['ItemAdded']['itemId'] == itemId
    assert tx.events['ItemAdded']['category'] == "Electronics"
    assert tx.events['ItemAdded']['owner'] == accounts[1]

    category, itemInfo, owner = item_registry.getItem(itemId)

    assert category == "Electronics"
    assert itemInfo == "Smartphone"
    assert owner == accounts[1]

def test_get_nonexistent_item(item_registry):
    with reverts("item_not_exist"):
        item_registry.getItem(999)

def test_add_multiple_items(item_registry, accounts):
    tx1 = item_registry.addItem("Books", "Blockchain Basics", {'from': accounts[1]})
    itemId1 = tx1.return_value

    tx2 = item_registry.addItem("Movies", "Inception", {'from': accounts[2]})
    itemId2 = tx2.return_value

    category1, itemInfo1, owner1 = item_registry.getItem(itemId1)
    category2, itemInfo2, owner2 = item_registry.getItem(itemId2)

    assert category1 == "Books"
    assert itemInfo1 == "Blockchain Basics"
    assert owner1 == accounts[1]

    assert category2 == "Movies"
    assert itemInfo2 == "Inception"
    assert owner2 == accounts[2]

def test_item_counter_increments_correctly(item_registry, accounts):
    tx1 = item_registry.addItem("Category1", "Item A", {'from': accounts[1]})
    itemId1 = tx1.return_value

    tx2 = item_registry.addItem("Category2", "Item B", {'from': accounts[1]})
    itemId2 = tx2.return_value

    assert itemId2 == itemId1 + 1
