pragma solidity ^0.6.1;

contract Dummy {
    uint public storedData;
    address public owner;

    constructor() public {
        storedData = 255;
    }

    function set(uint x) public {
        storedData = x;
    }
    function get() public view returns (uint) {
        return storedData;
    }
}
