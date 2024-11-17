// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IReputationManager {
    function updateReputation(address _user, uint256 _fieldId, uint8 _score) external;
    function getReputation(address _user, uint256 _fieldId) external view returns (uint256);
}

interface IUserRegistry {
    function getNickByAddress(address _address) external view returns (string memory);
    function getUserInfo(string memory _nick)
        external
        view
        returns (
            address public_key,
            uint256[] memory expertFields,
            string memory additional_data,
            bool is_bot
        );
}

contract ExpertCaseManager {
    struct ExpertCase {
        uint256 ECId;
        uint256 itemId;
        uint256 fieldId;
        uint256 minReputation;
        bool botAllowed;
        string ECInfo;
        mapping(address => bool) hasVoted;
        mapping(address => uint8) voterChoices;
        address[] voters;
        mapping(uint8 => uint256) votes;
        uint8[] optionsVoted; // Added to track voted options
        bool isOpen;
        bool exists;
    }

    mapping(uint256 => ExpertCase) private expertCases;
    uint256 private ECIdCounter;

    IReputationManager private reputationManager;
    IUserRegistry private userRegistry;

    event ExpertCaseOpened(uint256 ECId, uint256 itemId, address openedBy);
    event VoteCast(uint256 ECId, address voter, uint8 option);
    event ExpertCaseClosed(uint256 ECId, uint8 winningOption);

    constructor(address _reputationManagerAddress, address _userRegistryAddress) {
        reputationManager = IReputationManager(_reputationManagerAddress);
        userRegistry = IUserRegistry(_userRegistryAddress);
    }

    function openExpertCase(
        uint256 _itemId,
        uint256 _fieldId,
        uint256 _minReputation,
        bool _botAllowed,
        string memory _ECInfo
    ) public returns (uint256) {
        ECIdCounter++;
        uint256 newECId = ECIdCounter;

        ExpertCase storage ec = expertCases[newECId];
        ec.ECId = newECId;
        ec.itemId = _itemId;
        ec.fieldId = _fieldId;
        ec.minReputation = _minReputation;
        ec.botAllowed = _botAllowed;
        ec.ECInfo = _ECInfo;
        ec.isOpen = true;
        ec.exists = true;

        emit ExpertCaseOpened(newECId, _itemId, msg.sender);

        return newECId;
    }

    function castVote(
        uint256 _ECId,
        uint8 _option
    ) public {
        require(expertCases[_ECId].exists, "EC_not_exist");
        require(expertCases[_ECId].isOpen, "EC_closed");

        ExpertCase storage ec = expertCases[_ECId];

        // Verify voter registration
        string memory voterNick = userRegistry.getNickByAddress(msg.sender);
        require(bytes(voterNick).length > 0, "user_not_registered");

        // Get user info
        (
            ,
            uint256[] memory expertFields,
            ,
            bool isBot
        ) = userRegistry.getUserInfo(voterNick);

        // Check if bots are allowed
        require(ec.botAllowed || !isBot, "bots_not_allowed");

        // Check if user is an expert in the required field
        bool isExpert = false;
        for (uint256 i = 0; i < expertFields.length; i++) {
            if (expertFields[i] == ec.fieldId) {
                isExpert = true;
                break;
            }
        }
        require(isExpert, "not_expert_in_field");

        // Check user's reputation
        uint256 userReputation = reputationManager.getReputation(msg.sender, ec.fieldId);
        require(userReputation >= ec.minReputation, "reputation_too_low");

        // Check if user has already voted
        require(!ec.hasVoted[msg.sender], "already_voted");

        // Record the vote
        ec.hasVoted[msg.sender] = true;
        ec.votes[_option] += 1;
        ec.voterChoices[msg.sender] = _option;
        ec.voters.push(msg.sender);

        // Add option to optionsVoted if it's the first vote for that option
        if (ec.votes[_option] == 1) {
            ec.optionsVoted.push(_option);
        }

        emit VoteCast(_ECId, msg.sender, _option);
    }

    function closeExpertCase(uint256 _ECId) public {
        require(expertCases[_ECId].exists, "EC_not_exist");
        require(expertCases[_ECId].isOpen, "EC_already_closed");

        ExpertCase storage ec = expertCases[_ECId];
        ec.isOpen = false;

        // Determine the winning option
        uint8 winningOption;
        uint256 maxVotes = 0;

        for (uint256 i = 0; i < ec.optionsVoted.length; i++) {
            uint8 option = ec.optionsVoted[i];
            uint256 votesForOption = ec.votes[option];
            if (votesForOption > maxVotes) {
                maxVotes = votesForOption;
                winningOption = option;
            }
        }

        // Update reputation for voters
        for (uint256 i = 0; i < ec.voters.length; i++) {
            address voter = ec.voters[i];
            uint8 voterOption = ec.voterChoices[voter];
            uint256 fieldId = ec.fieldId;

            if (voterOption == winningOption) {
                // Voter chose the winning option, increment reputation
                reputationManager.updateReputation(voter, fieldId, 1);
            }
        }

        emit ExpertCaseClosed(_ECId, winningOption);
    }

    function getExpertCase(uint256 _ECId)
        public
        view
        returns (
            uint256 itemId,
            uint256 fieldId,
            uint256 minReputation,
            bool botAllowed,
            string memory ECInfo,
            bool isOpen
        )
    {
        require(expertCases[_ECId].exists, "EC_not_exist");
        ExpertCase storage ec = expertCases[_ECId];
        return (
            ec.itemId,
            ec.fieldId,
            ec.minReputation,
            ec.botAllowed,
            ec.ECInfo,
            ec.isOpen
        );
    }
}
