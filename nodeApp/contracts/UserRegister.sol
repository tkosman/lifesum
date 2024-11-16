// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserRegistry {
    struct User {
        address userAddress;
        string nickname;
        string publicKey;
        bool exists;
    }

    mapping(address => User) public users;
    mapping(string => bool) private nicknames;  // To enforce unique nicknames

    event UserRegistered(address indexed userAddress, string nickname, string publicKey);

    // Function to register a new user
    function registerUser(string memory nickname, string memory publicKey) public {
        require(!users[msg.sender].exists, "User already registered");
        require(!nicknames[nickname], "Nickname is already taken");

        users[msg.sender] = User({
            userAddress: msg.sender,
            nickname: nickname,
            publicKey: publicKey,
            exists: true
        });

        nicknames[nickname] = true;  // Mark nickname as taken

        emit UserRegistered(msg.sender, nickname, publicKey);
    }

    // Function to get the full user information
    function getUser(address userAddress) public view returns (string memory, string memory) {
        require(users[userAddress].exists, "User not registered");
        return (users[userAddress].nickname, users[userAddress].publicKey);
    }

    // Function to get only the public key of a user
    function getUserPublicKey(address userAddress) public view returns (string memory) {
        require(users[userAddress].exists, "User not registered");
        return users[userAddress].publicKey;
    }
}
