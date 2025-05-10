from dataclasses import dataclass
from typing import Optional, Tuple
from src.ContractUtility import ContractUtility
from src.utils import get_contract


@dataclass
class ComputeTask:
    sender: str  # Address is typically a string in Python
    timestamp: int
    content: str
    sum: int
    id: int
    subContractAddress: str  # Address is typically a string in Python

    @classmethod
    def from_tuple(cls, data: Tuple) -> 'ComputeTask':
        return cls(
            sender=data[0],  # Address (string)
            timestamp=data[1],  # Timestamp (int)
            content=data[2],  # Content (string)
            sum=data[3],  # Sum (int)
            id=data[4],  # ID (int)
            subContractAddress=data[5]  # Subcontract address (string)
        )


async def add_to_request_queue(
    address: str,
    content: str,
    sum_value: int,
    task_id: int,
    network_name: Optional[str] = "sapphire-testnet"
):
    contract_utility = ContractUtility(network_name)
    abi, _ = get_contract("MainContract")
    contract = contract_utility.w3.eth.contract(address=address, abi=abi)

    gas_price = await contract_utility.w3.eth.gas_price
    tx_hash = await contract.functions.addToRequestQueue(
        content, sum_value, task_id
    ).transact({"value": sum_value, "gasPrice": gas_price})
    tx_receipt = await contract_utility.w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"addToRequestQueue transaction: {tx_receipt.transactionHash.hex()}")
    print(tx_receipt)


async def move_to_in_progress_queue(
    address: str,
    task_id: int,
    sub_contract_address: str,
    network_name: Optional[str] = "sapphire-testnet"
):
    contract_utility = ContractUtility(network_name)
    abi, _ = get_contract("MainContract")
    contract = contract_utility.w3.eth.contract(address=address, abi=abi)

    gas_price = await contract_utility.w3.eth.gas_price
    tx_hash = await contract.functions.moveToInProgressQueue(
        task_id, sub_contract_address
    ).transact({"gasPrice": gas_price})
    tx_receipt = await contract_utility.w3.eth.wait_for_transaction_receipt(tx_hash)
    print(
        f"moveToInProgressQueue transaction: {tx_receipt.transactionHash.hex()}")


async def move_to_completed_queue(
    address: str,
    task_id: int,
    network_name: Optional[str] = "sapphire-testnet"
):
    contract_utility = ContractUtility(network_name)
    abi, _ = get_contract("MainContract")
    contract = contract_utility.w3.eth.contract(address=address, abi=abi)

    gas_price = await contract_utility.w3.eth.gas_price
    tx_hash = await contract.functions.moveToCompletedQueue(
        task_id
    ).transact({"gasPrice": gas_price})
    tx_receipt = await contract_utility.w3.eth.wait_for_transaction_receipt(tx_hash)
    print(
        f"moveToCompletedQueue transaction: {tx_receipt.transactionHash.hex()}")


async def get_request_queue(
    address: str,
    network_name: Optional[str] = "sapphire-testnet"
) -> list[ComputeTask]:
    contract_utility = ContractUtility(network_name)
    abi, _ = get_contract("MainContract")
    contract = contract_utility.w3.eth.contract(address=address, abi=abi)

    queue = await contract.functions.getRequestQueue().call()
    print(f"RequestQueue: {queue}")
    return [ComputeTask.from_tuple(ct) for ct in queue]


async def get_in_progress_queue(
    address: str,
    network_name: Optional[str] = "sapphire-testnet"
):
    contract_utility = ContractUtility(network_name)
    abi, _ = get_contract("MainContract")
    contract = contract_utility.w3.eth.contract(address=address, abi=abi)

    queue = await contract.functions.getInProgressQueue().call()
    print(f"InProgressQueue: {queue}")
    return [ComputeTask.from_tuple(ct) for ct in queue]


async def get_completed_queue(
    address: str,
    network_name: Optional[str] = "sapphire-testnet"
):
    contract_utility = ContractUtility(network_name)
    abi, _ = get_contract("MainContract")
    contract = contract_utility.w3.eth.contract(address=address, abi=abi)

    queue = await contract.functions.getCompletedQueue().call()
    print(f"CompletedQueue: {queue}")
    return [ComputeTask.from_tuple(ct) for ct in queue]
