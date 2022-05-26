# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: Philippe@loco-labs.io

The `ES.test_ilist` module contains the unit tests (class unittest) for the
`Ilist` functions.
"""
import unittest
from ilist import Ilist
from copy import copy
import csv #, os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from test_observation import dat3, loc3, prop2, _res
from ESObservation import Observation
from ESValue import NamedValue, DatationValue, LocationValue, PropertyValue, ESValue #, ReesultValue
from datetime import datetime
from ESconstante import ES

#import ..\ESValue

f = ['er', 'rt', 'er', 'ry']
l = [[0, 2, 0, 2], [30, 12, 20, 15]]
il=Ilist.Iext(f,l)

class Test_ilist(unittest.TestCase):

    il = Ilist.Iidic({}, {'id1':[0,1,2], 'id2':[3,4,5]})

    def test_static(self) :
        self.assertEqual( il._toext(il._toint(f, il._toset(f)), il._toset(f)), f)
        self.assertEqual( il._reorder(f, il.sortidx([0,1])), ['er', 'er', 'rt', 'ry'])
        self.assertTrue( il._coupled([0,0,1,1], [2,2,1,1]))
        self.assertFalse( il._coupled([0,0,1,1], [2,1,2,1]))
        self.assertEqual( il._transpose(il._transpose(il.iidx)), il.iidx)

    def test_creation_list(self) :
        self.assertEqual(Ilist.Iext([[1,2], [0,1], [1,2]], [0, 1, 2]).sort(inplace=False).iidx,
                         Ilist.Iext(['b', 'a', 'b'], [0, 1, 2]).sort(inplace=False).iidx)

    def test_creation(self) :
        self.assertEqual(Ilist.Iext(['a', 'b', 'c']), Ilist.Iext(['a', 'b', 'c'], [0, 1, 2]))
        self.assertEqual(Ilist.Iext(extidx=[1, 2, 3]), Ilist.Iext([True, True, True], [1, 2, 3]))
        self.assertEqual(Ilist.Iext(extidx=[[1, 2, 3]]), Ilist.Iext([True, True, True], [1, 2, 3]))

    def test_init_dict(self) :
        il = Ilist.Iidic({'namvalue' : ['a', 'b', 'c', 'd', 'e', 'f']},
                         {'datationvalue' : [10,20,30],
                          'locationvalue' : [100,200,300],
                          'propertyvalue' : [True, False]},
                          idxref=[0,0,2], order = [0,2])
        il2 =Ilist.Iidic({'namvalue' :[['a', [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]], ['d', [1, 1, 1]],
                                         ['e', [2, 2, 0]], ['f', [2, 2, 1]]]},
                         {'datationvalue' : [10,20,30],
                          'locationvalue' : [100,200,300],
                          'propertyvalue' : [True, False]})
        il3 =Ilist.Iedic({'namvalue'   : ["a", "b", "c", "d", "e", "f"]}, 
                         {'datationvalue' : [10, 10, 20, 20, 30, 30],
                          'locationvalue' : [100, 100, 200, 200, 300, 300],
                          'propertyvalue' : [True, False, True, False, True, False]})   
        self.assertEqual(il.iidx[1], [0, 0, 1, 1, 2, 2])
        self.assertEqual(il, il2, il3)
        il2 =Ilist.Iidic({'namvalue' :[[{'a':5}, [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]], ['d', [1, 1, 1]],
                                         ['e', [2, 2, 0]], [['f', 'g'], [2, 2, 1]]]},
                         {'datationvalue' : [[{'a':5}, [0, 0, 0]],20,{'a':5, 'r':'r'}],
                          'locationvalue' : [100,200,300],
                          'propertyvalue' : [True, False]})
        self.assertEqual(il.iidx[1], [0, 0, 1, 1, 2, 2])

    def test_init_set(self) :
        il = Ilist.Iset(['a', 'b', 'c', 'd', 'e', 'f'], [[10,20,30],[100,200,300], [True, False]],
                         idxref=[0,0,2], order = [0,2])
        il2 = Ilist.Iset([['a', [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]], ['d', [1, 1, 1]],
                          ['e', [2, 2, 0]], ['f', [2, 2, 1]]], [[10,20,30],[100,200,300], [True, False]])
        self.assertEqual(il.iidx[1], [0, 0, 1, 1, 2, 2])
        self.assertEqual(il, il2)

    def test_init_from_obj(self):
        il=Ilist.from_obj(dict((dat3, loc3, prop2, _res(6)))|{'idxref': {'location':'datation'}, 
                        'order':['property', 'datation', 'location']})
        self.assertTrue(isinstance(il.setidx[1][0], DatationValue))
        self.assertTrue(isinstance(Ilist.from_obj(), Ilist))
        self.assertEqual(Ilist.from_obj(Ilist().json()), Ilist())
        
    def test_init_index(self) :
        order = [2,0]
        idxlen = [3,3,2]
        idxref = [0,0,2]
        extval = ['a', 'b', 'c', 'd', 'e', 'f']
        self.assertEqual( Ilist.Iidx(extval, idxlen, idxref, order).idxlen, idxlen)
        self.assertEqual( Ilist.Iidx(extval, idxlen, idxref, order).idxref, idxref)
        idxlen = [2,3,3]
        idxref = [0,1,1]
        self.assertEqual( Ilist.Iidx(extval, idxlen, idxref, order).idxlen, idxlen)
        self.assertEqual( Ilist.Iidx(extval, idxlen, idxref, order).idxref, idxref)
        order = []
        idxlen = [3,3,3]
        idxref = [0,0,0]
        extval = ['a', 'b', 'c']
        self.assertEqual( Ilist.Iidx(extval, idxlen, idxref, order).iidx[1], [0, 1, 2])

    def test_properties(self) :
        l = [[0, 2, 0, 2], [30, 12, 12, 15], [2, 0, 2, 0], [2, 2, 0, 0], ['info', 'info', 'info', 'info'],[12, 12, 15, 30]]
        il=Ilist.Iext(f,l)
        self.assertEqual( il.idxref, [0, 1, 0, 3, 4, 5])
        self.assertEqual( il.idxlen, [2, 3, 2, 2, 1, 3])
        self.assertEqual( il.dimension, 3)
        self.assertEqual( il.lencompletefull, 18)
        l = [[0, 2, 0, 0], [30, 12, 20, 20]]
        il=Ilist.Iext(f,l)
        self.assertFalse( il.consistent)
        l = [[0, 2, 0, 1], [30, 12, 20, 20]]
        il=Ilist.Iext(f,l)
        self.assertTrue( il.consistent)

    def test_sort(self) :
        il=Ilist.Iext(f,l)
        self.assertEqual( il.sortidx([0]),   [0, 2, 1, 3])
        self.assertEqual( il.sortidx([1]),   [1, 3, 2, 0])
        self.assertEqual( il.sortidx([1,0]), [1, 3, 2, 0])
        self.assertEqual( il.sortidx([0,1]), [2, 0, 1, 3])
        self.assertEqual( il.sort(inplace=False).sort(inplace=False), il.sort(inplace=False))
        self.assertEqual( il.reorder([1,3], inplace=False).idxlen, [1,2])

    def test_filter(self):
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
        self.assertEqual(Ilist._filter(ESValue.getName, ob.setDatation, 'date1'), [0])

    def test_full(self) :
        f = ['er', 'rt', 'er', 'ry']
        l = [[0, 2, 0, 2], [30, 12, 20, 30], [2, 0, 2, 0], [2, 2, 0, 0], ['info', 'info', 'info', 'info'],[12, 20, 20, 12]]
        il=Ilist.Iext(f,l)
        ilc=il.full()
        #ild=il.full(minind=False)
        ild=il.full(axes=list(range(il.lenidx)))
        self.assertEqual( len(ild), 48)
        self.assertEqual( ild.idxref,  [0, 1, 2, 3, 4, 5])
        self.assertEqual( ilc.extidx[1], [30, 12, 20, 30, 30, 12, 12, 20, 30, 12, 20, 20])
        self.assertEqual( ilc.idxcoupled, il.idxcoupled)
        self.assertTrue( ilc.idxlen == il.idxlen == ild.idxlen)
        self.assertEqual( ilc.idxref, il.idxref)
        self.assertTrue( ilc.idxunique == il.idxunique == ild.idxunique)

    def test_append(self) :
        il=Ilist.Iext(['er', 'rt', 'er', 'ry'], [[0, 2, 0, 2], [30, 12, 20, 15]])
        il.append('truc', [0,20], unique = True)
        self.assertEqual( len(il), 4)
        il.append('truc', [0,40])
        self.assertEqual( len(il), 5)
        self.assertEqual( il, Ilist.Iext(['er', 'rt', 'er', 'ry', 'truc'], [[0, 2, 0, 2, 0], [30, 12, 20, 15, 40]]))

    def test_vlist(self) :
        il = Ilist.Iext([1,2,3])
        self.assertEqual(il.vlist(2, func=pow), [1, 4, 9])
        il = Ilist.Iext(['er', 'ar', 'ty'])
        self.assertEqual(il.vlist(func=len), [2, 2, 2])
        self.assertEqual(il.vlist(func=Ilist._index), [0, 1, 2])
        il = Ilist.Iext([datetime(2010, 1,2), datetime(2012, 1,2)])
        self.assertEqual(il.vlist(func=datetime.isoformat,timespec='hours', sep='-'),
                         ['2010-01-02-00', '2012-01-02-00'])
        il =Ilist.Iext(['aer', 'e', 'h'], [[1,2,3], ['a', 'efg', 'h'], [0,1,0]])
        self.assertEqual(il.vlist(func=len, idx=1), [1, 3, 1])
        il=Ilist.Iext([1,2,3,4], [[DatationValue('morning'), DatationValue('afternoon')],
                             [LocationValue('paris'), LocationValue([4.1, 42.8])]])
        self.assertEqual(il.vlist(func=ESValue.vName, idx=0), ['morning', 'afternoon'])
        self.assertEqual(il.vlist(func=ESValue.vName, idx=1, genName='ici'), ['paris', 'ici'])

    def test_add_update_list(self) :
        il=Ilist.Iext([1,2,3])
        il.addextidx('test', [0,1,1])
        self.assertEqual(il.extidx[0], [0,1,1])
        il.updatelist([0,2,2],0)
        self.assertEqual(il.extidx[0], [0,2,2])
        il= Ilist.Izip(['a', 'b', 'c'], [1,2,2], [4,5,5])
        il.updateidx(1,["d",8,2])
        il.append("truc", ["z", 1,10])
        self.assertEqual(il.idxlen, [4,3,4])

    def test_add(self):
        il1 = Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab'], [[0, 2, 0, 2, 0], [10,0,20,20,15]])
        il2 = Ilist.Iext(['_er', '_rt', '_er', '_ry', '_ab'], [[10, 12, 10, 12, 10], [110,10,120,120,115]])
        il3 = il1 + il2
        self.assertEqual(len(il3) , len(il1) + len(il2))
        self.assertEqual(il2.loc([12, 10]), il3.loc([12, 10]))
        self.assertEqual(il1.loc([0, 20]), il3.loc([0, 20]))
        il2=Ilist.Iext(['_er', '_rt', '_er', '_ry', '_ab'], [[10, 2, 10, 12, 10], [110,0,120,120,115]])
        il3 = il1 + il2
        self.assertEqual(len(il3) , len(il1) + len(il2) - 1)
        self.assertEqual(il2.loc([12, 120]), il3.loc([12, 120]))
        self.assertEqual(il1.loc([0, 20]), il3.loc([0, 20]))

    def test_extend(self):
        il1 = Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab'], [[0, 2, 0, 2, 0], [10,0,20,20,15]])
        il2 = Ilist.Iext(['_er', '_rt', '_er', '_ry', '_ab'], [[10, 12, 10, 12, 10], [110,10,120,120,115]])
        il3 = il1 | il2
        self.assertEqual(il3, il1)
        il2.idxname = ['il2 idx1', 'il2 idx2']
        il3 = il1 | il2
        self.assertEqual(il3.lenidx, il1.lenidx + il2.lenidx)
        il=Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab', 'ert'])
        ilx = Ilist.Iext(extidx=[[0,0,0,1,1,1], [0,1,2,3,4,1]])
        il2 = il | ilx
        self.assertEqual(il2.extidx, ilx.extidx)
        self.assertEqual(il2.extval, il .extval)
        il2=Ilist.Iext(['_er', '_rt', '_er', '_ry', '_ab'], [[10, 2, 10, 12, 10], [110,0,120,120,115]])
        il2.addlistidx('truc', ['un', 'deux'], [0,0,1,1,0])
        il2.addextidx('truc2', ['un', 'de', 'un', 'de', 'un'])
        self.assertEqual(il2.loc([12, 120, "deux", "de"]), '_ry')

    def test_merge(self):
        il1 = Ilist.Iedic({'notes'     : [10, 11, 12]}, 
                          {'course'    : ['math', 'english', 'software']})        
        il2 = Ilist.Iedic({'notes'     : [15, 14, 11]},
                          {'course'    : ['physic', 'english', 'software'],
                           'group'     : ['gr1', 'gr1', 'gr2']})
        il3 = Ilist.Iedic({'list'      : [il1, il2]},
                          {'name'      : ['philippe white', 'anne white'],
                           'firstname' : ['philippe', 'anne']})
        self.assertEqual(il3.merge().loc(["physic", "anne", "gr1", "anne white"]), 15)
        il3= Ilist.Iext(extval=[il1, il2])
        self.assertEqual(il3.merge().loc(["english", "gr1"]), 14)
        
    def test_swap(self):
        il = Ilist.Iset([['a', [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]],
                         ['d', [1, 1, 1]], ['e', [2, 2, 0]], ['f', [2, 2, 1]]],
                        [[10,20,30],[100,200,300], [True, False]])
        il1 = copy(il)
        il.swapindex([2,0,1])
        il.swapindex([2,0,1])
        il.swapindex([2,0,1])
        self.assertEqual(il, il1)

    def test_to_numpy(self):
        il = Ilist.Iidic({'result':[10,11,12,13,14,15]}, {'datation':['d0', 'd1', 'd2'],
                          'location':['l0', 'l1', 'l2'], 'property':['p0', 'p1']},
                         idxref=[0,0,2], order=[2,0])
        ilnp, setidx = il.to_numpy()
        '''self.assertEqual(ilnp[setidx[0].index(DatationValue('d1')),setidx[1].index(PropertyValue('p1'))], 
                         ReesultValue(14))
        ilnp, setidx = il.to_numpy(ind='all')
        self.assertEqual(ilnp[setidx[0].index(DatationValue('d1')),setidx[1].index(LocationValue('l1')),
                              setidx[2].index(PropertyValue('p0'))], ReesultValue(11))'''
        self.assertEqual(ilnp[setidx[0].index(DatationValue('d1')),setidx[1].index(PropertyValue('p1'))], 
                         NamedValue(14))
        ilnp, setidx = il.to_numpy(ind='all')
        self.assertEqual(ilnp[setidx[0].index(DatationValue('d1')),setidx[1].index(LocationValue('l1')),
                              setidx[2].index(PropertyValue('p0'))], NamedValue(11))
        #il = Ilist.Iidic({'result':[ReesultValue(0), ReesultValue(1), ReesultValue(2),
        #                            ReesultValue(3), ReesultValue(4), ReesultValue(5)]},
        il = Ilist.Iidic({'result':[0,1,2,3,4,5]},
                         {'datation':[DatationValue(dat3[1][0]), DatationValue(dat3[1][1]),
                                      DatationValue(dat3[1][2])],
                          'location':[LocationValue(loc3[1][0]), LocationValue(loc3[1][1]),
                                      LocationValue(loc3[1][2])],
                          'property':[PropertyValue(prop2[1][0]), PropertyValue(prop2[1][1])]},
                         idxref=[0,0,2], order=[2,0])
        ilnp, setidx = il.to_numpy(func=ESValue.vSimple, string=False)
        self.assertEqual(ilnp[setidx[0].index(DatationValue("2021-05-04T10:05:00+00:00")),
                              setidx[1].index(PropertyValue({"prp": "PM25", "unit": "kg/m3"}))]
                         , 2.0)

    def test_to_xarray(self):
        il=Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab'], [[0, 2, 0, 2, 0], [10,0,20,20,15], [1,2,1,2,1]])
        self.assertTrue(str(il.to_xarray().sel(idx0=2, idx1=20).values), il.loc([2,20,2]))
        self.assertTrue(str(il.to_xarray(axes=il.axesall).sel(idx0=2, idx1=20, idx2=2).values), il.loc([2,20,2]))

    def test_csv(self):
        il=Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab'], [[0, 2, 0, 2, 0], [10,0,20,20,15], [1,2,1,2,1]])
        il.to_csv('ilist.txt', dialect='excel')
        il2 = Ilist.from_csv('ilist.txt', quoting=csv.QUOTE_NONNUMERIC)
        self.assertEqual(il.extidx, il2.extidx)
        self.assertEqual(il.extval, il2.extval)

    def test_list(self):
        il = Ilist([1,2,3,4,5,6])
        self.assertEqual(il[1], 2)
        self.assertEqual(len(il), 6)

    def test_zip(self):
        il = Ilist.Izip([1, 2, 3], [10, 20, 30], [100, 200, 300])
        self.assertEqual(list(il.zip)[1], list(zip([1, 2, 3], [10, 20, 30], [100, 200, 300]))[1])

    def test_example(self):
        test = Ilist.Iext([10, 12, 15], [['Paul', 'Karin', 'John'], [16, 17, 15], ['math', 'math', 'english']],
                          'score', ['name', 'age', 'subject'])
        test.to_xarray(axes=[0,2], fillvalue=-1)
        test.json(json_mode='vi')

        cours = Ilist.from_csv('example cours light.csv', delimiter=';')
        coursfull = cours.full(cours.axesmin, fillvalue='-')
        coursfull.to_csv('example cours light full.txt')
        print('\n', 'taille (bytes) : ', coursfull.to_obj(encode_format='bson').__sizeof__(), '\n')  # 2025, csv : 2749, xlsx : 12245

    def test_to_obj_file(self):
        #il = Ilist.Iidic({'result':[ReesultValue(0), ReesultValue(1), ReesultValue(2),
        #                            ReesultValue(3), ReesultValue(4), ReesultValue(5)]},
        il = Ilist.Iidic({'result':[0,1,2,3,4,5]},
                         {'datation':[DatationValue(dat3[1][0]), DatationValue(dat3[1][1]),
                                      DatationValue(dat3[1][2])],
                          'location':[LocationValue(loc3[1][0]), LocationValue(loc3[1][1]),
                                      LocationValue(loc3[1][2])],
                          'property':[PropertyValue(prop2[1][0]), PropertyValue(prop2[1][1])]},
                         idxref=[0,0,2], order=[2,0])
        for forma in ['json', 'bson', 'cbor']:
        #for forma in ['json', 'cbor']:
            for encoded in [False, True]:
                for codif in [ES.codeb, {}]:
                    il2 = Ilist.from_obj(il.to_obj(encoded=encoded, encode_format=forma, codif=codif))
                    il2.setidx[0] = DatationValue.cast(il2.setidx[0])
                    il2.setidx[1] = LocationValue.cast(il2.setidx[1])
                    il2.setidx[2] = PropertyValue.cast(il2.setidx[2])
                    #il2.extval = ReesultValue.cast(il2.extval)
                    self.assertEqual(il.to_obj(encoded=False), il2.to_obj(encoded=False))
        il3 = Ilist.from_obj(il.to_obj(encoded=False))
        il3.setidx[0] = DatationValue.cast(il3.setidx[0])
        il3.setidx[1] = LocationValue.cast(il3.setidx[1])
        il3.setidx[2] = PropertyValue.cast(il3.setidx[2])
        #il3.extval=ReesultValue.cast(il3.extval)
        self.assertEqual(il.to_obj(encoded=False), il3.to_obj(encoded=False))
        il=Ilist.Iext(['er', 'rt', 'er', 'ry'], [[0, 2, 0, 2], [30, 12, 20, 15]]
                      ).sort(order=[0,1], inplace=False)
        ilf = il.full(axes=[0,1]).sort(order=[0,1], inplace=False)
        self.assertEqual(il, il.from_obj(il.json()).sort(order=[0,1], inplace=False))
        self.assertEqual(ilf, il.from_obj(ilf.json()))
        for forma in ['json', 'bson', 'cbor']:
            il.to_file('test.tst', encode_format=forma)
            ilf.to_file('testf.tst', encode_format=forma)
            self.assertEqual(il, il.from_file('test.tst').sort(order=[0,1], inplace=False))
            self.assertEqual(ilf, il.from_file('testf.tst'))
    
    def test_derived_to_coupled(self):
        il=Ilist.Iext([1,2,3,4,5,6], [['a', 'b', 'b', 'c', 'c', 'a'], 
         [20,  10,  10,  10,  10,  20], [200, 200, 300, 200, 300, 300]] )
        il.derived_to_coupled(1,0)
        self.assertTrue(il.complete)
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
