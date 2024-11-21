// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserRegistry {
    struct User {
        string nick;
        address public_key;
        uint256[] expertFields;
        mapping(uint256 => bool) hasExpertField; // For checking duplicates
        string additional_data;
        bool is_bot;
        bool exists;
    }

    mapping(string => User) private users;
    mapping(address => string) private addressToNick;

    event UserRegistered(string nick, address public_key);
    event ExpertFieldAdded(string nick, uint256 fieldId);

    function registerUser(
        string memory _nick,
        string memory _additionalData,
        bool _isBot
    ) public returns (string memory) {
        require(!users[_nick].exists, "nick_already_taken");
        require(bytes(addressToNick[msg.sender]).length == 0, "address_already_registered");

        User storage user = users[_nick];
        user.nick = _nick;
        user.public_key = msg.sender;
        user.additional_data = _additionalData;
        user.is_bot = _isBot;
        user.exists = true;

        addressToNick[msg.sender] = _nick;

        emit UserRegistered(_nick, msg.sender);

        return "register_success";
    }

    function addExpertField(string memory _nick, uint256 _fieldId) external {
        require(users[_nick].exists, "user_not_exist");
        User storage user = users[_nick];

        require(!user.hasExpertField[_fieldId], "field_already_added");

        user.expertFields.push(_fieldId);
        user.hasExpertField[_fieldId] = true;

        emit ExpertFieldAdded(_nick, _fieldId);
    }

    function getUserInfo(string memory _nick)
        public
        view
        returns (
            address public_key,
            uint256[] memory expertFields,
            string memory additional_data,
            bool is_bot
        )
    {
        require(users[_nick].exists, "user_not_exist");
        User storage user = users[_nick];
        return (
            user.public_key,
            user.expertFields,
            user.additional_data,
            user.is_bot
        );
    }

    function getNickByAddress(address _address) external view returns (string memory) {
        return addressToNick[_address];
    }
}