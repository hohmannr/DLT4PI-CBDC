package kraken

import(
    _ "fmt"
    "bytes"
    "net/http"
    "encoding/json"
    "errors"

    log "github.com/sirupsen/logrus"
    "github.com/ethereum/go-ethereum/common/hexutil"
)

const(
    RPC_VERSION = "2.0"
)

type RPCClient struct {
    Url     string
    Port    string
    ChainID uint
}

type RPCRequest struct {
    Jsonrpc string        `json:"jsonrpc"`
    Method  string        `json:"method"`
    Params  []interface{} `json:"params"`
    ChainID uint          `json:"id"`
}

type RPCResponse struct {
    Jsonrpc string           `json:"jsonrpc"`
    ChainID uint             `json:"id"`
    Result  interface{}      `json:"result"`
    Method  string
    Error   RPCResponseError `json:"error"`
}

type RPCResponseError struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
}

type JsonBlock struct {
    Difficulty       string   `json:"difficulty"`
    Extra            string   `json:"extraData"`
    GasLimit         string   `json:"gasLimit"`
    GasUsed          string   `json:"gasUsed"`
    Hash             string   `json:"hash"`
    LogsBloom        string   `json:"logsBloom"`
    Miner            string   `json:"miner"`
    MixHash          string   `json:"mixHash"`
    Nonce            string   `json:"nonce"`
    Number           string   `json:"number"`
    ParentHash       string   `json:"parentHash"`
    ReceiptRoot      string   `json:"receiptRoot"`
    Sha3Uncles       string   `json:"sha3Uncles"`
    Size             string   `json:"size"`
    StateRoot        string   `json:"stateRoot"`
    Timestamp        string   `json:"timestamp"`
    TotalDifficulty  string   `json:"totalDifficulty"`
    Transactions     []string `json:"transactions"`
    TransactionsRoot string   `json:"transactionsRoot"`
    Uncles           []string `json:"uncles"`
}

type JsonBlockWithTx struct {
    Difficulty       string   `json:"difficulty"       bson:"difficulty,omitempty"`
    Extra            string   `json:"extraData"        bson:"extraData,omitempty"`
    GasLimit         string   `json:"gasLimit"         bson:"gasLimit,omitempty"`
    GasUsed          string   `json:"gasUsed"          bson:"gasUsed,omitempty"`
    Hash             string   `json:"hash"             bson:"hash,omitempty"`
    LogsBloom        string   `json:"logsBloom"        bson:"logsBloom,omitempty"`
    Miner            string   `json:"miner"            bson:"miner,omitempty"`
    MixHash          string   `json:"mixHash"          bson:"mixHash,omitempty"`
    Nonce            string   `json:"nonce"            bson:"nonce,omitempty"`
    Number           string   `json:"number"           bson:"number,omitempty"`
    ParentHash       string   `json:"parentHash"       bson:"parentHash,omitempty"`
    ReceiptRoot      string   `json:"receiptRoot"      bson:"receiptRoot,omitempty"`
    Sha3Uncles       string   `json:"sha3Uncles"       bson:"sha3Uncles,omitempty"`
    Size             string   `json:"size"             bson:"size,omitempty"`
    StateRoot        string   `json:"stateRoot"        bson:"stateRoot,omitempty"`
    Timestamp        string   `json:"timestamp"        bson:"timestamp,omitempty"`
    TotalDifficulty  string   `json:"totalDifficulty"  bson:"totalDifficulty,omitempty"`
    Transactions     []*JsonTx `json:"transactions"    bson:"transactions,omitempty"`
    TransactionsRoot string   `json:"transactionsRoot" bson:"transactionsRoot,omitempty"`
    Uncles           []string `json:"uncles"           bson:"uncles,omitempty"`
}

type JsonTx struct {
    BlockHash   string `bson:"blockHash"        json:"blockHash"`
    BlockNumber string `bson:"blockNumber"      json:"blockNumber"`
    From        string `bson:"from"             json:"from"`
    Gas         string `bson:"gas"              json:"gas"`
    GasPrice    string `bson:"gasPrice"         json:"gasPrice"`
    Hash        string `bson:"hash"             json:"hash"`
    Input       string `bson:"input"            json:"input"`
    Nonce       string `bson:"nonce"            json:"nonce"`
    To          string `bson:"to"               json:"to"`
    Index       string `bson:"transactionIndex" json:"transactionIndex"`
    Value       string `bson:"value"            json:"value"`
    V           string `bson:"v"                json:"v"`
    R           string `bson:"r"                json:"r"`
    S           string `bson:"s"                json:"s"`
}

func (b *JsonBlock) fromMap(blockMap interface{}) error {
    jsonMap, err := json.Marshal(blockMap)
    if err != nil {
        return err
    }
    err = json.Unmarshal(jsonMap, b)
    if err != nil {
        return err
    }

    return nil
}

func (b *JsonBlockWithTx) fromMap(blockMap interface{}) error {
    jsonMap, err := json.Marshal(blockMap)
    if err != nil {
        return err
    }
    err = json.Unmarshal(jsonMap, b)
    if err != nil {
        return err
    }

    return nil
}

func (t *JsonTx) fromMap(blockMap interface{}) error {
    jsonMap, err := json.Marshal(blockMap)
    if err != nil {
        return err
    }
    err = json.Unmarshal(jsonMap, t)
    if err != nil {
        return err
    }
    
    return nil
}

