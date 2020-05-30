#!/usr/bin/python3

import os
import sys
import subprocess
import signal
import shutil
import yaml
import json
import abc
import time

# UTILS
class color:
    """Colors used for terminal printing."""
    INFO = "\033[94m"
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    STATUS = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    STOP = "\033[0m"

class Command():
    """Defines an abstract skeleton class for Subcommands used."""
    __metaclass__ = abc.ABCMeta
    WORKDIR = os.getcwd()
    LOGFILE = os.path.join(WORKDIR, ".tmp", "logs.txt")
    CONF_FILE = "network.yaml"

    # Binary directories
    ISTANBUL_BIN = os.path.join(WORKDIR, "istanbul-tools", "build", "bin")
    QUORUM_BIN = os.path.join(WORKDIR, "quorum", "build", "bin")

    COMMANDS = ["prepare", "init", "up", "down", "clean", "help"]

    COMMANDS_HELP = {
        "prepare": "Makes 'quorum' and 'istanbul-tools' dependencies.",
        "init": "Initializes network from config file.",
        "up": "Boots up all network nodes.",
        "down": "Shuts down all network nodes.",
        "clean": "Deletes network directory and cleans up afterwards."
    }

    @classmethod
    def call(cls):
        """Implements functionality on class call."""

    @classmethod
    def handle_flags(cls, args):
        """Defines the default on how to handle command flags."""
        for arg in args:
            if arg in ["-h", "--help"]:
                cls.print_help()
                sys.exit(0)

    @classmethod
    def parse_args(cls):
        """"Parses command line arguments and defines subcommand with subcommand arguments"""
        args = sys.argv
        if len(args) == 1:
            cls.print_help()
            sys.exit(1)

        subcmd = args[1]

        # check if valid subcmd
        if subcmd not in cls.COMMANDS:
            errstr = f"Unknown subcommand {subcmd}.\n"
            cls.handle_err(None, errstr)

        # parses flags
        subcmd_args = []
        if len(args) > 2:
            subcmd_args =  args[2:]

        return subcmd, subcmd_args

    @classmethod
    def print_help(cls):
        """Prints command help to stdout."""
        helpstr = (
                "Usage like:\n"
                f"    {sys.argv[0]} COMMAND [FLAGS]\n"
                "\n"
                "COMMAND")

        for cmd, desc in cls.COMMANDS_HELP.items():
            if cmd == "up":
                helpstr += f"\n    {cmd}\t\t{desc}"
            else:
                helpstr += f"\n    {cmd}\t{desc}"

        helpstr += ("\n\nFor more info on commands use:\n"
                    f"    {sys.argv[0]} COMMAND --help"
        )

        print(helpstr)

    @classmethod
    def print_info(cls, infostr):
        """Prints progress to stdout."""
        print(f"{color.INFO}{color.BOLD}[INFO]{color.STOP}\t{infostr}")

    @classmethod
    def handle_err(cls, err, errstr):
        """Handles error by exiting programm and writing to stderr."""
        outerr = f"\n{color.ERR}{color.BOLD}[ERROR]{color.STOP}\t{errstr}\n"
        print(outerr, file=sys.stderr)

        # wirte to logs
        with open(cls.LOGFILE, "a") as logs:
            if err is None:
                err = ""
            logs.write(outerr + "\nPYTHON_ERROR: " + str(err) + "\n")

        print(f"Logs can be found at '{cls.LOGFILE}'")
        print(f"\nUse '{sys.argv[0]} help' for help")
        sys.exit(1)

    @classmethod
    def print_progress(cls, progrstr, end="\r"):
        """Prints progress to terminal and provides a way to easily update outputstring on completion"""
        if progrstr == "ok":
            print(f"{color.OK}{color.BOLD}[OK]{color.STOP}  ", end="\n")
        elif progrstr == "stop":
            print(f"{color.WARN}{color.BOLD}[STOP]{color.STOP}")
        else:
            print(f"{color.INFO}{color.BOLD}[INFO]{color.STOP}\t{progrstr}", end=end)

