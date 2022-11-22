let dico_alias_mongo = {
  'string' : {
    undefined:"$eq",
    "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
    "in":"$in", "$in":"$in"
  },
  'number' : {
    undefined:"$eq",
    "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
    "gte":"$gte", ">=":"$gte", "=>":"$gte", "$gte":"$gte",
    "gt":"$gt", ">":"$gt", "$gt":"$gt",
    "lte":"$lte", "<=":"$lte", "=<":"$lte", "$lte":"$lte",
    "lt":"$lt", "<":"$lt", "$lt":"$lt",
    "in":"$in", "$in":"$in"
  },
  'date' : { //attention, typeof détecte object
    undefined:"$eq",
    "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
    "gte":"$gte", ">=":"$gte", "=>":"$gte", "$gte":"$gte",
    "gt":"$gt", ">":"$gt", "$gt":"$gt",
    "lte":"$lte", "<=":"$lte", "=<":"$lte", "$lte":"$lte",
    "lt":"$lt", "<":"$lt", "$lt":"$lt",
    "in":"$in", "$in":"$in"
  },
  'array' : { //attention, typeof détecte object
    undefined:"$geoIntersects",
    "eq":"equals", "=":"equals", "==":"equals", "$eq":"equals", "equals":"equals", "$equals":"equals",
    "$geowithin":"$geoWithin", "geowithin":"$geoWithin", "$geoWithin":"$geoWithin", "geoWithin":"$geoWithin", "within":"$geoWithin", "$within":"$geoWithin",
    "disjoint":"disjoint", "$disjoint":"disjoint",
    "intersects":"$geoIntersects", "$intersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geointersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geoIntersects":"$geoIntersects",
    "touches":"touches", "$touches":"touches",
    "overlaps":"overlaps", "$overlaps":"overlaps",
    "contains":"contains", "$contains":"contains",
    "$geoNear":"$geoNear", "$geonear":"$geoNear", "geonear":"$geoNear", "geoNear":"$geoNear",
    
    "in":"$in", "$in":"$in"
  }
};

export class ESSearch {
  constructor({parameters, collection, heavy}) {
    this.parameters = [[]];
    this.collection = collection;
    this.heavy = heavy;
    if (parameters) {this.addConditions(parameters);}
  }

  get request() {
    return this._fullSearchMongo();
  }

  addConditions(parameters) {
    for (const param of parameters) {
      if (Array.isArray(param)) {this.addCondition.apply(this, param);}
      else {this.addCondition(param);}
    }
  }

  addCondition(name, operand, comparator, path, or_position = this.parameters.length - 1, others = {}) {
    let condition;
    
    if (path === undefined) {
      if (name) {
        if (["$year", "$month", "$dayOfMonth", "$hour", "$minute", "$second", "$millisecond", "$dayOfYear", "$dayOfWeek"].includes(name)) {
          path = "data.datation.value.codec";
        }
        else {
          path = "data." + name + ".value.codec";
        }
      }
      else { path = "data";}
    }

    if (operand) {
      try {comparator = dico_alias_mongo[typeof operand][comparator];}
      catch {
        if (others.formatstring) {
          comparator = dico_alias_mongo['date'][comparator];
        }
        else if (Array.isArray(operand)) {
          comparator = dico_alias_mongo['array'][comparator];
        }
      }
    }

    condition = Object.assign({"comparator" : comparator, "operand" : operand, "path" : path, "name" : name}, others);

    if (Array.isArray(this.parameters[or_position])){
      this.parameters[or_position] = this.parameters[or_position].concat([condition]);
    }
    else {
        this.parameters[or_position] = condition;
    }
  }

