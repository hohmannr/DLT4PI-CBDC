const utils = require('./utils');

async function getGovernor() {
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.governingContract, utils.gov0, 'governorCount', []);
        });
}

async function voteOnProposal(govAcc, govRPC, proposalID) {
    let result = await utils.web3Connect(govRPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.governingContract, govAcc, 'vote', [proposalID], 'NewVote');
        });
    return result.voteCount;
}

async function addGovernor() {
    utils.testStart('Adding new governor...');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.governingContract, utils.gov0, 'makeProposal', [utils.smp0.addr, 0, 0], 'NewProposal');
        });

    let voteCount;
    voteCount = await voteOnProposal(utils.gov0, utils.gov0RPC, result.proposalID);
    voteCount = await voteOnProposal(utils.gov1, utils.gov1RPC, result.proposalID);
    
    let isGovernor = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.governingContract, utils.gov0, 'governors', [utils.smp0.addr]);
        });
    utils.testEval(isGovernor, true);
}

async function removeGovernor() {
    utils.testStart('Removing governor...');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.governingContract, utils.gov0, 'makeProposal', [utils.smp0.addr, 0, 1], 'NewProposal');
        });

    let voteCount;
    voteCount = await voteOnProposal(utils.gov0, utils.gov0RPC, result.proposalID);
    voteCount = await voteOnProposal(utils.gov1, utils.gov1RPC, result.proposalID);
    
    let isGovernor = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodCall(web3, utils.governingContract, utils.gov0, 'governors', [utils.smp0.addr]);
        });
    utils.testEval(isGovernor, false);
}

async function makeProposalAsNonGovernor() {
    utils.testStart('Make proposal as non-governor...(should not be possible)');
    let result = await utils.web3Connect(utils.bnk0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.governingContract, utils.bnk0, 'makeProposal', [utils.smp0.addr, 0, 0], 'NewProposal');
        });
    utils.testEval(result, null);
}

async function addExistingNodeToOtherGroup() {
    utils.testStart('Trying to add existing node of type banker to governors...(should not be possible)');
    let result = await utils.web3Connect(utils.gov0RPC)
        .then(web3 => {
            return utils.methodSend(web3, utils.governingContract, utils.gov0, 'makeProposal', [utils.bnk0.addr, 0, 0], 'NewProposal');
        });
    utils.testEval(result, null);
}

async function tests() {
    let test0 = await addGovernor();
    let test1 = await removeGovernor();
    let test3 = await makeProposalAsNonGovernor();
    let test4 = await addExistingNodeToOtherGroup();
}

tests();

