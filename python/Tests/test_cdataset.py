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

    def test_analysis(self):
        idx = Cfield(['er', 2, (1, 2), 2], 'test')
        self.assertEqual(idx.analysis, {'id': 'test', 'lencodec': 4,
         'mincodec': 3, 'maxcodec': 4, 'hashf': 3646226025507127397})
        
class Test_Cdataset(unittest.TestCase):
    
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
        
