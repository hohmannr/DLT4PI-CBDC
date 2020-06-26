pragma solidity ^0.6.0;

//Helpful Intro to OpenZeppelin: YouTube - Video: https://www.youtube.com/watch?v=wkISWhw7AP0&list=PLbbtODcOYIoFdQ37ydykQNO-MNGER6mtd&index=3)

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.1/contracts/presets/ERC20PresetMinterPauser.sol";
import "GoverningContract.sol"
import "GeneralDigitalCoin.sol"

    contract CDCToken is ERC20PresetMinterPauser, GoverningContract, GDCToken {
    constructor() public ERC20PresetMinterPauser("ColoredDigitalCoin", "CDC") {}

// -------------- PCBDC Issuance ----------------------------

//Alternative to STEP 1-5 might be using so-calleed "Hooks" , e.g. _beforeTokenTransfer(address from, address to, uin256 amount) --> See OpenZeppelin docs!

//STEP 1: Central (Admin) Governor Node - Role allocation

//Access limited to DEFAULT_ADMIN_ROLE
function roleallocation() public view {
require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Function use only allowed for DEFAULT_ADMIN_ROLE!");

    //GoverNodes role allocation
    if(... == GovernorNode) {
        grantRole(MINTER_ROLE, ...);
        grantRole(PAUSER_ROLE, ...);
    }

    //MaintainerNode role allocation
    if(... == MaintainerNode) {
        grantRole(PAUSER_ROLE, ...);
    }

    //BankerNode role allocation
    if(... == BankerNode) {
        grantRole(PAUSER_ROLE, ...);
    }

    //TBD with Anagha (to be included in GoverningContract - NGONode (needing to validate that farmer has lost his crops!)
    if(... == BankerNode) {
        grantRole(PAUSER_ROLE, ...);
    }

    else {
        console.log("ERROR - Type of node (e.g. BankerNode) was not recognized!");
        //Return error!
    }
}

//STEP 2: ObserverNode requests specific CDC amount (amount is validatet by trusted NGO!)

function CDCmintingrequest() public view {

    //ObserverNode inputs amount, corresponding to his loss
    uint256 requestedCDCamount; //How is the amount inputted by the ObserverNode?

    //Checking if requested CDC amount is valid
    if(...){
        return true;
    }

    else {
        console.log("ERROR - Requested CDC amount could not be validated!");
        //Return error!
    }

}

//STEP 3: CDC Minting requested amount (to governors address)

//Access limited to MINTER_ROLE and only if minting request is true.
function CDCminting() public view {
require(hasRole(MINTER_ROLE, msg.sender) && hasRole(PAUSER_ROLE, msg.sender), "Function use only allowed for MINTER_ROLE and PAUSER_ROLE!");

    //Node having the MINTER_ROLE (:= GovernorNode) inputs amount to be minted
    uint256 CDCmintingamount; //How is the amount inputted by the GoverNode?

    /*Make sure that no minting is possible before checking that the requested
    amount of CDC (requestedCDCamount) equals the actual minting amount (CDCmintingamount)*/
    if(whenNotPaused(...) == true) {
        pause(...);
    }

    //Minting if requested amount of CDC equals amount to be minted AND requested amount was validated by NGO!
    if(CDCmintingrequest(...) == true && CDCmintingamount == requestedCDCamount) {
        unpause(...);
        mint(..., CDCmintingamount);
    }

    else {
            console.log("ERROR - CDCminting function not working!");
            //Return error!
    }
}

//STEP 4: BankerNode - Transfering minted amount to verfified wallet address (inlc. Incentive for doing so - Reward for helping!)
function transfermintedCDCamount() public view {
require(... == BankerNode, "Function use only allowed for BankerNodes!");

    //BankerNode has to request the newly minted CDCamount
    if(...){

        //TBD: What does increaseAllowancde and decreaseAllowance mean? Is it worth it to inherit from SafeERC20 contract? 
    }

    else{
        console.log("ERROR - Transfer of minted CDC failed!");
        //Return error!
    }
}

// --------------- TRADING PHASE! ----------------------------

//STEP 6: Observer node - Requesting sendind specific amount to verfied wallet address of seller (also observer node)

//STEP 7: Governor node - After NGO has ensured that crops have been delivered - Sending request of PCBDC is gruanted

//STEP 8: Banker node - PCBDC are transferred to verified wallet address of seller 

// --------------- TOKEN CONVERSION PHASE! ----------------------------

//STEP 9: Observer node - Seller requests for conversion of PCBDC to GeneralCBDC

//STEP10: Banker node - Transfers one to one GCBDC in exchange for PCBDC 

//STEP11: Banker node - Converted and used PCBDC is burnt


}