class Prepare(Command):
    """Makes network dependencies such as quorum and istanbul-tools."""
    DEPENDENCIES = {
            "quorum": "make all",
            "istanbul-tools": "make"
        }

    @classmethod
    def call(cls, flgs):
        cls.handle_flags(flgs)

        for dep, makecmd in cls.DEPENDENCIES.items():
            cls.print_progress(f"Making dependency '{dep}'.")
            try:
                os.chdir(dep)
                process = subprocess.run(makecmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, universal_newlines=True)
                os.chdir("..")
            except Exception as err:
                errstr = f"Could not make dependency '{dep}'."

                cls.handle_err(err, errstr)

            cls.print_progress("ok")

    @classmethod
    def print_help(cls):
        helpstr = (
                "Usage like:\n"
                f"    {sys.argv[0]} prepare\n"
                "\n"
                "Please make sure that the following repos exist in the current working directory:\n"
        )

        for repo, _ in cls.DEPENDENCIES.items():
            helpstr += f"    - {repo}\n"

        helpstr += (
                "\nIf any repo does not exist, please call:"
                "    git submodule init\n"
                "    git submodule update\n"
        )
        print(helpstr)

class Clean(Command):
    """Shuts down all nodes, deletes network directory and cleans up afterwards"""
    FLAGS = {
        "config": Command.CONF_FILE
    }

    @classmethod
    def call(cls, flgs):
        cls.handle_flags(flgs)

        net = Network(cls.FLAGS["config"], cls.WORKDIR)

        # shutdown all running nodes before cleaning
        Down.call([cls.FLAGS["config"]])

        # delete network directory
        try:
            cls.print_progress("Cleaning Network.", end="\n")
            awsr = input(f"    Are you sure you want to delete the network '{net.name}'?\n    y/[n] -> ")
            if awsr.lower() in ["y", "yes", "yea"]:
                shutil.rmtree(net.name)
                cls.print_progress("Cleaning Network.")
                cls.print_progress("ok")
            else:
                cls.print_progress("Aborting.")
                cls.print_progress("stop")
        except:
            cls.print_progress(f"No such network '{net.name}'.", end="\n")

    @classmethod
    def handle_flags(cls, args):
        for arg in args:
            if arg in ["-h", "--help"]:
                cls.print_help()
                sys.exit(0)
            else:
                cls.FLAGS["config"] = arg

    @classmethod
    def print_help(cls):
        helpstr = (
            "Usage like:\n"
            f"    {sys.argv[0]} clean <CONF>\n"
            "\n"
            "DESC\n"
            "    Deletes network directory given from network config file.\n"
            "\n"
            "INPUT\n"
            f"    <CONF>\t{cls.CONF_FILE}\tThe network config file for the network that will be deleted."
        )

        print(helpstr)

