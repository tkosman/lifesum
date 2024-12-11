// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IUserRegistry {
    event UserRegistered(string indexed nick, string public_key);
    event ExpertFieldAdded(string indexed nick, uint256 fieldId);

    function registerUser(
        string memory _nick,
        string memory _publicKey,
        string memory _additionalData,
        bool _isBot
    ) external returns (string memory);

    function addExpertField(
        string memory _nick,
        uint256 _fieldId
    ) external;

    function getUserInfo(
        string memory _nick
    )
        external
        view
        returns (
            string memory public_key,
            uint256[] memory expertFields,
            string memory additional_data,
            bool is_bot
        );

    function getNickByAddress(
        string memory _address
    )
        external
        view
        returns (string memory);
}
