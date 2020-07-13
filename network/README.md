# Network

This directory is the core of all network components necessary to host a quorum test-network locally. A script `network.py` is provided that automagically sets up a network from a given `network.yaml` configuration file.

## Description

This is a network proposal, that is the basis for a publicly visible but permissioned blockchain based on [quorum](https://github.com/jpmorganchase/quorum), which itself is based on [geth](https://github.com/ethereum/go-ethereum). To achieve this, the network design depends on five different kind of nodes: `validators`, `observers`, `governers`, `maintainers` and `bankers`. Their roles are illustrated below.

`validators` secure the network through Ethereum's **Istanbul BFT Consensus**, `observers` broadcast the blockchain content to the wider public, `governers` govern collectively the blockchain, `maintainers` upload and maintain smart contracts and `bankers` provide wallets for blockchain interaction and ecosystem inclusion.

![network-nodes](https://raw.githubusercontent.com/hohmannr/DLT4PI-CBDC/master/pics/network-nodes.png)

## Network Config File

The network configuration file `network.yaml` is used to define the network participants (organizations) with their specific nodes.

More on the `network.yaml` file [here](http://www.url.com)

The included `network.yaml` configuration models a central bank which issues a CBDC over this network. It includes

- 4x `validators` from two different organizations (central bank and government)
- 2x `governors` one from the central bank and one from the government
- 2x `bankers` from two different private banks (aclydia and bb-bank)
- 1x `maintainer` from the government
- 1x `observer` from life-ngo

## Network Script

`network.py` is the network setup tool that builds a network automagically from the network configuration file `network.yaml`.

```
$ ./network.py help

Usage like:
	./network.py COMMAND [FLAGS] <config-file>

Commands
	prepare	Builds needed docker images and creates new docker network.
	init	Initializes network, espacially nodes, from config file.
	clean	Removes network directory and cleans up afterwards.
	up	Boots up all network nodes in docker containers.
	setup	Sets up network state by compiling and deploying smart contracts.
	down	Stops and shuts down every node's docker container.

For more info on commands use:
	./network.py COMMAND --help
```

## Default Network Setup

To setup the network from the provided `network.yaml` config file, first **make sure to have the dependent submodules 'quorum' and 'istanbul-tool'** cloned in this directory.

```
$ git submodule init
$ git submodule update
```

The first network in this directory is setup in four simple steps:

**Step 1.** - Making dependencies

```
$ cd quorum && make all && cd ..
$ cd istanbul-tools && make && cd ..
$ ./network.py prepare
```

This makes the dependencies and builds up the needed docker images for all node-types from each `Dockerile` located at `./docker/<node-tpye>/Dockerfile`. For more information on how we use docker in this prototype please check [here](http://www.url.com). Depending on your machine, this can take a while, since it is compiling quorum/geth from source in the `quorum-node` base container, since the officially provided quorum-image has no Istanbul BFT built in.

**Step 2.** - Initializing nodes

```
$ ./network.py init
```

This initializes the nodes, creates a certain directory hierarchy (learn more [here](#directory-tree)) and prepares every node for booting. All nodes are initialized as seperate docker containers.

**Step 3.** - Booting up all nodes

```
$ ./network.py up
```

Now the network configured in `network.yaml` should be running.
Every node is a seperate running quorum/geth node running in docker containers.

**Step 4** - Setting up contracts

```
$ ./network.py setup
```

This sets up all contracts specified in `network.yaml`. There are three types of contracts: `Governing.sol`, `CBDC.sol`, `CCBDC.sol`. They are at the core of the proposed payment system.

For more information on the Contracts, look [here](http://www.url.com).


**Stopping running nodes**

```
$ ./network.py down
```

This shuts down all nodes. **Please always use this method to stop the geth nodes**, it is doing important clean up work.

**Resetting the network**

```
$ ./network.py init --reset
```

This simply shuts down all nodes, deletes the network directory, cleans up network fragments and then reinitializes the network with a shiny clean and new directory.

**Deleting the network**

```
$ ./network.py clean
```

This shuts down all running network nodes, completly removes the network directory and cleans up afterwards.

## Directory Tree

When using `network.py` to setup the network, following directory logic is created and should not be messed with.

```
./<network-name>
    +-- addresses.json
    +-- <org>
        +-- <node-type>
            +-- <node-name>
                +-- genesis.json
                +-- data
                +-- info.json
                +-- <contract-name>-contract.json
    +-- contracts
        +-- <contract-name>
            +-- <contract-name>.abi
            +-- info.json
            +-- bin
                +-- <contract-name>.bin
            
```

- `addresses.json` - file containing addresses of all nodes
- `<org>` - directory containing organizations participating nodes grouped in their node-types subdirectories
- `<node-type>` - directory containing all nodes of this type e.g. validators, observers etc.
- `<node-name>` - directory containing node logic
- `genesis.json` - node's genesis file (is the same for all nodes)
- `data` - `geth` data direcory
- `info.json` - a node/contract information file, contains addresses, account data, etc.
- `<contract-name>` - directory containing contract ABI
- `<contract-name>.abi` - contract's ABI
- `<contract-name>`.bin - contract's compiled bytecode

This structure is generated from the `network.yaml` and represents all nodes and organizations listed in there. It is needed for the setup with docker containers.

More on the file-structure [here](http://www.url.com).
More on the docker setup used [here](http://www.url.com).

## How to connect to the network

Once the network is setup and running, there are three main ways to connect to a network nodes

**Option 1**

Connect via console. This connects directly to the geth/quorum node and gives you a javascript-console to work with. To make contract interaction easier, use `geth.js` as a preload. The binary to connect to the nodes is located at `./quorum/build/geth`. Fore example, to connect to the government's first governor-node use the following command. The node's ip and rpc-port are printed to the console when calling `./network.py up`, but are also available at `./<network-name>/<org-name>/<node-type>/<node-name>/info.json`. Please **do not use** `--preload geth.js` when connecting to a validator-node, since they do not have any accounts and are seperated from other node-types.

```
$ ./quorum/build/bin/geth attach --preload geth.js http://127.0.0.1:22006
```

Once connected via console, before you can invoke transactions to call contract methods, you need to initialize the contract you want to interact with, with its address. For each contract, the `geth.js` preloads its interface (called `governing`, `cbdc` and `ccbdc`). So if you want to interact for example with `Governing.sol`, use the following command. Since addresses are generated for each network setup anew, you can find each contract's address in `./<network-name>/contracts/<contract-name>/info.json`.

```
> gov = governing.at("<address>")
> gov.governorCount.call() 
```

If you want to know about each smart contract, please refer to [here](http://www.url.com).

**This interface is not thought for human interaction.** The benefit of having this interface is to automate web services in the future that interact with these smart contracts. So this is the foundation for future applications that can be built upon this prototype.

**Option 2**

Connect via JSON-RPC. This method is thought to be used extensively used for observer-nodes. These nodes broadcast a copy of the blockchain to the general public. Everyone can get any information on the blockchain via standard quorum/geth JSON-RPC calls (more documentation on the [official website](https://eth.wiki/json-rpc/API)).

For example if you want to get the current block number from the observer-node (which in production should be the only node that has this port open), just use a `POST` request as such:

```
$ curl -X POSTi -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":10}' http://127.0.0.1:22009
```

This allows the setup of blockchain listeners, which everyone can operate without the ability to participate in the consensus algorithm. Thus ensuring trust in a permissioned blockchain.

**Option 3**

Connect via `docker`. For security relevant operations (anything that includes a node's main private key), e.g. creation of new colored coins via `CCBDC.sol`, we considered a web-connection as insecure. Therefore we provide command-line-tools (more info [here](http://www.url.com)), to interact with the provided smart contracts in a more secure fashion by directly connecting to the underlying docker container. In production this can be done via a private intra-net. This allows future automation via network scripts.

To connect to the government's first governor-node and e.g. get information on how to issue a new colored coin use the following command.

```
$ docker exec -it government.gov0 /bin/sh
> ccbdc --help
```

## Changelog

- version 0.4:
    - added lacking node types (observer, banker, governor)
    - added contract interface for banker and governor node

- version 0.3:
    - added smart contract creation automation
    - added maintainer node type

- version 0.2:
    - added docker container support (this will be the default)

- version 0.1.1:
    - added automatic node boot up and shut down
    - overhauled `network.py` script in OOP manner
    - added network setup guide in README

- version 0.1:
    - initial commit with `network.py` setup script

