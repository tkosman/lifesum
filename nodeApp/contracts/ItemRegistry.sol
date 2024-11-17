// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ItemRegistry {
    struct Item {
        uint256 itemId;
        string category;
        string itemInfo;
        address owner;
        bool exists;
    }

    mapping(uint256 => Item) private items;
    uint256 private itemCounter;

    event ItemAdded(uint256 itemId, string category, address owner);

    function addItem(
        string memory _category,
        string memory _itemInfo
    ) public returns (uint256) {
        itemCounter++;
        uint256 newItemId = itemCounter;

        items[newItemId] = Item({
            itemId: newItemId,
            category: _category,
            itemInfo: _itemInfo,
            owner: msg.sender,
            exists: true
        });

        emit ItemAdded(newItemId, _category, msg.sender);

        return newItemId;
    }

    function getItem(uint256 _itemId)
        public
        view
        returns (
            string memory category,
            string memory itemInfo,
            address owner
        )
    {
        require(items[_itemId].exists, "item_not_exist");
        Item storage item = items[_itemId];
        return (item.category, item.itemInfo, item.owner);
    }
}
