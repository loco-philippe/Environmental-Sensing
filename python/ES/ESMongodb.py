from datetime import datetime
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
                    collection = None,
                    searchtype = "aggregate",
                    datation = {},
                    location = {},
                    property = None,
                    name = None,
                    extern = None,
                    parameters = None,
                    dateType = None,
                    **kwargs
                    ):
        self.collection = collection
        self.searchtype = searchtype # peut être fonction des critères de recherche
        self.datation = datation
        if dateType:
            if 'dateType' not in datation: self.datation['dateType'] = dateType
            else: raise AttributeError("dateType already included in dateparam.")
        self._or_length_Auto()
        self.location = location
        self.property = property
        self.name = name
        self.extern = extern
        if parameters: self.addParam(parameters)
        
# params = {"dateparam" : {"dateType", [datetimes]}, "locparam" : [locparam], "proparam" : [proparam],
#           "nameparam" : [nameparam], "extparam" : [extparam]}

    def __repr__(self):
        return {"collection" : self.collection, "searchtype" : self.searchtype, "parameters" : self.parameters}

    @property
    def parameters(self):
        return {'datation' : self.datation, 'location' : self.location, 'property' : self.property,
                'name' : self.name, 'extern' : self.extern}

    def addParam(self, param):
        for paramtype in param: # On suppose ici que tous les paramètres sont correctement entrés.
            if paramtype == 'datation':
                self.addDatationCondition(param[paramtype]) #actuellement problème puisque prend un argument à la fois et un dictionnaire de paramètres n'est pas accepté en entrée
            elif paramtype == 'location':
                self.addLocationCondition(param[paramtype])
            elif paramtype == 'property':
                self.addPropertyCondition(param[paramtype])
            elif paramtype == 'name':
                self.addNameCondition(param[paramtype])
            elif paramtype == 'extern':
                self.addExternCondition(param[paramtype])
            else:
                raise ValueError("This type of parameter does not exist.")

    def addDatationCondition(self, dates = None, comparator = None, all = None, dateType = None, or_position = None, formatstring = None, date = None, comp = None):
        """
        Adds one condition on the datation.

        Condition format : {comparator, dates} where dates is either a date or a list of dates.
        cond1 -> [cond1, cond2] -> [[cond1, cond2], [cond1', cond2', cond3']]
        Date format is defined once and for all with parameter dateType, and formatstring when needed.

        or_position : parameter used when mongo request contains "$or"
        """
        if not dates:
            if date: dates = date
            else: raise ValueError("Parameter dates is missing.")
        if not comparator:
            if comp: comparator = comp
            else: raise ValueError("Parameter comparator is missing.")

        if dateType: self.datation['dateType'] = dateType

        condition = {"comp" : comparator, "date" : dates}
        if all: condition |= {"all" : all}
        if formatstring: condition |= {"formatstring" : formatstring} #paramètre actuellement sans effet

        if or_position:
            if self.datation['_or_length'] == 0:
                self.datation['_or_length'] = 1
                if 'dateparam' in self.datation: self.datation['dateparam'] = [self.datation['dateparam']]
                else: self.datation['dateparam'] = []
            if or_position > self.datation['_or_length'] - 1 or or_position == -1:
                self.datation['dateparam'].append([condition])
                self.datation['_or_length'] += 1
            else:
                self.datation['dateparam'][or_position].append(condition)
        else:
            if self.datation['_or_length'] > 0:
                self.datation['dateparam'][-1].append(condition)
            else:
                if 'dateparam' in self.datation and isinstance(self.datation['dateparam'], list):
                    self.datation['dateparam'].append(condition)
                elif 'dateparam' in self.datation and isinstance(self.datation['dateparam'], dict):
                    self.datation['dateparam'] = [self.datation['dateparam'], condition]
                else:
                    self.datation['dateparam'] = condition

    def orDatationCondition(self, dates = None, comparator = None, all = True, dateType = None, formatstring = None, date = None, comp = None):
        #possible réécriture en mettant juste **kwargs en entrée et en sortie ?
        """
        Adds a datation condition for elements in the database that we want to get but are currently not selected.
        """
        or_position = -1
        self.addDatationCondition(dates, comparator, all, dateType, or_position, formatstring, date, comp)

    def removeDatationCondition(self, datationcondnum = None, or_position = None):
        if not or_position:
            if not datationcondnum: self.datation = {}
            else: self.datation['dateparam'].pop(datationcondnum)
        else:
            if not datationcondnum: self.datation['dateparam'].pop(or_position)
            else: self.datation['dateparam'][or_position].pop(datationcondnum)


    def _dateTypeAuto(self):
        """
        Pas fait
        """
        self.datation['dateType'] = 'tests_date'
        #self.datation['dateType'] = 'datetime'

    def _or_length_Auto(self):
        """
        Automatically detects the value for self.datation['_or_length']
        """
        self.datation['_or_length'] = 0 #to do

    def _SearchDate(self): #EN L'ÉTAT NE FONCTIONNE QUE POUR DES AGGRÉGATIONS

        if 'dateType' not in self.datation:
            self._dateTypeAuto()
    
        
        if self.datation['dateType'] == 'tests_date':
            self._request.append({"$match":{"$or":[{"datation.datationType":"simple"},{"datation.datationType":"multi"}]}})
            self._request.append({"$unwind" : "$datation.dateTime"})

        if self.datation['dateType'] == "datetime":
            self._request.append({"$match" : {"datation.dateType" : "datetime"}}) #à remettre après les test et enlever ligne suivante
            self._request.append({"$unwind" : "$datation.dateTime"})

        if self.datation['_or_length'] == 0:
            self._condSearchDate(self.datation['dateparam'])
        else:
            for cond in self.datation['dateparam']:
                self._condSearchDate(cond)

    def _condSearchDate(self, params):
        """
        Prend en entrée des paramètres et retourne un dictionnaire de la condition pour la recherche MongoDB.
        Tri par dates : (Tout) / (au moins une date) est (supérieur à) / (inférieur à) / (égal à) / (dans) [date(s) en paramètre]
        (syntaxe à vérifier) -> Dans le cas d'un intervalle, cette fonction est appelée plusieurs fois.
        -> Traiter le cas de conditions redondantes (ex <4 => <8)
        -> Max actuel : 4 conditions : "tout" dans un intervalle et "au moins un" dans un intervalle inclus dans celui-ci.
        L'utilisation de OR est gérée par _SearchDate.

        Format dates : array de 2^k valeurs, kcN [date1, date2, date3, date3] <-> Timeslot([[date1, date2], date3])
        """
        # évoluera pour accepter les formats DatationValue autres que datetime

        if 'date' in params and not 'dates' in params: params['dates'] = params['date']
        if not 'dates' in params: raise ValueError("Date parameter missing.") #-> si paramètres entrés non nommés (itérable quelconque), attribuer les paramètres dans l'ordre entré
        if 'comparator' in params and not 'comp' in params: params['comp'] = params['comparator']
        if not 'comp' in params: params['comp'] = "$eq"
        if not 'loc' in params: params['loc'] = "datation.dateTime"
        if not 'all' in params: params['all'] = True
        
        if not params['comp'] in {"$eq", "$gte", "$gt", "$lte", "$lt", "$in"}:
            if params['comp'] in {"eq", "=", "=="}      : params['comp'] = "$eq"
            elif params['comp'] in {"gte", ">=", "=>"}  : params['comp'] = "$gte"
            elif params['comp'] in {"gt", ">"}          : params['comp'] = "$gt"
            elif params['comp'] in {"lte", "<=", "=<"}  : params['comp'] = "$lte"
            elif params['comp'] in {"lt", "<"}          : params['comp'] = "$lt"
            elif params['comp'] == "in"                 : params['comp'] = "$in"
            else:
                raise ValueError("Comparators allowed are =, <, >, <=, >=, in and MongoDB equivalents.")
        
        if params['all'] and type(params['dates']) == datetime:
            if params['comp'] == "$eq"    :   cond_0 = {"$nor" : [{"$lt" : params['dates']}, {"$gt" : params['dates']}]}
            elif params['comp'] == "$gte" :   cond_0 = {"$not" : {"$lt"  : params['dates']}}
            elif params['comp'] == "$gt"  :   cond_0 = {"$not" : {"$lte" : params['dates']}}
            elif params['comp'] == "$lte" :   cond_0 = {"$not" : {"$gt"  : params['dates']}}
            elif params['comp'] == "$lt"  :   cond_0 = {"$not" : {"$gte" : params['dates']}}
        else:                                 cond_0 = {params['comp'] : params['dates']}
        if self.searchtype == "aggregate": cond = {"$match" : { params['loc'] : cond_0 }}

        self._request.append(cond)
        return self._request
    
    
    def _fullSearchQuery(self):
        
        self._request = {}

        if self.datation != {}:
            self._SearchDate()


    def _fullSearchAggregation(self):
        
        self._request = []

        if self.datation != {}:
                self._SearchDate()
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
        #if self.collection == None:
        #    raise AttributeError("Missing collection parameter. Set it with <ESSearchMongo object>.collection = <Collection>.")
        #else:
        return self._fullSearch()

    def execute(self):
        """
        Executes the request and returns the cursor created by pymongo.
        """
        #print("Requête exécutée : self.collection."+self.searchtype+"(", self.request, ")")
        exec('setattr(self, "cursor", self.collection.' + self.searchtype + '(self.request))')
        return self.cursor

if __name__ == "__main__":
    from dotenv import dotenv_values

    # 1. Connection à la base de donnée
    config = dotenv_values(".env")
    client = clientMongo(config["USER"], config["PWD"], config["SITE"])
    db = client[config["DB_NAME"]]
    coll = db['observation2']

    #2. Exemple de requête avec condition sur la date :
    research = ESSearchMongo(collection = coll, datation = {'dateparam' : {"date" : datetime(2022, 9, 19, 1), 'comp' : "$gte"}})
    print("Requête effectuée :", research.request)
    curseur = research.execute()
    for el in curseur: print(el)

    # équivalent à :
    research = ESSearchMongo(collection = coll)
    research.addDatationCondition(datetime(2022, 9, 19, 1), ">=")
    print("Requête effectuée :", research.request)