  _cond(or_pos, cond) {
    let match, name = cond.name, path = cond.path, comparator = cond.comparator, operand = cond.operand;
    match = '2';
    if (cond.unwind) {
      if (typeof cond.unwind === 'string') {this._unwind.push(cond.unwind);}
      else if (typeof cond.unwind === 'number') {
        for (let i = 0; i < 20; i++) {this._unwind.push(path);}
      }
      else if (Array.isArray(cond.unwind)) {
        for (let i = 0; i < cond.unwind[1]; i++) {this._unwind.push(cond.unwind[0]);}
      }
    }
    else if (name && operand && !(this._unwind.includes("data." + name + ".value"))) {this._unwind.push("data." + name + ".value");}
    else if (path && path.slice(0, 5) !== "data.") {match = '1';}
    if (this.heavy && operand && path && path.slice(0, 4) === "data") {
      if (!(this._heavystages.includes(path))) {this._heavystages.concat([path]);}
      path = "_" + path + ".v";
    }
    if (operand === undefined) {
      if (name) {path = "data." + name;}
      comparator = "$exists";
      operand = 1;
    }
    if (["$year", "$month", "$dayOfMonth", "$hour", "$minute", "$second", "$millisecond", "$dayOfYear", "$dayOfWeek"].includes(name)) {
      const temp_0 = {}, temp_1 = {}; nameno$ = name.slice(1);
      temp_0[name.slice(1)] = {};
      temp_0[name.slice(1)][name] = path;
      Object.assign(this._set, temp_0);
      path = name.slice(1);
      temp_1[path] = 0;
      Object.assign(this._project, temp_1);
    }
    if (cond.formatstring) {
      if (cond.formatstring === "default") {
        if (typeof operand === 'string') {
          operand = new Date(operand);
        }
        if (Object.values(this._set).includes(path)) {
          Object.assign(this._set[path], {"$convert": {"input" : "$" + path, "to" : "date", "onError" : "$" + path}});
        }
        else {
          this._set[path] = {"$convert": {"input" : "$" + path, "to" : "date", "onError" : "$" + path}};
        }
      }
      else {
        if (typeof operand === 'string') {
          new Date(operand); // date devrait être créée en prenant la formatstring en paramètre ici.
        }
        
        if (Object.values(this._set).includes(path)) {
          Object.assign(this._set[path], {"$dateFromString" : {"dateString" : "$" + path, "format": cond.formatstring, "onError": "$" + path}});
        }
        else {
          this._set[path] = {"$dateFromString" : {"dateString" : "$" + path, "format": cond.formatstring, "onError": "$" + path}};
        }
      }
    }

    if (comparator === "$geoIntersects" || comparator === "$geoWithin") {
      let geom_type, coordinates;
      if (Array.isArray(operand)) {
        if (!(Array.isArray(operand[0]))) {
          geom_type = "Point";
          coordinates = operand;
        }
        else if (!(Array.isArray(operand[0][0]))) {
          if (operand.length === 1) {
            geom_type = "Point";
            coordinates = operand[0];
          }
          else if (operand.length === 2)  {
            geom_type = "LineString";
            coordinates = operand;
          }
          else if (operand.length > 2) {
            if (operand[-1] !== operand[0]) {
              operand.concat([operand[0]]);
            }
            geom_type = "Polygon";
            coordinates = [operand];
          }
        }
        else {
          geom_type = "Polygon";
          coordinates = operand;
        }
        operand = {"$geometry" : {"type" : geom_type, "coordinates" : coordinates}};
      }
      else if (typeof operand === 'object' && !(Object.values(operand).includes('$geometry'))) {
        operand = {"$geometry" : operand};
      }
    }
    else if (comparator === "$geoNear") {
      /* ne fonctionnera pas en l'état */
      Object.assign(this._geonear, cond); // paramètres à mentionner explicitement, puisque cond contient aussi des informations sans rapport
      return;
    }

    let cond_0 = {};
    cond_0[comparator] = operand;
        
    if (cond.inverted) {
      if (Object.values(this._match[match][or_pos]).includes(path)) {
        if (Object.values(this._match[match][or_pos][path]).includes("$nor")) {
          this._match[match][or_pos][path]["$nor"].concat([cond_0]);
        }
        else if (Object.values(this._match[match][or_pos][path]).includes("not")) {
          this._match[match][or_pos][path]["$nor"] = [this._match[match][or_pos][path]["$not"], cond_0];
          delete this._match[match][or_pos][path]["$not"];
        }
        else {
          this._match[match][or_pos][path]["$not"] = cond_0;
        }
      }
      else {
        this._match[match][or_pos][path] = {"$not" : cond_0};
      }
    }
    else {
      if (!(Object.values(this._match[match][or_pos]).includes(path))) {
        this._match[match][or_pos][path] = cond_0;
      }
      else {
        Object.assign(this._match[match][or_pos][path], cond_0);
      }
    }
  }

