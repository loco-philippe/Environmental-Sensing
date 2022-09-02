# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `ES.test_esvalue` module contains the unit tests (class unittest) for the
`ESValue` functions.
"""
import unittest, json
from ilist import Ilist
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
from util import util

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
        self.assertEqual(ESValue.valClassName({"truc": Ilist()}), 'ExternValue')
        self.assertEqual(ESValue.valClassName(NamedValue("cou")), 'NamedValue')
        self.assertEqual(ESValue.valClassName(LocationValue(name="cou")), 'LocationValue')
        self.assertEqual(ESValue.valClassName(Ilist()), 'ExternValue')
        #self.assertEqual(ESValue.valClassName(Observation()), 'Observation')
        #self.assertEqual(ESValue.valClassName(datetime.datetime(2020,1,1)), 'datetime')
        self.assertEqual(ESValue.valClassName(datetime.datetime(2020,1,1)), 'DatationValue')
        self.assertEqual(ESValue.valClassName('{"namvalue":{"val":21}}'), 'NamedValue')
        self.assertEqual(ESValue.valClassName('{"locvalue":{"val":21}}'), 'LocationValue')
        self.assertEqual(ESValue.valClassName('{"observation":{"val":21}}'), 'Observation')
        self.assertEqual(ESValue.valClassName('{"truc":{"observation":{}}}'), 'NamedValue')
       # self.assertEqual(ESValue.valClassName('{"locvalue":1, "observation":{}}'), 'NamedValue')
        self.assertEqual(ESValue.valClassName('{"locvalue":1, "observation":{}}'), 'PropertyValue')
        self.assertEqual(ESValue.valClassName({"namvalue":{"val":21}}), 'NamedValue')
        self.assertEqual(ESValue.valClassName({"locvalue":{"val":21}}), 'LocationValue')
        self.assertEqual(ESValue.valClassName({"observation":{"val":21}}), 'Observation')
        #self.assertEqual(ESValue.valClassName({"truc": Observation()}), 'Observation')
        #self.assertEqual(ESValue.valClassName({"locvalue":1, "observation":{}}), 'NamedValue')
        self.assertEqual(ESValue.valClassName({"locvalue":1, "observation":{}}), 'PropertyValue')
        
    def test_NamedValue(self):
        self.assertEqual(NamedValue("coucou").to_obj(), '"coucou"')
        self.assertEqual(NamedValue.from_obj('{"er":2}').json(), '{"er": 2}')
        self.assertEqual(NamedValue.from_obj('{"er":0}').json(), '{"er": 0}')
        self.assertEqual(NamedValue(21).json(), '21')
        self.assertEqual(NamedValue(2.1).json(), '2.1')

    def test_locationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(LocationValue(lyon).json(), json.dumps(lyon))
        self.assertEqual(LocationValue(lyon), LocationValue(LocationValue(lyon)))
        self.assertTrue(LocationValue(lyon) > LocationValue(paris))
        self.assertEqual(LocationValue(pol1).json(), json.dumps(pol1))
        self.assertTrue(LocationValue(paris).value == LocationValue.from_obj({'paris':paris}).value ==
                        LocationValue(name='paris', val=LocationValue._gshape(paris)).value)
        self.assertTrue(LocationValue(name='paris').name == LocationValue.from_obj({'paris':paris}).name ==
                        LocationValue(name='paris', val=LocationValue._gshape(paris)).name)
        self.assertEqual(LocationValue.Box(LocationValue(paris).bounds).bounds,
                         LocationValue.from_obj({'box':paris}).bounds)
        self.assertEqual(LocationValue.from_obj(pol75).name, '75 Paris')
        self.assertEqual(LocationValue(name='pol75').simple, ES.nullCoor)
        self.assertEqual(LocationValue().simple, ES.nullCoor)
        self.assertTrue(LocationValue.from_obj('{"paris":[2,3]}') == LocationValue.from_obj({"paris":[2,3]}))
        


    def test_DatationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(DatationValue(t1), DatationValue(DatationValue(t1)))
        self.assertEqual(DatationValue(t1).to_obj(encoded=False), t1.astimezone(datetime.timezone.utc))
        self.assertTrue(DatationValue(t1) < DatationValue(t2))
        self.assertEqual(DatationValue.from_obj(json.loads(t1n)).json(), t1n)
        self.opt["json_dat_name"] = True
        self.assertEqual(DatationValue.from_obj(json.loads(t1n)).json(), t1n)
        self.assertTrue(DatationValue(t1).value == DatationValue.from_obj({'t1':t1}).value ==
                        DatationValue(name='t1', val=t1).value)
        self.assertTrue(DatationValue(name='t1').name == DatationValue.from_obj({'t1':t1}).name ==
                        DatationValue(name='t1', val=t1).name)
        self.assertEqual(DatationValue(matin).simple,
                        datetime.datetime(2020, 2, 4, 10, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(DatationValue(travail).simple,
                        datetime.datetime(2020, 2, 4, 12, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(DatationValue(pt1).simple, pt1)
        self.assertEqual(DatationValue(tnull).simple, tnull)
        self.assertEqual(DatationValue.from_obj(t1n).json(), t1n)
        self.assertEqual(DatationValue(name='t1n').name, 't1n')


    def test_propertyValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(PropertyValue().json(), '{}')
        self.assertEqual(PropertyValue({ES.prp_type : "PM25"}, prp_dict=True).json(),
                         '{"'+ES.prp_type+'": "PM25", "unit": "kg/m3"}')
        self.assertEqual(PropertyValue({ES.prp_type : "PM25"}).json(),
                         '{"'+ES.prp_type+'": "PM25"}')
        self.assertEqual(PropertyValue(pprop_pm10).json(), json.dumps(pprop_pm10))
        self.assertTrue(PropertyValue(prop_pm25).simple == 'PM25' == 
                        PropertyValue(pprop_pm25).simple)
        self.assertEqual(PropertyValue({'truc':2}).json(), '{"truc": 2}')
        self.assertEqual(PropertyValue({'machin':{'truc':2}}).json(), '{"machin": {"truc": 2}}')
        self.assertEqual(PropertyValue('truc').name, 'truc')
        self.assertEqual(PropertyValue(PropertyValue.nullValue()), PropertyValue())

    def test_externValue(self):
        il=Ilist()
        self.assertTrue(ExternValue.from_obj({'truc':il}).value == il == 
                        ExternValue(il).value == 
                        ExternValue.from_obj({'ilist':{'truc':il}}).value ==
                        ExternValue.from_obj(json.dumps({"ilist":{"truc":il.json()}})).value)
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
        self.assertEqual(PropertyValue(pprop_pm25).json(), json.dumps(pprop_pm25))
        self.assertEqual(PropertyValue('test').json(), '"test"')
        self.opt["json_loc_name"] = True
        self.assertEqual(LocationValue(lyon).json(), json.dumps(lyon))
        self.assertEqual(LocationValue(name='test').json(), '"test"')

    def test_setValue_setName(self):
        val = LocationValue(lyon)
        val.setValue(LocationValue([4,5]))
        self.assertEqual(val.vSimple(), [4,5])
        val.setValue(LocationValue([[6,7], [7,8], [8,6]]))
        self.assertEqual(val.value, LocationValue._gshape([[6,7], [7,8], [8,6]]))
        val.setValue(LocationValue([[[6,7], [7,8], [8,6]]]))
        self.assertEqual(val.value, LocationValue._gshape([[[6,7], [7,8], [8,6]]]))
        val.setName('truc')
        self.assertEqual(val.name, 'truc')
        val = DatationValue(t1)
        val.setValue(t2)
        self.assertEqual(val.simple, t2)
        val.setValue(DatationValue(s1))
        self.assertEqual(val.vInterval(encoded=False), s1)
        val.setName('truc')
        self.assertEqual(val.name, 'truc')

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

    def test_cast(self):
        data=[[ESValue.from_obj({'pos':[1.2, 3.4]}, 'LocationValue'), [1.2, 3.4], {'pos':[1.2, 3.4]}],
              [ESValue.from_obj({'datvalue':'date1'}), 
               datetime.datetime(1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'date1'],
              [{'pos': [1.2, 3.4]}, {'pos': [1.2, 3.4]}, {'pos': [1.2, 3.4]}], 
              [[1.2, 3.4], [1.2, 3.4], [1.2, 3.4]],
              [{'tes':3, 'tr':1}, {'tes':3, 'tr':1}, {'tes':3, 'tr':1}]]             
        for dat in data:
            self.assertEqual(util.cast(dat[0], 'obj'),    dat[2])
            self.assertEqual(util.cast(dat[0], 'simple', string=False), dat[1])
        #data = [[{'pos':[1.2, 3.4]},                        'NamedValue'],
        data = [[{'pos':[1.2, 3.4]},                        'str'],
                [{'datvalue': datetime.datetime(2020,1,1)}, 'DatationValue'],
                [{'truc': 25, 'dict':[1,2]},                'str'],
                #[{'truc': 25, 'dict':[1,2]},                'PropertyValue'],
                [21,                                        'int'],
                #[21,                                        'NamedValue'],
                [datetime.datetime(2020,1,1),               'datetime'],
                ['2021-01-01',                              'datetime'],
                #[datetime.datetime(2020,1,1),               'DatationValue'],
                #['2021-01-01',                              'DatationValue'],
                ['{"namvalue":{"val":21}}',                 'NamedValue'],
                ['{"locvalue":{"val":[2,1]}}',              'LocationValue'],
                #['{"observation":{"val":21}}',              'Observation'],
                ['{"truc":{"observation":{}}}',             'str'],
                #['{"truc":{"observation":{}}}',             'NamedValue'],
                ['{"locvalue":1, "observation":{}}',        'str'],
                #['{"locvalue":1, "observation":{}}',        'PropertyValue'],
                [{"iindex": ["simple", [{"truc": 25}, 21]]},'Iindex']
                ]     
        for dat in data: 
            #print(dat[0])
            self.assertEqual(util.castval(dat[0]).__class__.__name__, dat[1])

    def test_json(self):
        self.assertEqual(ESValue.from_obj(21, simple=False).json(encoded=False), 21)
        self.assertEqual(ESValue.from_obj('test', simple=False).json(encoded=False), 'test')
        self.assertEqual(ESValue.from_obj({"truc": 21}, simple=False).json(encoded=False), {"truc": 21})
        self.assertEqual(ESValue.from_obj({"truc": Ilist()}, simple=False).value.__class__.__name__, 'Ilist')
        #self.assertEqual(ESValue.from_obj(Ilist()).value.__class__.__name__, 'Ilist')
        self.assertEqual(ESValue.from_obj('test', 'NamedValue'), NamedValue('test'))
        self.assertEqual(ESValue.from_obj('test', 'LocationValue'), LocationValue(name='test'))
        #self.assertEqual(ESValue.from_obj(Observation()).value.__class__.__name__, 'Observation')
        #self.assertEqual(ESValue.from_obj(datetime.datetime(2020,1,1)).json(encoded=False), datetime.datetime(2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(ESValue.from_obj('{"namvalue":{"val":21}}').json(encoded=False), {"val":21})
        self.assertEqual(ESValue.from_obj('{"locvalue":{"val":[2,1]}}').json(encoded=False), {"val":[2,1]})
        self.assertEqual(ESValue.from_obj({"locvalue":{"val":[2,1]}}).json(encoded=False), {"val":[2,1]})
        self.assertEqual(ESValue.from_obj('{"observation":{"val":21}}').__class__.__name__, 'Observation')
        self.assertEqual(ESValue.from_obj({"observation":{"val":21}}).__class__.__name__, 'Observation')
        #self.assertEqual(ESValue.from_obj('{"truc":{"observation":{}}}').json(encoded=False), {"truc":'{"observation": {}}'})
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
        #self.assertTrue(v == DatationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=True)))
        #                  == DatationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=False))))
        v = LocationValue.from_obj({"loc1": pol2})
        #self.assertTrue(v == LocationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=True)))
        #                  == LocationValue.from_obj(ESValue.__from_bytes__(v.__to_bytes__(encoded=False))))

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
