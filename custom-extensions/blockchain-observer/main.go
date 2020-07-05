package main

import(
    "fmt"
    "os"
    "html"
    "net/http"
    "encoding/json"

    _ "github.com/sirupsen/logrus"
    _ "github.com/gorilla/mux"

    "github.com/hohmannr/blockchain-explorer/chain"
    _ "github.com/ethereum/go-ethereum/common"
)

func main() {
    port := os.Getenv("BLOCKEXPLORER_PORT")
    if port == "" {
        port = "8000"
    }

    // hash := common.HexToHash("0x98aa8c2dd8b7fa0c950157c491b42784ddff9183")
    geth := chain.NewConnection()
    defer geth.Close()

    blk, _ := geth.GetBlockByNumber(123)
    jsonBlk, _ := json.Marshal(blk)
    fmt.Println(string(jsonBlk))
}

func serveDashboard(w http.ResponseWriter, r *http.Request) {
    fmt.Fprint(w, "Hello", html.EscapeString(r.URL.Path))
}
