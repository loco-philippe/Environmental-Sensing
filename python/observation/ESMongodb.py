from datetime import datetime
import shapely
from pymongo import MongoClient


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
            
    def addCondition(self, condtype = None, operand = None, operator = None, path = None, all = None, or_position = -1, formatstring = None):

        if condtype == 'datation':
            self.datation = True
            if path == None: path = "datation.dateTime"
        elif condtype == 'location':
            if path == None: path = "location.coordinates"


        condition = {"comp" : operator, "operand" : operand, "path" : path}
        if all != None: condition |= {"all" : all}
        if formatstring: condition |= {"formatstring" : formatstring} #paramètre actuellement sans effet. lorsque entré, s'applique d'abord aux dates de la base de donnée, et ensuite éventuellement sur la date en paramètre de la condition.

        if or_position >= len(self.params):
            self.params.append([condition])
        else:
            self.params[or_position].append(condition)

    def addDatationCondition(self, dates = None, comparator = None, all = None, path = "datation.dateTime", 
                                or_position = -1, formatstring = None, date = None, comp = None):
        """
        Adds one condition on the datation.
        Condition format : {comparator, dates} where dates is either a date or a list of dates.
        cond1 -> [cond1, cond2] -> [ [cond1, cond2], [cond1', cond2', cond3']]
        Date format must be consistent, and can use formatstring when needed.
        or_position : parameter used when Mongo request contains "$or"
        """
        
        #seules parties nécessitant vraiment le côté date sont le chemin et l'éventuelle vérification du type datetime, str et application du format.

        if dates == None:
            if date: dates = date
            else: raise ValueError("Parameter dates is missing.")
        if comparator == None:
            if comp: comparator = comp
            else: raise ValueError("Parameter comparator is missing.")

        self.addCondition('datation', dates, comparator, path, all, or_position, formatstring)


    def orCondition(self, **kwargs):
        """
        Adds a condition for elements in the database that we want to get but are currently not selected.
        """
        self.addCondition(or_position = len(self.params), **kwargs)

    def removeCondition(self, condnum = None, or_position = None):
        if or_position == None:
            if condnum == None: self.params = {}
            else: self.params.pop(condnum)
        else:
            if condnum == None: self.params.pop(or_position)
            else: self.params[or_position].pop(condnum)

    def _search(self): #EN L'ÉTAT NE FONCTIONNE QUE POUR DES AGGRÉGATIONS

        if self.datation:
            self._match_1 = {"$match" : {"datation.dateType" : "datetime"}}
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
        
        if all:
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
        self._match_1 = {}
        self._unwind = []
        self._match_2 = {}
        #self._group = {"_id" : '$_id'} # ne renvoie rien d'autre que les _id
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
        if self.collection == None:
            raise AttributeError("self.collection not defined.")
        #print("Requête exécutée : self.collection."+self.searchtype+"(", self.request, ")")
        exec('setattr(self, "cursor", self.collection.' + self.searchtype + '(self.request))')
        return self.cursor

if __name__ == "__main__":
    from dotenv import dotenv_values

    # 1. Connection à la base de donnée
    #config = dotenv_values(".env")
    #client = clientMongo(config["USER"], config["PWD"], config["SITE"])
    client = clientMongo()
    db = client['test_obs']
    coll = db['observation']

    #2. Exemple de requête avec condition sur la date :
    research = ESSearchMongo(collection=coll)
    research.addDatationCondition(datetime(2022, 9, 19, 1), ">=")
    research.addDatationCondition(datetime(2022, 9, 20, 3), ">=", all = False)
    print("Requête effectuée :", research.request)
    curseur = research.execute()
    for el in curseur: print(el)

    # équivalent à :
    research = ESSearchMongo([{"condtype" : 'datation', "operand" : datetime(2022, 9, 19, 1), 'operator' : "$gte"},
                {"condtype" : 'datation', "operand" : datetime(2022, 9, 20, 3), 'operator' : "$gte", 'all' : False}], collection = coll)
    print("Requête effectuée :", research.request)


# possibilité d'enregistrer tous les chemins lors du tour à vide. (avec coll. count() ?) + regarder les index présents dans mongoDB.
