#!/usr/bin/env python3

import os
import sys
import subprocess
import signal
import shutil
import pathlib
import yaml
import json
import time
import traceback

import web3
from web3 import Web3

# UTILS
class Deco():
    """Colors used for terminal printing."""
    INFO = "\033[94m\033[1m"
    OK = "\033[92m\033[1m"
    ERR = "\033[91m\033[1m"
    WARN = "\033[91m\033[1m"
    STATUS = "\033[96m\033[1m"

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

class Shell():
    """Represents a simpel shell environment to call commands."""
    @classmethod
    def call(cls, cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=None, invis=False, check_ret=False):
        """Calls a shell command and handles return value."""
        process = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr, stdin=subprocess.PIPE, env=env)

        # check if process should terminate or runs invisibly in background and act accordingly
        if not invis and stdin is None:
            stdout, stderr = process.communicate()
            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")
            process.wait()
            
            if check_ret and process.returncode != 0:
                raise ShellCommandErr(f"Command '{cmd}' has terminated with non-zero error code '{process.returncode}' and message:\n\t{stderr}")
            
            return stdout
        elif not invis and stdin is not None:
            inbytes = bytes(stdin.encode("utf-8"))
            stdout, stderr = process.communicate(inbytes)
            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")
            process.wait()
            
            if check_ret and process.returncode != 0:
                raise ShellCommandErr(f"Command '{cmd}' has terminated with non-zero error code '{process.returncode}' and message:\n\t{stderr}")
            
            return stdout

# ERRORS
class InvalidFlagErr(Exception):
    pass

class ConfigFileNotFoundErr(FileNotFoundError):
    pass

class MandatoryKeyMissingErr(Exception):
    pass

class ShellCommandErr(Exception):
    pass

class NetworkDirExistsErr(FileExistsError):
    pass

class NodeDirCreationErr(Exception):
    pass

class NetworkDirDoesNotExistErr(FileNotFoundError):
    pass

class GenesisBlockErr(Exception):
    pass
 
class StaticNodesErr(Exception):
    pass

class ValidatorNotSetupErr(Exception):
    pass

class NodeNotInitErr(Exception):
    pass

class NodeAlreadyRunningErr(Exception):
    pass

class ContractDirCreationErr(Exception):
    pass

class ContractCompilationErr(Exception):
    pass

class BytecodeNotReadableErr(Exception):
    pass

class ByteCodeNotFoundErr(Exception):
    pass

class ReadingInfoFileErr(Exception):
    pass

class WritingInfoFileErr(Exception):
    pass

class MainAccountErr(Exception):
    pass

class NoMaintainerPresentErr(Exception):
    pass

class Web3ConnectionErr(Exception):
    pass

class AbiNotFoundErr(Exception):
    pass

class ObjNotSavableErr(Exception):
    pass

class GoverningContractNotDeployedErr(Exception):
    pass

# COMMAND
class Command():
    """Defines the working shell environment."""
    # directories
    WORKDIR = os.getcwd()
    TMPDIR = os.path.join(WORKDIR, ".tmp")

    # files
    LOGFILE = os.path.join(TMPDIR, "logs.txt")
    CONFFILE = os.path.join(WORKDIR, "network.yaml")

    # docker
    DOCKERDIR = os.path.join(WORKDIR, "docker")

    # consts
    NAME = sys.argv[0]
    FLAGS = {
        "help": False,
        "dev": False
    }

    @classmethod
    def parse_args(cls):
        """Defines an argument parser for the command and its subcommands."""
        # splitting up flags for subcommands
        subcmds = [sys.argv[0]]
        for subcls in cls.__subclasses__():
            subcmd = subcls.__name__.lower()
            subcmds.append(subcmd)

        args = {}
        for arg in sys.argv:
            if arg in subcmds:
                cmd = arg
                args[cmd] = []
            else:
                args[cmd].append(arg)

        return args

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["--help", "-h", "help"]:
                cls.FLAGS["help"] = True
            elif flg in ["-d", "--dev"]:
                cls.FLAGS["dev"] = True
            else:
                raise InvalidFlagErr(f"Flag '{flg}' does not exist.")

        return cls.FLAGS
    
    @classmethod
    def helpstr(cls):
        """Defines the help string printed to console."""
        usage = f"Usage like:\n\t{cls.NAME} COMMAND [FLAGS] <config-file>\n"
        # automatically fetch subcmd help strings
        cmds = "Commands\n"
        for subcls in cls.__subclasses__():
            cmds += f"\t{subcls.__name__.lower()}\t{subcls.HELP}\n"
        cmds += "\n"
        epilog = f"For more info on commands use:\n\t{cls.NAME} COMMAND --help\n"
        
        helpstr = usage + "\n" + cmds + "\n" + epilog + "\n"

        return helpstr

    @classmethod
    def handle_err(cls, err):
        """Logs and prints a given error to stderr."""
        cls.log(f"[ERROR]\t{err}")
        print(f"{Deco.ERR}[ERROR]{Deco.RESET}\t{err}", file=sys.stderr)

        if Command.FLAGS["dev"]:
            print(f"\n{Deco.WARN}[PYTHON-ERROR]{Deco.RESET}")
            traceback.print_exc()

        return 1

    @classmethod
    def print_progress(cls, string, function, *args, **kwargs):
        """Prints an updatable progress string to stdout."""
        print(f"{Deco.INFO}[INFO]{Deco.RESET}\t{string}", end="\r")
        cls.log(f"[INFO]\t{string}")
        ret = function(*args, **kwargs)
        print(f"{Deco.OK}[OK]{Deco.RESET}  ")

        return ret

    @classmethod
    def log(cls, msg):
        """Logs a given string."""
        with open(cls.LOGFILE, "a") as logs:
            logs.write(msg)

    @classmethod
    def pre_exec(cls):
        """Function called before any real command execution."""
        # create .tmp directory
        if os.path.exists(cls.TMPDIR):
            shutil.rmtree(cls.TMPDIR)
        os.mkdir(cls.TMPDIR)

        # check if docker is enabled
        try:
            cmd = "docker network ls"
            Shell.call(cmd, check_ret=True)
        except ShellCommandErr as err:
            return cls.handle_err(err)

        return 0

    @classmethod
    def post_exec(cls, ret):
        """Function called after command execution."""
        if ret != 0:
            # remove .tmp direcotry
            if os.path.exists(cls.TMPDIR):
                shutil.rmtree(cls.TMPDIR)
    
    @classmethod
    def call(cls):
        """Execution wrapper."""
        ret = cls.pre_exec()
        if ret != 0:
            return ret

        ret = cls.exec()

        cls.post_exec(ret)

        return ret

    @classmethod
    def exec(cls):
        """Execution of the given subcommand."""
        args = cls.parse_args()
        try:
            flgs = cls.parse_flags(args[sys.argv[0]])
        except InvalidFlagErr as err:
            return cls.handle_err(err)
        
        # check if only help wanted
        if flgs["help"]:
            print(cls.helpstr())
            return 0

        # read in config file
        try:
            conf_dict = cls.read_conf_file(cls.CONFFILE)
        except ConfigFileNotFoundErr as err:
            return cls.handle_err(err)

        # setting network object from config file
        try:
            net = Network(conf_dict["network"]["name"], conf_dict["network"], cls.WORKDIR)
        except Exception as err:
            return cls.handle_err(err)

        for cmd, flags in args.items():
            if cmd == "prepare":
                return Prepare.exec(net, flags=flags)
            elif cmd == "init":
                return Init.exec(net, flags=flags)
            elif cmd == "clean":
                return Clean.exec(net, flags=flags)
            elif cmd == "up":
                return Up.exec(net, flags=flags)
            elif cmd == "down":
                return Down.exec(net, flags=flags)
            elif cmd == "setup":
                return Setup.exec(net, flags=flags)

        return 1

    @classmethod
    def read_conf_file(cls, conf_file):
        """Reads in config file from given path."""
        # read in .yaml network config file
        try:
            with open(cls.CONFFILE) as f:
                conf_dict = yaml.full_load(f)
        except FileNotFoundError as err:
            raise ConfigFileNotFoundErr(f"Could not find config file at '{cls.conf_file}'.")

        return conf_dict

