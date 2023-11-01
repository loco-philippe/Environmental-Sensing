# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 15:29:48 2023

@author: phili
"""
import unittest

from itertools import product
from observation.cfield import Cfield
from observation.cdataset import Cdataset
from observation.util import util

class Test_Cfield(unittest.TestCase):

    def test_null(self):
        fnull = Cfield()
        self.assertTrue(fnull.keys == fnull.values == fnull.codec == [])
        self.assertTrue(len(fnull) == 0)
        self.assertEqual(fnull.infos, {'lencodec': 0, 'mincodec': 0,
                         'maxcodec': 0, 'typecodec': 'null', 'ratecodec': 0.0})
        self.assertEqual({'id': 'field', 'lencodec': 0, 'mincodec': 0, 'maxcodec': 0,
                          'hashf': hash(fnull)}, fnull.to_analysis)

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
        self.assertEqual(idx.to_analysis, {'id': 'test', 'lencodec': 4,
         'mincodec': 3, 'maxcodec': 4, 'hashf': hash(idx)})
        
class Test_Cdataset(unittest.TestCase):
    
    def test_null(self):
        dnull = Cdataset()
        self.assertTrue(dnull.keys == dnull.indexlen == dnull.iindex == [])
        self.assertTrue(dnull.lenindex == len(dnull) == 0) 
        self.assertEqual(dnull.to_analysis(), {'name': None, 'fields': [], 
                                          'length': 0, 'relations': {}})
        
    def test_init(self):
        dts = Cdataset([Cfield([10, 20, 30, 20], 'i0', default=True), 
                        Cfield([1, 2, 3, 4], 'i1', default=True), 
                        Cfield([1, 2, 3, 2], 'i2', default=True)])
        dts2 = Cdataset.from_ntv({'i0': [10, 20, 30, 20], 
                        'i1': [1, 2, 3, 4],
                        'i2': [1, 2, 3, 2]})        
        self.assertEqual(dts, dts2)
        self.assertTrue(Cdataset(dts) == dts)

    def test_analys(self):
        dts = Cdataset([Cfield([10, 20, 30, 20], 'i0', default=True), 
                        Cfield([1, 2, 3, 4], 'i1', default=True), 
                        Cfield([1, 2, 3, 2], 'i2', default=True)], 'test')
        self.assertEqual(dts.to_analysis()['fields'][0], dts.lindex[0].to_analysis)
        self.assertEqual(dts.to_analysis()['relations'], {'i0': {'i1': 4, 'i2': 3}, 
                                                     'i1': {'i2': 4}})

    def test_distrib(self):
        self.assertTrue(util.dist([1,0,1,0,1,0,1,0], [1,1,0,0,1,1,0,0], True)[1])
        self.assertTrue(util.dist([1,0,1,0,1,0,1,0], [1,1,1,0,0,0,0,1], True)[1])
        self.assertFalse(util.dist([0,0,0,0,1,1,1,1], [1,1,1,0,0,0,0,1], True)[1])                 
        dts = Cdataset.from_ntv({'i0': [1,0,1,0,1,0,1,0], 
                                'i1': [1,1,0,0,1,1,0,0],
                                'i2':[1,1,1,0,0,0,0,1],
                                'i3':[1,1,1,1,0,0,0,0]})
        self.assertTrue(dts.to_analysis(True)['relations']['i1']['i3'][1])
        self.assertFalse(dts.to_analysis(True)['relations']['i2']['i3'][1])

    def test_analysis(self):
        ilm = Cdataset.from_ntv([['math', 'english', 'software', 'math', 'english', 'software'],
                          ['philippe', 'philippe', 'philippe', 'anne', 'anne', 'anne'],
                          [None, None, None, 'gr1', 'gr1', 'gr2'],
                          ['philippe white', 'philippe white', 'philippe white',
                           'anne white', 'anne white', 'anne white']])
        self.assertTrue(ilm.partitions[0] == ilm._analysis.partitions('index')[0] == [0, 1])
        self.assertTrue(ilm.dimension == ilm._analysis.dimension == 2)
        
    def test_checkrelation(self):
        ilm = Cdataset.from_ntv({'month':   ['jan', 'feb', 'apr', 'jan', 'sep', 'dec', 'apr', 'may', 'jan'],
                                 'quarter': ['q1',  'q1',  'q2',  'q1',  'q3',  'q4',  'q2',  'q2',  'q1']})      
        self.assertEqual(ilm._analysis.get_relation('month', 'quarter').distomin, 0)
        ilm[2] = ['apr', 'q1']
        self.assertEqual(ilm._analysis.get_relation('month', 'quarter').distomin, 1)
        self.assertEqual(ilm.nindex('month').coupling(ilm.nindex('quarter')), (2,6))
        field = { "name": "quarter",  "relationship" : { "parent" : "month", "link" : "derived" }}
        self.assertEqual(ilm.check_relationship(field), (2,6))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
        
