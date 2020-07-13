const utils = require('./utils');

async function getBalance(addr, coinID) {
    let balance = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.ccbdcContract, utils.gov0, 'balanceOf', [coinID, addr]);
        });
    return balance;
}

async function getBalanceCBDC(addr) {
    let balance = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.cbdcContract, utils.gov0, 'balanceOf', [addr]);
        });
    return balance;
}

async function getShadeCBDC(addr) {
    let shade = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.cbdcContract, utils.gov0, 'isMerchant', [addr]);
        });
    return shade;
}

async function setShadeCBDC(addr, shadeID) {
    let shade = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.bnk0, 'allocate', [addr, 0, shadeID], 'Allocation');
        });
    return shade;
}

async function getMintingRequest(requestID) {
    let mintingRequest = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.ccbdcContract, utils.gov0, 'mintingRequests', [requestID]);
        });
    return mintingRequest;
}

async function hasMintingRequest(addr, coinID) {
    let hasRequest = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.ccbdcContract, utils.gov0, 'hasMintingRequest', [addr, coinID]);
        });
    return hasRequest;
}

async function getCoinInfo(coinID) {
    let coinInfo = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.ccbdcContract, utils.gov0, 'showCoinInfo', [coinID]);
        });
    return coinInfo;
}

async function createNewCoin() {
    utils.testStart('Create a new colored coin...');
    let newCoin = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.gov0, 'createNewCoin', [1, [10, 20, 30], 1000, 1000000], 'CoinCreation');
        });
    let coinInfo = await getCoinInfo(newCoin.coinID);
    utils.testEval(coinInfo['0'].toLowerCase(), utils.gov0.addr.toLowerCase());
    utils.testEval(coinInfo['2'], '1000');
}

async function createNewCoinAsNonGovernor() {
    utils.testStart('Create a new colored coin as non-governor...(should not work)');
    let newCoin = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.bnk0, 'createNewCoin', [1, [10, 20, 30], 1000, 1000000], 'CoinCreation');
        });
    utils.testEval(newCoin, null);
}

async function createMintingRequest() {
    utils.testStart('Create request for colored coin...');
    let result = await utils.web3Connect(utils.smp0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.smp0, 'requestCoin', [1, 100], null);
        });
    let mintingRequest = await hasMintingRequest(utils.smp0.addr, 1);
    utils.testEval(mintingRequest, true);
}

async function createMintingRequestTwice() {
    utils.testStart('Create request for the same colored coin twice...(should not work)');
    let result = await utils.web3Connect(utils.smp0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.smp0, 'requestCoin', [1, 100], null);
        });
    utils.testEval(result, null);
}

async function approveMintingRequest() {
    utils.testStart('Approve minting request...');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.gov0, 'approveMintingRequest', [1], 'Approval');
        });
    let newBalance = await getBalance(utils.smp0.addr, 1);
    utils.testEval(newBalance, "100");
}

async function approveMintingRequestAsNonGovernor() {
    utils.testStart('Approve minting request as non-governor...(should not work)');
    let result = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.bnk0, 'approveMintingRequest', [1], 'Approval');
        });
    let newBalance = await getBalance(utils.smp0.addr, 1);
    utils.testEval(result, null);
}

async function transfer() {
    utils.testStart('Transferring CCDBC (within the contract)...');
    let result = await utils.web3Connect(utils.smp0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.smp0, 'transfer', [1, utils.bnk0.addr, 50], 'Transfer');
        });
    let balance = await getBalance(utils.smp0.addr, 1);
    let newBalance = await getBalance(utils.bnk0.addr, 1);
    utils.testEval(newBalance, "50");
}

async function convert() {
    utils.testStart('Converting from CCBDC to CBDC...');
    let result = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.bnk0, 'transfer', [1, utils.smp0.addr, 50], 'Conversion');
        });
    let balance = await getBalanceCBDC(utils.smp0.addr);
    utils.testEval(balance, "50");
}

async function getShade() {
    utils.testStart('Setting and getting an address shade...');
    let thisShade = await setShadeCBDC(utils.smp0.addr, 10);
    let shade = await getShadeCBDC(utils.smp0.addr);
    utils.testEval(shade, "10");
}

async function transferWithNotSufficientFunds() {
    utils.testStart('Transferring CCDBC without sufficient balance (should not work)...');
    let result = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.ccbdcContract, utils.bnk0, 'transfer', [1, utils.smp0.addr, 50], 'Conversion');
        });
    utils.testEval(result, null);
}

async function tests() {
    let test0 = await createNewCoin();
    let test1 = await createNewCoinAsNonGovernor();
    let test2 = await createMintingRequest();
    let test3 = await createMintingRequestTwice();
    let test4 = await approveMintingRequest();
    let test5 = await approveMintingRequestAsNonGovernor();
    let test6 = await transfer();
    let test7 = await getShade();
    let test8 = await convert();
    let test9 = await transferWithNotSufficientFunds();
}

tests();
