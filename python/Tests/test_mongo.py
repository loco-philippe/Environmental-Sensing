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
        self.assertTrue(len(result) == 2)
        result[0].swapindex(ob_tests[42].lname)
        self.assertTrue(ob_tests[42].loc(result[0][0], row=True) == [1])
        result[1].swapindex(ob_tests[42].lname)
        self.assertTrue(ob_tests[42].loc(result[1][0], row=True) == [2])
        result[0].add(result[1], name=True)
        self.assertTrue(result[0].idxlen == [2, 1, 2, 2, 2, 2, 1, 1])

        
if __name__ == '__main__':
    unittest.main(verbosity=2)        