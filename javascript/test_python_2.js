import { MongoClient } from "mongodb";
import { ESSearch } from "./essearch_javascript.js";

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
    let result = await srch.execute();
    console.log(result);
  } finally {
    await client.close();
  }
}
run();