# Network

This directory is the core of all network components necessary to host a quorum test-network locally. A script `network.py` is provided that automagically sets up a network from a given `network.yaml` configuration file.

## Description

This is a network proposal, that is the basis for a publicly visible but permissioned blockchain based on [quorum](https://github.com/jpmorganchase/quorum), which itself is based on [geth](https://github.com/ethereum/go-ethereum). To achieve this, the network design depends on five different kind of nodes: `validators`, `observers`, `governers`, `maintainers` and `bankers`. Their roles are illustrated below.

`validators` secure the network through Ethereum's **Istanbul BFT Consensus**, `observers` broadcast the blockchain content to the wider public, `governers` govern collectively the blockchain, `maintainers` upload and maintain smart contracts and `bankers` provide wallets for blockchain interaction and ecosystem inclusion.

![network-nodes](https://raw.githubusercontent.com/hohmannr/DLT4PI-CBDC/master/pics/network-nodes.png)

## Network Config File

The network configuration file `network.yaml` is used to define the network participants (organizations) with their specific nodes.

<!-- TODO: DESCRIBE NETWORK CONFIG FILE MORE -->

The included `network.yaml` configuration models a central bank which issues a CBDC over this network. It includes

- 4x `validators` from two different organizations (central bank and government)

<!-- TODO: ADD NODES HERE -->

## Network Script

`network.py` is the network setup tool that builds a network automagically from the network configuration file `network.yaml`.

```
$ ./network.py help

Usage like:
    ./network.py COMMAND [FLAGS]

COMMAND
    prepare	Makes 'quorum' and 'istanbul-tools' dependencies.
    init	Initializes network from config file.
    up		Boots up all network nodes.
    down	Shuts down all network nodes.
    clean	Deletes network directory and cleans up afterwards.

For more info on commands use:
    ./network.py COMMAND --help
```

## Default Network Setup

To setup the network from the provided `network.yaml` config file, first **make sure to have the dependent submodules 'quorum' and 'istanbul-tool'** cloned in this directory.

```
$ git submodule init
$ git submodule update
```

The first network in this directory is setup in three simple steps:

**Step 1.** - Making dependencies

```
$ ./network.py prepare
```

**Step 2.** - Initializing nodes

```
$ ./network.py init --no-docker
```

This initializes the nodes, creates a certain directory hierarchy (learn more [here](#directory-tree)) and prepares every node for booting. By default, this also initializes the use of `docker` for the nodes, but this is **NOT IMPLEMENTED YET**.

**Step 3.** - Booting up all nodes

```
$ ./network.py up --no-docker
```

Now the network configured in `network.yaml` should be running.
Every node is a seperate running (quorum flavored) `geth` node.

**Stopping running nodes**

```
$ ./network.py down
```

This downs every node. **Please always use this method to stop the geth nodes**, it is doing important clean up work.

**Resetting the network**

```
$ ./network.py init --reset
```

This simply shuts down all nodes, deletes the network directory cleans up network fragments and then reinitializes the network with a shiny clean new directory.

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
```

- `addresses.json` - file containing addresses of all nodes
- `<org>` - directory containing organizations participating nodes grouped in their node-types subdirectories
- `<node-type>` - directory containing all nodes of this type e.g. validators, observers etc.
- `<node-name>` - directory containing node logic
- `genesis.json` - node's genesis file (is the same for all nodes)
- `data` - `geth` data direcory

This structure is generated from the `network.yaml` and represents all nodes and organizations listed in there. It is needed for the setup with docker containers.

## Changelog

- version 0.1.1:
    - added automatic node boot up and shut down
    - overhauled `network.py` script in OOP manner
    - added network setup guide in README

- version 0.1:
    - initial commit with `network.py` setup script

