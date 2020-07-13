const utils = require('./utils');

async function getSupply(addr) {
    let supply = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.cbdcContract, utils.gov0, 'supplyOf', [addr]);
        });
    return supply;
}

async function getBalance(addr) {
    let supply = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.cbdcContract, utils.gov0, 'balanceOf', [addr]);
        });
    return supply;
}

async function getInitialSupply() {
    utils.testStart('Get initial supply of banker node...(should be 1000 tokens)')
    let supply = await getSupply(utils.bnk0.addr);
    utils.testEval(supply, "1000");
}

async function mint() {
    utils.testStart('Mint new coins as governor...');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.gov0, 'mint', [utils.bnk0.addr, 100], 'Minting');
        });
    let newSupply = await getSupply(utils.bnk0.addr);
    utils.testEval(newSupply, "1100");
}

async function mintAsNonGovernor() {
    utils.testStart('Mint new coins as non-governor...(should not work)');
    let result = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.bnk0, 'mint', [utils.bnk0.addr, 100], 'Minting');
        });
    utils.testEval(result, null);
}

async function mintToNonBanker() {
    utils.testStart('Mint new coins to non-banker...(should not work)');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.gov0, 'mint', [utils.smp0.addr, 100], 'Minting');
        });
    utils.testEval(result, null);
}

async function allocate() {
    utils.testStart('Allocate coins as banker to customer...');
    let allocation = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.bnk0, 'allocate', [utils.smp0.addr, 100, 10], 'Allocation');
        });
    let newBalance = await getBalance(utils.smp0.addr);
    utils.testEval(newBalance, "100");
}

async function allocateAsNonBanker() {
    utils.testStart('Allocate coins as non-banker...(should not work)');
    let allocation = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.gov0, 'allocate', [utils.smp0.addr, 100, 10], 'Allocation');
        });
    utils.testEval(allocation, null);
}

async function callConvert() {
    utils.testStart('Try to convert CCBDC into CBDC manually...(should not work)');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.gov0, 'convert', [utils.smp0.addr, utils.bnk0.addr, 100], 'Conversion');
        });
    utils.testEval(result, null);
}

async function transfer() {
    utils.testStart('Transfer coins...');
    let allocation = await utils.web3Connect(utils.smp0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.smp0, 'transfer', [utils.bnk1.addr, 100], 'Transfer');
        });
    let supply = await getSupply(utils.bnk1.addr);
    utils.testEval(supply, "1100");
}

async function transferInsufficientFunds() {
    utils.testStart('Transfer coins, but has insufficient balance...(should not work)');
    let transfer = await utils.web3Connect(utils.smp0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.cbdcContract, utils.smp0, 'transfer', [utils.bnk1.addr, 100], 'Transfer');
        });
    utils.testEval(transfer, null);
}

async function isMerchant(addr) {
    let merchant = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.cbdcContract, utils.gov0, 'isMerchant', [addr]);
        });
    return merchant;
}
async function checkMerchantCode() {
    utils.testStart('Checking merchant code that has been set...');
    let merchCode = await isMerchant(utils.smp0.addr);
    utils.testEval(merchCode, "10");
}

async function tests() {
    let test0 = await getInitialSupply();
    let test1 = await mint();
    let test2 = await mintAsNonGovernor();
    let test3 = await mintToNonBanker();
    let test4 = await allocate();
    let test5 = await allocateAsNonBanker();
    let test6 = await callConvert();
    let test7 = await transfer();
    let test8 = await transferInsufficientFunds();
    let test9 = await checkMerchantCode();
}

tests();
