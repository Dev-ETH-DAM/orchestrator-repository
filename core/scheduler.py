from asyncio import sleep
import os
from web3 import Web3, AsyncWeb3
from web3.middleware import SignAndSendRawMiddlewareBuilder

from eth_account.signers.local import LocalAccount
from eth_account import Account
from sapphirepy import sapphire
import json
from pathlib import Path
from typing import Union
from core.transformer_task import TransformerTask


class Orchestrator:
    def __init__(self, network: str, contract: str, pkey: str):
        self.network = network
        self.contract = contract
        self.pkey = pkey

        if not all(
            [
                self.pkey,
            ]
        ):
            raise Warning("""Missing required environment variables.
                          Please set PRIVATE_KEY.""")

        private_key_file = open(self.pkey)
        account: LocalAccount = Account.from_key(private_key_file.read())

        w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(
                sapphire.NETWORKS[self.network]
            )
        )

        w3.middleware_onion.add(
            SignAndSendRawMiddlewareBuilder.build(account)
        )
        w3 = sapphire.wrap(w3, account)
        # w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
        w3.eth.default_account = account.address
        self.w3: Web3 | AsyncWeb3 = w3

    # Functions for working with contracts
    def process_json_file(filepath, mode="r", data=None):
        with open(filepath, mode) as file:
            if mode == "r":
                return json.load(file)
            elif mode == "w" and data:
                json.dump(data, file)

    def get_contract(self, contract_name: str):
        output_path = (
            Path(__file__).parent.parent
            / "compiled_contracts"
            / f"{contract_name}_compiled.json"
        ).resolve()
        compiled_contract = self.process_json_file(output_path)

        contract_data = compiled_contract["contracts"][f"{contract_name}.sol"][
            contract_name
        ]
        abi, bytecode = (
            contract_data["abi"],
            contract_data["evm"]["bytecode"]["object"]
        )
        return abi, bytecode

    def fetch_job(self):
        self.current_job = {
            "name": "testjob",
            "params": """{
                "task_type": "sentiment-analysis",
                "model_name": "",
                "dataset_url": "",
                "id_dict": {},
                "label_dict": {},
                "batch_size": 32,
                "train_ds_url": "",
                "test_ds_url": "",
                "ds_text_column": "text",
                "ds_id_column": "id",
                "predict_ds_url": "https://raw.githubusercontent.com/AskingAlexander/Datasets/refs/heads/master/sample.csv"
            }"""
        }
        return True


async def start_orchestrator(
    network: str,
    contract: str,
    pkey: str,
) -> None:
    # Initialize the Orchestrator
    print("Starting orchestrator...")
    print(f"Network: {network}")
    print(f"Contract: {contract}")
    orchestrator = Orchestrator(network, contract,  pkey)

    print("Starting recurring task for fetching jobs...")
    while orchestrator.fetch_job():
        task = TransformerTask()
        task.set_params(orchestrator.current_job["params"])
        task.start_working()

        print(task.get_results())
        await sleep(10)
