# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `observation.test_mongo` module contains the tests (class unittest) for the
`observation.essearch` methods.
The dataset used is defined in `observation.Tests.data.py` 
"""
import unittest
from datetime import datetime
from tabulate import tabulate
from pymongo import MongoClient
from pprint import pprint
from observation.essearch import ESSearch
from data import obs_mixte, obs_tests

# Requires the PyMongo package# https://api.mongodb.com/python/current
# pathClient = 'mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/test'
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

client = clientMongo()
ob_mixte = obs_mixte()
ob_tests = obs_tests()

ob_mesure = ob_tests[:30]
ob_signal = ob_tests[30:40]
ob_fixe = ob_tests[40:42]
ob_mob_1 = ob_tests[42:44]
ob_mobile = ob_tests[44:46]
ob_multi = ob_tests[46:48]
ob_dalle = ob_tests[48:50]
ob_m_dal = ob_tests[50:52]
ob_liste = [ob_mesure, ob_signal, ob_fixe, ob_mob_1, ob_mobile, ob_multi, ob_dalle, ob_m_dal]
type0 = [ob[0].param['type'] for ob in ob_liste]
name0 = [ob[0].name for ob in ob_liste]
len_ob = [len(ob) for ob in ob_liste]

class Test_jeu_data_py(unittest.TestCase):
    collec = client['test_search']['jeu_data_py']

    def test_param_name(self):
        srch = ESSearch(collection=Test_jeu_data_py.collec)
        for typ, nam, leno, lis in zip(type0, name0, len_ob, ob_liste): 
            srch.addCondition(path='param.type', operand=typ, comparator='==')
            result = srch.execute()        
            self.assertTrue(len(result) == leno and result == lis)
            srch.clearConditions()
        srch.addCondition(path='name', comparator='regex', operand='mesures')
        result = srch.execute()        
        self.assertTrue(result == ob_tests[40:52])
        srch.addCondition(path='name', comparator='regex', operand='polluant')
        result = srch.execute()        
        self.assertTrue(result == ob_tests[40:48] + ob_tests[50:52])

    def test_datation(self):
        srch = ESSearch(collection=Test_jeu_data_py.collec)
        srch.addCondition('datation', comparator='>=', operand=datetime(2022, 1, 2, 0, 0))
        srch.addCondition('datation', comparator='<=', operand=datetime(2022, 1, 4, 0, 0))
        srch.addCondition(path='name', comparator='regex', operand='mobile')
        result = srch.execute()
        # une seule observation répond aux critères (avec deux enregistrements correspondants à deux dates)
        self.assertTrue(len(result) == 2) # ok : deux resultats
        # par contre les eux résultats ne sont pas corrects
        
        print(result[0])
        '''
            name: mesures mobiles, 1 polluant - 0
            data:
                ["result", [11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9]]
    
                ["datation", ["2022-01-02T12:00:00+00:00"]]
                ["property", [{"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}]]
                ["location", [[7.19, 43.71], {"marseille": [[[5.28, 43.25], [5.48, 43.25], [5.48, 43.35], [5.28, 43.35], [5.28, 43.25]]]}, [1.44, 43.61], {"bordeaux": [[[-0.68, 44.79], [-0.48, 44.79], [-0.48, 44.89], [-0.68, 44.89], [-0.68, 44.79]]]}, [-1.55, 47.22], {"paris": [[[2.25, 48.82], [2.45, 48.82], [2.45, 48.92], [2.25, 48.92], [2.25, 48.82]]]}, [3.06, 50.63], {"strasbourg": [[[7.65, 48.54], [7.85, 48.54], [7.85, 48.64], [7.65, 48.64], [7.65, 48.54]]]}, [4.83, 45.76], {"clermont": [[[2.98, 45.73], [3.18, 45.73], [3.18, 45.83], [2.98, 45.83], [2.98, 45.73]]]}]]
                ["ville", ["nice", "marseille", "toulouse", "bordeaux", "nantes", "paris", "lille", "strasbourg", "lyon", "clermont"]]
                ["jour", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
                ["mois", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
                ["structure", ["mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile"]]
            param:
                {"date": "2022-10-20", "project": "reference", "type": "4-dim1", "context": {"version": "v0", "origin": "data.py"}}
        '''
        print(result[1])
        '''
            name: mesures mobiles, 1 polluant - 0
            data:
                ["result", [11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9]]
    
                ["datation", ["2022-01-03T12:00:00+00:00"]]
                ["property", [{"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}]]
                ["location", [[7.19, 43.71], {"marseille": [[[5.28, 43.25], [5.48, 43.25], [5.48, 43.35], [5.28, 43.35], [5.28, 43.25]]]}, [1.44, 43.61], {"bordeaux": [[[-0.68, 44.79], [-0.48, 44.79], [-0.48, 44.89], [-0.68, 44.89], [-0.68, 44.79]]]}, [-1.55, 47.22], {"paris": [[[2.25, 48.82], [2.45, 48.82], [2.45, 48.92], [2.25, 48.92], [2.25, 48.82]]]}, [3.06, 50.63], {"strasbourg": [[[7.65, 48.54], [7.85, 48.54], [7.85, 48.64], [7.65, 48.64], [7.65, 48.54]]]}, [4.83, 45.76], {"clermont": [[[2.98, 45.73], [3.18, 45.73], [3.18, 45.83], [2.98, 45.83], [2.98, 45.73]]]}]]
                ["ville", ["nice", "marseille", "toulouse", "bordeaux", "nantes", "paris", "lille", "strasbourg", "lyon", "clermont"]]
                ["jour", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
                ["mois", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
                ["structure", ["mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile"]]
            param:
                {"date": "2022-10-20", "project": "reference", "type": "4-dim1", "context": {"version": "v0", "origin": "data.py"}}
        '''
        print(ob_tests[42])
        '''
            name: mesures mobiles, 1 polluant - 0
            data:
                ["result", [11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9]]
    
                ["datation", ["2022-01-01T12:00:00+00:00", "2022-01-02T12:00:00+00:00", "2022-01-03T12:00:00+00:00", "2022-01-04T12:00:00+00:00", "2022-01-05T12:00:00+00:00", "2022-01-06T12:00:00+00:00", "2022-01-07T12:00:00+00:00", "2022-01-08T12:00:00+00:00", "2022-01-09T12:00:00+00:00", "2022-01-10T12:00:00+00:00"]]
                ["property", [{"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}, {"prp": "PM25", "unit": "kg/m3", "sampling": "instantaneous", "domain": "air", "type": "pollutant"}]]
                ["location", [[7.19, 43.71], {"marseille": [[[5.28, 43.25], [5.48, 43.25], [5.48, 43.35], [5.28, 43.35], [5.28, 43.25]]]}, [1.44, 43.61], {"bordeaux": [[[-0.68, 44.79], [-0.48, 44.79], [-0.48, 44.89], [-0.68, 44.89], [-0.68, 44.79]]]}, [-1.55, 47.22], {"paris": [[[2.25, 48.82], [2.45, 48.82], [2.45, 48.92], [2.25, 48.92], [2.25, 48.82]]]}, [3.06, 50.63], {"strasbourg": [[[7.65, 48.54], [7.85, 48.54], [7.85, 48.64], [7.65, 48.64], [7.65, 48.54]]]}, [4.83, 45.76], {"clermont": [[[2.98, 45.73], [3.18, 45.73], [3.18, 45.83], [2.98, 45.83], [2.98, 45.73]]]}]]
                ["ville", ["nice", "marseille", "toulouse", "bordeaux", "nantes", "paris", "lille", "strasbourg", "lyon", "clermont"]]
                ["jour", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
                ["mois", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
                ["structure", ["mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile", "mobile"]]
            param:
                {"date": "2022-10-20", "project": "reference", "type": "4-dim1", "context": {"version": "v0", "origin": "data.py"}}
        '''
        
if __name__ == '__main__':
    unittest.main(verbosity=2)        