import { MongoClient } from "mongodb";
import { ESSearch } from "../essearch_javascript.js";

const uri = "mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/?retryWrites=true&w=majority";
const client = new MongoClient(uri);

async function run() {
  try {
    const database = client.db("test_obs");
    const coll = database.collection("observation_1");
    let srch = new ESSearch({collection: coll});
    srch.addCondition('datation', new Date(2022, 0, 1), '>=');
    //srch.addCondition('datation', new Date(2022, 11, 32), '<=');
    //srch.addCondition('property', 'PM25');
    //srch.addCondition(undefined, 'observation', '==', 'type');
    let result = await srch.execute({modecodec: 'dict'});
    console.log(result.data);
    // for (const date of result.data.datation.value) {console.log(date);} // n'a de sens que lorsque modecodec = 'dict', sinon provoque une erreur

    let data_array = [];
    for (const date of result.data.datation.value) {
      let count;
      if (Array.isArray(date.record)) {count = date.record.length;}
      else if (date.record === undefined || date.record === null) {count = 0;}
      else {count = 1;}
      data_array.push({'date':date.codec, 'count':count}) ;
    }
    console.log(data_array);
  } finally {
    await client.close();
  }
}
run();

/*
Pour exploiter les données, il faut que les colonnes soient reconstruites (mais seules celles qui sont utilisées ont besoin de l'être).

Ensuite, voir pour l'utilisation de d3js / Observable Plot sans passer par Observable hq pour le tracé de graphiques exploitables

+ création d'une API / interface utilisateur
*/
