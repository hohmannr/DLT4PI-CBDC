#!/usr/bin/env python3

import os
import sys
import json
from getpass import getpass
import argparse
import traceback

import web3
from web3 import Web3

CONTRACT_NAME = "Governing"
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

class Governing(Contract):
    """Represents an API to the governing contracts."""

    def caller(self, func_name, *args):
        """Handles calls to contract."""
        # translate string from command line to enum int of contract
        type_to_int = {
            "governor": 0,
            "maintainer": 1,
            "observer": 2,
            "banker": 3,
            "blacklist": 4
        }

        if func_name == "add":
            t, addr = args
            tx_hash = self.instance.functions.makeProposal(addr, type_to_int[t], 0).transact({"gas": 1000000})
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            return self.instance.events.NewProposal().processReceipt(tx_receipt)
        elif func_name == "remove":
            t, addr = args
            tx_hash = self.instance.functions.makeProposal(addr, type_to_int[t], 1).transact({"gas": 1000000})
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            return self.instance.events.NewProposal().processReceipt(tx_receipt)
        elif func_name == "is":
            t, addr = args
            if t == "governor":
                try:
                    return self.instance.functions.governors(addr).call()
                except:
                    return False
            elif t == "maintainer":
                try:
                    return self.instance.functions.maintainers(addr).call()
                except:
                    return False
            elif t == "observer":
                try:
                    return self.instance.functions.observers(addr).call()
                except:
                    return False
            elif t == "banker":
                try:
                    return self.instance.functions.bankers(addr).call()
                except:
                    return False
            elif t == "blacklist":
                try:
                    return self.instance.functions.blacklist(addr).call()
                except:
                    return False
        elif func_name == "vote":
            tx_hash = self.instance.functions.vote(args[0]).transact({"gas": 1000000})
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            return self.instance.events.NewVote().processReceipt(tx_receipt)
        else:
            print(f"Unkown function name '{func_name}'.")
            sys.exit(1)

def arg_parser():
    """Defines parser for command line input."""
    parser = argparse.ArgumentParser(prog=PROG, description="Command line wrapper to interact with governing contract.")
    parser.add_argument("--ipc", help="Path to 'geth.ipc'.", default=RPC_IPC, metavar="path/to/ipc", type=str)
    parser.add_argument("--info", help=f"Path to '{CONTRACT_NAME}-contract.info'.", default=CONTRACT_INFO_FILE, metavar=f"/path/to/{CONTRACT_NAME}.info", type=str)
    parser.add_argument("--node-info", help=f"Path to node's 'info.json'.", default=NODE_INFO_FILE, metavar="/path/to/info.json", type=str)
    subparsers = parser.add_subparsers(dest="cmd")

    # add subcmd
    add_parser = subparsers.add_parser("add", help="Makes proposal to add given address to specified type.")
    add_parser.add_argument("-t", required=True, choices=["maintainer", "observer", "governor", "blacklist", "banker"], type=str, help="Make proposal to add given address to this type.", metavar="<type>")
    add_parser.add_argument("-a", required=True, type=str, help="Address to be added.", metavar="<addr>")

    # remove subcmd
    remove_parser = subparsers.add_parser("remove", help="Makes proposal to remove given address from specified list.")
    remove_parser.add_argument("-t", required=True, choices=["maintainer", "observer", "governor", "blacklist", "banker"], type=str, help="Make proposal to remove address to this type.", metavar="<type>")
    remove_parser.add_argument("-a", required=True, type=str, help="Address to be removed.", metavar="<addr>")

    # is subcmd
    is_parser = subparsers.add_parser("is", help="Checks if given address is of given type.")
    is_parser.add_argument("-t", required=True, choices=["maintainer", "observer", "governor", "blacklist", "banker"], type=str, help="Query if address is of this type.", metavar="<type>")
    is_parser.add_argument("-a", required=True, type=str, help="Address to be queried.", metavar="<addr>")

    # vote subcmd
    vote_parser = subparsers.add_parser("vote", help="Votes for given proposal id.")
    vote_parser.add_argument("-i", type=int, help="Proposal ID to vote for.", required=True, metavar="<id>")

    return parser

def main():
    args = arg_parser().parse_args()
    if "a" in vars(args).keys():
        try:
            args.a = Web3.toChecksumAddress(args.a)
        except:
            print("Invalid address format")
            sys.exit(1)

    contract = Governing(args.info, args.node_info, args.ipc)

    # check which subcmd was used and act accordingly
    if args.cmd == "add":
        print(">", contract.call("add", args.t, args.a))
    elif args.cmd == "remove":
        print(">", contract.call("remove", args.t, args.a))
    elif args.cmd == "is":
        print(">", contract.call("is", args.t, args.a))
    elif args.cmd == "vote":
        print(">", contract.call("vote", args.i))

if __name__ == "__main__":
    main()
