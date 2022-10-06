from datetime import datetime
from xmlrpc.client import boolean
import shapely
import pymongo
from pymongo import MongoClient
from esobservation import Observation
import pandas as pd


# ajouter des vérifications sur le format des données entrées.
# (actuellement, on peut entrer n'importe quoi sans déclencher d'erreur)

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


class ESSearchMongo:
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
                    collection = None,
                    searchtype = "aggregate",
                    **kwargs
                    ):
        self.collection = collection
        self.searchtype = searchtype # devrait être fonction des critères de recherche
        self.params = [[]]
        self.datation = False
        if parameters: self.addParams(parameters)
        if kwargs: #syntaxe à vérifier
            self.addCondition(**kwargs)


# params = [[ cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]

# -> si présence de dates, nécessité d'un $unwind. Mais également pour tous les autres array correspondant à des séries de mesures.

    def __repr__(self):
        return {"collection" : self.collection, "searchtype" : self.searchtype, "parameters" : self.params}

    def addParams(self, params):
        if isinstance(params, dict):
            self.addCondition(**params)
        else :
            for param in params: # On suppose ici que tous les paramètres sont correctement entrés.
                self.addCondition(**param)
            
    def addCondition(self, condtype = None, operand = None, operator = "$eq", path = None, all = None, or_position = -1, formatstring = None):

        if condtype == 'datation':
            self.datation = True
            if path is None: path = "data.datation"
        elif condtype == 'location':
            if path is None: path = "data.location"
        elif condtype == 'property':
            if path is None: path = "data.property"
        elif condtype != None:
            if path is None: path = "data." + condtype

        condition = {"comp" : operator, "operand" : operand, "path" : path}
        if all != None: condition |= {"all" : all}
        if formatstring: condition |= {"formatstring" : formatstring} #paramètre actuellement sans effet. Lorsque entré, s'applique d'abord aux dates de la base de donnée, et ensuite éventuellement sur la date en paramètre de la condition.

        if or_position >= len(self.params):
            self.params.append([condition])
        else:
            self.params[or_position].append(condition)

    def orCondition(self, **kwargs):
        """
        Adds a condition for elements in the database that we want to get but are currently not selected.
        """
        self.addCondition(or_position = len(self.params), **kwargs)

    def removeCondition(self, condnum = None, or_position = None):
        if or_position is None:
            if condnum is None: self.params = {}
            else: self.params.pop(condnum)
        else:
            if condnum is None: self.params.pop(or_position)
            else: self.params[or_position].pop(condnum)

    def _search(self): #EN L'ÉTAT NE FONCTIONNE QUE POUR DES AGGRÉGATIONS

        if self.datation:
            #self._match_1 = {"datation.dateType" : "datetime"}
            self._match_1 = {"$or":[{"datation.datationType":"simple"}, {"datation.datationType":"multi"}]}
            self._unwind.append("datation.dateTime")

        for param in self.params:
            for cond in param:
                self._cond(**cond)

    def _cond(self, operand, comp, path, all = True):
        """
        Prend en entrée des paramètres et retourne un dictionnaire de la condition pour la recherche MongoDB.
        Tri par dates : (Tout) / (au moins une date) est (supérieur à) / (inférieur à) / (égal à) / (dans) [date(s) en paramètre]
        (syntaxe à vérifier) -> Dans le cas d'un intervalle, cette fonction est appelée plusieurs fois.
        -> Traiter le cas de conditions redondantes (ex <4 => <8) (actuelleme,t, le dernier arrivé l'emporte)
        -> Max actuel : 4 conditions : "tout" dans un intervalle et "au moins un" dans un intervalle inclus dans celui-ci.
        L'utilisation de OR est gérée par _search.
        Format dates : array de 2^k valeurs, kcN [date1, date2, date3, date3] <-> Timeslot([[date1, date2], date3])
        """
        
        if isinstance(comp, str) and comp[0] != "$":
            if comp in {"eq", "=", "=="}        : comp = "$eq"
            elif comp in {"gte", ">=", "=>"}    : comp = "$gte"
            elif comp in {"gt", ">"}            : comp = "$gt"
            elif comp in {"lte", "<=", "=<"}    : comp = "$lte"
            elif comp in {"lt", "<"}            : comp = "$lt"
            elif comp == "in"                   : comp = "$in"
            else:
                raise ValueError("Comparators allowed are =, <, >, <=, >=, in and MongoDB equivalents.")
        
        if all and type(operand) in {datetime, int}:
            if comp == "$eq"    :   cond_0 = {"$nor" : [{"$lt" : operand}, {"$gt" : operand}]}
            elif comp == "$gte" :   cond_0 = {"$not" : {"$lt"  : operand}}
            elif comp == "$gt"  :   cond_0 = {"$not" : {"$lte" : operand}}
            elif comp == "$lte" :   cond_0 = {"$not" : {"$gt"  : operand}}
            elif comp == "$lt"  :   cond_0 = {"$not" : {"$gte" : operand}}
        else:                                 cond_0 = {comp : operand}

        if self.searchtype == "aggregate":
            if path not in self._match_2:
                self._match_2[path] = cond_0
            else:
                self._match_2[path] |= cond_0
        
        return { path : cond_0 }
    
    def _fullSearchQuery(self):
        
        self._request = {}

        self._search()


    def _fullSearchAggregation(self):
        
        self._request = []
        self._match_1 = {'type' : 'obs'}
        self._unwind = []
        self._match_2 = {}
        #self._group = {"_id" : '$_id'} # ne renvoie rien d'autre que les _id mais évite de renvoyer des doublons
        self._project = {} #{"data" : 1}
        self._sort = {}
        
        self._search()
        if self._match_1 != {}:
            self._request.append({"$match" : self._match_1})
        if self._unwind != {}:
            for unwind in self._unwind:
                self._request.append({"$unwind" : "$" + unwind})
        if self._match_2 != {}:
            self._request.append({"$match" : self._match_2})
        #if self._group != {}:
        #    self._request.append({"$group" : self._group})
        if self._project != {}:
            self._request.append({"$project" : self._project})
        if self._sort != {}:
            self._request.append({"$sort" : self._sort})
        return self._request

    def _fullSearch(self):
        if self.searchtype in {"find", "find_one"}:
            return self._fullSearchQuery()
        elif self.searchtype in {"aggregate", "update"}:
            return self._fullSearchAggregation()
        else:
            raise ValueError("This type of resarch does not exist.")

    @property
    def request(self):
        return self._fullSearch()

    def execute(self):
        """
        Executes the request and returns the cursor created by pymongo.
        """
        if self.collection is None:
            raise AttributeError("self.collection not defined.")
        #print("Requête exécutée : self.collection."+self.searchtype+"(", self.request, ")")
        exec('setattr(self, "cursor", self.collection.' + self.searchtype + '(self.request))')
        return [self._filtered(item) for item in self.cursor]

    def _filtered(self, dico):
        """
        Takes a dictionary corresponding to an Observation and returns a filtered dictionary corresponding to a filtered Observation.
        """
        # self.params = [[ cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]
        # dico = {'data': [['datation', [date1, date2, date3], [0,1,0,2,2,1]], ['location', [loc1, loc2, loc3], [0,1,2,0]]]}
        if self.params is None: return dico

        if len(dico['data']) == 0: return dico
        else:
            iindexes = [] # list of dictionnaries where key = old iindexes, value = new iindexes
            for i in range(len(dico['data'])):
                iindexes.append({})
                if not (len(dico['data'][i]) > 2 and (isinstance(dico['data'][i][2], int) or (isinstance(dico['data'][i][2], list) \
                        and len(dico['data'][i][2]) > 1 and isinstance(dico['data'][i][2][1], list)))):   # column does not depend on another column
                    if isinstance(dico['data'][i], list):
                        if len(dico['data'][i]) == 1: # condition type is not given
                            if not self._condcheck(dico['data'][i][0]):
                                dico['data'][i] = []
                                iindexes[i][0] = -1
                        elif len(dico['data'][i]) > 1: # condition type is given (with some assumptions)
                            for j in range(len(dico['data'][i][1])):
                                if not self._condcheck(dico['data'][i][1][j], dico['data'][i][0]):
                                    iindexes[i][j] = -1
                    else:
                        if not self._condcheck(dico['data'][i]):
                            dico['data'][i] = []
                            iindexes[i][0] = -1
                else: # column depends on another column (déplaçable en sous-cas de la présence de iindex)
                    if isinstance(dico['data'][i][2], int): # case 1 : [..., 0]
                        pass

                        #to do

                    elif isinstance(dico['data'][i][2], list): # case 2 : [..., [0, [0, 1, 2]]]
                        k = 0
                        for j in range(len(dico['data'][i][1])):
                            if iindexes[dico['data'][i][2][j]][j] == -1: #CONDITION NON CORRECTE : IL FAUT QUE TOUS VAILLENT -1 SIMULTANEMENT
                                iindexes[i][j] = -1
                            elif not self._condcheck(dico['data'][i][1][j], dico['data'][i][0]):
                                iindexes[i][j] = -1
                        for j in range(len(dico['data'][i][1][2][1])): # reporting remove on column derived from
                            if iindexes[i][j] == -1:
                                iindexes[dico['data'][i][2][0]][dico['data'][i][2][1][j]] = -1
        # séparation plus adaptée à l'usage des méthodes de Ilist. Partie précédente peut être considérée comme la construction du filtre.
        # potentiellement plus efficace avec Ilist.setfilter(), Ilist.applyfilter() ?
            for i in range(len(dico['data'])):
                if len(dico['data'][i]) > 1: # condition type is given (with some assumptions)
                    k = 0
                    for j in range(len(dico['data'][i][1])):
                        if j not in iindexes[i]:
                            #déplacement élément par élément et màj des iindex
                            iindexes[i][j] = k
                            dico['data'][i][1][k] = dico['data'][i][1][j]
                            k += 1
                    dico['data'][i][1] = dico['data'][i][1][:k]
                    if len(dico['data'][i]) > 2: # iindex update
        # LE CAS OU L'IINDEX EST IMPLICITE N'EST PAS GÉRÉ
                        L = []
                        if isinstance(dico['data'][i][2], list) and (len(dico['data'][i][2][1]) != 2 \
                                or isinstance(dico['data'][i][2][1], int)): # case 1 : [..., [0, 1, 2]]
                            for item in dico['data'][i][2]: #-> potentiellement incorrect dans le cas non considéré ici où le nom est manquant
                                if iindexes[item] != -1:
                                    L.append(item)
                            dico['data'][i][2] = L
                        elif isinstance(dico['data'][i][2], list) and isinstance(dico['data'][i][2][1], list): # case 2 : [..., [0, [0, 1, 2]]]
                            for item in dico['data'][i][2][1]:
                                if iindexes[item] != -1:
                                    L.append(item)
                            dico['data'][i][2][1] = L
                            
    def _condcheck(self, item, type = None):
        """
        Takes an item and returns a Boolean.
        """
        # self.params = [[ cond1 AND cond 2 AND cond 3] OR [cond4 AND cond5 AND cond6]]
        if self.params: return True
        booleans = [True] * len(self.params)
        for i in range(len(self.params)):
            for param in self.params[i]:
                booleans[i] = booleans[i] and self._condcheck_0(item, param, type)
        boolean = False
        for item in booleans:
            boolean = boolean or item
        return boolean

    def _condcheck_0(self, item, cond = None, type = None):
        """
        Takes an item and returns a Boolean.
        """
        #cond = {"comp" : operator, "operand" : operand, "path" : path} and sometimes can contain "all" and "formatstring"
        if cond is None: return True

        if type == 'datation':
            pass
        if type == 'location': # voir si ces cas peuvent être traités avec shapely
            if cond['comp'] in {"$geowithin", "geowithin", "$geoWithin", "geoWithin"}:
                pass
            if cond['comp'] in {"$geonear", "geonear", "$geoNear", "geoNear"}:
                pass

        if cond['comp'] in {"$eq", "eq", "=", "=="}     : return item == cond['operand']
        elif cond['comp'] in {"$gte", "gte", ">=", "=>"}: return item >= cond['operand']
        elif cond['comp'] in {"$gt", "gt", ">"}         : return item >  cond['operand']
        elif cond['comp'] in {"$lte", "lte", "<=", "=<"}: return item <= cond['operand']
        elif cond['comp'] in {"$lt", "lt", "<"}         : return item <  cond['operand']
        elif cond['comp'] in {"$in", "in"}              : return item in cond['operand']
        else:
            raise ValueError("Comparator not supported.")

    def __iter__(self): # suggéré par Copilot. Ne semble pas fonctionner.
        return self.execute()

    def __next__(self): # idem
        return next(self.cursor)

    def __getitem__(self, key): # idem
        return self.cursor[key]

    def __str__(self): #idem
        return str(self.request)

