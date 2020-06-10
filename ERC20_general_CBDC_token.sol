pragma solidity ^0.4.19;

/* The basic ERC20 Token was copied from https://gist.github.com/giladHaimov/8e81dbde10c9aeff69a1d683ed6870be#file-basicerc20-sol
and comments base on the explanatory article https://www.toptal.com/ethereum/create-erc20-token-tutorial */

contract ERC20Basic {

    string public constant name = "ERC20Basic";
    string public constant symbol = "BSC";
    uint8 public constant decimals = 18;  


    event Approval(address indexed tokenOwner, address indexed spender, uint tokens);
    event Transfer(address indexed from, address indexed to, uint tokens);

    //The first mapping object, balances, will hold the token balance of each owner account.
    mapping(address => uint256) balances;

    /*The second mapping object, allowed, will include all of the accounts approved to 
    withdraw from a given account together with the withdrawal sum allowed for each.*/
    mapping(address => mapping (address => uint256)) allowed;
    
    uint256 totalSupply_;

    using SafeMath for uint256;

    //Setting the initial amount of ICO tokens as "totalSupply"
   constructor(uint256 total) public {  
	totalSupply_ = total;
	balances[msg.sender] = totalSupply_;
    }  

    //This function will return the number of all tokens allocated by this contract regardless of owner.
    function totalSupply() public view returns (uint256) {
	return totalSupply_;
    }
    
    //balanceOf will return the current token balance of an account, identified by its owner’s address.
    function balanceOf(address tokenOwner) public view returns (uint) {
        return balances[tokenOwner];
    }

    /* The transfer function is used to move "numTokens" amount of tokens from the owner’s balance to that of 
    another user, or receiver. The transferring owner is msg.sender i.e. the one executing the function, which 
    implies that only the owner of the tokens can transfer them to others.*/
    function transfer(address receiver, uint numTokens) public returns (bool) {
        require(numTokens <= balances[msg.sender]);
        balances[msg.sender] = balances[msg.sender].sub(numTokens);
        balances[receiver] = balances[receiver].add(numTokens);
        emit Transfer(msg.sender, receiver, numTokens);
        return true;
    }

    /* What approve does is to allow an owner i.e. msg.sender to approve a delegate account — possibly 
    the marketplace itself — to withdraw tokens from his account and to transfer them to other accounts.*/
    function approve(address delegate, uint numTokens) public returns (bool) {
        allowed[msg.sender][delegate] = numTokens;
        Approval(msg.sender, delegate, numTokens);
        return true;
    }

    //This function returns the current approved number of tokens by an owner to a specific delegate, as set in the approve function.
    function allowance(address owner, address delegate) public view returns (uint) {
        return allowed[owner][delegate];
    }

    /*The transferFrom function is the peer of the approve function, which we discussed previously. 
    It allows a delegate approved for withdrawal to transfer owner funds to a third-party account.*/
    function transferFrom(address owner, address buyer, uint numTokens) public returns (bool) {
        require(numTokens <= balances[owner]);    
        require(numTokens <= allowed[owner][msg.sender]);
    
        balances[owner] = balances[owner].sub(numTokens);
        allowed[owner][msg.sender] = allowed[owner][msg.sender].sub(numTokens);
        balances[buyer] = balances[buyer].add(numTokens);
        Transfer(owner, buyer, numTokens);
        return true;
    }

    /*NOTE "transferFrom" function: The two require statements at function start are to verify that the transaction is legitimate, 
    i.e. that the owner has enough tokens to transfer and that the delegate has approval for (at least) numTokens to withdraw.
    In addition to transferring the numTokens amount from owner to buyer, this function also subtracts numTokens from the delegate’s allowance. 
    This basically allows a delegate with a given allowance to break it into several separate withdrawals, which is typical marketplace behavior.*/

}

library SafeMath { 
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
      assert(b <= a);
      return a - b;
    }
    
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
      uint256 c = a + b;
      assert(c >= a);
      return c;
    }
    
/*NOTE SafeMath: SafeMath is a Solidity library aimed at dealing with one way hackers have been known to break contracts: integer overflow attack. 
In such an attack, the hacker forces the contract to use incorrect numeric values by passing parameters that 
will take the relevant integers past their maximal values.*/

}