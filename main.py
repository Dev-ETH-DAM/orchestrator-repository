#!/usr/bin/env python3

import asyncio
import os
from core.scheduler import start_orchestrator
from src.ContractUtility import ContractUtility
from src.MessageBox import set_message, get_message
import argparse


async def async_main():
    """
    Main method for the Python CLI tool.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description="""A Python CLI tool for compiling,
                    deploying, and interacting with smart contracts."""
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Subparser for compile
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile the source code"
    )
    compile_parser.add_argument(
        "--contract",
        help="Name of the contract to compile",
        default="MessageBox"
    )

    # Subparser for deploy
    deploy_parser = subparsers.add_parser(
        "deploy",
        help="Deploy the smart contract"
    )
    deploy_parser.add_argument(
        "--contract",
        help="Name of the contract to deploy",
        default="MessageBox"
    )
    deploy_parser.add_argument(
        "--network",
        help="Chain name to connect to "
        "(sapphire, sapphire-testnet, sapphire-localnet)",
        required=True,
    )

    # Subparser for set message
    set_message_parser = subparsers.add_parser(
        "setMessage", help="Interact with a deployed contract"
    )
    set_message_parser.add_argument(
        "--address", help="Contract address to call", required=True
    )
    set_message_parser.add_argument(
        "--message", help="Message to store in the contract", required=True
    )
    set_message_parser.add_argument(
        "--network",
        help="Chain name to connect to "
        "(sapphire, sapphire-testnet, sapphire-localnet)",
        required=True,
    )

    # Subparser for get message
    get_message_parser = subparsers.add_parser(
        "message", help="Interact with a deployed contract"
    )
    get_message_parser.add_argument(
        "--address", help="Contract address to call", required=True
    )
    get_message_parser.add_argument(
        "--network",
        help="Chain name to connect to "
        "(sapphire, sapphire-testnet, sapphire-localnet)",
        required=True,
    )

    # Subparser for start
    start_parser = subparsers.add_parser(
        "start",
        help="Start the application"
    )

    start_parser.add_argument(
        "--network",
        help="Chain name to connect to "
        "(sapphire, sapphire-testnet, sapphire-localnet)",
        required=True,
    )
    start_parser.add_argument(
        "--pkfile",
        help="Path to the private key file",
        required=True,
    )

    arguments = parser.parse_args()

    match arguments.command:
        case "compile":
            # Use class method which does not
            # require an instance of ContractUtility.
            # This is to avoid setting up the Web3 instance
            # which requires the PRIVATE_KEY.
            ContractUtility.setup_and_compile_contract(arguments.contract)
        case "deploy":
            contract_utility = ContractUtility(arguments.network)
            await contract_utility.deploy_contract(arguments.contract)
        case "setMessage":
            await set_message(
                arguments.address,
                arguments.message,
                arguments.network
            )
        case "message":
            await get_message(arguments.address, arguments.network)
        case "start":
            print("Starting the application...")
            print("With private key file [" + arguments.pkfile +
                  "] on network [" + arguments.network + "]")
            await start_orchestrator(
                network=arguments.network,
                contract="MessageBox",
                pkey=arguments.pkfile,

            )
        case _:
            parser.print_help()


def main():
    """
    Entry point that runs the async main function
    """
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
