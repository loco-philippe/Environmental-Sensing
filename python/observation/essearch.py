from argparse import ArgumentError
import datetime
import shapely.geometry
from pymongo.collection import Collection
from esobservation import Observation
from util import util
from timeslot import TimeSlot

dico_alias = { # dictionnary of the different names accepted for each comparator and a given type. <key>:<value> -> <accepted name>:<name in MongoDB>
    # any type other than those used as keys is considered non valid
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
    TimeSlot : { # only used in python filtering part
        None:"equals",
        "eq":"equals", "=":"equals", "==":"equals", "eq":"equals", "equals":"equals", "$equals":"equals",
        "contains":"contains", "$contains":"contains",
        "in":"within", "$in":"within", "within":"within", "$within":"within",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"intersects", "$intersects":"intersects"
    },
    list : { # lists are interpreted as geometries
        None:"$geoIntersects",
        "eq":"equals", "=":"equals", "==":"equals", "eq":"equals", "equals":"equals", "$equals":"equals",
        "$geowithin":"$geoWithin", "geowithin":"$geoWithin", "$geoWithin":"$geoWithin", "geoWithin":"$geoWithin", "within":"$geoWithin", "$within":"$geoWithin",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"$geoIntersects", "$intersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geointersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geoIntersects":"$geoIntersects",
        "touches":"touches", "$touches":"touches",
        "overlaps":"overlaps", "$overlaps":"overlaps",
        "contains":"contains", "$contains":"contains",
        "$geoNear":"$geoNear", "$geonear":"$geoNear", "geonear":"$geoNear", "geoNear":"$geoNear", #nécessite des paramètres supplémentaires
        
        "in":"$in", "$in":"$in" # only case where a list is not a geometry
    }
}
dico_alias[float] = dico_alias[int]

def insert_from_doc(collection, document = '..//Tests//json_examples.obs', info=True):
    with open(document, 'r') as doc:
        for line in doc:
            try: insert_to_mongo(collection, line, info)
            except: pass

def insert_to_mongo(collection, obj, info=True):
    '''Takes an object and inserts it into a MongoDB collection, with info by default.'''
    obs = Observation.from_obj(obj)
#### A REPRENDRE CAR NE PERMET PAS DE RENTRER datetime.datetime EN DATES ET geometry EN GEOMETRIE DANS MONGODB TEL QUEL
    dico2 = obs.json(json_info=info)
