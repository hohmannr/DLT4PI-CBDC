FROM quorum-node

CMD geth --allow-insecure-unlock --datadir data --nodiscover --syncmode full --verbosity 5 --networkid $NETWORK_ID --rpc --rpcaddr 0.0.0.0 --rpcport $RPC_PORT --rpcapi admin,db,eth,debug,mine,net,shh,txpool,personal,web3,quorum,istanbul --emitcheckpoints --port $GETH_PORT

