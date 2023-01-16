'''
# How to use observation.essearch ?

1. **Create the MongoDB database:**
You can easily create an account on MongoDB. Once you have a database, follow the guidelines [here](https://www.mongodb.com/docs/atlas/tutorial/connect-to-your-cluster/#connect-to-your-atlas-cluster) to connect to it using pymongo.
All you need in order to be able to use this module is to be able to connect to the Collection with pymongo.

2. **Fill the database with your data:**
Construct an observation or a list of observations containing your data using dedicated functions from `observation.Observation`. 
You can then use either `insert_one_to_mongo(collection, observation)` or `insert_many_to_mongo(collection, observation_list)` to insert it in the database.

3. **Write a request using observation.ESSearch:**
An `ESSearch` instance must be created with either a MongoDB Collection (passed as argument **collection**) or a list of observations (passed as argument **data**).
Criteria for the query are then added one by one using `ESSearch.addCondition` or `ESSearch.orCondition`, or all together with `ESSearch.addConditions` or passed as argument **parameters** of ESSearch.

A condition is composed of:
- a **name** of a column or an exact **path** giving which element is concerned by the condition (name is a shortcut allowing not to enter a full path);
- an **operand** which is the item of the comparison (if omitted, the existence of the path is tested);
- a **comparator** which can be applied on the operand, for example '>=' or 'within' (defaults to equality in most cases);
- optional parameters detailed in `ESSearch.addCondition` documentation, like **inverted** to add a *not*.

Execute the research with `ESSearch.execute()`. Put the parameter **single** to True if you want the return to be a single observation
instead of a list of observations.

Example of python code using observation.essearch module:
```python
from pymongo import MongoClient
from observation.essearch import ESSearch
import datetime

client = Mongoclient(<Mongo-auth>)
collection = client[<base>][<collection>]

# In this example, we search for measures of property PM25 taken between 2022/01/01 
# and 2022/31/12 and we ensure the measure is an Observation.
# We execute with argument single = True to merge the result in one single
# Observation.

# Option 1
srch = ESSearch(collection)
srch.addCondition('datation', datetime.datetime(2022, 1, 1), '>=')
srch.addCondition('datation', datetime.datetime(2022, 12, 31), '<=')
srch.addCondition('property', 'PM25')
srch.addCondition(path = 'type', comparator = '==', operand = 'observation')
result = srch.execute(single = True)

# Option 2 (equivalent to option 1 but on one line)
result = ESSearch(collection,
                [['datation', datetime.datetime(2022, 1, 1), '>='], 
                ['datation', datetime.datetime(2022, 12, 31), '<='], 
                ['property', 'PM25'], 
                {'path': 'type', 'comparator': '==', 'operand': 'observation'}] 
                ).execute(single = True)
```
'''
import datetime
import shapely.geometry
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.command_cursor import CommandCursor
from esobservation import Observation
from iindex import Iindex
from util import util
from timeslot import TimeSlot
import bson

dico_alias_mongo = { # dictionnary of the different names accepted for each comparator and each given type. <key>:<value> -> <accepted name>:<name in MongoDB>
    # any type other than those used as keys is considered non valid
    str : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "in":"$in", "$in":"$in",
        "regex":"$regex", "$regex":"$regex",
        "oid":"$oid","$oid":"$oid"
    },
    int : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "gte":"$gte", ">=":"$gte", "=>":"$gte", "$gte":"$gte",
        "gt":"$gt", ">":"$gt", "$gt":"$gt",
        "lte":"$lte", "<=":"$lte", "=<":"$lte", "$lte":"$lte",
        "lt":"$lt", "<":"$lt", "$lt":"$lt",
        "in":"$in", "$in":"$in"
    },
    datetime.datetime : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "gte":"$gte", ">=":"$gte", "=>":"$gte", "$gte":"$gte",
        "gt":"$gt", ">":"$gt", "$gt":"$gt",
        "lte":"$lte", "<=":"$lte", "=<":"$lte", "$lte":"$lte",
        "lt":"$lt", "<":"$lt", "$lt":"$lt",
        "in":"$in", "$in":"$in"
    },
    TimeSlot : {
        None:"within",
        "eq":"within", "=":"within", "==":"within", "$eq":"within", "within":"within", "within":"within",
        "contains":"intersects", "$contains":"intersects",
        "in":"within", "$in":"within", "within":"within", "$within":"within",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"intersects", "$intersects":"intersects"
    },
    list : { # lists are interpreted as geometries
        None:"$geoIntersects",
        "eq":"equals", "=":"equals", "==":"equals", "$eq":"equals", "equals":"equals", "$equals":"equals",
        "$geowithin":"$geoWithin", "geowithin":"$geoWithin", "$geoWithin":"$geoWithin", "geoWithin":"$geoWithin", "within":"$geoWithin", "$within":"$geoWithin",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"$geoIntersects", "$intersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geointersects":"$geoIntersects", "geoIntersects":"$geoIntersects", "$geoIntersects":"$geoIntersects",
        "touches":"touches", "$touches":"touches",
        "overlaps":"overlaps", "$overlaps":"overlaps",
        "contains":"contains", "$contains":"contains",
        "$geoNear":"$geoNear", "$geonear":"$geoNear", "geonear":"$geoNear", "geoNear":"$geoNear",
        
        "in":"$in", "$in":"$in" # only in case where a list is not a geometry
    },
    bson.objectid.ObjectId : {
        None:"$eq",
        "eq":"$eq", "=":"$eq", "==":"$eq", "$eq":"$eq",
        "in":"$in", "$in":"$in"
    }
}
dico_alias_mongo[float] = dico_alias_mongo[int]

