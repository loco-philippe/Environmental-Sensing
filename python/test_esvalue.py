# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `ES.test_esvalue` module contains the unit tests (class unittest) for the
`ESValue` functions.
"""
import unittest, json
from ilist3 import Ilist3
from ESObservation import Observation
from ESValue import LocationValue, DatationValue, \
    PropertyValue, NamedValue, ExternValue, ESValue #, _gshape
from ESconstante import ES
#from pprint import pprint
import datetime
from test_observation import dat3, loc3, prop2, _res, lyon, paris, pol1, \
    pol75, t1, pprop_pm25, t2, s1, t1n, matin, travail, pt1, tnull, pprop_pm10, \
    prop_pm25, pol2, pol13, aprem
from itertools import product

# couverture tests (True if non passed)----------------------------------------
simple  = False  # False

@unittest.skipIf(simple, "test unitaire")
class TestObsUnitaire(unittest.TestCase):
    '''Unit tests for `ES.ESValue`, `ES.ESObs`, `ES.ESElement` '''
    opt = ES.mOption.copy()

    def test_valClassName(self):
        self.assertEqual(ESValue.valClassName(21), 'NamedValue')
        self.assertEqual(ESValue.valClassName('test'), 'NamedValue')
        self.assertEqual(ESValue.valClassName({"truc": 21}), 'NamedValue')
        self.assertEqual(ESValue.valClassName({"truc": Ilist3()}), 'Ilist3')
        self.assertEqual(ESValue.valClassName(NamedValue("cou")), 'NamedValue')
        self.assertEqual(ESValue.valClassName(LocationValue(name="cou")), 'LocationValue')
        self.assertEqual(ESValue.valClassName(Ilist3()), 'Ilist3')
        self.assertEqual(ESValue.valClassName(Observation()), 'Observation')
        self.assertEqual(ESValue.valClassName(datetime.datetime(2020,1,1)), 'datetime')
        self.assertEqual(ESValue.valClassName('{"namvalue":{"val":21}}'), 'NamedValue')
        self.assertEqual(ESValue.valClassName('{"locvalue":{"val":21}}'), 'LocationValue')
        self.assertEqual(ESValue.valClassName('{"observation":{"val":21}}'), 'Observation')
        self.assertEqual(ESValue.valClassName('{"truc":{"observation":{}}}'), 'NamedValue')
        self.assertEqual(ESValue.valClassName('{"locvalue":1, "observation":{}}'), 'NamedValue')
        self.assertEqual(ESValue.valClassName({"namvalue":{"val":21}}), 'NamedValue')
        self.assertEqual(ESValue.valClassName({"locvalue":{"val":21}}), 'LocationValue')
        self.assertEqual(ESValue.valClassName({"observation":{"val":21}}), 'Observation')
        self.assertEqual(ESValue.valClassName({"truc": Observation()}), 'Observation')
        self.assertEqual(ESValue.valClassName({"locvalue":1, "observation":{}}), 'NamedValue')
        
    def test_NamedValue(self):
        self.assertEqual(NamedValue("coucou").json(), '"coucou"')
        self.assertEqual(NamedValue.from_obj('{"er":2}').json(), '{"er": 2}')
        self.assertEqual(NamedValue(21).json(), '21')
        self.assertEqual(NamedValue(2.1).json(), '2.1')
        self.assertEqual(NamedValue.from_obj('{"er":2}').EStype, 132)
        self.assertEqual(NamedValue(22).EStype, 32)
        self.assertEqual(NamedValue("coucou").EStype, 32)

    def test_locationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(LocationValue(lyon).json(**self.opt), json.dumps(lyon))
        self.assertEqual(LocationValue(lyon), LocationValue(LocationValue(lyon)))
        self.assertTrue(LocationValue(lyon) > LocationValue(paris))
        self.assertEqual(LocationValue(pol1).json(**self.opt), json.dumps(pol1))
        self.assertTrue(LocationValue(paris).value == LocationValue.from_obj({'paris':paris}).value ==
                        LocationValue(name='paris', val=LocationValue._gshape(paris)).value)
        self.assertTrue(LocationValue(name='paris').name == LocationValue.from_obj({'paris':paris}).name ==
                        LocationValue(name='paris', val=LocationValue._gshape(paris)).name)
        self.assertEqual(LocationValue.Box(LocationValue(paris).bounds).bounds,
                         LocationValue.from_obj({'box':paris}).bounds)
        self.assertEqual(LocationValue(lyon).EStype, 12)
        self.assertEqual(LocationValue(pol1).EStype, 13)
        self.assertEqual(LocationValue.from_obj(pol75).EStype, 113)
        self.assertEqual(LocationValue(name='pol75').EStype, 100)
        self.assertEqual(LocationValue(LocationValue.nullValue()).EStype, 0)
        self.assertTrue(LocationValue.from_obj('{"paris":[2,3]}') == LocationValue.from_obj({"paris":[2,3]}))
        


    def test_DatationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(DatationValue(t1), DatationValue(DatationValue(t1)))
        self.assertEqual(DatationValue(t1).json(encoded=False), t1.astimezone(datetime.timezone.utc))
        self.assertTrue(DatationValue(t1) < DatationValue(t2))
        self.assertEqual(DatationValue.from_obj(json.loads(t1n)).json(), t1n)
        self.opt["json_dat_name"] = True
        self.assertEqual(DatationValue.from_obj(json.loads(t1n)).json(**self.opt), t1n)
        self.assertTrue(DatationValue(t1).value == DatationValue.from_obj({'t1':t1}).value ==
                        DatationValue(name='t1', val=t1).value)
        self.assertTrue(DatationValue(name='t1').name == DatationValue.from_obj({'t1':t1}).name ==
                        DatationValue(name='t1', val=t1).name)
        self.assertEqual(DatationValue(matin).EStype, 3)
        self.assertEqual(DatationValue(travail).EStype, 4)
        self.assertEqual(DatationValue(pt1).EStype, 2)
        self.assertEqual(DatationValue(tnull).EStype, 0)
        self.assertEqual(DatationValue.from_obj(t1n).EStype, 102)
        self.assertEqual(DatationValue(name='t1n').EStype, 100)


    def test_propertyValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(PropertyValue().json(**self.opt), '{}')
        self.assertEqual(PropertyValue({ES.prp_type : "PM25"}, prp_dict=True).json(**self.opt),
                         '{"'+ES.prp_type+'": "PM25", "unit": "kg/m3"}')
        self.assertEqual(PropertyValue({ES.prp_type : "PM25"}).json(**self.opt),
                         '{"'+ES.prp_type+'": "PM25"}')
        self.assertEqual(PropertyValue(pprop_pm10).json(**self.opt), json.dumps(pprop_pm10))
        self.assertEqual(PropertyValue(prop_pm25).EStype, 22)
        self.assertEqual(PropertyValue(pprop_pm25).EStype, 23)
        self.assertEqual(PropertyValue({'truc':2}).EStype, 23)
        self.assertEqual(PropertyValue({'machin':{'truc':2}}).EStype, 123)
        self.assertEqual(PropertyValue('truc').EStype, 100)
        self.assertEqual(PropertyValue(PropertyValue.nullValue()).EStype, 0)

    def test_externValue(self):
        il=Ilist3()
        self.assertEqual(ExternValue.from_obj({'truc':il}).EStype, 143)
        self.assertEqual(ExternValue(il).EStype, 43)
        self.assertEqual(ExternValue.from_obj({'ilist':{'truc':il}}).EStype, 143)
        self.assertEqual(ExternValue.from_obj(json.dumps({"ilist":{"truc":il.json()}})).EStype, 131)
        """dic={'observation': {'type': 'observation',
          'datation': [{'date1': datetime.datetime(2021, 2, 4, 11, 5, tzinfo=datetime.timezone.utc)},
           datetime.datetime(2021, 7, 4, 10, 5, tzinfo=datetime.timezone.utc),
           datetime.datetime(2021, 5, 4, 10, 5, tzinfo=datetime.timezone.utc)],
          'location': [{'paris': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]],
          'property': [{'prp': 'PM25', 'unit': 'kg/m3'},
           {'prp': 'PM10', 'unit': 'kg/m3'}],
          'result': [0, 1, 2, 3, 4, 5],
          'index': [[0, 0, 1, 1, 2, 2], [0, 0, 1, 1, 2, 2], [0, 1, 0, 1, 0, 1]]}}
        self.assertEqual(ExternValue(dic).EStype, 44)
        self.assertEqual(ExternValue(Observation(dict((dat3, loc3, prop2, _res(6))), 
                                                 idxref={'location':'datation'})).EStype, 44)"""
        
    def test_nameValue(self):
        self.assertEqual(DatationValue(name='recre').json(encoded=False), 'recre')
        self.opt["json_prp_name"] = True
        self.assertEqual(PropertyValue(pprop_pm25).json(**self.opt), json.dumps(pprop_pm25))
        self.assertEqual(PropertyValue('test').json(**self.opt), '"test"')
        self.opt["json_loc_name"] = True
        self.assertEqual(LocationValue(lyon).json(**self.opt), json.dumps(lyon))
        self.assertEqual(LocationValue(name='test').json(**self.opt), '"test"')

    def test_setValue_setName(self):
        val = LocationValue(lyon)
        val.setValue(LocationValue([4,5]))
        self.assertEqual(val.vSimple(), [4,5])
        self.assertEqual(val.EStype, 12)
        val.setValue(LocationValue([[6,7], [7,8], [8,6]]))
        self.assertEqual(val.EStype, 14)
        self.assertEqual(val.value, LocationValue._gshape([[6,7], [7,8], [8,6]]))
        val.setValue(LocationValue([[[6,7], [7,8], [8,6]]]))
        self.assertEqual(val.EStype, 13)
        self.assertEqual(val.value, LocationValue._gshape([[[6,7], [7,8], [8,6]]]))
        val.setName('truc')
        self.assertEqual(val.name, 'truc')
        self.assertEqual(val.EStype, 113)
        val = DatationValue(t1)
        val.setValue(t2)
        self.assertEqual(val.simple, t2)
        val.setValue(DatationValue(s1))
        self.assertEqual(val.EStype, 3)
        self.assertEqual(val.vInterval(encoded=False), s1)
        val.setName('truc')
        self.assertEqual(val.name, 'truc')
        self.assertEqual(val.EStype, 103)

    def test_link(self):
        dat = DatationValue(datetime.datetime(2005,1,1))
        dat2 = DatationValue([datetime.datetime(2000,1,2), datetime.datetime(2006,1,1)])
        self.assertEqual(dat.link(dat2), 'within')
        self.assertTrue(dat.within(dat2))

        loc = LocationValue([[[0,1],[1,1], [1,0], [0,0]]])
        loc2 = LocationValue([[[0,10],[10,10], [10,0],[0,0]]])
        loc3 = LocationValue([0.5, 0.5])
        self.assertEqual(loc.link(loc2), 'within')
        self.assertTrue(loc.within(loc2))
        self.assertEqual(loc.link(loc3), 'contains')
        self.assertEqual(LocationValue([0.5, 0.5]).link(LocationValue([0.5, 0.5])), 'equals')

        prp10 = PropertyValue({"prp":'PM10', "truc":12})
        prp25 = PropertyValue({"prp":'PM25', "truc":15})
        prp25bis = PropertyValue({"prp":'PM25', "truc":12})
        prp25ter = PropertyValue({"prp":'PM25'})
        prp10_20 = PropertyValue.Simple(['PM10', 'PM20'])
        prp10_25 = PropertyValue.Simple(['PM10', 'PM25'])
        self.assertEqual(prp10_20.link(prp10), 'contains')
        self.assertTrue(prp10_20.contains(prp10))
        self.assertEqual(prp10.link(prp10_20), 'within')
        self.assertEqual(prp10_20.link(prp10_25), 'intersects')
        self.assertEqual(prp25.link(prp25bis), 'intersects')
        self.assertEqual(prp25.link(prp25ter), 'within')

    def test_json(self):
        self.assertEqual(ESValue.from_obj(21).json(encoded=False), 21)
        self.assertEqual(ESValue.from_obj('test').json(encoded=False), 'test')
        self.assertEqual(ESValue.from_obj({"truc": 21}).json(encoded=False), {"truc": 21})
        self.assertEqual(ESValue.from_obj({"truc": Ilist3()}).value.__class__.__name__, 'Ilist3')
        #self.assertEqual(ESValue.from_obj(Ilist3()).value.__class__.__name__, 'Ilist3')
        self.assertEqual(ESValue.from_obj('test', 'NamedValue'), NamedValue('test'))
        self.assertEqual(ESValue.from_obj('test', 'LocationValue'), LocationValue(name='test'))
        #self.assertEqual(ESValue.from_obj(Observation()).value.__class__.__name__, 'Observation')
        self.assertEqual(ESValue.from_obj(datetime.datetime(2020,1,1)).json(encoded=False), datetime.datetime(2020, 1, 1, 0, 0))
        self.assertEqual(ESValue.from_obj('{"namvalue":{"val":21}}').json(encoded=False), {"val":21})
        self.assertEqual(ESValue.from_obj('{"locvalue":{"val":[2,1]}}').json(encoded=False), {"val":[2,1]})
        self.assertEqual(ESValue.from_obj({"locvalue":{"val":[2,1]}}).json(encoded=False), {"val":[2,1]})
        self.assertEqual(ESValue.from_obj('{"observation":{"val":21}}').__class__.__name__, 'Observation')
        self.assertEqual(ESValue.from_obj({"observation":{"val":21}}).__class__.__name__, 'Observation')
        self.assertEqual(ESValue.from_obj('{"truc":{"observation":{}}}').json(encoded=False), {"truc":'{"observation": {}}'})
        #self.assertEqual(ESValue.from_obj({"truc": Observation()}).json(encoded=False), {"truc":{"type":"observation"}})
        #self.assertEqual(ESValue.valClassName('{"locvalue":1, "observation":{}}'), 'NamedValue')
        self.assertEqual(ESValue.from_obj({"namvalue":{"val":21}}).json(encoded=False), {"val": 21})
        #self.assertEqual(ESValue.valClassName({"locvalue":1, "observation":{}}), 'NamedValue')

    def test_json_encode(self):
        v = DatationValue.from_obj({"date1": "2021-02-04T12:05:00"})
        encoded    = [True, False]
        format     = ['json', 'cbor']
        test = list(product(encoded, format))
        for ts in test:
            option  = {'encoded': ts[0], 'encode_format': ts[1], 'untyped': True}
            option2 = {'encoded': ts[0], 'encode_format': ts[1], 'untyped': False}
            self.assertTrue(v == ESValue.from_obj(v.json(**option2),'DatationValue'))
            self.assertTrue(v == ESValue.from_obj(v.json(**option)))
        v = LocationValue.from_obj({"loc1": pol2})
        for ts in test:
            option = {'encoded': ts[0], 'encode_format': ts[1], 'untyped': True}
            option2 = {'encoded': ts[0], 'encode_format': ts[1], 'untyped': False}
            self.assertTrue(v == ESValue.from_obj(v.json(**option2),'LocationValue'))
            self.assertTrue(v == ESValue.from_obj(v.json(**option)))
        v = DatationValue.from_obj({"date1": "2021-02-04T12:05:00"})
        self.assertTrue(v == DatationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=True)))
                          == DatationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=False))))
        v = LocationValue.from_obj({"loc1": pol2})
        self.assertTrue(v == LocationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=True)))
                          == LocationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=False))))

    def test_box_bounds(self):
        v = LocationValue.Box(LocationValue.from_obj(pol13))
        self.assertTrue(v.isEqual(v.Box(v.bounds), name=False))
        self.assertTrue(v == v.Box(v.bounds))
        v = DatationValue.Box(DatationValue(travail))
        self.assertTrue(v.isEqual(v.Box(v.bounds), name=False))
        self.assertTrue(v == v.Box(v.bounds))
        l = LocationValue(lyon)
        p = LocationValue(paris)
        self.assertEqual(l.boxUnion(p, 'union').bounds,
                         (min(l.bounds[0], p.bounds[0]), min(l.bounds[1], p.bounds[1]),
                          max(l.bounds[2], p.bounds[2]), max(l.bounds[3], p.bounds[3])))
        l = DatationValue(matin)
        p = DatationValue(aprem)
        self.assertEqual(l.boxUnion(p, 'union').bounds,
                         (min(l.bounds[0], p.bounds[0]), max(l.bounds[1], p.bounds[1])))
        prp10_20 = PropertyValue.Simple(['PM10', 'PM20'])
        prp10_25 = PropertyValue.Simple(['PM10', 'PM25'])
        self.assertEqual(prp10_20.boxUnion(prp10_25).vSimple(), ["PM10", "PM20", "PM25"])

if __name__ == '__main__':
    unittest.main(verbosity=2)