# SUBCOMMANDS
class Prepare(Command):
    """Subcommand that prepares the docker images and network."""
    HELP = "Builds needed docker images and creates new docker network."

    FLAGS = {
        "help": False
    }

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["help", "--help", "-h"]:
                cls.FLAGS["help"] = True
            else:
                raise InvalidFlagErr(f"Invalid flag '{flg}' for subcommand '{cls.__name__.lower()}'")

        return cls.FLAGS

    @classmethod
    def exec(cls, net, flags=[]):
        try:
            flgs = cls.parse_flags(flags)
        except InvalidFlagErr as err:
            return cls.handle_err(err)

        # check flags
        if flgs["help"]:
            print(cls.helpstr())
            return 0
        
        # prepare docker network
        try:
            cmd = f"docker network create -d {net.docker_settings.network_driver} --subnet {net.docker_settings.subnet} {net.name}"
            # progress wrapper for Shell.call to print output
            cls.print_progress(f"Creating docker network '{net.name}'.", Shell.call, cmd)
        except ShellCommandErr as err:
            return cls.handle_err(err)

        # build docker images
        docker_images = os.listdir(cls.DOCKERDIR)
        # TODO: make this less hacky
        docker_images.remove("quorum-node")
        docker_images.remove("README.md")
        docker_images.insert(0, "quorum-node")
        for img in docker_images:
            try:
                uid = os.getuid()
                dir = os.path.join(cls.DOCKERDIR, img)
                cmd = f"docker image build --build-arg UID={uid} --build-arg DOCKER_GETH_PORT={net.docker_settings.geth_port} --build-arg DOCKER_RPC_PORT={net.docker_settings.rpc_port} -t {img}:latest {dir}"
                cls.print_progress(f"Building docker image '{img}'.", Shell.call, cmd, check_ret=True)
            except Exception as err:
                return cls.handle_err(err)
            
        return 0

    @classmethod
    def helpstr(cls):
        cmd = cls.__name__.lower()
        usage = f"Usage like:\n\t{Command.NAME} {cmd} [FLAGS]\n"
        flgs = (
            "Flags\n"
            "\t-h, --help\tPrints help and exits.\n"
        )
        helpstr = usage + "\n" + cls.HELP + "\n" + "\n" + flgs + "\n"

        return helpstr

class Init(Command):
    """Initializes network from given config file. This means creating directory hierarchy and initializing validators and other node types."""

    HELP = "Initializes network, espacially nodes, from config file."
        
    FLAGS = {
        "reset": False,
        "help": False
    }

    @classmethod
    def helpstr(cls):
        cmd = cls.__name__.lower()
        usage = f"Usage like:\n\t{Command.NAME} {cmd} [FLAGS]\n"
        flgs = (
            "Flags\n"
            "\t-r, --reset\tCleans the network (directory) before initialization.\n"
            "\t-h, --help\tPrints help and exits.\n"
        )
        helpstr = usage + "\n" + cls.HELP + "\n" + "\n" + flgs + "\n"

        return helpstr

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["help", "--help", "-h"]:
                cls.FLAGS["help"] = True
            elif flg in ["--reset", "-r"]:
                cls.FLAGS["reset"] = True
            else:
                raise InvalidFlagErr(f"Invalid flag '{flg}' for subcommand '{cls.__name__.lower()}'")

        return cls.FLAGS

    @classmethod
    def exec(cls, net, flags=[]):
        try:
            flgs = cls.parse_flags(flags)
        except InvalidFlagErr as err:
            return cls.handle_err(err)

        # check flags
        if flgs["help"]:
            print(cls.helpstr())
            return 0
        if flgs["reset"]:
            Clean.exec(net)
        
        try:
            cls.print_progress("Generating file hierarchy.", cls.gen_dir_structure, net)
            cls.print_progress("Setting up IBFT validator nodes.", cls.setup_validators, net)
            cls.print_progress("Forming validator consortium.", cls.form_consortium, net)
            cls.print_progress("Creating geth accounts.", cls.create_accounts, net)
            cls.print_progress("Pre-allocating funds.", cls.pre_alloc_funds, net)
            cls.print_progress("Setting up non-validator nodes.", cls.setup_non_validators, net)
            cls.print_progress("Setting up node discovery.", cls.setup_static_nodes, net)
            cls.print_progress("Initializing geth on all nodes.", cls.geth_init, net)

        except Exception as err:
            return cls.handle_err(err)

    @classmethod
    def gen_dir_structure(cls, net):
        """Generates working directories for the nodes."""
        net.create_dir()
        for node in net.nodes:
            node.create_dir()

        for c in net.contracts:
            c.create_dir()

    @classmethod
    def setup_validators(cls, net):
        """Create istanbul bft compatible genesis block and according-static nodes file."""
        for val in net.validators:
            # calling 'istanbul setup ...' on validators
            val.setup()

    @classmethod
    def setup_non_validators(cls, net):
        """Copies genesis block from main validator to all other nodes."""
        val = net.validators[0]
        val_genesis = os.path.join(val.dir, "genesis.json")
        for node in net.nodes:
            if node.type != "validator":
                node.setup(val_genesis)

    @classmethod
    def form_consortium(cls, net):
        """Forms a constortium of validators at genesis block by adding all validators to each validator's genesis block."""
        for val in net.validators:
            val.form_consortium(net.validators)

    @classmethod
    def setup_validator_discovery(cls, net):
        """Edits all validators' 'static-nodes.json' to be able to discover each other at runtime."""
        for val in net.validators:
            val.create_static_nodes(net.validators)

    @classmethod
    def setup_static_nodes(cls, net):
        """Edits all nodes' 'static-nodes.json' to be able to discover each other at runtime."""
        static_nodes = [node.enode for node in net.nodes]
        for node in net.nodes:
            node.set_static_nodes(static_nodes)

    @classmethod
    def create_accounts(cls, net):
        """Creates geth accounts for all nodes that have specified one."""
        for node in net.nodes:
            node.create_accs()

    @classmethod
    def pre_alloc_funds(cls, net):
        """Checks if some node wants to have a pre-allocated balance and adds it then to all validators' genesis block."""
        for node in net.nodes:
            if node.accs is not None:
                for _, acc in node.accs.items():
                    if acc.balance is not None:
                        for val in net.validators:
                            # modifying validator's genesis
                            val.pre_alloc_funds(acc.addr, acc.balance)

    @classmethod
    def geth_init(cls, net):
        """Calling 'geth init ...' on all nodes."""
        for node in net.nodes:
            node.init()

    @classmethod
    def write_contracts_to_genesis(cls, net):
        """Adds all contracts specified in config file to genesis block."""
        for c in net.contracts:
            c.write_to_genesis(net.validators)

    @classmethod
    def compile_contracts(cls, net):
        """Compiles contracts into network directory, to be able to write the bytecode to genesis block later."""
        for c in net.contracts:
            c.compile(runtime=True)

