pragma solidity ^0.6.0;

import "./Governing.sol";
import "./CBDC.sol";

contract CCBDC {

    // Defining external contracts
    Governing private governingContract;
    CBDC private cbdcContract;

    // colored coins
    mapping(uint => ColoredCoin) public coloredCoins;
    uint256 coloredCoinCount;

    // requests to receive colored coin
    mapping(uint => MintingRequest) public mintingRequests;
    uint256 mintingRequestCount;

    // check to prevent multiple request for the same coin by the same addr
    mapping(address => mapping(uint => bool)) public hasMintingRequest;

    // Structs
    struct ColoredCoin {
        address creator;
        uint color;
        uint[] shades;
        uint256 supply;
        uint deadlineBlock;
        mapping(address => uint256) balanceOf;
    }

    struct MintingRequest {
        uint coinID;
        address sender;
        bool approved;
        uint256 amount;
    }

    // Events
    event CoinCreation(
        address from,
        uint coinID,
        uint256 supply
    );

    event Transfer(
        uint coinID,
        address from,
        address to,
        uint256 amount
    );

    event Request(
        uint coinID,
        address from,
        uint256 amount
    );

    event Approval(
        uint coinID,
        address to,
        uint256 amount
    );

    event Conversion(
        uint coinID,
        address from,
        address to,
        uint256 amount
    );

    // Modifiers
    modifier preDeadline(uint deadLineBlock) {
        require(block.number <= deadLineBlock);
        _;
    }

    modifier onlyGovernor() {
        require(governingContract.governors(msg.sender));
        _;
    }

    modifier onlyMaintainer() {
        require(governingContract.maintainers(msg.sender));
        _;
    }

    modifier isValidCoin(uint coinID) {
        // check that coinID exists and that coin has not yet timed out
        require(coinID <= coloredCoinCount);
        require(coloredCoins[coinID].deadlineBlock > block.number);
        _;
    }

    modifier hasNoRequest(uint coinID) {
        require(!hasMintingRequest[msg.sender][coinID], "You have already a request running.");
        _;
    }

    modifier enoughBalance(uint coinID, uint amount) {
        require(coloredCoins[coinID].balanceOf[msg.sender] >= amount, "You do not have enough tokens.");
        _;
    }

    // Functions
    constructor(address _governingContract) public {
        governingContract = Governing(_governingContract);
    }

    function setup(address _cbdcContract) public onlyMaintainer {
        cbdcContract = CBDC(_cbdcContract);
    }

    // -------------- CCBDC Creation ----------------------------
    //STEP 1: Central Bank creates a new coin
    function createNewCoin(uint _color, uint[] memory _shades, uint256 _supply, uint _deadline) public onlyGovernor {
        // Create nee colored coin
        ColoredCoin memory newCC = ColoredCoin({
            creator:       msg.sender,
            color:         _color,
            shades:        _shades,
            supply:        _supply,
            deadlineBlock: block.number + _deadline
        });

        coloredCoinCount++;
        coloredCoins[coloredCoinCount] = newCC;

        emit CoinCreation(msg.sender, coloredCoinCount, _supply);
    }

    function showCoinInfo(uint coinID) public returns(address, uint[] memory, uint256, uint) {
        ColoredCoin memory coin = coloredCoins[coinID];
        return (coin.creator, coin.shades, coin.supply, coin.deadlineBlock);
    }

    // -------------- CCBDC Issuance ----------------------------
    //STEP 2: User requests specific CCBDC amount with a dedicated minting request
    function requestCoin(uint _coinID, uint256 _amount) public isValidCoin(_coinID) hasNoRequest(_coinID) {
        MintingRequest memory newMR = MintingRequest({
            coinID: _coinID,
            sender: msg.sender,
            approved: false,
            amount: _amount
        });

        mintingRequestCount++;
        mintingRequests[mintingRequestCount] = newMR;

        // prevent request spamming by limiting request for specific coinID on one
        hasMintingRequest[msg.sender][_coinID] = true;
    }

    //STEP 3: CCBDC minting requested amount (if approved) and transferring it to the users wallet
    function approveMintingRequest(uint requestID) public onlyGovernor {
        MintingRequest memory request = mintingRequests[requestID];
        // check if request has already been approved and if coin deadline is not exceeded and if there is still enough supply
        require(!request.approved, "Request is already approved");
        require(coloredCoins[request.coinID].deadlineBlock >= block.number, "Colored Coin has already timed out.");
        require(coloredCoins[request.coinID].supply >= request.amount, "Not enough supply left.");

        // approve request
        mintingRequests[requestID].approved = true;

        // update balances
        coloredCoins[request.coinID].supply -= request.amount;
        coloredCoins[request.coinID].balanceOf[request.sender] += request.amount;

        emit Approval(request.coinID, request.sender, request.amount);
    }

    // --------------- TRADING PHASE! ----------------------------
    //STEP 4: user spends CCBDC and if receiver is of same shade (merchant code) as coin, the coin gets transferred to a general purpose CBDC
    function transfer(uint coinID, address to, uint tokens) public enoughBalance(coinID, tokens) {
        // check if coin and receiver have same shades
        bool hasSameShade = false;
        for(uint i; i < coloredCoins[coinID].shades.length; i++) {
            uint shade = coloredCoins[coinID].shades[i];
            if(shade == cbdcContract.isMerchant(to)) {
                hasSameShade = true;
            }
        }

        // update balances
        coloredCoins[coinID].balanceOf[msg.sender] -= tokens;

        if(hasSameShade) {
            cbdcContract.convert(msg.sender, to, tokens);
            emit Conversion(coinID, msg.sender, to, tokens);
        } else {
            coloredCoins[coinID].balanceOf[to] += tokens;
            emit Transfer(coinID, msg.sender, to, tokens);
        }
    }

    function balanceOf(uint coinID, address query) public returns(uint256) {
        return coloredCoins[coinID].balanceOf[query];
    }
}

