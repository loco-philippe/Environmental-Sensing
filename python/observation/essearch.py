import datetime
import shapely.geometry
from pymongo import MongoClient
from esobservation import Observation
from util import util
from timeslot import TimeSlot


# ajouter des vérifications sur le format des données entrées.
# (actuellement, on peut entrer n'importe quoi sans déclencher d'erreur)

# tout comparateur non présent dans ces dictionnaires est considéré invalide
# pas besoin de faire tuple = ("$eq", "==") puisque de toute façon il faudra encore un if côté Python. (exec pas rentable)
dico_alias = {
    str : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "in":"$in", "$in":"$in"
    },
    int : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "gte":"$gte", ">=":"$gte", "=>":"$gte", "$gte":"$gte",
        "gt":"$gt", ">":"$gt", "$gt":"$gt",
        "lte":"$lte", "<=":"$lte", "=<":"$lte",
        "lt":"$lt", "<":"$lt", "$lt":"$lt",
        "in":"$in", "$in":"$in"
    },
    datetime.datetime : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "gte":"$gte", ">=":"$gte", "=>":"$gte", "$gte":"$gte",
        "gt":"$gt", ">":"$gt", "$gt":"$gt",
        "lte":"$lte", "<=":"$lte", "=<":"$lte",
        "lt":"$lt", "<":"$lt", "$lt":"$lt",
        "in":"$in", "$in":"$in"
    },
    TimeSlot : { #only works in Python part
        None:"equals",
        "eq":"equals", "=":"equals", "==":"equals", "eq":"equals", "equals":"equals", "$equals":"equals",
        "contains":"contains", "$contains":"contains",
        "in":"within", "$in":"within", "within":"within", "$within":"within",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"intersects", "$intersects":"intersects"
    },
    list : {
        None:"$geoIntersects",
        "eq":"equals", "=":"equals", "==":"equals", "eq":"equals", "equals":"equals", "$equals":"equals",
        "$geowithin":"$geoWithin", "geowithin":"$geoWithin", "$geoWithin":"$geoWithin", "geoWithin":"$geoWithin", "within":"$geoWithin", "$within":"$geoWithin",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"$geoIntersects", "$intersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geointersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geoIntersects":"$geoIntersects",
        "touches":"touches", "$touches":"touches",
        "overlaps":"overlaps", "$overlaps":"overlaps",
        "contains":"contains", "$contains":"contains",
        "$geoNear":"$geoNear", "$geonear":"$geoNear", "geonear":"$geoNear", "geoNear":"$geoNear", #nécessite des paramètres supplémentaires
        
        "in":"$in", "$in":"$in" #unique cas dans lequel les listes ne sont pas interprétées comme des géométries
    }
}
dico_alias[float] = dico_alias[int]

def clientMongo(user='ESobsUser', pwd='observation', site='esobs.gwpay.mongodb.net/test'):
    auth        = 'authSource=admin'
    replicaSet  = 'replicaSet=atlas-13vws6-shard-0'
    readPref    = 'readPreference=primary'
    appName     = 'appname=MongoDB%20Compass'
    ssl         = 'ssl=true'  
    st = 'mongodb+srv://' + user +':' + pwd + '@' + site + \
            '?' + auth + \
            '&' + replicaSet + \
            '&' + readPref + \
            '&' + appName + \
            '&' + ssl    
    return MongoClient(st)

def f(num=5):
    client = clientMongo()
    return client["test_obs"]['observation' + str(num)]

def insert_from_doc(collection, document = '..//Tests//json_examples.obs', info=True):
    with open(document, 'r') as doc:
        for line in doc:
            try: insert_to_mongo(collection, line, info)
            except: pass

def insert_to_mongo(collection, obj, info=True):
    '''Takes an object and inserts it into a MongoDB collection with info.
    Just use collection.insert_one(obj) if you don't need to add query helpers'''
    obs = Observation.from_obj(obj)
#### A REPRENDRE CAR NE PERMET PAS DE RENTRER datetime.datetime EN DATES ET shapely.geometry EN GEOMETRIE DANS MONGODB TEL QUEL
    dico2 = obs.json(json_info=info)
####
    collection.insert_one(dico2)

def index_creation(coll): # index pris en compte uniquement dans le premier stage de $match dans la requête telle qu'elle est écrite.
    coll.collection.createIndex({"$type": 1}) # $ à confirmer

