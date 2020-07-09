pragma solidity >=0.6.0 <0.7.0;

contract Governing {
    
    mapping(address => bool) public governors;
    uint public governorCount;
    mapping(address => bool) public maintainers;
    uint public maintainerCount;
    mapping(address => bool) public observers;
    uint public observerCount;
    mapping(address => bool) public bankers;
    uint public bankerCount;
    mapping(address => bool) public blacklist;
    uint public blacklistCount;

    constructor(address[] memory _governors, address[] memory _maintainers, address[] memory _observers, address[] memory _bankers, address[] memory _blacklist) public {
        
        for(uint i = 0; i < _governors.length; i++) {
            governors[_governors[i]] = true;
            governorCount++;
        }
        for(uint i = 0; i < _maintainers.length; i++) {
            maintainers[_maintainers[i]] = true;
            maintainerCount++;
        }
        for(uint i = 0; i < _observers.length; i++) {
            observers[_observers[i]] = true;
            observerCount++;
        }
        for(uint i = 0; i < _bankers.length; i++) {
            bankers[_bankers[i]] = true;
            bankerCount++;
        }
        for(uint i = 0; i < _blacklist.length; i++) {
            blacklist[_blacklist[i]] = true;
            blacklistCount++;
        }
    }

    enum NodeType {
        Governor,
        Maintainer,
        Observer,
        Banker,
        Blacklist
    }

    enum ProposalType {
        VoteIn,
        VoteOut
    }

    struct Proposal {
        address candidate;
        ProposalType t;
        NodeType asType;
        uint deadlineBlock;
        uint voteCount;
        uint voteThreshold;
        bool accepted;
        mapping(address => bool) hasVoted;
    }

    mapping(uint => Proposal) public proposals;
    uint proposalCount;

    // Utility functions
    function addNode(address node, NodeType t) internal {
        if(t == NodeType.Governor) {
            governors[node] = true;
            governorCount++;
        } else if(t == NodeType.Maintainer) {
            maintainers[node] = true;
            maintainerCount++;
        } else if(t == NodeType.Observer) {
            observers[node] = true;
            observerCount++;
        } else if(t == NodeType.Banker) {
            bankers[node] = true;
            bankerCount++;
        } else if(t == NodeType.Blacklist) {
            blacklist[node] = true;
            blacklistCount++;
        }
    }

    function removeNode(address node, NodeType t) internal {
        if(t == NodeType.Governor) {
            delete governors[node];
            governorCount--;
        } else if(t == NodeType.Maintainer) {
            delete maintainers[node];
            maintainerCount--;
        } else if(t == NodeType.Observer) {
            delete observers[node];
            observerCount--;
        } else if(t == NodeType.Banker) {
            delete bankers[node];
            bankerCount--;
        } else if(t == NodeType.Blacklist) {
            delete blacklist[node];
            blacklistCount--;
        }
    }

    event NewProposal(
        uint time,
        uint indexed proposalID
    );

    function makeProposal(address _candidate, NodeType _asType, ProposalType _proposalType) public {
        // make sure that only governors can propose
        require(governors[msg.sender], "You must be a governor to make a proposal.");
        // make sure that address is not already a node
        if(_proposalType == ProposalType.VoteIn) {
            require(!governors[_candidate] && !observers[_candidate] && !maintainers[_candidate] && !bankers[_candidate], "Candidate cannot be member of any node type.");
        } else {
            if(_asType == NodeType.Banker) {
                require(bankers[_candidate], "Candidate must be node of given type first to be able to be voted out.");
            } else if(_asType == NodeType.Governor) {
                require(governors[_candidate], "Candidate must be node of given type first to be able to be voted out.");
            } else if(_asType == NodeType.Maintainer) {
                require(maintainers[_candidate], "Candidate must be node of given type first to be able to be voted out.");
            } else if(_asType == NodeType.Observer) {
                require(observers[_candidate], "Candidate must be node of given type first to be able to be voted out.");
            } else if(_asType == NodeType.Blacklist) {
                require(blacklist[_candidate], "Candidate must be node of given type first to be able to be voted out.");
            }
        }

        // create new proposal
        Proposal memory proposal = Proposal({
            candidate:      _candidate,
            t:              _proposalType,
            asType:         _asType,
            deadlineBlock:  block.number + 64,
            voteCount:      0,
            voteThreshold:  governorCount / 2 + 1,
            accepted:       false
        });
        
        proposalCount++;
        proposals[proposalCount] = proposal;

        emit NewProposal(now, proposalCount);
    }

    event NewVote(
        uint time,
        uint indexed proposalID,
        uint voteCount
    );

    function vote(uint _proposalID) public {
        require(governors[msg.sender], "You must be a governor to make a proposal.");
        Proposal storage proposal = proposals[_proposalID];
        require(!proposal.accepted, "Candidate has already been accepted.");
        require(block.number <= proposal.deadlineBlock, "Proposal timed out.");
        require(!proposal.hasVoted[msg.sender], "You have already voted for this proposal.");

        proposal.voteCount++;
        proposal.hasVoted[msg.sender] = true;

        emit NewVote(now, _proposalID, proposal.voteCount);

        // check if votes have surpassed the threshold
        if(proposal.voteCount > proposal.voteThreshold) {
            proposal.accepted = true;

            if(proposal.t == ProposalType.VoteIn) {
                addNode(proposal.candidate, proposal.asType);
            } else {
                removeNode(proposal.candidate, proposal.asType);
            }
        }
    }
}