def cursor_to_Observation(cursor, filtre):
    """
    Takes a pymongo cursor and returns a filtered Observation object.
    """
    L = []
    for dico in cursor:
        del dico["_id"]
        obs = Observation.filtrage(obs, filtre) #éventuellement, filtrage du dictionnaire puis passage en Observation
        L.append()
    return Observation.fusion(L)

if __name__ == "__main__":
    #from dotenv import dotenv_values

    # 1. Connection à la base de donnée
    #config = dotenv_values(".env")
    #client = clientMongo(config["USER"], config["PWD"], config["SITE"])
    client = clientMongo()
    db = client['test_obs']
    coll = db['observation3']

    #2. Exemple de requête avec condition sur la date :
    research = ESSearchMongo(collection=coll)
    research.addCondition('datation', datetime(2022, 9, 19, 1), ">=", path="datation.dateTime")
    #research.addCondition('datation', datetime(2022, 9, 20, 3), ">=", all = False)
    #research.addCondition('location', [2.1, 45.1])
    print("Requête effectuée :", research.request)
    curseur = research.execute()
    for el in curseur: print(el)
    #obs = cursor_to_Observation(research.execute())
    #print(obs)
    #print(obs[1])
    #print(obs[1].to_obj())

    # équivalent à :
    research = ESSearchMongo([{"condtype" : 'datation', "operand" : datetime(2022, 9, 19, 1), 'operator' : "$gte"},
                {"condtype" : 'datation', "operand" : datetime(2022, 9, 20, 3), 'operator' : "$gte", 'all' : False}], collection = coll)
    print("Requête effectuée :", research.request)