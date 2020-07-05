package chain

import(
    "fmt"
    "context"
    "math/big"
    "os"

    log "github.com/sirupsen/logrus"
    "github.com/ethereum/go-ethereum/ethclient"
    "github.com/ethereum/go-ethereum/common"
    "github.com/ethereum/go-ethereum/core/types"
)

type Connection struct {
    client *ethclient.Client
}

func NewConnection() (*Connection) {
    url := os.Getenv("GETH_RPC_URL")
    if url == "" {
        log.Fatal("GETH_RPC_URL environment variable not set. Please set it.")
    }

    client, err := ethclient.Dial(url)
    if err != nil {
        log.Fatal(fmt.Sprintf("Could not connect to, '%s'", url))
    }

    conn := &Connection{client}
    return conn
}

func (conn *Connection) GetChainID() (*big.Int, error) {
    return conn.client.ChainID(context.Background())
}

func (conn *Connection) GetBlockByHash(hash common.Hash) (*types.Block, error) {
    blk, err := conn.client.BlockByHash(context.Background(), hash)
    if err != nil {
        return nil, err
    }
    header, err := conn.client.HeaderByHash(context.Background(), hash)
    if err != nil {
        return nil, err
    }

    return types.NewBlockWithHeader(header), nil
}

func (conn *Connection) GetBlockByNumber(n *big.Int) (*types.Block, error) {
    blk, err := conn.client.BlockByNumber(context.Background(), n)
    if err != nil {
        return nil, err
    }
    header, err := conn.client.HeaderByNumber(context.Background(), n)
    if err != nil {
        return nil, err
    }

    return types.NewBlockWithHeader(header), nil
}

func (conn *Connection) GetLatestBlock() (*types.Block, error) {
    return conn.client.BlockByNumber(context.Background(), nil)
}

func (conn *Connection) GetBlockNumber() (*big.Int, error) {
    blk, err := conn.GetLatestBlock()
    if err != nil {
        return nil, err
    }
    return blk.Number(), nil
}

func (conn *Connection) GetLatestBlocks(n uint64) ([]*types.Block, error) {
    blk_num, err := conn.GetBlockNumber()
    if err != nil {
        return nil, err
    }

    // retrieving the latest blocks
    blks := make([]*types.Block, n)
    for i := uint64(0); i < n; i++ {
        curr_i := big.NewInt(0).Sub(blk_num, new(big.Int).SetUint64(i))
        blk, err := conn.GetBlockByNumber(curr_i)
        if err != nil {
            return nil, err
        }
        blks[i] = blk
    }
    return blks, nil
}

func (conn *Connection) GetTransactionByHash(txHash common.Hash) (*types.Transaction, bool, error) {
    return conn.client.TransactionByHash(context.Background(), txHash)
}
