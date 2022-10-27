import unittest
from esobservation import Observation
from pymongo import MongoClient
from essearch import ESSearch, insert_many_to_mongo
import datetime
from data import ob_mesure, ob_signal, ob_fixe, ob_mob_1, ob_mobile, ob_multi, ob_dalle, ob_multi_dalle
import time
#from dotenv import dotenv_values

#config = dotenv_values(".env")
#client = clientMongo(config["USER"], config["PWD"], config["SITE"])

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

def f(num='_1'):
    client = clientMongo()
    return client["test_obs"]['observation' + str(num)]

coll = f()

#PROBLEME CONSTATE : LA SORTIE CONTIENT AUSSI DES RÉSULTATS HORS SUJET.

#VERIFIER LA RECONSTRUCTION CORRECTE POUR DIFFERENTES VALEURS DES RECORD (les exemples actuel sont trop simples à reconstruire pour savoir si ça fonctionne correctement)

class TestSearch(unittest.TestCase):
    """
    Tries different requests using MongoDB
    """
    def test4(self):
        t = time.time()
        obs1 = Observation.from_obj({'name':'test4_valid', 'data':[['property', ['PM25']]]})
        obs2 = Observation.from_obj({'name':'test4_valid_2', 'data':[['property', [{'prp': 'PM25', 'unit': 'kg/m3', 'sampling': 'instantaneous', 'domain': 'air', 'type': 'pollutant'}]]]})
        obs3 = Observation.from_obj({'name':'test4_not_valid', 'data':[['property', ['PM1']]]})
        obs4 = Observation.from_obj({'name':'test4_not_valid_2', 'data':[['datation', ['PM25']]]})
        coll.insert_one(obs1.to_obj(modecodec='dict'))
        coll.insert_one(obs2.to_obj(modecodec='dict'))
        coll.insert_one(obs3.to_obj(modecodec='dict'))
        coll.insert_one(obs4.to_obj(modecodec='dict'))
        research = ESSearch(collection=coll)
        research.addcondition('property', 'PM25')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        print(result)
        print("durée d'exécution de test4 : ", time.time() - t)
        self.assertIsNotNone(result)
        self.assertIn(obs1, result)
        self.assertIn(obs2, result)
        self.assertNotIn(obs3, result)
        self.assertNotIn(obs4, result)

    def test0(self):
        # requête longue car c'est la seule non vide -> la requête est rapide, c'est la fusion des observations qui est longue
        obs1 = Observation.from_obj({'name':'test0_valid', 'data':[['datation', [datetime.datetime(2022, 2, 1)]]]})
        obs2 = Observation.from_obj({'name':'test0_valid_2', 'data':[['datation', []]]})
        obs3 = Observation.from_obj({'name':'test0_not_valid', 'data':[['date', [datetime.datetime(2022, 2, 1)]]]})
        coll.insert_one(obs1.to_obj(modecodec='dict'))
        coll.insert_one(obs2.to_obj(modecodec='dict'))
        coll.insert_one(obs3.to_obj(modecodec='dict'))
        t = time.time()
        research = ESSearch(collection=coll)
        research.addcondition('datation')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test0 : ", time.time() - t)
        self.assertIsNotNone(result)
        self.assertIn(obs1, result)
        self.assertIn(obs2, result)
        self.assertNotIn(obs3, result)


    def test0_1(self):
        t = time.time()
        obs1 = Observation.from_obj({'name':'test1_valid', 'data':[['datation', [datetime.datetime(2022, 2, 1)]]]})
        obs2 = Observation.from_obj({'name':'test1_valid_2', 'data':[['datation', [[datetime.datetime(2022, 2, 2), datetime.datetime(2022, 2, 1)]]]]})
        obs3 = Observation.from_obj({'name':'test1_not_valid', 'data':[['datation', [datetime.datetime(2022, 2, 1, 1)]]]})
        coll.insert_one(obs1.to_obj(modecodec='dict'))
        coll.insert_one(obs2.to_obj(modecodec='dict'))
        coll.insert_one(obs3.to_obj(modecodec='dict'))
        research = ESSearch(collection=coll)
        research.addcondition('datation')
        research.addcondition('datation', datetime.datetime(2022, 2, 1))
        print("Requête effectuée :", research.request, '\n')
        for el in coll.aggregate(research.request):print(el)
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test0_1 : ", time.time() - t)
        self.assertIsNotNone(result)
        self.assertIn(obs1, result)
        self.assertIn(obs2, result)
        self.assertNotIn(obs3, result)
    
    # parameter inverted is to be used to select measures checking where everyting checks the conditions (and not just part of it)
    def test1(self):
        t = time.time()
        research = ESSearch(collection=coll)
        research.addcondition('datation', datetime.datetime(2022, 1, 1, 0), ">=", inverted = True) #sort quand même un résultat car le inverted met un "$not"
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test1 : ", time.time() - t)
        self.assertIsNotNone(result)

    def test2(self):
        t = time.time()
        research = ESSearch(collection=coll)
        research.addcondition('datation', datetime.datetime(2022, 3, 9), ">=", formatstring='default')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test2 : ", time.time() - t)
        self.assertIsNotNone(result)

    def test3(self): #ACTUELLEMENT NE FONCTIONNE PAS CAR GÉOMÉTRIES MAL RENTRÉES DANS LA BASE
        t = time.time()
        research = ESSearch(collection=coll)
        research.addcondition('location', [2.1, 45.1])
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test3 : ", time.time() - t)
        self.assertIsNotNone(result)
    
    def test5(self):
        t = time.time()
        research = ESSearch([{"name" : 'datation', "operand" : datetime.datetime(2022, 9, 19, 1), 'comparator' : "$gte", 'inverted' : True},
                    {"name" : 'datation', "operand" : datetime.datetime(2022, 9, 20, 3), 'comparator' : "$gte"}], collection = coll)
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test5 : ", time.time() - t)
        self.assertIsNotNone(result)

    def test6(self):
        t = time.time()
        research = ESSearch(collection=coll)
        research.addcondition('property', 'PM1')
        research.addcondition('datation', '2022-09-01T00:00:00+00:00', formatstring='default')
        research.orcondition('datation', '2022-09-02T00:00:00+00:00', formatstring='default')
        research.addcondition('property', 'PM2')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        print("durée d'exécution de test6 : ", time.time() - t)
        self.assertIsNotNone(result)

    def test6_2(self):
        t = time.time()
        research = ESSearch(collection=coll)
        research.addcondition('property', 'PM1')
        research.addcondition('datation', '2022-09-01T00:00:00+00:00')
        research.orcondition('datation', '2022-09-02T00:00:00+00:00')
        research.addcondition('property', 'PM2')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)
        research2 = ESSearch(collection=coll, data=result)
        result2 = research2.execute()
        #print(result2)
        print("durée d'exécution de test6_2 : ", time.time() - t)
        self.assertIsNotNone(result2)


