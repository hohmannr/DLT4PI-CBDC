pragma solidity >=0.6.0 <0.7.0;

import "./Governing.sol";
import "./CCBDC.sol";

contract CBDC {
    
    // constants
    string public constant name     = "General Purpose Coin";
    string public constant symbol   = "GPC";
    uint8  public constant decimals = 18;

    // contracts
    Governing private governingContract;
    CCBDC     private ccbdcContract;

    // mappings
    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public supplyOf;
    mapping(address => uint)    public isMerchant;

    // events
    event Transfer(
        address from,
        address to,
        uint256 amount
    );

    event Minting(
        address from,
        address to,
        uint256 amount
    );

    event Allocation(
        address from,
        address to,
        uint256 amount
    );

    event Conversion(
        address from,
        address to,
        uint256 amount
    );

    // modifiers
    modifier onlyGovernor() {
        require(governingContract.governors(msg.sender), "Only a governor can call this function.");
        _;
    }

    modifier onlyMaintainer() {
        require(governingContract.maintainers(msg.sender), "Only a maintainer can call this function.");
        _;
    }

    modifier onlyCCBDC() {
        require(msg.sender == address(ccbdcContract), "Can only be called from CCBDC contract.");
        _;
    }

    modifier onlyBanker() {
        require(governingContract.bankers(msg.sender), "Only a governor can call this function.");
        _;
    }

    modifier enoughSupply(uint256 amount) {
        require(supplyOf[msg.sender] >= amount);
        _;
    }

    modifier enoughBalance(uint256 amount) {
        require(balanceOf[msg.sender] >= amount);
        _;
    }

    // functions
    constructor(address _governingContract, address[] memory _bankers, uint[] memory _supplies) public {
        governingContract = Governing(_governingContract);

        // pre-initialize supply for banker nodes
        require(_bankers.length == _supplies.length);
        for(uint i = 0; i < _bankers.length; i++) {
            address banker = _bankers[i];
            require(governingContract.bankers(banker));
            supplyOf[banker] = _supplies[i];
        }
    }

    function setup(address _ccbdcContract) public onlyMaintainer {
        ccbdcContract = CCBDC(_ccbdcContract);
    }

    function transfer(address to, uint tokens) public enoughBalance(tokens) {
        if(!governingContract.bankers(to)) {
            balanceOf[msg.sender] -= tokens;
            balanceOf[to] += tokens;
        } else {
            balanceOf[msg.sender] -= tokens;
            supplyOf[to] += tokens;
        }

        emit Transfer(msg.sender, to, tokens);
    }

    function mint(address to, uint256 amount) public onlyGovernor {
        require(governingContract.bankers(to), "To address must be a banker.");
        supplyOf[to] += amount;

        emit Minting(msg.sender, to, amount);
    }

    function allocate(address to, uint256 amount, uint merchantCode) public onlyBanker enoughSupply(amount) {
        balanceOf[to] += amount;
        supplyOf[msg.sender] -= amount;
        isMerchant[to] = merchantCode;

        emit Allocation(msg.sender, to, amount);
    }

    function convert(address from, address to, uint amount) public onlyCCBDC {
        if(!governingContract.bankers(to)) {
            balanceOf[to] += amount;
        } else {
            supplyOf[to] += amount;
        }

        emit Conversion(from, to, amount);
    }
}

