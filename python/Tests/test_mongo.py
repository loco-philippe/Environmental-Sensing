# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `observation.test_mongo` module contains the tests (class unittest) for the
`observation.essearch` methods.
The dataset used is defined in `observation.Tests.data.py` 
"""
import unittest
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

class Test_essai1(unittest.TestCase):
    collec = client['test_search']['essai1']

    def test_name(self):
        srch = ESSearch(collection=Test_essai1.collec)
        srch.addcondition(path='name', operand='mesure10', comparator='==')
        result = srch.execute()        
        self.assertTrue(len(result) == 3 and result == ob_tests[0:3])


if __name__ == '__main__':
    unittest.main(verbosity=2)        