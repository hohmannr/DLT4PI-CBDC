# Tests

This directory contains various integration tests for all of the provided smart contracts.

## Running tests

These tests considers tht the network has been fully setup using the `../network/network.yaml` default configuration file that ships with this repository. They are intended to be used right after the network has been setup.

First make sure that `web3.js` is installed.

```
$ npm install web3
```

Please **follow the testing order** below, since the tests can influence each other, if not executed one after the other.

**Step 1** - Test `Governing.sol`

```
$ node governingTests.js
```

**Step 2** - Test `CBDC.sol`

```
$ node cbdcTests.js
```

**Step 3** - Test `CCBDC.sol`

```
$ node ccbdcTests.js
```

Tests can be fairly slow, this is because we are altering blockchain state by one transaction per block and the blocktime is by default set to 5 seconds.