  _fullSearchMongo() {
    let request = [];
    this._match = {};
    this._match['1'] = [{}];
    this._unwind = [];
    this._heavystages = [];
    this._set = {};
    this._geonear = {};
    this._match['2'] = [{}];
    this._project = {"_id" : 0, "_data" : 0, "information" : 0};
        
    for (let i = 0; i < this.parameters.length; i++) {
      this._match['1'].concat([{}]);
      this._match['2'].concat([{}]);
      for (const cond of this.parameters[i]) {
        this._cond(i, cond);
      }
    }

    if (this._match['1'].length !== 0 && Object.keys(this._match['1'][0]).length !== 0) {
      let j = 0;
      for (let i = 0; i < this._match['1'].length; i++) {
        if (Object.keys(this._match['1'][i]).length !== 0 && j != i) {
          this._match['1'][j] = this._match['1'][i];
          j += 1;
        }
      }
      if (j === 0) {
        if (Object.keys(this._match['1'][0]).length !== 0) {request.push({"$match" : this._match['1'][0]});}
      }
      else {
        request.push({"$match" : {"$or": this._match['1'].slice(0, j)}});
      }
    }
    if (this._unwind.length !== 0) {
      for (const unwind of this._unwind) {
        request.push({"$unwind" : "$" + unwind});
      }
    }
    if (this._heavystages.length !== 0) {
      let heavy = {};
      for (const path of this._heavystages) {
        if (Object.values(operand).includes("_" + path)) {
          Object.assign(heavy["_" + path], {"$cond":{"if":{"$eq":[{"$type":"$" + path},"object"]},"then":{"$objectToArray":"$" + path},"else": {"v":"$" + path}}});
        }
        else {
          heavy["_" + path] = {"$cond":{"if":{"$eq":[{"$type":"$" + path},"object"]},"then":{"$objectToArray":"$" + path},"else": {"v":"$" + path}}};
        }
      }
      request.push({"$set" : heavy});
    }
    if (Object.keys(this._set).length !== 0) {request.push({"$set" : this._set});}
    if (Object.keys(this._geonear).length !== 0) {request.push({"$geoNear" : this._geonear});}
    if (this._match['2'].length !== 0 && Object.keys(this._match['2'][0]).length !== 0) {
      let j = 0;
      for (let i = 0; i < this._match['2'].length; i++) {
        if (Object.keys(this._match['2'][i]).length !== 0 && j != i) {
          this._match['2'][j] = this._match['2'][i];
          j += 1;
        }
      }
      if (j === 0) {
        if (Object.keys(this._match['2'][0]).length !== 0) {request.push({"$match" : this._match['2'][0]});}
      }
      else {
        request.push({"$match" : {"$or": this._match['2'].slice(0, j)}});
      }
    }
    if (this._unwind.length !== 0) {
      let dico = {};
      for (const unwind of this._unwind) {
        dico[unwind] = ["$" + unwind]; //foireux dans la version en python également
      }
      request.push({"$set" : dico});
    }
    if (Object.keys(this._project).length !== 0) {request.push({"$project" : this._project});}
    return request;
  }

  execute() {
    /* No conversion to Observation in this version */
    let cursor, result = [];
    cursor = this.collection.aggregate(this._fullSearchMongo());
    return cursor; // temporaire
    for (const item of cursor) {result.push(item);} // devrait être un await ici, mais provoque une erreur si on le met. (tout cela est bien mystérieux)
    return result;
  }
}

// Tests à retirer
/*
let srch = new ESSearch({collection: 'collec'});
srch.addCondition('datation', new Date(2022, 0, 1), '>=');
srch.addCondition('datation', new Date(2022, 11, 32), '<=');
srch.addCondition('property', 'PM25');
srch.addCondition(undefined, 'observation', '==', 'type');
console.log(srch.parameters);
console.log(srch.request);
console.log(JSON.stringify(srch.request, null, 2));

let srch2 = new ESSearch({parameters: [['datation', new Date(2022, 0, 1), '>='],
                        ['datation', new Date(2022, 11, 32), '<='], 
                        ['property', 'PM25'], 
                        [undefined, 'observation', '==', 'type']],
                        collection: 'collec'})
console.log(srch2.parameters);
console.log(srch2.request);
console.log(JSON.stringify(srch2.request, null, 2));
console.log(srch.parameters == srch2.parameters);
console.log(srch.request == srch2.request);
*/