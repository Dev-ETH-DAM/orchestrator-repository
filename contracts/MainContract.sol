// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract MainContract {
    struct ComputeTask {
        address sender;
        uint256 timestamp;
        string content;
        uint256 sum;
        uint256 id;
        address subContractAddress;
    }

    ComputeTask[] public RequestQueue;
    ComputeTask[] public InProgressQueue;
    ComputeTask[] public CompletedQueue;

    // Function to add a new task to the request queue
    //Public available to all users
    function addToRequestQueue(
        string memory _content,
        uint256 _sum,
        uint256 _id
    ) public payable {
        require(msg.value == _sum, "Incorrect token amount sent");
        require(msg.sender.balance >= _sum, "Insufficient balance to add task");

        ComputeTask memory newTask = ComputeTask({
            sender: msg.sender,
            timestamp: block.timestamp,
            content: _content,
            sum: _sum,
            id: _id,
            subContractAddress: address(0)
        });

        RequestQueue.push(newTask);
    }

    //Function to move a task from the RequestQueue to the InProgressQueue
    //only availabe to the ROFL/TEE
    function moveToInProgressQueue(uint256 _id, address _subContractAddress) public {
        for (uint256 i = 0; i < RequestQueue.length; i++) {
            if (RequestQueue[i].id == _id) {
                // Update the subcontract address
                RequestQueue[i].subContractAddress = _subContractAddress;

                // Add the task to the InProgressQueue
                InProgressQueue.push(RequestQueue[i]);

                // Remove the task from the RequestQueue
                RequestQueue[i] = RequestQueue[RequestQueue.length - 1];
                RequestQueue.pop();

                return;
            }
        }
        revert("Task with the given ID not found in RequestQueue");
    }

    //Function to move a task from the InProgressQueue to the CompletedQueue
    //only availabe to the ROFL/TEE
    function moveToCompletedQueue(uint256 _id) public {
        for (uint256 i = 0; i < InProgressQueue.length; i++) {
            if (InProgressQueue[i].id == _id) {
                // Add the task to the CompletedQueue
                CompletedQueue.push(InProgressQueue[i]);

                // Remove the task from the InProgressQueue
                InProgressQueue[i] = InProgressQueue[InProgressQueue.length - 1];
                InProgressQueue.pop();

                return;
            }
        }
        revert("Task with the given ID not found in InProgressQueue");
    }

    function getRequestQueue() public view returns (ComputeTask[] memory) {
        return RequestQueue;
    }

    function getInProgressQueue() public view returns (ComputeTask[] memory) {
        return InProgressQueue;
    }

    function getCompletedQueue() public view returns (ComputeTask[] memory) {
        return CompletedQueue;
    }

}