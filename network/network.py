#!/usr/bin/python3

import os
import sys
import subprocess
import shutil
import yaml
import json

# UTILS
class color:
    """Colors used for terminal printing."""
    INFO = "\033[94m"
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    STOP = "\033[0m"


def print_info(infostr):
    print(f"{color.INFO}{color.BOLD}[INFO]{color.STOP}\t{infostr}")

def print_progress(progstr):
    print("\t-->", progstr)

def print_err(errstr):
    print(f"{color.ERR}{color.BOLD}[ERROR]{color.STOP}\t{errstr}")
    print(f"\nLogs can be found at '{LOG_FILE}'")
    sys.exit(1)

def log(process):
    with open(LOG_FILE, "a") as f:
        f.write(process.stdout)
        f.write(process.stderr)

def print_help():
    print(f"Usage like:\n\t{sys.argv[0]} [COMMAND] [FLAGS]")
    print("\nCOMMAND")
    print("  prepare\tMakes 'quorum' and 'istanbul-tools' dependencies.")
    print("  init\t\tInitializes network from config file.")
    print("  up\t\tBoots up all network nodes.")
    print("  down\t\tShuts down all network nodes.")
    print("  clean\t\tDeletes network directory and cleans up afterwards.")
    print(f"\n For more info on commands use:\n\t{sys.argv[0]} [COMMAND] --help")

# SUBCOMMAND FUNCTIONS
def prepare():
    """Makes network dependencies such as quorum and istanbul-tools"""
    print_info("Preparing network")
    dependencies = {
            "quorum": "make all",
            "istanbul-tools": "make"
        }

    for dep, makecmd in dependencies.items():
        print_progress(f"making dependency '{dep}'")
        try:
            os.chdir(dep)
            process = subprocess.run(makecmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, universal_newlines=True)
            log(process)
            os.chdir("..")
        except:
            print_err(f"Could not make dependency '{dep}'.\nHave you run\n\tgit submodule init\n\tgit submodule update")

def init():
    """Initializes network from local init.yaml file"""
    print_info("initializing network")
    
    network = read_network_yaml()
    network_dir = create_file_structure(network)
    genesis_file, static_nodes_file, lead_val_dir = validator_setup(network, network_dir)
    edit_static_nodes(network, static_nodes_file)
    addrs = gen_accounts(network, network_dir)
    config_genesis(network, network_dir, genesis_file, addrs)
    distrib_network_files(network, network_dir, genesis_file, static_nodes_file, lead_val_dir)

def read_network_yaml():
    try:
        with open(NETWORK_FILE) as f:
            network = yaml.full_load(f)["network"]
    except:
        print_err(f"Could not read network initialization file '{NETWORK_FILE}'.")

    return network

def create_file_structure(network):
    print_progress("Generating network file structure")
    try:
        network_dir = os.path.join(WORK_DIR, network["name"])
        os.mkdir(network_dir)

        # creating org dirs
        for org in network["orgs"]:
            org_dir = os.path.join(network_dir, org)
            os.mkdir(org_dir)

            # creating validator dirs for org
            for val_name, val in network["validators"].items():
                if val["org"] == org:
                    val_path = os.path.join(org_dir, "validators")
                    if not os.path.exists(val_path):
                        os.mkdir(val_path)
                    os.makedirs(os.path.join(val_path, val_name, "data", "geth"), exist_ok=True)

            # TODO: creating other nodes dirs

        return network_dir

    except:
        print_err(f"Could not create network file structure. If this is not the first time setting up a network with this name, please clean the old one first by using\n\n\t{sys.argv[0]} clean")

def validator_setup(network, network_dir):
    print_progress("Setting up validator nodes")
    vals = list(network["validators"].keys())
    lead_val_name = vals[0]
    lead_val = network["validators"][lead_val_name]

    lead_val_dir = os.path.join(network_dir, lead_val["org"], "validators", lead_val_name)
    os.chdir(lead_val_dir)

    try:
        cmd = f"../../../../istanbul-tools/build/bin/istanbul setup --num {len(vals)} --nodes --quorum --save --verbose"
        process = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, universal_newlines=True)
        log(process)
    except:
        print_err(f"Could not setup validators.")

    static_nodes_json = os.path.join(lead_val_dir, "static-nodes.json")
    genesis_file = os.path.join(lead_val_dir, "genesis.json")
    os.chdir(WORK_DIR)

    return genesis_file, static_nodes_json, lead_val_dir

def edit_static_nodes(network, static_nodes_path):
    # open generated static-nodes.json
    with open(static_nodes_path) as f:
        static_nodes = json.load(f)

    # edit static nodes
    val_names = list(network["validators"].keys())
    edited_enodes = []
    for i, enode in enumerate(static_nodes):
        ip = network["validators"][val_names[i]]["ip"]
        port = network["validators"][val_names[i]]["port"]
        
        enode = enode.replace("@0.0.0.0:", f"@{ip}:")
        enode = enode.replace(":30303?", f":{port}?")
        edited_enodes.append(enode)

    # dumping new enodes to file
    with open(static_nodes_path, 'w') as f:
        json.dump(edited_enodes, f, indent=4, separators=(",", ":"))

