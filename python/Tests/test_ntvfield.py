# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 22:44:05 2022

@author: Philippe@loco-labs.io

The `observation.test_iindex` module contains the unit tests (class unittest) for the
`Ntvfield` class.
"""
import unittest
from copy import copy
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')

from itertools import product
from observation import Ntvdataset, Ntvfield, ES, util
from json_ntv import Ntv, NtvSingle, NtvList
from observation.fields import Nfield, Sfield
from observation.datasets import Ndataset, Sdataset

type_test = 'ntv'
type_test = 'simple'

if type_test == 'ntv':
    Field = Nfield
    Dataset = Ndataset
else:
    Field = Sfield
    Dataset = Sdataset
arr12 = 'ar[1,2]' if Field == Sfield else [1,2]

def internal(val):
    if Field == Sfield:
        return val
    return NtvSingle(val)

class Test_Field(unittest.TestCase):

    def test_init_unitaire(self):
        idx = Field()
        idx2 = Field.ntv()
        #idx3 = Field.ext()
        #self.assertTrue(idx == idx2 == idx3 == Field(idx))
        self.assertTrue(idx == idx2 == Field(idx))
        self.assertTrue(
            idx.name == ES.defaultindex and idx.codec == [] and idx.keys == [])
        self.assertTrue(idx.values == [])
        idx = Field(lendefault=3)
        self.assertTrue(idx.name == ES.defaultindex and 
                        idx.cod == [0] and idx.keys == [0, 0, 0])
        self.assertTrue(idx.val == [0, 0, 0])
        self.assertTrue(Field(1) == Field([1]))
        self.assertTrue(Field('trux') == Field(['trux']))

    def test_init(self):
        if Field != Sfield:
            idx = Field(codec=[Ntv.obj('er'), Ntv.obj(2), Ntv.obj(arr12)], name='test', keys=[0, 1, 2, 1])
            idx2 = Field.from_ntv({'test': ['er', 2, arr12, 2]})
            idx3 = Field(['er', 2, [1, 2], 2], 'test', reindex=True)
            idx4 = Field(['er', 2, [1, 2], 2], 'test')
            self.assertTrue(Field(idx) == idx)
            self.assertTrue(idx.name == 'test' and 
                            idx.cod == ['er', 2, arr12] and 
                            idx.keys == [0, 1, 2, 1])
            self.assertTrue(idx == idx2 == idx3 == idx4 and len(idx) == 4)
            self.assertTrue(idx.val == idx4.val == idx4.cod == ['er', 2, [1, 2], 2])
        else:
            idx = Field(codec=['er', 2, arr12], name='test', keys=[0, 1, 2, 1])
            idx2 = Field.from_ntv({'test': ['er', 2, arr12, 2]})
            self.assertTrue(Field(idx) == idx)
            self.assertTrue(idx == idx2)            
        idx = Field(['er', 'rt', Dataset()], 'result', [0, 1, 2, 2])
        idx2 = Field(['er', 'rt', Dataset(), Dataset()], 'result')
        self.assertTrue(idx == idx2)
        if Field == Sfield:
            self.assertTrue(idx[3] == Dataset())
        else:
            self.assertTrue(idx[3].to_obj(format='obj', dicobj={'tab':'NdatasetConnec'}) == Dataset())            
        self.assertTrue(Field.ntv([1, 2, 3]) == Field([1, 2, 3]))
        self.assertTrue(Field(codec=[True], lendefault=3).val == [True, True, True])
        idx = Field(['er', 'rt', 'ty'], 'datation', [0, 1, 2, 2])
        idx2 = Field(['er', 'rt', 'ty', 'ty'], 'datation')
        idx3 = Field.ntv({'datation': ['er', 'rt', 'ty', 'ty']})
        self.assertTrue(idx == idx2 == idx3)
        self.assertTrue(idx.val[3] == 'ty')

    def test_obj(self):
        listval = [{'name': ['value']}, 
                   'value', 
                   ['value'], 
                   ['value', 'value2']]
        if Field != Sfield:
            listval += [
                   {'b': ['value', [[1], [2]], [[3], [4]]]},
                   {'b': ['value', [[[0.0, 1.0], [1.0, 2.0], [1.0, 1.0], [0.0, 1.0]]],
                          [[[0.0, 2.0], [2.0, 2.0], [1.0, 1.0], [0.0, 2.0]]]]}
                   ]
        for val in listval:
            self.assertTrue(Field.ntv(val).val[0] == 'value')
            self.assertTrue(Field.ntv(Field.ntv(val).to_ntv()) == Field.ntv(val))
        val = {'namvalue': 'value'}
        val2 = {'namvalue': ['value']}
        self.assertTrue(Field.ntv(val).name == 'namvalue')
        self.assertTrue(Field.ntv(val2).name == 'namvalue')
        self.assertTrue(Field.ntv(val2).val[0] == 'value')
        self.assertTrue(Field.ntv(val).val[0] == 'value')
        self.assertTrue(Field.ntv(val).to_ntv().to_obj() == val)
        self.assertTrue(Field.ntv(val2).to_ntv().to_obj() == val)
        val  = {'datation': ['name']}
        val2 = {'datation': 'name'}
        self.assertTrue(Field.ntv(val).name == 'datation')
        self.assertTrue(Field.ntv(val).val[0] == 'name')
        self.assertTrue(Field.ntv(val).to_ntv().to_obj() == val2)

    def test_infos(self):
        idx = Field.ntv(['er', 2, arr12])
        self.assertTrue(idx.infos == {'lencodec': 3, 'mincodec': 3, 'maxcodec': 3,
                                      'typecodec': 'complete', 'ratecodec': 0.0})
        if Field != Sfield:
            idx2 = Field.ntv({'result': ['er', Dataset(), Dataset()]} )
            self.assertTrue(idx2.infos == {'lencodec': 2, 'mincodec': 2, 'maxcodec': 3,
                                           'typecodec': 'default', 'ratecodec': 1.0})
        idx2 = Field()
        self.assertTrue(idx2.infos == {'lencodec': 0, 'mincodec': 0, 'maxcodec': 0,
                                       'typecodec': 'null', 'ratecodec': 0.0})

    def test_append(self):
        idx = Field.ntv(['er', 2, arr12])
        self.assertTrue(idx.append(8) == 3)
        self.assertTrue(idx.append(8) == 3)
        self.assertTrue(idx.append(8, unique=False) == 4)
        self.assertTrue(idx[4] == internal(8))

    def test_loc_keyval(self):
        idx = Field.ntv(['er', 2, arr12])
        self.assertTrue(idx.keytoval(idx.valtokey(arr12)) == arr12)
        self.assertTrue(idx.isvalue(arr12))
        if Field != Sfield:
            idx = Field.ntv( {'location::point': 
                           [{'paris': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]]})
            self.assertTrue(idx.keytoval(
                idx.valtokey({':point':[4.83, 45.76]})) == {':point':[4.83, 45.76]})
            self.assertTrue(idx.loc({':point':[4.83, 45.76]}) == [1])
        idx = Field.ntv([1, 3, 3, 2, 5, 3, 4])
        self.assertTrue(idx.loc(3) == [1, 2, 5])

    def test_setvalue_setname(self):
        idx = Field.ntv(['er', 2, arr12])
        idx[1] = internal('er')
        #idx[1] = Ntv.obj('er')
        self.assertTrue(idx.val == ['er', 'er', arr12])
        idx.setcodecvalue('er', 'ez')
        self.assertTrue(idx.val == ['ez', 'ez', arr12])
        idx[1] = internal(3)
        self.assertTrue(idx.val == ['ez', 3, arr12])
        if Field != Sfield:
            idx.setvalue(0, {':date': '2001-02-03'})
            self.assertTrue(idx.val == [{':date': '2001-02-03'}, 3, arr12])
            self.assertTrue(idx.values[0] == Ntv.obj({':date': '2001-02-03'}))
            idx.setlistvalue([3, [3, 4], 'ee'])
            self.assertTrue(idx.val == [3, [3, 4], 'ee'])
        idx.setname('truc')
        self.assertEqual(idx.name, 'truc')

    def test_record(self):
        ia = Field.ntv(['anne', 'paul', 'lea', 'andre', 'paul', 'lea'])
        if Field != Sfield:
            self.assertEqual([ia[i].to_obj()
                         for i in ia.recordfromvalue('paul')], ['paul', 'paul'])
        else:
            self.assertEqual([ia[i] for i in ia.recordfromvalue('paul')], ['paul', 'paul'])
            
    def test_reset_reorder_sort(self):
        idx = Field.ntv(['er', 2, 'er', arr12])
        cod = copy(idx.codec)
        idx.codec.append(Ntv.obj('ez'))
        # idx.resetkeys()
        idx.reorder()
        self.assertEqual(cod, idx.codec)
        order = [1, 3, 0, 2]
        idx.reorder(order)
        self.assertEqual(idx.val, [2, arr12, 'er', 'er'])
        # idx.sort()
        if Field != Sfield:
            self.assertEqual(idx.sort().val, ['er', 'er', 2, arr12])
        else:
            self.assertEqual(idx.sort().val, [2, arr12, 'er', 'er'])
        idxs = idx.sort(inplace=False, reverse=True)
        if Field != Sfield:
            self.assertEqual(idxs.val, [arr12, 2, 'er', 'er'])
        else:
            self.assertEqual(idxs.val, ['er', 'er', arr12, 2])
        idx = Field.ntv([1, 3, 3, 2, 5, 3, 4]).sort(inplace=False)
        self.assertEqual(idx.val, [1, 2, 3, 3, 3, 4, 5])
        self.assertEqual(idx.cod,  [1, 2, 3, 4, 5])

    def test_derived_coupled(self):
        der = Field.ntv([1, 1, 1, 2])
        ref = Field.ntv([1, 1, 3, 4])
        self.assertTrue(der.isderived(ref) and not der.iscoupled(ref))
        der.tocoupled(ref)
        self.assertTrue(not der.isderived(ref) and der.iscoupled(ref))
        # der.resetkeys()
        der.reorder()
        self.assertTrue(der.isderived(ref) and not der.iscoupled(ref))
        ia = Field.ntv(['anne', 'paul', 'anne', 'lea', 'anne'])
        ib = Field.ntv([25, 25, 12, 12, 25])
        self.assertTrue(not ia.isderived(ib) and not ia.iscoupled(ib))
        self.assertTrue(not ib.isderived(ia) and not ib.iscoupled(ia))
        ia.coupling(ib)
        self.assertTrue(ib.isderived(ia))
        ia.coupling(ib, derived=False)
        self.assertTrue(ib.iscoupled(ia))

    def test_coupling_infos(self):
        ia = Field()
        ib = Field.ntv([25, 25, 12, 12, 25])
        self.assertEqual(ia.couplinginfos(ib),
                         {'dist': 0, 'rateder': 0, 'distance': 0, 'ratecpl': 0,
                          'disttomin': 0, 'disttomax': 0, 'distmin': 0, 'distmax': 0,
                          'diff': 0, 'typecoupl': 'null'})
        ia = Field.ntv(['anne', 'paul', 'anne', 'lea', 'anne'])
        self.assertEqual(ia.couplinginfos(ib),
                         {'dist': 4, 'rateder': 0.3333333333333333, 'distance': 2,
                          'disttomin': 1, 'disttomax': 2, 'distmin': 3, 'distmax': 6,
                          'ratecpl': 0.5, 'diff': 1, 'typecoupl': 'link'})
        self.assertTrue(ia.islinked(ib))
        ia = Field.ntv(['anne', 'lea', 'anne', 'lea', 'anne'])
        self.assertEqual(ia.couplinginfos(ib),
                         {'dist': 4, 'rateder': 1.0, 'distance': 2, 'ratecpl': 1.0,
                          'disttomin': 2, 'disttomax': 0, 'distmin': 2, 'distmax': 4,
                          'diff': 0, 'typecoupl': 'crossed'})
        self.assertTrue(ia.iscrossed(ib))

    def test_vlist(self):
        testidx = [Field(), Field.ntv(['er', 2, 'er', arr12])]
        residx = [[], ['er', '2', 'er', str(arr12)]]
        for idx, res in zip(testidx, residx):
            self.assertEqual(idx.vlist(str), res)
        idx = Nfield.ntv({'datation::datetime': [{'date1': '2021-02-04T11:05:00+00:00'},
                                       '2021-07-04T10:05:00+00:00', '2021-05-04T10:05:00+00:00']})
        self.assertTrue(idx.vlist(func=Ntv.to_name, extern=False) ==
                        ['date1', '', ''] == idx.vName())
        il = Ndataset.ntv({"i0": ["er", "er"], "i1": [0, 0], "i2": [30, 20]})
        idx = Nfield.ntv([il, il])
        self.assertEqual(idx.vlist(func=Ntv.to_obj, extern=False, format='obj', dicobj={'tab':'NdatasetConnec'})[0][0][0].val,
                         'er')
        il = Sdataset.ntv({"i0": ["er", "er"], "i1": [0, 0], "i2": [30, 20]})
        idx = Sfield([il, il])
        self.assertEqual(idx.vlist(func=Sdataset.vlist, extern=False, index=0)[0][0], 'er')

    def test_numpy(self):
        if Field != Sfield:
            idx = Field.ntv(['er', 2, 'er', arr12])
            self.assertEqual(len(idx.to_numpy(func=str)), len(idx))
            idx = Field.ntv([{'test':'er'}, 2, 'er', arr12])
            self.assertEqual(len(idx.to_numpy(func=str)), len(idx))
        else:
            idx = Field.ntv(['er', 2, 'er'])
            self.assertEqual(len(idx.to_numpy(func=str)), len(idx))

    def test_coupled_extendvalues(self):
        ia = Field.ntv(['anne', 'paul', 'lea', 'andre', 'paul', 'lea'])
        ib = Field.ntv([25, 25, 12, 12])
        self.assertTrue(ib.isderived(ia))
        # ib.extendvalues(ia)
        ib.tocoupled(ia)
        self.assertEqual(ib.val, [25, 25, 12, 12, 25, 12])
        self.assertTrue(ib.keys == ia.keys and ib.iscoupled(ia))
        #ib.extendvalues(ia, coupling=False)
        ib.tocoupled(ia, coupling=False)
        self.assertEqual(ib.val, [25, 25, 12, 12, 25, 12])
        self.assertTrue(ib.cod, [25, 12] and ib.isderived(ia))

    def test_full(self):
        ia = Field(['anne', 'paul', 'anne', 'lea'])
        ib = Field([25,25,12,12])
        Field.full([ia,ib])
        self.assertTrue(ib.iscrossed(ia))
        ia = Field(['anne', 'paul', 'anne', 'lea'])
        ib = Field([25,25,12,12])
        ic = Field(['White', 'Grey', 'White', 'Grey'])
        Field.full([ia,ib, ic])
        self.assertTrue(ib.iscrossed(ia) and ib.iscrossed(ic))

    def test_tocodec(self):
        v = [10,10,10,10,30,10,20,20,20]        
        k = [1, 1, 1, 2, 3, 2, 0, 0, 0 ]
        self.assertEqual(util.tocodec(v, k), [20, 10, 10, 30])
        self.assertEqual(sorted(util.tocodec(v)), [10, 20, 30])

    def test_to_std(self):
        idx = Field.ntv(['d1', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
        self.assertEqual(len(idx.tostdcodec().codec), len(idx))
        self.assertEqual(len(idx.tostdcodec(full=False).codec), len(idx.codec))
        self.assertTrue(idx == idx.tostdcodec(full=False) == idx.tostdcodec())
        idx = Field.ntv(['d1', 'd1', 'd1', 'd1', 'd1', 'd1', 'd1'])
        self.assertEqual(len(idx.tostdcodec().codec), len(idx))
        self.assertEqual(len(idx.tostdcodec(full=False).codec), len(idx.codec))
        self.assertTrue(idx == idx.tostdcodec(full=False) == idx.tostdcodec())

    def test_extendcodec(self):
        papy = Field.ntv(['d1', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
        parent = Field.ntv(['j', 'j', 'f', 'f', 'm', 's', 's'])
        idx = Field.ntv(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        parent2 = parent.setkeys(papy.keys, inplace=False)
        idx2 = idx.setkeys(parent.keys, inplace=False)
        self.assertEqual(idx.values, idx2.values)
        self.assertEqual(len(parent2.codec), len(papy.codec))
        self.assertEqual(len(idx2.codec), len(parent.codec))
        self.assertTrue(idx2.isderived(parent2) and parent2.iscoupled(papy))
        idxcalc = Field.from_parent(idx2.codec, parent=parent)
        self.assertTrue(idxcalc.values == idx2.values == idx.values)
        idx = Field(codec=['s', 'n', 's', 'd', 's', 'd'],
                     keys=[0, 4, 2, 1, 5, 3, 3])
        values = idx.values
        parent = Field(codec=[6, 9, 8, 11, 7, 9], keys=[0, 4, 2, 1, 5, 3, 3])
        idx.setkeys(parent.keys)
        idxcalc = Field.from_parent(idx.codec, parent=parent)
        self.assertTrue(idxcalc.values == idx.values == values)

    def test_duplicates(self):
        il = Field(['a', 'b', 'c', 'a', 'b', 'c', 'a', 'e', 'f', 'b', 'd', 'a', 'b', 'c',
                     'c', 'a', 'a', 'a', 'b', 'c', 'a', 'e', 'f', 'b', 'd'])
        il.setkeys([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0,
                   1, 2, 2, 3, 3, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(
            set([il.val[item] for item in il.getduplicates()]), set(['a', 'b', 'c']))

    def test_derkeys(self):
        parent = Field.ntv(['j', 'j', 'f', 'f', 'm', 's', 's'])
        fils = Field.ntv(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        idx = Field(fils.codec, keys=Field.keysfromderkeys(
            parent.keys, fils.derkeys(parent)))
        self.assertEqual(idx, fils)
        grandpere = Field.ntv(
            [0,     0,   2,   3,   4,   4,   6,   7,   8,   9,   9,  11,  12])
        pere = Field.ntv(['j', 'j', 'f', 'a', 'm', 'm',
                           's', 's', 's', 'n', 'd', 'd', 'd'])
        fils = Field.ntv(['t1', 't1', 't1', 't2', 't2',
                           't2', 't3', 't3', 't3', 't4', 't4', 't4', 't4'])
        petitfils = Field.ntv(
            ['s11', 's1', 's1', 's1', 's1', 's11', 's2', 's2', 's2', 's1', 's2', 's2', 's2'])
        fils.coupling(petitfils)
        pere.coupling(fils)
        grandpere.coupling(pere)
        self.assertTrue(petitfils.isderived(fils) == fils.isderived(pere)
                        == pere.isderived(grandpere))
        idx = Field(petitfils.codec,
                     keys=Field.keysfromderkeys(fils.keys, petitfils.derkeys(fils)))
        self.assertEqual(idx, petitfils)
        idx = Field(fils.codec,
                     keys=Field.keysfromderkeys(pere.keys, fils.derkeys(pere)))
        self.assertEqual(idx, fils)
        idx = Field(pere.codec,
                     keys=Field.keysfromderkeys(grandpere.keys, pere.derkeys(grandpere)))
        self.assertEqual(idx, pere)

    def test_json(self):
        self.assertTrue(Field.ntv(
            Field(['a']).to_ntv()).to_ntv() == Field(['a']).to_ntv() == Ntv.obj('a'))
        self.assertTrue(Field.ntv(
            Field([0]).to_ntv()).to_ntv() == Field([0]).to_ntv() == Ntv.obj(0))
        self.assertTrue(Field.ntv(Field().to_ntv()).to_ntv() == Field().to_ntv() == NtvList([]))
        parent = Field.ntv(['j', 'j', 'f', 'f', 'm', 's', 's'])
        fils = Field.ntv(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        js = fils.tostdcodec().to_ntv(parent=-1)
        idx = Field.from_ntv(js)
        self.assertEqual(idx, fils)
        js = fils.to_ntv(keys=fils.derkeys(parent), parent=1)
        idx = Field.from_ntv(js, extkeys=parent.keys)
        self.assertEqual(idx, fils)
        encoded = [True, False]
        format = ['json', 'cbor']
        test = list(product(encoded, format))
        for ts in test:
            option = {'encoded': ts[0], 'format': ts[1]}
            idx2 = Field.from_ntv(idx.to_ntv().to_obj(**option), decode_str=True)
            self.assertEqual(idx.values, idx2.values)
            idx2 = Field.from_ntv(idx.tostdcodec().to_ntv().to_obj(**option), decode_str=True)  # full format
            self.assertEqual(idx.values, idx2.values)
            idx2 = Field.from_ntv(idx.to_ntv(keys=fils.derkeys(parent), parent=1).to_obj(**option),
                              extkeys=parent.keys, decode_str=True)  # default format
            self.assertEqual(idx.values, idx2.values)

    def test_to_from_ntv(self):
        if Field != Sfield:
            listobj = [Field(),
                       Field(1),
                       Field.ntv([0]),
                       Field.ntv(['a']),
                       Field.ntv({'datatio': ['er', 'rt', 'ty', 'ty']}),
                       Field.ntv([arr12, [2, 3], [3, 4]]),
                       Field(codec=['s', 'n', 's', 'd', 's', 'd'],
                              keys=[0, 4, 2, 1, 5, 3, 3]),
                       Field.ntv(['er', 2, 'er', arr12]),
                       Field(codec=['er', 2, arr12],
                              name='test', keys=[0, 1, 2, 1]),
                       #Field.ntv(['er', 2, [1, 2], 2], 'test'),
                       Field.ntv({'test': ['er', 2, arr12, 2]}),
                       #Field.dic({'test': ['er', 2, [1, 2], 2]}, fullcodec=True),
                       #Field.ext(['er', 2, [1, 2], 2], 'test', fullcodec=True)
                       ]
        else:
            listobj = [Field(),
                       Field(1),
                       Field.ntv([0]),
                       Field.ntv(['a']),
                       Field.ntv({'datatio': ['er', 'rt', 'ty', 'ty']}),
                       Field(codec=['s', 'n', 's', 'd', 's', 'd'],
                              keys=[0, 4, 2, 1, 5, 3, 3]),
                       Field.ntv(['er', 2, 'er']),
                       Field(codec=['er', 2],
                              name='test', keys=[0, 1, 1]),
                       Field.ntv({'test': ['er', 2, 2]}),
                       #Field.dic({'test': ['er', 2, [1, 2], 2]}, fullcodec=True),
                       #Field.ext(['er', 2, [1, 2], 2], 'test', fullcodec=True)
                       ]
        encoded = [True, False]
        format = ['json', 'cbor']
        modecodec = ['full', 'default', 'optimize']
        test = list(product(encoded, format, modecodec))
        for i, idx in enumerate(listobj):
            for ts in test:
                option = {
                    'encoded': ts[0], 'format': ts[1], 'modecodec': ts[2]}
                #print(i, option)
                idx2 = Field.from_ntv(idx.to_ntv().to_obj(**option), decode_str=True)
                self.assertEqual(idx, idx2)

    def test_iadd(self):
        if Field != Sfield:
            idx = Field.ntv(['er', 2, arr12])
        else:
            idx = Field.ntv(['er', 2])
        idx2 = idx + idx
        self.assertEqual(idx2.val, idx.val + idx.val)
        self.assertEqual(len(idx2), 2 * len(idx))
        self.assertEqual(len(idx2), 2 * len(idx))
        idx += idx
        self.assertEqual(idx2, idx)

    def test_periodic_coef(self):
        self.assertEqual(Field.encode_coef([0,0,1,1,2,2,3,3]), 2)
        self.assertEqual(Field.encode_coef([0,0,1,1,2,2,4,4]), 0)
        self.assertEqual(Field.encode_coef([0,1,2,3,4,5,6,7]), 1)
        self.assertEqual(Field.encode_coef([0,0,0,0,1,1,1,1]), 4)
        self.assertEqual(Field.encode_coef([1,1,1,1,0,0,0,0]), 0)

    def test_ntv(self):
        fields = [{'full_dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21']},
                  ['1964-01-01', '1985-02-05', '2022-01-21'],
                  {'full_simple': [1,2,3,4]},
                  {'complete_test': [['a', 'b'], [0, 0, 1, 0]]},
                  {'complete_test': [['a', 'b'], [0, 0, 1, 0]]},
                  {"complete_date": [{"::date": ["2000-01-01", "2000-02-01"]}, [0, 0, 1]]},
                  {'implicit_test': [['a', 'b'], 'parent']},
                  {'relative_test': [{'::string': ['a', 'b']}, 1, [0, 1, 1]]},
                  [{'::string': ['a', 'b']}, 1, [0, 1, 1]],
                  {'primary_test': [['a', 'b'], [2]]},
                  [['a', 'b'], [2]],
                  {'unic_test': 'valunic' },
                  'valunic',
                  {'primary': [['oui', 'fin 2022'], [1]]},
                  [['oui', 'fin 2022'], [1]]
                  ]
        if Field != Sfield:
            fields += [{'full_coord::point':    [[1,2], [3,4], [5,6]]}]
        for field in fields:
            idx = Field.from_ntv(field, reindex=False)
            #print(idx, type(idx.values[0]))
            if idx:
                for mode in ['full', 'default', 'optimize']:
                    #print(Field.to_ntv(idx, mode))
                    self.assertEqual(idx, Field.from_ntv(idx.to_ntv(mode)))

if __name__ == '__main__':
    unittest.main(verbosity=2)
