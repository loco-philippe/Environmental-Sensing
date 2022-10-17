import datetime
from sqlite3 import Cursor
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
        "$geoNear":"$geoNear", "$geonear":"$geoNear", "geonear":"$geoNear", "geoNear":"$geoNear", #nécessite la présence d'un index 2dsphere
        
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

def insert_from_doc(collection, document = '..//Tests//json_examples.obs', info=True):
    with open(document, 'r') as doc:
        for line in doc:
            try: insert_to_mongo(collection, line, info)
            except: pass

def insert_to_mongo(collection, obj, info=True):
    """Takes an object and inserts it into a MongoDB collection with info.
    Just use collection.insert_one(obj) if you don't need to add query helpers"""
    #casser les observations à l'entrée dans Mongo pour permettre des recherches intéressantes. (implique recréation de la redondance)
    #corriger pour que dates restent au format date en entrée
    obs = Observation.from_obj(obj)
#### A REPRENDRE CAR NE PERMET PAS DE RENTRER datetime.datetime EN DATES ET shapely.geometry EN GEOMETRIE DANS MONGODB TEL QUEL
    dico2 = obs.json(json_info=info)
####
    collection.insert_one(dico2)

class ESSearch:
    #Modifier en une classe ESSearch qui peut faire la recherche sur une liste qui n'est pas dans MongoDB
    """
    Prend en entrée les paramètres de la requête et retourne la requête à effectuer.
    -> faire en sorte que l'on puisse ajouter tous les paramètres d'un coup, mais également ajouter/retirer un paramètre à la 
    fois. Être permissif sur les manières d'entrer les paramètres.
    __repr__ donne la liste des paramètres actuels... ou bien une méthode dediée le fait et __repr__ renvoie juste le nom de l'objet ?
    -> éventuellement, possibilité d'itérer sur les paramètres entrés pour les consulter un par un
    -> plutôt le rendre callable pour faciliter les modifications / ajouts / suppressions, avec les positions égales à celles des dictionnaires ?
    """
    def __init__(self, 
                    parameters = None,
                    data = None,
                    collection = None,
                    **kwargs
                    ):
        self.params = [[]]                      # params = [[cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]
        if isinstance(data, Observation):
            self.data = [data]
        else:
            self.data = data                    # list of observations 
        self.collection = collection            # MongoDB collection of observations
        if parameters: self.addParams(parameters)
        if kwargs: self.addCondition(**kwargs)

    def __repr__(self):
        return {"collection" : self.collection, "parameters" : self.params}

    def __str__(self):
        return str(self.request)

    def __iter__(self):
        self.n = -1
        return self

    def __next__(self):
        if self.n < len(self.params)-1:
            self.n += 1
            return self.params[self.n]
        else:
            raise StopIteration

    def __getitem__(self, key):
        return self.params[key]

    def addParams(self, params):
        if isinstance(params, dict):
            self.addCondition(**params)
        else :
            for param in params: # On suppose ici que tous les paramètres sont correctement entrés.
                self.addCondition(**param)
            
    def addCondition(self, condtype = None, operand = None, operator = None, path = None, or_position = -1, **kwargs):
        # pas d'operator => on prend celui par défaut dans dico_alias (l'égalité) -> OK
        # pas d'operand => on teste juste l'existence de l'objet trouvé par condtype ou path -> TO DO
        if condtype is None and operand is None and operator is None and path is None:
            raise TypeError("ESSearch.addcondition() requires at least one of these parameters : condtype, operand or path.")

        if isinstance(operand, datetime.datetime) and (operand.tzinfo is None or operand.tzinfo.utcoffset(operand) is None):
            operand = operand.replace(tzinfo=datetime.timezone.utc)

        if condtype == 'datation':
            self.datation = True
            if path is None: # quand ce sont des TimeSlot (et donc par défaut), faire sur la datationBox
                path = "information.datationBox"
                if operator in {"$eq", "$in"}: #déplacer ça dans la partie qui ne concerne que MongoDB
                    pass #le changer en une combinaison de >= et <= appropriée
        elif condtype == 'location':
            if path is None: path = "information.geobox.coordinates" #seems better than information.locationBox

        elif condtype == 'property':
            if path is None: path = "information.propertyBox"
        elif condtype != None:
            if path is None: path = "data"

        if operand:
            try: operator = dico_alias[type(operand)][operator]
            except: raise ValueError('Incompatible values for operator and operand.')
        elif operator:
            raise ValueError('operand must be defined when operator is used.')

        condition = {"comp" : operator, "operand" : operand, "path" : path, "condtype" : condtype} | kwargs

        if or_position >= len(self.params):
            self.params.append([condition])
        else:
            self.params[or_position].append(condition)

    def orCondition(self, *args, **kwargs):
        """
        Adds a condition for elements in the database that we want to get but are currently not selected.
        """
        self.addCondition(or_position = len(self.params), *args, **kwargs)

    def removeCondition(self, condnum = None, or_position = None):
        """
        Removes a condition from self.params
        """
        if or_position is None:
            if condnum is None: self.params = {}
            else: self.params.pop(condnum)
        else:
            if condnum is None: self.params.pop(or_position)
            else: self.params[or_position].pop(condnum)

    def _cond(self, or_pos, operand, comp, path, inverted = False, condtype = None, formatstring = None):
        """
        Prend en entrée des paramètres et retourne un dictionnaire de la condition pour la recherche MongoDB.
        Tri par dates : (Tout) / (au moins une date) est (supérieur à) / (inférieur à) / (égal à) / (dans) [date(s) en paramètre]
        (syntaxe à vérifier) -> Dans le cas d'un intervalle, cette fonction est appelée plusieurs fois.
        -> Traiter le cas de conditions redondantes (ex <4 => <8) (actuellement, le dernier arrivé l'emporte)
        L'utilisation de OR est gérée par _fullSearchMongo.
        """
        
        try: comp = dico_alias[type(operand)][comp] #global variable
        except: raise ValueError("Comparator not allowed.")

        if comp is None : return #si on ne peut pas utiliser un comparateur, juste vérifier la présence.

