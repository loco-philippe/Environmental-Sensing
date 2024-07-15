import { MongoClient } from "mongodb";
import { ESSearch } from "../essearch_javascript.js";
import http from 'http';
import * as Plot from "@observablehq/plot";
import {JSDOM} from "jsdom";

const uri = "mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/?retryWrites=true&w=majority";
const client = new MongoClient(uri);
const jsdom = new JSDOM(`
<!DOCTYPE html><html>
<head><meta charset="UTF-8"></head>
<body>
<div class='container'><figure id='graphic'>
</figure></div>
</body></html>`);


let data_array = [];

try {
  const database = client.db("test_obs");
  const coll = database.collection("observation_1");
  let srch = new ESSearch({collection: coll});
  srch.addCondition('datation', new Date(2022, 0, 1), '>=');
  //srch.addCondition('datation', new Date(2022, 11, 32), '<=');
  //srch.addCondition('property', 'PM25');
  //srch.addCondition(undefined, 'observation', '==', 'type');
  let result = await srch.execute({});
  for (const date of result.data.datation.value) {
    let count;
    if (Array.isArray(date.record)) {count = date.record.length;}
    else if (date.record === undefined || date.record === null) {count = 0;}
    else {count = 1;}
    data_array.push({'date':new Date(date.codec), 'count':count}) ;
  }
  console.log(data_array);
} finally {
  await client.close();
}

jsdom.window.document.getElementById('graphic')
                     .appendChild(Plot.plot({
                      y: {
                        grid: true
                      },
                      marks: [
                        Plot.barY(data_array, {x: "date", y: "count", fill: "#bab0ab"}),
                        Plot.ruleY([0])
                      ],
                      document: jsdom.window.document}));

http.createServer(function (req, res) {
  let html = jsdom.serialize();
  res.end(html);
}).listen(8080);

/*
===== Étape 0 : Import des données dans une base MongoDB =====
Pour l'instant, les utilisateurs se débrouillent.

===== Étape 1 : Aide à la recherche =====
- Entrée des information de connexion à la base de données MongoDB.
- Éxécuter la requête vide pour connaître les noms des colonnes.
- Bouton pour exécuter une autre requête vide qui compte le nombre de valeurs dans la base. (potentiellement en regardant les
  informations)
Boutons pour l'exécution d'une requête avec ESSearch :
  - Liste déroulante des noms de colonnes, obtenus lors de l'étape 1, contenant également une option « chemin exact » pour
    autoriser l'entrée d'un chemin à la main ;
  - Liste déroulante des comparateurs autorisés ;
  - Champ pour entrer la valeur de l'opérande (essayer d'aider pour les dates et les géométries) ;
  - Bouton '+' pour ajouter un champ supplémentaire. Lorsque appuyé, ajoute une liste déroulante des champs autorisés. Lorsque
    clic, ajout d'un champ de texte pour définir la valeur et d'un nouveau bouton + pour ajouter un autre champ supplémentaire
    (voir pour ne pas laisser ajouter plusieurs fois le même champ ? en soi, ne pose pas de problème puisque ça génère juste un
    dictionnaire)

Boutons pour paramétrer les graphiques à afficher

Bouton pour l'export des données de sorties avec sélection des colonnes conservées. (qui pourrait aussi se faire avec un
$project dans la requête, mais pas le cas actuellement.

-> voir pour une utilisation de $project automatisée, pas nécessaire de tout sortir à chaque fois si on ne trace qu'une courbe
avec deux des colonnes.

Bouton d'export des données, avec liste déroulante pour les formats si plusieurs formats.

===== Les trois types de graphiques à gérer : =====

- histogramme répartissant les valeurs par fréquence / quantité ;
  -> potentiellement, la version non dépliée des valeurs peut être utile ici pour réduire les calculs (au moins un peu).
  -> format des données : [{'data': value_1, 'frequency': value_2}, ...]

- tracé de courbes pour une ou plusieurs valeurs (légendées) en fonction d'une abscisse donnée ;
  ex: valeur de chaque propriété est une courbe fonction de la date, issue d'un tri des données par villes.

- positionnement de valeurs sur une carte -> probablement plus lisible avec des échelles de couleur.
  -> à voir si les positions str sont simple à positionner... On part du principe que c'est du GeoJson (même si ce sera
  rarement le cas ?) de toute façon, ce genre de conversions n'est pas l'objet de ce module.

===== Possibilité d'export =====
Proposer l'export des données au format csv (et aux éventuels autres formats)
se fait en appliquant single = True et fillvalue = '' (à vérifier) puis en appliquant to_csv.

===== Suite =====
Adaptation de l'intégralité du code en javascript et retrait de la partie appelant python.


Problème à régler des maintenant : la méthode actuelle ne permet pas une communication avec le serveur, mais potentiellement
réglable en englobant tout dans l'appel du module http (ou après ? puisque le serveur reste actif tant que l'on ne fait pas
CTRL+C dans l'invite de commandes, c'est potentiellement possible)
-> à voir si on y arrive.
*/