def gen_accounts(network, network_dir):
    print_progress("Generating accounts")

    addrs = {}

    # generate validator accounts
    for val_name, val in network["validators"].items():
        val_dir = os.path.join(network_dir, val["org"], "validators", val_name)

        data_dir = os.path.join(val_dir, "data")
        addrs[val_name] = gen_geth_account(data_dir, val["passphrase"])

    # TODO: generate other accounts
    ###

    # save addresses of initial accounts
    addr_file = os.path.join(network_dir, "addresses.json")
    with open(addr_file, "w") as f:
        json.dump(addrs, f, indent=4, separators=(",", ":"))

    return addrs
        
def gen_geth_account(data_dir, passphrase):
    try:
        # create process to inpu to geth
        cmd = f"geth --datadir {data_dir} account new"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        inbytes = bytes(f"{passphrase}\n{passphrase}\n".encode("utf-8"))
        process.stdin.write(inbytes)
        out = process.communicate()[0].decode("utf-8")
        process.stdin.close()

        # get created address from output
        addr = None
        for literal in out.split():
            if literal.startswith("0x"):
                addr = literal
                break

        return addr
    except:
        print_err(f"Could not create geth account for data directory '{data_dir}'")

def config_genesis(network, network_dir, genesis_file, addrs):
    print_progress("Editing genesis block")

    # read in genesis block
    try:
        with open(genesis_file) as f:
            genesis = json.load(f)
            new_genesis = genesis.copy()

        # remove vanilla allocated stuff, since they are of no use
        new_genesis["alloc"] = {}
    except:
        print_err(f"Could not allocate funds, since provided genesis file '{genesis_file}' was not found.")
    
    # pre allocating funds
    new_genesis = pre_alloc_funds(network, new_genesis, addrs)

    # TODO: configure istanbul epochs etc.

    # TODO: configure network ID

    # TODO: pre-allocate contracts

    # TODO: configure limit on tx size

    # write newly configured genesis block
    with open(genesis_file, "w") as f:
        json.dump(new_genesis, f, indent=4, separators=(",", ":"))

def pre_alloc_funds(network, genesis_dict, addrs):
    print_progress("Pre-allocating funds")

    # validators
    for val_name, val in network["validators"].items():
        if "balance" in val.keys():
            addr = addrs[val_name]
            balance = str(int(val["balance"]))
            genesis_dict["alloc"][addr] = {"balance": balance}

    # TODO: pre allocate funds for other nodes

    return genesis_dict

def distrib_network_files(network, network_dir, genesis_file, static_nodes_file, lead_val_dir):
    print_progress("Distributing network files to every node")
    # validator nodes
    for i, tpl in enumerate(network["validators"].items()):
        val_name, val = tpl
        val_dir = os.path.join(network_dir, val["org"], "validators", val_name)

        # do not copy genesis in lead validator dir, it is already there
        if i != 0:
            shutil.copyfile(genesis_file, os.path.join(val_dir, "genesis.json"))

        shutil.copyfile(static_nodes_file, os.path.join(val_dir, "data", "static-nodes.json"))

        nodekey_file = os.path.join(lead_val_dir, str(i), "nodekey")
        shutil.copyfile(nodekey_file, os.path.join(val_dir, "data", "geth", "nodekey"))

    
    # TODO: Also distribute to other nodes

def clean():
    """Deletes network and cleans up directory afterwards."""
    network = read_network_yaml()
    try:
        awsr = input(f"Are you sure you want to delete the network '{network['name']}'?\n  y/[n] -> ")
        if awsr in ["y", "Y", "YES", "yes", "Yes"]:
            shutil.rmtree(network["name"])
        else:
            print("Aborting.")
    except:
        pass

# MAIN
def main():
    # PREPARATION
    try:
        os.mkdir(".tmp")
    except:
        shutil.rmtree(".tmp")
        os.mkdir(".tmp")

    # CONSTS
    global WORK_DIR
    global LOG_FILE
    global NETWORK_FILE
    WORK_DIR = os.getcwd()
    LOG_FILE = os.path.join(WORK_DIR, ".tmp", "logs.txt")
    NETWORK_FILE = os.path.join(WORK_DIR, "network.yaml")

    # FUNCTIONALITY
    parse_args()

    # CLEAN UP
    shutil.rmtree(".tmp")

def parse_args():
    """Parses system args"""
    args = sys.argv

    # check if command was given
    if len(args) == 1:
        print_help()
        sys.exit(1)
    else:
        subcmd = args[1]

    flags = []
    for flag in args:
        if flag in ["--help", "-h"]:
            print_help()
            sys.exit(0)

    # check for subcommand
    if subcmd == "prepare":
        prepare()
    elif subcmd == "init":
        init()
    elif subcmd == "up":
        up()
    elif subcmd == "down":
        down()
    elif subcmd == "clean":
        clean()
    else:
        print_err(f"Unknown subcommand: {subcmd}.")


if __name__ == "__main__":
    main()
