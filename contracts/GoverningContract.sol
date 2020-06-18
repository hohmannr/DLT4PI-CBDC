pragma solidity ^0.6.1;

contract GoverningContract{
    
     //Structure for the address to be voted on
    struct Candidate{
        uint id;
        address addresses;
        uint voteCount;
        string nodetype ;
    }
    
    
    struct GovernorNode{
        uint id;
        address addresses;
        bool voted;  //Only Governer node has the right to vote.
        
    }
     struct ObserverNode{
        uint id;
        address addresses;
       
        
    }
     struct MaintainerNode{
        uint id;
        address addresses;
       
        
    }
     struct  BankerNode{
        uint id;
        address addresses;
       
    }
    
    //Struture for global list of addresses(can contain Governers,Maintainers,Bankers and Obeservers)
    struct AddressList{
        uint id;
        address addresses;
        string nodetype ;
    }
    
    //mapping used to fetch details of Candidate by using id and each node by using address
    mapping(uint => Candidate) public  candidates;
    //Fetch GovernorNode
    mapping(address => GovernorNode) public Governors;
     //Fetch ObserverNode
    mapping(address => ObserverNode) public Observers;
      //Fetch BankerNode
    mapping(address => BankerNode) public Bankers;
      //Fetch MaintainerNode
    mapping(address => MaintainerNode) public Maintainers; 

    //Mapping used get address using id 
    mapping(uint => AddressList) private AddressLists;
   
  
    uint private candidatesCount;
    uint private addresscount;
    uint public governorCount;
    uint public observerCount;
    uint public bankerCount;
    uint public maintainerCount;
    uint private votingThreshold=50;  //number between 0 to 100 to define the percentage of governer node voting threshold
    
    
    constructor() public {
        addCandidate(0xfa047D882c622878185BD50bf385e7644EF52BF9,"observer");
        addGovenerNode(0xdD870fA1b7C4700F2BD7f44238821C26f7392148);
        addGovenerNode(0x583031D1113aD414F02576BD6afaBfb302140225);
        addGovenerNode(0x4B0897b0513fdC7C541B6d9D7E929C4e5364D2dB);
        addGovenerNode(0x43AA152cdd3A691e2190711854B3c40Df1b90596);
        addGovenerNode(0x9aEc6f6dbCB0f8B92C1D95609f107739a5E4995A);
        addGovenerNode(0x94Cb5224c887a934d9db5B3413bfb6C87D0a277C);
    }
    

    //Functions to add each address to particular node type
    function addCandidate (address _address ,string memory _nodetype) public {
        candidatesCount ++;
        candidates[candidatesCount] = Candidate(candidatesCount,_address, 0,_nodetype);
    }
    
   function addGovenerNode(address _governerAddress) private {   
        governorCount++;
        Governors[_governerAddress] = GovernorNode(governorCount,_governerAddress, false);
        addtoAddressList(_governerAddress,"governer");
    }
    
    function addOberverNode(address _observerAddress) private{
        observerCount++;
        Observers[_observerAddress] = ObserverNode(observerCount,_observerAddress);
    }
    
    function addMaintainerNode(address _maintainerAddress) private {
        maintainerCount++;
        Maintainers[_maintainerAddress] = MaintainerNode(maintainerCount,_maintainerAddress);
    }

    function addBankerNode(address _bankerAddress) private{
        bankerCount++;
        Bankers[_bankerAddress] = BankerNode(bankerCount,_bankerAddress);
    }
    function addtoAddressList(address _address,string memory  nodetype) private {
        addresscount++;
        AddressLists[addresscount] = AddressList(addresscount,_address,nodetype);
    }
    
    //Common function for Governer Addresses to vote 
    function Vote (uint _candidateId) public {

        // check if it is a Governor address
        require(
            Governors[msg.sender].addresses != address(0) ,
            "Only Governers can give right to vote."
        );
        // check if it is already voted
        require(
            !Governors[msg.sender].voted,
            "The address has already voted."
        );

        // check if it is  a valid candidate
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate.");

        //mark the vote against the Governer address
        Governors[msg.sender].voted=true;

        //  update candidate vote Count
        candidates[_candidateId].voteCount ++;
 
    }
    
    //Function to Count the votes to check if the address can be added to a particular node
    function CheckAddAddressVote (uint _candidateId) public {
        
        require(candidates[_candidateId].voteCount > ( governorCount *votingThreshold / 100 ), "address didnot get majority vote");
        
        string memory nodetype=candidates[_candidateId].nodetype;
        
        if(keccak256(abi.encodePacked((nodetype)))==keccak256(abi.encodePacked(("observer")))){
            
            addOberverNode(candidates[_candidateId].addresses);
        } 

        else if(keccak256(abi.encodePacked((nodetype)))==keccak256(abi.encodePacked(("maintainer")))){
        
            addMaintainerNode(candidates[_candidateId].addresses);
        
        }

        else if(keccak256(abi.encodePacked((nodetype)))==keccak256(abi.encodePacked(("banker")))){
            
            addBankerNode(candidates[_candidateId].addresses);
            
        }   
        
    }
    
    //Function to set the voted variable to false in GovernerNodes
    function ResetVote () public {                        
        for ( uint i=0 ;i < addresscount;i++)   
        {        
            address _address =AddressLists[i].addresses;
            Governors[_address].voted=false;
        }

    }

    //Function to Count the votes to check if the address can be removed to a particular node 
    function CheckRemoveAddressVote (uint _candidateId,string memory nodetype) public {

        require(candidates[_candidateId].voteCount > ( governorCount *votingThreshold / 100 ), "address didnot get majority vote"); 
        
        address candidate_address =candidates[_candidateId].addresses;
        
        if(keccak256(abi.encodePacked((nodetype)))==keccak256(abi.encodePacked(("observer")))) 
        {   
            delete Governors[candidate_address];           
            observerCount--;            
        } 

        else if(keccak256(abi.encodePacked((nodetype)))==keccak256(abi.encodePacked(("maintainer")))) 
        {
            delete Maintainers[candidate_address];
            maintainerCount--;
        }

        else if(keccak256(abi.encodePacked((nodetype)))==keccak256(abi.encodePacked(("banker")))) 
        {
            delete Bankers[candidate_address];
            bankerCount--;
        }   
       
    }

}
