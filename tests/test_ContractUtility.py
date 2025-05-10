import os
import pytest
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider

# Set default private key
if os.environ.get("PRIVATE_KEY") is None:
    os.environ["PRIVATE_KEY"] = (
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    )

from src.MessageBox import set_message, get_message
from src.ContractUtility import ContractUtility
from unittest.mock import MagicMock, patch, AsyncMock, PropertyMock


@pytest.mark.asyncio
async def test_contract_utility_init():
    with patch("src.ContractUtility.setup_web3_middleware", return_value=AsyncMock()) as mock_middleware:
        util = ContractUtility("sapphire-localnet")
        mock_middleware.assert_called_once()
        assert isinstance(util, ContractUtility)
        assert util.w3 == mock_middleware.return_value


@patch("src.ContractUtility.compile_standard", return_value="compiled_sol")
@patch("src.ContractUtility.install_solc")
@patch("builtins.open", new_callable=MagicMock)
@patch("src.ContractUtility.setup_web3_middleware", return_value={})
def test_setup_and_compile_contract(
    mock_middleware, mock_open, mock_install_solc, mock_compile_standard
):
    util = ContractUtility("sapphire-localnet")
    contract_name = "MessageBox"

    output = util.setup_and_compile_contract(contract_name)

    mock_install_solc.assert_called_once()
    mock_compile_standard.assert_called_once()

    assert output == "compiled_sol"


def test_compiles_contract_successfully():
    """
    Make sure sapphire-localnet is running before running the following tests!
    """
    contract_utility = ContractUtility("sapphire-localnet")
    contract_name = "MessageBox"
    contract_utility.setup_and_compile_contract(contract_name)
    
    # Get the directory of the current test file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go one level up to the project root
    project_root = os.path.dirname(current_dir)
    # Join with the compiled_contracts directory
    compiled_contracts_dir = os.path.join(project_root, "compiled_contracts")
    
    assert contract_name + "_compiled.json" in os.listdir(compiled_contracts_dir)


@pytest.mark.asyncio
async def test_deploys_contract_successfully():
    contract_name = "MessageBox"
    contract_utility = ContractUtility("sapphire-localnet")
    contract_address = await contract_utility.deploy_contract(contract_name)
    contract_code = await contract_utility.w3.eth.get_code(contract_address)
    assert contract_code != "0x"
    await contract_utility.w3.provider.disconnect()


@pytest.mark.asyncio
async def test_sets_message_successfully():
    contract_name = "MessageBox"
    contract_message = "Hello World"
    contract_utility = ContractUtility("sapphire-localnet")
    contract_address = await contract_utility.deploy_contract(contract_name)
    await set_message(contract_address, contract_message)
    message = await get_message(contract_address)
    assert message == contract_message
    await contract_utility.w3.provider.disconnect()


@pytest.mark.asyncio
async def test_websocket_connection():
    contract_name = "MessageBox"
    contract_utility = ContractUtility("sapphire-localnet")
    block_number = await contract_utility.w3.eth.get_block_number()
    
    print(f"Block number: {block_number}")

    async with AsyncWeb3(WebSocketProvider(f"ws://localhost:8546")) as w3:
        subscription_id = await w3.eth.subscribe("newHeads")
        async for response in w3.socket.process_subscriptions():
            if response['result'].get('number') > block_number + 5:
                contract_address = await contract_utility.deploy_contract(contract_name)
                contract_code = await contract_utility.w3.eth.get_code(contract_address)
                assert contract_code != "0x"
                await w3.eth.unsubscribe(subscription_id)
                break

        latest_block = await w3.eth.get_block("latest")
        print(f"Latest block: {latest_block}")
    await contract_utility.w3.provider.disconnect()
    