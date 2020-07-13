const fs = require('fs');
const Web3 = require('web3');
const Contract = require('web3-eth-contract');
const os = require('os');

async function web3Connect(providerUrl) {
    let web3 = new Web3(new Web3.providers.HttpProvider(providerUrl));
    
    let isConnected = await web3.eth.net.isListening()
        .then(result => {
            return result;
        })
        .catch(err => {
            console.error('Could not connect to given geth RPC. Are the nodes up and running?');} );
    return web3;
}

function getMainAccount(pathToNodeInfo) {
    let data = fs.readFileSync(pathToNodeInfo, 'utf8');
    let info = JSON.parse(data);
    
    return {addr: info.acc_addrs.main.toLowerCase(), pw: "root"};
}

function getAccount(pathToNodeInfo) {
    let data = fs.readFileSync(pathToNodeInfo, 'utf8');
    let info = JSON.parse(data);
    
    return {addr: info.acc_addrs.account0.toLowerCase(), pw: "root"};
}

async function unlockAccount(web3, acc) {
    return web3.eth.personal.unlockAccount(acc.addr, acc.pw, 100);
}

async function lockAccount(web3, acc) {
    return web3.eth.personal.lockAccount(acc.addr);
}

function getContractInfo(pathToContractInfo) {
    let data = fs.readFileSync(pathToContractInfo, 'utf8');
    let contractInfo = JSON.parse(data);

    return {addr: contractInfo.addr.toLowerCase(), abi: contractInfo.get_abi};
}

async function methodCall(web3, contractInfo, from, method, args) {
    let contract = new web3.eth.Contract(contractInfo.abi, contractInfo.addr);

    let unlocked = await unlockAccount(web3, from);
    let result = await contract.methods[method](...args).call({from: from.addr});
    let locked = await lockAccount(web3, from);

    return result;
}

async function methodSend(web3, contractInfo, from, method, args, event) {
    let contract = new web3.eth.Contract(contractInfo.abi, contractInfo.addr);

    let unlocked = await unlockAccount(web3, from);
    let result = await contract.methods[method](...args).send({from: from.addr, gas: 1000000000})
        .catch(err => {
            // console.error(err);
            return null;
        });
    let locked = await lockAccount(web3, from);
    if (event !== null && result !== null) {
        return result.events[event].returnValues;
    } else {
        return null;
    }
}

function testStart(desc) {
    console.log(`\x1b[34m[TEST]\x1b[0m ${desc}`);
}

function testEval(result, expect) {
    if (result === expect) {
        console.log(`    \x1b[32m--> test passed\x1b[0m`);
    } else {
        console.log(`    \x1b[31m--> Result is not expectation: ${result} != ${expect}\x1b[0m`);
        console.log(`    \x1b[31m--> test failed\x1b[0m`);
    }
}

const val0Info = '../network/cbdc-net/central-bank/validators/central-bank.val0/info.json'
const gov0Info = '../network/cbdc-net/central-bank/governors/central-bank.gov0/info.json';
const gov1Info = '../network/cbdc-net/government/governors/government.gov0/info.json';
const mnt0Info = '../network/cbdc-net/government/maintainers/government.mnt0/info.json';
const bnk0Info = '../network/cbdc-net/aclydia/bankers/aclydia.bnk0/info.json';
const bnk1Info = '../network/cbdc-net/bb-bank/bankers/bb-bank.bnk0/info.json';
// TODO: Add observer

const smp0 = getAccount(val0Info)
const gov0 = getMainAccount(gov0Info);
const gov1 = getMainAccount(gov1Info);
const mnt0 = getMainAccount(mnt0Info);
const bnk0 = getMainAccount(bnk0Info);
const bnk1 = getMainAccount(bnk1Info);
// TODO: Add observer

const smp0Url = 'http://127.0.0.1:22000';
const gov0Url = 'http://127.0.0.1:22005';
const gov1Url = 'http://127.0.0.1:22006';
const mnt0Url = 'http://127.0.0.1:22004';
const bnk0Url = 'http://127.0.0.1:22007';
const bnk1Url = 'http://127.0.0.1:22008';
// TODO: Add observer

const governingContractInfo = getContractInfo('../network/cbdc-net/contracts/Governing/info.json');
const cbdcContractInfo = getContractInfo('../network/cbdc-net/contracts/CBDC/info.json');
const ccbdcContractInfo = getContractInfo('../network/cbdc-net/contracts/CCBDC/info.json');

// exports
exports.smp0 = smp0;
exports.gov0 = gov0;
exports.gov1 = gov1;
exports.mnt0 = mnt0;
exports.bnk0 = bnk0;
exports.bnk1 = bnk1;
// TODO: Add observer

exports.governingContract = governingContractInfo;
exports.cbdcContract      = cbdcContractInfo;
exports.ccbdcContract     = ccbdcContractInfo;

exports.smp0RPC = smp0Url;
exports.gov0RPC = gov0Url;
exports.gov1RPC = gov1Url;
exports.mnt0RPC = mnt0Url;
exports.bnk0RPC = bnk0Url;
exports.bnk1RPC = bnk1Url;
// TODO: Add observer

exports.methodCall = methodCall;
exports.methodSend = methodSend;
exports.web3Connect = web3Connect;
exports.testStart = testStart;
exports.testEval = testEval;

