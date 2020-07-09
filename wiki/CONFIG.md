# Network Configuration File

The network config file is used by the network setup script `network.py` to setup all the components of the network, e.g. nodes, docker settings, contracts etc. The default name is `network.yaml` and it is read each time that `network.py` is run. It provides an easy way for customization, network design and architecture, aswell as network deployment accross multiple machines.

## Keys

- `id` - geth/quorum network ID
- `name` - network name
- `orgs` - organizations participating in the network
- `docker-settings` - Settings docker will use to setup a docker network and enable communication among nodes
- `validators` - validator nodes forming Istabul BFT consensus
- `maintainers` - maintainer nodes to setup and maintain contracts
- `governors` - governer nodes to govern blockchain (control node types)
- `bankers` - banker nodes to allocate CBDC for customers on chain
- `observers` - observer nodes that broadcast the permissioned blockchain to the public

## Docker Settings

- `network-driver` - [docker network driver](https://www.docker.com/blog/understanding-docker-networking-drivers-use-cases/)
- `subnet` - subnet mask that containers will use to form a network
- `geth-port` - port that containers will use to communicate via geth/quorum protocol
- `rpc-port` - geth/quorum's JSON-RPC interface
- `workdir` - working directory that each node will use in its container

## Nodes

- `<node-name>` - node name used for network directory setup and as docker container name. Per convention it is `<org>.<three-digit-node-code><number-in-org>` e.g. `central-bank.gov0`
    - **Mandatory Keys**
    - `org` - organization the node is part of
    - `ip` - IP on physical machine connected with node
    - `port` - geth/quorum port on physical machine
    - `rpc-port` - geth/quorum's JSON RPC interface port
    - `docker-ip` - IP of docker container. Must be within specified docker `subnet`!
    - **Optional Keys**
    - `accounts` - pre-creates geth/quorum accounts/addresses to be used in the network
    - **Node Specific Keys**
    - `accounts` - every non-validator node must have at least one account named `main`. These are encoded into the `Governing.sol` contract and represet the node on chain
    - `supply` - optional key for banker nodes, it specifies the initial supply of CBDC that they can hand out

## Accounts

- `<account-name>` - account's name used for aliasing
    - **Mandatory Keys**
    - `passphrase` - passphrase used to unlock private key

## Contracts

- `<contract-name>` - contract's name as specified in the `<contract-name>.sol` file
    - **Madatory Keys**
    - `path` - Path to `<contract-name>.sol` file