func (e *RPCResponseError) Error() (string) {
    return e.Message
}

func (c *RPCClient) FormRequest(method string, params []interface{}) (*RPCRequest) {
    req:= &RPCRequest{RPC_VERSION, method, params, c.ChainID}
    return req
}

func (c *RPCClient) PostRequest(req *RPCRequest) (*RPCResponse, error) {
    reqBody, err:= json.Marshal(req)
    if err != nil {
        return nil, err
    }
    
    resp, err := http.Post(c.Url + ":" + c.Port, "application/json", bytes.NewBuffer(reqBody))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    //r, _ := ioutil.ReadAll(resp.Body)
    //fmt.Println(string(r))

    var result RPCResponse
    err = json.NewDecoder(resp.Body).Decode(&result)
    if err != nil {
        return nil, err
    }
    if result.Result == nil {
        return nil, errors.New("No Result came back")
    }
    result.Method = req.Method

    // check for returned error message
    if result.Error.Message != "" {
        return nil, errors.New(result.Error.Message)
    }
    
    return &result, nil
}

func (c *RPCClient) GetBlockByNumber(i uint64) (*JsonBlock, error) {
    params := []interface{}{hexutil.EncodeUint64(i), false}
    req := c.FormRequest("eth_getBlockByNumber", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    // try to unmarshal response
    var block JsonBlock
    block.fromMap(resp.Result)

    return &block, nil
}

func (c *RPCClient) GetBlockByNumberWithTx(i uint64) (*JsonBlockWithTx, error) {
    params := []interface{}{hexutil.EncodeUint64(i), true}
    req := c.FormRequest("eth_getBlockByNumber", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    // try to unmarshal response
    var block JsonBlockWithTx
    block.fromMap(resp.Result)

    return &block, nil
}

func (c *RPCClient) GetBlockByHash(hash string) (*JsonBlock, error) {
    params := []interface{}{hash, false}
    req := c.FormRequest("eth_getBlockByHash", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    var block JsonBlock
    block.fromMap(resp.Result)

    return &block, nil
}

func (c *RPCClient) GetBlockByHashWithTx(hash string) (*JsonBlockWithTx, error) {
    params := []interface{}{hash, true}
    req := c.FormRequest("eth_getBlockByHash", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    var block JsonBlockWithTx
    block.fromMap(resp.Result)

    return &block, nil
}

func (c *RPCClient) BlockNumber() (uint64, error) {
    params := []interface{}{}
    req := c.FormRequest("eth_blockNumber", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return 0, err
    }

    heightStr, ok := resp.Result.(string)
    if !ok {
        return 0, errors.New("Could not convert heightStr from interface{} to string.")
    }
    height, err := hexutil.DecodeUint64(heightStr)
    if err != nil {
        return 0, err
    }

    return height, nil
}

func (c *RPCClient) GetLatestBlocks(n uint64) ([]*JsonBlock, error) {
    blockHeight, err := c.BlockNumber()
    if err != nil {
        return nil, err
    }

    var blocks = make([]*JsonBlock, n)
    var currN uint64
    for i := uint64(0); i < n; i++ {
        currN = blockHeight - i
        block, err := c.GetBlockByNumber(currN)
        if err != nil {
            return nil, err
        }
        blocks[i] = block
    }

    return blocks, nil
}

func (c *RPCClient) GetLatestBlocksWithTx(n uint64) ([]*JsonBlockWithTx, error) {
    blockHeight, err := c.BlockNumber()
    if err != nil {
        return nil, err
    }

    var blocks = make([]*JsonBlockWithTx, n)
    var currN uint64
    for i := uint64(0); i < n; i++ {
        currN = blockHeight - i
        block, err := c.GetBlockByNumberWithTx(currN)
        if err != nil {
            return nil, err
        }
        blocks[i] = block
    }

    return blocks, nil
}

func (c *RPCClient) GetTxByHash(hash string) (*JsonTx, error) {
    params := []interface{}{hash}
    req := c.FormRequest("eth_getTransactionByHash", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    var tx JsonTx
    tx.fromMap(resp.Result)

    return &tx, nil
}

func (c *RPCClient) GetValidatorsFromBlockByNumber(i uint64) ([]string, error) {
    params := []interface{}{hexutil.EncodeUint64(i)}
    req := c.FormRequest("istanbul_getValidators", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    // type conversion
    validatorInterfaces, ok := resp.Result.([]interface{})
    if !ok {
        log.Fatalln("Could not convert result to validator []interface{}.")
        return nil, errors.New("Could not convert result to []interface{}.")
    }
    validators := make([]string, len(validatorInterfaces))
    for i, v := range validatorInterfaces {
        validators[i] = v.(string)
    }

    return validators, nil
}

func (c *RPCClient) GetValidatorsFromBlockByHash(hash string) ([]string, error) {
    params := []interface{}{hash}
    req := c.FormRequest("istanbul_getValidatorsAtHash", params)
    resp, err := c.PostRequest(req)
    if err != nil {
        return nil, err
    }

    // type conversion
    validatorInterfaces, ok := resp.Result.([]interface{})
    if !ok {
        log.Fatalln("Could not convert result to validator []interface{}.")
        return nil, errors.New("Could not convert result to []interface{}.")
    }
    validators := make([]string, len(validatorInterfaces))
    for i, v := range validatorInterfaces {
        validators[i] = v.(string)
    }

    return validators, nil
}