class Clean(Command):
    """Shuts down all nodes, deletes the network directory and cleans up afterwards."""

    HELP = "Removes network directory and cleans up afterwards."

    FLAGS = {
        "help": False,
        "docker": False
    }

    @classmethod
    def helpstr(cls):
        cmd = cls.__name__.lower()
        usage = f"Usage like:\n\t{Command.NAME} {cmd} [FLAGS]\n"
        flgs = (
            "Flags\n"
            "\t--docker\tAlso removes created docker network and built images.\n"
            "\t-h, --help\tPrints help and exits.\n"
        )
        helpstr = usage + "\n" + cls.HELP + "\n" + "\n" + flgs + "\n"

        return helpstr

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["help", "--help", "-h"]:
                cls.FLAGS["help"] = True
            elif flg in ["--docker"]:
                cls.FLAGS["docker"] = True
            else:
                raise InvalidFlagErr(f"Invalid flag '{flg}' for subcommand '{cls.__name__.lower()}'")

        return cls.FLAGS

    @classmethod
    def exec(cls, net, flags=[]):
        try:
            flgs = cls.parse_flags(flags)
        except InvalidFlagErr as err:
            return cls.handle_err(err)

        # check flags
        if flgs["help"]:
            print(cls.helpstr())
            return 0

        # shutdown nodes before deleting
        Down.exec(net)
        
        # delete network directory
        try:
            cls.print_progress("Deleting network directory.", cls.delete_network_dir, net)
        except NetworkDirDoesNotExistErr as err:
            # only checking if network exists when docker flag is not given
            if not flgs["docker"]:
                return cls.handle_err(err)

        # delete docker network and images
        if flgs["docker"]:
            try:
                cls.print_progress(f"Deleting docker network '{net.name}'.", cls.delete_docker_network, net)
                cls.delete_docker_imgs(net)
            except Exception as err:
                return cls.handle_err(err)

    @classmethod
    def delete_network_dir(cls, net):
        try:
            shutil.rmtree(net.dir)
        except FileNotFoundError:
            raise NetworkDirDoesNotExistErr(f"No such network '{net.name}' with network directory '{net.dir}'.")
    
    @classmethod
    def delete_docker_imgs(cls, net):
        docker_images = os.listdir(cls.DOCKERDIR)
        docker_images.remove("README.md")
        for img in docker_images:
            cmd = f"docker image rm {img}"
            cls.print_progress(f"Deleting docker image '{img}'.", Shell.call, cmd, check_ret=True)

    @classmethod
    def delete_docker_network(cls, net):
        cmd = f"docker network rm {net.name}"
        Shell.call(cmd, check_ret=True)

class Up(Command):
    """Boots up all network nodes defined in config file. All nodes are booted in docker containers."""

    HELP = "Boots up all network nodes in docker containers."

    FLAGS = {
        "help": False,
    }

    @classmethod
    def helpstr(cls):
        cmd = cls.__name__.lower()
        usage = f"Usage like:\n\t{Command.NAME} {cmd} [FLAGS]\n"
        flgs = (
            "Flags\n"
            "\t-h, --help\tPrints help and exits.\n"
        )
        helpstr = usage + "\n" + cls.HELP + "\n" + "\n" + flgs + "\n"

        return helpstr

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["help", "--help", "-h"]:
                cls.FLAGS["help"] = True
            else:
                raise InvalidFlagErr(f"Invalid flag '{flg}' for subcommand '{cls.__name__.lower()}'")

        return cls.FLAGS

    @classmethod
    def exec(cls, net, flags=[]):
        try:
            flgs = cls.parse_flags(flags)
        except InvalidFlagErr as err:
            return cls.handle_err(err)

        # check flags
        if flgs["help"]:
            print(cls.helpstr())
            return 0
        
        try:
            cls.boot_up_nodes(net)
        except Exception as err:
            cls.handle_err(err)

        return 0

    @classmethod
    def boot_up_nodes(cls, net):
        """Boots up all given nodes in docker containers with node.name as container name."""
        for node in net.nodes:
            cls.print_progress(f"Booting up node '{node.name}'.", node.up, net)
        
        for node in net.nodes:
            node.print_status()

