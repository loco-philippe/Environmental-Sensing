# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: a179227
"""
import unittest
from ilist import Ilist
from copy import copy
import csv, os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from EStestunitaire import obs_1, dat3, loc3, prop2, _res
#from ESObservation import Observation
from ESValue import ResultValue, DatationValue, LocationValue, PropertyValue, ESValue
from datetime import datetime

#import ..\ESValue

f = ['er', 'rt', 'er', 'ry']
l = [[0, 2, 0, 2], [30, 12, 20, 15]]
il=Ilist.Iext(f,l)
'''ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), order='px')
lres = ob.setResult.vList(ResultValue.getValue)
lind = il._transpose(ob.setResult.vListIndex)
iobs = Ilist.Iext(lres,lind)'''
'''reslist = [ResultValue(21, 'test'), ResultValue(22, 'test2'),
           ResultValue(23, 'test3'), ResultValue(24, 'test4')]
resind = [[0,2,3,1], [2,1,3,0], [0,1,2,3]]
setres =Ilist.Iext(reslist, resind) 
dicttest = dict((obs_1, dat3, loc3, prop2, _res(6)))'''


class Test_ilist(unittest.TestCase):

    il = Ilist.Idict({}, {'id1':[0,1,2], 'id2':[3,4,5]})
    
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
        il = Ilist.Idict({'resultvalue' : ['a', 'b', 'c', 'd', 'e', 'f']}, 
                         {'datationvalue' : [10,20,30],
                          'locationvalue' : [100,200,300],
                          'propertyvalue' : [True, False]}, 
                         idxref=[0,0,2], order = [0,2])
        il2 =Ilist.Idict({'resultvalue' :[['a', [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]], ['d', [1, 1, 1]], 
                                         ['e', [2, 2, 0]], ['f', [2, 2, 1]]]},
                         {'datationvalue' : [10,20,30],
                          'locationvalue' : [100,200,300],
                          'propertyvalue' : [True, False]})
        self.assertEqual(il.iidx[1], [0, 0, 1, 1, 2, 2])
        self.assertEqual(il, il2)

    def test_init_set(self) :
        il = Ilist.Iset(['a', 'b', 'c', 'd', 'e', 'f'], [[10,20,30],[100,200,300], [True, False]], 
                         idxref=[0,0,2], order = [0,2])
        il2 = Ilist.Iset([['a', [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]], ['d', [1, 1, 1]], 
                          ['e', [2, 2, 0]], ['f', [2, 2, 1]]], [[10,20,30],[100,200,300], [True, False]])
        self.assertEqual(il.iidx[1], [0, 0, 1, 1, 2, 2])
        self.assertEqual(il, il2)
        
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
        self.assertEqual( il.dimension, 4)
        self.assertEqual( il.lencomplete, 36)    
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
        
    def test_full(self) :
        f = ['er', 'rt', 'er', 'ry']
        l = [[0, 2, 0, 2], [30, 12, 20, 15], [2, 0, 2, 0], [2, 2, 0, 0], ['info', 'info', 'info', 'info'],[12, 20, 15, 30]]
        il=Ilist.Iext(f,l)
        ilc=il.full()
        #ild=il.full(minind=False)
        ild=il.full(axes=list(range(il.lenidx)))
        self.assertEqual( len(ild), 128)
        self.assertEqual( ild.idxref,  [0, 1, 2, 3, 4, 5])
        self.assertEqual( ilc.extidx[1], [30, 12, 20, 15, 12, 12, 20, 30, 15, 15, 12, 20, 20, 30, 30, 15])
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
        
    def test_swap(self):
        il = Ilist.Iset([['a', [0, 0, 0]], ['b', [0, 0, 1]], ['c', [1, 1, 0]],
                         ['d', [1, 1, 1]], ['e', [2, 2, 0]], ['f', [2, 2, 1]]],
                        [[10,20,30],[100,200,300], [True, False]])
        il1 = copy(il)
        il.swapindex([2,0,1])
        il.swapindex([2,0,1])
        il.swapindex([2,0,1])
        self.assertEqual(il, il1)

    def test_extend(self):
        il2=Ilist.Iext(['_er', '_rt', '_er', '_ry', '_ab'], [[10, 2, 10, 12, 10], [110,0,120,120,115]])
        il2.addlistidx('truc', ['un', 'deux'], [0,0,1,1,0])
        il2.addextidx('truc2', ['un', 'de', 'un', 'de', 'un'])
        self.assertEqual(il2.loc([12, 120, "deux", "de"]), '_ry')
        
    def test_to_numpy(self):      
        il = Ilist.Idict({'result':[ResultValue(0), ResultValue(1), ResultValue(2), 
                                    ResultValue(3), ResultValue(4), ResultValue(5)]}, 
                         {'datation':[DatationValue(dat3[1][0]), DatationValue(dat3[1][1]), 
                                      DatationValue(dat3[1][2])],
                          'location':[LocationValue(loc3[1][0]), LocationValue(loc3[1][1]), 
                                      LocationValue(loc3[1][2])],
                          'property':[PropertyValue(prop2[1][0]), PropertyValue(prop2[1][1])]},
                         idxref=[0,0,2], order=[2,0])
        self.assertEqual(il.to_numpy(func=ResultValue.vSimple, string=True)[1,1], '2.0')
        self.assertEqual(il.to_numpy(func=ResultValue.vSimple, string=False)[1,1], 2.0)
        self.assertEqual(il.to_numpy(func=ESValue.vName, genName='-')[1,1], '-')
        self.assertEqual(il.to_numpy(func=ResultValue.vSimple, string=True, ind='all')[1,1,0], '5.0')
        
    def test_to_xarray(self):
        il=Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab'], [[0, 2, 0, 2, 0], [10,0,20,20,15], [1,2,1,2,1]])
        self.assertTrue(str(il.to_xarray().sel(idx0=2, idx1=20).values), il.loc([2,20,2]))
        self.assertTrue(str(il.to_xarray(axes=il.axesall).sel(idx0=2, idx1=20, idx2=2).values), il.loc([2,20,2]))

    def test_csv(self):
        il=Ilist.Iext(['er', 'rt', 'er', 'ry', 'ab'], [[0, 2, 0, 2, 0], [10,0,20,20,15], [1,2,1,2,1]])
        il.to_csv('ilist.txt', dialect='excel')
        il2 = Ilist.Icsv('ilist.txt', quoting=csv.QUOTE_NONNUMERIC)
        self.assertEqual(il, il2)

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
        
if __name__ == '__main__':
    unittest.main(verbosity=2)





