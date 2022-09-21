# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: Philippe@loco-labs.io

The `ES.test_ilist` module contains the unit tests (class unittest) for the
`Ilist` functions.
"""
import unittest
from ilist import Ilist
from iindex import Iindex
from copy import copy
from util import util
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
il=Ilist(l)
defv = 'default value'
i1 = 'i1'
class Test_Ilist(unittest.TestCase):

    def test_creation_unique(self):
        self.assertTrue(Ilist().to_obj() == [])
        self.assertTrue(Ilist([1,2,3]).to_obj() == [1,2,3])
        self.assertTrue(Ilist(['er', 'er', 'er']).to_obj() == ['er', 'er', 'er'])
        self.assertTrue(Ilist.from_obj([1,2,3]).to_obj() == [1,2,3])
        self.assertTrue(Ilist.from_obj(['er', 'er', 'er']).to_obj() == ['er', 'er', 'er'])        
        self.assertTrue(Ilist.Iext([1,2,3]).to_obj() == [1,2,3])
        self.assertTrue(Ilist.Iext(['er', 'er', 'er']).to_obj() == ['er', 'er', 'er'])
        
    def test_creation_simple(self) :
        iidx = Ilist([['datationvalue', [10,20,30]],
                          ['locationvalue', [100,200,300], 0],
                          ['propertyvalue', [True, False]]])                 
        iidx1 = Ilist([['datationvalue', [10,20,30]],
                          ['locationvalue', [100,200,300], 0],
                          ['propertyvalue', [True, False]]], length=6)                 
        iidx2 = Ilist([['datationvalue', [10,20,30], [0,0,1,1,2,2]],
                           ['locationvalue', [100,200,300], [0,0,1,1,2,2]],
                           ['propertyvalue', [True, False], [0,1,0,1,0,1]]], length=6)
        iidx3 = Ilist([['datationvalue', [10, 10, 20, 20, 30, 30]],
                           ['locationvalue', [100, 100, 200, 200, 300, 300]],
                           ['propertyvalue', [True, False, True, False, True, False]]], length=6)   
        iidx4 = Ilist([['datationvalue', [10, 10, 20, 20, 30, 30]],
                           ['locationvalue', [100, 100, 200, 200, 300, 300]],
                           ['propertyvalue', [True, False, True, False, True, False]]])   
        self.assertTrue(len(iidx) == len(iidx1) == len(iidx3) == len(iidx2) == len(iidx4))
        self.assertTrue(iidx.lidx[2].values  == iidx3.lidx[2].values == 
                        iidx2.lidx[2].values == iidx4.lidx[2].values ==
                        iidx1.lidx[2].values)
        self.assertEqual(Ilist(Ilist([[0, 2, 0, 2, 0], [10,0,20,20,15]])), 
                         Ilist([[0, 2, 0, 2, 0], [10,0,20,20,15]]))
        il = Ilist([[{'paris': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]]], 
                   name='location', context=False) 
        self.assertEqual(il.lindex[0].codec[1].value.__class__.__name__, 'Point')
        
    def test_creation_variable(self) :
        #self.assertEqual(Ilist2(indexset=['i1', [1, 2, 3]]), Ilist2([defv, [True, True, True]], ['i1', [1, 2, 3]]))
        il = Ilist([['namvalue'     , ['a', 'b', 'c', 'd', 'e', 'f']],
                     ['datationvalue', [10,20,30]],
                     ['locationvalue', [100,200,300], 1],
                     ['propertyvalue', [True, False]]], var=0)
        il1= Ilist([['namvalue'     , ['a', 'b', 'c', 'd', 'e', 'f'], -1],
                     ['datationvalue', [10,20,30]],
                     ['locationvalue', [100,200,300], 1],
                     ['propertyvalue', [True, False]]])
        il2 =Ilist([['namvalue'     , ["a", "b", "c", "d", "e", "f"], -1], 
                     ['datationvalue', [10, 10, 20, 20, 30, 30]],
                     ['locationvalue', [100, 100, 200, 200, 300, 300]],
                     ['propertyvalue', [True, False, True, False, True, False]]])   
        self.assertTrue(il == il1 == il2)
        self.assertTrue(il == Ilist(il.lindex, var=il.lvarrow) == copy(il))  
        
    def test_creation_idic_iext(self) :
        iidx = Ilist.Idic({'datationvalue': [10, 10, 20, 20, 30, 30],
                            'locationvalue': [100, 100, 200, 200, 300, 300],
                            'propertyvalue': [True, False, True, False, True, False]})   
        iidx1 =Ilist.Iext([[10, 10, 20, 20, 30, 30], [100, 100, 200, 200, 300, 300],
                            [True, False, True, False, True, False]],
                            ['datationvalue', 'locationvalue', 'propertyvalue'])
        iidx4 = Ilist([    ['datationvalue', [10, 10, 20, 20, 30, 30]],
                            ['locationvalue', [100, 100, 200, 200, 300, 300]],
                            ['propertyvalue', [True, False, True, False, True, False]]])   
        self.assertTrue(iidx == iidx1 == iidx4)
        self.assertTrue(Ilist.Idic({}) == Ilist.Idic() == Ilist() ==
                        Ilist.Iext([]) == Ilist.Iext())
        il = Ilist.Iext([[1,2,3], [[4,5,6],0], [7,8], [[11,12,13,14,15,16], -1]])
        il1 = Ilist([[1,2,3], [[4,5,6],0], [7,8], [[11,12,13,14,15,16], -1]])
        il2 = Ilist.Idic({'i0':[1,2,3], 'i1':[[4,5,6],0], 'i2':[7,8], 'i3':[[11,12,13,14,15,16], -1]})
        self.assertTrue(il == il1 == il2)
        self.assertTrue(len(il) == len(il1) == len(il2) == 6)
        
    def test_var(self):
        il2 =Ilist([['namvalue'     , ["a", "b", "c", "d", "e", "f"], -1], 
                     ['datationvalue', [10, 10, 20, 20, 30, 30]],
                     ['locationvalue', [100, 100, 200, 200, 300, 300]],
                     ['propertyvalue', [True, False, True, False, True, False]]])
        il2.setvar(0)
        self.assertEqual(il2.lvarname, ['namvalue'])
        il2.setvar()
        self.assertEqual(il2.lvarname, [])
        il2.setvar('namvalue')
        self.assertEqual(il2.lvarname, ['namvalue'])

    def test_creation_idic_iext_variable(self) :
        iidx = Ilist.Idic({'varvalue'     : ['a', 'b', 'c', 'd', 'e', 'f'],
                            'datationvalue': [10, 10, 20, 20, 30, 30],
                            'locationvalue': [100, 100, 200, 200, 300, 300],
                            'propertyvalue': [True, False, True, False, True, False]},
                           var=0)   
        iidx1 =Ilist.Iext([['a', 'b', 'c', 'd', 'e', 'f'],
                            [10, 10, 20, 20, 30, 30], 
                            [100, 100, 200, 200, 300, 300],
                            [True, False, True, False, True, False]],
                           ['varvalue', 'datationvalue', 'locationvalue', 'propertyvalue'],
                           var=0)
        iidx2 =Ilist.Iext([[10, 10, 20, 20, 30, 30], 
                            [100, 100, 200, 200, 300, 300],
                            [True, False, True, False, True, False],
                            ['a', 'b', 'c', 'd', 'e', 'f']],
                           ['datationvalue', 'locationvalue', 'propertyvalue', 'varvalue'],
                           var=3)
        iidx4 = Ilist(    [['varvalue', ['a', 'b', 'c', 'd', 'e', 'f'], -1],
                            ['datationvalue', [10, 10, 20, 20, 30, 30]],
                            ['locationvalue', [100, 100, 200, 200, 300, 300]],
                            ['propertyvalue', [True, False, True, False, True, False]]])   
        self.assertTrue(iidx == iidx1 == iidx2 == iidx4)
        ilx = Ilist.Iext([20,['a', 'b', 'b', 'c', 'c', 'a'], [1,1,2,2,3,3] ] )
        self.assertTrue(ilx.lindex[0].values == [20, 20, 20, 20, 20, 20])
        
    def test_properties(self) :
        il=Ilist([['ext', ['er', 'rt', 'er', 'ry'], -1],[0, 2, 0, 2], 
                   [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0], 
                   ['info', 'info', 'info', 'info'],[12, 12, 15, 30]])
        #il.reindex()
        self.assertEqual( il.idxref, [0, 1, 0, 5, 4, 5])
        self.assertEqual( il.idxlen, [2, 3, 2, 2, 1, 3])
        self.assertEqual( il.dimension, 3)
        self.assertEqual( il.lencomplete, 18)
        il = Ilist([['ext', ['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 0], [30, 12, 20, 20]])
        #il.reindex()
        self.assertFalse( il.consistent)
        il = Ilist([['ext', ['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 1], [30, 12, 20, 20]])
        #il.reindex()
        self.assertTrue( il.consistent)

    def test_item(self):
        il = Ilist([['ext', ['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 1], [30, 12, 20, 20]])
        il[1] = ['rtt', 22, 1212]
        self.assertEqual( il[1], ['rtt', 22, 1212], 
                         [il.lindex[0][1], il.lindex[1][1], il.lindex[2][1]])
        del(il[1])
        self.assertEqual( len(il), 3) 
        
    def test_canonorder(self):
        il = Ilist.Iext([[0,1,2,3,4,5], 
                          ['j','j','f','f','a','a'],
                          [100,100,200,200,300,300], 
                          [True, False, True, False, True, False]], var=0)
        il.setcanonorder()
        self.assertTrue(il.iscanonorder())
        
    def test_addindex(self):
        iidx=Ilist([['a', 'b', 'c'], [1,2,2], [4,5,5]])
        idx=Iindex([6,7,8], 'i2')
        idx2=Iindex([6,7,8], 'truc')
        iidx.addindex(idx)
        iidx.addindex(idx)
        self.assertEqual(iidx.idxname, ['i0', 'i1', 'i2', 'i2(2)', 'i2(2)(2)']) 
        iidx.delindex('i2(2)')
        self.assertEqual(iidx.idxname, ['i0', 'i1', 'i2', 'i2(2)(2)']) 
        iidx.addindex(idx2)
        self.assertEqual(iidx.idxname, ['i0', 'i1', 'i2', 'i2(2)(2)', 'truc'])
        iidx.addindex(idx, merge=True)
        self.assertEqual(iidx.lindex[2].val, [4,5,5])
        iidx.addindex(idx, merge=True, update=True)
        self.assertEqual(iidx.lindex[2].val, [6,7,8])

    def test_add_update_list(self) :
        il=Ilist([[1, 2, 3]])
        il.addindex(['test', [0, 1, 1]])
        self.assertEqual(il.lidx[0].val, [0, 1, 1])
        il.updateindex([0, 2, 2], 1)
        self.assertEqual(il.lidx[0].val, [0, 2, 2])
        il= Ilist([['a', 'b', 'c'], [1, 2, 2], [4, 5, 5]])
        il.updateindex(["d", 8, 2], 1)
        il.append(["z", 1, 10])
        self.assertEqual(il.idxlen, [4, 4, 3])

    def test_add(self):
        il1 = Ilist([[['er', 'rt', 'er', 'ry', 'ab'], -1], [0, 2, 0, 2, 0], [10,0,20,20,15]])
        il2 = Ilist([[['_er', '_rt', '_er', '_ry', '_ab'], -1], [10, 12, 10, 12, 10], 
                      [110,10,120,120,115]])
        il3 = il1 + il2
        self.assertEqual(len(il3) , len(il1) + len(il2))
        self.assertEqual(il2.loc([12, 10]), il3.loc([12, 10]))
        self.assertEqual(il1.loc([0, 20]), il3.loc([0, 20]))
        il2 = Ilist([[['_er', '_rt', '_er', '_ry', '_ab'], -1], [10, 2, 10, 12, 10], 
                      [110,0,120,120,115]])
        il3 = il1 + il2
        self.assertEqual(len(il3) , len(il1) + len(il2))
        self.assertEqual(il2.loc([12, 120]), il3.loc([12, 120]))
        self.assertEqual(il1.loc([0, 20]), il3.loc([0, 20]))

    def test_swap(self):
        il = Ilist([[10,20,30],[[100,200,300], 0], [True, False]])
        il1 = copy(il)
        il.swapindex([2,0,1])
        il.swapindex([2,0,1])
        il.swapindex([2,0,1])
        self.assertEqual(il, il1)

    def test_list(self):
        il = Ilist([[1,2,3,4,5,6]])
        self.assertEqual(il[1], 2)
        il[1] = 3
        self.assertEqual(il[1], 3)
        self.assertEqual(len(il), 6)


    def test_extend(self):
        il1 = Ilist([['er', 'rt', 'er', 'ry', 'ab'], [0, 2, 0, 2, 0], [10,0,20,20,15]])
        il2 = Ilist([[['_er', '_rt', '_er', '_ry', '_ab'], -1], [10, 12, 10, 12, 10], 
                      [110,10,120,120,115]])
        il3 = il1 | il2
        self.assertEqual(il3.lenidx, il1.lenidx + il2.lenidx)
        il  = Ilist([['er', 'rt', 'er', 'ry', 'ab', 'ert']])
        ilx = Ilist([[0,0,0,1,1,1], [0,1,2,3,4,1]])
        il2 = il | ilx
        self.assertEqual(il2.lidx, ilx.lidx)
        self.assertEqual(il2.lvar, il .lvar)
        il2 = Ilist([[['_er', '_rt', '_er', '_ry', '_ab'], -1], [10, 2, 10, 12, 10], 
                      [110,0,120,120,115]])
        il2.addindex(['truc', ['un', 'deux'], [0,0,1,1,0]])
        il2.addindex(['truc2', ['un', 'de', 'un', 'de', 'un']])
        il2.reindex()
        self.assertEqual(il2.loc([12, 120, "deux", "de"]), ['_ry'])
        
    def test_append(self) :
        il=Ilist([[0, 2, 0, 2], [30, 12, 20, 15]])
        il.append([0,20], unique = True)
        self.assertEqual( len(il), 4)
        il.append([0,40])
        self.assertEqual( len(il), 5)
        self.assertEqual( il, Ilist([[0, 2, 0, 2, 0], [30, 12, 20, 15, 40]]))
        il = Ilist([[{'paris': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]]], 'location', context=False)
        il.append([[4.83, 45.76]])
        self.assertEqual( len(il), 4)
        self.assertEqual( len(il.lindex[0].codec), 3)
        

    def test_append_variable(self) :
        il=Ilist([[['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 2], [30, 12, 20, 15]])
        il.append(['truc', 0, 20], unique = True)
        self.assertEqual( len(il), 4)
        il.append(['truc', 0, 40])
        self.assertEqual( len(il), 5)
        self.assertEqual( il, Ilist([['er', 'rt', 'er', 'ry', 'truc'], 
                                      [0, 2, 0, 2, 0], [30, 12, 20, 15, 40]], var=0))


    def test_magic(self):
        iidx5 = Ilist([['datationvalue', [10, 10, 20, 20, 30, 30]],
                           ['locationvalue', [100, 100, 200, 200, 300, 300]],
                           ['propertyvalue', [True, False, True, False, True, False]]])   
        self.assertEqual(iidx5.lidx[0], Iindex.Iext([10, 10, 20, 20, 30, 30], 'datationvalue'))
        self.assertEqual(iidx5.idxname, ['datationvalue', 'locationvalue', 'propertyvalue'])
        iidx5 += iidx5
        self.assertEqual(len(iidx5), 12)
        #iidx5 |= iidx5
        #self.assertEqual(len(iidx5.lidx), 6)
        #iidx6 = Ilist() | iidx5
        #iidx7 = iidx5 | Ilist()
        #self.assertTrue(iidx6 == iidx7)
        #self.assertTrue(iidx5 == iidx6 == iidx7)

    def test_primary(self):
        ['ext', ['er', 'rt', 'er', 'ry']]
        ilm = Ilist.Iext([['math', 'english', 'software', 'physic', 'english', 'software'],
                              ['philippe', 'philippe', 'philippe', 'anne', 'anne', 'anne'],
                              [nan, nan, nan, 'gr1', 'gr1', 'gr2'],
                              ['philippe white', 'philippe white', 'philippe white',
                               'anne white', 'anne white', 'anne white']])
        self.assertEqual(ilm.primary, [0,2])
        ilm = Ilist([['ext', ['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 2], [30, 12, 12, 15],
                      [2, 0, 2, 0], [2, 2, 0, 0], ['info', 'info', 'info', 'info'],[12, 12, 15, 30]])
        self.assertEqual(ilm.primary, [0, 1, 5])        
        ilm = Ilist([['ext', ['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 2], [30, 12, 20, 30],
                      [2, 0, 2, 0], [2, 2, 0, 0], ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertEqual(ilm.primary, [0, 1, 3])        
        ilm = Ilist.Iext([[0, 2, 0, 2], [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 12, 15, 30]])
        self.assertEqual(ilm.primary, [0, 1, 5])        
        ilm = Ilist.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertEqual(ilm.primary, [0, 1, 3])
        
    def test_to_obj(self):
        ilm = Ilist.Iext([[0,     0,   2,   3,   4,   4,   6,   7,   8,   9,   9,  11,  12 ],
                              ['j', 'j', 'f', 'a', 'm', 'm', 's', 's', 's', 'n', 'd', 'd', 'd' ], 
                              ['t1','t1','t1','t2','t2','t2','t3','t3','t3','t4','t4','t4','t4'],
                              ['s11','s1','s1','s1','s1','s11','s2','s2','s2','s1','s2','s2','s2'],
                              [2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021,2021],
                              ['t1','t1','t1','t2','t2','t2','t3','t3','t3','t4','t4','t4','t4']])
        coupling = [True, False]
        keyscrd  = [True, False]
        test = list(product(coupling, keyscrd))
        for ts in test:
            #ilm.reindex()
            if coupling: ilm.coupling()
            if keyscrd:  ilm.lidx[0].tostdcodec(inplace=True)
            self.assertEqual(Ilist.from_obj(ilm.to_obj()), ilm)
            #self.assertEqual(Ilist.from_obj(ilm.to_obj()).to_obj(), ilm.to_obj())
        encoded     = [True, False]
        format      = ['json', 'cbor']
        fullcodec   = [True, False]
        defaultcodec= [False, False]
        test = list(product(encoded, format, fullcodec, defaultcodec))
        for ts in test:
            opt = {'encoded': ts[0], 'encode_format': ts[1], 'fullcodec': ts[2],
                   'defaultcodec': ts[3]}
            self.assertEqual(Ilist.from_obj(ilm.to_obj(**opt)), ilm)
            ilm.to_file('test.il', **opt)
            self.assertEqual(Ilist.from_file('test.il'), ilm)
        ilm = Ilist.Iext([[6, 7, 8, 9, 9, 11, 12],
                              ['s', 's', 's', 'n', 'd', 'd', 'd' ]])
        ilm.coupling()
        for ts in test:
            opt = {'encoded': ts[0], 'encode_format': ts[1], 'fullcodec': ts[2],
                   'defaultcodec': ts[3]}
            self.assertEqual(Ilist.from_obj(ilm.to_obj(**opt)), ilm)
        
    def test_to_obj_variable(self):
        il = Ilist.Iext([[0,1,2,3,4,5], 
                          ['j','j','f','f','a','a'],
                          [100,100,200,200,300,300], 
                          [True, False, True, False, True, False]], var=0)
        self.assertEqual(Ilist.from_obj(il.to_obj()), il)
        il.setcanonorder()
        self.assertEqual(Ilist.from_obj(il.to_obj()), il)
        self.assertEqual(Ilist.from_obj(), Ilist())
        
    def test_coupling(self):
        ilx = Ilist.Iext([['a', 'b', 'b', 'c', 'c', 'a'], 
         [20,  10,  10,  10,  10,  20], [200, 200, 300, 200, 300, 300]] )
        self.assertTrue(ilx.complete)
        ilx.coupling(derived=False)
        self.assertTrue(ilx.indexinfos()[1]['typecoupl'] == 'coupled')
        ilx.reindex()
        ilx.coupling()
        self.assertTrue(ilx.indexinfos()[1]['typecoupl'] == 'derived')
        il=Ilist([[[1,2,3,4,5,6], -1], ['a', 'b', 'b', 'c', 'c', 'a'], 
         [20,  10,  10,  10,  10,  20], [200, 200, 300, 200, 300, 300]] )
        self.assertTrue(il.complete)
        il.coupling(derived=False)
        self.assertTrue(il.indexinfos()[1]['typecoupl'] == 'coupled')
        il.reindex()
        il.coupling()
        self.assertTrue(il.indexinfos()[1]['typecoupl'] == 'derived')

    def test_duplicates(self):
        ilx = Ilist.Iext([['a', 'b', 'b', 'c', 'c', 'a'], 
                          [20,  10,  10,  10,  10,  20], [200, 200, 400, 200, 300, 300], 
                          [1,1,2,2,3,3] ] )
        ilx.coupling(derived=False, rate=0.6)
        ilx.getduplicates(['i2'], 'test')
        self.assertEqual(ilx.lindex[4].values, [False, False, True, False, False, False])
        ilx = Ilist.Iext([['a', 'b', 'b', 'c', 'c', 'a'], 
                          [20,  10,  10,  10,  10,  20], [200, 200, 200, 300, 300, 200], 
                          [1,1,1,2,3,1] ] )
        ilx.coupling(rate=0.2)
        ilx.getduplicates(resindex='test')
        self.assertEqual(ilx.lindex[4].values, [True, True, True, False, False, True])
        
    def test_name(self):
        ilm = Ilist.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        ilm.full()
        self.assertTrue(ilm.from_obj(ilm.to_obj())==ilm)
        
    def test_full(self):
        ilm = Ilist.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])
        self.assertFalse(ilm.complete)
        ilm.full()
        self.assertTrue(ilm.lidx[0].iscrossed(ilm.lidx[1])==ilm.lidx[0].iscrossed(ilm.lidx[2])
                        ==ilm.lidx[1].iscrossed(ilm.lidx[2])==True)
        self.assertTrue(ilm.complete)
        il=Ilist.Iext([['er', 'rt', 'er', 'ry'], [0, 2, 0, 2], [30, 12, 20, 30], 
                       [2, 0, 2, 0], [2, 2, 0, 0], ['info', 'info', 'info', 'info'],
                       [12, 20, 20, 12]], var=0)
        ilc=il.full()
        #ild=il.full(minind=False)
        '''ild=il.full(axes=list(range(il.lenidx)))
        self.assertEqual( len(ild), 48)
        self.assertEqual( ild.idxref,  [0, 1, 2, 3, 4, 5])
        self.assertEqual( ilc.extidx[1], [30, 12, 20, 30, 30, 12, 12, 20, 30, 12, 20, 20])
        self.assertEqual( ilc.idxcoupled, il.idxcoupled)
        self.assertTrue( ilc.idxlen == il.idxlen == ild.idxlen)
        self.assertEqual( ilc.idxref, il.idxref)
        self.assertTrue( ilc.idxunique == il.idxunique == ild.idxunique)'''


    def test_valtokey(self):
        ilm = Ilist.Iext([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], 
                              ['info', 'info', 'info', 'info'],[12, 20, 20, 12]])        
        self.assertEqual(ilm.keytoval(ilm.valtokey([2,12,0, 2, 'info', 20])), [2,12,0, 2, 'info', 20])

    def test_vlist(self) :
        il = Ilist([[1,2,3]])
        self.assertEqual(il.vlist(2, func=pow), [1, 4, 9])
        il = Ilist([['er', 'ar', 'ty']])
        self.assertEqual(il.vlist(func=len), [2, 2, 2])
        il = Ilist([[datetime(2010, 1,2), datetime(2012, 1,2)]])
        self.assertEqual(il.vlist(func=datetime.isoformat,timespec='hours', sep='-', extern=False), #!!!
                         ['2010-01-02-00', '2012-01-02-00'])
        il =Ilist([[['aer', 'e', 'h'], -1], [1,2,3], ['a', 'efg', 'h'], [0,1,0]])
        self.assertEqual(il.vlist(func=len, index=2), [1, 3, 1])
        il=Ilist([[[1,2,3,4], -1], [DatationValue(name='morning'), DatationValue(name='afternoon')],
                             [LocationValue(name='paris'), LocationValue([4.1, 42.8])]])
        self.assertEqual(il.vlist(func=ESValue.vName, extern=False, index=1), 
                         ['morning', 'morning', 'afternoon', 'afternoon'])
        self.assertEqual(il.vlist(func=ESValue.vName, extern=False, index=2, default='ici'), 
                         ['paris', 'ici', 'paris', 'ici'])

    def test_merge(self):
        il1 = Ilist.Idic({'notes'     : [10, 11, 12], 
                           'course'    : ['math', 'english', 'software']}, var=0)        
        il2 = Ilist.Idic({'notes'     : [15, 14, 11],
                           'course'    : ['physic', 'english', 'software'],
                           'group'     : ['gr1', 'gr1', 'gr2']}, var=0)
        il3 = Ilist.Idic({'$list'      : [il1, il2],
                           'name'      : ['philippe white', 'anne white'],
                           'firstname' : ['philippe', 'anne'],
                           'group'     : ['gr1', 'gr2']}, var=0)
        self.assertEqual(il3.merge(mergeidx=True, updateidx=True).loc(["anne white", "anne", "gr1", "english" ]), [14])
        self.assertEqual(il3.merge(mergeidx=True, updateidx=False).loc(["anne white", "anne", "gr2", "english" ]), [14])
        il3 = Ilist([[il1, il2]], typevalue=None)
        self.assertEqual(il3.merge(mergeidx=True, updateidx=True).loc(["english", "gr1"]), [14])


    def test_csv(self):
        il=Ilist([[['er', 'rt', 'er', 'ry'], -1], [0, 2, 0, 2], [30, 12, 20, 15]])
        il.to_csv('test.csv')
        il2 = Ilist.from_csv('test.csv', var=0)
        self.assertTrue(il == il2)
        if ES.def_clsName: 
            il.to_csv(ifunc=ESValue.vSimple)
            il.to_csv(ifunc=ESValue.json, encoded=False)
            il3 = Ilist.from_csv(var=0)
            self.assertTrue(il == il3)
        il=Ilist.Iext([['er', 'rt', 'er', 'ry', 'ab'], [0, 2, 0, 2, 0], [10,0,20,20,15], [1,2,1,2,1]], var=0)
        il.to_csv('test.csv', optcsv={'dialect':'excel', 'delimiter':';', 'quoting': csv.QUOTE_NONNUMERIC})
        il2 = Ilist.from_csv('test.csv', var=0, optcsv={'dialect':'excel', 'delimiter':';', 
                                                        'quoting': csv.QUOTE_NONNUMERIC})
        self.assertTrue(il == il2)

    def test_axes(self):
        
        il1 = Ilist.Idic({'notes'     : [10, 11, 12], 
                           'course'    : ['math', 'english', 'software']}, var=0)        
        il2 = Ilist.Idic({'notes'     : [15, 14, 11],
                           'course'    : ['physic', 'english', 'software'],
                           'group'     : ['gr1', 'gr1', 'gr2']}, var=0)
        il3 = Ilist.Idic({'list'      : [il1, il2],
                           'name'      : ['philippe white', 'anne white'],
                           'firstname' : ['philippe', 'anne']}, var=0)        
        self.assertEqual(il3.merge(mergeidx=True, updateidx=False).primary, [2, 3])
        
    def test_sort(self) :
        il=Ilist.Iext([['er', 'rt', 'er', 'ry'], [0, 2, 0, 2], [30, 12, 20, 15]], var=0)
        il.sort()
        self.assertEqual( il.lindex[0].keys,   sorted(il.lindex[0].keys))
        il.sort([2,1,0], reverse=True)
        self.assertEqual( il.lindex[2].keys,   [3, 2, 1, 0])
        il.sort([1,0,2])
        self.assertEqual( il.lindex[1].keys,   [0, 0, 1, 1])

    def test_filter(self):
        il=Ilist.Iext([['er', 'rt', 'er', 'ry'], [0, 2, 0, 2], [30, 12, 20, 15]])
        il.setfilter([True, False, True, False])
        il.applyfilter()
        self.assertEqual( il.lindex[1].val,   [0, 0])
        il=Ilist.Iext([['er', 'rt', 'er', 'ry'], [0, 2, 0, 2], [30, 12, 20, 15]])
        il.setfilter([True, False, True, False])
        il.applyfilter(reverse=True)
        self.assertEqual( il.lindex[1].val,   [2, 2])
        
        '''
        il = Ilist.Iext(f,l).setfilter([[0, 2], [12, 20, 30]], inplace=False, index=False)
        self.assertEqual( il.setidx, [[0, 2], [30, 12, 20]])
        il = Ilist.Iext(f,l).setfilter([[2], [12, 20, 30]], inplace=False, index=False)
        self.assertEqual( il.setidx, [[2], [12]])
        #ob = Observation(dict((dat3, loc3, prop2, _res(6))), idxref=[0,0,2], order=[2,0])
        ob = Observation(dict((dat3, loc3, prop2, _res(6))), idxref={'location':'datation'}, 
                         order=['property', 'datation', 'location'])
        ob.majList(ES.dat_classES, ['name1', 'autre name', 'encore autre name3'], name=True)
        self.assertEqual(ob.ilist._idxfilter('isName', 'setidx', 0, 'name[1-9]'), [0,2])
        self.assertEqual(Ilist._filter(ESValue.isName, ob.ilist.setidx[0], True, 'name[1-9]'), [0,2])
        self.assertEqual(Ilist._filter(LocationValue.link, ob.ilist.setidx[1], 'within',
                                       LocationValue([[[6,41], [6,44], [4,44], [4,41], [6,41]]])), [2])
        self.assertEqual(Ilist._filter(LocationValue.link, ob.ilist.setidx[1], 'within',
                                       LocationValue.Box((4, 41, 6, 44))), [2])
        self.assertEqual(Ilist._funclist(DatationValue({"date1": "2021-02-04T12:05:00"}), ESValue.getName), 'date1')
        self.assertTrue(Ilist._funclist(DatationValue({"date1": "2021-02-04T12:05:00"}),
                                         ESValue.equals, DatationValue("2021-02-04T12:05:00")))
        ob = Observation(dict((dat3, loc3, prop2, _res(6))), idxref={'location':'datation'}, 
                         order=['property', 'datation', 'location'])
        self.assertEqual(Ilist._filter(ESValue.getName, ob.setDatation, 'date1'), [0])        '''

    def test_to_numpy(self):
        '''à faire''' #!!!

    def test_to_xarray(self):
        ilm = Ilist.Iobj([['plants', ['fruit', 'fruit','fruit','fruit','vegetable', 'vegetable', 'vegetable', 'fruit']],
                          ['quantity', ['kg', '10 kg', 'kg', '10 kg','kg', '10 kg','kg', '10 kg']], 
                          ['product',['apple', 'apple', 'orange', 'orange', 'peppers', 'peppers', 'banana', 'banana']], 
                          ['price', [1, 10, 2, 20, 1.5, 15, 0.5, 5], -1]])
        ilm.nindex('product').coupling(ilm.nindex('plants'))
        ilx = ilm.to_xarray()
        self.assertEqual(float(ilx.sel(quantity='10 kg', product='apple').values),
                         float(ilm.loc(['fruit', '10 kg', 'apple'])[0]))
        self.assertTrue(str(ilm.loc(['fruit', '10 kg', 'banana'])[0]) in 
                        str(ilx.sel(quantity='10 kg', product='banana').values))        
        fruit = Ilist.Iobj([['product',['apple', 'apple', 'orange', 'orange', 'banana', 'banana']],
                            ['quantity', ['kg', '10 kg', 'kg', '10 kg', 'kg', '10 kg']], 
                            ['price', [1, 10, 2, 20, 0.5, 5], -1]])
        vege  = Ilist.Iobj([['product',['peppers', 'peppers']],
                            ['quantity', ['kg', '10 kg']], 
                            ['price', [1.5, 15], -1]])
        total = Ilist.Iobj([['plants', ['fruit', 'vegetable']],
                            ['price', [fruit, vege], -1]])
        ilx2=total.merge(mergeidx=True).to_xarray()
        self.assertEqual(float(ilx2.sel(quantity='10 kg', product='apple').values),
                         float(ilm.loc(['fruit', '10 kg', 'apple'])[0]))
        self.assertTrue(str(ilm.loc(['fruit', '10 kg', 'banana'])[0]) in 
                        str(ilx2.sel(quantity='10 kg', product='banana').values))  
        il = Ilist.Idic({'locatio': [0, [4.83, 45.76], [5.38, 43.3]],
                         'datatio': [[{'date1': '2021-02-04T11:05:00+00:00'},
                           '2021-07-04T10:05:00+00:00',
                           '2021-05-04T10:05:00+00:00'],
                          0],
                         'propert': [{'prp': 'PM25', 'unit': 'kg/m3'},
                          {'prp': 'PM10', 'unit': 'kg/m3'}],
                         'result': [[{'ert':0}, 1, 2, 3, 4, 5],-1]})
        ilx1 = il.to_xarray(lisfunc=[None, None, None, ESValue.to_float])
        ilx2 = il.to_xarray(lisfunc=[None, None, None, util.cast], dtype='float')
        ilx3 = il.to_xarray(numeric=True)
        self.assertTrue(list(ilx1.values[0]) == list(ilx2.values[0]) == list(ilx3.values[0]) == [1.0, 0.0])
                        
    def test_example(self):
        '''à faire''' #!!!

    def test_to_obj_file(self): #!!!
        il = Ilist([['result', [0,1,2,3,4,5], -1],
                          ['datation', [DatationValue.from_obj(dat3[1][0]), 
                                        DatationValue.from_obj(dat3[1][1]),
                                        DatationValue.from_obj(dat3[1][2])]],
                          ['location', [LocationValue.from_obj(loc3[1][0]), 
                                        LocationValue.from_obj(loc3[1][1]),
                                        LocationValue.from_obj(loc3[1][2])], 1],
                          ['property', [PropertyValue(prop2[1][0]), PropertyValue(prop2[1][1])]]])        
        encoded    = [True, False]
        format     = ['json', 'cbor']
        test = list(product(encoded, format))
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1]}
            #il2 = Ilist.from_obj(il.to_obj(**option))
            #self.assertEqual(il, il2)   #!!!

    '''for forma in ['json', 'cbor']:
        #for forma in ['json', 'cbor']:
            for encoded in [False, True]:
                for codif in [ES.codeb, {}]:
                    il2 = Ilist2.from_obj(il.to_obj(encoded=encoded, encode_format=forma, codif=codif))
                    il2.setidx[0] = DatationValue.cast(il2.setidx[0])
                    il2.setidx[1] = LocationValue.cast(il2.setidx[1])
                    il2.setidx[2] = PropertyValue.cast(il2.setidx[2])
                    #il2.extval = ReesultValue.cast(il2.extval)
                    self.assertEqual(il.to_obj(encoded=False), il2.to_obj(encoded=False))
        il3 = Ilist2.from_obj(il.to_obj(encoded=False))
        il3.setidx[0] = DatationValue.cast(il3.setidx[0])
        il3.setidx[1] = LocationValue.cast(il3.setidx[1])
        il3.setidx[2] = PropertyValue.cast(il3.setidx[2])
        #il3.extval=ReesultValue.cast(il3.extval)
        self.assertEqual(il.to_obj(encoded=False), il3.to_obj(encoded=False))
        il=Ilist2.Iext(['er', 'rt', 'er', 'ry'], [[0, 2, 0, 2], [30, 12, 20, 15]]
                      ).sort(order=[0,1], inplace=False)
        ilf = il.full(axes=[0,1]).sort(order=[0,1], inplace=False)
        self.assertEqual(il, il.from_obj(il.json()).sort(order=[0,1], inplace=False))
        self.assertEqual(ilf, il.from_obj(ilf.json()))
        for forma in ['json', 'cbor']:
            il.to_file('test.tst', encode_format=forma)
            ilf.to_file('testf.tst', encode_format=forma)
            self.assertEqual(il, il.from_file('test.tst').sort(order=[0,1], inplace=False))
            self.assertEqual(ilf, il.from_file('testf.tst'))'''

                
if __name__ == '__main__':
    unittest.main(verbosity=2)
