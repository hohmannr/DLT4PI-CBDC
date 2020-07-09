package database

import(
    "context"
    "fmt"

    "github.com/hohmannr/blockchain-explorer/kraken"
    "go.mongodb.org/mongo-driver/bson/primitive"
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
)

func EstimateDocuments(ctx context.Context, database *mongo.Database) (int64, error) {
    collection := database.Collection("blocks")
    count, err := collection.EstimatedDocumentCount(ctx)
    if err != nil {
        return 0, err
    }
    fmt.Printf("Count: %v\n", count)

    return count, err
}

type BsonBlock struct {
    ID primitive.ObjectID `json:"_id,omitempty" bson:"_id,omitempty"`
    Transactionss []primitive.ObjectID
    kraken.JsonBlockWithTx
}

type BsonTx struct {
    ID primitive.ObjectID `json:"_id,omitempty" bson:"_id,omitempty"`
    kraken.JsonTx
}

func (b BsonBlock) Save(ctx context.Context, database *mongo.Database) error {
    collection := database.Collection("blocks")
    _, err := collection.InsertOne(ctx, b)
    if err != nil {
        return err
    }

    return nil
}

func (t BsonTx) Save(ctx context.Context, database *mongo.Database) error {
    collection := database.Collection("transactions")
    _, err := collection.InsertOne(ctx, t)
    if err != nil {
        return err
    }

    return nil
}

func SyncFullBlockchain(ctx context.Context, rpc *kraken.RPCClient, database *mongo.Database) error {
    i := uint64(0)
    for {
        // print progress
        chainHeight, err := rpc.BlockNumber()
        if err != nil {
            return err
        }
        fmt.Println(fmt.Sprintf("%v", i) + "/" + fmt.Sprintf("%v", chainHeight))

        // check if snycronisation is done
        if i >= chainHeight {
            break
        } else {
            i++;
        }
        // get block and create new database entry
        block, err := rpc.GetBlockByNumberWithTx(i)
        if err != nil {
            return err
        }
        bsonBlock := BsonBlock{JsonBlockWithTx: *block}
        err = bsonBlock.Save(ctx, database)
        if err != nil {
            return err
        }

        // write transactions seperetly to find them more easily later
        for _, tx := range bsonBlock.Transactions {
            bsonTx := BsonTx{JsonTx: *tx}
            err := bsonTx.Save(ctx, database)
            if err != nil {
                return err
            }
        }
    }

    return nil
}

func SyncToLatestBlock(ctx context.Context, rpc *kraken.RPCClient, database *mongo.Database) error {

    i := uint64(0)
    for {
        chainHeight, err := rpc.BlockNumber()
        if err != nil {
            return err
        }
        fmt.Println(fmt.Sprintf("%v", i) + "/" + fmt.Sprintf("%v", chainHeight))

        // check if snycronisation is done
        if i >= chainHeight {
            break
        } else {
            i++;
        }
    }

    

    return nil
}

