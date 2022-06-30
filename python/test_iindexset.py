# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: Philippe@loco-labs.io

The `ES.test_ilist` module contains the unit tests (class unittest) for the
`Ilist` functions.
"""
import unittest
from iindexset import Iindexset
from iindex import Iindex
from copy import copy
import csv #, os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from test_observation import dat3, loc3, prop2, _res
from ESObservation import Observation
from ESValue import NamedValue, DatationValue, LocationValue, PropertyValue, ESValue #, ReesultValue
from datetime import datetime
from ESconstante import ES
from math import nan
from itertools import product

#import ..\ESValue

l = [['i1', 0, 2, 0, 2], ['i2', 30, 12, 20, 15]]
il=Iindexset(l)
defv = 'default value'
i1 = 'i1'
class Test_iindexset(unittest.TestCase):

    def test_creation(self) :
        iidx = Iindexset([[[10,20,30], 'datationvalue'],
                          [[100,200,300],['locationvalue', 0]],
                          [[True, False], 'propertyvalue']])                 
        iidx2 = Iindexset([[[10,20,30], 'datationvalue', [0,0,1,1,2,2]],
                           [[100,200,300], 'locationvalue', [0,0,1,1,2,2]],
                           [[True, False], 'propertyvalue', [0,1,0,1,0,1]]], 6)
        iidx3 = Iindexset([[[10, 10, 20, 20, 30, 30], 'datationvalue'],
                           [[100, 100, 200, 200, 300, 300], 'locationvalue'],
                           [[True, False, True, False, True, False], 'propertyvalue']], 6)   
        iidx4 = Iindexset([[[10, 10, 20, 20, 30, 30], 'datationvalue'],
                           [[100, 100, 200, 200, 300, 300], 'locationvalue'],
                           [[True, False, True, False, True, False], 'propertyvalue']])   
        self.assertTrue(iidx.leng == iidx3.leng == iidx2.leng == iidx4.leng)
        self.assertTrue(iidx.lidx[2].values  == iidx3.lidx[2].values == 
                        iidx2.lidx[2].values == iidx4.lidx[2].values)
        
    def test_magic(self):
        iidx5 = Iindexset([[[10, 10, 20, 20, 30, 30], 'datationvalue'],
                           [[100, 100, 200, 200, 300, 300], 'locationvalue'],
                           [[True, False, True, False, True, False], 'propertyvalue']])   
        self.assertEqual(iidx5[0], Iindex.Iext([10, 10, 20, 20, 30, 30], 'datationvalue'))
        self.assertEqual(iidx5.idxname, ['datationvalue', 'locationvalue', 'propertyvalue'])
        iidx5 += iidx5
        self.assertEqual(len(iidx5), 12)
        iidx5 |= iidx5
        self.assertEqual(len(iidx5.lidx), 6)

    def test_primary(self):
        ilm = Iindexset.Iext([['math', 'english', 'software', 'physic', 'english', 'software'],
                              ['philippe', 'philippe', 'philippe', 'anne', 'anne', 'anne'],
                              [nan, nan, nan, 'gr1', 'gr1', 'gr2'],
                              ['philippe white', 'philippe white', 'philippe white',
                               'anne white', 'anne white', 'anne white']])
        self.assertEqual(ilm.primary, [0,2])
        ilm = Iindexset.Iext([[0, 2, 0, 2], [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 12, 15, 30]])
        self.assertEqual(ilm.primary, [0, 1, 5])        
        ilm = Iindexset.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertEqual(ilm.primary, [0, 1, 3])
        
    def test_to_obj(self):
        ilm = Iindexset.Iext([[0,     0,   2,   3,   4,   4,   6,   7,   8,   9,   9,  11,  12 ],
                              ['j', 'j', 'f', 'a', 'm', 'm', 's', 's', 's', 'n', 'd', 'd', 'd' ], 
                              ['t1','t1','t1','t2','t2','t2','t3','t3','t3','t4','t4','t4','t4'],
                              ['s11','s1','s1','s1','s1','s11','s2','s2','s2','s1','s2','s2','s2'],
                              [2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021],
                              ['t1','t1','t1','t2','t2','t2','t3','t3','t3','t4','t4','t4','t4']])
        coupling = [True, False]
        keyscrd  = [True, False]
        test = list(product(coupling, keyscrd))
        for ts in test:
            ilm.reindex()
            if coupling: ilm.coupling()
            if keyscrd:  ilm[0].tostdcodec(inplace=True)
            self.assertEqual(Iindexset.from_obj(ilm.to_obj()).to_obj(), ilm.to_obj())
        encoded     = [True, False]
        format      = ['json', 'cbor']
        fullcodec   = [True, False]
        defaultcodec= [False, False]
        fast        = [True, False]
        test = list(product(encoded, format, fullcodec, defaultcodec, fast))
        for ts in test:
            opt = {'encoded': ts[0], 'encode_format': ts[1], 'fullcodec': ts[2],
                   'defaultcodec': ts[3], 'fast': ts[4]}
            self.assertEqual(Iindexset.from_obj(ilm.to_obj(**opt)).to_obj(**opt),
                             ilm.to_obj(**opt))
        ilm = Iindexset.Iext([[6, 7, 8, 9, 9, 11, 12],
                              ['s', 's', 's', 'n', 'd', 'd', 'd' ]])
        ilm.coupling()
        for ts in test:
            opt = {'encoded': ts[0], 'encode_format': ts[1], 'fullcodec': ts[2],
                   'defaultcodec': ts[3], 'fast': ts[4]}
            self.assertEqual(Iindexset.from_obj(ilm.to_obj(**opt)).to_obj(**opt),
                             ilm.to_obj(**opt))
        

    def test_full(self):
        ilm = Iindexset.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertFalse(ilm.complete)
        ilm.full()
        self.assertTrue(ilm.lidx[0].iscrossed(ilm.lidx[1])==ilm.lidx[0].iscrossed(ilm.lidx[3])
                        ==ilm.lidx[1].iscrossed(ilm.lidx[3])==True)
        self.assertTrue(ilm.complete)
        
    '''def test_creation(self) :
        iidx = Iindexset([['datationvalue', 10,20,30],
                          [{'locationvalue':0}, 100,200,300],
                          ['propertyvalue', True, False]])                 
        iidx2 = Iindexset([['datationvalue',10,20,30, 0,0,1,1,2,2],
                           ['locationvalue',100,200,300, 0,0,1,1,2,2],
                           ['propertyvalue',True, False, 0,1,0,1,0,1]], 6)
        iidx3 = Iindexset([['datationvalue',10, 10, 20, 20, 30, 30],
                           ['locationvalue',100, 100, 200, 200, 300, 300],
                           ['propertyvalue',True, False, True, False, True, False]], 6)   
        iidx4 = Iindexset([['datationvalue',10, 10, 20, 20, 30, 30],
                           ['locationvalue',100, 100, 200, 200, 300, 300],
                           ['propertyvalue',True, False, True, False, True, False]])   
        self.assertTrue(iidx.leng == iidx3.leng == iidx2.leng == iidx4.leng)
        self.assertTrue(iidx.lidx[2].values  == iidx3.lidx[2].values == 
                        iidx2.lidx[2].values == iidx4.lidx[2].values)

    def test_magic(self):
        iidx5 = Iindexset([['datationvalue',10, 10, 20, 20, 30, 30],
                           ['locationvalue',100, 100, 200, 200, 300, 300],
                           ['propertyvalue',True, False, True, False, True, False]])   
        self.assertEqual(iidx5[0], Iindex.Iext([10, 10, 20, 20, 30, 30], 'datationvalue'))
        self.assertEqual(iidx5.idxname, ['datationvalue', 'locationvalue', 'propertyvalue'])
        iidx5 += iidx5
        self.assertEqual(len(iidx5), 12)
        iidx5 |= iidx5
        self.assertEqual(len(iidx5.lidx), 6)
        
    def test_primary(self):
        ilm = Iindexset.Iext([['math', 'english', 'software', 'physic', 'english', 'software'],
                              ['philippe', 'philippe', 'philippe', 'anne', 'anne', 'anne'],
                              [nan, nan, nan, 'gr1', 'gr1', 'gr2'],
                              ['philippe white', 'philippe white', 'philippe white',
                               'anne white', 'anne white', 'anne white']])
        self.assertEqual(ilm.primary, [0,2])
        ilm = Iindexset.Iext([[0, 2, 0, 2], [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 12, 15, 30]])
        self.assertEqual(ilm.primary, [0, 1, 5])        
        ilm = Iindexset.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertEqual(ilm.primary, [0, 1, 3])

    def test_to_obj(self):
        ilm = Iindexset.Iext([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                              ['j', 'j', 'f', 'a', 'm', 'm', 's', 's', 's', 'n', 'd', 'd', 'd' ], 
                              ['t1','t1','t1','t2','t2','t2','t3','t3','t3','t4','t4','t4','t4'],
                              ['s1','s1','s1','s1','s1','s1','s2','s2','s2','s2','s2','s2','s2'],
                              [2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021]])
        encoded     = [True, False]
        format      = ['json', 'cbor']
        fullcodec   = [True, False]
        test = list(product(encoded, format, fullcodec))
        for ts in test:
            opt = {'encoded': ts[0], 'encode_format': ts[1], 'fullcodec': ts[2]}
            self.assertEqual(Iindexset.from_extobj(ilm.to_extobj(**opt)).to_extobj(**opt),
                             ilm.to_extobj(**opt))

    def test_full(self):
        ilm = Iindexset.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertFalse(ilm.complete)
        ilm.full()
        self.assertTrue(ilm.lidx[0].iscrossed(ilm.lidx[1])==ilm.lidx[0].iscrossed(ilm.lidx[3])
                        ==ilm.lidx[1].iscrossed(ilm.lidx[3])==True)
        self.assertTrue(ilm.complete)'''
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
