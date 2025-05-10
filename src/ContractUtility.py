import os
from pathlib import Path
from solcx import compile_standard, install_solc

from src.utils import (
    setup_web3_middleware,
    get_contract,
    process_json_file,
)


class ContractUtility:
    """
    Initializes the ContractUtility class.

    :param network_name: Name of the network to connect to
    :type network_name: str
    :return: None
    """

    def __init__(self, network_name: str):
        PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
        self.w3 = setup_web3_middleware(network_name, PRIVATE_KEY)

    @classmethod
    def setup_and_compile_contract(
        cls, contract_name: str = "MessageBox", SOLIDITY_VERSION: str = "0.8.0"
    ) -> str:
        # This remains synchronous as compilation doesn't need to be async.
        install_solc(SOLIDITY_VERSION)
        contract_dir = (Path(__file__).parent.parent / "contracts").resolve()
        contract_dir.mkdir(parents=True, exist_ok=True)
        contract_path = contract_dir / f"{contract_name}.sol"
        with open(contract_path, "r") as file:
            contract_source_code = file.read()
        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {f"{contract_name}.sol":
                            {"content": contract_source_code}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi",
                                    "metadata",
                                    "evm.bytecode",
                                    "evm.sourceMap"
                                    ]}
                    }
                },
            },
            solc_version=SOLIDITY_VERSION,
        )
        output_path = (
            Path(__file__).parent.parent
            / "compiled_contracts"
            / f"{contract_name}_compiled.json"
        ).resolve()
        Path(output_path.parent).mkdir(parents=True, exist_ok=True)
        process_json_file(output_path, mode="w", data=compiled_sol)
        print(f"Compiled contract {contract_name} {output_path}")
        return compiled_sol

    async def deploy_contract(self, contract_name: str):
        abi, bytecode = get_contract(contract_name)
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        gas_price = await self.w3.eth.gas_price
        tx_hash = await contract.constructor().transact({
            "gasPrice": gas_price
            })
        tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Contract deployed at {tx_receipt.contractAddress}")
        return tx_receipt.contractAddress