class Init(Command):
    """Initializes network (espacially all nodes) from given network config file"""

    FLAGS = {
        "docker": True,
        "pass": False,
        "reset": False,
        "config": Command.CONF_FILE
    }

    @classmethod
    def handle_flags(cls, args):
        for arg in args:
            if arg in ["-h", "--help"]:
                cls.print_help()
                sys.exit(0)
            elif arg in ["--no-docker"]:
                cls.FLAGS["docker"] = False
            elif arg in ["--pass", "-p"]:
                cls.FLAGS["pass"] = True
            elif arg in ["--reset"]:
                cls.FLAGS["reset"] = True
            else:
                cls.FLAGS["config"] = arg

    @classmethod
    def call(cls, flgs):
        cls.handle_flags(flgs)

        if cls.FLAGS["reset"]:
            Clean.call([cls.FLAGS["config"]])

        net = Network(cls.FLAGS["config"], cls.WORKDIR)

        cls.gen_file_structure(net)
        genesis_file, static_nodes_file = cls.setup_validators(net)
        cls.edit_static_nodes(net, static_nodes_file)
        addrs = cls.gen_accounts(net)
        cls.config_genesis(net, genesis_file, addrs)
        cls.distrib_network_files(net, genesis_file, static_nodes_file)

        # TODO: Implement docker setup
        if cls.FLAGS["docker"]:
            pass
        else:
            cls.geth_init(net, cls.FLAGS["docker"])

    @classmethod
    def gen_file_structure(cls, net):
        cls.print_progress("Generating network file structure.")
        try:
            os.mkdir(net.dir)

            # creating node dirs
            for node in net.nodes:
                os.makedirs(os.path.join(node.dir, "data", "geth"), exist_ok=True)

            cls.print_progress("ok")

        except Exception as err:
            errstr = "Could not create network file structure. If this is not the first time setting up a network with this name, please clean the old one first by using\n\n\t{sys.argv[0]} clean"
            cls.handle_err(err, errstr)

    @classmethod
    def setup_validators(cls, net):
        cls.print_progress("Setting up validator nodes.")

        os.chdir(net.lead_val.dir)
        istanbul_bin = os.path.join(cls.ISTANBUL_BIN, "istanbul")
        try:
            cmd = f"{istanbul_bin} setup --num {len(net.vals)} --nodes --quorum --save --verbose"
            process = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, universal_newlines=True)
        except Exception as err:
            errstr = f"Could not setup validators. Issue with binary from '{istanbul_bin}'."
            cls.handle_err(err, errstr)

        static_nodes_file = os.path.join(net.lead_val.dir, "static-nodes.json")
        genesis_file = os.path.join(net.lead_val.dir, "genesis.json")
        os.chdir(cls.WORKDIR)

        cls.print_progress("ok")

        return genesis_file, static_nodes_file
    
    @classmethod
    def edit_static_nodes(cls, net, static_nodes_file):
        # open generated static-nodes.json
        cls.print_progress("Writing validator IPs and ports to static-nodes.json.")
        with open(static_nodes_file) as f:
            static_nodes = json.load(f)

        # edit static nodes
        edited_enodes = []
        for i, enode in enumerate(static_nodes):
            ip = net.vals[i].ip
            port = net.vals[i].port
            
            enode = enode.replace("@0.0.0.0:", f"@{ip}:")
            enode = enode.replace(":30303?", f":{port}?")
            edited_enodes.append(enode)

        # dumping new enodes to file
        with open(static_nodes_file, 'w') as f:
            json.dump(edited_enodes, f, indent=4, separators=(",", ":"))

        cls.print_progress("ok")

    @classmethod
    def gen_accounts(cls, net):
        cls.print_progress("Generating accounts.")

        addrs = {}
        for node in net.nodes:
            data_dir = os.path.join(node.dir, "data")

            if cls.FLAGS["pass"]:
                addrs[node.name] = cls.gen_geth_account(data_dir, None)
            else:
                addrs[node.name] = cls.gen_geth_account(data_dir, passphrase=node.opt_dict["passphrase"])

            # save nodes addr to node's addr file
            with open(node.addr_file, "w") as f:
                f.write(addrs[node.name])

        # save all addresses to network's addr file
        with open(net.addr_file, "w") as f:
            json.dump(addrs, f, indent=4, separators=(",", ":"))

        cls.print_progress("ok")

        return addrs

    @classmethod
    def gen_geth_account(cls, data_dir, passphrase):
        try:
            # create process to input to geth
            geth_bin = os.path.join(cls.QUORUM_BIN, "geth")
            cmd = f"{geth_bin} --datadir {data_dir} account new"
            if passphrase is None:
                passphrase = input(f"Passphrase for '{data_dir}':\n--> ")

            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            inbytes = bytes(f"{passphrase}\n{passphrase}\n".encode("utf-8"))
            stdout, stderr = process.communicate(inbytes)
            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")

            # get created address from output
            addr = None
            for literal in stdout.split():
                if literal.startswith("0x"):
                    addr = literal
                    break

            return addr
        except Exception as err:
            errstr = f"Could not create geth account for data directory '{data_dir}'"
            cls.handle_err(err, errstr)
    
    @classmethod
    def config_genesis(cls, net, genesis_file, addrs):
        cls.print_progress("Configuring genesis block.")

        # read in genesis block
        try:
            with open(genesis_file) as f:
                genesis = json.load(f)

            genesis["alloc"] = {}
        except Exception as err:
            errstr = f"Could not configure genesis block, since provided genesis file '{genesis_file}' was not found."
            cls.handle_err(err, errstr)
        
        # pre allocating funds
        genesis = cls.pre_alloc_funds(net, genesis, addrs)

        # TODO: configure istanbul epochs etc.

        # TODO: configure network ID

        # TODO: pre-allocate contracts

        # TODO: configure limit on tx size

        # write newly configured genesis block
        with open(genesis_file, "w") as f:
            json.dump(genesis, f, indent=4, separators=(",", ":"))
        cls.print_progress("ok")

    @classmethod
    def pre_alloc_funds(cls, net, genesis_dict, addrs):
        for node in net.nodes:
            if "balance" in node.opt_dict.keys():
                addr = addrs[node.name]
                balance = str(int(node.opt_dict["balance"]))
                genesis_dict["alloc"][addr] = {"balance": balance}

        return genesis_dict

    @classmethod
    def distrib_network_files(cls, net, genesis_file, static_nodes_file):
        cls.print_progress("Distributing network files to every node.")

        # validator nodes
        for i, val in enumerate(net.vals):
            # do not copy genesis in lead validator dir, it is already there
            if i != 0:
                shutil.copyfile(genesis_file, os.path.join(val.dir, "genesis.json"))

            shutil.copyfile(static_nodes_file, os.path.join(val.dir, "data", "static-nodes.json"))

            nodekey_file = os.path.join(net.lead_val.dir, str(i), "nodekey")
            shutil.copyfile(nodekey_file, os.path.join(val.dir, "data", "geth", "nodekey"))

        # TODO: Also distribute to other nodes

        cls.print_progress("ok")

    @classmethod
    def geth_init(cls, net, docker):
        """Calls 'geth init' on all nodes to complete initialization process."""
        cls.print_progress(f"Calling 'geth init' on all nodes. DOCKER={docker}")

        for node in net.nodes:
            node.geth_init(docker)

        cls.print_progress("ok")

    @classmethod
    def print_help(cls):
        helpstr = (
            "Usage like:\n"
            f"    {sys.argv[0]} init [FLAGS] <CONF>\n"
            "\n"
            "DESC\n"
            "    Initializes network fragments (e.g. nodes, smart contracts, etc.) from given network config file <CONF>. By default, nodes are initialized in docker containers (turn of with '--no-docker').\n" 
            "\n"
            "FLAGS\n"
            "   --no-docker\tDoes not initialize nodes in docker. This is normally used for development and testing.\n"
            "    --pass, -p\tInitializes nodes and asks for passphrases when creating accounts via geth. Passphrases have then to be typed in by hand. Not recommended for many nodes.\n"
            "    --reset\tDeletes network and rebuilds it from network config file.\n"
            "\n"
            "INPUT\n"
            f"    <CONF>\t{cls.CONF_FILE}\tThe network config file used to initialize the network fragments with."
        )

        print(helpstr)

