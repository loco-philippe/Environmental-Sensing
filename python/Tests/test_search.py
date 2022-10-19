import unittest
from essearch import *

def f(num=5):
    client = clientMongo()
    return client["test_obs"]['observation' + str(num)]

coll = f()

class TestSearch(unittest.TestCase):
    """
    Tries different requests
    """
    def test0(self): #ACTUELLEMENT NE FONCTIONNE PAS CAR DATETIMES MAL RENTRÉES DANS LA BASE
        research = ESSearch(collection=coll)
        research.addcondition('datation')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)

    def test0_1(self): #ACTUELLEMENT NE FONCTIONNE PAS CAR DATETIMES MAL RENTRÉES DANS LA BASE
        research = ESSearch(collection=coll)
        research.addcondition('datation')
        research.addcondition('datation', datetime.datetime(2022, 9, 1, 3))
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)
    
    # parameter inverted is to be used to select measures checking where everyting checks the conditions (and not just part of it)
    def test1(self): #ACTUELLEMENT NE FONCTIONNE PAS CAR DATETIMES MAL RENTRÉES DANS LA BASE
        research = ESSearch(collection=coll)
        research.addcondition('datation', datetime.datetime(2022, 1, 1, 0), ">=", inverted = True) #sort quand même un résultat car le inverted met un "$not"
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)

    def test2(self): #ACTUELLEMENT NE FONCTIONNE PAS CAR DATETIMES MAL RENTRÉES DANS LA BASE
        research = ESSearch(collection=coll)
        research.addcondition('datation', datetime.datetime(2022, 9, 1, 3), ">=", formatstring='default')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        print(result)
        self.assertIsNotNone(result)

    def test3(self):  #ACTUELLEMENT NE FONCTIONNE PAS CAR GÉOMÉTRIES MAL RENTRÉES DANS LA BASE
        research = ESSearch(collection=coll)
        research.addcondition('location', [2.1, 45.1])
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)

    def test4(self):
        research = ESSearch(collection=coll)
        research.addcondition('property', 'PM1')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)
    
    def test5(self):
        research = ESSearch([{"name" : 'datation', "operand" : datetime.datetime(2022, 9, 19, 1), 'comparator' : "$gte", 'inverted' : True},
                    {"name" : 'datation', "operand" : datetime.datetime(2022, 9, 20, 3), 'comparator' : "$gte"}], collection = coll)
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)

    def test6(self):
        research = ESSearch(collection=coll)
        research.addcondition('property', 'PM1')
        research.addcondition('datation', '2022-09-01T00:00:00+00:00', formatstring='default')
        research.orcondition('datation', '2022-09-02T00:00:00+00:00', formatstring='default')
        research.addcondition('property', 'PM2')
        print("Requête effectuée :", research.request, '\n')
        self.assertNotEqual(research.request, [{'$match': {'type': 'obs'}}, {'$project': {'information': 0}}])
        result = research.execute()
        #print(result)
        self.assertIsNotNone(result)

    def test6_2(self):
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