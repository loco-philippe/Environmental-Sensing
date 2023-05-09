# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: Philippe@loco-labs.io

The `observation.test_ilist` module contains the unit tests (class unittest) for the
`Ilist` functions.
"""
import unittest
from copy import copy
#from util import util
import csv  # , os
from datetime import datetime
from math import nan
from itertools import product
import json
from observation import DatationValue, LocationValue, \
    PropertyValue, ESValue, Ilist, Iindex, ES, util
from test_obs import dat3, loc3, prop2
from json_ntv import Ntv, NtvList

#l = [['i1', 0, 2, 0, 2], ['i2', 30, 12, 20, 15]]
#il = Ilist.obj(l)
defv = 'default value'
i1 = 'i1'


class Test_Ilist(unittest.TestCase):

    def test_creation_unique(self):
        self.assertEqual(Ilist().to_ntv(), Ntv.obj({}))
        self.assertEqual(Ilist.ntv([1, 2, 3]).to_ntv(), Ntv.obj([1,2,3]))
        self.assertEqual(Ilist.ntv([[1, 2, 3]]).to_ntv(), Ntv.obj([[1, 2, 3]]))
        self.assertEqual(Ilist.ntv(['er', 'er', 'er']).to_ntv(),  Ntv.obj(['er', 'er', 'er']))

    def test_creation_simple(self):
        iidx  = Ilist.ntv({'datationvalue': [[10, 20, 30], [2]],
                           'locationvalue': [[100, 200, 300], 0],
                           'propertyvalue': [[True, False], [1]] })
        iidx2 = Ilist.ntv({'datationvalue': [[10, 20, 30], [0, 0, 1, 1, 2, 2]],
                           'locationvalue': [[100, 200, 300], [0, 0, 1, 1, 2, 2]],
                           'propertyvalue': [[True, False], [0, 1, 0, 1, 0, 1]]})
        iidx4 = Ilist.ntv({'datationvalue': [10, 10, 20, 20, 30, 30],
                           'locationvalue': [100, 100, 200, 200, 300, 300],
                           'propertyvalue': [True, False, True, False, True, False]})
        self.assertTrue(len(iidx) == len(iidx2) == len(iidx4))
        self.assertTrue(iidx.lindex[2].values ==
                        iidx2.lindex[2].values == iidx4.lindex[2].values)
        self.assertEqual(Ilist(Ilist.ntv([[0, 2, 0, 2, 0], [10, 0, 20, 20, 15]])),
                         Ilist.ntv([[0, 2, 0, 2, 0], [10, 0, 20, 20, 15]]))
        il = Ilist([Iindex([{'paris:point': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]],
                   name='location')])
        self.assertEqual(il.lindex[0].values[0].type_str, 'point')
        self.assertEqual(il.lindex[0].values[1].type_str, 'json')

    def test_creation_variable(self):
        #self.assertEqual(Ilist2(indexset=['i1', [1, 2, 3]]), Ilist2([defv, [True, True, True]], ['i1', [1, 2, 3]]))
        '''il = Ilist([['namvalue', ['a', 'b', 'c', 'd', 'e', 'f']],
                    ['datationvalue', [10, 20, 30]],
                    ['locationvalue', [100, 200, 300], 1],
                    ['propertyvalue', [True, False]]], var=0)'''
        il1 = Ilist.ntv({'namvalue': ['a', 'b', 'c', 'd', 'e', 'f'],
                         'datationvalue': [[10, 20, 30], [2]],
                         'locationvalue': [[100, 200, 300], 1],
                         'propertyvalue': [[True, False], [1]]})
        il2 = Ilist.ext([["a", "b", "c", "d", "e", "f"],
                         [10, 10, 20, 20, 30, 30],
                         [100, 100, 200, 200, 300, 300],
                         [True, False, True, False, True, False]],
                        ['namvalue', 'datationvalue', 'locationvalue', 'propertyvalue'])
        self.assertTrue(il1 == il2)
        self.assertTrue(il1 == Ilist(il1.lindex) == copy(il1))

    def test_creation_mode(self):
        il1 = Ilist.ntv([{'ext': [['er', 'rt', 'er', 'ry'], -1]}, [0, 2, 0, 2],
                         [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 12, 15, 30]])
        il2 = Ilist.ntv([{'ext': [['er', 'rt', 'ry'], [0, 1, 0, 2]]},
                         [[0, 2], [0, 1, 0, 1]], [[30, 12, 15], [0, 1, 1, 2]],
                         [[2, 0], 1], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 12, 15, 30]])
        il3 = Ilist.ntv([{'ext': [['er', 'rt', 'ry'], [0, 1, 0, 2]]},
                         [[0, 2], [0, 1, 0, 1]],
                         [[30, 12, 15], [0, 1, 1, 2]],
                         [[2, 0], [0, 1, 0, 1]],
                         [[2, 0], [0, 0, 1, 1]],
                         [['info'], [0, 0, 0, 0]],
                         [[12, 15, 30], [0, 0, 1, 2]]])
        self.assertTrue(il1 == il2 == il3)

    def test_creation_dic_ext(self):
        iidx = Ilist.ntv({'datationvalue': [10, 10, 20, 20, 30, 30],
                          'locationvalue': [100, 100, 200, 200, 300, 300],
                          'propertyvalue': [True, False, True, False, True, False]})
        iidx1 = Ilist.ext([[10, 10, 20, 20, 30, 30], [100, 100, 200, 200, 300, 300],
                           [True, False, True, False, True, False]],
                          ['datationvalue', 'locationvalue', 'propertyvalue'])

        self.assertEqual(iidx, iidx1)
        self.assertTrue(Ilist.ntv({}) == Ilist.ntv([]) == Ilist() ==
                        Ilist.ext([]) == Ilist.ext())
        try:
            il1 = Ilist.ext([[1, 2, 3], [[4, 5, 6], 0], [7, 8],
                             [11, 12, 13, 14, 15, 16]])
            res1 = True
        except:
            res1 = False
        try:
            il2 = Ilist.ntv([[[1, 2, 3],[2]] , [[4, 5, 6], 0], [[7, 8], [1]],
                             [11, 12, 13, 14, 15, 16]])
            res2 = True
        except:
            res2 = False
        try:
            il3 = Ilist.ntv({'i0': [1, 2, 3], 'i1': [[4, 5, 6], 0], 'i2': [
                7, 8], 'i3': [11, 12, 13, 14, 15, 16]})
            res3 = True
        except:
            res3 = False
        self.assertTrue(not res1 and res2 and not res3 and len(il2) == 6)

    """def test_var(self):
        il2 = Ilist.obj([['namvalue', ["a", "b", "c", "d", "e", "f"], -1],
                    ['datationvalue', [10, 10, 20, 20, 30, 30]],
                    ['locationvalue', [100, 100, 200, 200, 300, 300]],
                    ['propertyvalue', [True, False, True, False, True, False]]])
        il2.setvar(0)
        self.assertEqual(il2.lvarname, ['namvalue'])
        il2.setvar()
        self.assertEqual(il2.lvarname, [])
        il2.setvar('namvalue')
        self.assertEqual(il2.lvarname, ['namvalue'])"""

    def test_creation_dic_ext_variable(self):
        iidx = Ilist.ntv({'varvalue': ['a', 'b', 'c', 'd', 'e', 'f'],
                          'datationvalue': [10, 10, 20, 20, 30, 30],
                          'locationvalue': [100, 100, 200, 200, 300, 300],
                          'propertyvalue': [True, False, True, False, True, False]})
        iidx1 = Ilist.ext([['a', 'b', 'c', 'd', 'e', 'f'],
                           [10, 10, 20, 20, 30, 30],
                           [100, 100, 200, 200, 300, 300],
                           [True, False, True, False, True, False]],
                          ['varvalue', 'datationvalue',
                           'locationvalue', 'propertyvalue'])
        iidx2 = Ilist.ext([[10, 10, 20, 20, 30, 30],
                           [100, 100, 200, 200, 300, 300],
                           [True, False, True, False, True, False],
                           ['a', 'b', 'c', 'd', 'e', 'f']],
                          ['datationvalue', 'locationvalue',
                           'propertyvalue', 'varvalue'])
        self.assertTrue(iidx == iidx1 == iidx2)
        try:
            ilx = Ilist.ext(
                [20, ['a', 'b', 'b', 'c', 'c', 'a'], [1, 1, 2, 2, 3, 3]])
            res = True
        except:
            res = False
        self.assertFalse(res)

    def test_properties(self):
        il = Ilist.ntv([{'ext': ['er', 'rt', 'er', 'ry']}, [0, 2, 0, 2],
                        [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0],
                        ['info', 'info', 'info', 'info'], [12, 12, 15, 30]])
        self.assertEqual(il.indexlen, [3, 2, 3, 2, 2, 1, 3])
        self.assertEqual(il.dimension, 2)
        self.assertEqual(il.lencomplete, 4)
        il = Ilist.obj([[0, 2, 0, 0], [30, 12, 20, 20]])
        self.assertFalse(il.consistent)
        il = Ilist.obj([['ext', ['er', 'rt', 'er', 'ry']],
                        [0, 2, 0, 1], [30, 12, 20, 20]])
        self.assertTrue(il.consistent)

    def test_item(self):
        il = Ilist.ntv([{'ext': ['er', 'rt', 'er', 'ry']},
                        [0, 2, 0, 1], [30, 12, 20, 20]])
        il[1] = ['rtt', 22, 1212]
        self.assertEqual(il[1], NtvList(['rtt', 22, 1212]).val,
                         [il.lindex[0][1], il.lindex[1][1], il.lindex[2][1]])
        del(il[1])
        self.assertEqual(len(il), 3)

    def test_canonorder(self):
        il = Ilist.ext([[0, 1, 2, 3, 4, 5],
                        ['j', 'j', 'f', 'f', 'a', 'a'],
                        [100, 100, 200, 200, 300, 300],
                        [True, False, True, False, True, False]])
        il.setcanonorder()
        self.assertTrue(il.iscanonorder())

    def test_addindex(self):
        iidx = Ilist.ntv([['a', 'b', 'c'], [1, 2, 2], [4, 5, 5]])
        idx = Iindex.ext([6, 7, 8], 'i2')
        idx2 = Iindex.ext([6, 7, 8], 'truc')
        iidx.addindex(idx)
        iidx.addindex(idx)
        self.assertEqual(iidx.idxname, ['i0', 'i1', 'i2', 'i2(2)', 'i2(2)(2)'])
        iidx.delindex('i2(2)')
        self.assertEqual(iidx.idxname, ['i0', 'i1', 'i2', 'i2(2)(2)'])
        iidx.addindex(idx2)
        self.assertEqual(iidx.idxname, ['i0', 'i1', 'i2', 'i2(2)(2)', 'truc'])
        iidx.addindex(idx, merge=True)
        self.assertEqual(iidx.lindex[2].val, [4, 5, 5])
        iidx.addindex(idx, merge=True, update=True)
        self.assertEqual(iidx.lindex[2].val, [6, 7, 8])

    def test_add_update_list(self):
        il = Ilist.ntv([[1, 2, 3]])
        il.addindex({'test': [0, 1, 1]})
        self.assertEqual(il.lidx[1].val, [0, 1, 1])
        il.updateindex([0, 2, 2], 1)
        self.assertEqual(il.lidx[1].val, [0, 2, 2])
        il = Ilist.ntv([['a', 'b', 'c'], [1, 2, 2], [4, 5, 5]])
        il.updateindex(["d", 8, 2], 1)
        il.append(["z", 1, 10])
        self.assertEqual(il.idxlen, [4, 4, 3])

    def test_add(self):
        il1 = Ilist.ntv([['er', 'rt', 'er', 'ry', 'ab'],
                         [0, 2, 0, 2, 0], [10, 0, 20, 20, 15]])
        il2 = Ilist.ntv([['_er', '_rt', '_er', '_ry', '_ab'], [10, 12, 10, 12, 10],
                         [110, 10, 120, 120, 115]])
        il3 = il1 + il2
        self.assertEqual(len(il3), len(il1) + len(il2))
        self.assertEqual(il2.loc(["_rt", 12, 10]), il3.loc(["_rt", 12, 10]))
        self.assertEqual(il1.loc(['er', 0, 20]), il3.loc(['er', 0, 20]))
        il2 = Ilist.obj([['_er', '_rt', '_er', '_ry', '_ab'], [10, 2, 10, 12, 10],
                         [110, 0, 120, 120, 115]])
        il3 = il1 + il2
        self.assertEqual(len(il3), len(il1) + len(il2))
        self.assertEqual(il2.loc(['_ry', 12, 120]), il3.loc(['_ry', 12, 120]))
        self.assertEqual(il1.loc(['er', 0, 20]), il3.loc(['er', 0, 20]))

    def test_swap(self):
        il = Ilist.ntv([[[10, 20, 30], [2]], [[100, 200, 300], 0], [[True, False], [1]]])
        il1 = copy(il)
        il.swapindex([2, 0, 1])
        il.swapindex([2, 0, 1])
        il.swapindex([2, 0, 1])
        self.assertEqual(il, il1)

    def test_list(self):
        il = Ilist.ntv([[1, 2, 3, 4, 5, 6]])
        self.assertEqual(il[1].val, 2)
        il[1] = 3
        self.assertEqual(il[1].val, 3)
        self.assertEqual(len(il), 6)

    def test_extend(self):
        il1 = Ilist.ntv([['er', 'rt', 'er', 'ry', 'ab'], [0, 2, 0, 2, 0],
                         [10, 0, 20, 20, 15]])
        il2 = Ilist.ntv([['_er', '_rt', '_er', '_ry', '_ab'], [10, 12, 10, 12, 10],
                         [110, 10, 120, 120, 115]])
        il3 = il1 | il2
        self.assertEqual(il3, il1)
        il = Ilist.ntv([['er', 'rt', 'er', 'ry', 'ab', 'ert']])
        ilx = Ilist.ntv([[0, 0, 0, 1, 1, 1], [0, 1, 2, 3, 4, 1]])
        il2 = il | ilx
        self.assertEqual(il2.lindex[0], il.lindex[0])
        il2 = Ilist.ntv([['_er', '_rt', '_er', '_ry', '_ab'], [10, 2, 10, 12, 10],
                         [110, 0, 120, 120, 115]])
        il2.addindex({'truc': [['un', 'deux'], [0, 0, 1, 1, 0]]})
        il2.addindex({'truc2': ['un', 'de', 'un', 'de', 'un']})
        il2.reindex()
        self.assertEqual(
            il2.loc(['_ry', 12, 120, "deux", "de"], row=True), [3])

    def test_append(self):
        il = Ilist.ntv([[0, 2, 0, 2], [30, 12, 20, 15]])
        il.append([0, 20], unique=True)
        self.assertEqual(len(il), 4)
        il.append([0, 40])
        self.assertEqual(len(il), 5)
        self.assertEqual(il, Ilist.ntv(
            [[0, 2, 0, 2, 0], [30, 12, 20, 15, 40]]))
        il = Ilist.ntv([{'::point': [{'paris': [2.35, 48.87]}, [4.83, 45.76],
                         [5.38, 43.3]]}])
        il.append([{':point':[4.83, 45.76]}])
        self.assertEqual(len(il), 4)
        self.assertEqual(len(il.lindex[0].codec), 3)

    def test_append_variable(self):
        il = Ilist.ntv([['er', 'rt', 'er', 'ry'], [
                       0, 2, 0, 2], [30, 12, 20, 15]])
        il.append(['truc', 0, 20], unique=True)
        self.assertEqual(len(il), 5)
        il.append(['truc', 0, 20], unique=True)
        self.assertEqual(len(il), 5)
        self.assertEqual(il, Ilist.ntv([['er', 'rt', 'er', 'ry', 'truc'],
                                        [0, 2, 0, 2, 0], [30, 12, 20, 15, 20]]))

    def test_magic(self):
        iidx5 = Ilist.ntv({'datationvalue': [10, 10, 20, 20, 30, 30],
                           'locationvalue': [100, 100, 200, 200, 300, 300],
                           'propertyvalue': [True, False, True, False, True, False]})
        self.assertEqual(iidx5.lidx[0], Iindex.ntv({'datationvalue': [10, 10, 20, 20, 30, 30]}))
        self.assertEqual(iidx5.idxname, ['datationvalue', 'locationvalue',
                                         'propertyvalue'])
        iidx5 += iidx5
        self.assertEqual(len(iidx5), 12)
        iidx5 |= iidx5
        self.assertEqual(len(iidx5.lidx), 3)
        iidx5.orindex(iidx5, first=False, merge=False, update=False)
        self.assertEqual(len(iidx5.lidx), 6)
        iidx6 = Ilist() | iidx5
        iidx7 = iidx5 | Ilist()
        self.assertTrue(iidx6 == iidx7)
        self.assertTrue(iidx5 == iidx6 == iidx7)

    def test_primary(self):
        #['ext', ['er', 'rt', 'er', 'ry']]
        ilm = Ilist.ntv([['math', 'english', 'software', 'physic', 'english', 'software'],
                         ['philippe', 'philippe', 'philippe',
                          'anne', 'anne', 'anne'],
                         [nan, nan, nan, 'gr1', 'gr1', 'gr2'],
                         ['philippe white', 'philippe white', 'philippe white',
                          'anne white', 'anne white', 'anne white']])
        self.assertEqual(ilm.primary, [])
        ilm = Ilist.ntv([{'ext': ['er', 'rt', 'er', 'ry']}, [0, 2, 0, 2],
                         [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 12, 15, 30]])
        self.assertEqual(ilm.primary, [0, 2])
        ilm = Ilist.ntv([{'ext': ['er', 'rt', 'er', 'ry']}, [0, 2, 0, 2],
                         [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 20, 20, 12]])
        self.assertEqual(ilm.primary, [0, 2])
        ilm = Ilist.ntv([[0, 2, 0, 2], [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 12, 15, 30]])
        self.assertEqual(ilm.primary, [0, 2])
        ilm = Ilist.ntv([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 20, 20, 12]])
        self.assertEqual(ilm.primary, [0, 2])

    def test_to_ntv(self):
        ilm = Ilist.ntv([[ 0,   0,   2,   3,   4,   4,   6,
                           7,   8,   9,   9,  11,  12],
                         ['j', 'j', 'f', 'a', 'm', 'm', 's',
                          's', 's', 'n', 'd', 'd', 'd'],
                         ['t1', 't1', 't1', 't2', 't2', 't2', 't3',
                          't3', 't3', 't4', 't4', 't4', 't4'],
                         ['s11', 's1', 's1', 's1', 's1', 's11', 's2',
                          's2', 's2', 's1', 's2', 's2', 's2'],
                         [2021, 2021, 2021, 2021, 2021, 2021, 2021,
                          2021, 2021, 2021, 2021, 2021, 2021],
                         ['t1', 't1', 't1', 't2', 't2', 't2', 't3',
                          't3', 't3', 't4', 't4', 't4', 't4']])
        coupling = [True, False]
        keyscrd = [True, False]
        test = list(product(coupling, keyscrd))
        for ts in test:
            # ilm.reindex()
            if ts[0]:
                ilm.coupling()
            if ts[1]:
                ilm.lidx[0].tostdcodec(inplace=True)
            self.assertEqual(Ilist.from_ntv(ilm.to_ntv()), ilm)
            #self.assertEqual(Ilist.from_obj(ilm.to_obj()).to_obj(), ilm.to_obj())
        encoded = [False, True]
        format = ['json', 'cbor']
        modecodec = ['full', 'default', 'optimize']
        #modecodec = ['full', 'default', 'optimize', 'dict']
        #defaultcodec = [False, False]
        test = list(product(encoded, format, modecodec))
        for ts in test:
            opt = {'encoded': ts[0],
                   'encode_format': ts[1], 'modecodec': ts[2]}
            self.assertEqual(Ilist.ntv(ilm.to_ntv(ts[2]).to_obj(**opt)), ilm)
            ilm.to_file('test.il', **opt)
            self.assertEqual(Ilist.from_file('test.il'), ilm)
        ilm = Ilist.ntv([[6, 7, 8, 9, 9, 11, 12],
                         ['s', 's', 's', 'n', 'd', 'd', 'd']])
        ilm.coupling()
        for ts in test:
            opt = {'encoded': ts[0],
                   'encode_format': ts[1], 'modecodec': ts[2]}
            self.assertEqual(Ilist.from_ntv(ilm.to_ntv(ts[2]).to_obj(**opt)), ilm)
        il = Ilist.ntv({'produit': ['po', 'po', 'or', 'or', 'pi', 'pi', 'ba', 'ba'], 
                        'aliment': ['fr', 'fr', 'fr', 'fr', 'le', 'le', 'fr', 'fr'],
                        'contenant': ['sa', 'ca', 'sa', 'ca', 'sa', 'ca', 'sa', 'ca'],
                        'prix': [1, 9, 2, 18, 1.5, 13, 0.5, 4],
                        'dispo': [1,1,0,0,0,0,1,1]})
        self.assertEqual(Ilist.from_ntv(il.to_ntv()), il)
        
    def test_to_ntv_variable(self):
        il = Ilist.ntv([[0, 1, 2, 3, 4, 5],
                        ['j', 'j', 'f', 'f', 'a', 'a'],
                        [100, 100, 200, 200, 300, 300],
                        [True, False, True, False, True, False]])
        self.assertEqual(Ilist.ntv(il.to_ntv()), il)
        il.setcanonorder()
        self.assertEqual(Ilist.ntv(il.to_ntv()), il)
        self.assertEqual(Ilist.ntv({}), Ilist())

    def test_coupling(self):
        ilx = Ilist.ntv([['a', 'b', 'b', 'c', 'c', 'a'],
                         [20,  10,  10,  10,  10,  20],
                         [200, 200, 300, 200, 300, 300]])
        self.assertTrue(ilx.complete)
        ilx.lindex[1].coupling(ilx.lindex[0], derived=False)
        self.assertTrue(ilx.indexinfos()[1]['cat'] == 'coupled')
        ilx.reindex()
        self.assertTrue(ilx.indexinfos()[1]['cat'] == 'secondary')
        il = Ilist.ntv([[1, 2, 3, 4, 5, 6], ['a', 'b', 'b', 'c', 'c', 'a'],
                        [20, 10, 10, 10, 10, 20], [200, 200, 300, 200, 300, 300]])
        self.assertTrue(il.complete)
        il.lindex[2].coupling(il.lindex[1], derived=False)
        self.assertTrue(il.indexinfos()[2]['cat'] == 'coupled')
        il.reindex()
        self.assertTrue(il.indexinfos()[2]['cat'] == 'secondary')
        ilx = Ilist.ntv([['a', 'b', 'b', 'c', 'c', 'a', 'd', 'e', 'd'],
                         [20,  20,  10,  30,  10,  20,  20,  30,  40],
                         [100, 200, 300, 400, 400, 200, 200, 500, 600]])
        ilx.coupling()
        self.assertTrue(ilx == Ilist.ntv(ilx.to_ntv()))
        ilx.setcanonorder()
        self.assertTrue(ilx == Ilist.ntv(ilx.to_ntv()))

    def test_duplicates(self):
        ilx = Ilist.ntv([['a', 'b', 'b', 'c', 'c', 'a'],
                         [20,  10,  10,  10,  10,  20],
                         [200, 200, 400, 200, 300, 300],
                         [1, 1, 2, 2, 3, 3]])
        ilx.coupling(derived=False, level=0.2)
        ilx.getduplicates(['i1'], 'dup-i1')
        self.assertEqual(ilx.nindex('dup-i1').val, [
                         True, False, False, False, False, True])
        ilx = Ilist.ntv([['a', 'b', 'b', 'c', 'c', 'a'],
                         [20,  10,  10,  10,  10,  20],
                         [200, 200, 200, 300, 300, 200],
                         [1, 1, 1, 2, 3, 1]])
        ilx.coupling(level=0.2)
        ilx.getduplicates(resindex='dupli')
        self.assertEqual(ilx.nindex('dupli').val, [
                         True, True, True, False, False, True])

    def test_name(self):
        ilm = Ilist.ntv([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 20, 20, 12]])
        ilm.full()
        self.assertTrue(ilm.ntv(ilm.to_ntv()) == ilm)

    def test_full(self):
        ilm = Ilist.ntv([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 20, 20, 12]])
        self.assertTrue(ilm.complete)
        self.assertTrue(ilm.full(inplace=False, complete=False) == ilm)
        ilmf = ilm.full(idxname=['i0', 'i1'], inplace=False)
        self.assertTrue(ilmf.nindex('i0').iscrossed(ilmf.nindex('i1')))
        self.assertTrue(ilmf.nindex('i0').iscoupled(ilmf.nindex('i2')))
        ilm.full(idxname=['i0', 'i3', 'i5'])
        self.assertTrue(ilm.nindex('i0').iscrossed(ilm.nindex('i3')) ==
                        ilm.nindex('i0').iscrossed(ilm.nindex('i5')) ==
                        ilm.nindex('i3').iscrossed(ilm.nindex('i5')) == True)
        self.assertTrue(ilm.complete)
        il = Ilist.ntv([['er', 'rt', 'er', 'ry'], [0, 2, 0, 2], [30, 12, 20, 30],
                        [2, 0, 2, 0], [2, 2, 0, 0],
                        ['info', 'info', 'info', 'info'], [12, 20, 20, 12]])
        ilc = il.full(inplace=False)
        ild = il.full(idxname=['i2', 'i6', 'i1', 'i3',
                      'i4', 'i5'], inplace=False)
        self.assertEqual(len(ild), 48)
        self.assertTrue(il.nindex('i5').codec == ilc.nindex('i5').codec ==
                        ild.nindex('i5').codec)

    def test_valtokey(self):
        ilm = Ilist.ntv([[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0],
                         ['info', 'info', 'info', 'info'], [12, 20, 20, 12]])
        self.assertEqual(ilm.keytoval(ilm.valtokey([2, 12, 0, 2, 'info', 20])), [
                         2, 12, 0, 2, 'info', 20])

    def test_vlist(self):
        il = Ilist.ntv([[1, 2, 3]])
        self.assertEqual(il.vlist(2, func=pow), [1, 4, 9])
        il = Ilist.ntv([['er', 'ar', 'ty']])
        self.assertEqual(il.vlist(func=len), [2, 2, 2])
        #il = Ilist.ntv([[datetime(2010, 1, 2), datetime(2012, 1, 2)]])
        #self.assertEqual(il.vlist(func=datetime.isoformat, timespec='hours',
        #                          sep='-', extern=False), ['2010-01-02-00', '2012-01-02-00'])
        il = Ilist.ntv([['aer', 'e', 'h'], [1, 2, 3],
                       ['a', 'efg', 'h'], [0, 1, 0]])
        self.assertEqual(il.vlist(func=len, index=2), [1, 3, 1])
        il = Ilist.ntv([[1, 2, 3, 4], [{'morning:time': '08:00:00', 'afternoon:time': '14:00:00'}, [2]],
                        [{'paris:point': None, ':point':[4.1, 42.8]}, [1]]])
        self.assertEqual(il.vlist(func=Ntv.to_name, extern=False, index=1),
                         ['morning', 'morning', 'afternoon', 'afternoon'])
        self.assertEqual(il.vlist(func=Ntv.to_name, extern=False, index=2, default='ici'),
                         ['paris', 'ici', 'paris', 'ici'])

    """def test_mergerecord(self):
        a = Ilist.ntv([[1, 2, 3], [4, 5, 6]])
        b = Ilist.ntv({'merge_i0': ['x'], 'merge': [a]})
        self.assertEqual(Ilist._mergerecord(b)[0].lenindex, 3)

    def test_merge(self):
        il1 = Ilist.dic({'notes': [10, 11, 12],
                         'course': ['math', 'english', 'software']})
        il2 = Ilist.dic({'notes': [15, 14, 11],
                         'course': ['physic', 'english', 'software'],
                         'group': ['gr1', 'gr1', 'gr2']})
        il3 = Ilist.dic({'student': [il1, il2],
                         'name': ['philippe white', 'anne white'],
                         'firstname': ['philippe', 'anne'],
                         'student_group': ['gr1', 'gr2']})
        self.assertEqual(il3.merge()[4], [
                         14, 'english', 'anne white', 'anne', 'gr1'])
        il3s = Ilist.dic({'student': [il1, il2],
                          'name': ['philippe white', 'anne white'],
                          'firstname': ['philippe', 'anne'],
                          'group': ['gr1', 'gr2']})
        self.assertEqual(il3s.merge(simplename=True)[4], [
                         14, 'english', 'anne white', 'anne', 'gr1'])
        il3 = Ilist.ntv([[il1, il2]], typevalue=None)
        self.assertEqual(il3.merge()[4], [14, 'english', 'gr1'])"""

    def test_csv(self):
        il = Ilist.ntv([['er', 'rt', 'er', 'ry'], [
                       0, 2, 0, 2], [30, 12, 20, 15]])
        il.to_csv('test.csv')
        il2 = Ilist.from_csv('test.csv')
        self.assertTrue(il == il2)
        '''if ES.def_clsName:
            il.to_csv(ifunc=ESValue.vSimple)
            il.to_csv(ifunc=ESValue.json, encoded=False)
            il3 = Ilist.from_csv(var=0)
            self.assertTrue(il == il3)'''
        il = Ilist.ntv([['er', 'rt', 'er', 'ry', 'ab'], [0, 2, 0, 2, 0],
                        [10, 0, 20, 20, 15], [1, 2, 1, 2, 1]])
        il.to_csv('test.csv', optcsv={
                  'dialect': 'excel', 'delimiter': ';', 'quoting': csv.QUOTE_NONNUMERIC})
        il2 = Ilist.from_csv('test.csv', optcsv={'dialect': 'excel', 'delimiter': ';',
                                                 'quoting': csv.QUOTE_NONNUMERIC})
        self.assertTrue(il == il2)

    """def test_axes(self):

        il1 = Ilist.dic({'notes': [10, 11, 12],
                         'course': ['math', 'english', 'software']})
        il2 = Ilist.dic({'notes': [15, 14, 11],
                         'course': ['math', 'english', 'software'],
                         'group': ['gr1', 'gr1', 'gr2']})
        il3 = Ilist.dic({'list': [il1, il2],
                         'name': ['philippe white', 'anne white'],
                         'firstname': ['philippe', 'anne']})
        self.assertEqual(
            il3.merge().primary, [0, 1])"""

    def test_sort(self):
        il = Ilist.ntv([['er', 'rt', 'er', 'ry'], [
                       0, 2, 0, 2], [30, 12, 20, 15]])
        il.sort()
        self.assertEqual(il.lindex[0].keys, sorted(il.lindex[0].keys))
        il.sort([2, 1, 0], reverse=True)
        self.assertEqual(il.lindex[2].keys, [3, 2, 1, 0])
        il.sort([1, 0, 2])
        self.assertEqual(il.lindex[1].keys, [0, 0, 1, 1])

    def test_filter(self):
        il = Ilist.ntv([['er', 'rt', 'er', 'ry'], [
                       0, 2, 0, 2], [30, 12, 20, 15]])
        il.setfilter([True, False, True, False])
        il.applyfilter()
        self.assertEqual(il.lindex[1].val,   [0, 0])
        il = Ilist.ntv([['er', 'rt', 'er', 'ry'], [
                       0, 2, 0, 2], [30, 12, 20, 15]])
        il.setfilter([True, False, True, False])
        il.applyfilter(reverse=True)
        self.assertEqual(il.lindex[1].val,   [2, 2])
        il1 = Ilist.ntv([['er', 'rt', 'er', 'ry', 'ry', 'er'],
                         [0, 2, 0, 2, 0, 2], [30, 12, 20, 15, 30, 12]])
        ilft1 = il1.setfilter(
            [True, True, True, True, True, True]).applyfilter(inplace=False)
        ilfr1 = il1.setfilter([True, True, True, True, True, True]).applyfilter(
            reverse=True, inplace=False)
        ilfr2 = il1.setfilter(
            [False, False, False, False, False, False]).applyfilter(inplace=False)
        ilft2 = il1.setfilter([False, False, False, False, False, False]).applyfilter(
            reverse=True, inplace=False)
        self.assertTrue(il1.sort() == ilft1.sort() == ilft2.sort())
        self.assertTrue(Ilist.ntv([[], [], []]) == ilfr1 == ilfr2)
        '''
        il = Ilist.ntv(f,l).setfilter([[0, 2], [12, 20, 30]], inplace=False, index=False)
        self.assertEqual( il.setidx, [[0, 2], [30, 12, 20]])
        il = Ilist.ntv(f,l).setfilter([[2], [12, 20, 30]], inplace=False, index=False)
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
        '''à faire'''  # !!!

    """def test_to_xarray(self):
        ilm = Ilist.ntv({'plants': ['fruit', 'fruit', 'fruit', 'fruit',
                                    'vegetable', 'vegetable', 'vegetable', 'fruit'],
                         'quantity': ['kg', '10 kg', 'kg', '10 kg',
                                      'kg', '10 kg', 'kg', '10 kg'],
                         'product': ['apple', 'apple', 'orange', 'orange',
                                     'peppers', 'peppers', 'banana', 'banana'],
                         'price': [1, 10, 2, 20, 1.5, 15, 0.5, 5]})
        ilm.nindex('product').coupling(ilm.nindex('plants'))
        ilm.full(idxname=['product', 'quantity'])
        ilx = ilm.to_xarray()
        self.assertEqual(float(ilx.sel(quantity='10 kg', product='apple').values),
                         float(ilm.loc(['10 kg', 'apple', 'fruit'])[0][3]))
        self.assertTrue(str(ilm.loc(['10 kg', 'banana', 'fruit'])[0][3]) in
                        str(ilx.sel(quantity='10 kg', product='banana').values))
        '''fruit = Ilist.obj([['product', ['apple', 'apple', 'orange', 'orange', 'banana', 'banana']],
                           ['quantity', ['kg', '10 kg', 'kg', '10 kg', 'kg', '10 kg']],
                           ['price', [1, 10, 2, 20, 0.5, 5]]])
        vege = Ilist.obj([['product', ['peppers', 'peppers']],
                          ['quantity', ['kg', '10 kg']],
                          ['price', [1.5, 15]]])
        total = Ilist.obj([['plants', ['fruit', 'vegetable']],
                           ['total', [fruit, vege]]])
        ilx2 = total.merge().to_xarray()
        self.assertEqual(float(ilx2.sel(total_quantity='10 kg', total_product='apple').values),
                         float(ilm.loc(['10 kg', 'apple', 'fruit'])[0][3]))
        self.assertTrue(str(ilm.loc(['10 kg', 'banana', 'fruit'])[0][3]) in
                        str(ilx2.sel(total_quantity='10 kg', total_product='banana').values))'''
        il = Ilist.ntv({'locatio': [0, [4.83, 45.76], [5.38, 43.3]],
                         'datatio': [[{'date1': '2021-02-04T11:05:00+00:00'},
                                      '2021-07-04T10:05:00+00:00',
                                      '2021-05-04T10:05:00+00:00'],
                                     0],
                         'propert': [{'prp': 'PM25', 'unit': 'kg/m3'},
                                     {'prp': 'PM10', 'unit': 'kg/m3'}],
                         'result': [[{'ert': 0}, 1, 2, 3, 4, 5], -1]})
        '''il = Ilist.obj([['locatio', [0, [4.83, 45.76], [5.38, 43.3]]],
                        ['datatio', [{'date1': '2021-02-04T11:05:00+00:00'},
                                     '2021-07-04T10:05:00+00:00',
                                     '2021-05-04T10:05:00+00:00'], 0],
                        ['propert', [{'prp': 'PM25', 'unit': 'kg/m3'},
                         {'prp': 'PM10', 'unit': 'kg/m3'}]],
                        ['result', [{'ert': 0}, 1, 2, 3, 4, 5]]])'''
        ilx1 = il.to_xarray(lisfunc=[None, None, None, ESValue.to_float])
        ilx2 = il.to_xarray(
            lisfunc=[None, None, None, util.cast], dtype='float')
        ilx3 = il.to_xarray(numeric=True)
        self.assertTrue(list(ilx1.values[0]) == list(
            ilx2.values[0]) == list(ilx3.values[0]))"""

    def test_example(self):
        '''à faire'''  # !!!

    """def test_to_obj_file(self):  # !!!
        il = Ilist.obj([['result', [0, 1, 2, 3, 4, 5]],
                        ['datation', [DatationValue.ntv(dat3[1][0]),
                                      DatationValue.ntv(dat3[1][1]),
                                      DatationValue.ntv(dat3[1][2])]],
                        ['location', [LocationValue.ntv(loc3[1][0]),
                                      LocationValue.ntv(loc3[1][1]),
                                      LocationValue.ntv(loc3[1][2])], 1],
                        ['property', [PropertyValue(prop2[1][0]), PropertyValue(prop2[1][1])]]])
        encoded = [True, False]
        format = ['json', 'cbor']
        test = list(product(encoded, format))
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1]}
            #il2 = Ilist.ntv(il.to_ntv(**option))
            # self.assertEqual(il, il2)   #!!!"""

    def test_to_ntv_simple(self):
        tab_data   = ({'value':           [10, 20, 30, 40],
                      'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21', '2022-01-22'],
                      'value32::int32':  [10, 20, 30, 40],
                      'coord::point':    [[1,2], [3,4], [5,6], [7,8]],
                      'names::string':   ['john', 'eric', 'judith', 'max'],
                      'index':           [1, 2, 3, 4],
                      'complete_test':   [['a', 'b'], [0, 0, 1, 0]],
                      'complete_date':   [{"::date": ["2000-01-01", "2000-02-01"]}, [0, 0, 1, 0]],
                      'implicit_test':   [['a', 'b'], [1]],
                      'implicit_test2':  [['a', 'b'], [2]],
                      'unic_test':       'valunic' },
                      [['1964-01-01', '1985-02-05', '2022-01-21', '2022-01-22'], 
                      [10, 20, 30, 40],
                      [10, 20, 30, 40],
                      [[1,2], [3,4], [5,6], [7,8]],
                      ['john', 'eric', 'judith', 'max'],
                      [1, 2, 3, 4],
                      [['a', 'b'], [0, 0, 1, 0]],
                      [['a', 'b'], [1]],
                      [['a', 'b'], [2]],
                      'valunic' ] )
        for tab in tab_data:
            lis = [tab, json.dumps(tab), Ntv.obj(tab)]
            for il in lis:
                il = Ilist.from_ntv(tab)
                for mode in ['full', 'default', 'optimize']:
                    #print(to_ntv_ilist(il, mode))
                    self.assertEqual(il, Ilist.from_ntv(il.to_ntv(mode)))

    def test_matrix(self):
        ntv = Ntv.obj({'matrix': [{"annee": [[2000, 2010],         [1]]}, 
                                  {"pays":  [['france', 'italie'], [2]]}, 
                                  {"age":   [[10, 50, 100],        [4]]}, 
                                  {"result":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}]})
        il = Ilist.from_ntv(ntv)
        self.assertEqual(il.primaryname, ['annee', 'pays', 'age'])
        self.assertEqual(il.lvarname, ['result'])
    
    """
    '''for forma in ['json', 'cbor']:
        #for forma in ['json', 'cbor']:
            for encoded in [False, True]:
                for codif in [ES.codeb, {}]:
                    il2 = Ilist2.ntv(il.to_ntv(encoded=encoded, encode_format=forma, codif=codif))
                    il2.setidx[0] = DatationValue.cast(il2.setidx[0])
                    il2.setidx[1] = LocationValue.cast(il2.setidx[1])
                    il2.setidx[2] = PropertyValue.cast(il2.setidx[2])
                    #il2.extval = ReesultValue.cast(il2.extval)
                    self.assertEqual(il.to_ntv(encoded=False), il2.to_ntv(encoded=False))
        il3 = Ilist2.ntv(il.to_ntv(encoded=False))
        il3.setidx[0] = DatationValue.cast(il3.setidx[0])
        il3.setidx[1] = LocationValue.cast(il3.setidx[1])
        il3.setidx[2] = PropertyValue.cast(il3.setidx[2])
        #il3.extval=ReesultValue.cast(il3.extval)
        self.assertEqual(il.to_ntv(encoded=False), il3.to_ntv(encoded=False))
        il=Ilist2.ext(['er', 'rt', 'er', 'ry'], [[0, 2, 0, 2], [30, 12, 20, 15]]
                      ).sort(order=[0,1], inplace=False)
        ilf = il.full(axes=[0,1]).sort(order=[0,1], inplace=False)
        self.assertEqual(il, il.ntv(il.json()).sort(order=[0,1], inplace=False))
        self.assertEqual(ilf, il.ntv(ilf.json()))
        for forma in ['json', 'cbor']:
            il.to_file('test.tst', encode_format=forma)
            ilf.to_file('testf.tst', encode_format=forma)
            self.assertEqual(il, il.from_file('test.tst').sort(order=[0,1], inplace=False))
            self.assertEqual(ilf, il.from_file('testf.tst'))'''
"""

if __name__ == '__main__':
    unittest.main(verbosity=2)