class Up(Command):
    """Boots up all nodes configured in network config file."""
    FLAGS = {
        "docker": True,
        "config": Command.CONF_FILE
    }

    @classmethod
    def handle_flags(cls, args):
        for arg in args:
            if arg in ["-h", "--help"]:
                cls.print_help()
                sys.exit(0)
            elif arg in ["--no-docker"]:
                cls.FLAGS["docker"] = False
            else:
                cls.FLAGS["config"] = arg

    @classmethod
    def call(cls, flgs):
        cls.handle_flags(flgs)

        net = Network(cls.FLAGS["config"], cls.WORKDIR)

        # check if nodes are already running
        for node in net.nodes:
            if node.is_running():
                errstr = f"Node '{node.name}' is already running. Please shut it down, before trying to boot it up."
                cls.handle_err(None, errstr)

        # booting up nodes
        for node in net.nodes:
            node.up(cls.FLAGS["docker"])

        # show booted nodes
        for node in net.nodes:
            node.print_status()

    @classmethod
    def print_help(cls):
        helpstr = (
            "Usage like:\n"
            f"    {sys.argv[0]} up [FLAGS] <CONF>\n"
            "\n"
            "DESC\n"
            "    Boots up all network nodes specified in <CONF>. By default, nodes are booted in docker containers (turn of with '--no-docker').\n" 
            "\n"
            "FLAGS\n"
            "   --no-docker\tDoes not boot nodes as docker containers. This is normally used for development and testing.\n"
            "\n"
            "INPUT\n"
            f"    <CONF>\t{cls.CONF_FILE}\tThe network config file used to initialize the network."
        )

        print(helpstr)

