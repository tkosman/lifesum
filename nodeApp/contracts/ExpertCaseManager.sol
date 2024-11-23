// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IReputationManager {
    function updateReputation(string memory _user, uint256 _fieldId, int8 _score) external;
    function getReputation(string memory _user, uint256 _fieldId) external view returns (uint256);
}

interface IUserRegistry {
    function getNickByAddress(string memory _address) external view returns (string memory);
    function getUserInfo(string memory _nick)
        external
        view
        returns (
            string memory public_key,
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
        mapping(string => bool) hasVoted;
        mapping(string => uint8) voterChoices;
        string[] voters;
        mapping(uint8 => uint256) votes;
        uint8[] optionsVoted; // Added to track voted options
        bool isOpen;
        bool exists;
    }

    mapping(uint256 => ExpertCase) private expertCases;
    uint256 private ECIdCounter;

    IReputationManager private reputationManager;
    IUserRegistry private userRegistry;

    event ExpertCaseOpened(uint256 ECId, uint256 itemId, string openedBy);
    event VoteCast(uint256 ECId, string voter, uint8 option);
    event ExpertCaseClosed(uint256 ECId, uint8 winningOption);

    constructor(address _reputationManagerAddress, address _userRegistryAddress) {
        reputationManager = IReputationManager(_reputationManagerAddress);
        userRegistry = IUserRegistry(_userRegistryAddress);
    }

    function openExpertCase(
        uint256 _itemId,
        uint256 _fieldId,
        uint256 _minReputation,
        string memory _publicKey,
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

        emit ExpertCaseOpened(newECId, _itemId, _publicKey);

        return newECId;
    }

    function castVote(
        uint256 _ECId,
        uint8 _option,
        string memory _publicKey
    ) public {
        require(expertCases[_ECId].exists, "EC_not_exist");
        require(expertCases[_ECId].isOpen, "EC_closed");

        ExpertCase storage ec = expertCases[_ECId];

        // Verify voter registration
        string memory voterNick = userRegistry.getNickByAddress(_publicKey);
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
        uint256 userReputation = reputationManager.getReputation(_publicKey, ec.fieldId);
        require(userReputation >= ec.minReputation, "reputation_too_low");

        // Check if user has already voted
        require(!ec.hasVoted[_publicKey], "already_voted");

        // Record the vote
        ec.hasVoted[_publicKey] = true;
        ec.votes[_option] += 1;
        ec.voterChoices[_publicKey] = _option;
        ec.voters.push(_publicKey);

        // Add option to optionsVoted if it's the first vote for that option
        if (ec.votes[_option] == 1) {
            ec.optionsVoted.push(_option);
        }

        emit VoteCast(_ECId, _publicKey, _option);
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

        uint256 winningVotersCount = 0;
        for (uint256 i = 0; i < ec.voters.length; i++) {
            string memory voter = ec.voters[i];
            if (ec.voterChoices[voter] == winningOption) {
                winningVotersCount += 1;
            }
        }

        int256 reputationIncrementTemp = int256(ec.voters.length / winningVotersCount);
        int8 reputationIncrement = reputationIncrementTemp > 10 ? int8(10) : int8(reputationIncrementTemp);

        // Update reputation for voters
        for (uint256 i = 0; i < ec.voters.length; i++) {
            string memory voter = ec.voters[i];
            uint8 voterOption = ec.voterChoices[voter];
            uint256 fieldId = ec.fieldId;

            if (voterOption == winningOption) {
                reputationManager.updateReputation(voter, fieldId, reputationIncrement);
            }
            else {
                reputationManager.updateReputation(voter, fieldId, -1);
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
