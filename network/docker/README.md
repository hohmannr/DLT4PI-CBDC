# Docker

This prototype utilizes docker containers to "virtualize" the network nodes (and their types) and to run a virtual network on a local machine. Since there are custom docker images for each node type, a network can be setup fairly easily also accross multiple machines.

## Docker Images

For each node-type there is a custom `Dockerfile` located at `./network/docker/<node-type>/Dockerfile`. All of node-type images inherit quorum functionality from the custom `quorum-node` image. We had to build a custom image for quorum, since the official one does not yet support consensus through Istanbul BFT.

## Docker Containers

Each container is spin up from its according node-type docker image. Container names are chosen according to the convention that also the network configuration file follows: `<org>.<node-tpye><index>`, e.g. `government.gov0`.

## Contract interaction through docker

Like described in `./network/README.md` there is the option to connect and interact directly through the docker container shell with the blockchain. This is considered more secure, than over a http-connection. For automation purposes, we have provided three command-line-tools that interact with the three provided smart contracts `Governing.sol`, `CBDC,sol` and `CCBDC.sol`. These tools are meant for contract-management (e.g. creating a new colored coin or voting to add a new governor).

Since they are meant for contract-management, only governor-nodes posses access to all three command-line-tools and banker-nodes possess only access to the tool for interacting with the `CBDC.sol` contract. For all other node-types that (usually) are not interacting with these smart-contracts it makes no sense to ship the tools.

Connect to a network node via its name and create an interactive shell and print command-line-tool's help:

```
$ docker exec -it government.gov0 /bin/sh
> governing --help

usage: /bin/governing [-h] [--ipc path/to/ipc] [--info /path/to/Governing.info]
                      [--node-info /path/to/info.json]
                      {add,remove,is,vote} ...

Command line wrapper to interact with governing contract.

positional arguments:
  {add,remove,is,vote}
    add                 Makes proposal to add given address to specified type.
    remove              Makes proposal to remove given address from specified list.
    is                  Checks if given address is of given type.
    vote                Votes for given proposal id.

optional arguments:
  -h, --help            show this help message and exit
  --ipc path/to/ipc     Path to 'geth.ipc'.
  --info /path/to/Governing.info
                        Path to 'Governing-contract.info'.
  --node-info /path/to/info.json
                        Path to node's 'info.json'.
```

```
> cbdc --help

usage: /bin/cbdc [-h] [--ipc path/to/ipc] [--info /path/to/CBDC.info]
                 [--node-info /path/to/info.json]
                 {balance,supply,mint,alloc} ...

Command line wrapper to interact with CBDC contract.

positional arguments:
  {balance,supply,mint,alloc}
    balance             Shows balance of address.
    supply              Shows supply of banking node address.
    mint                Mints a given amount of CBDC to given banking node address. Only
                        available to governor nodes.
    alloc               Allocates CBDC into given address. Only available to banker nodes.

optional arguments:
  -h, --help            show this help message and exit
  --ipc path/to/ipc     Path to 'geth.ipc'.
  --info /path/to/CBDC.info
                        Path to 'CBDC-contract.info'.
  --node-info /path/to/info.json
                        Path to node's 'info.json'.
```

```
> ccbdc --help

usage: /bin/ccbdc [-h] [--ipc path/to/ipc] [--info /path/to/CCBDC.info]
                  [--node-info /path/to/info.json]
                  {balance,approve,show,create} ...

Command line wrapper to interact with CCBDC contract.

positional arguments:
  {balance,approve,show,create}
    balance             Shows the address' balance of a given colored coin.
    approve             Approves a request.
    show                Shows colored coin details.
    create              Creates a new colored coin.

optional arguments:
  -h, --help            show this help message and exit
  --ipc path/to/ipc     Path to 'geth.ipc'.
  --info /path/to/CCBDC.info
                        Path to 'CCBDC-contract.info'.
  --node-info /path/to/info.json
                        Path to node's 'info.json'.
```

## Example: Create a new colored coin

Each subcommand has its own help page, so use it to checkout what the other commands do.

```
> ccbdc create --help

usage: /bin/ccbdc create [-h] -C <color-id> -S <shade>... [<shade>... ...] -s <supply> -d
                         <deadline>

optional arguments:
  -h, --help            show this help message and exit
  -C <color-id>         Color of new coin.
  -S <shade>... [<shade>... ...]
                        Shade/Merchantcode that converts colored coin to general CBDC.
  -s <supply>           Initial supply of new coin.
  -d <deadline>         Amount of blocks the new coin can exist before destroyed.
```

Now let's create a new colored coin with `color-id: 1`, `shades: [10, 20]`, `supply: 10000000` and `expiration: 8000000`

```
> ccbdc create -C 1 -S 10 20 -s 10000000 -d 800000
```

Type in this node's passphrase. (If you use the default network configuration file, all node's passwords are "root").
A new colored coin has been created. From the return value, you can read its `coinID`, which is used to reference the coin later.

