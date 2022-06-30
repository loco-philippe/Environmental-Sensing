# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: Philippe@loco-labs.io

The `ES.test_iindex` module contains the unit tests (class unittest) for the
`Iindex` class.
"""
import unittest
from iindex import Iindex, util
from ilist import Ilist
from copy import copy
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from test_observation import dat3, loc3, prop2, _res
from ESObservation import Observation
from ESValue import NamedValue, DatationValue, LocationValue, PropertyValue, ESValue #, ReesultValue
import datetime
from ESconstante import ES
from itertools import product
from timeslot import TimeSlot


'''f = ['er', 'rt', 'er', 'ry']
l = [30, 12, 20, 15]
il=Ilist.Iext(f,l)'''

class Test_iindex(unittest.TestCase):

    def test_init(self) :
        idx = Iindex(['er', 2, [1,2]], 'test', [0,1,2,1])
        idx2 = Iindex.Iext(['er', 2, [1,2], 2], 'test', fast=False)
        idx3 = Iindex.Idic({'test': ['er', 2, [1,2], 2]}, fast=False)
        idx4 = Iindex.Idic({'test': ['er', 2, [1,2], 2]}, fullcodec=True)
        idx5 = Iindex.Iext(['er', 2, [1,2], 2], 'test', fullcodec=True)
        self.assertTrue(Iindex(idx) == Iindex.Iext(idx) == Iindex.Idic(idx) == idx)
        self.assertTrue(idx.name == 'test' and idx.codec == ['er', 2, [1,2]] and idx.keys == [0,1,2,1])
        self.assertTrue(idx == idx2 == idx3)
        self.assertTrue(idx.values == idx4.values == idx4.codec == ['er', 2, [1,2], 2] 
                        == idx5.values == idx5.codec and len(idx) == 4)
        idx = Iindex() 
        idx2 = Iindex.Iext()
        idx3 = Iindex.Idic()
        self.assertTrue(idx == idx2 == idx3 == Iindex(idx))
        self.assertTrue(idx.name == 'default index' and idx.codec == [] and idx.keys == [])
        self.assertTrue(idx.values == [])
        idx = Iindex(lendefault=3) 
        self.assertTrue(idx.name == 'default index' and idx.codec == [0,1,2] and idx.keys == [0,1,2])
        self.assertTrue(idx.values == [0,1,2])
        idx = Iindex(['er', 'rt', 'ty'], 'datation', [0,1,2,2])
        idx2 = Iindex.Iext(['er', 'rt', 'ty', 'ty'], 'datation', fast=True)
        idx3 = Iindex.Idic({'datation': ['er', 'rt', 'ty', 'ty']}, fast=True)
        self.assertTrue(idx == idx2 == idx3)
        self.assertTrue(isinstance(idx.codec[0], DatationValue))
        self.assertTrue(idx.values[3] == DatationValue('ty'))
        idx = Iindex(['er', 'rt', Ilist()], 'result', [0,1,2,2])
        idx2 = Iindex.Iext(['er', 'rt', Ilist(), Ilist()], 'result', fast=False)
        idx3 = Iindex.Idic({'result': ['er', 'rt', Ilist(), Ilist()]}, fast=False)
        self.assertTrue(idx == idx2 == idx3)
        self.assertTrue(isinstance(idx.codec[0], NamedValue) and isinstance(idx.codec[2], Ilist))
        self.assertTrue(idx.values[3] == Ilist())
        
    def test_infos(self) :
        idx = Iindex.Iext(['er', 2, [1,2]], fast=False)
        self.assertTrue(idx.infos == {'lencodec': 3, 'typeindex': 'complete',
         'rate': 0.0, 'disttomin': 2, 'disttomax': 0})
        idx2 = Iindex.Iext(['er', Ilist(), Ilist()], 'result', fast=False)
        self.assertTrue(idx2.infos == {'lencodec': 2, 'typeindex': 'mixte',
         'rate': 0.5, 'disttomin': 1, 'disttomax': 1})
        idx2 = Iindex()
        self.assertTrue(idx2.infos == {'lencodec': 0, 'typeindex': 'null',
         'rate': 0.0, 'disttomin': 0, 'disttomax': 0})
        
    def test_append(self) :
        idx = Iindex.Iext(['er', 2, [1,2]], fast=False)
        self.assertTrue(idx.append(8)==3)
        self.assertTrue(idx.append(8)==3)
        self.assertTrue(idx.append(8, unique=False)==4)
        
    def test_loc_keyval(self):
        idx = Iindex.Iext(['er', 2, [1,2]], fast=False)
        self.assertTrue(idx.keytoval(2) == [1,2])
        self.assertTrue(idx.valtokey([1,2]) == 2)
        self.assertTrue(idx.isvalue([1,2]), 2)

    def test_setvalue_setname(self):
        idx = Iindex.Iext(['er', 2, [1,2]], fast=False)
        idx[1] = 'er'
        self.assertTrue(idx.values == ['er', 'er', [1,2]])
        idx.setcodecvalue('er', 'ez')
        self.assertTrue(idx.values == ['ez', 'ez', [1,2]])        
        idx[1] = 3
        self.assertTrue(idx.values == ['ez', 3, [1,2]])
        idx.setvalue(0, 'ez', dtype='datvalue', fast=False)
        self.assertTrue(idx.values == [DatationValue('ez'), 3, [1,2]])
        idx.setname('truc')
        self.assertEqual(idx.name, 'truc')

    def test_record(self):
        ia = Iindex.Iext(['anne', 'paul', 'lea', 'andre', 'paul', 'lea'])
        self.assertEqual([ia[i] for i in ia.recordfromvalue('paul')], ['paul', 'paul'])

    def test_reset_reorder_sort(self):
        idx = Iindex.Iext(['er', 2, 'er', [1,2]], fast=False)
        cod = copy(idx.codec)
        idx.codec.append('ez')
        #idx.resetkeys()
        idx.reorder(fast=False)
        self.assertEqual(cod, idx.codec)
        order=[1,3,0,2]
        idx.reorder(order, fast=False)
        self.assertEqual(idx.values, [2, [1,2], 'er', 'er'])
        idx.sort(fast=False)
        self.assertEqual(idx.values, [2, [1,2], 'er', 'er'])        
        idxs = idx.sort(inplace=False, reverse=True, fast=False)
        self.assertEqual(idxs.values, ['er', 'er', [1, 2], 2])
        idx = Iindex.Iext([1,3,3,2,5,3,4]).sort(inplace=False)
        self.assertEqual(idx.values, [1, 2, 3, 3, 3, 4, 5])
        self.assertEqual(idx.codec,  [1, 2, 3, 4, 5])
        
    def test_derived_coupled(self):
        der = Iindex.Iext([1,1,1,2])
        ref = Iindex.Iext([1,1,3,4])
        self.assertTrue(der.isderived(ref) and not der.iscoupled(ref))
        der.tocoupled(ref)
        self.assertTrue(not der.isderived(ref) and der.iscoupled(ref))
        #der.resetkeys()
        der.reorder()
        self.assertTrue(der.isderived(ref) and not der.iscoupled(ref))
        ia = Iindex.Iext(['anne', 'paul', 'anne', 'lea', 'anne'])
        ib = Iindex.Iext([25,25,12,12,25])
        self.assertTrue(not ia.isderived(ib) and not ia.iscoupled(ib))
        self.assertTrue(not ib.isderived(ia) and not ib.iscoupled(ia))
        ia.coupling(ib)
        self.assertTrue(ib.isderived(ia))
        ia.coupling(ib, derived=False)
        self.assertTrue(ib.iscoupled(ia))
        
    def test_coupling_infos(self):
        ia = Iindex.Iext()
        ib = Iindex.Iext([25,25,12,12,25])
        self.assertEqual(ia.couplinginfos(ib), {'lencoupling': 0, 'rate': 0, 
                    'disttomin': 0, 'disttomax': 0, 'distmin': 0, 'distmax': 0,
                    'diff': 0, 'typecoupl': 'null'})
        ia = Iindex.Iext(['anne', 'paul', 'anne', 'lea', 'anne'])
        self.assertEqual(ia.couplinginfos(ib), {'lencoupling': 4, 'rate': 0.3333333333333333,
                    'disttomin': 1, 'disttomax': 2, 'distmin': 3, 'distmax': 6, 
                    'diff': 1, 'typecoupl': 'link'})
        self.assertTrue(ia.islinked(ib))
        ia = Iindex.Iext(['anne', 'lea', 'anne', 'lea', 'anne'])
        self.assertEqual(ia.couplinginfos(ib), {'lencoupling': 4, 'rate': 1.0,
                    'disttomin': 2, 'disttomax': 0, 'distmin': 2, 'distmax': 4,
                    'diff': 0, 'typecoupl': 'crossed'})
        self.assertTrue(ia.iscrossed(ib))

    def test_vlist(self):
        testidx = [Iindex(), Iindex.Iext(['er', 2, 'er', [1,2]], fast=False)]
        residx  = [[], ['er', '2', 'er', '[1, 2]']]
        for idx, residx in zip(testidx, residx):
            self.assertEqual(idx.vlist(str), residx)

    def test_numpy(self):
        idx = Iindex.Iext(['er', 2, 'er', [1,2]], fast=False)
        self.assertEqual(len(idx.to_numpy(func=str)), len(idx)) 

    def test_coupled_extendvalues(self):
        ia = Iindex.Iext(['anne', 'paul', 'lea', 'andre', 'paul', 'lea'])
        ib = Iindex.Iext([25,25,12,12])   
        self.assertTrue(ib.isderived(ia))
        #ib.extendvalues(ia)
        ib.tocoupled(ia)
        self.assertEqual(ib.values, [25, 25, 12, 12, 25, 12])
        self.assertTrue(ib.keys == ia.keys and ib.iscoupled(ia))
        #ib.extendvalues(ia, coupling=False)
        ib.tocoupled(ia, coupling=False)
        self.assertEqual(ib.values, [25, 25, 12, 12, 25, 12])
        self.assertTrue(ib.codec, [25, 12] and ib.isderived(ia))
        
    def test_crossed(self):
        ia = Iindex.Iext(['anne', 'paul', 'anne', 'lea'])
        ib = Iindex.Iext([25,25,12,12])
        Iindex.tocrossed([ia,ib])
        self.assertTrue(ib.iscrossed(ia))
        ia = Iindex.Iext(['anne', 'paul', 'anne', 'lea'])
        ib = Iindex.Iext([25,25,12,12])
        ic = Iindex.Iext(['White', 'Grey', 'White', 'Grey'])
        Iindex.tocrossed([ia,ib, ic])
        self.assertTrue(ib.iscrossed(ia) and ib.iscrossed(ic))

    def test_tocodec(self):
        v = [10,10,10,10,30,10,20,20,20]        
        k = [1, 1, 1, 2, 3, 2, 0, 0, 0 ]
        self.assertEqual(util.tocodec(v, k, True), util.tocodec(v, k, False))
        self.assertEqual(sorted(util.tocodec(v, fast=True)), 
                         sorted(util.tocodec(v, fast=False)))

    def test_to_std(self):   
        idx = Iindex.Iext(['d1', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
        self.assertEqual(len(idx.tostdcodec().codec), len(idx))
        self.assertEqual(len(idx.tostdcodec(full=False).codec), len(idx.codec))
        self.assertTrue(idx == idx.tostdcodec(full=False) == idx.tostdcodec())
        idx = Iindex.Iext(['d1', 'd1', 'd1', 'd1', 'd1', 'd1', 'd1'])
        self.assertEqual(len(idx.tostdcodec().codec), len(idx))
        self.assertEqual(len(idx.tostdcodec(full=False).codec), len(idx.codec))
        self.assertTrue(idx == idx.tostdcodec(full=False) == idx.tostdcodec())
        
    def test_extendcodec(self):
        papy = Iindex.Iext(['d1', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
        parent = Iindex.Iext(['j', 'j', 'f', 'f', 'm', 's', 's'])
        idx = Iindex.Iext(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        parent2 = parent.toextendcodec2(papy, inplace=False)
        idx2 = idx.toextendcodec2(parent, inplace=False)
        self.assertEqual(idx.values, idx2.values)
        self.assertEqual(len(parent2.codec), len(papy.codec))
        self.assertEqual(len(idx2.codec), len(parent.codec))
        self.assertTrue(idx2.isderived(parent2) and parent2.iscoupled(papy))
        idxcalc = Iindex.from_parent(idx2.codec, parent=parent)
        self.assertTrue(idxcalc.values == idx2.values == idx.values)
        idx=Iindex(codec=['s', 'n', 's', 'd', 's', 'd'], keys=[0, 4, 2, 1, 5, 3, 3])
        values = idx.values
        parent=Iindex(codec=[6, 9, 8, 11, 7, 9], keys=[0, 4, 2, 1, 5, 3, 3])
        idx.toextendcodec2(parent)
        idxcalc = Iindex.from_parent(idx.codec, parent=parent)
        self.assertTrue(idxcalc.values == idx.values == values)

    def test_derkeys(self):
        parent = Iindex.Iext(['j', 'j', 'f', 'f', 'm', 's', 's'])
        fils = Iindex.Iext(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        idx = Iindex(fils.codec, keys=Iindex.keysfromderkeys(parent.keys, fils.derkeys(parent))) 
        self.assertEqual(idx, fils)
        grandpere=Iindex.Iext([0,     0,   2,   3,   4,   4,   6,   7,   8,   9,   9,  11,  12 ])
        pere = Iindex.Iext(['j', 'j', 'f', 'a', 'm', 'm', 's', 's', 's', 'n', 'd', 'd', 'd' ])
        fils = Iindex.Iext(['t1','t1','t1','t2','t2','t2','t3','t3','t3','t4','t4','t4','t4'])
        petitfils =Iindex.Iext(['s11','s1','s1','s1','s1','s11','s2','s2','s2','s1','s2','s2','s2'])
        fils.coupling(petitfils)
        pere.coupling(fils)
        grandpere.coupling(pere)
        self.assertTrue(petitfils.isderived(fils)==fils.isderived(pere)==pere.isderived(grandpere))
        idx = Iindex(petitfils.codec, keys=Iindex.keysfromderkeys(fils.keys, petitfils.derkeys(fils))) 
        self.assertEqual(idx, petitfils)
        idx = Iindex(fils.codec, keys=Iindex.keysfromderkeys(pere.keys, fils.derkeys(pere))) 
        self.assertEqual(idx, fils)
        idx = Iindex(pere.codec, keys=Iindex.keysfromderkeys(grandpere.keys, pere.derkeys(grandpere))) 
        self.assertEqual(idx, pere)


    def test_json(self):
        parent = Iindex.Iext(['j', 'j', 'f', 'f', 'm', 's', 's'])
        fils = Iindex.Iext(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        js=fils.to_obj(keys=fils.derkeys(parent), parent=1)
        idx = Iindex.from_obj(js, extkeys=parent.keys)[1]
        self.assertEqual(idx, fils)
        encoded    = [True, False]
        format     = ['json', 'cbor']
        test = list(product(encoded, format))
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1]}
            idx2=Iindex.from_obj(idx.to_obj(keys=True, **option))[1]
            self.assertEqual(idx.values, idx2.values)
            idx2=Iindex.from_obj(idx.tostdcodec().to_obj(**option))[1] # full format
            self.assertEqual(idx.values, idx2.values)
            idx2=Iindex.from_obj(idx.to_obj(keys=fils.derkeys(parent), parent=1, **option), 
                                 extkeys=parent.keys)[1] # default format
            self.assertEqual(idx.values, idx2.values)

    def test_castobj(self):
        lis = [['{"namvalue":{"val":21}}',   'ESValue',         NamedValue],
               [{"val":21},                  'ESValue',         NamedValue],
               [{"val":21},                  None,              dict],
               ['{"namvalue":{"val":21}}',   None,              str],
               ['{"locvalue":{"val":21}}',   'LocationValue',   LocationValue],
               ['{"observation":{"val":21}}','Observation',     Observation],
               [Observation(),               'Observation',     Observation],
               [Observation(),               None,              Observation],
               [datetime.datetime(2020,1,1), 'DatationValue',   DatationValue],
               [datetime.datetime(2020,1,1), 'TimeSlot',        TimeSlot],
               [datetime.datetime(2020,1,1), None,              datetime.datetime]]
        for t in lis:
            self.assertTrue(isinstance(util.castobj([t[0]], t[1])[0], t[2]))
        idx = Iindex.Idic({'datation': ['er', 'rt', 'ty', 'ty']}, fast=True)
        self.assertTrue(isinstance(idx[0], DatationValue))
        idx = Iindex.Idic({'ESdatation': ['er', 'rt', 'ty', 'ty']}, fast=True)
        self.assertTrue(isinstance(idx[0], NamedValue))
        idx = Iindex.Idic({'dates': ['er', 'rt', 'ty', 'ty']}, fast=True)
        self.assertTrue(isinstance(idx[0], str))

    def test_iadd(self):            
        idx = Iindex.Iext(['er', 2, 'er', [1,2]], fast=False)
        idx2 = idx + idx
        self.assertEqual(idx2.codec, idx.codec)
        self.assertEqual(len(idx2), 2 * len(idx))
        self.assertEqual(len(idx2), 2 * len(idx))
        idx += idx
        self.assertEqual(idx2, idx)
        
if __name__ == '__main__':  unittest.main(verbosity=2)


'''def test_json(self):
    testidx = [Iindex(), Iindex.Iext(['er', 2, 'er', [1,2]])]
    encoded  = [True, False]
    format   = ['json', 'bson', 'cbor']
    link     = [-1, 0]
    complete = [True, False]
    values   = [True, False]
    test = list(product(encoded, format, link, complete, values))
    for idx in testidx:
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1], 'link':ts[2],
                      'complete':ts[3], 'values':ts[4]}
            idx2=Iindex.from_obj(idx.to_obj(**option), indexset=[idx])
            if option['complete']: idx2.keys=idx.keys
            self.assertEqual(idx, idx2)     

    def test_json(self):
        parent = Iindex.Iext(['j', 'j', 'f', 'f', 'm', 's', 's'])
        idx = Iindex.from_parent(['t1', 't1', 't2', 't3'], parent=parent)        
        fullcodec  = [True, False]
        encoded    = [True, False]
        format     = ['json', 'cbor']
        test = list(product(encoded, format, fullcodec))
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1], 'fullcodec': ts[2]}
            #standalone
            idx2=Iindex.from_obj(idx.to_obj(keys=True, **option)) # default format
            self.assertEqual(idx.values, idx2.values)
            idx2=Iindex.from_obj(idx.to_obj(**option)) # full format
            self.assertEqual(idx.values, idx2.values)
            #Ilist
            idx2=Iindex.from_extobj(idx.to_extobj(keys=True, **option), 7)[1] # default format
            self.assertEqual(idx.values, idx2.values)
            if not ts[2]:
                idx2=Iindex.from_extobj(idx.to_extobj(**option), 7, extkeys=parent.keys)[1] # default format
                self.assertEqual(idx.values, idx2.values)
                idx2=Iindex.from_extobj(idx.to_extobj(parent=2, **option), 7, extkeys=parent.keys)[1] # default format
                self.assertEqual(idx.values, idx2.values)
                '''