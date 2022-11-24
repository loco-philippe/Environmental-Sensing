import { MongoClient } from "mongodb";
import { ESSearch } from "./essearch_javascript.js";
import pythonBridge from 'python-bridge';

const uri = "mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/?retryWrites=true&w=majority";
const client = new MongoClient(uri);
const python = pythonBridge();
 
python.ex`from observation import Observation`;
python.ex`from observation.essearch import ESSearch`;
//const obs = await python`Observation().json()`

async function run() {
  try {
    const database = client.db("test_obs");
    const coll = database.collection("observation_1");
    let srch = new ESSearch({collection: coll});
    //srch.addCondition('datation', new Date(2022, 0, 1), '>=');
    //srch.addCondition('datation', new Date(2022, 11, 32), '<=');
    srch.addCondition('property', 'PM25');
    //srch.addCondition(undefined, 'observation', '==', 'type');
    let result = await srch.execute(false, false);
    let result_json = await python`ESSearch(data = [Observation.from_obj(item) for item in ${result}]).execute(single = True).json()`;
    python.end();
    console.log(result_json);
  } finally {
    await client.close();
  }
}
run();