// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ItemTracking {
    struct Item {
        uint256 id;
        address owner;
        string[] history;
        bool exists;
    }

    struct Expert {
        address addr;
        uint256 reputation;
        uint256 stake;
        bool exists;
    }

    struct Request {
        uint256 id;
        uint256 itemId;
        address requester;
        string newInfo;
        uint256 approvalCount;
        bool executed;
        mapping(address => bool) approvals;
    }

    mapping(uint256 => Item) public items;
    mapping(address => Expert) public experts;
    mapping(uint256 => Request) public requests;

    uint256 public requestCounter;
    address[] public expertList;
    uint256 public expertApprovalThreshold = 90; // 90% approval required
    uint256 public minimumStake = 1 ether;

    // Modifiers
    modifier onlyExpert() {
        require(experts[msg.sender].exists, "Caller is not an expert");
        _;
    }

    modifier itemExists(uint256 itemId) {
        require(items[itemId].exists, "Item does not exist");
        _;
    }

    // Events
    event ItemUpdated(uint256 indexed itemId, string newInfo);
    event RequestCreated(uint256 indexed requestId, uint256 indexed itemId, address requester);
    event ExpertApproved(address indexed expert);
    event ExpertCaseOpened(uint256 indexed caseId, uint256 indexed itemId);

    // Client Functions

    function checkItemHistory(uint256 itemId) public view itemExists(itemId) returns (string[] memory) {
        return items[itemId].history;
    }

    function requestChange(uint256 itemId, string memory newInfo) public itemExists(itemId) {
        requestCounter++;
        Request storage r = requests[requestCounter];
        r.id = requestCounter;
        r.itemId = itemId;
        r.requester = msg.sender;
        r.newInfo = newInfo;
        r.approvalCount = 0;
        r.executed = false;

        emit RequestCreated(requestCounter, itemId, msg.sender);
    }

    function requestExpertRole() public payable {
        require(msg.value >= minimumStake, "Insufficient stake");
        require(!experts[msg.sender].exists, "Already an expert");

        _addExpert(msg.sender, msg.value);

        // Auto-approve for simplicity
        emit ExpertApproved(msg.sender);
    }

    // Expert Functions

    function approveExpert(address applicant) public onlyExpert {
        require(experts[applicant].exists, "Applicant not found");

        // Implement approval logic (e.g., voting)
        // For simplicity, we'll auto-approve here
        experts[applicant].reputation = 100; // Initial reputation

        emit ExpertApproved(applicant);
    }

    function approveRequest(uint256 requestId) public onlyExpert {
        Request storage r = requests[requestId];
        require(!r.executed, "Request already executed");
        require(!r.approvals[msg.sender], "Already approved");

        r.approvals[msg.sender] = true;
        r.approvalCount++;

        if (r.approvalCount * 100 / expertList.length >= expertApprovalThreshold) {
            _executeRequest(requestId);
        }
    }

    function openExpertCase(uint256 itemId, string memory newInfo) public onlyExpert itemExists(itemId) {
        requestCounter++;
        Request storage r = requests[requestCounter];
        r.id = requestCounter;
        r.itemId = itemId;
        r.requester = msg.sender;
        r.newInfo = newInfo;
        r.approvalCount = 0;
        r.executed = false;

        emit ExpertCaseOpened(requestCounter, itemId);
    }

    // Internal Functions

    function _addExpert(address expertAddress, uint256 stake) internal {
        Expert storage e = experts[expertAddress];
        e.addr = expertAddress;
        e.reputation = 0;
        e.stake = stake;
        e.exists = true;
        expertList.push(expertAddress);
    }

    function _executeRequest(uint256 requestId) internal {
        Request storage r = requests[requestId];
        require(!r.executed, "Request already executed");

        Item storage item = items[r.itemId];
        item.history.push(r.newInfo);

        r.executed = true;

        emit ItemUpdated(r.itemId, r.newInfo);
    }

    // Additional Functions

    function createItem(uint256 itemId) public {
        require(!items[itemId].exists, "Item already exists");

        Item storage newItem = items[itemId];
        newItem.id = itemId;
        newItem.owner = msg.sender;
        newItem.exists = true;
    }

    // Public function to add experts for testing purposes
    function addExpert(address expertAddress, uint256 stake) public {
        _addExpert(expertAddress, stake);
    }

    // Getter function for Item
    function getItem(uint256 itemId)
        public
        view
        returns (uint256, address, string[] memory, bool)
    {
        require(items[itemId].exists, "Item does not exist");
        Item storage item = items[itemId];
        return (item.id, item.owner, item.history, item.exists);
    }

    // Getter function for Request
    function getRequest(uint256 requestId)
        public
        view
        returns (
            uint256,
            uint256,
            address,
            string memory,
            uint256,
            bool
        )
    {
        Request storage r = requests[requestId];
        return (
            r.id,
            r.itemId,
            r.requester,
            r.newInfo,
            r.approvalCount,
            r.executed
        );
    }

    // Fallback function to receive Ether
    receive() external payable {}
}