pragma solidity ^0.6.0;

//Helpful Intro to OpenZeppelin: YouTube - Video: https://www.youtube.com/watch?v=wkISWhw7AP0&list=PLbbtODcOYIoFdQ37ydykQNO-MNGER6mtd&index=3)

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v3.0.1/contracts/token/ERC20/ERC20.sol";

contract GDCToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("GeneralDigitalCoin", "GDC") public {
        _mint(msg.sender, initialSupply);
    }
}