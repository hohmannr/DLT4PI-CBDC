# DLT4PI-CBDC

## Documentation

This Repo has several important sub-directories. They hold the code for specific parts of the overall model.
Documentation of the code is provided as READMEs in the according sub-directories. 

Available READMEs:

- [network](https://github.com/hohmannr/DLT4PI-CBDC/blob/master/network/README.md)

## Requirements

A generic UNIX operating system is needed.

### Linux

Make sure `linux.h` headers are installed.

### General

```
- python3
    - pyyaml
    - web3.py
- make
- go
- docker
- solc
```

**Please make sure the requirements are fullfilled before proceeding.**

## Network

For further information on how to setup a test network, please check the guide provided in the networks [README](https://github.com/hohmannr/DLT4PI-CBDC/tree/master/network#default-network-setup)

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

