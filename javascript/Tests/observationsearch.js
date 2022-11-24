//const { MongoClient } = require("mongodb");
import { MongoClient } from "mongodb";
import { ESSearch } from "../essearch_javascript.js";
const uri = "mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/?retryWrites=true&w=majority";
const client = new MongoClient(uri);

async function run() {
  try {
    const database = client.db("test_obs");
    const coll = database.collection("observation_1");
    let srch = new ESSearch({collection: coll});
    //srch.addCondition('datation', new Date(2022, 0, 1), '>=');
    //srch.addCondition('datation', new Date(2022, 11, 32), '<=');
    srch.addCondition('property', 'PM25');
    //srch.addCondition(undefined, 'observation', '==', 'type');
    console.log(srch.request);
    let result = srch.execute();
    console.log(result)
    //for await (const doc of result) {
    //  console.log(doc);
    //}
    /*const pipeline = [
      {'$match': {'type': {'$eq': 'observation'}}},
      {'$unwind': '$data.datation.value'},
      //{'$unwind': '$data.property.value'},
      //{'$set': {'_data.datation.value.codec': {'$cond': {'if': {'$eq': [{'$type': '$data.datation.value.codec'}, 'object']}, 'then': {'$objectToArray': '$data.datation.value.codec'}, 'else': {'v': '$data.datation.value.codec'}}}, '_data.property.value.codec': {'$cond': {'if': {'$eq': [{'$type': '$data.property.value.codec'}, 'object']}, 'then': {'$objectToArray': '$data.property.value.codec'}, 'else': {'v': '$data.property.value.codec'}}}}},
      //{'$match': {'_data.datation.value.codec.v': {'$gte': datetime.datetime(2022, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '$lte': datetime.datetime(2022, 12, 31, 0, 0, tzinfo=datetime.timezone.utc)}, '_data.property.value.codec.v': {'$eq': 'PM25'}}},
      {'$match': {'data.datation.value.codec': {'$gte': new Date(2022, 0, 1)}}},
      //{'$set': {'data.datation.value': ['$data.datation.value'], 'data.property.value': ['$data.property.value']}},
      {'$set': {'data.datation.value': ['$data.datation.value']}},
      {'$project': {'_id': 0, '_data': 0, 'information': 0}}
    ];
    const aggCursor = coll.aggregate(pipeline);
    for await (const doc of aggCursor) {
      console.log(doc);
    }*/
  } finally {
    await client.close();
  }
}
run().catch(console.dir); //Affiche les propriétés de l'élément en cas d'erreur