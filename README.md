# DLT4PI-CBDC

## Documentation

This Repo has is structured in main sub-directories `./network`, `./contracts`, `./tests`. Each sub-directory has its own README that explains the code setup in this specific sub-directory. In addition to these READMEs, a small Wiki can be found in `./wiki`. It contains all READMEs and further explanations.

## Requirements

A generic UNIX operating system is needed.

### Linux

Make sure `linux.h` headers are installed (they normally should be installed already).

### General

```
- python3
    - pyyaml
    - web3.py
- make
- go
- docker
- solc
- node
- npm
    - web3.js
```

**Please make sure the requirements are fullfilled before proceeding.**

### How to install?

The installation process for the dependencies rely heavily on your operating system. Here is some official documentation for each of the dependecies:

**Python3**

Python3 often comes already shipped with your OS. On certain Linux distribution you have to install an additional `python3-dev` package, which contains header-files necessary for running own python code. [This is the offical python3 download page](https://www.python.org/downloads/). See [Testing Disclaimer](#testing-disclaimer) for the python version used.

Additionally to `python3`, you also need the packages `web3.py` and `pyyaml`. The network setup script relies on these dependencies. You can install them via the python3 package installer `pip3` [official pip documentation](https://pypi.org/project/pip/).

```
$ pip3 install web3 pyyaml
```

**make**

Make is needed to make the dependencies. Normally the `make` command ships already with your OS.

**Golang**

Golang is needed to run the quorum/geth instances. How to install it, depends heavily on your OS. Golang normally also gets shipped with your distro's package-manager (if you are on linux). Further information can be found [here](https://golang.org/doc/install).

**Docker**

Docker is the containerization software used to build up the various node types and to form a virtual network on a single physical machine. Docker is sometimes tricky to setup. How to do it properly can be read in their [documentation](https://docs.docker.com/get-docker/). Also make sure that the `docker-daemon` is running before trying to setup the network.

**Solc**

`solc` is the solidity compiler used to automatically compile the smart contracts located in `./contracts`. There are various ways to install `solc` described [here](https://solidity.readthedocs.io/en/v0.4.21/installing-solidity.html). Normally if you install the `solidity` package with your package-manager, it comes with `solc` as its compiler. It is important to have the `solc` command working. Check by typing:

```
$ which solc
```

**Nodejs**

`node` is used for tests performed in `./tests` of the smart contracts aswell as to make interaction with the network nodes easier. `node` can be downloaded from [here](https://nodejs.org/en/download/), but it is most likely also inclueded as a package of your package-manader.

**Node Package Manager**

`npm` is used to build a node packages, e.g. the tests in `./tests`. It comes normally distributed with `node`.


## Where to go now?

Once the requirements are fullfilled, you are ready to setup the network. Therefore please go to `./network` and proceed with the README there.

**Intended Process Flow**
- fullfill requirements 
- setup network
- test smart contracts

## Testing Disclaimer

The Code has been tested with following versions on `5.6.14-arch1-1` Linux.

```
- python3=3.8.3
- make=4.3
- go=go1.14.3
- docker
    - client=19.03.9-ce
    - engine=19.03.9-ce
    - containerd=v1.3.4.m
    - runc=1.0.0-rc10
    - docker-init=0.18.0
- solc=0.6.10
- node=v14.5.0
- npm=6.14.5
```

## License

### MIT License

Copyright (c) 2020 hohmannr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

