// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReputationManager {
    struct Reputation {
        int256 totalScore;
        uint256 totalCases;
        mapping(uint256 => int8) recentScores;
        uint256 recentIndex;
    }

    // Use public key (string) to identify users, and fieldId (uint256) for reputation within fields
    mapping(string => mapping(uint256 => Reputation)) private reputations;

    uint256 public constant MAX_RECENT_SCORES = 100;

    event ReputationUpdated(string user, uint256 indexed fieldId, int8 score);

    // Update the reputation of a user identified by their public key
    function updateReputation(
        string memory _user,  // Public key as string
        uint256 _fieldId,          // Field ID to track reputation in a specific area
        int8 _score                // Score to be added (positive or negative)
    ) external {
        Reputation storage rep = reputations[_user][_fieldId];

        // Update the total score and total cases
        rep.totalScore += _score;
        rep.totalCases += 1;

        // Add the score to the recent scores array with circular indexing
        rep.recentScores[rep.recentIndex % MAX_RECENT_SCORES] = _score;
        rep.recentIndex += 1;

        // Emit the ReputationUpdated event with public key and field ID
        emit ReputationUpdated(_user, _fieldId, _score);
    }

    // Get the sum of recent reputation scores for a user in a specific field
    function getReputation(string memory _user, uint256 _fieldId)
        external
        view
        returns (int256 sumRecentScores)
    {
        Reputation storage rep = reputations[_user][_fieldId];

        // Determine the number of recent scores to sum (based on totalCases vs. MAX_RECENT_SCORES)
        uint256 scoresCount = rep.totalCases > MAX_RECENT_SCORES ? MAX_RECENT_SCORES : rep.totalCases;
        sumRecentScores = 0;

        // Sum up the recent scores
        for (uint256 i = 0; i < scoresCount; i++) {
            sumRecentScores += rep.recentScores[i];
        }
    }
}
