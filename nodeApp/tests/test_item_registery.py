import pytest
from brownie import ItemRegistry, accounts, reverts

@pytest.fixture
def item_registry():
    return ItemRegistry.deploy({'from': accounts[0]})

def test_add_item(item_registry, accounts):
    # Use a public key (could be a string like an address, etc.)
    public_key = "user_public_key_1"  # Use Ethereum address as public key

    tx = item_registry.addItem("Electronics", "Smartphone", public_key, {'from': accounts[0]})
    itemId = tx.return_value

    assert 'ItemAdded' in tx.events
    assert tx.events['ItemAdded']['itemId'] == itemId
    assert tx.events['ItemAdded']['category'] == "Electronics"
    assert tx.events['ItemAdded']['owner'] == public_key  # Check public key in event

    # Retrieve the item and verify its data
    category, itemInfo, owner = item_registry.getItem(itemId)

    assert category == "Electronics"
    assert itemInfo == "Smartphone"
    assert owner == public_key  # Verify that the public key was stored correctly

def test_get_nonexistent_item(item_registry):
    with reverts("item_not_exist"):
        item_registry.getItem(999)

def test_add_multiple_items(item_registry, accounts):
    public_key1 = "user_public_key_2"
    public_key2 = "user_public_key_3"

    # Add first item
    tx1 = item_registry.addItem("Books", "Blockchain Basics", public_key1, {'from': accounts[0]})
    itemId1 = tx1.return_value

    # Add second item
    tx2 = item_registry.addItem("Movies", "Inception", public_key2, {'from': accounts[0]})
    itemId2 = tx2.return_value

    # Retrieve and check both items
    category1, itemInfo1, owner1 = item_registry.getItem(itemId1)
    category2, itemInfo2, owner2 = item_registry.getItem(itemId2)

    assert category1 == "Books"
    assert itemInfo1 == "Blockchain Basics"
    assert owner1 == public_key1

    assert category2 == "Movies"
    assert itemInfo2 == "Inception"
    assert owner2 == public_key2

def test_item_counter_increments_correctly(item_registry, accounts):
    public_key1 = "user_public_key_4"
    public_key2 = "user_public_key_5"

    # Add first item
    tx1 = item_registry.addItem("Category1", "Item A", public_key1, {'from': accounts[0]})
    itemId1 = tx1.return_value

    # Add second item
    tx2 = item_registry.addItem("Category2", "Item B", public_key2, {'from': accounts[0]})
    itemId2 = tx2.return_value

    assert itemId2 == itemId1 + 1  # Check that item counter is incremented correctly