class ESSearch:
    '''
    An `ESSearch` is defined as an ensemble of conditions to be used to execute a MongoDB request or any iterable containing only observations.

    *Attributes (for @property, see methods)* :

    - **parameters** : list of list of conditions for queries, to be interpreted as : parameters = [[cond_1 AND cond_2 AND cond_3] OR [cond_4 AND cond_5 AND cond_6]] where conds are criteria for queries
    - **data** : iterable on which we want to query. Must contain observations only.
    - **collection** : pymongo.collection.Collection on which we want to query.

    The methods defined in this class are (documentations in methods definitions):
    
    *dynamic value (getter @property)*

    - `ESSearch.request`
    
    *parameters for query - update methods*

    - `ESSearch.addconditions`
    - `ESSearch.addcondition`
    - `ESSearch.orcondition`
    - `ESSearch.removecondition`
    - `ESSearch.clearconditions`
    - `ESSearch.clear`

    *query method*

    - `ESSearch.execute`
    '''
    def __init__(self, 
                    parameters = None,
                    data = None,
                    collection = None,
                    **kwargs
                    ):
        '''
        ESSearch constructor. Parameters can also be defined and updated using class methods.

        *Arguments*

        - **parameters** :  list (default None) - list of dictionnaries whose keys are arguments of ESSearch.addcondition method
        ex: parameters = [
            {'name' : 'datation', 'operand' : datetime.datetime(2022, 9, 19, 1), 'comparator' : '>='},
            {'name' : 'property', 'operand' : 'PM2'}
        ]
        - **data** :  list (default None) - list of Observation
        - **collection** :  pymongo.collection.Collection (default None) - MongoDB collection of Observation. Documents must have been inserted in an appropriate format
        - **kwargs** :  other parameters are used as arguments for ESSearch.addcondition method
        '''
        self.parameters = [[]]
        if isinstance(data, Observation):
            self.data = [data]
        else:
            self.data = data
        self.collection = collection 
        if parameters: self.addconditions(parameters)
        if kwargs: self.addcondition(**kwargs)

    def __repr__(self):
        return "ESSearch(collection = " + str(self.collection) + ", data = " + str(self.data) + ", parameters = " + str(self.parameters) + ")"

    def __str__(self):
        return str(self.parameters)

    def __iter__(self):
        self.n = -1
        return self

    def __next__(self):
        if self.n < len(self.parameters)-1:
            self.n += 1
            return self.parameters[self.n]
        else:
            raise StopIteration

    def __getitem__(self, key):
        return self.parameters[key]

    def addconditions(self, parameters):
        '''
        Takes multiple parameters and executes self.addcondition() for each of them.
        '''
        if isinstance(parameters, dict):
            self.addcondition(**parameters)
        else:
            for parameter in parameters: # On suppose ici que tous les paramètres sont correctement entrés.
                self.addcondition(**parameter)
            
    def addcondition(self, name = None, operand = None, comparator = None, path = None, or_position = -1, **kwargs):
        '''
        Takes parameters and inserts corresponding query condition in self.parameters.

        *Parameters*

        - **name** :  str (default None) - name of an IIndex, which corresponds to an Ilist column name.
        (ex: 'datation', 'location', 'property')

        - **operand** :  - (default None) - Object used for the comparison.
        (ex: if we search for observations made in Paris, operand is 'Paris')

        - **comparator** or **comp** :  str (default None) - str giving the comparator to use. (ex: '>=', 'in')

        - **path** :  str (default None) - to use to define a precise MongoDB path. When name is given, default path is data.<name>.value
        
        - **or_position** :  int (default -1) - position in self.parameters in which the condition is to be inserted.

        - **formatstring** :  str (default None) - str to use to automatically change str to datetime before applying condition. 
        Does not update the data base. If value is set to 'default', format is assumed to be Isoformat.
        
        - **inverted** :  bool (default None) - to add a "not" in the condition.
        To use in case where every element of a MongoDB array (equivalent to python list) must verify the condition (by default, condition is verified when one element of the array verifies it).
        
        - **unwind** :  int (default None) - int corresponding to the number of additional {"$unwind" : "$" + path} to be added in the beginning of the query.


        no comparator => we take the default one given in dico_alias (mainly equality)
        no operand => we only test the existence of something located at path
        '''
        if name is None and operand is None and comparator is None and path is None:
            raise TypeError("ESSearch.addcondition() requires at least one of these parameters : name, operand or path.")

        for item in kwargs:
            if item not in {'formatstring', 'inverted', 'comp', 'unwind'}:
                raise KeyError("Unknown parameter : ", item)

        if isinstance(operand, datetime.datetime) and (operand.tzinfo is None or operand.tzinfo.utcoffset(operand) is None):
            operand = operand.replace(tzinfo=datetime.timezone.utc)

        if path is None:
            if name: path = "data." + name + ".value"
            else: path = "data"

        if operand:
            try: comparator = dico_alias[type(operand)][comparator]
            except: raise ValueError("Incompatible values for comparator and operand.")
        elif comparator:
            raise ValueError("operand must be defined when comparator is used.")

        condition = {"comp" : comparator, "operand" : operand, "path" : path, "name" : name} | kwargs

        if or_position >= len(self.parameters):
            self.parameters.append([condition])
        else:
            self.parameters[or_position].append(condition)

    def orcondition(self, *args, **kwargs):
        '''
        Adds a condition in a new sublist in self.parameters. Separations in sublists correspond to "or" in the query.
        '''
        self.addcondition(or_position = len(self.parameters), *args, **kwargs)

    def removecondition(self, or_position = None, condnum = None): # A CORRIGER
        '''
        Removes a condition from self.parameters. By default, last element added is removed.
        Otherwise, condition removed is self.parameters[or_position][condnum]

        To remove all conditions, use ESSearch.clearconditions() method.
        '''
        if self.parameters == [[]]: return
        if or_position is None:
            if condnum is None: self.parameters[-1].pop(-1)
            else: self.parameters.pop(condnum)
        else:
            if condnum is None: self.parameters.pop(or_position)
            else: self.parameters[or_position].pop(condnum)

    def clearconditions(self):
        '''
        Removes all conditions from self.parameters
        To remove all attributes, use ESSearch.clear() method.
        '''
        self.parameters = [[]]

    def clear(self):
        '''
        Resets self
        '''
        self = ESSearch()

    def _cond(self, or_pos, operand, comp, path, inverted = False, name = None, formatstring = None, unwind = None):
        '''
        Takes parameters and adds corresponding MongoDB expression to sel._match_2.
        self._unwind and self._set are updated when necessary.

        -> Traiter le cas de conditions redondantes (ex: <4 => <8) (actuellement, le dernier arrivé l'emporte)
        '''
        if unwind:
            for _ in range(unwind):
                self._unwind.append(path)
        elif name and operand and name not in self._unwind: self._unwind.append("data." + name)

        if operand is None: # no operand => we only test if there is something located at path or at path given by name
            if name: path = "data." + name
            comp = "$exists"
            operand = 1
        else:
            try: comp = dico_alias[type(operand)][comp] #global variable
            except:
                if formatstring:
                    try: comp = dico_alias[datetime.datetime][comp]
                    except: raise ValueError("Comparator not allowed.")

        if isinstance(operand, TimeSlot): #equals, contains, within, disjoint, intersects
            if comp in {"equals", "within"}:
                self._cond(or_pos, operand[0].start, "$gte", path, False, name)
                self._cond(or_pos, operand[-1].end, "$lte", path, False, name)
            elif comp in {"contains", "intersects"}:
                self._cond(or_pos, operand[0].start, "$lte", path, False, name)
                self._cond(or_pos, operand[-1].end, "$gte", path, False, name)
            return

        if formatstring:
            if formatstring == "default":
                if isinstance(operand, str):
                    operand = datetime.datetime.fromisoformat(operand)
                self._set |= {path : {"$convert": {"input" : "$" + path, "to" : "date", "onError" : "$" + path}}}
            else:
                if isinstance(operand, str):
                    datetime.datetime.strptime(operand, formatstring)
                self._set |= {path : {"$dateFromString" : {"dateString" : "$" + path, "format": formatstring, "onError": "$" + path}}}

        if comp in {"$geoIntersects", "$geoWithin", "$geoNear"}:
            if len(operand) == 1 or (len(operand) > 1 and not isinstance(operand[0], list)): geomtype = "Point"
            elif len(operand) == 2: geomtype = "LineString"
            elif len(operand) > 2:
                if len(operand) == 3:
                    operand.append(operand[-1])
                geomtype = "Polygon"
            # self._set |= {path : {"$geometry" : {{"type" : geomtype, "coordinates" : "$" + path, "onError": "null"}}}
            if comp == "$geoNear": # geoNear est un stage Mongo en soi
                pass
            else:
                operand = {"$geometry" : {"type" : geomtype, "coordinates" : operand}}

        cond_0 = {comp : operand}

        if inverted:
            if path in self._match_2[or_pos]:
                if "$nor" in self._match_2[or_pos][path]: #CHEMINS A VERIFIER
                    self._match_2[or_pos][path]["$nor"].append(cond_0)
                elif "not" in self._match_2[or_pos][path]:
                    self._match_2[or_pos][path]["$nor"] = [self._match_2[or_pos][path]["$not"], cond_0]
                    del self._match_2[or_pos][path]["$not"]
                else:
                    self._match_2[or_pos][path]["$not"] = cond_0
            else:
                self._match_2[or_pos][path] = {"$not" : cond_0}
        else:
            if path not in self._match_2[or_pos]:
                self._match_2[or_pos][path] = cond_0
            else:
                self._match_2[or_pos][path] |= cond_0

    def _fullSearchMongo(self):
        self._request = []
        #self._match_1 = {"type" : "obs"}
        self._unwind = []
        self._set = {}
        self._match_2 = []
        self._project = {"information" : 0}
        
        for i in range(len(self.parameters)):
            self._match_2.append({})
            for cond in self.parameters[i]:
                self._cond(or_pos = i, **cond)

        #if self._match_1:
        #    self._request.append({"$match" : self._match_1})
        if self._unwind:
            for unwind in self._unwind:
                self._request.append({"$unwind" : "$" + unwind})
        if self._set: # A VÉRIFIER, NON TESTÉ
            self._request.append({"$set" : self._set})
        if self._match_2:
            if len(self.parameters) == 1: # no $or
                self._request.append({"$match" : self._match_2[0]})
            else: # there is a $or
                self._request.append({"$match" : {"$or": self._match_2}})
        if self._project:
            self._request.append({"$project" : self._project})
        return self._request

    @property
    def request(self):
        '''
        content of the aggregation query to be executed with ESSearch.execute()
        '''
        return self._fullSearchMongo()

    def execute(self, single = True):
        '''
        Executes the request and returns its result, either in one or many Observations.

        *Parameter*

        - **single** :  bool (default True) - Must be put to False in order to return a list of Observation instead of a single Observation.
        '''
        if self.collection is None: cursor = []
        else: cursor = self.collection.aggregate(self.request)
        if not self.data: self.data = []
        if self.parameters == [[]]:
            result = self.data
            for item in cursor: result.append(Observation.from_obj(item)) # paramètres de from_obj dépendant du format entré dans la base
        else:
            result = [self._filtered_observation(item) for item in self.data]            
            for item in cursor: result.append(self._filtered_observation(Observation.from_obj(item)))
        if single: return self._fusion(result)
        else: return result

    def _filtered_observation(self, obs):
        '''
        Takes an Observation and returns a filtered Observation with self.parameters as a filter.
        '''
        # self.parameters = [[cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]
        # dico = {"data": [["datation", [date1, date2, date3], [0,1,0,2,2,1]], ["location", [loc1, loc2, loc3], [0,1,2,0]]]}
        if len(obs) == 0: return obs
        
        if not(isinstance(obs, Observation)):
            try: Observation(obs)   #pas parfait puisque Observation.from_obj(obs) ne sera pas fait implicitement.
            except: raise TypeError("Could not convert argument to an Observation.")

        for i in range(len(self.parameters)):
            if self.parameters[i] != []:
                conds, next_relevant = self._newconds(obs, self.parameters[i])
                filter = util.funclist(obs.lindex[0].cod, self._condcheck, conds[0], obs.lindex[0].name)
                if not isinstance(filter, list): filter = [filter]
                full_filter = util.tovalues(obs.lindex[0].keys, filter)
                for j in range(1, obs.lenidx):
                    next_filter = util.funclist(obs.lindex[j].cod, self._condcheck, conds[j], obs.lindex[j].name)
                    if not isinstance(next_filter, list): next_filter = [next_filter]
                    next_filter_full = util.tovalues(obs.lindex[j].keys, next_filter)
                    full_filter = [full_filter[k] and next_filter_full[k] for k in range(len(full_filter))]
                if i == 0:
                    final_filter = full_filter
                    relevant = next_relevant
                else:
                    final_filter = [full_filter[j] or final_filter[j] for j in range(len(full_filter))]
                    relevant = relevant and next_relevant
        if relevant:
            obs.setfilter(final_filter)
            obs.applyfilter()
            return obs
        else:
            return Observation()

    def _newconds(self, obs, parameter):
        '''
        Takes parameters and returns a list of bool.
        Allows to only test conditions on relevant elements. ex: 'cat' > 3 does not make sense.
        '''
        # parameter = [cond1 AND cond 2 AND cond 3]
        new_conds = []
        relevant =  False
        for i in range(len(obs.lindex)):
            new_conds.append([])
            for cond in parameter:
                if ("name" not in cond and ("path" not in cond or ("path" in cond and cond["path"] == "data." + obs.lindex[i].name) ) \
                        or ("name" in cond and cond["name"] == obs.lindex[i].name)) \
                        and ("operand" not in cond or ("operand" in cond and self._compatibletypes(obs.lindex[i].cod[0], cond))):
                    new_conds[i].append(cond)
                    relevant = True
                elif "name" not in cond and "path" in cond and cond["path"][:11] == "information" : #Les vérifications sur les path commençant par information ne se font que dans MongoDB
                    relevant = True
        return new_conds, relevant

    def _condcheck(self, item, parameter = None, datatype = None):
        '''
        Takes an item corresponding to a colum in the Observation and returns a Boolean if it verifies criteria given by parameter.
        '''
        # parameters = [cond1 AND cond 2 AND cond 3]
        if not parameter: return True
        boolean = True
        for cond in parameter:
            boolean = boolean and self._condcheck_0(item, cond, datatype)
        return boolean

    def _condcheck_0(self, item, cond = None, datatype = None):
        '''
        Takes an item and returns a Boolean.
        Subfonction executed by _condcheck for each condition in parameter.
        '''
        #cond = {"comp" : comparator, "operand" : operand, "path" : path, "name" : name} and sometimes can contain "inverted" or "formatstring"
        if cond is None: return True
        if cond["comp"] is None and cond["operand"] is None: return True

        if cond["name"] == "datation":
            if "formatstring" in cond:
                if not isinstance(item, datetime.datetime):
                    item = datetime.datetime.strptime(item, cond["formatstring"])
                if not isinstance(cond["operand"], datetime.datetime):
                    cond["operand"] = datetime.datetime.strptime(cond["operand"], cond["formatstring"])
            elif isinstance(item, TimeSlot):
                if cond["comp"] in dico_alias[type(cond["comp"])]:
                    cond["comp"] = dico_alias[type(cond["comp"])][cond["comp"]]
                    return item.link(cond["operand"])[0] == cond["comp"]
                else:
                    if cond["comp"] in {"$gte", "gte", ">=", "=>"}:
                        if "inverted" in cond and cond["inverted"]: return item.bounds[0] >= cond["operand"]
                        else: return item.bounds[1] >= cond["operand"]
                    elif cond["comp"] in {"$gt", "gt", ">"}         :
                        if "inverted" in cond and cond["inverted"]: return item.bounds[0] > cond["operand"]
                        else: return item.bounds[1] > cond["operand"]
                    elif cond["comp"] in {"$lte", "lte", "<=", "=<"}:
                        if "inverted" in cond and cond["inverted"]: return item.bounds[1] <= cond["operand"]
                        else: return item.bounds[0] <= cond["operand"]
                    elif cond["comp"] in {"$lt", "lt", "<"}         :
                        if "inverted" in cond and cond["inverted"]: return item.bounds[1] < cond["operand"]
                        else: return item.bounds[0] < cond["operand"]
                    else: raise ValueError("Comparator not supported for TimeSlot.")
        elif cond["name"] == "location":
            if cond["comp"] in {"$eq", "eq", "=", "==", "$equals", "equals"}            : return item.equals(cond["operand"])
            elif cond["comp"] in {"$geowithin", "geowithin", "$geoWithin", "geoWithin", "$within", "within"} : return item.within(cond["operand"])
            elif cond["comp"] in {"$disjoint", "disjoint"}                              : return item.disjoint(cond["operand"])
            elif cond["comp"] in {"$intersects", "intersects"}                          : return item.intersects(cond["operand"])
            elif cond["comp"] in {"$touches", "touches"}                                : return item.touches(cond["operand"])
            elif cond["comp"] in {"$overlaps", "overlaps"}                              : return item.overlaps(cond["operand"])
            elif cond["comp"] in {"$contains", "contains"}                              : return item.contains(cond["operand"])
            elif cond["comp"] not in {"$geonear", "geonear", "$geoNear", "geoNear"}         : return True # no equivalent for this MongoDB operator in shapely
        elif cond["name"] == "property": # assuming property contains dict and the search targets one of its values
            for val in item.values():
                if self._condcheck_0(val, cond | {"name" : None}, datatype):
                    return True
            return False

        if cond["comp"] in {"$eq", "eq", "=", "=="}     : return item == cond["operand"]
        elif cond["comp"] in {"$gte", "gte", ">=", "=>"}: return item >= cond["operand"]
        elif cond["comp"] in {"$gt", "gt", ">"}         : return item >  cond["operand"]
        elif cond["comp"] in {"$lte", "lte", "<=", "=<"}: return item <= cond["operand"]
        elif cond["comp"] in {"$lt", "lt", "<"}         : return item <  cond["operand"]
        elif cond["comp"] in {"$in", "in"}              : return item in cond["operand"]
        else:
            return True
            #raise ValueError("Comparator not supported.")

    def _compatibletypes(self, item, cond):
        '''
        Takes an item and a condition and returns True if the condition can be applied on the item.
        ex: 3 > 1 makes sense (returns True), but 'cat' > 1 does not (returns False).
        (In this example, item = 3 or 'cat', cond = {'operand': 1, 'comparator': '>'})
        '''
        #NE FONCTIONNE PAS
        if type(item) == type(cond["operand"]): return True
        elif cond["comp"] == "$in":
            if isinstance(cond["operand"], list) and len(cond["operand"]) > 0:
                return self._compatibletypes(item, cond | {"operand" : cond["operand"][0], "comp" : None})
            elif len(cond["operand"]) == 0: return True
            else: return False
        elif "formatstring" in cond:
            if isinstance(item, str):
                return type(cond["operand"]) in {str, datetime.datetime, TimeSlot}
            elif isinstance(cond["operand"], str):
                return type(item) in {datetime.datetime, TimeSlot}
        elif isinstance(item, dict):
            for val in item.values():
                if self._compatibletypes(val, cond):
                    return True
            return False
        else:
            return False

    def _fusion(self, obsList): #n'a pas sa place ici, à déplacer comme constructeur d'Observation ou ailleurs
        '''
        Takes a list of observations and returns one observation mixing them together in one single observation.
        '''
        if len(obsList) == 1:
            return obsList[0]
        elif len(obsList) > 1:
            obs = obsList[0].mix(obsList[1])
            for item in obsList[2:]:
                obs = obs.mix(item)
            return obs


