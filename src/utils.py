from web3 import Web3, AsyncWeb3
from web3.middleware import SignAndSendRawMiddlewareBuilder

from eth_account.signers.local import LocalAccount
from eth_account import Account
from sapphirepy import sapphire
import json
from pathlib import Path
from typing import Union


def setup_web3_middleware(
        network_name: str,
        PRIVATE_KEY: str,
        ) -> Union[Web3, AsyncWeb3]:
    if not all(
        [
            PRIVATE_KEY,
        ]
    ):
        raise Warning("""Missing required environment variables.
                      Please set PRIVATE_KEY.""")

    account: LocalAccount = Account.from_key(PRIVATE_KEY)
    w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(
                sapphire.NETWORKS[network_name]
                )
            )

    w3.middleware_onion.add(
        SignAndSendRawMiddlewareBuilder.build(account)
        )
    w3 = sapphire.wrap(w3, account)
    # w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
    w3.eth.default_account = account.address
    return w3


def process_json_file(filepath, mode="r", data=None):
    with open(filepath, mode) as file:
        if mode == "r":
            return json.load(file)
        elif mode == "w" and data:
            json.dump(data, file)


def get_contract(contract_name: str):
    output_path = (
        Path(__file__).parent.parent
        / "compiled_contracts"
        / f"{contract_name}_compiled.json"
    ).resolve()
    compiled_contract = process_json_file(output_path)

    contract_data = compiled_contract["contracts"][f"{contract_name}.sol"][
        contract_name
    ]
    abi, bytecode = (
        contract_data["abi"],
        contract_data["evm"]["bytecode"]["object"]
        )
    return abi, bytecode