class Setup(Command):
    """Sets up the network when it is running. Builds and deploys smart contracts specified in config file."""

    HELP = "Sets up network state by compiling and deploying smart contracts."
        
    FLAGS = {
        "help": False
    }

    @classmethod
    def helpstr(cls):
        cmd = cls.__name__.lower()
        usage = f"Usage like:\n\t{Command.NAME} {cmd} [FLAGS]\n"
        flgs = (
            "Flags\n"
            "\t-h, --help\tPrints help and exits.\n"
        )
        helpstr = usage + "\n" + cls.HELP + "\n" + "\n" + flgs + "\n"

        return helpstr

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["help", "--help", "-h"]:
                cls.FLAGS["help"] = True
            else:
                raise InvalidFlagErr(f"Invalid flag '{flg}' for subcommand '{cls.__name__.lower()}'")

        return cls.FLAGS

    @classmethod
    def exec(cls, net, flags=[]):
        try:
            flgs = cls.parse_flags(flags)
        except InvalidFlagErr as err:
            return cls.handle_err(err)

        # check flags
        if flgs["help"]:
            print(cls.helpstr())
            return 0

        try:
            cls.compile_contracts(net)
            cls.deploy_contracts(net)
            cls.contract_setup(net)
            cls.print_progress("Copying contract info to nodes.", cls.copy_contract_info, net)
            # printing contract address to stdout
            for contract in net.contracts:
                contract.print_status()
        except Exception as err:
            cls.handle_err(err)

    @classmethod
    def compile_contracts(cls, net):
        """Compiles contracts given in network config file."""
        for c in net.contracts:
            cls.print_progress(f"Compiling contract '{c.name}'.", c.compile)

    @classmethod
    def deploy_contracts(cls, net):
        """Deploys contracts given in network config file to the network."""
        if net.maintainers is not None and net.maintainers != []:
            lead_maintainer = net.maintainers[0]
            for contract in net.contracts:
                # create args for constructor of special contracts that depend on each other such as Governing.sol
                args = []
                if contract.name == "Governing":
                    args = cls.governing_contract_args(net)
                elif contract.name == "CBDC":
                    args = cls.cbdc_contract_args(net)
                elif contract.name == "CCBDC":
                    args = cls.ccbdc_contract_args(net)

                cls.print_progress(f"Deploying contract '{contract.name}'.", lead_maintainer.deploy_contract, contract, *args)

        else:
            raise NoMaintainerPresentErr(f"There is no maintainer configured in the network's config file, ergo you cannot deploy smart contracts.")

    @classmethod
    def governing_contract_args(cls, net):
        """Arguments for the governing contract."""
        governors = [g.acc_addrs["main"] for g in net.governors] if net.governors is not None else []
        maintainers = [m.acc_addrs["main"] for m in net.maintainers] if net.maintainers is not None else []
        observers = [o.acc_addrs["main"] for o in net.observers] if net.observers is not None else []
        bankers = [b.acc_addrs["main"] for b in net.bankers] if net.bankers is not None else []
        blacklist = []
        args = [governors, maintainers, observers, bankers, blacklist]

        return args

    @classmethod
    def cbdc_contract_args(cls, net):
        """Arguments for the CBDC contract."""
        # get governing contract address for CBDC contract since it is needed
        addr = None
        for c in net.contracts:
            if c.name == "Governing":
                addr = c.addr
                break

        args = []
        if addr is not None:
            args.append(addr)
        else:
            raise GoverningContractNotDeployedErr("No address for Governing Contract found. Is it already deployed?")

        # get token supply from banker nodes
        bankers = []
        token_supply = []
        for b in net.bankers:
            if b.token_supply is not None:
                token_supply.append(b.token_supply)
                bankers.append(b.acc_addrs["main"])

        args.append(bankers)
        args.append(token_supply)

        return args

    @classmethod
    def ccbdc_contract_args(cls, net):
        """Arguments for the CBDC contract."""
        # get governing contract address for CBDC contract since it is needed
        addr = None
        for c in net.contracts:
            if c.name == "Governing":
                addr = c.addr
                break

        return [addr]

    @classmethod
    def contract_setup(cls, net):
        """Calls contract setup functions to fully set them up."""
        if net.maintainers is not None and net.maintainers != []:
            lead_maintainer = net.maintainers[0]
            for contract in net.contracts:
                # create args for constructor of special contracts that depend on each other such as Governing.sol
                if contract.name == "CBDC":
                    for c in net.contracts:
                        if c.name == "CCBDC":
                            addr = c.addr
                            break
                    cls.print_progress(f"Setting up contract '{contract.name}'.", lead_maintainer.setup_contract, contract, addr)
                elif contract.name == "CCBDC":
                    for c in net.contracts:
                        if c.name == "CBDC":
                            addr = c.addr
                            break
                    cls.print_progress(f"Setting up contract '{contract.name}'.", lead_maintainer.setup_contract, contract, addr)
        else:
            raise NoMaintainerPresentErr(f"There is no maintainer configured in the network's config file, ergo you cannot deploy smart contracts.")

    @classmethod
    def copy_contract_info(cls, net):
        """Copies contract interaction tools to nodes."""
        for c in net.contracts:
            for node in net.nodes:
                c.copy_info_to(node.dir)

class Down(Command):
    """Shuts down all docker containers created from config file."""
    HELP = "Stops and shuts down every node's docker container."

    FLAGS = {
        "help": False,
    }

    @classmethod
    def helpstr(cls):
        cmd = cls.__name__.lower()
        usage = f"Usage like:\n\t{Command.NAME} {cmd} [FLAGS]\n"
        flgs = (
            "Flags\n"
            "\t-h, --help\tPrints help and exits.\n"
        )
        helpstr = usage + "\n" + cls.HELP + "\n" + "\n" + flgs + "\n"

        return helpstr

    @classmethod
    def parse_flags(cls, flgs):
        for flg in flgs:
            if flg in ["help", "--help", "-h"]:
                cls.FLAGS["help"] = True
            else:
                raise InvalidFlagErr(f"Invalid flag '{flg}' for subcommand '{cls.__name__.lower()}'")

        return cls.FLAGS

    @classmethod
    def exec(cls, net, flags=[]):
        try:
            flgs = cls.parse_flags(flags)
        except InvalidFlagErr as err:
            return cls.handle_err(err)

        # check flags
        if flgs["help"]:
            print(cls.helpstr())
            return 0
        
        try:
            cls.shut_down_nodes(net)
        except Exception as err:
            cls.handle_err(err)

        return 0

    @classmethod
    def shut_down_nodes(cls, net):
        """Boots up all given nodes in docker containers with node.name as container name."""
        for node in net.nodes:
            if node.is_running():
                cls.print_progress(f"Shutting down node '{node.name}'.", node.down)

# UTILITIES
class Config(object):
    """Represents any object that can be read from config file."""
    def __init__(self, name, config_dict):
        self.dict = config_dict
        self.name = name

        # setting mandatory and optional attributes from dict
        self.set_mand_keys(self.dict)
        self.set_opt_keys(self.dict)

    def set_mand_keys(self, config_dict):
        """Sets mandatory keys of config file as class attribute."""
        # check if all mandatory keys are in file
        for mand_key in self.MANDATORY_KEYS:
            if mand_key not in config_dict.keys():
                raise MandatoryKeyMissingErr(f"Mandatory key '{mand_key}' for '{self.name}' missing from config file.")
            else:
                setattr(self, self.attribute_safe_string(mand_key), self.dict[mand_key])

    def set_opt_keys(self, config_dict):
        """Sets optional keys from config file as class attribute."""
        # read in optional keys and if not present set them to None
        for opt_key in self.OPTIONAL_KEYS:
            if opt_key not in self.dict.keys():
                setattr(self, self.attribute_safe_string(opt_key), None)
            else:
                setattr(self, self.attribute_safe_string(opt_key), self.dict[opt_key])

    def attribute_safe_string(self, string):
        """Transforms strings that are not safe to set as an attribute to a string that is safe to set as an attribute."""
        replace_dict = {
            " ": "_",
            "-": "_"
        }
        for char, replacer in replace_dict.items():
            string = string.replace(char, replacer)

        return string

    def save(self):
        """Saves a config object by writing its important attributes to a 'info.json' in its working directory."""
        # checking if object can be saved
        if hasattr(self, "SAVABLE_ATTRIBUTES") and hasattr(self, "dir"):
            # deciding which keys to save
            dict = {}
            for attr in self.SAVABLE_ATTRIBUTES:
                if attr in self.__dict__.keys():
                    dict[attr] = self.__dict__[attr]
                elif attr in dir(self.__class__):
                    dict[attr] = getattr(self.__class__, attr)(self)

            # write keys to file
            try:
                with open(os.path.join(self.dir, "info.json"), "w") as f:
                    json.dump(dict, f, indent=2)
            except:
                raise Exception(f"Could not write '{self.name}' dictionary to 'info.json'.")
        else:
            raise ObjNotSavableErr(f"Object '{self.name}' is not savable.")

    def info_file_attribs(self):
        """Checks if 'info.json' exists and reads attributes from it."""
        info_file = os.path.join(self.dir, "info.json")
        if os.path.isfile(info_file):
            with open(info_file, "r") as f:
                content = f.read()

            attr_dict = json.loads(content)

            for attr in attr_dict:
                if attr in self.__dict__.keys():
                    self.__dict__[attr] = attr_dict[attr]

