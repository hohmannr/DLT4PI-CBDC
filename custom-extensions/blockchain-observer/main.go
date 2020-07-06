package main

import(
    _ "fmt"
    "context"
    "time"
    "net/http"

    "github.com/hohmannr/blockchain-explorer/kraken"
    "github.com/hohmannr/blockchain-explorer/database"
    "github.com/gorilla/mux"
    log "github.com/sirupsen/logrus"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

const(
    RPC_URL  = "http://127.0.0.1"
    RPC_PORT = "22000"
    CHAIN_ID = 10
    MONGODB_URI = "mongodb://127.0.0.1:27017"
    MONGODB_NAME = "observer"
)

func main() {
    // Connect to geth RPC
    rpcClient := &kraken.RPCClient{RPC_URL, RPC_PORT, CHAIN_ID}
    
    // Connect to database
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    mongoClient, err := mongo.NewClient(options.Client().ApplyURI(MONGODB_URI))
    if err != nil {
        log.Fatalln(err)
    }
    err = mongoClient.Connect(ctx)
    if err != nil {
        log.Fatal(err)
    }
    mongoDB := mongoClient.Database(MONGODB_NAME)

    // Routers
    router := mux.NewRouter().StrictSlash(true)

    err = database.SyncFullBlockchain(ctx, rpcClient, mongoDB)
    if err != nil {
        log.Fatal(err)
    }
    http.ListenAndServe(":8080", router)
}

