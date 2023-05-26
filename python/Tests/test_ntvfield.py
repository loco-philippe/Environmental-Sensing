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
import datetime
from itertools import product
from observation import NamedValue, DatationValue, LocationValue, PropertyValue, ESValue, Ntvdataset, Ntvfield, ES, util
from test_obs import dat3, loc3, prop2
from ntv import Ntv, NtvSingle, NtvList


class Test_Ntvfield(unittest.TestCase):

    def test_init_unitaire(self):
        idx = Ntvfield()
        idx2 = Ntvfield.ntv()
        idx3 = Ntvfield.ext()
        self.assertTrue(idx == idx2 == idx3 == Ntvfield(idx))
        self.assertTrue(
            idx.name == ES.defaultindex and idx.codec == [] and idx.keys == [])
        self.assertTrue(idx.values == [])
        idx = Ntvfield(lendefault=3)
        self.assertTrue(idx.name == ES.defaultindex and 
                        idx.cod == [0] and idx.keys == [0, 0, 0])
        self.assertTrue(idx.val == [0, 0, 0])
        self.assertTrue(Ntvfield(1) == Ntvfield([1]))
        self.assertTrue(Ntvfield('trux') == Ntvfield(['trux']))

    def test_init(self):
        idx = Ntvfield(codec=[Ntv.obj('er'), Ntv.obj(2), Ntv.obj([1, 2])], name='test', keys=[0, 1, 2, 1])
        idx2 = Ntvfield.from_ntv({'test': ['er', 2, [1, 2], 2]})
        #idx3 = Ntvfield.ext(['er', 2, [1, 2], 2], 'test')
        #idx4 = Ntvfield.ext(['er', 2, [1, 2], 2], 'test', fullcodec=True)
        self.assertTrue(Ntvfield(idx) == idx)
        #self.assertTrue(Ntvfield(idx) == Ntvfield.ext(idx) == idx)
        self.assertTrue(idx.name == 'test' and 
                        idx.cod == ['er', 2, [1, 2]] and 
                        idx.keys == [0, 1, 2, 1])
        self.assertTrue(idx == idx2)
        #self.assertTrue(idx == idx2 ==idx3)
        #self.assertTrue(idx.val == idx4.val == idx4.cod == ['er', 2, [1, 2], 2]
        #                == idx5.val == idx5.cod and len(idx) == 4)
        '''idx = Ntvfield(['er', 'rt', 'ty'], 'datation', [0, 1, 2, 2])
        idx2 = Ntvfield.ext(['er', 'rt', 'ty', 'ty'], 'datation')
        idx3 = Ntvfield.dic({'datation': ['er', 'rt', 'ty', 'ty']})
        self.assertTrue(idx == idx2 == idx3)
        self.assertTrue(isinstance(idx.codec[0], DatationValue))
        self.assertTrue(idx.values[3] == DatationValue(name='ty'))
        idx = Ntvfield(['er', 'rt', Ntvdataset()], 'result', [0, 1, 2, 2])
        idx2 = Ntvfield.ext(['er', 'rt', Ntvdataset(), Ntvdataset()], 'result')
        idx3 = Ntvfield.dic({'result': ['er', 'rt', Ntvdataset(), Ntvdataset()]})
        self.assertTrue(idx == idx2 == idx3)
        if ES.def_clsName:
            self.assertTrue(isinstance(idx.codec[0], NamedValue))
        self.assertTrue(idx.values[3].value == Ntvdataset())
        self.assertTrue(Ntvfield.obj(
            [1, 2, 3], typevalue=None) == Ntvfield([1, 2, 3]))
        self.assertTrue(Ntvfield(codec=[True], lendefault=3).val == [
                        True, True, True])'''

    def test_obj(self):
        listval = [{'name': ['value']}, 
                   'value', 
                   ['value'], 
                   ['value', 'value2'],
                   {'b': ['value', [[1], [2]], [[3], [4]]]},
                   {'b': ['value', [[[0.0, 1.0], [1.0, 2.0], [1.0, 1.0], [0.0, 1.0]]],
                          [[[0.0, 2.0], [2.0, 2.0], [1.0, 1.0], [0.0, 2.0]]]]}
                   ]
        for val in listval:
            self.assertTrue(Ntvfield.ntv(val).val[0] == 'value')
            self.assertTrue(Ntvfield.ntv(Ntvfield.ntv(val).to_ntv()) == Ntvfield.ntv(val))
        val = {'namvalue': 'value'}
        val2 = {'namvalue': ['value']}
        self.assertTrue(Ntvfield.ntv(val).name == 'namvalue')
        self.assertTrue(Ntvfield.ntv(val2).name == 'namvalue')
        self.assertTrue(Ntvfield.ntv(val2).val[0] == 'value')
        self.assertTrue(Ntvfield.ntv(val).val[0] == 'value')
        self.assertTrue(Ntvfield.ntv(val).to_ntv().to_obj() == val)
        self.assertTrue(Ntvfield.ntv(val2).to_ntv().to_obj() == val)
        val  = {'datation': ['name']}
        val2 = {'datation': 'name'}
        self.assertTrue(Ntvfield.ntv(val).name == 'datation')
        self.assertTrue(Ntvfield.ntv(val).val[0] == 'name')
        self.assertTrue(Ntvfield.ntv(val).to_ntv().to_obj() == val2)

    def test_infos(self):
        idx = Ntvfield.ntv(['er', 2, [1, 2]])
        self.assertTrue(idx.infos == {'lencodec': 3, 'mincodec': 3, 'maxcodec': 3,
                                      'typecodec': 'complete', 'ratecodec': 0.0})
        idx2 = Ntvfield.ntv({'result': ['er', Ntvdataset(), Ntvdataset()]} )
        self.assertTrue(idx2.infos == {'lencodec': 2, 'mincodec': 2, 'maxcodec': 3,
                                       'typecodec': 'default', 'ratecodec': 1.0})
        idx2 = Ntvfield()
        self.assertTrue(idx2.infos == {'lencodec': 0, 'mincodec': 0, 'maxcodec': 0,
                                       'typecodec': 'null', 'ratecodec': 0.0})

    def test_append(self):
        idx = Ntvfield.ntv(['er', 2, [1, 2]])
        self.assertTrue(idx.append(8) == 3)
        self.assertTrue(idx.append(8) == 3)
        self.assertTrue(idx.append(8, unique=False) == 4)
        self.assertTrue(idx[4] == NtvSingle(8))

    def test_loc_keyval(self):
        idx = Ntvfield.ntv(['er', 2, [1, 2]])
        self.assertTrue(idx.keytoval(idx.valtokey([1, 2])) == [1, 2])
        self.assertTrue(idx.isvalue([1, 2]))
        idx = Ntvfield.ntv( {'location::point': 
                           [{'paris': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]]})
        self.assertTrue(idx.keytoval(
            idx.valtokey({':point':[4.83, 45.76]})) == {':point':[4.83, 45.76]})
        self.assertTrue(idx.loc({':point':[4.83, 45.76]}) == [1])
        idx = Ntvfield.ntv([1, 3, 3, 2, 5, 3, 4])
        self.assertTrue(idx.loc(3) == [1, 2, 5])

    def test_setvalue_setname(self):
        idx = Ntvfield.ntv(['er', 2, [1, 2]])
        idx[1] = Ntv.obj('er')
        self.assertTrue(idx.val == ['er', 'er', [1, 2]])
        idx.setcodecvalue('er', 'ez')
        self.assertTrue(idx.val == ['ez', 'ez', [1, 2]])
        idx[1] = Ntv.obj(3)
        self.assertTrue(idx.val == ['ez', 3, [1, 2]])
        idx.setvalue(0, {':date': '2001-02-03'})
        self.assertTrue(idx.val == [{':date': '2001-02-03'}, 3, [1, 2]])
        self.assertTrue(idx.values[0] == Ntv.obj({':date': '2001-02-03'}))
        idx.setlistvalue([3, [3, 4], 'ee'])
        self.assertTrue(idx.val == [3, [3, 4], 'ee'])
        idx.setname('truc')
        self.assertEqual(idx.name, 'truc')

    def test_record(self):
        ia = Ntvfield.ntv(['anne', 'paul', 'lea', 'andre', 'paul', 'lea'])
        self.assertEqual([ia[i].to_obj()
                         for i in ia.recordfromvalue('paul')], ['paul', 'paul'])

    def test_reset_reorder_sort(self):
        idx = Ntvfield.ntv(['er', 2, 'er', [1, 2]])
        cod = copy(idx.codec)
        idx.codec.append(Ntv.obj('ez'))
        # idx.resetkeys()
        idx.reorder()
        self.assertEqual(cod, idx.codec)
        order = [1, 3, 0, 2]
        idx.reorder(order)
        self.assertEqual(idx.val, [2, [1, 2], 'er', 'er'])
        # idx.sort()
        self.assertEqual(idx.sort().val, ['er', 'er', 2, [1, 2]])
        idxs = idx.sort(inplace=False, reverse=True)
        self.assertEqual(idxs.val, [[1, 2], 2, 'er', 'er'])
        idx = Ntvfield.ntv([1, 3, 3, 2, 5, 3, 4]).sort(inplace=False)
        self.assertEqual(idx.val, [1, 2, 3, 3, 3, 4, 5])
        self.assertEqual(idx.cod,  [1, 2, 3, 4, 5])

    def test_derived_coupled(self):
        der = Ntvfield.ntv([1, 1, 1, 2])
        ref = Ntvfield.ntv([1, 1, 3, 4])
        self.assertTrue(der.isderived(ref) and not der.iscoupled(ref))
        der.tocoupled(ref)
        self.assertTrue(not der.isderived(ref) and der.iscoupled(ref))
        # der.resetkeys()
        der.reorder()
        self.assertTrue(der.isderived(ref) and not der.iscoupled(ref))
        ia = Ntvfield.ntv(['anne', 'paul', 'anne', 'lea', 'anne'])
        ib = Ntvfield.ntv([25, 25, 12, 12, 25])
        self.assertTrue(not ia.isderived(ib) and not ia.iscoupled(ib))
        self.assertTrue(not ib.isderived(ia) and not ib.iscoupled(ia))
        ia.coupling(ib)
        self.assertTrue(ib.isderived(ia))
        ia.coupling(ib, derived=False)
        self.assertTrue(ib.iscoupled(ia))

    def test_coupling_infos(self):
        ia = Ntvfield()
        ib = Ntvfield.ntv([25, 25, 12, 12, 25])
        self.assertEqual(ia.couplinginfos(ib),
                         {'dist': 0, 'distrate': 0, 'distance': 0, 'rate': 0,
                          'disttomin': 0, 'disttomax': 0, 'distmin': 0, 'distmax': 0,
                          'diff': 0, 'typecoupl': 'null'})
        ia = Ntvfield.ntv(['anne', 'paul', 'anne', 'lea', 'anne'])
        self.assertEqual(ia.couplinginfos(ib),
                         {'dist': 4, 'distrate': 0.3333333333333333, 'distance': 2,
                          'disttomin': 1, 'disttomax': 2, 'distmin': 3, 'distmax': 6,
                          'rate': 0.5, 'diff': 1, 'typecoupl': 'link'})
        self.assertTrue(ia.islinked(ib))
        ia = Ntvfield.ntv(['anne', 'lea', 'anne', 'lea', 'anne'])
        self.assertEqual(ia.couplinginfos(ib),
                         {'dist': 4, 'distrate': 1.0, 'distance': 2, 'rate': 1.0,
                          'disttomin': 2, 'disttomax': 0, 'distmin': 2, 'distmax': 4,
                          'diff': 0, 'typecoupl': 'crossed'})
        self.assertTrue(ia.iscrossed(ib))

    def test_vlist(self):
        testidx = [Ntvfield(), Ntvfield.ntv(['er', 2, 'er', [1, 2]])]
        residx = [[], ['er', '2', 'er', str([1, 2])]]
        for idx, res in zip(testidx, residx):
            self.assertEqual(idx.vlist(str), res)
        '''il = Ntvdataset.ntv({"i0": ["er", "er"], "i1": [0, 0], "i2": [30, 20]})
        idx = Ntvfield.ntv([il, il])
        self.assertEqual(idx.vlist(func=Ntvdataset.to_obj, extern=False, encoded=False)[0][0],
                         ['er'])
        idx = Ntvfield.ntv({'datation::datetime': [{'date1': '2021-02-04T11:05:00+00:00'},
                                       '2021-07-04T10:05:00+00:00', '2021-05-04T10:05:00+00:00']})
        self.assertTrue(idx.vlist(func=ESValue.vName, extern=False, default='ici') ==
                        ['date1', 'ici', 'ici'] == idx.vName(default='ici'))'''

    def test_numpy(self):
        idx = Ntvfield.ntv(['er', 2, 'er', [1, 2]])
        self.assertEqual(len(idx.to_numpy(func=str)), len(idx))
        idx = Ntvfield.ntv([{'test':'er'}, 2, 'er', [1, 2]])
        self.assertEqual(len(idx.to_numpy(func=str)), len(idx))

    def test_coupled_extendvalues(self):
        ia = Ntvfield.ntv(['anne', 'paul', 'lea', 'andre', 'paul', 'lea'])
        ib = Ntvfield.ntv([25, 25, 12, 12])
        self.assertTrue(ib.isderived(ia))
        # ib.extendvalues(ia)
        ib.tocoupled(ia)
        self.assertEqual(ib.val, [25, 25, 12, 12, 25, 12])
        self.assertTrue(ib.keys == ia.keys and ib.iscoupled(ia))
        #ib.extendvalues(ia, coupling=False)
        ib.tocoupled(ia, coupling=False)
        self.assertEqual(ib.val, [25, 25, 12, 12, 25, 12])
        self.assertTrue(ib.cod, [25, 12] and ib.isderived(ia))

    '''def test_crossed(self):
        ia = Ntvfield.ext(['anne', 'paul', 'anne', 'lea'])
        ib = Ntvfield.ext([25,25,12,12])
        Ntvfield.tocrossed([ia,ib])
        self.assertTrue(ib.iscrossed(ia))
        ia = Ntvfield.ext(['anne', 'paul', 'anne', 'lea'])
        ib = Ntvfield.ext([25,25,12,12])
        ic = Ntvfield.ext(['White', 'Grey', 'White', 'Grey'])
        Ntvfield.tocrossed([ia,ib, ic])
        self.assertTrue(ib.iscrossed(ia) and ib.iscrossed(ic))'''

    def test_tocodec(self):
        v = [10,10,10,10,30,10,20,20,20]        
        k = [1, 1, 1, 2, 3, 2, 0, 0, 0 ]
        self.assertEqual(util.tocodec(v, k), [20, 10, 10, 30])
        self.assertEqual(sorted(util.tocodec(v)), [10, 20, 30])

    def test_to_std(self):
        idx = Ntvfield.ntv(['d1', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
        self.assertEqual(len(idx.tostdcodec().codec), len(idx))
        self.assertEqual(len(idx.tostdcodec(full=False).codec), len(idx.codec))
        self.assertTrue(idx == idx.tostdcodec(full=False) == idx.tostdcodec())
        idx = Ntvfield.ntv(['d1', 'd1', 'd1', 'd1', 'd1', 'd1', 'd1'])
        self.assertEqual(len(idx.tostdcodec().codec), len(idx))
        self.assertEqual(len(idx.tostdcodec(full=False).codec), len(idx.codec))
        self.assertTrue(idx == idx.tostdcodec(full=False) == idx.tostdcodec())

    def test_extendcodec(self):
        papy = Ntvfield.ntv(['d1', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
        parent = Ntvfield.ntv(['j', 'j', 'f', 'f', 'm', 's', 's'])
        idx = Ntvfield.ntv(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        parent2 = parent.setkeys(papy.keys, inplace=False)
        idx2 = idx.setkeys(parent.keys, inplace=False)
        self.assertEqual(idx.values, idx2.values)
        self.assertEqual(len(parent2.codec), len(papy.codec))
        self.assertEqual(len(idx2.codec), len(parent.codec))
        self.assertTrue(idx2.isderived(parent2) and parent2.iscoupled(papy))
        idxcalc = Ntvfield.from_parent(idx2.codec, parent=parent)
        self.assertTrue(idxcalc.values == idx2.values == idx.values)
        idx = Ntvfield(codec=['s', 'n', 's', 'd', 's', 'd'],
                     keys=[0, 4, 2, 1, 5, 3, 3])
        values = idx.values
        parent = Ntvfield(codec=[6, 9, 8, 11, 7, 9], keys=[0, 4, 2, 1, 5, 3, 3])
        idx.setkeys(parent.keys)
        idxcalc = Ntvfield.from_parent(idx.codec, parent=parent)
        self.assertTrue(idxcalc.values == idx.values == values)

    def test_duplicates(self):
        il = Ntvfield(['a', 'b', 'c', 'a', 'b', 'c', 'a', 'e', 'f', 'b', 'd', 'a', 'b', 'c',
                     'c', 'a', 'a', 'a', 'b', 'c', 'a', 'e', 'f', 'b', 'd'])
        il.setkeys([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0,
                   1, 2, 2, 3, 3, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(
            set([il.val[item] for item in il.getduplicates()]), set(['a', 'b', 'c']))

    def test_derkeys(self):
        parent = Ntvfield.ntv(['j', 'j', 'f', 'f', 'm', 's', 's'])
        fils = Ntvfield.ntv(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        idx = Ntvfield(fils.codec, keys=Ntvfield.keysfromderkeys(
            parent.keys, fils.derkeys(parent)))
        self.assertEqual(idx, fils)
        grandpere = Ntvfield.ntv(
            [0,     0,   2,   3,   4,   4,   6,   7,   8,   9,   9,  11,  12])
        pere = Ntvfield.ntv(['j', 'j', 'f', 'a', 'm', 'm',
                           's', 's', 's', 'n', 'd', 'd', 'd'])
        fils = Ntvfield.ntv(['t1', 't1', 't1', 't2', 't2',
                           't2', 't3', 't3', 't3', 't4', 't4', 't4', 't4'])
        petitfils = Ntvfield.ntv(
            ['s11', 's1', 's1', 's1', 's1', 's11', 's2', 's2', 's2', 's1', 's2', 's2', 's2'])
        fils.coupling(petitfils)
        pere.coupling(fils)
        grandpere.coupling(pere)
        self.assertTrue(petitfils.isderived(fils) == fils.isderived(pere)
                        == pere.isderived(grandpere))
        idx = Ntvfield(petitfils.codec,
                     keys=Ntvfield.keysfromderkeys(fils.keys, petitfils.derkeys(fils)))
        self.assertEqual(idx, petitfils)
        idx = Ntvfield(fils.codec,
                     keys=Ntvfield.keysfromderkeys(pere.keys, fils.derkeys(pere)))
        self.assertEqual(idx, fils)
        idx = Ntvfield(pere.codec,
                     keys=Ntvfield.keysfromderkeys(grandpere.keys, pere.derkeys(grandpere)))
        self.assertEqual(idx, pere)

    def test_json(self):
        self.assertTrue(Ntvfield.ntv(
            Ntvfield(['a']).to_ntv()).to_ntv() == Ntvfield(['a']).to_ntv() == Ntv.obj('a'))
        self.assertTrue(Ntvfield.ntv(
            Ntvfield([0]).to_ntv()).to_ntv() == Ntvfield([0]).to_ntv() == Ntv.obj(0))
        self.assertTrue(Ntvfield.ntv(Ntvfield().to_ntv()).to_ntv() == Ntvfield().to_ntv() == NtvList([]))
        parent = Ntvfield.ntv(['j', 'j', 'f', 'f', 'm', 's', 's'])
        fils = Ntvfield.ntv(['t1', 't1', 't1', 't1', 't2', 't3', 't3'])
        js = fils.tostdcodec().to_ntv(parent=-1)
        #prt, idx = Ntvfield.from_ntv(js)
        idx = Ntvfield.from_ntv(js)
        self.assertEqual(idx, fils)
        #self.assertEqual(prt, -1)
        js = fils.to_ntv(keys=fils.derkeys(parent), parent=1)
        #prt, idx = Ntvfield.from_obj(js, extkeys=parent.keys)
        idx = Ntvfield.from_ntv(js, extkeys=parent.keys)
        self.assertEqual(idx, fils)
        #self.assertEqual(prt, 1)
        encoded = [True, False]
        format = ['json', 'cbor']
        test = list(product(encoded, format))
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1]}
            idx2 = Ntvfield.ntv(idx.to_ntv().to_obj(**option))
            #idx2 = Ntvfield.obj(idx.to_obj(keys=True, **option))
            self.assertEqual(idx.values, idx2.values)
            idx2 = Ntvfield.ntv(idx.tostdcodec().to_ntv().to_obj(**option))  # full format
            self.assertEqual(idx.values, idx2.values)
            idx2 = Ntvfield.ntv(idx.to_ntv(keys=fils.derkeys(parent), parent=1).to_obj(**option),
                              extkeys=parent.keys)  # default format
            self.assertEqual(idx.values, idx2.values)

    """def test_castobj(self):  # !!!
        liste = [['{"namvalue":{"val":21}}',    'ESValue',         NamedValue],
                 [{"val": 21},                     'ESValue',         NamedValue],
                 [{"val": 21},                     None,              str],
                 #[{"val":21},                     None,              NamedValue],
                 ['{"namvalue":{"val":21}}',      None,              NamedValue],
                 ['{"locvalue":{"val":[2, 1]}}',
                     'LocationValue',   LocationValue],
                 ['{"locvalue":{"val":[2, 1]}}',
                     None,              LocationValue],
                 #['{"observation":{"val":21}}',  'Observation',     Observation],
                 #[Observation(),                 'Observation',     Observation],
                 #[Observation(),                  None,             Observation],
                 [datetime.datetime(2020, 1, 1),
                  'DatationValue',   DatationValue],
                 #[datetime.datetime(2020,1,1),   'TimeSlot',        TimeSlot],
                 [datetime.datetime(2020, 1, 1),    None,              datetime.datetime]]
        for t in liste:
            self.assertTrue(isinstance(util.castobj([t[0]], t[1])[0], t[2]))
        idx = Ntvfield.dic({'datation': ['er', 'rt', 'ty', 'ty']})
        self.assertTrue(isinstance(idx.values[0], DatationValue))
        idx = Ntvfield.dic({'ESdatation': ['er', 'rt', 'ty', 'ty']})
        self.assertTrue(isinstance(idx.values[0], NamedValue))
        idx = Ntvfield.dic({'dates': ['er', 'rt', 'ty', 'ty']})
        if not ES.def_clsName:
            self.assertTrue(isinstance(idx.values[0], str))
        else:
            self.assertTrue(isinstance(idx.values[0], NamedValue))"""

    def test_to_from_obj(self):
        listobj = [Ntvfield(),
                   Ntvfield(1),
                   Ntvfield.ntv([0]),
                   Ntvfield.ntv(['a']),
                   Ntvfield.ntv({'datatio': ['er', 'rt', 'ty', 'ty']}),
                   Ntvfield.ntv([[1, 2], [2, 3], [3, 4]]),
                   Ntvfield(codec=['s', 'n', 's', 'd', 's', 'd'],
                          keys=[0, 4, 2, 1, 5, 3, 3]),
                   Ntvfield.ntv(['er', 2, 'er', [1, 2]]),
                   Ntvfield(codec=['er', 2, [1, 2]],
                          name='test', keys=[0, 1, 2, 1]),
                   #Ntvfield.ntv(['er', 2, [1, 2], 2], 'test'),
                   Ntvfield.ntv({'test': ['er', 2, [1, 2], 2]}),
                   #Ntvfield.dic({'test': ['er', 2, [1, 2], 2]}, fullcodec=True),
                   #Ntvfield.ext(['er', 2, [1, 2], 2], 'test', fullcodec=True)
                   ]
        encoded = [True, False]
        format = ['json', 'cbor']
        #modecodec = ['full', 'default', 'dict']
        modecodec = ['full', 'default', 'optimize']
        test = list(product(encoded, format, modecodec))
        for i, idx in enumerate(listobj):
            for ts in test:
                option = {
                    'encoded': ts[0], 'encode_format': ts[1], 'modecodec': ts[2]}
                #print(i, option)
                idx2 = Ntvfield.ntv(idx.to_ntv().to_obj(**option))
                '''if ts[2] == 'dict':
                    idx2 = Ntvfield.obj(idx.to_dict_obj(**option))
                else:
                    idx2 = Ntvfield.obj(idx.to_obj(**option))'''
                self.assertEqual(idx, idx2)

    def test_iadd(self):
        idx = Ntvfield.ntv(['er', 2, [1, 2]])
        idx2 = idx + idx
        self.assertEqual(idx2.val, idx.val + idx.val)
        self.assertEqual(len(idx2), 2 * len(idx))
        self.assertEqual(len(idx2), 2 * len(idx))
        idx += idx
        self.assertEqual(idx2, idx)

    def test_iskeys(self):
        istrue = [1, [1], [-1, [1, 2, 3]], [1, [1]], [1, 2, 3]]
        isfalse = ['a', [[1, 2]], [[1, 2], [2, 3]], [1, 2, [2, 3]], [[1], 2, 3], [1, [1, 2, 0.1]],
                   [-1.5, [1, 2, 3]], [1, 2, 3.2]]
        for isT in istrue:
            self.assertTrue(Ntvfield.iskeysobj(isT))
        for isF in isfalse:
            self.assertFalse(Ntvfield.iskeysobj(isF))

    '''def test_jsontype(self):
        self.assertEqual(Ntvfield.decodetype(
            Ntvfield.decodeobj([1, 2, 3, 4]), 4), 'root coupled')
        self.assertEqual(Ntvfield.decodetype(
            Ntvfield.decodeobj([1, 2, 3, 4]), 3), 'primary')
        self.assertEqual(Ntvfield.decodetype(Ntvfield.decodeobj([1])), 'unique')
        self.assertEqual(Ntvfield.decodetype(Ntvfield.decodeobj(
            [[1, 2, 3], [0, 1, 2, 0]]), 4), 'root derived')
        self.assertEqual(Ntvfield.decodetype(Ntvfield.decodeobj(
            [[1, 2, 3], [1]]), 4), 'periodic derived')
        self.assertEqual(Ntvfield.decodetype(
            Ntvfield.decodeobj([[1, 2, 3], 1]), 4), 'periodic derived')
        self.assertEqual(Ntvfield.decodetype(
            Ntvfield.decodeobj([[1, 2, 3, 4], 1]), 4), 'coupled')
        self.assertEqual(Ntvfield.decodetype(Ntvfield.decodeobj(
            [[1, 2, 3], [1, [0, 1, 2]]]), 4), 'derived')'''

    def test_periodic_coef(self):
        self.assertEqual(Ntvfield.encodecoef([0,0,1,1,2,2,3,3]), 2)
        self.assertEqual(Ntvfield.encodecoef([0,0,1,1,2,2,4,4]), 0)
        self.assertEqual(Ntvfield.encodecoef([0,1,2,3,4,5,6,7]), 1)
        self.assertEqual(Ntvfield.encodecoef([0,0,0,0,1,1,1,1]), 4)
        self.assertEqual(Ntvfield.encodecoef([1,1,1,1,0,0,0,0]), 0)

    def test_ntv(self):
        fields = [{'full_dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21']},
                  ['1964-01-01', '1985-02-05', '2022-01-21'],
                  {'full_coord::point':    [[1,2], [3,4], [5,6]]},
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
        for field in fields:
            idx = Ntvfield.from_ntv(field, reindex=False)
            #print(idx, type(idx.values[0]))
            if idx:
                for mode in ['full', 'default', 'optimize']:
                    #print(Ntvfield.to_ntv(idx, mode))
                    self.assertEqual(idx, Ntvfield.from_ntv(idx.to_ntv(mode)))

if __name__ == '__main__':
    unittest.main(verbosity=2)