_geoeq    = lambda x, y: x.equals(y)
_geowith  = lambda x, y: x.within(y)
_geodis   = lambda x, y: x.disjoint(y)
_geointer = lambda x, y: x.intersects(y)
_geotou   = lambda x, y: x.touches(y)
_geoover  = lambda x, y: x.overlaps(y)
_geocont  = lambda x, y: x.contains(y)
_geonear  = lambda x, y: True

_defeq    = lambda x, y: x == y
_defsupeq = lambda x, y: x >= y
_defsup   = lambda x, y: x > y
_definfeq = lambda x, y: x <= y
_definf   = lambda x, y: x < y
_defin    = lambda x, y: x in y

_timsupeq_0 = lambda x, y: x.bounds[0] >= y
_timsup_0   = lambda x, y: x.bounds[0] > y
_timinfeq_0 = lambda x, y: x.bounds[0] <= y
_timinf_0   = lambda x, y: x.bounds[0] < y
_timsupeq_1 = lambda x, y: x.bounds[1] >= y
_timsup_1   = lambda x, y: x.bounds[1] > y
_timinfeq_1 = lambda x, y: x.bounds[1] <= y
_timinf_1   = lambda x, y: x.bounds[1] < y

dico_alias_python = {
    TimeSlot : { # only used in python filtering part
        None:"equals",
        "eq":"equals", "=":"equals", "==":"equals", "$eq":"equals", "equals":"equals", "$equals":"equals",
        "contains":"contains", "$contains":"contains",
        "in":"within", "$in":"within", "within":"within", "$within":"within",
        "disjoint":"disjoint", "$disjoint":"disjoint",
        "intersects":"intersects", "$intersects":"intersects",
        
        True: {
            "$gte":_timsupeq_0, "gte":_timsupeq_0, ">=":_timsupeq_0, "=>":_timsupeq_0,
            "$gt":_timsup_0, "gt":_timsup_0, ">":_timsup_0,
            "$lte":_timinfeq_1, "lte":_timinfeq_1, "<=":_timinfeq_1, "=<":_timinfeq_1,
            "$lt":_timinf_1, "lt":_timinf_1, "<":_timinf_1
        },
        False: {
            "$gte":_timsupeq_1, "gte":_timsupeq_1, ">=":_timsupeq_1, "=>":_timsupeq_1,
            "$gt":_timsup_1, "gt":_timsup_1, ">":_timsup_1,
            "$lte":_timinfeq_0, "lte":_timinfeq_0, "<=":_timinfeq_0, "=<":_timinfeq_0,
            "$lt":_timinf_0, "lt":_timinf_0, "<":_timinf_0
        }
    },
    'geometry' : { # lists are interpreted as geometries
        None:_geointer,
        "eq":_geoeq, "=":_geoeq, "==":_geoeq, "$eq":_geoeq, "equals":_geoeq, "$equals":_geoeq,
        "$geowithin":_geowith, "geowithin":_geowith, "$geoWithin":_geowith, "geoWithin":_geowith, "within":_geowith, "$within":_geowith,
        "disjoint":_geodis, "$disjoint":_geodis,
        "intersects":_geointer, "$intersects":_geointer, "geoIntersects":_geointer, "$geointersects":_geointer, "geoIntersects":_geointer, "$geoIntersects":_geointer,
        "touches":_geotou, "$touches":_geotou,
        "overlaps":_geoover, "$overlaps":_geoover,
        "contains":_geocont, "$contains":_geocont,
        "$geoNear":_geonear, "$geonear":_geonear, "geonear":_geonear, "geoNear":_geonear
    },
    'default' : {
        None:_defeq,
        "eq":_defeq, "=":_defeq, "==":_defeq, "$eq":_defeq,
        "gte":_defsupeq, ">=":_defsupeq, "=>":_defsupeq, "$gte":_defsupeq,
        "gt":_defsup, ">":_defsup, "$gt":_defsup,
        "lte":_definfeq, "<=":"$lte", "=<":_definfeq,
        "lt":_definf, "<":_definf, "$lt":_definf,
        "in":_defin, "$in":_defin
    }
}

def insert_from_doc(collection, document , info=True):
    '''Inserts all observations from a document into a collection, where each line of the document corresponds to an observation.'''
    with open(document, 'r') as doc:
        for line in doc:
            try: insert_one_to_mongo(collection, line, info)
            except: pass

def insert_to_mongo(collection, obj, info=True):
    '''Takes an observation or a list of observations and inserts them into a MongoDB collection, with info by default.'''
    # Faire une fonction pour permettre l'ajout direct de fichiers csv.
    inserted_list = []
    if isinstance(obj, list):
        pile = obj
    elif isinstance(obj, Observation):
        pile = [obj]
    else:
        pile = [Observation.from_obj(obj)]
    for obs in pile:
        if obs.id: obs_hash = obs.id
        else: obs_hash = hash(obs)
        metadata = {'type': "observationMetadata", 'id': obs_hash}
        if obs.name : metadata['name']  = obs.name
        if obs.param: metadata['param'] = obs.param
        metadata['information'] = Observation._info(True)#, True)
        inserted_list.append(metadata)
        if len(obs.lname) == 1:
            for line in obs:
                inserted_list.append({obs.lname[0]: util.json(line, encoded=False, typevalue=None, simpleval=False, geojson=True),
                                        '_hash': obs_hash})
        elif len(obs.lname) > 1:
            for line in obs:
                inserted_list.append({obs.lname[i]: util.json(line[i], encoded=False, typevalue=None, simpleval=False, geojson=True) 
                                                                for i in range(len(line))} | {'_hash': obs_hash})
    if inserted_list != []: collection.insert_many(inserted_list)

def insert_one_to_mongo(collection, obj, info=True):
    '''Takes an object and inserts it into a MongoDB collection, with info by default.'''
    if not isinstance(obj, Observation): obj = Observation.from_obj(obj)
    dico2 = obj.json(json_info=info, modecodec='dict', geojson=True)
    collection.insert_one(dico2)

