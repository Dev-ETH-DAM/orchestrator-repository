# type:ignore
from typing import Optional
from src.ContractUtility import ContractUtility
from src.utils import get_contract


async def set_message(
    address: str,
    message: str,
    network_name: str = "sapphire-localnet"
) -> None:
    contract_utility = ContractUtility(network_name)

    abi, bytecode = get_contract("MessageBox")

    contract = contract_utility.w3.eth.contract(
        address=address,
        abi=abi
    )

    gas_price = await contract_utility.w3.eth.gas_price
    tx_hash = await contract.functions.setMessage(message).transact(
        {"gasPrice": gas_price}
    )
    tx_receipt = await contract_utility.w3.eth.wait_for_transaction_receipt(
        tx_hash
    )
    print(f"""Message set.
          Transaction hash: {tx_receipt.transactionHash.hex()}"""
          )


async def get_message(
        address: str,
        network_name: Optional[str] = "sapphire-localnet"
) -> str:
    contract_utility = ContractUtility(network_name)

    abi, bytecode = get_contract("MessageBox")

    contract = contract_utility.w3.eth.contract(
        address=address,
        abi=abi
    )
    # Retrieve message from contract
    message = await contract.functions.message().call()
    author = await contract.functions.author().call()

    print(f"Retrieved message: {message}")
    print(f"Author: {author}")

    return message