####
    collection.insert_one(dico2)

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

        - **parameters** :  dict, list (default None) - list of dictionnaries whose keys are arguments of ESSearch.addcondition method
        ex: parameters = [
            {'name' : 'datation', 'operand' : datetime.datetime(2022, 9, 19, 1), 'comparator' : '>='},
            {'name' : 'property', 'operand' : 'PM2'}
        ]
        - **data** :  list (default None) - list of Observation
        - **collection** :  pymongo.collection.Collection (default None) - MongoDB collection of Observation. Documents must have been inserted in an appropriate format
        - **kwargs** :  other parameters are used as arguments for ESSearch.addcondition method
        '''
        self.parameters = [[]]
        if isinstance(data, list) or data is None:
            self.data = data
        elif isinstance(data, Observation):
            self.data = [data]
        else: raise TypeError("data must be a list.")

        if isinstance(collection, Collection) or collection is None:
            self.collection = collection
        else: raise TypeError("collection must be a pymongo.collection.Collection.")
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
        elif isinstance(parameters, list) or isinstance(parameters, tuple):
            for parameter in parameters:
                self.addcondition(**parameter)
        else: raise TypeError("parameters must be either a dict or a list of dict.")
            
    def addcondition(self, name = None, operand = None, comparator = None, path = None, or_position = -1, **kwargs):
        '''
        Takes parameters and inserts corresponding query condition in self.parameters.

        *Parameters*

        - **name** :  str (default None) - name of an IIndex, which corresponds to an Ilist column name.
                    (ex: 'datation', 'location', 'property')

        - **operand** :  - (default None) - Object used for the comparison.
                    (ex: if we search for observations made in Paris, operand is 'Paris')

        - **comparator**:  str (default None) - str giving the comparator to use. (ex: '>=', 'in')

        - **path** :  str (default None) - to use to define a precise MongoDB path. When name is given, default path is data.<name>.value
        
        - **or_position** :  int (default -1) - position in self.parameters in which the condition is to be inserted.

        - **formatstring** :  str (default None) - str to use to automatically change str to datetime before applying condition. 
                    Does not update the data base. If value is set to 'default', format is assumed to be Isoformat.
        
        - **inverted** :  bool (default None) - to add a "not" in the condition.
                    To use in case where every element of a MongoDB array (equivalent to python list) must verify the condition (by default, condition is verified when at least one element of the array verifies it).
        
        - **unwind** :  int (default None) - int corresponding to the number of additional {"$unwind" : "$" + path} to be added in the beginning of the query.


        no comparator => default comparator associated with operand type in dico_alias is used (mainly equality)
        no operand => only the existence of something located at path is tested
        '''
        if name is not None and not isinstance(name, str): raise TypeError("name must be a str.")
        if comparator is not None and not isinstance(name, str): raise TypeError("comparator must be a str.")
        if path is not None and not isinstance(path, str): raise TypeError("path must be a str.")
        if or_position is not None and not isinstance(or_position, int): raise TypeError("or_position must be an int.")

        if name is None and operand is None and comparator is None and path is None:
            raise ArgumentError("ESSearch.addcondition() requires at least one of these parameters : name, operand or path.")

        for item in kwargs:
            if item not in {'formatstring', 'inverted', 'unwind', 'distanceField', 'distanceMultiplier', 'includeLocs', 'key', 'maxDistance', 'minDistance', 'near', 'query', 'spherical'}:
                raise ArgumentError("Unknown parameter : ", item)

        if isinstance(operand, datetime.datetime) and (operand.tzinfo is None or operand.tzinfo.utcoffset(operand) is None):
            operand = operand.replace(tzinfo=datetime.timezone.utc)

        if path is None:
            if name:
                if name == 'property':
                    path = "data." + name + ".value.prp"
                else:
                    path = "data." + name + ".value"
            else: path = "data"

        if operand:
            try: comparator = dico_alias[type(operand)][comparator]
            except: raise ValueError("Incompatible values for comparator and operand.")
        elif comparator:
            raise ValueError("operand must be defined when comparator is used.")

        condition = {"comparator" : comparator, "operand" : operand, "path" : path, "name" : name} | kwargs

        if or_position >= len(self.parameters):
            self.parameters.append([condition])
        else:
            self.parameters[or_position].append(condition)

    def orcondition(self, *args, **kwargs):
        '''
        Adds a condition in a new sublist in self.parameters. Separations in sublists correspond to "or" in the query.
        '''
        self.addcondition(or_position = len(self.parameters), *args, **kwargs)

    def removecondition(self, or_position = None, condnum = None):
        '''
        Removes a condition from self.parameters. By default, last element added is removed.
        Otherwise, condition removed is self.parameters[or_position][condnum]

        To remove all conditions, use ESSearch.clearconditions() method.
        '''
        if self.parameters == [[]]: return
        if or_position is None:
            if condnum is None:
                if len(self.parameters[-1]) > 1: self.parameters[-1].pop(-1)
                else: self.parameters.pop(-1)
            else:
                if len(self.parameters[-1]) > 1 or condnum > 1: self.parameters[-1].pop(condnum)
                else: self.parameters.pop(-1)
        else:
            if condnum is None or (len(self.parameters[or_position]) == 1 and condnum == 0): self.parameters.pop(or_position)
            else: self.parameters[or_position].pop(condnum)
        if self.parameters == []:
            self.parameters = [[]]

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

    def _cond(self, or_pos, operand, comparator, path, inverted = False, name = None, formatstring = None, unwind = None, **kwargs):
        '''
        Takes parameters and adds corresponding MongoDB expression to self._match_2.
        self._unwind and self._set are updated when necessary.
        '''
        if unwind:
            for _ in range(unwind):
                self._unwind.append(path)
        elif name and operand and name not in self._unwind: self._unwind.append("data." + name)

        if operand is None: # no operand => we only test if there is something located at path or at path given by name
            if name: path = "data." + name
            comparator = "$exists"
            operand = 1
        else:
            try: comparator = dico_alias[type(operand)][comparator] #global variable
            except:
                if formatstring:
                    try: comparator = dico_alias[datetime.datetime][comparator]
                    except: raise ValueError("Comparator not allowed.")
                else:
                    try: operand = {"type" : operand.geom_type, "coordinates" : list(operand.exterior.coords)}
                    except: raise ValueError("Comparator not allowed.")

        if isinstance(operand, TimeSlot): #equals, contains, within, disjoint, intersects
            if comparator in {"equals", "within"}:
                self._cond(or_pos, operand[0].start, "$gte", path, False, name)
                self._cond(or_pos, operand[-1].end, "$lte", path, False, name)
            elif comparator in {"contains", "intersects"}:
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

        if comparator in {"$geoIntersects", "$geoWithin"}:  # operand :
                                                            # [x, y] or [[x, y]] -> Point ;
                                                            # [[x1, y1], [x2, y2]] -> LineString ;
                                                            # [[x1, y1], [x2, y2], [x3, y3], ...] or [[x1, y1], [x2, y2], [x3, y3], ..., [x1, y1]] -> Polygon.
            if isinstance(operand, list):
                if len(operand) == 1:
                    geom_type = "Point"
                    coordinates = operand[0]
                elif (len(operand) > 1 and not isinstance(operand[0], list)):
                    geom_type = "Point"
                    coordinates = operand
                elif len(operand) == 2:
                    geom_type = "LineString"
                    coordinates = operand
                elif len(operand) > 2:
                    if not operand[-1] == operand[0]:
                        operand.append(operand[0])
                    geom_type = "Polygon" # Polygons are assumed not to have multiple rings.
                    coordinates = [operand]
                operand = {"$geometry" : {"type" : geom_type, "coordinates" : coordinates}}
            elif isinstance(operand, dict) and '$geometry' not in operand:
                operand = {"$geometry" : operand}
        elif comparator == "$geoNear": # $geoNear est un stage Mongo en soi
            self._geonear | kwargs
            if 'distanceField' not in self._geonear: raise ArgumentError("distanceField missing in MongoDB stage $geoNear.")
            return

        cond_0 = {comparator : operand}

        if inverted:
            if path in self._match_2[or_pos]:
                if "$nor" in self._match_2[or_pos][path]:
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
        self._geonear = {}
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
        if self._set:
            self._request.append({"$set" : self._set})
        if self._geonear: self._request.append({"$geoNear" : self._geonear})
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
            for item in cursor: result.append(Observation.from_obj(item)) # à adapter pour permettre la sélection du bon format des données dans la base
        else:
            result = [self._filtered_observation(item) for item in self.data]            
            for item in cursor: result.append(self._filtered_observation(Observation.from_obj(item)))
        if single: return self._fusion(result)
        else: return self._fusion(result, True)

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
        #cond = {"comparator" : comparator, "operand" : operand, "path" : path, "name" : name} and sometimes can contain "inverted" or "formatstring"
        if cond is None: return True
        if cond["comparator"] is None and cond["operand"] is None: return True

        if cond["name"] == "datation":
            if "formatstring" in cond:
                if not isinstance(item, datetime.datetime):
                    item = datetime.datetime.strptime(item, cond["formatstring"])
                if not isinstance(cond["operand"], datetime.datetime):
                    cond["operand"] = datetime.datetime.strptime(cond["operand"], cond["formatstring"])
            elif isinstance(item, TimeSlot):
                if cond["comparator"] in dico_alias[type(cond["comparator"])]:
                    cond["comparator"] = dico_alias[type(cond["comparator"])][cond["comparator"]]
                    return item.link(cond["operand"])[0] == cond["comparator"]
                else:
                    if cond["comparator"] in {"$gte", "gte", ">=", "=>"}:
                        if "inverted" in cond and cond["inverted"]: return item.bounds[0] >= cond["operand"]
                        else: return item.bounds[1] >= cond["operand"]
                    elif cond["comparator"] in {"$gt", "gt", ">"}         :
                        if "inverted" in cond and cond["inverted"]: return item.bounds[0] > cond["operand"]
                        else: return item.bounds[1] > cond["operand"]
                    elif cond["comparator"] in {"$lte", "lte", "<=", "=<"}:
                        if "inverted" in cond and cond["inverted"]: return item.bounds[1] <= cond["operand"]
                        else: return item.bounds[0] <= cond["operand"]
                    elif cond["comparator"] in {"$lt", "lt", "<"}         :
                        if "inverted" in cond and cond["inverted"]: return item.bounds[1] < cond["operand"]
                        else: return item.bounds[0] < cond["operand"]
                    else: raise ValueError("Comparator not supported for TimeSlot.")
        elif cond["name"] == "location":
            #changer listes en géométries. pour les str ? et séparation par name encore pertinente ?
            if cond["comparator"] in {"$eq", "eq", "=", "==", "$equals", "equals"}            : return item.equals(cond["operand"])
            elif cond["comparator"] in {"$geowithin", "geowithin", "$geoWithin", "geoWithin", "$within", "within"} : return item.within(cond["operand"])
            elif cond["comparator"] in {"$disjoint", "disjoint"}                              : return item.disjoint(cond["operand"])
            elif cond["comparator"] in {"$intersects", "intersects"}                          : return item.intersects(cond["operand"])
            elif cond["comparator"] in {"$touches", "touches"}                                : return item.touches(cond["operand"])
            elif cond["comparator"] in {"$overlaps", "overlaps"}                              : return item.overlaps(cond["operand"])
            elif cond["comparator"] in {"$contains", "contains"}                              : return item.contains(cond["operand"])
            elif cond["comparator"] not in {"$geonear", "geonear", "$geoNear", "geoNear"}     : return True # no equivalent for this MongoDB operator in shapely
        elif cond["name"] == "property": # assuming that property contains dicts and that the query targets one of its values
            for val in item.values():
                if self._condcheck_0(val, cond | {"name" : None}, datatype):
                    return True
            return False

        if cond["comparator"] in {"$eq", "eq", "=", "=="}     : return item == cond["operand"]
        elif cond["comparator"] in {"$gte", "gte", ">=", "=>"}: return item >= cond["operand"]
        elif cond["comparator"] in {"$gt", "gt", ">"}         : return item >  cond["operand"]
        elif cond["comparator"] in {"$lte", "lte", "<=", "=<"}: return item <= cond["operand"]
        elif cond["comparator"] in {"$lt", "lt", "<"}         : return item <  cond["operand"]
        elif cond["comparator"] in {"$in", "in"}              : return item in cond["operand"]
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
        elif cond["comparator"] == "$in":
            if isinstance(cond["operand"], list) and len(cond["operand"]) > 0:
                return self._compatibletypes(item, cond | {"operand" : cond["operand"][0], "comparator" : None})
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

    def _fusion(self, obsList, samename = False): #n'a pas sa place ici, à déplacer comme constructeur d'Observation ou ailleurs
        '''
        Takes a list of observations and returns one observation mixing them together in one single observation
        or a list of observations where all observations sharing the same name are fused together.
        '''
        if len(obsList) == 1:
            return obsList[0]
        elif len(obsList) > 1:
            if not samename:
                obs = obsList[0].mix(obsList[1])
                for item in obsList[2:]:
                    obs = obs.mix(item)
                return obs
            else:
                new_obsList = []
                dict_names = {}
                for item in obsList:
                    if item.name in dict_names:
                        new_obsList[dict_names[item.name]].mix(item)
                    else:
                        new_obsList.append(item)
                        dict_names[item.name] = len(new_obsList) - 1
                return new_obsList