def insert_many_to_mongo(collection, objList, info=True):
    '''Takes an object and inserts it into a MongoDB collection, with info by default.'''
    for i in range(len(objList)):
        if not isinstance(objList[i], Observation): objList[i] = Observation.from_obj(objList[i])
        objList[i] = objList[i].json(json_info=info, modecodec='dict', geojson=True)
    collection.insert_many(objList)

def empty_request(collection):
    """
    Empty request to get an idea of what the database contains.
    Currently returns the count of elements in the collection and the names of each column.
    """
    count = 0
    column_names = []
    cursor = collection.find()
    for doc in cursor:
        count += 1
        for column_name in doc['data']:
            if column_name not in column_names:
                column_names.append(column_name)
    return count, column_names

class ESSearch:
    """
    An `ESSearch` is defined as an ensemble of conditions to be used to execute a MongoDB request or any iterable containing only observations.

    *Attributes (for @property, see methods)* :

    - **input** : input on which the query is done. One of or a list of these : 
        - pymongo.collection.Collection
        - pymongo.cursor.Cursor
        - pymongo.command_cursor.CommandCursor
        - Observation (can be defined from a str or a dict)
    - **parameters** : list of list of conditions for queries, to be interpreted as : parameters = [[cond_1 AND cond_2 AND cond_3] OR [cond_4 AND cond_5 AND cond_6]] where conds are criteria for queries
    - **hide** : list of paths to hide from the output
    - **heavy** : boolean indicating whether the request should be simplified or not
    - **sources** : attribute used to indicate the sources of the data in param

    The methods defined in this class are (documentations in methods definitions):
    
    *setter*

    - `ESSearch.addInput`
    - `ESSearch.removeInputs`
    - `ESSearch.setHide`
    - `ESSearch.setHeavy`
    - `ESSearch.clear`
    
    *dynamic value (getter @property)*

    - `ESSearch.request`
    - `ESSearch.cursor`
    
    *parameters for query - update methods*

    - `ESSearch.addConditions`
    - `ESSearch.addCondition`
    - `ESSearch.orCondition`
    - `ESSearch.removeCondition`
    - `ESSearch.clearConditions`

    *query method*

    - `ESSearch.execute`
    """
    def __init__(self,
                    input = None,
                    parameters = None,
                    hide = [],
                    heavy = False,
                    sources = None, 
                    **kwargs
                    ):
        '''
        ESSearch constructor. Parameters can also be defined and updated using class methods.

        *Arguments*

        - **input** : input on which the query is done. Must be one of or a list of these (can be nested): 
            - pymongo.collection.Collection
            - pymongo.cursor.Cursor
            - pymongo.command_cursor.CommandCursor
            - Observation
            - str corresponding to a json Observation
            - dict corresponding to a json Observation
        - **parameters** :  dict, list (default None) - list of list or list of dictionnaries whose keys are arguments of ESSearch.addCondition method
        ex: parameters = [
            {'name' : 'datation', 'operand' : datetime.datetime(2022, 9, 19, 1), 'comparator' : '>='},
            {'name' : 'property', 'operand' : 'PM2'}
        ]
        - **hide** : list (default []) - List of strings where strings correspond to paths to remove from the output
        - **heavy** :  bool (default False) - Must be True when values are defined directly and inside dictionnaries simultaneously.
        - **sources** : (default None) - Optionnal parameter indicating the sources of the data in case when a query is executed with parameter single = True.
        - **kwargs** :  other parameters are used as arguments for ESSearch.addCondition method.
        '''
        self.parameters = [[]]                                          # self.parameters
        if isinstance(hide, list): self.hide = hide                     # self.hide
        else: raise TypeError("hide must be a list.")

        if isinstance(heavy, bool): self.heavy = heavy                  # self.heavy
        else: raise TypeError("heavy must be a bool.")
        self.sources = sources                                          # self.sources

        self.input = []                                                 # self.input
        if isinstance(input, list): pile = input
        else: pile = [input]
        while not len(pile) == 0:
            obj = pile.pop()
            if isinstance(obj, list):
                pile += obj
            elif isinstance(obj, (Collection, Cursor, CommandCursor, Observation)):
                self.input.append(obj)
            elif isinstance(obj, (str, dict)):
                try:
                    self.input.append(Observation.from_obj(obj))
                except:
                    raise ValueError("Cannot convert " + str(obj) + " to an Observation ")
            elif obj is not None:
                raise TypeError("Unsupported type for input " + str(obj))

        if parameters: self.addConditions(parameters)
        if kwargs: self.addCondition(**kwargs)

    def __repr__(self):
        return "ESSearch(input = " + str(self.input) + ", parameters = " + str(self.parameters) + ")"

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

    def addInput(self, input):
        """
        Adds one or many inputs on which the query is to be executed given by argument input
        """
        added_input = []
        if isinstance(input, list): pile = input
        else: pile = [input]
        while not len(pile) == 0:
            obj = pile.pop()
            if isinstance(obj, list):
                pile += obj
            elif isinstance(obj, (Collection, Cursor, CommandCursor, Observation)):
                added_input.append(obj)
            elif isinstance(obj, (str, dict)):
                try:
                    added_input.append(Observation.from_obj(obj))
                except:
                    raise ValueError("Cannot convert " + str(obj) + " to an Observation ")
            elif obj is not None:
                raise TypeError("Unsupported type for input " + str(obj))
        self.input += added_input

    def removeInputs(self):
        """
        Removes all inputs from self.
        """
        self.input = []

    def setHide(self, hide):
        '''
        Sets self.hide to a value given by argument hide.
        '''
        if isinstance(hide, list): self.hide = hide
        else: raise TypeError("hide must be a list.")
        
    def setHeavy(self, heavy):
        '''
        Sets self.heavy to a value given by argument heavy.
        '''
        if isinstance(heavy, list): self.heavy = heavy
        else: raise TypeError("heavy must be a bool.")

    def setSources(self, sources):
        '''
        Sets self.sources to a value given by argument sources.
        '''
        self.sources = sources

    def addConditions(self, parameters):
        '''
        Takes multiple parameters and applyes self.addCondition() on each of them.
        '''
        if isinstance(parameters, dict):
            self.addCondition(**parameters)
        elif isinstance(parameters, (list, tuple)):
            for parameter in parameters:
                if isinstance(parameter, dict): self.addCondition(**parameter)
                elif isinstance(parameters, (list, tuple)): self.addCondition(*parameter)
                else: self.addCondition(parameter)
        else: raise TypeError("parameters must be either a dict or a list of dict.")
            
    def addCondition(self, name = None, operand = None, comparator = None, path = None, or_position = -1, **kwargs):
        '''
        Takes parameters and inserts corresponding query condition in self.parameters.

        *Parameters*

        - **name** :  str (default None) - name of an IIndex, which corresponds to an Ilist column name.
                    (ex: 'datation', 'location', 'property')
                    This parameter is used to give a default value to parameters path and unwind.

        - **operand** :  - (default None) - Object used for the comparison.
                    (ex: if we search for observations made in Paris, operand is 'Paris')

        - **comparator**:  str (default None) - str giving the comparator to use. (ex: '>=', 'in')

        - **path** :  str (default None) - to use to define a precise MongoDB path. When name is given, default path is data.*name*.value.codec
        
        - **or_position** :  int (default -1) - position in self.parameters in which the condition is to be inserted.

        - **formatstring** :  str (default None) - str to use to automatically change str to datetime before applying condition. 
                    Does not update the data base. If value is set to 'default', format is assumed to be Isoformat.
        
        - **inverted** :  bool (default None) - to add a "not" in the condition.
                    To use in case where every element of a MongoDB array (equivalent to python list) must verify the condition (by default, condition is verified when at least one element of the array verifies it).
        
        - **unwind** :  int (default None) - int corresponding to the number of additional {"$unwind" : "$" + path} to be added in the beginning of the query.
        
        - **regex_options** :  str (default None) - str associated to regex options (i, m, x and s). See [this link](https://www.mongodb.com/docs/manual/reference/operator/query/regex/) for more details.

        no comparator => default comparator associated with operand type in dico_alias_mongo is used (mainly equality)
        no operand => only the existence of something located at path is tested
        '''
        if name is not None and not isinstance(name, str): raise TypeError("name must be a str.")
        if comparator is not None and not isinstance(comparator, str): raise TypeError("comparator must be a str.")
        if path is not None and not isinstance(path, str): raise TypeError("path must be a str.")
        if or_position is not None and not isinstance(or_position, int): raise TypeError("or_position must be an int.")

        if name is None and operand is None and comparator is None and path is None:
            raise ValueError("ESSearch.addCondition() requires at least one of these parameters : name, operand or path.")

        for item in kwargs:
            if item not in {'formatstring', 'inverted', 'unwind', 'regex_options', 'distanceField', 'distanceMultiplier', 'includeLocs', 'key', 'maxDistance', 'minDistance', 'near', 'query', 'spherical'}:
                raise ValueError("Unknown parameter : ", item)

        if isinstance(operand, datetime.datetime) and (operand.tzinfo is None or operand.tzinfo.utcoffset(operand) is None):
            operand = operand.replace(tzinfo=datetime.timezone.utc)

        if path is None: # default values for path when not defined
            if name:
                if name in {"$year", "$month", "$dayOfMonth", "$hour", "$minute", "$second", "$millisecond", "$dayOfYear", "$dayOfWeek"}:
                    path = "data.datation.value.codec"
                else:
                    path = name #"data." + name + ".value.codec" # there is no default case when name == "name": path is set to "data.name.value.cod" and not to "name"
            else: path = "data"

        if operand:
            try: comparator = dico_alias_mongo[type(operand)][comparator]
            except: raise ValueError("Incompatible values for comparator and operand. Ensure parameters are in the correct order.")
        elif comparator:
            raise ValueError("operand must be defined when comparator is used.")

        condition = {"comparator" : comparator, "operand" : operand, "path" : path, "name" : name} | kwargs

        if or_position >= len(self.parameters):
            self.parameters.append([condition])
        else:
            self.parameters[or_position].append(condition)

    def orCondition(self, *args, **kwargs):
        '''
        Adds a condition in a new sublist in self.parameters. Separations in sublists correspond to "or" in the query.
        '''
        self.addCondition(or_position = len(self.parameters), *args, **kwargs)

    def removeCondition(self, or_position = None, condnum = None):
        '''
        Removes a condition from self.parameters. By default, last element added is removed.
        Otherwise, the removed condition is the one at self.parameters[or_position][condnum].

        To remove all conditions, use ESSearch.clearConditions() method.
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

    def clearConditions(self):
        '''
        Removes all conditions from self.parameters.
        To remove all attributes, use ESSearch.clear() method.
        '''
        self.parameters = [[]]

    def clear(self):
        '''
        Resets self
        '''
        self = ESSearch()

    def _cond(self, or_pos, operand, comparator, path, inverted = False, name = None, formatstring = None, unwind = None, regex_options = None, **kwargs):
        '''
        Takes parameters and adds corresponding MongoDB expression to self._match.
        self._unwind and self._set are updated when necessary.
        '''
        if unwind: # unwind is applied by default when name is used and controlled precisely with parameter unwind
            if isinstance(unwind, str):
                self._unwind.append(unwind)
            elif isinstance(unwind, int):
                for _ in range(unwind): self._unwind.append(path)
            elif isinstance(unwind, tuple): # format : (<path>, <unwind quantity>)
                for _ in range(unwind[1]): self._unwind.append(unwind[0])
            else: raise TypeError("unwind must be a tuple, a str or an int.")
        #elif name and operand and "data." + name + ".value" not in self._unwind: self._unwind.append("data." + name + ".value")

        if self.heavy and operand is not None:
            if path not in self._heavystages: self._heavystages.add(path) # peut-être mieux de laisser l'utilisateur choisir manuellement
            path = "_" + path + ".v"

        if operand is None: # no operand => we only test if there is something located at path or at path given by name
            comparator = "$exists"
            operand = 1
        else:
            try: comparator = dico_alias_mongo[type(operand)][comparator] #global variable
            except:
                if formatstring:
                    try: comparator = dico_alias_mongo[datetime.datetime][comparator]
                    except: raise ValueError("Comparator not allowed.")
                elif isinstance(operand, shapely.geometry.base.BaseGeometry):
                    operand = {"type" : operand.geom_type, "coordinates" : list(operand.exterior.coords)}
                else: raise ValueError("Comparator not allowed.")

        if name in {"$year", "$month", "$dayOfMonth", "$hour", "$minute", "$second", "$millisecond", "$dayOfYear", "$dayOfWeek"}:
            self._set |= {name[1:]: {name : path}} #à tester
            path = name[1:]
            self._project |= {name[1:]:0}

        if isinstance(operand, TimeSlot): #equals->within, contains->intersects, within, disjoint, intersects
            if comparator == "within":
                self._cond(or_pos, operand[0].start, "$gte", path, False, name)
                self._cond(or_pos, operand[-1].end, "$lte", path, False, name)
            elif comparator == "intersects":
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
                                                            # [[x1, y1], [x2, y2], [x3, y3], ...] or [[x1, y1], [x2, y2], [x3, y3], ..., [x1, y1]] or [[[x1, y1], [x2, y2], [x3, y3], ..., [x1, y1]]] -> Polygon.
            if isinstance(operand, list):
                if not isinstance(operand[0], list):
                    geom_type = "Point"
                    coordinates = operand
                elif not isinstance(operand[0][0], list):
                    if len(operand) == 1:
                        geom_type = "Point"
                        coordinates = operand[0]
                    elif len(operand) == 2:
                        geom_type = "LineString"
                        coordinates = operand
                    elif len(operand) > 2:
                        if not operand[-1] == operand[0]:
                            operand.append(operand[0])
                        geom_type = "Polygon"
                        coordinates = [operand]
                    else: raise ValueError("Unable to define a geometry from " + str(operand))
                else:
                    geom_type = "Polygon"
                    coordinates = operand
                operand = {"$geometry" : {"type" : geom_type, "coordinates" : coordinates}}
            elif isinstance(operand, dict) and '$geometry' not in operand:
                operand = {"$geometry" : operand}
        elif comparator == "$geoNear": # $geoNear is a MongoDB stage
            self._geonear = self._geonear | kwargs
            if 'distanceField' not in self._geonear: raise ValueError("distanceField missing in MongoDB stage $geoNear.")
            return
        
        if comparator == "$regex" and regex_options:
            cond_0 = {"$regex" : operand, "$options" : regex_options}
        else:
            cond_0 = {comparator : operand}
        
        if inverted:
            if path in self._match[or_pos]:
                if "$nor" in self._match[or_pos][path]:
                    self._match[or_pos][path]["$nor"].append(cond_0)
                elif "not" in self._match[or_pos][path]:
                    self._match[or_pos][path]["$nor"] = [self._match[or_pos][path]["$not"], cond_0]
                    del self._match[or_pos][path]["$not"]
                else:
                    self._match[or_pos][path]["$not"] = cond_0
            else:
                self._match[or_pos][path] = {"$not" : cond_0}
        else:
            if path not in self._match[or_pos]:
                self._match[or_pos][path] = cond_0
            else:
                self._match[or_pos][path] |= cond_0

    def _fullSearchMongo(self):
        """
        Takes self.parameters and returns a MongoDB Aggregation query.
        """
        request = []
        self._match = []
        self._unwind = []
        self._heavystages = set() # two additional set stages when format is too unknown
        self._set = {}
        self._geonear = {}
        self._match = []

        for i in range(len(self.parameters)): # rewriting conditions in MongoDB format
            self._match.append({})
            for cond in self.parameters[i]:
                self._cond(or_pos = i, **cond)

        if not self._unwind and not self.heavy and not self._set and not self._geonear:
            if self._match:
                j = 0
                for i in range(len(self._match)):
                    if self._match[i] and j != i: # removing empty elements in place
                        self._match[j] = self._match[i]
                        j += 1
                if j == 0: # when there is no $or
                    if self._match[0]: match = self._match[0]
                else: # when there is a $or
                    match = {"$or": self._match[:j]}
            return 'find', match
        else:
            if self._unwind:                                                    # Mongo $unwind stage
                for unwind in self._unwind:
                    request.append({"$unwind" : "$" + unwind})
            if self._heavystages:                                               # additional Mongo $set stage
                heavy = {}
                for path in self._heavystages:
                    heavy |= {"_"+path:{"$cond":{"if":{"$eq":[{"$type":"$"+path},"object"]},"then":{"$objectToArray":"$"+path},"else": {"v":"$"+path}}}}
                request.append({"$set" : heavy})
            if self._set: request.append({"$set" : self._set})                  # Mongo $set stage
            if self._geonear: request.append({"$geoNear" : self._geonear})      # Mongo $geoNear stage
            if self._match:                                                     # Mongo $match stage
                j = 0
                for i in range(len(self._match)):
                    if self._match[i] and j != i:
                        self._match[j] = self._match[i]
                        j += 1
                if j == 0: # when there is no $or
                    if self._match[0]: request.append({"$match" : self._match[0]})
                else: # when there is a $or
                    request.append({"$match" : {"$or": self._match[:j]}})
            if self._unwind:                                                    # Second Mongo $set stage when unwind not empty
                dico = {}
                for unwind in self._unwind:
                    if not unwind in dico: dico[unwind] = ["$" + unwind]
                    else: dico[unwind] = [dico[unwind]]
                request.append({"$set" : dico})
            if self._project: request.append({"$project" : self._project})      # Mongo $project stage
            return 'aggregation', request

    @property
    def request(self):
        '''
        Getter returning the content of the aggregation query to be executed with ESSearch.execute().
        '''
        if self.heavy: self._project = {"_data" : 0}
        else: self._project = {}
        for el in self.hide: self._project |= {el : 0}
        request_type, request_content = self._fullSearchMongo()
        if request_type == 'find':
            return 'collection.find(' + str(request_content) + ', ' + str(self._project) + ')'
        else:
            return 'collection.aggregate(' + str(request_content) + ')'

    @property
    def cursor(self, input):
        '''
        Getter returning the cursors of the aggregation query result on all collections and cursors contained in self.input
        or on the argument input if given.
        '''
        if self.heavy: self._project = {"_data" : 0}
        else: self._project = {}
        for el in self.hide: self._project |= {el : 0}
        request_type, request_content = self._fullSearchMongo()
        if input: 
            if request_type == 'find':
                return input.find(request_content, self._project)
            else:
                return input.aggregate(request_content)
        cursor_list = []
        for item in self.input:
            if isinstance(item, (Collection, Cursor, CommandCursor)):
                if request_type == 'find':
                    cursor_list.append(item.find(request_content, self._project))
                else:
                    cursor_list.append(item.aggregate(request_content))
        if len(cursor_list) == 1:
            return cursor_list[0]
        else:
            return cursor_list

    def execute(self, returnmode = None, filtered = False, fillvalue = None):
        '''
        Executes the request and returns its result, either in one or many Observations.

        *Parameter*

        - **fitered** :  bool (default False) - Parameter to force filtering on Mongo out.
        - **returnmode** : str (default None) - Parameter giving the format of the output:
            - None: output is returned as it is in the database;
            - 'observation': Each element is returned as an observation, but original observations aren't recreated;
            - 'hashfused': observations whose hashes are the same are merged together; 
            - 'single': return a single observation merging all observations together.
        - **fillvalue** :  (default None) - Value to use to fill gaps when observations are fused together.
        '''
        result = []
        if self.heavy: self._project = {"_id" : 0, "_data" : 0}
        else: self._project = {"_id" : 0}
        for el in self.hide: self._project |= {el : 0}
        if returnmode != 'observation' and returnmode != 'hashfused': self._project |= {'_hash': 0}
        
        if self.parameters == [[]]:
            for data in self.input:
                if isinstance(data, Observation):
                    result.append(data)
                else:
                    cursor = data.find({'type': {'$not': {'$eq': 'observationMetadata'}}}, self._project)
                    for item in cursor:
                        if returnmode == 'observation' or returnmode == 'hashfused':
                            dic = {'idxdic': item}
                            try:
                                metadata = data.find_one({'type': 'observationMetadata', 'id': item['_hash']})
                                if 'name'   in metadata: dic['name']    = metadata['name']
                                if 'id'     in metadata: dic['id']      = str(metadata['id'])
                                if 'param'  in metadata: dic['param']   = metadata['param']
                                del item['_hash']
                                result.append(Observation.dic(**dic))
                            except: raise KeyError('Unable to retreive data. Try executing with returnmode = None. If you used parameter inverted, you should add more conditions in order not to return the whole collection.')
                        else:
                            result.append(Observation.dic(item))
        else:
            for data in self.input:
                if isinstance(data, Observation):
                    result.append(self._filtered_observation(item))
                else:
                    request_type, request_content = self._fullSearchMongo()
                    if request_type == 'find':
                        cursor = data.find(request_content, self._project)
                    else:
                        cursor = data.aggregate(request_content)
                    if filtered:
                        for item in cursor:
                            if returnmode == 'observation' or returnmode == 'hashfused':
                                dic = {'idxdic': item}
                                try:
                                    metadata = data.find_one({'type': 'observationMetadata', 'id': item['_hash']})
                                    if 'name'   in metadata: dic['name']    = metadata['name']
                                    if 'id'     in metadata: dic['id']      = str(metadata['id'])
                                    if 'param'  in metadata: dic['param']   = metadata['param']
                                    del item['_hash']
                                    obs_out = Observation.dic(**dic)
                                except: raise KeyError('Unable to retreive data. Try executing with returnmode = None. If you used parameter inverted, you should add more conditions in order not to return the whole collection.')
                            else:
                                obs_out = Observation.dic(item)
                            if obs_out:
                                result.append(self._filtered_observation(obs_out))
                    else:
                        for item in cursor:
                            if returnmode == 'observation' or returnmode == 'hashfused':
                                dic = {'idxdic': item}
                                try: 
                                    metadata = data.find_one({'type': 'observationMetadata', 'id': item['_hash']})
                                    if 'name'   in metadata: dic['name']    = metadata['name']
                                    if 'id'     in metadata: dic['id']      = str(metadata['id'])
                                    if 'param'  in metadata: dic['param']   = metadata['param']
                                    del item['_hash']
                                    obs_out = Observation.dic(**dic)
                                except: raise KeyError('Unable to retreive data. Try executing with returnmode = None. If you used parameter inverted, you should add more conditions in order not to return the whole collection.')
                            else:
                                obs_out = Observation.dic(item)
                            if obs_out:
                                result.append(obs_out)
        if returnmode == 'single': return self._fusion(result, fillvalue = fillvalue)
        elif returnmode == 'hashfused': return self._fusion(result, True, fillvalue)
        else: return result

    def _mongo_out_to_obs(self, dico):
        '''
        // Obsolete //
        Takes a dictionnary output by the Mongo request and filters it to return an Observation which contains only valid measures.
        '''
        valid_records = set()
        first_column = True
        for column_key in dico['data']:
            if first_column:
                for i in range(len(dico['data'][column_key]['value'])):
                    if isinstance(dico['data'][column_key]['value'][i]['record'], int):
                        valid_records.add(dico['data'][column_key]['value'][i]['record'])
                    elif isinstance(dico['data'][column_key]['value'][i]['record'], list):
                        for k in dico['data'][column_key]['value'][i]['record']:
                            valid_records.add(k)
                first_column = False
            else:
                next_valid_records = set()
                for i in range(len(dico['data'][column_key]['value'])):
                    if isinstance(dico['data'][column_key]['value'][i]['record'], int) and \
                            dico['data'][column_key]['value'][i]['record'] in valid_records:
                        next_valid_records.add(dico['data'][column_key]['value'][i]['record'])
                    elif isinstance(dico['data'][column_key]['value'][i]['record'], list):
                        for k in dico['data'][column_key]['value'][i]['record']:
                            if k in valid_records:
                                next_valid_records.add(k)
                valid_records = next_valid_records
            if len(valid_records) == 0: return None
        for column_key in dico['data']:
            k = 0
            for i in range(0, len(dico['data'][column_key]['value'])):
                if isinstance(dico['data'][column_key]['value'][i]['record'], int) and \
                        dico['data'][column_key]['value'][i]['record'] in valid_records:
                    if k < i :
                        dico['data'][column_key]['value'][k] = dico['data'][column_key]['value'][i]
                    k += 1
                elif isinstance(dico['data'][column_key]['value'][i]['record'], list):
                    new_record = []
                    for j in range(0, len(dico['data'][column_key]['value'][i]['record'])):
                        if dico['data'][column_key]['value'][i]['record'][j] in valid_records:
                            new_record.append(dico['data'][column_key]['value'][i]['record'][j])
                    if len(new_record) != 0:
                        dico['data'][column_key]['value'][k]['codec'] = dico['data'][column_key]['value'][i]['codec']
                        if len(new_record) == 1:
                            dico['data'][column_key]['value'][k]['record'] = new_record[0]
                        else:
                            dico['data'][column_key]['value'][k]['record'] = new_record
                        k += 1
            dico['data'][column_key]['value'] = dico['data'][column_key]['value'][:k]
        return Observation.from_obj(dico)

    def _filtered_observation(self, obs):
        '''
        Takes an Observation and returns a filtered Observation with self.parameters as a filter.
        '''
        # self.parameters = [[cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]
        # dico = {"data": [["datation", [date1, date2, date3], [0,1,0,2,2,1]], ["location", [loc1, loc2, loc3], [0,1,2,0]]]}
        if len(obs) == 0: return obs

        for i in range(len(self.parameters)):
            if self.parameters[i] != []:
                conds, next_relevant = self._newconds(obs, self.parameters[i])
                filter = util.funclist(obs.lindex[0].cod, self._condcheck, conds[0])
                if not isinstance(filter, list): filter = [filter]
                full_filter = util.tovalues(obs.lindex[0].keys, filter)
                for j in range(1, obs.lenidx):
                    next_filter = util.funclist(obs.lindex[j].cod, self._condcheck, conds[j])
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

    def _condcheck(self, item, parameter = None):
        '''
        Takes an item corresponding to an element of a column in an Observation and returns a Boolean if it verifies criteria given by parameter.
        '''
        # parameters = [cond_1 AND cond_2 AND cond_3]
        if not parameter: return True
        boolean = True
        for cond in parameter:
            boolean = boolean and self._condcheck_0(item, cond)
        return boolean

    def _condcheck_0(self, item, cond = None):
        '''
        Takes an item and returns a Boolean.
        Subfonction executed by _condcheck for each condition in parameter.
        '''
        #cond = {"comparator" : comparator, "operand" : operand, "path" : path, "name" : name} and sometimes can contain "inverted" or "formatstring"
        if cond is None: return True
        if cond["comparator"] is None and cond["operand"] is None: return True

        if "formatstring" in cond:
            if not isinstance(item, datetime.datetime):
                item = datetime.datetime.strptime(item, cond["formatstring"])
            if not isinstance(cond["operand"], datetime.datetime):
                cond["operand"] = datetime.datetime.strptime(cond["operand"], cond["formatstring"])
        elif isinstance(item, TimeSlot):
            if cond["comparator"] in dico_alias_python[TimeSlot]:
                cond["comparator"] = dico_alias_python[TimeSlot][cond["comparator"]]
                return item.link(cond["operand"])[0] == cond["comparator"]
            else:
                if not 'inverted' in cond and cond['inverted']: inverted = False
                else: inverted = True
                try: return dico_alias_python[TimeSlot][inverted](item, cond["operand"])
                except: raise ValueError("Comparator not supported for TimeSlot.")

        elif isinstance(item, list) or isinstance(item, shapely.geometry.base.BaseGeometry):
            if isinstance(item, list):
                if len(item) == 1: item = shapely.geometry.Point(item[0])
                elif (len(item) > 1 and not isinstance(item[0], list)): item = shapely.geometry.Point(item)
                elif len(item) == 2: item = shapely.geometry.LineString(item)
                elif len(item) > 2:
                    if not item[-1] == item[0]:
                        item.append(item[0])
                    item = shapely.geometry.Polygon([item])
            if isinstance(cond["operand"], list):
                if len(cond["operand"]) == 1: cond["operand"] = shapely.geometry.Point(cond["operand"][0])
                elif (len(cond["operand"]) > 1 and not isinstance(cond["operand"][0], list)):
                    cond["operand"] = shapely.geometry.Point(cond["operand"])
                elif len(cond["operand"]) == 2: cond["operand"] = shapely.geometry.LineString(cond["operand"])
                elif len(cond["operand"]) > 2:
                    if not item[-1] == item[0]:
                        item.append(item[0])
                    item = shapely.geometry.Polygon([item])
            return dico_alias_mongo['geometry'][cond["comparator"]](item, cond["operand"])
            
        elif cond["name"] == "property": # assuming that property contains dicts and that the query targets one of its values
            for val in item.values():
                if self._condcheck_0(val, cond | {"name" : None}):
                    return True
            return False

        try: return dico_alias_mongo['default'][cond["comparator"]](item, cond["operand"])
        except:
            #raise ValueError("Comparator not supported.")
            return True

    def _compatibletypes(self, item, cond):
        '''
        Takes an item and a condition and returns True if the condition can be applied on the item.
        ex: 3 > 1 makes sense (returns True), but 'cat' > 1 does not (returns False).
        (In this example, item = 3 or 'cat', cond = {'operand': 1, 'comparator': '>'})
        '''
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

    def _fusion(self, obsList, hashfused = False, fillvalue = None, name = None):
        '''
        Takes a list of observations and returns one observation merging them together in one single observation
        or a list of observations where all observations sharing the same name are fused together.
        '''
# NE FONCTIONNE PAS S'IL NE S'AGIT PAS D'UNE LISTE D'OBSERVATIONS
# parce que la conversion en observation est faite au sein d'execute et donc que les données entrées par le champ data ne sont pas converties
# à voir pour modifier fusion / l'intégrer comme méthode de Ilist/Observation / modifier execute.
# -> dans tous les cas, fait sens d'insérer fusion comme méthode d'Observation.
        if len(obsList) == 1:
            return obsList[0]
        elif len(obsList) > 1:
            if not hashfused:
                lidx = []
                new_lname = set()
                for obs in obsList:
                    new_lname |= set(obs.lname)
                new_lname = list(new_lname)
                
                for i in range(len(new_lname)): # for each column of the new Observation
                    values = []
                    for obs in obsList: # for each Observation in the list
                        if new_lname[i] in obs.lname: values += obs.lindex[obs.lname.index(new_lname[i])].values # values of the column are added to the new column
                        else: values += [fillvalue] * len(obs) # when there is no value, filled with fillvalue
                    codec = util.tocodec(values)
                    lidx.append(Iindex(codec, new_lname[i], util.tokeys(values, codec)))

                if name is None: name = "ESSearch query result on " + str(datetime.datetime.now())
                if self.sources:
                    sources = self.sources
                else:
                    sources = []
                    for item in self.input:
                        if isinstance(item, Observation):
                            if item.name is not None:
                                sources.append('Observation: ' + item.name)
                            else:
                                sources.append('data')
                        elif isinstance(item, Collection):
                            sources.append('MongoDB collection: ' + item.name + ' from database: ' + item.database.name)
                        elif isinstance(item, Cursor):
                            sources.append('Pymongo cursor: ' + item.cursor_id + ' from collection ' + item.collection.name + 
                                            ' from database: ' + item.collection.database.name)
                        elif isinstance(item, CommandCursor):
                            sources.append('Pymongo commandcursor: ' + item.cursor_id + ' from collection ' + item.collection.name + 
                                            ' from database: ' + item.collection.database.name)
                        else: # should not happen
                            sources.append('data')
                param = {'date': str(datetime.datetime.now()), 'project': 'essearch', 'type': 'dim3', 
                        'context': {'origin': 'ESSearch query', 'sources ': sources, 
                        'ESSearch_parameters': str(self.parameters)}}
                new_obs = Observation(lidx, name, param=param)
                return new_obs
            else:                   # à tester
                new_obsList = []
                dict_names = {}
                for item in obsList:
                    if item.name in dict_names:
                        new_obsList[dict_names[item.name]].append(item)
                    else:
                        new_obsList.append([item])
                        dict_names[item.name] = len(new_obsList) - 1
                for i in range(len(new_obsList)):
                    new_obsList[i] = self._fusion(new_obsList[i], False, fillvalue, new_obsList[i][0].name)
                return new_obsList
        else:
            if not hashfused:
                if self.sources:
                    sources = self.sources
                else:
                    sources = []
                    for item in self.input:
                        if isinstance(item, Observation):
                            if item.name is not None:
                                sources.append('Observation: ' + item.name)
                            else:
                                sources.append('data')
                        elif isinstance(item, Collection):
                            sources.append('MongoDB collection: ' + item.name + ' from database: ' + item.database.name)
                        elif isinstance(item, Cursor):
                            sources.append('Pymongo cursor: ' + item.cursor_id + ' from collection ' + item.collection.name + 
                                            ' from database: ' + item.collection.database.name)
                        elif isinstance(item, CommandCursor):
                            sources.append('Pymongo commandcursor: ' + item.cursor_id + ' from collection ' + item.collection.name + 
                                            ' from database: ' + item.collection.database.name)
                        else: # should not happen
                            sources.append('data')
                param = {'date': str(datetime.datetime.now()), 'project': 'essearch', 'type': 'dim3', 
                        'context': {'origin': 'ESSearch query', 'sources ': sources, 
                        'ESSearch_parameters': str(self.parameters)}}               
                return Observation(param=param)
            else: return []