if __name__ == '__main__':
    unittest.main()

"""
Insertion dans MongoDB :

Chaque élément de chaque colonne forme un document qui n'est lié qu'aux index de son Iindex.
-> Les numéros de colonne sont remplacés par les noms des Iindex.

OU BIEN

Changer [['datation', [datetime(2022, 9, 1, 0, 0), datetime(2022, 9, 3, 0, 0), datetime(2022, 9, 2, 0, 0)], [0, 2, 1, 1, 0, 2]]
en {'data': {'datation': [{'value': datetime(2022, 9, 1, 0, 0), 'indexes':(0, 4)}, {'value': datetime(2022, 9, 3, 0, 0), 'indexes': (2, 3)}, {'value': datetime(2022, 9, 2, 0, 0), 'indexes': (1, 5)}], 'location': [{'value': 'Bordeaux', 'indexes':(0, 1)}, {'value': 'Nantes', 'indexes': (3, 5)}, {'value': 'Paris', 'indexes': (2, 4)}]}}

cursor = coll4.aggregate([{"$unwind":"$data.datation"},{"$unwind":"$data.location"},{"$match":{'data.datation.value':{"$lte":datetime(2022,9,1)},'data.location.value': {"$in" :['Bordeaux','Nantes']}}}])
cursor = coll4.aggregate([{"$unwind":"$data.datation"},{"$unwind":"$data.location"},{"$match":{"$or":[{'data.datation.value':{"$lte":datetime(2022,9,1)}},{'data.location.value': {"$in" :['Bordeaux','Nantes']}}]}}])


"""

# validations nécessaires : fonctionnement de chaque opérateur pour chaque format -> pour les opérateurs proches, le test d'un seul suffit
# base de donnée : un élément du bon format vérifiant la requête, un élément du bon format vérifiant en partie seulement la requête et un élément du bon format ne vérifiant pas la requête.
# ainsi qu'un ensemble d'éléments dont on se fiche du format et de l'effet de la requête sur eux
# => on ne vérifie l'effet de la requête que sur les trois premiers de ces éléments. (trouvés par le nom, puis test d'égalité.)


#t1 = time.time()
# jeu de tests - performance
#liste_obs_tests = []
#for i in range(1000):
#    liste_obs_tests += [ob_mesure(res=i, jour=i, mois=1, lieu=0, prop=0)]
#    liste_obs_tests += [ob_mesure(res=10+i, jour=i, mois=1, lieu=i+1, prop=1)]
#    liste_obs_tests += [ob_mesure(res=100+i, jour=i, mois=1, lieu=i+1, prop=i)]
#for i in range(1000):
#    liste_obs_tests += [ob_signal(jour=i, mois=1, lieu=i, nuis=i, intens=i)]
#liste_obs_tests += [ob_fixe(dj=2, nh=240), ob_fixe(dj=3, nh=24)]
#liste_obs_tests += [ob_mob_1(d=0, nval=100), ob_mob_1(d=1, nval=10)]
#liste_obs_tests += [ob_mobile(d=1, nval=100), ob_mob_1(d=2, nval=10)]
#liste_obs_tests += [ob_multi(dj=3, nh=240, nloc=10), ob_multi(dj=4, nh=240, nloc=10)]
#liste_obs_tests += [ob_dalle(dj=4, nbd=100, lg=0.03), ob_dalle(dj=4, nbd=100, lg=0.05)]
#liste_obs_tests += [ob_multi_dalle(dj=5, nh=5, nbd=100, lg=0.03), 
#                    ob_multi_dalle(dj=6, nh=5, nbd=100, lg=0.04)]

#print('nb observations : ', len(liste_obs_tests))
#print('nb records : ', sum([len(obs) for obs in liste_obs_tests]))
#t2 = time.time()
#print("durée de définition : ", t2-t1)

#for i in range(len(liste_obs_tests)):
#    if not isinstance(liste_obs_tests[i], Observation): liste_obs_tests[i] = Observation.from_obj(liste_obs_tests[i])
#    liste_obs_tests[i] = liste_obs_tests[i].json(json_info=True, modecodec='dict')

#t3 = time.time()
#print("durée de conversion totale : ", t3-t2)

#coll.insert_many(liste_obs_tests)

#t4 = time.time()
#print("durée d'insertion : ", t4-t3)