#Potentiellement test pour le unwind ici si format validé

        if isinstance(operand, TimeSlot): #equals, contains, within, disjoint, intersects
            if comp in {"equals", "within"}:
                self._cond(operand[0].start, "$gte", path, False, condtype)
                self._cond(operand[-1].end, "$lte", path, False, condtype)
            elif comp in {"contains", "intersects"}:
                self._cond(operand[0].start, "$lte", path, False, condtype)
                self._cond(operand[-1].end, "$gte", path, False, condtype)
            return

        if comp in {"$geoIntersects", "$geoWithin", "$geoNear"}:
            if len(operand) == 1 or (len(operand) > 1 and not isinstance(operand[0], list)): geomtype = 'Point'
            elif len(operand) == 2: geomtype = 'LineString'
            elif len(operand) > 2:
                if len(operand) == 3:
                    operand.append(operand[-1])
                geomtype = 'Polygon'                
            cond_0 = {comp :{"$geometry": {"type" : geomtype, "coordinates" : operand}}}

        elif formatstring:
            if isinstance(operand, str):
                operand = {"$dateFromString" : {'dateString' : operand, 'format': formatstring, 'onError': 'null'}}

        elif inverted and type(operand) in {datetime.datetime, int, float}:
            if comp == "$eq"    :   cond_0 = {"$nor" : [{"$lt" : operand}, {"$gt" : operand}]}
            elif comp == "$gte" :   cond_0 = {"$not" : {"$lt"  : operand}}
            elif comp == "$gt"  :   cond_0 = {"$not" : {"$lte" : operand}}
            elif comp == "$lte" :   cond_0 = {"$not" : {"$gt"  : operand}}
            elif comp == "$lt"  :   cond_0 = {"$not" : {"$gte" : operand}}
        else:                       cond_0 = {comp : operand}

        if path not in self._match_2[or_pos]:
            self._match_2[or_pos][path] = cond_0
        else:
            self._match_2[or_pos][path] |= cond_0

    def _fullSearchMongo(self):
        
        self._request = []
        self._match_1 = {'type' : 'obs'}
        self._unwind = {}
        self._match_2 = []
        self._project = {"information" : 0}
        
        for i in range(len(self.params)):
            self._match_2.append({})
            for cond in self.params[i]:
                self._cond(or_pos = i, **cond)

        if self._match_1:
            self._request.append({"$match" : self._match_1})
        if self._unwind:
            for unwind in self._unwind:
                self._request.append({"$unwind" : "$" + unwind})
        if self._match_2:
            if len(self.params) == 1: # no $or
                self._request.append({"$match" : self._match_2[0]})
            else: # there is a $or
                self._request.append({"$match" : {"$or": self._match_2}}) #problème : self._match_2 est un dictionnaire
        if self._project:
            self._request.append({"$project" : self._project})
        return self._request

    @property
    def request(self):
        return self._fullSearchMongo()

    def execute(self, single = True):
        """
        Executes the request and returns its result.
        """
        if self.collection is None: cursor = []
        else: cursor = self.collection.aggregate(self.request)
        if not self.data: self.data = []
        if self.params == [[]]:
            result = self.data
            for item in cursor: result.append(Observation.from_obj(item))
        else:
            result = [self._filtered_observation(item) for item in self.data]            
            for item in cursor: result.append(self._filtered_observation(Observation.from_obj(item)))
        if single: return self._fusion(result)
        else: return result

    def _filtered_observation(self, obs):
        """
        Takes an Observation and returns a filtered Observation with self.params as a filter.
        """
        # self.params = [[cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]
        # dico = {'data': [['datation', [date1, date2, date3], [0,1,0,2,2,1]], ['location', [loc1, loc2, loc3], [0,1,2,0]]]}
        if len(obs) == 0: return obs
        
        if not(isinstance(obs, Observation)):
            try: Observation(obs)   #pas parfait puisque Observation.from_obj(obs) ne sera pas fait implicitement.
            except: raise TypeError("Could not convert argument to an Observation.")

        for i in range(len(self.params)):
            if self.params[i] != []:
                conds, next_relevant = self._newconds(obs, self.params[i])
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

    def _newconds(self, obs, param):
        """
        Takes parameters and returns a function which takes an item and returns a Boolean which is True iif item verifies all parameters.
        It also changes self._relevant so that it equals True when relevant criteria are applied (i.e. of the same type as the item)
        """
        # param = [cond1 AND cond 2 AND cond 3]
        new_conds = []
        relevant =  False
        for i in range(len(obs.lindex)):
            new_conds.append([])
            for cond in param:
                if ('condtype' not in cond and ('path' not in cond or ('path' in cond and cond['path'] == 'data.' + obs.lindex[i].name) ) \
                        or ('condtype' in cond and cond['condtype'] == obs.lindex[i].name)) \
                        and ('operand' not in cond or ('operand' in cond and self._compatibletypes(obs.lindex[i].cod[0], cond))):
                    new_conds[i].append(cond)
                    relevant = True
                elif 'condtype' not in cond and 'path' in cond and cond['path'][:11] == 'information' : #Les vérifications sur les path commençant par information ne se font que dans MongoDB
                    relevant = True
        return new_conds, relevant

    def _condcheck(self, item, param = None, datatype = None):
        """
        Takes an item and returns a Boolean.
        """
        # params = [cond1 AND cond 2 AND cond 3]
        if not param: return True
        boolean = True
        for cond in param:
            boolean = boolean and self._condcheck_0(item, cond, datatype)
        return boolean

    def _condcheck_0(self, item, cond = None, datatype = None):
        """
        Takes an item and returns a Boolean.
        """
        #cond = {"comp" : operator, "operand" : operand, "path" : path, "condtype" : condtype} and sometimes can contain "inverted" or "formatstring"
        if cond is None: return True
        if cond['comp'] is None and cond['operand'] is None: return True

        if cond['condtype'] == 'datation':
            if 'formatstring' in cond:
                if not isinstance(item, datetime.datetime):
                    item = datetime.datetime.strptime(item, cond['formatstring'])
                if not isinstance(cond['operand'], datetime.datetime):
                    cond['operand'] = datetime.datetime.strptime(cond['operand'], cond['formatstring'])
            elif isinstance(item, TimeSlot):
                if cond['comp'] in dico_alias[type(cond['comp'])]:
                    cond['comp'] = dico_alias[type(cond['comp'])][cond['comp']]
                    return item.link(cond['operand'])[0] == cond['comp']
                else:
                    if cond['comp'] in {"$gte", "gte", ">=", "=>"}:
                        if 'inverted' in cond and cond['inverted']: return item.bounds[0] >= cond['operand']
                        else: return item.bounds[1] >= cond['operand']
                    elif cond['comp'] in {"$gt", "gt", ">"}         :
                        if 'inverted' in cond and cond['inverted']: return item.bounds[0] > cond['operand']
                        else: return item.bounds[1] > cond['operand']
                    elif cond['comp'] in {"$lte", "lte", "<=", "=<"}:
                        if 'inverted' in cond and cond['inverted']: return item.bounds[1] <= cond['operand']
                        else: return item.bounds[0] <= cond['operand']
                    elif cond['comp'] in {"$lt", "lt", "<"}         :
                        if 'inverted' in cond and cond['inverted']: return item.bounds[1] < cond['operand']
                        else: return item.bounds[0] < cond['operand']
                    else: raise ValueError("Comparator not supported for TimeSlot.")
        elif cond['condtype'] == 'location':
            if cond['comp'] in {"$eq", "eq", "=", "==", "$equals", "equals"}            : return item.equals(cond['operand'])
            elif cond['comp'] in {"$geowithin", "geowithin", "$geoWithin", "geoWithin", "$within", "within"} : return item.within(cond['operand'])
            elif cond['comp'] in {"$disjoint", "disjoint"}                              : return item.disjoint(cond['operand'])
            elif cond['comp'] in {"$intersects", "intersects"}                          : return item.intersects(cond['operand'])
            elif cond['comp'] in {"$touches", "touches"}                                : return item.touches(cond['operand'])
            elif cond['comp'] in {"$overlaps", "overlaps"}                              : return item.overlaps(cond['operand'])
            elif cond['comp'] in {"$contains", "contains"}                              : return item.contains(cond['operand'])
            elif cond['comp'] not in {"$geonear", "geonear", "$geoNear", "geoNear"}         : return True # no equivalent for this MongoDB operator in shapely
        elif cond['condtype'] == 'property': # assuming property contains dict and the search targets one of its values
            for val in item.values():
                if self._condcheck_0(val, cond | {'condtype' : None}, datatype):
                    return True
            return False

        if cond['comp'] in {"$eq", "eq", "=", "=="}     : return item == cond['operand']
        elif cond['comp'] in {"$gte", "gte", ">=", "=>"}: return item >= cond['operand']
        elif cond['comp'] in {"$gt", "gt", ">"}         : return item >  cond['operand']
        elif cond['comp'] in {"$lte", "lte", "<=", "=<"}: return item <= cond['operand']
        elif cond['comp'] in {"$lt", "lt", "<"}         : return item <  cond['operand']
        elif cond['comp'] in {"$in", "in"}              : return item in cond['operand']
        else:
            return True
            #raise ValueError("Comparator not supported.")

    def _compatibletypes(self, item, cond):
        """
        Takes three parameters and returns True if they are compatible.
        """
        #NE FONCTIONNE PAS
        if type(item) == type(cond['operand']): return True
        elif cond['comp'] == "$in":
            if isinstance(cond['operand'], list) and len(cond['operand']) > 0:
                return self._compatibletypes(item, cond | {'operand' : cond['operand'][0], 'comp' : None})
            elif len(cond['operand']) == 0: return True
            else: return False
        elif 'formatstring' in cond:
            if isinstance(item, str):
                return type(cond['operand']) in {str, datetime.datetime, TimeSlot}
            elif isinstance(cond['operand'], str):
                return type(item) in {datetime.datetime, TimeSlot}
        elif isinstance(item, dict):
            for val in item.values():
                if self._compatibletypes(val, cond):
                    return True
            return False
        else:
            return False

    def _fusion(self, obsList): #n'a pas sa place ici, à déplacer comme constructeur d'Observation ou ailleurs
        """
        Takes a list of observations and returns one observation mixing them.
        """
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
    db = client['test_obs']
    coll = db['observation5']

    #2. Exemple de requête avec condition sur la date :
    research = ESSearch(collection=coll)
    research.addCondition('datation', datetime.datetime(2022, 1, 1, 0), ">=", inverted = True) #ACTUELLEMENT NE FONCTIONNE PAS CAR DONNÉES MAL RENTRÉES DANS LA BASE
    #research.addCondition('datation', datetime.datetime(2022, 9, 2, 3), ">=")
    #research.addCondition('location', [2.1, 45.1]) #ACTUELLEMENT NE FONCTIONNE PAS CAR DONNÉES MAL RENTRÉES DANS LA BASE
    #research.addCondition('property', 'PM1')
    print("Requête effectuée :", research.request, '\n')
    search_result = research.execute()
    if not search_result is None:
        if isinstance(search_result, cursor.Cursor):
            for el in search_result[:10]: print(el)
        else:
            print(search_result.to_obj(), '\n')
    else: print(None)

    # équivalent à :
    research = ESSearch([{"condtype" : 'datation', "operand" : datetime.datetime(2022, 9, 19, 1), 'operator' : "$gte", 'inverted' : True},
                {"condtype" : 'datation', "operand" : datetime.datetime(2022, 9, 20, 3), 'operator' : "$gte"}], collection = coll)
    print("Requête effectuée :", research.request)