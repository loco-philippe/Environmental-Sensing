from datetime import datetime
from pymongo import MongoClient
from ESObservation import Observation

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
    fois. Être permissif sur les manières d'entrer les paramètres pour apporter une vraie plus-value.
    __repr__ donne la liste des paramètres actuels ... ou bien une méthode dediée et __repr__ renvoie juste le nom de l'objet ?
    -> éventuellement, possibilité d'itérer sur les paramètres entrés pour les consulter un par un
    """
    def __init__(self, collection = None, searchtype = "aggregate", **kwargs):
        self.collection = collection
        self.searchtype = searchtype # peut être fonction des critères de recherche
        self.params = kwargs # params = {"dateparam" : dateparam, "locparam" : locparam, "proparam" : proparam, "nameparam" : nameparam, "extparam" : extparam}

    def __repr__(self):
        return {"collection" : self.collection, "searchtype" : self.searchtype, "parameters" : self.params}

    def _condSearchDate(self, **kwargs):
        """
        Prend en entrée des paramètres et retourne un dictionnaire de la condition pour la recherche MongoDB.
        Tri par dates : (Tout) / (au moins une date) est (supérieur à) / (inférieur à) / (égal à) / (dans) [date(s) en paramètre]
        (syntaxe à vérifier) -> Dans le cas d'un intervalle, cette fonction est appelée plusieurs fois.

        Format dates : array de 2^k valeurs, kcN [date1, date2, date3, date3] <-> Timeslot([[date1, date2], date3])
        """
        # évoluera pour accepter les formats DatationValue autres que datetime
        if not 'dateparam' in kwargs: raise ValueError("Date parameter missing.")
        if not 'comp' in kwargs: kwargs['comp'] = "$eq"
        if not 'loc' in kwargs: kwargs['loc'] = "datation.dateTime"
        if not 'all' in kwargs: kwargs['all'] = True
        
        if not kwargs['comp'] in {"$eq", "$gte", "$gt", "$lt", "$lte", "$in"}:
            if kwargs['comp'] in {"eq", "gte", "gt", "lt", "lte", "in"}:
                kwargs['comp'] = "$" + kwargs['comp']
            else:
                raise ValueError("Comparators allowed are $eq, $gte, $gt, $lt, $lte and $in.")

        valid_type = True
        if not type(kwargs['dateparam']) == datetime:
            if type(kwargs['dateparam']) == list:
                for date in kwargs['dateparam']: #voir si peut tenir en une ligne
                    if not type(date) == datetime:
                        valid_type = False
            else:
                valid_type = False
        if not valid_type:
            raise TypeError("Condition can only be on a datetime or a list of datetimes.")
        
        if kwargs['all'] and type(kwargs['dateparam']) == datetime:
### EN L'ÉTAT, RENVOIE AUSSI TOUT CE QUI NE CONTIENT PAS DE DATE AU BON FORMAT
            if kwargs['comp'] == "$eq"    :   cond_0 = {"$nor" : [{"$lt" : kwargs['dateparam']}, {"$gt" : kwargs['dateparam']}]}
            elif kwargs['comp'] == "$gte" :   cond_0 = {"$not" : {"$lt"  : kwargs['dateparam']}}
            elif kwargs['comp'] == "$gt"  :   cond_0 = {"$not" : {"$lte" : kwargs['dateparam']}}
            elif kwargs['comp'] == "$lte" :   cond_0 = {"$not" : {"$gt"  : kwargs['dateparam']}}
            elif kwargs['comp'] == "$lt"  :   cond_0 = {"$not" : {"$gte" : kwargs['dateparam']}}
        else:                       cond_0 = {kwargs['comp'] : kwargs['dateparam']}
        if self.searchtype == "aggregate": cond = {"$match" : {kwargs['loc'] : cond_0 }}
        return cond
    
    
    def _fullSearchQuery(self, **kwargs):
        
        request = {}

        if kwargs["datation"]:
            if not isinstance(kwargs["datation"], list):
                request.add(self._condSearchDate(**kwargs["datation"]))
            else:
                for cond in kwargs["datation"]:
                    request.add(self._condSearchDate(**cond))

        return request


    def _fullSearchAggregation(self, **kwargs):
        
        request = []

        if kwargs["datation"]:
            if not isinstance(kwargs["datation"], list):
                request.append(self._condSearchDate(**kwargs["datation"]))
            else:
                for cond in kwargs["datation"]:
                    request.append(self._condSearchDate(**cond))

        #print('Requête exécutée :\nself.collection.'+self.searchtype+'(', request, ')')
        #loc = {}
        #exec('curseur = collection.' + self.searchtype + '(request)\nprint(curseur)\nfor el in curseur:print(el)\nprint("truc")', {'collection':self.collection, 'request':request}, loc)
        #return loc['curseur']
        return request

    def _fullSearch(self, **kwargs):
        if self.searchtype in {"find", "find_one"}:
            return self._fullSearchQuery(**kwargs)
        elif self.searchtype in {"aggregate", "update"}:
            return self._fullSearchAggregation(**kwargs)
        else:
            raise ValueError("This type of resarch does not exist.")

    @property
    def request(self):
        if self.collection == None:
            raise AttributeError("Missing collection parameter. Set it with <ESSearchMongo object>.collection = <Collection>.")
        else:
            return self._fullSearch(**self.params)

    def execute(self):
        #NE FONCTIONNE PAS COMME DÉSIRÉ
        #print("Requête exécutée : self.collection."+self.searchtype+"(", self.request, ")")
        exec('setattr(self, "cursor", self.collection.' + self.searchtype + '(self.request))')

if __name__ == "__main__":
    from dotenv import dotenv_values

    # 1. Connection à la base de donnée
    config = dotenv_values(".env")
    client = clientMongo(config["USER"], config["PWD"], config["SITE"])
    db = client[config["DB_NAME"]]
    coll = db['observation2']

    #observation_exemple = Observation('morning', 'Paris', 'Temp', 'high') #ne fonctionne pas
    research = ESSearchMongo(collection=coll, **{'datation':{'dateparam':datetime(2022,9,19,1), 'comp':"gte"}})
    print(research.request)
    research.execute()
    curseur = research.cursor
    for el in curseur: print(el)




