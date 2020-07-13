#!/usr/bin/env python3

import os
import sys
import json
from getpass import getpass
import argparse
import traceback

import web3
from web3 import Web3

CONTRACT_NAME = "CCBDC"
CONTRACT_INFO_FILE = f"{CONTRACT_NAME}-contract.info"
NODE_INFO_FILE= "info.json"
RPC_IPC = os.path.join("data", "geth.ipc")
PROG = sys.argv[0]

class Contract(object):
    """Represents a contract wrapper to easily interact."""
    def __init__(self, info_file, node_info, ipc):
        self.addr, self.abi = self.read_contract_info(info_file)
        self.w3 = self.connect(ipc)
        self.instance = self.w3.eth.contract(self.addr, abi=self.abi)

        # account related
        self.addr =  self.get_main_addr(node_info)
        self.w3.eth.defaultAccount = self.addr

    def connect(self, ipc):
        try:
            w3 = Web3(Web3.IPCProvider(ipc))
            w3.middleware_onion.inject(web3.middleware.geth_poa_middleware, layer=0)
            if not w3.isConnected():
                raise Exception
        except:
            print(f"Could not connect to IPC '{ipc}'")
            sys.exit(1)

        return w3

    def get_main_addr(self, node_info):
        """Gets account address"""
        try:
            with open(node_info) as f:
                data = json.load(f)
        except:
            print("Could not read node's info file 'info.json'.")
            sys.exit(1)

        return data["acc_addrs"]["main"]

    def read_contract_info(self, info_file):
        """Retrieves addr and ABI from config file."""
        try:
            with open(info_file) as f:
                contract_dict = json.load(f)
        except:
            print(f"Could not read contract's info file '{info_file}.'")
            sys.exit(1)

        return contract_dict["addr"], contract_dict["get_abi"]

    def unlock_acc(self):
        """Unlocks given main account."""
        passphrase = getpass()
        try:
            self.w3.geth.personal.unlockAccount(self.addr, passphrase)
            print("Correct.\n")
        except:
            print(f"\nCould not unlock node's main account '{self.addr}' with given password.")
            sys.exit(1)

    def call(self, func_name, *args):
        """Calls the contract functions."""
        self.unlock_acc()
        return self.caller(func_name, *args)

    def caller(self, func_name, *args):
        raise NotImplementedError

class CCBDC(Contract):
    """Represents an API to the governing contracts."""

    def caller(self, func_name, *args):
        """Handles calls to contract."""
        if func_name == "balance":
            coin_id, addr = args
            try:
                return self.instance.functions.balanceOf(coin_id, addr).call()
            except:
                return "Something went wrong."
        if func_name == "show":
            coin_id = args[0]
            try:
                return self.instance.functions.showCoinInfo(coin_id).call()
            except:
                traceback.print_exc()
                return "Something went wrong."
        elif func_name == "create":
            color, shades, supply, deadline = args
            tx_hash = self.instance.functions.createNewCoin(color, shades, supply, deadline).transact({"gas": 10000000})
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            return self.instance.events.CoinCreation().processReceipt(tx_receipt)
        elif func_name == "approve":
            req_id = args[0]
            tx_hash = self.instance.functions.approveMintingRequest(req_id).transact({"gas": 10000000})
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            return self.instance.events.Approval().processReceipt(tx_receipt)
        else:
            print(f"Unkown function name '{func_name}'.")
            sys.exit(1)

def arg_parser():
    """Defines parser for command line input."""
    parser = argparse.ArgumentParser(prog=PROG, description="Command line wrapper to interact with CCBDC contract.")
    parser.add_argument("--ipc", help="Path to 'geth.ipc'.", default=RPC_IPC, metavar="path/to/ipc", type=str)
    parser.add_argument("--info", help=f"Path to '{CONTRACT_NAME}-contract.info'.", default=CONTRACT_INFO_FILE, metavar=f"/path/to/{CONTRACT_NAME}.info", type=str)
    parser.add_argument("--node-info", help=f"Path to node's 'info.json'.", default=NODE_INFO_FILE, metavar="/path/to/info.json", type=str)
    subparsers = parser.add_subparsers(dest="cmd")

    # balance subcmd
    balance_parser = subparsers.add_parser("balance", help="Shows the address' balance of a given colored coin.")
    balance_parser.add_argument("-c", required=True, type=int, help="Of which colored coin.", metavar="<coin-id>")
    balance_parser.add_argument("-a", required=True, type=str, help="Balance of this address.", metavar="<addr>")

    # approve subcmd
    approve_parser = subparsers.add_parser("approve", help="Approves a request.")
    approve_parser.add_argument("-r", required=True, type=int, help="ID of request to be approved.", metavar="<req-id>")

    # show subcmd
    show_parser = subparsers.add_parser("show", help="Shows colored coin details.")
    show_parser.add_argument("-c", required=True, type=int, help="ID of coin to be shown.", metavar="<coin-id>")

    # create subcmd
    create_parser = subparsers.add_parser("create", help="Creates a new colored coin.")
    create_parser.add_argument("-C", required=True, type=int, help="Color of new coin.", metavar="<color-id>")
    create_parser.add_argument("-S", required=True, nargs="+", type=int, help="Shade/Merchantcode that converts colored coin to general CBDC.", metavar="<shade>...")
    create_parser.add_argument("-s", required=True, type=int, help="Initial supply of new coin.", metavar="<supply>")
    create_parser.add_argument("-d", required=True, type=int, help="Amount of blocks the new coin can exist before destroyed.", metavar="<deadline>")

    return parser

def main():
    args = arg_parser().parse_args()
    if "a" in vars(args).keys():
        try:
            args.a = Web3.toChecksumAddress(args.a)
        except:
            print("Invalid address format")
            sys.exit(1)

    contract = CCBDC(args.info, args.node_info, args.ipc)

    # check which subcmd was used and act accordingly
    if args.cmd == "balance":
        print(">", contract.call("balance", args.c, args.a))
    elif args.cmd == "create":
        print(">", contract.call("create", args.C, args.S, args.s, args.d))
    elif args.cmd == "approve":
        print(">", contract.call("approve", args.r))
    elif args.cmd == "show":
        print(">", contract.call("show", args.c))

if __name__ == "__main__":
    main()