class Network(Config):
    """Represents a network config .yaml file as an object and builds functionality and class definitions on top of it."""

    MANDATORY_KEYS = ["id", "name", "orgs", "validators", "docker-settings"]
    OPTIONAL_KEYS = ["contracts", "governors", "bankers", "maintainers", "observers"]

    def __init__(self, name, config_dict, work_dir):
        super().__init__(name, config_dict)

        # setting utility properties which are independent from the config-file
        self.dir = os.path.join(work_dir, self.name)

        # defining docker-settings
        self.docker_settings = DockerSettings(None, config_dict["docker-settings"])

        # defining nodes from input dictionaries
        self.nodes = []
        for node_type in Node.TYPES:
            # trying if node of current type is in config file
            attr = node_type + "s"
            try:
                if attr in self.__dict__.keys() and self.__dict__[attr] is not None:
                    node_dicts = self.__dict__[attr]
                    nodes = []
                    for node_dict in node_dicts:
                        node_name = list(node_dict.keys())[0]
                        node = self.create_node(node_dict, node_type)
                        nodes.append(node)

                    # adding the nodes to self.nodes and to self."node-type" as an attribute
                    self.nodes.extend(nodes)
                    self.__dict__[attr] = nodes
            except:
                traceback.print_exc()
                print()

        # defining contracts
        contracts = []
        for contract_dict in self.contracts:
            contract = self.create_contract(contract_dict)
            contracts.append(contract)

        self.contracts = contracts

    def create_node(self, node_dict, type):
        """Creates a node object of specific type."""
        name = list(node_dict.keys())[0]
        # TODO: Add other node types
        if type == "validator":
            return Validator(name, type, node_dict[name], self.dir, self.docker_settings.geth_port, self.docker_settings.rpc_port, self.docker_settings.workdir)
        elif type == "maintainer":
            return Maintainer(name, type, node_dict[name], self.dir, self.docker_settings.geth_port, self.docker_settings.rpc_port, self.docker_settings.workdir)
        elif type == "governor":
            return Governor(name, type, node_dict[name], self.dir, self.docker_settings.geth_port, self.docker_settings.rpc_port, self.docker_settings.workdir)
        elif type == "banker":
            return Banker(name, type, node_dict[name], self.dir, self.docker_settings.geth_port, self.docker_settings.rpc_port, self.docker_settings.workdir)
        elif type == "observer":
            return Observer(name, type, node_dict[name], self.dir, self.docker_settings.geth_port, self.docker_settings.rpc_port, self.docker_settings.workdir)
    
    def create_contract(self, contract_dict):
        """Creates a contract object."""
        name = list(contract_dict.keys())[0]
        return Contract(name, contract_dict[name], self.dir)

    def create_dir(self):
        try:
            os.mkdir(self.dir)
        except FileExistsError as err:
            raise NetworkDirExistsErr(f"Network directory already exists at '{self.dir}'. Please use the 'init --reset' if you want to reset the network.")

class DockerSettings(Config):
    """Represents docker-settings from network config file."""

    MANDATORY_KEYS = ["network-driver", "subnet", "geth-port", "rpc-port", "workdir"]
    OPTIONAL_KEYS = ["contracts", "governors", "bankers", "maintainers", "observers"]

