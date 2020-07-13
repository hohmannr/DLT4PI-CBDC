# Contracts

These contracts are the core of blockchain, they provide utility for governance, they define how CBDC is created and transferred and they provide an untamperable creation tool for colored coins.

## Governing.sol

This represents the governing contract used by governor-nodes to vote in/out other node-types or to blacklist addresses and prevent them from spending/receiving CBDC.

### Important properties

```
mapping(address => bool) public governors;
```
Monitors if address is a governor.

```
mapping(address => bool) public maintainers;
```
Monitors if address is maintainer.

```
mapping(address => bool) public observers;
```
Monitors if address is obsever.

```
mapping(address => bool) public bankers;
```
Monitors if address is banker.

```
mapping(address => bool) public blacklist;
```
Monitors if address is blacklisted.

### Important methods

```
function makeProposal(address _candidate, NodeType _asType, ProposalType _proposalType)
```
Allows a governor-node to propose a candidate to be voted in/out of a node-type role. Total votes needed for a proposal to get accepted are `governorCount / 2 + 1`.

```
function vote(uint _proposalID) public
```
Allows all governors to vote on a previously made proposal. Automatically decides on each vote if proposal was succesful and if so, adds the candidate to the respective node-type role.

## CBDC.sol

This represents an ERC20-like (it does not need certain ERC20-functionality) token. With governor-nodes having the right to mint new coins and distribute them to banker-nodes and banker-nodes having the ability to allocate new accounts/addresses with a certain amount of CBDC (which is limited by the banker's supply), aswell as providing a shade/merchantcode as metadata to each allocated account/address.

### Important properties

```
mapping(address => uint256) public balanceOf;
```
Monitors the balance of a certain address.

```
mapping(address => uint256) public supplyOf;
```
Monitors the supply of a certain banker.

```
mapping(address => uint)    public isMerchant;
```
Monitors the metadata (shade/merchantcode) for a certain address.

### Important methods

```
function transfer(address to, uint tokens) public enoughBalance(tokens)
```
Transfer CBDC from one address to another, if the target address is a banker, it gets added to its supply.

```
function mint(address to, uint256 amount) public onlyGovernor
```
Allows governor to mint new CBDC and allocate it directly to a banker.

```
function allocate(address to, uint256 amount, uint merchantCode)
```
Allows bankers to allocate money for a certain address and to define this address' shade/merchantcode.

```
function convert(address from, address to, uint amount)
```
Allows the CCBDC.sol contract to convert colored coins into CBDC.

## CCBDC.sol

This represents a coin factory for colored coins. Colored coins are described by a color and a shades/merchantcodes, every colored coin is only spendable for a certain amount time, to make sure that they get spent for what they are intended. Once a colored coin gets spent to an address with the same shade, it converts itself back to a general CDBC.

### Important properties

```
mapping(uint => ColoredCoin) public coloredCoins;
```
Monitors every created colored coin.

```
mapping(uint => MintingRequest) public mintingRequests;
```
Monitors every proposed minting request.

```
mapping(address => mapping(uint => bool)) public hasMintingRequest;
```
Monitors minting requests for all coins of a certain address to prevent two requests for the same coin.

### Important methods

```
function balanceOf(uint coinID, address query) public returns(uint256)
```
Monitors the balance of an address of a given colored coin.

```
function createNewCoin(uint _color, uint[] memory _shades, uint256 _supply, uint _deadline)
```
Allows governors to create a new colored coin, which times out after `_deadline` amount of blocks after its creation and has a supply of `_supply` many token.

```
function showCoinInfo(uint coinID) public returns(address, uint[] memory, uint256, uint)
```
Returns info like creator, color and shades of colored coin with `coinID`.

```
function requestCoin(uint _coinID, uint256 _amount)
```
Allows anyone to create a minting request to receive colored coin of id `_coinID`.

```
function approveMintingRequest(uint requestID)
```
Allows governors to approve a minting request, thus handing over the requested amount if the colored coin has enough supply left.

```
function transfer(uint coinID, address to, uint tokens) public enoughBalance(coinID, tokens)
```
Makes colored coin tradable and automatically converts colored coin to general CBDC if recipient has the same shade as the colored coin.





