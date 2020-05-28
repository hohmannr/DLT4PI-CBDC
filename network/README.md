# Network

This directory is the core of all network components necessary to host a quorum test-network locally. A script `network.py` is provided that automagically sets up a network from a given `network.yaml` file.

## Description

This is a network proposal, that is the basis for a publicly visible but permissioned blockchain based on [quorum](https://github.com/jpmorganchase/quorum), which itself is based on [geth](https://github.com/ethereum/go-ethereum). To achieve this, the network design depends on five different kind of nodes: `validators`, `observers`, `governers`, `maintainers` and `bankers`. Their roles are illustrated below. `validators` secure the network through Ethereum's **Istanbul BFT Consensus**, `observers` broadcast the blockchain content to the wider public, `governers` govern collectively the blockchain, `maintainers` upload and maintain smart contracts and `bankers` provide wallets for blockchain interaction and ecosystem inclusion.

![network-architecture]("PATH")

## Network Config File

The network configuration file `network.yaml` is used to define the network participants (organizations) with their specific nodes.

<!-- TODO: DESCRIBE NETWORK CONFIG FILE MORE -->

The included `network.yaml` configuration models a central bank which issues a CBDC over this network. It includes

- 4x `validators` from two different organizations (central bank and government

<!-- TODO: ADD NODES HERE -->

## Network Script

`network.py` is the network setup tool that builds a network automagically from the network configuration file `network.yaml`.

<!-- TODO: ADD NETWORK SCRIPT TUTORIAL -->

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