class Contract(Config):
    """Represents a solidity smart contract from the config file as an object."""
    
    MANDATORY_KEYS = ["path"]
    OPTIONAL_KEYS = []

    SAVABLE_ATTRIBUTES = ["addr", "get_abi"]

    def __init__(self, name, config_dict, net_dir):
        super().__init__(name, config_dict)

        self.dir = os.path.join(net_dir, "contracts", self.name)
        self.info_file = os.path.join(self.dir, "info.json")
        self.bin = os.path.join(self.dir, "bin")
        self.addr = None

        try:
            self.info_file_attribs()
        except:
            pass

    def create_dir(self):
        try:
            os.makedirs(self.bin, exist_ok=True)
        except Exception as err:
            raise ContractDirCreationErr(f"Could not create directory for contract '{self.name}'.")

    def get_bytecode(self):
        """Gets bytecode of this contract as 0x-prefixed hex string."""
        bins = os.listdir(self.bin)
        contract_bin = None
        for cbin in bins:
            if cbin == f"{self.name}.bin":
                contract_bin = os.path.join(self.bin, cbin)
                break
        if cbin is None:
            raise ByteCodeNotFoundErr(f"Bytecode for contract '{self.name}' was not found. Is it already compiled?")

        try:
            bytecode = "0x"
            with open(contract_bin, "r") as f:
                bytecode += f.read()
        
            return bytecode
        except:
            raise ByteCodeNotFoundErr(f"Bytecode for contract '{self.name}' was not found. Is it already compiled?")

    def get_abi(self, load_json=False):
        """Gets ABI of this contract as python dictionary."""
        abis = os.listdir(self.dir)
        abi = os.path.join(self.dir, abis[0])
        for a in abis:
            if a == f"{self.name}.abi":
                abi = os.path.join(self.dir, a)
                break
        if abi is None:
            raise AbiNotFoundErr(f"ABI for contract '{self.name}' was not found. Is it already compiled?")

        try:
            with open(abi, "r") as f:
                abi = f.read()

            if load_json:
                return abi
            else:
                abi = json.loads(abi)
                return abi
        except:
            raise AbiNotFoundErr(f"ABI for contract '{self.name}' was not found. Is it already compiled?")

    def compile(self, runtime=False):
        """Compiles contract to bytecode and ABI."""
        try:
            # compile
            if runtime:
                cmd = f"solc --overwrite --optimize --optimize-runs=1000 --bin-runtime -o {self.bin} {self.path}"
            else:
                cmd = f"solc --overwrite --optimize --optimize-runs=1000 --bin -o {self.bin} {self.path}"

            Shell.call(cmd, check_ret=True)

            # create ABI
            cmd = f"solc --abi --overwrite -o {self.dir} {self.path}"
            Shell.call(cmd, check_ret=True)
        except:
            raise ContractCompilationErr(f"Could not compile contract '{self.name}'.")

    def deploy(self, w3):
        """Deploys a contract on the blockchain."""
        bytecode = self.get_bytecode()
        abi = self.get_abi()
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)

        tx_hash = contract.constructor().transact()

        return tx_hash

    def write_to_genesis(self, validators):
        """Writes compiled bytecode into genesis block."""
        contract = os.listdir(self.bin)[0]
        
        try:
            bytecode = "0x"
            with open(os.path.join(self.bin, contract), "r") as f:
                bytecode += f.read() 

            for val in validators:
                genesis = val.get_genesis()
                addr_dict = {
                    "code": bytecode,
                    "balance": "0"
                }
                genesis["alloc"][self.node_addr] = addr_dict
                val.set_genesis(genesis)
        except:
            raise BytecodeNotReadableErr(f"Could not read contract '{self.name}' bytecode file '{contract}'.")

    def get_info_dict(self):
        """Gets content saved to contract's 'info.json'."""
        try:
            with open(self.info_file, "r") as f:
                data = f.read()

            info_dict = json.loads(data)

            return info_dict
        except:
            raise ReadingInfoFileErr(f"'info.json' for contract '{self.name}' was not found at '{self.info_file}'.")

    def write_info_dict(self, info_dict):
        """Writes a dictionary to contract's 'info.json'."""
        try:
            with open(self.info_file, "w") as f:
                json.dump(info_dict, f)
        except:
            raise WritingInfoFileErr(f"Could not write to contract '{self.name}'s 'info.json' at '{self.info_file}'. Does it exist?")

    def write_contract_addr(self, addr):
        """Writes the contracts address to its directory."""
        info_dict = self.get_info_dict()
        info_dict["addr"] = addr
        self.write_info_file(info_dict)

    def copy_info_to(self, dir):
        """Copies 'info.json' to given directory."""
        shutil.copy(self.info_file, os.path.join(dir, f"{self.name}-contract.info"))

    def print_status(self):
        """Prints node's status to stdoud."""
        str = f"\n{Deco.STATUS}[STAT]{Deco.RESET}\t{self.name}"
        for attr in self.SAVABLE_ATTRIBUTES:
            if attr == "get_abi":
                continue
            if attr in self.__dict__.keys():
                str += f"\n\t{attr}: {self.__dict__[attr]}"
            elif attr in dir(self.__class__):
                str += f"\n\t{attr}: {getattr(self.__class__, attr)(self)}"
        print(str)

class Account(Config):
    """Represents a geth account as an object."""

    MANDATORY_KEYS = ["passphrase"]
    OPTIONAL_KEYS = ["balance"]

    GETH_BIN = os.path.join(Command.WORKDIR, "quorum", "build", "bin", "geth")

    def __init__(self, name, acc_dict):
        super().__init__(name, acc_dict)

        self.addr = None

    def create(self, dir):
        """Creates geth account."""
        # call 'geth account new'
        os.chdir(dir)
        cmd = f"{self.GETH_BIN} --datadir {os.path.join(dir, 'data')} account new"
        out = Shell.call(cmd, stdin=f"{self.passphrase}\n{self.passphrase}\n", check_ret=True)
        os.chdir(Command.WORKDIR)

        self.addr = self.get_addr(out)

    def get_addr(self, out):
        """Gets address from 'geth account new' output."""
        out = out.replace("\n", " ")
        for str in out.split(" "):
            if str.startswith("0x"):
                return str

