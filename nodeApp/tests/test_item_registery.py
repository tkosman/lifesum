import pytest
from ape import project, accounts
from ape.exceptions import ContractLogicError

@pytest.fixture
def item_registry():
    return project.ItemRegistry.deploy(sender=accounts[2])

def test_add_item(item_registry):
    public_key = "user_public_key_1"  # Use Ethereum address as public key

    receipt = item_registry.addItem("Electronics", "Smartphone", public_key, sender=accounts[2])
    event = receipt.events["ItemAdded"][0]
    itemId = event["itemId"]

    assert event["category"] == "Electronics"
    assert event["owner"] == public_key

    category, itemInfo, owner = item_registry.getItem(itemId)

    assert category == "Electronics"
    assert itemInfo == "Smartphone"
    assert owner == public_key

def test_get_nonexistent_item(item_registry):
    with pytest.raises(ContractLogicError, match="item_not_exist"):
        item_registry.getItem(999)

def test_add_multiple_items(item_registry):
    public_key1 = "user_public_key_2"
    public_key2 = "user_public_key_3"

    receipt1 = item_registry.addItem("Books", "Blockchain Basics", public_key1, sender=accounts[2])
    itemId1 = receipt1.events["ItemAdded"][0]["itemId"]

    receipt2 = item_registry.addItem("Movies", "Inception", public_key2, sender=accounts[2])
    itemId2 = receipt2.events["ItemAdded"][0]["itemId"]

    category1, itemInfo1, owner1 = item_registry.getItem(itemId1)
    category2, itemInfo2, owner2 = item_registry.getItem(itemId2)

    assert category1 == "Books"
    assert itemInfo1 == "Blockchain Basics"
    assert owner1 == public_key1

    assert category2 == "Movies"
    assert itemInfo2 == "Inception"
    assert owner2 == public_key2

def test_item_counter_increments_correctly(item_registry):
    public_key1 = "user_public_key_4"
    public_key2 = "user_public_key_5"

    receipt1 = item_registry.addItem("Category1", "Item A", public_key1, sender=accounts[2])
    itemId1 = receipt1.events["ItemAdded"][0]["itemId"]

    receipt2 = item_registry.addItem("Category2", "Item B", public_key2, sender=accounts[2])
    itemId2 = receipt2.events["ItemAdded"][0]["itemId"]

    assert itemId2 == itemId1 + 1