if __name__ == "__main__":
    #from dotenv import dotenv_values
    from pymongo import cursor

    # 1. Connection à la base de donnée
    #config = dotenv_values(".env")
    #client = clientMongo(config["USER"], config["PWD"], config["SITE"])
    client = clientMongo()
    db = client["test_obs"]
    coll = db["observation5"]

    #2. Exemple de requête avec condition sur la date :
    research = ESSearch(collection=coll)
    research.addcondition('datation', datetime.datetime(2022, 1, 1, 0), ">=", inverted = True) #ACTUELLEMENT NE FONCTIONNE PAS CAR DONNÉES MAL RENTRÉES DANS LA BASE
    #research.addcondition('datation', datetime.datetime(2022, 9, 2, 3), ">=")
    #research.addcondition('location', [2.1, 45.1]) #ACTUELLEMENT NE FONCTIONNE PAS CAR DONNÉES MAL RENTRÉES DANS LA BASE
    #research.addcondition('property', 'PM1')
    print("Requête effectuée :", research.request, '\n')
    search_result = research.execute()
    if not search_result is None:
        if isinstance(search_result, cursor.Cursor):
            for el in search_result[:10]: print(el)
        else:
            print(search_result.to_obj(), '\n')
    else: print(None)

    # équivalent à :
    research = ESSearch([{"name" : 'datation', "operand" : datetime.datetime(2022, 9, 19, 1), 'comparator' : "$gte", 'inverted' : True},
                {"name" : 'datation', "operand" : datetime.datetime(2022, 9, 20, 3), 'comparator' : "$gte"}], collection = coll)
    print("Requête effectuée :", research.request)