class Node(Config):
    """Represents a basic quorum node as an object and builds functionality on top of its node directory."""

    TYPES = ["quorum-node", "validator", "observer", "governor", "maintainer", "banker"]
    MANDATORY_KEYS = ["org", "ip", "port", "rpc-port", "docker-ip"]
    OPTIONAL_KEYS = ["accounts"]

    # binary directories
    ISTANBUL_BIN = os.path.join(Command.WORKDIR, "istanbul-tools", "build", "bin", "istanbul")
    GETH_BIN = os.path.join(Command.WORKDIR, "quorum", "build", "bin", "geth")
    BOOTNODE_BIN = os.path.join(Command.WORKDIR, "quorum", "build", "bin", "bootnode")

    INIT_FILES = [os.path.join("data", "geth", "chaindata", "CURRENT"), os.path.join("data", "geth", "chaindata", "LOCK"), os.path.join("data", "geth", "chaindata", "LOG")]
    SAVABLE_ATTRIBUTES = ["node_addr", "enode", "acc_addrs", "container_id", "ip", "rpc_port", "is_init", "is_setup", "is_running"]

    def __init__(self, name, type, node_dict, net_dir, docker_geth_port, docker_rpc_port, docker_dir):
        assert type in self.TYPES
        super().__init__(name, node_dict)

        self.type = type

        # functional attributes independent of config file
        self.dir = os.path.join(net_dir, self.org, self.type + "s", self.name)
        self.geth_dir = os.path.join(self.dir, "data", "geth")
        #self.logs = os.path.join(self.dir, "node.log")

        # setting docker ports
        self.docker_geth_port = docker_geth_port
        self.docker_rpc_port = docker_rpc_port
        self.docker_dir = docker_dir

        # uninitialized attributes
        self.accs = None
        self.acc_addrs = None
        self.container_id = None
        self.node_addr = None
        self.enode = None

        # read attributes from info.json file if it exists
        try:
            self.info_file_attribs()
        except:
            pass

        # create account objects
        self.create_acc_objs()

    def create_dir(self):
        """Creates this node's working directory as well as a geth directory."""
        try:
            os.makedirs(os.path.join(self.dir, "data", "geth"), exist_ok=True)
        except Exception as err:
            raise NodeDirCreationErr(f"Could not create directory for node '{self.name}' at '{self.dir}'.")

    def create_acc_objs(self):
        """Creates account objects from config file."""
        if self.accounts is not None:
            self.accs = {}
            for a in self.accounts:
                acc_name = list(a.keys())[0]
                acc_obj = Account(acc_name, a[acc_name])

                # try setting the address of the account (only works when it has been already created)
                try:
                    acc_obj.addr = self.acc_addrs[acc_name]
                except:
                    pass

                self.accs[acc_name] = acc_obj

    def create_accs(self):
        """Creates a geth accounts for this node."""
        if self.accs is not None:
            self.acc_addrs = {}
            for name, acc in self.accs.items():
                acc.create(self.dir)
                self.acc_addrs[name] = acc.addr
        self.save()

    def get_static_nodes(self):
        """Returns the nodes's local 'static-nodes.json' as a list."""
        try:
            static_nodes_path = os.path.join(self.dir, "data", "static-nodes.json")
            with open(static_nodes_path, "r") as f:
                data = f.read()
            static_nodes = json.loads(data)

            return static_nodes
        except:
            raise StaticNodesErr(f"Could not read 'static-nodes.json' at '{static_nodes_path}'.")

    def set_static_nodes(self, static_nodes):
        """Writes a given static nodes list to the node's local 'stati-nodes.json'."""
        try:
            static_nodes_path = os.path.join(self.dir, "data", "static-nodes.json")
            with open(static_nodes_path, "w") as f:
                json.dump(static_nodes, f, indent=2)
        except:
            raise StaticNodesErr(f"Could not write 'static-nodes.json' at '{static_nodes_path}'.")

    def init(self):
        """Calls 'geth init ...' on node's working directory."""
        os.chdir(self.dir)
        uid = os.getuid()
        cmd = f"{self.GETH_BIN} --datadir data init genesis.json"
        ret = Shell.call(cmd, check_ret=True)
        os.chdir(Command.WORKDIR)
        self.save()

    def is_init(self):
        """Checks if some files created by 'geth init' exist and then decides if validator was initialized."""
        init_files = [os.path.join(self.dir, path) for path in self.INIT_FILES]

        return self.all_files_exist(init_files)

    def is_setup(self):
        """Checks if setup files exist and then decides if validator was setup."""
        setup_files = [os.path.join(self.dir, path) for path in self.SETUP_FILES]

        return self.all_files_exist(setup_files)

    def all_files_exist(self, files):
        """Checks if all of the given file paths are valid files."""
        for f in files:
            if not os.path.isfile(f):
                return False

        return True

    def is_running(self):
        """Checks if docker container with node.name exists."""
        if self.is_init():
            cmd = f"docker ps -aq --filter name={self.name}"
            ret = Shell.call(cmd, check_ret=True)
            if ret == "":
                return False
            else:
                return True
        else:
            return False
        
        return True

    def print_status(self):
        """Prints node's status to stdoud."""
        str = f"\n{Deco.STATUS}[STAT]{Deco.RESET}\t{self.name}"
        for attr in self.SAVABLE_ATTRIBUTES:
            if attr in self.__dict__.keys():
                str += f"\n\t{attr}: {self.__dict__[attr]}"
            elif attr in dir(self.__class__):
                str += f"\n\t{attr}: {getattr(self.__class__, attr)(self)}"
        print(str)

    def down(self):
        """Stops node's docker container."""
        if self.is_running():
            cmd = f"docker stop {self.name}"
            Shell.call(cmd, check_ret=False)
            self.save()

    def up(self, net):
        """Boots up validator node in a docker container with name 'self.name'."""
        if not self.is_running():
            uid = os.getuid()
            cmd = f"docker run -d --rm --user {uid} -w {self.docker_dir} -v {self.dir}:{self.docker_dir} --name {self.name} --ip {self.docker_ip} -p {self.rpc_port}:{self.docker_rpc_port} -p {self.port}:{self.docker_geth_port} --network {net.name} -e ISTANBUL_BLOCK_PERIOD={self.ISTANBUL_BLOCK_PERIOD} -e NETWORK_ID={net.id} {self.type}"
            self.container_id = Shell.call(cmd, check_ret=True).replace("\n", "")[:12]
            self.save()
        else:
            raise NodeAlreadyRunningErr(f"Node '{self.name}' is already running. Please shut all nodes down, before trying to boot up.")

class Validator(Node):
    """Represents a validor node as an object."""

    SETUP_FILES = [os.path.join("genesis.json"), os.path.join("data", "geth", "nodekey"), os.path.join("data", "static-nodes.json")]

    # istanbul config
    ISTANBUL_BLOCK_PERIOD = 5

    def __init__(self, name, type, node_dict, net_dir, docker_geth_port, docker_rpc_port, docker_dir):
        assert type in self.TYPES
        super().__init__(name, type, node_dict, net_dir, docker_geth_port, docker_rpc_port, docker_dir)

    def setup(self):
        """Calls 'istanbul setup ...' on validator's working directory."""
        # call 'istanbul setup'
        os.chdir(self.dir)
        cmd = f"{self.ISTANBUL_BIN} setup --num 1 --quorum --save --verbose"
        out = Shell.call(cmd, check_ret=True)
        os.chdir(Command.WORKDIR)

        # empty the alloc field from created genesis block
        genesis = self.get_genesis()
        genesis["alloc"] = {}
        self.set_genesis(genesis)

        # write utility attributes for later refrences
        self.node_addr, pubkey = self.extract_info_from_istanbul_output(out)
        self.enode = self.edit_enode(pubkey, self.docker_ip, self.docker_geth_port)

        # copy nodekey to geth directory and remove directory '0'
        nodekey_path = os.path.join(self.dir, "0", "nodekey")
        try:
            shutil.copy(nodekey_path, self.geth_dir)
            shutil.rmtree(os.path.join(self.dir, "0"))
        except:
            raise Exception(f"Could not copy '{nodekey_path}' to '{self.geth_dir}'")

        # finally: save node
        self.save()

    def extract_info_from_istanbul_output(self, out):
        """Extracts validator address, enode info from 'istanbul setup ...' output."""
        val_info, _ = out.split("\n\n\n\n")

        val_info = val_info.split("\n", 1)[1]
        val_info = json.loads(val_info)
        self.save()

        return val_info["Address"], val_info["NodeInfo"]

    def edit_enode(self, pubkey, ip, port):
        """Edits given enode with node's port and ip."""
        enode = pubkey.replace("@0.0.0.0:", f"@{ip}:")
        enode = enode.replace(":30303?", f":{port}?")
        
        return enode

    def get_genesis(self):
        """Returns the validator's local genesis block as a dict."""
        try:
            genesis_path = os.path.join(self.dir, "genesis.json")
            with open(genesis_path, "r") as f:
                genesis_data = f.read()
            genesis_dict = json.loads(genesis_data)

            return genesis_dict
        except:
            raise GenesisBlockErr(f"Could not read 'genesis.json' at '{self.dir}/genesis.json'.")

    def set_genesis(self, genesis_dict):
        """Writes a given genesis dict to the validator's local genesis block."""
        try:
            genesis_path = os.path.join(self.dir, "genesis.json")
            with open(genesis_path, "w") as f:
                json.dump(genesis_dict, f, indent=2)
        except:
            raise GenesisBlockErr(f"Could not write 'genesis.json' at '{self.dir}/genesis.json'.")

    def create_static_nodes(self, vals):
        """Creates a static-nodes.json file in node's working directory from given validator nodes."""
        static_nodes = []
        # get enodes from all validators and check if they are present
        for val in vals:
            if val.enode is not None:
                static_nodes.append(val.enode)
            else:
                raise ValidatorNotSetupErr("Validator '{val.name}' has no enode. Is it setup already?")

        # write static_nodes.json
        try:
            with open(os.path.join(self.dir, "data", "static-nodes.json"), "w") as f:
                json.dump(static_nodes, f, indent=2)
        except:
            raise StaticNodesErr(f"Could not write static-nodes.json at '{self.dir}/data/data/static-nodes.json'.")

    def form_consortium(self, vals):
        """Edits genesis block of this validator to include given validators so that there is a consortium from the beginning."""
        val_addrs = [val.node_addr for val in vals]
        
        # creating a string to pass as an argument to 'istanbul extra encode ...'
        addr_str = ""
        for addr in val_addrs:
            addr_str += f"{addr},"
        addr_str = addr_str[:-1]

        # calling 'istanbul extra encode ...' and write extra data to genesis file
        cmd = f"{self.ISTANBUL_BIN} extra encode --validators={addr_str}"
        extra_data = Shell.call(cmd, check_ret=True).split(" ")[-1].replace("\n", "")

        # write extraData to genesis file
        genesis = self.get_genesis()
        genesis["extraData"] = extra_data
        self.set_genesis(genesis)

    def pre_alloc_funds(self, addr, balance):
        """Pre-allocates funds for a given address."""
        genesis = self.get_genesis()
        genesis["alloc"][addr] = {"balance": str(balance)}
        self.set_genesis(genesis)