class Down(Command):
    """Shuts down all nodes in network from given network config file."""
    FLAGS = {
        "docker": True,
        "config": Command.CONF_FILE
    }

    @classmethod
    def handle_flags(cls, args):
        for arg in args:
            if arg in ["-h", "--help"]:
                cls.print_help()
                sys.exit(0)
            else:
                cls.FLAGS["config"] = arg

    @classmethod
    def call(cls, flgs):
        cls.handle_flags(flgs)

        net = Network(cls.FLAGS["config"], cls.WORKDIR)

        # shut down all running nodes
        for node in net.nodes:
            if node.is_running():
                try:
                    # killing process
                    cls.print_progress(f"Shutting down node '{node.name}' with PID: {node.pid}.")
                    os.kill(int(node.pid), signal.SIGTERM)
                    cls.print_progress("ok")

                    # clean up PID file
                    cls.print_progress("Cleaning up.")
                    if os.path.isfile(node.pid_file):
                        os.remove(node.pid_file)
                    cls.print_progress("ok")
                except Exception as err:
                    errstr = (
                            f"Could not shut down node '{node.name}' with PID: {node.pid}\n"
                        "Check if it is still running by calling 'ps -l'. If so, please terminate it manually by calling 'kill -SIGTERM <PID>'."
                    )
                    cls.handle_err(err, errstr)

    @classmethod
    def print_help(cls):
        helpstr = (
            "Usage like:\n"
            f"    {sys.argv[0]} down [FLAGS] <CONF>\n"
            "\n"
            "DESC\n"
            "    Shuts down all network nodes specified in <CONF>.\n" 
            "\n"
            "INPUT\n"
            f"    <CONF>\t{cls.CONF_FILE}\tThe network config file used to initialize the network."
        )

        print(helpstr)

