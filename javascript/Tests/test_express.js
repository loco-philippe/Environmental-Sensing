import http from 'http';
import url from 'url';
import express from 'express';
import {JSDOM} from "jsdom"; // On ne peut pas se passer de jsdom si Observable Plot est côté serveur.
// -> Pour améliorer la rapidité, Observable Plot doit être côté client donc jsdom n'est pas nécessaire.
import { MongoClient } from "mongodb";
import { emptyRequest, ESSearch} from "../essearch_javascript.js";

let jsdom = await JSDOM.fromFile("html_initial.html");
const app = express();
app.use(express.json());

app.get('/', (req, res) => {
  res.writeHead(200, {'Content-Type': 'text/html'});
  let html = jsdom.serialize();
  res.end(html);
  console.log('get');
});

app.post('/', async function (req, res) {
  /* Problème : Requête exécutée jusqu'au bout même quand il y en a d'autre après, alors que le résultat n'est plus
  nécessaire et ne sera de toute façon pas lu. */
  let client, database, collection;
  console.log(req.body);
  if (req.body.request_type === 'mongo-validation' || req.body.request_type === 'mongo-validation-namelist') {
    try {
      client = new MongoClient(req.body.uri);
      database = client.db(req.body.database_name);
      collection = database.collection(req.body.collection_name);
      if (req.body.request_type === 'mongo-validation-namelist') {
        res.writeHead(200, {'Content-Type': 'application/json'});
        let empty = JSON.stringify(await emptyRequest(collection));
        console.log(empty);
        res.end(empty);
      } else {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end('mongo_data is valid');
      }
    } catch {
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end('mongo_data is invalid');
    }
  } else if (req.body.request_type === 'execute') {
    let client, database, collection;
    try {
      client = new MongoClient(req.body.uri);
      database = client.db(req.body.database_name);
      collection = database.collection(req.body.collection_name);
    } catch {
      res.writeHead(200, {'Content-Type': 'text/html'});
      res.end('mongo_data is invalid');
    }
    let srch = new ESSearch({parameters:req.body.parameters, collection:collection});
    console.log(JSON.stringify(srch.request));
    let result = await srch.execute({});
    console.log(result);
    //for (const obs of result) {console.log(obs);}
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify(result));

  } else {
  res.writeHead(200, {'Content-Type': 'text/html'});
  let html = jsdom.serialize();
  res.end(html);
  }
});

app.listen(3000);