class NonValidatorNode(Node):
    """Represents a non-validator node as an object. These nodes share certain properties such as that they need to have at least one account associated with them."""

    MANDATORY_KEYS = ["org", "ip", "port", "rpc-port", "docker-ip", "accounts"]
    SETUP_FILES = [os.path.join("genesis.json")]

    def __init__(self, name, type, node_dict, net_dir, docker_geth_port, docker_rpc_port, docker_dir):
        assert type in self.TYPES
        super().__init__(name, type, node_dict, net_dir, docker_geth_port, docker_rpc_port, docker_dir)

    def setup(self, val_genesis):
        """Copies genesis block that has been created by a validator to its own directory and sets up nodekey and enode for this node."""
        shutil.copy(val_genesis, self.dir)
        self.enode, self.node_addr = self.create_enode()

    def create_enode(self):
        """Creates node's enode and derives address from it to be recognizable later."""
        # create nodekey
        nodekey_path = os.path.join(self.dir, "data", "geth", "nodekey")
        cmd = f"{self.BOOTNODE_BIN} --genkey {nodekey_path}"
        Shell.call(cmd, check_ret=True)

        # derive enode from nodekey
        cmd = f"{self.BOOTNODE_BIN} --nodekey {nodekey_path} --writeaddress"
        pubkey = Shell.call(cmd, check_ret=True).replace("\n", "")
        enode = self.construct_enode(pubkey, self.docker_ip, self.docker_geth_port)
        addr = self.addr_from_pubkey(pubkey)

        return enode, addr

    def addr_from_pubkey(self, pubkey):
        """Calculates node's address from public key."""
        cmd = f"{self.ISTANBUL_BIN} address --nodeidhex {pubkey}"
        addr = Shell.call(cmd, check_ret=True).replace("\n", "")

        return addr

    def construct_enode(self, pubkey, ip, port):
        """Creates a enode from given public key and node's ip and port."""
        enode = f"enode://{pubkey}@{ip}:{port}?discport=0"

        return enode

    def up(self, net):
        """Boots up non-validator node in a docker container with name self.name."""
        if not self.is_running():
            uid = os.getuid()
            cmd = f"docker run -d --rm --user {uid} -w {self.docker_dir} -v {self.dir}:{self.docker_dir} --name {self.name} --ip {self.docker_ip} -p {self.rpc_port}:{self.docker_rpc_port} --network {net.name} {self.type} geth --allow-insecure-unlock --datadir data --nodiscover --syncmode full --verbosity 5 --networkid {net.id} --rpc --rpcaddr 0.0.0.0 --rpcport {self.docker_rpc_port} --rpcapi admin,db,eth,debug,mine,net,shh,txpool,personal,web3,quorum,istanbul --emitcheckpoints --port {self.docker_geth_port}"
            self.container_id = Shell.call(cmd, check_ret=True).replace("\n", "")[:12]
            self.save()
        else:
            raise NodeAlreadyRunningErr(f"Node '{self.name}' is already running. Please shut all nodes down, before trying to boot up.")

class Maintainer(NonValidatorNode):
    """Represents a maintainer node as an object. Maintainers deploy contracts to the network."""

    def setup_contract(self, contract, contract_addr):
        """Sets up CBDC contract."""
        if "main" in self.accs.keys():
            w3 = Web3(Web3.HTTPProvider(f"http://{self.ip}:{self.rpc_port}"))
            
            addr = self.accs["main"].addr
            passphrase = self.accs["main"].passphrase
            w3.middleware_onion.inject(web3.middleware.geth_poa_middleware, layer=0)
            w3.geth.personal.unlockAccount(addr, passphrase)

            w3.eth.defaultAccount = addr
            bytecode = contract.get_bytecode()
            abi = contract.get_abi()
            eth_contract = w3.eth.contract(contract.addr, abi=abi, bytecode=bytecode)
            tx_hash = eth_contract.functions.setup(contract_addr).transact()
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        else:
            raise MainAccountErr(f"No geth main account found for maintainer node '{self.name}'.")

    def deploy_contract(self, contract, *args):
        """Deploys given contract to the blockchain."""
        # unlock main account, create tx and lock account again
        if "main" in self.accs.keys():
            w3 = Web3(Web3.HTTPProvider(f"http://{self.ip}:{self.rpc_port}"))
            
            addr = self.accs["main"].addr
            passphrase = self.accs["main"].passphrase
            w3.middleware_onion.inject(web3.middleware.geth_poa_middleware, layer=0)
            w3.geth.personal.unlockAccount(addr, passphrase)

            w3.eth.defaultAccount = addr
            bytecode = contract.get_bytecode()
            abi = contract.get_abi()
            eth_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            tx_hash = eth_contract.constructor(*args).transact()
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

            contract.addr = tx_receipt.contractAddress
            contract.save()
        else:
            raise MainAccountErr(f"No geth main account found for maintainer node '{self.name}'.")

class Governor(NonValidatorNode):
    """Represents a governor node as an object. (Necessary Code in Dockerfile)."""

class Banker(NonValidatorNode):
    """Represents a banker node as an object."""
    OPTIONAL_KEYS = ["accounts", "token-supply"]

class Observer(NonValidatorNode):
    """Represents an observer as an object. (Necessary Code in Dockerfile)."""

if __name__ == "__main__":
    sys.exit(Command.call())