# HELPER OBJECT CLASSES
class Network(object):
    """Represents a network config .yaml file as an object and builds functionality and class definitions on top of it."""

    MANDATORY_KEYS = ["id", "name", "orgs", "validators"]
    # TODO: define optional keys such as contracts, observers, etc.
    OPTIONAL_KEYS = []

    def __init__(self, conf_file, work_dir):
        Command.print_progress(f"Reading network config file: '{conf_file}'.")
        # read in .yaml into dict
        self.conf_file = conf_file
        try:
            with open(conf_file) as f:
                self.dict = yaml.full_load(f)["network"]
        except Exception as err:
            errstr = f"Could not read network config file '{conf_file}'."
            Command.handle_err(err, errstr)

        # check if mandatory keys were in config file
        for key in self.MANDATORY_KEYS:
            if key not in self.dict.keys():
                errstr = f"Error while reading '{conf_file}'. Mandatory key '{key}' missing. Please provide it."
                Command.handle_err(None, errstr)

        # TODO: Read in optional keys like in Nodes class

        # get network dir from name
        self.dir = os.path.join(work_dir, self.dict["name"])
        self.addr_file = os.path.join(self.dir, "addresses.json")
        self.name = self.dict["name"]

        self.id = self.dict["id"]

        self.orgs = self.dict["orgs"]
        if self.orgs is None:
            errstr = f"Error while reading '{conf_file}'. There must be at least one organization."
            Command.handle_err(None, errstr)

        # build node objects
        self.nodes = []

        # validators
        self.vals = self.create_nodes("validators")
        self.lead_val = self.vals[0]
        self.nodes.extend(self.vals)

        # TODO: Build objects for other node types

        Command.print_progress(f"ok")

    def create_nodes(self, typ):
        """Creates node objects of given type from given dict"""
        nodes = []
        for node_name, node_dict in self.dict[typ].items():
            node = Node(node_name, node_dict, typ, self)
            # check if node's org is in self.orgs to not allow orphan nodes
            if node.org not in self.orgs:
                errstr = f"Organization '{node.org}' for node '{node_name}' of type '{typ}' not in network's 'orgs' list."
                Command.handle_err(None, errstr)

            nodes.append(node)

        return nodes

