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
from src.SubContract import Crumb, CrumbStatus, update_crumb_to_closed
from core.transformer_task import TransformerTask
from src.SubContract import get_crumbs_by_status, get_crumbs_by_requester
from src.MainContract import get_in_progress_queue, ComputeTask


class Orchestrator:
    def __init__(self, network: str, contract: str, pkey: str):
        self.network: str = network
        self.contract: str = contract
        self.pkey: str = pkey
        self.current_job: Crumb | None = None
        self.selected_contract: str | None = None
        if not all(
            [
                self.pkey,
            ]
        ):
            raise Warning("""Missing required environment variables.
                          Please set PRIVATE_KEY.""")

        private_key_file = open(self.pkey)
        private_key_value: str = private_key_file.read()

        os.environ.setdefault("PRIVATE_KEY", private_key_value)
        account: LocalAccount = Account.from_key(private_key_value)

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

    async def fetch_job(self):
        # Get crumbs that have been selected for work
        MAIN_CONTRACT_ADDR = "0x885cA90bD752A682dD1883614edA0C0557c973a6"
        all_subcontracts: list[ComputeTask] = await get_in_progress_queue(MAIN_CONTRACT_ADDR)
        for contract in all_subcontracts:
            available_crumbs: list[Crumb] = await get_crumbs_by_requester(contract.subContractAddress)
            if len(available_crumbs) > 0:
                for crumb in available_crumbs:
                    if crumb.status.value == CrumbStatus.QUEUED.value:
                        self.current_job = crumb
                        self.selected_contract = contract.subContractAddress
                        break
                if self.current_job is None:
                    continue
                # Shameful hack to get the setup_task
                self.current_job.setup_task = json.loads(
                    self.current_job.setup_task)
                self.current_job.setup_validation = json.loads(
                    self.current_job.setup_validation)
                break
        return self.current_job is not None

    async def publish_job_results(self, result: str) -> bool:
        if self.current_job is None:
            raise Exception("Current job is None")
        await update_crumb_to_closed(self.selected_contract, self.current_job.id, result)
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
    while True:
        await orchestrator.fetch_job()
        if orchestrator.current_job is None:
            await sleep(30)
            continue
        task = TransformerTask()
        task.set_params(
            orchestrator.current_job.setup_task)
        task.start_working()

        result_str = str(task.get_results())
        await orchestrator.publish_job_results(result_str)

        await sleep(30)
