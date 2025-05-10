// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// import {Subcall} from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";
// import {SiweAuth} from "@oasisprotocol/sapphire-contracts/contracts/auth/SiweAuth.sol";

contract SubContract {
    // Enum representing the status of a crumb
    enum CrumbStatus { NEW, QUEUED, CLOSED, CLOSED_VALIDATED }

    // Struct representing a crumb
    struct Crumb {
        bytes16 id; // UUID represented as 16-byte value
        string aliasName;
        uint256 price; // Price in wei
        CrumbStatus status;
        string setupTask; // JSON string
        string setupValidation; // JSON string
        string result; // JSON string
        address assignee;
        uint256 lastUpdated; // Timestamp of last change
        uint256 maxRun;
    }

    // State variables
    address public requester;
    string public requestName;
    Crumb[] public crumbs;
    bytes21 public roflAppID;

    // Events
    event CrumbAdded(bytes16 indexed id, string aliasName);
    event CrumbUpdated(bytes16 indexed id, CrumbStatus status, address assignee);

    // Checks whether the transaction was signed by the ROFL's app key inside
    // TEE.
    // modifier onlyTEE(bytes21 appId) {
    //     Subcall.roflEnsureAuthorizedOrigin(appId);
    //     _;
    // }

    // Constructor to initialize requester and request name
    // TODO - only ROFL/TEE
    constructor(
        string memory _requestName, 
        address _requester, 
        bytes21 _roflAppID
        ) 
    {
        requester = _requester;
        requestName = _requestName;
        roflAppID = _roflAppID;
    }


    // Function to add a new crumb
    function addCrumb(
        bytes16 _id,
        string memory _aliasName,
        uint256 _price,
        string memory _setupTask,
        string memory _setupValidation,
        uint256 _maxRun
    ) public {
        // TODO - only ROFL/TEE
        Crumb memory newCrumb = Crumb({
            id: _id,
            aliasName: _aliasName,
            price: _price,
            status: CrumbStatus.NEW,
            setupTask: _setupTask,
            setupValidation: _setupValidation,
            result: "",
            assignee: address(0),
            lastUpdated: block.timestamp,
            maxRun: _maxRun
        });

        crumbs.push(newCrumb);
        emit CrumbAdded(_id, _aliasName);
    }

    // Function to update a crumb's status to Queued and assignee
    // asignee beeing the transaction signer
    function updateCrumbToQueued(bytes16 _id) public {
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].id == _id) {
                crumbs[i].status = CrumbStatus.QUEUED;
                crumbs[i].assignee = msg.sender;
                crumbs[i].lastUpdated = block.timestamp;
                emit CrumbUpdated(_id, CrumbStatus.QUEUED, msg.sender);
                return;
            }
        }
        revert("Crumb not found");
    }

    // Function to update a crumb's status to Closed and set the result
    // only if the assignee is the transaction signer
    function updateCrumbToClosed(
        bytes16 _id,
        string memory _result
    ) public {
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].id == _id) {
                require(crumbs[i].assignee == msg.sender, "Not authorized");
                crumbs[i].status = CrumbStatus.CLOSED;
                crumbs[i].result = _result;
                crumbs[i].lastUpdated = block.timestamp;
                emit CrumbUpdated(_id, CrumbStatus.CLOSED, msg.sender);
                return;
            }
        }
        revert("Crumb not found");
    }
    
    // Function to update a crumb's status to ClosedValidated
    // TODO - only ROFL/TEE
    function updateCrumbToClosedValidated(
        bytes16 _id
    ) public {
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].id == _id) {
                crumbs[i].status = CrumbStatus.CLOSED_VALIDATED;
                crumbs[i].lastUpdated = block.timestamp;
                emit CrumbUpdated(_id, CrumbStatus.CLOSED_VALIDATED, msg.sender);
                return;
            }
        }
        revert("Crumb not found");
    }

    // GETTERS
    // Function to retrieve a crumb by its ID
    function getCrumb(bytes16 _id) public view returns (Crumb memory) {
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].id == _id) {
                return crumbs[i];
            }
        }
        revert("Crumb not found");
    }

    // Function to get the total number of crumbs
    function getCrumbCount() public view returns (uint256) {
        return crumbs.length;
    }

    // Function to get all crumbs
    function getAllCrumbs() public view returns (Crumb[] memory) {
        return crumbs;
    }

    // Function to get the number of crumbs with a specific status
    function getCrumbCountByStatus(CrumbStatus _status) public view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].status == _status) {
                count++;
            }
        }
        return count;
    }

    // Function to get all crumbs with a specific status
    function getCrumbsByStatus(CrumbStatus _status) public view returns (Crumb[] memory) {
        uint256 count = getCrumbCountByStatus(_status);
        Crumb[] memory filteredCrumbs = new Crumb[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].status == _status) {
                filteredCrumbs[index] = crumbs[i];
                index++;
            }
        }
        return filteredCrumbs;
    }


    function getCrumbsByRequester() public view returns (Crumb[] memory) {
        uint256 count = 0;

        // Count crumbs for the requester
        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].assignee == msg.sender) {
                count++;
            }
        }

        // Create an array to store the matching crumbs
        Crumb[] memory filteredCrumbs = new Crumb[](count);
        uint256 index = 0;

        for (uint256 i = 0; i < crumbs.length; i++) {
            if (crumbs[i].assignee == msg.sender) {
                filteredCrumbs[index] = crumbs[i];
                index++;
            }
        }

        return filteredCrumbs;
    }


}