class Node(object):
    """Represents a network node as an object."""
    MANDATORY_KEYS = ["org", "ip", "port", "rpc-port"]
    OPTIONAL_KEYS = ["docker-ip", "docker-port", "docker-rpc-port", "passphrase", "balance"]
    MANDATORY_FILES = ["genesis.json", os.path.join("data", "static-nodes.json"), os.path.join("data", "geth", "nodekey")]
    NODE_TYPES = ["validators", "observers", "governers", "maintainers", "bankers"]

    def __init__(self, name, node_dict, typ, net):
        self.name = name
        self.net = net
        self.dict = node_dict
        self.type = typ

        # check if mandatory keys were in config file
        for key in self.MANDATORY_KEYS:
            if key not in node_dict.keys():
                errstr = f"Mandatory key '{key}' for node '{self.name}' of type '{self.type}' missing. Please provide it."
                Command.handle_err(None, errstr)

        # mandatory keys
        self.ip = node_dict["ip"]
        self.port = node_dict["port"]
        self.rpc_port = node_dict["rpc-port"]
        self.org = self.dict["org"]

        # define node dir
        self.dir = os.path.join(self.net.dir, self.org, self.type, self.name)
        self.logs = os.path.join(self.dir, "node.log")
        self.pid_file = os.path.join(self.dir, "PID")
        self.addr_file = os.path.join(self.dir, "ADDR")

        # read in optional keys as a dict
        self.opt_dict = {}
        for key in self.OPTIONAL_KEYS:
            if key in node_dict.keys():
                self.opt_dict[key] = node_dict[key]

    def is_init(self):
        """Checks if node was initialized by checking if its mandatory files exist. If not writes an error."""
        for f in Node.MANDATORY_FILES:
            f = os.path.join(self.dir, f)
            if not os.path.isfile(f):
                errstr = f"Node '{node.name}' has not been initialized properly. If you have not done already, call '{sys.argv[0]} init'."
                Command.handle_err(None, errstr)

        return True

    def geth_init(self, docker):
        """Calls 'geth init' for node."""
        # TODO: Implement docker 'geth init'
        if docker:
            pass
        else:
            os.chdir(self.dir)
            try:
                geth_bin = os.path.join(Command.QUORUM_BIN, "geth")
                cmd = f"{geth_bin} --datadir data init genesis.json"
                process = subprocess.run(cmd.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception as err:
                errstr = f"Could not call 'geth init' for node '{self.name}'."
                Command.handle_err(err, errstr)
        
        os.chdir(Command.WORKDIR)

    def up(self, docker):
        """Boots up node."""
        Command.print_progress(f"Trying to boot up node '{self.name}'.", end="\n")
        Command.print_progress(f"Checking if it was initialized properly.")
        self.is_init()
        Command.print_progress("ok")

        Command.print_progress(f"Booting up.")
        if docker:
            # TODO: Implement docker boot up
            pass
        else:
            os.chdir(self.dir)
            try:
                # TODO: What is istanbul.blockperiod?
                geth_bin = os.path.join(Command.QUORUM_BIN, "geth")
                cmd = f"nohup {geth_bin} --datadir data --nodiscover --istanbul.blockperiod 5 --syncmode full --mine --minerthreads 1 --verbosity 5 --networkid {self.net.id} --rpc --rpcaddr 0.0.0.0 --rpcport {self.rpc_port} --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,istanbul --emitcheckpoints --port {self.port}"
                envs = os.environ.copy()
                envs["PRIVATE_CONFIG"] = "ignore"
                with open(self.logs, "w") as logs:
                    process = subprocess.Popen(cmd.split(), env=envs, stdout=logs, stderr=logs)

                # write PID to file to check if a node is running later
                self.write_pid(process.pid)

            except Exception as err:
                errstr = f"Could not start a 'geth' process for node '{self.name}'."
                Command.handle_err(err, errstr)
            
            os.chdir(Command.WORKDIR)

        Command.print_progress("ok")

    def write_pid(self, pid):
        """Writes PID from self.up() to a file, so one can distinguish it later"""
        with open(self.pid_file, "w") as f:
            f.write(str(pid))

    @property
    def pid(self):
        """Reads from self.pid_file and returns content if it exists"""
        if os.path.isfile(self.pid_file):
            with open(self.pid_file) as f:
                pid = f.read()
                return pid
        else:
            return None

    @property
    def addr(self):
        """Reads node's address from self.addr_file and returns it on success"""
        if os.path.isfile(self.addr_file):
            with open(self.addr_file) as f:
                addr = f.read()
                return addr
        else:
            return None

    def is_running(self):
        """Calls self.pid and checks if it exists and if it is a running process"""
        pid = self.pid
        if pid is None:
            return False
        else:
            try:
                os.kill(int(pid), 0)
            except OSError:
                return False
            else:
                return True

    @property
    def status(self):
        """Gets status of node: {plain, init, run}."""
        if not self.is_init():
            # plain means that node is not even initialized
            return "plain"
        else:
            if not self.is_running():
                return "init"
            else:
                runstr = ()
                return "run"

        # TODO: Check if this happens
        return "unidentified"

    def print_status(self):
        """Prints the status in consistent manner to stdout."""
        status = self.status
        statusstr = f"{color.STATUS}{color.BOLD}[STAT]{color.STOP}\t'{self.name}'\n"
        if status == "plain":
            statusstr += "    - not initialized"
        elif status == "init":
            statusstr += f"    - initialized with address:\n      {self.addr}\n"
        elif status == "run":
            statusstr += (
                f"    - initialized with address:\n      {self.addr}\n"
                f"    - running with PID: {self.pid} on port {self.port}\n"
            )

        print(statusstr)


# MAIN
def main():
    # PREPARATION
    try:
        os.mkdir(".tmp")
    except:
        shutil.rmtree(".tmp")
        os.mkdir(".tmp")

    # FUNCTIONALITY VIA CLASS STRUCTURE
    subcmd, args = Command.parse_args()
    
    if subcmd == "help":
        Command.print_help()
    elif subcmd == "prepare":
        Prepare.call(args)
    elif subcmd == "init":
        Init.call(args)
    elif subcmd == "up":
        Up.call(args)
    elif subcmd == "down":
        Down.call(args)
    elif subcmd == "clean":
        Clean.call(args)
    else:
        Command.handle_err(None, f"Unknown subcommand: {subcmd}.")

    # CLEAN UP
    shutil.rmtree(".tmp")

if __name__ == "__main__":
    main()

