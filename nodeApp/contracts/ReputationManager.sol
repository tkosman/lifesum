// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ReputationManager {
    struct Reputation {
        uint256 totalScore;
        uint256 totalCases;
        mapping(uint256 => uint8) recentScores;
        uint256 recentIndex;
    }

    mapping(address => mapping(uint256 => Reputation)) private reputations;

    uint256 public constant MAX_RECENT_SCORES = 100;

    event ReputationUpdated(address indexed user, uint256 indexed fieldId, uint8 score);

    function updateReputation(
        address _user,
        uint256 _fieldId,
        uint8 _score
    ) external {
        Reputation storage rep = reputations[_user][_fieldId];
        rep.totalScore += _score;
        rep.totalCases += 1;

        rep.recentScores[rep.recentIndex % MAX_RECENT_SCORES] = _score;
        rep.recentIndex += 1;

        emit ReputationUpdated(_user, _fieldId, _score);
    }

    function getReputation(address _user, uint256 _fieldId)
        external
        view
        returns (uint256 averageScore)
    {
        Reputation storage rep = reputations[_user][_fieldId];
        uint256 scoresCount = rep.totalCases > MAX_RECENT_SCORES
            ? MAX_RECENT_SCORES
            : rep.totalCases;
        uint256 sumRecentScores = 0;

        for (uint256 i = 0; i < scoresCount; i++) {
            sumRecentScores += rep.recentScores[i];
        }

        averageScore = scoresCount > 0 ? sumRecentScores / scoresCount : 0;
    }
}
