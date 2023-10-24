# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 15:29:48 2023

@author: phili
"""
import unittest

from itertools import product
from observation.cfield import Cfield
from observation.cdataset import Cdataset


class Test_Cfield(unittest.TestCase):

    def test_null(self):
        fnull = Cfield()
        self.assertTrue(fnull.keys == fnull.values == fnull.codec == [])
        self.assertTrue(len(fnull) == 0)
        self.assertEqual(fnull.infos, {'lencodec': 0, 'mincodec': 0,
                         'maxcodec': 0, 'typecodec': 'null', 'ratecodec': 0.0})
        self.assertEqual({'id': 'field', 'lencodec': 0, 'mincodec': 0, 'maxcodec': 0,
                          'hashf': 5740354900026072187}, fnull.analysis)

    def test_init(self):
        idx = Cfield(['er', 2, (1, 2), 2], 'test')
        self.assertTrue(Cfield(idx) == idx)
        self.assertTrue(idx.name == 'test' and 
                        idx.codec  == ['er', 2, (1, 2), 2] and 
                        idx.values == ['er', 2, (1, 2), 2] and 
                        idx.keys == [0, 1, 2, 3])
        idx = Cfield(['er', 2, (1, 2), 2], 'test', default=True)
        self.assertTrue(idx.keys == [0, 1, 2, 1] and
                        idx.values == ['er', 2, (1, 2), 2])
        idx2 = Cfield.from_ntv({'test': ['er', 2, (1, 2), 2]})
        self.assertEqual(idx, idx2)
        
    def test_ntv(self):
        idx = Cfield(codec=['er', 2, (1, 2), 2], name='test', keys=[0, 1, 2, 1])
        idx2 = Cfield.from_ntv({'test': ['er', 2, (1, 2), 2]})
        self.assertTrue(Cfield(idx) == idx)
        self.assertTrue(idx == idx2)            


    def test_analysis(self):
        idx = Cfield(['er', 2, (1, 2), 2], 'test')
        self.assertEqual(idx.analysis, {'id': 'test', 'lencodec': 4,
         'mincodec': 3, 'maxcodec': 4, 'hashf': -1379596020291439067})
        
class Test_Cdataset(unittest.TestCase):
    
    def test_null(self):
        dnull = Cdataset()
        self.assertTrue(dnull.keys == dnull.indexlen == dnull.iindex == [])
        self.assertTrue(dnull.lenindex == len(dnull) == 0) 
        self.assertEqual(dnull.analys, {'name': None, 'fields': [], 
                                          'length': 0, 'relations': {}})
        
    def test_init(self):
        dts = Cdataset([Cfield([10, 20, 30, 20], 'i0', default=True), 
                        Cfield([1, 2, 3, 4], 'i1', default=True), 
                        Cfield([1, 2, 3, 2], 'i2', default=True)])

    def test_analysis(self):
        dts = Cdataset([Cfield([10, 20, 30, 20], 'i0', default=True), 
                        Cfield([1, 2, 3, 4], 'i1', default=True), 
                        Cfield([1, 2, 3, 2], 'i2', default=True)], 'test')
        self.assertEqual(dts.analys['fields'][0], dts.lindex[0].analysis)
        self.assertEqual(dts.analys['relations'], {'i0': {'i1': 4, 'i2': 3}, 
                                                     'i1': {'i2': 4}})
                 
if __name__ == '__main__':
    unittest.main(verbosity=2)
        
