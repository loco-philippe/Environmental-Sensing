# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `ES.EStestunitaire` module contains the unit tests (class unittest) for all the 
Environmental Sensing functions.
"""
import unittest

from ESElement import ESElement
from ESValue import ResultValue, LocationValue, DatationValue, \
    PropertyValue #, _gshape #, ESSet
from ESSet import ESSet
from ESObservation import Observation
from ESObs import ESSetDatation, ESSetProperty, ESSetResult, ESSetLocation
from ESSlot import TimeSlot
from ESconstante import ES
from pprint import pprint
import json, copy #, shapely
import requests as rq
from datetime import datetime

# couverture tests (True if non passed)----------------------------------------
simple  = False  # False
plot    = True  # True
mongo   = True  # True

# datas-----------------------------------------------------------------------
def _val(n): return list(i for i in range(n))
def _res(n): return (ES.res_valName, _val(n))
with open('C:\\Users\\a179227\\OneDrive - Alliance\\perso Wx\\ES standard\\python ESstandard\\departements-version-simplifiee.geojson') as f: 
    dp = f.read()
dpt = json.loads(dp)['features']
#https://github.com/gregoiredavid/france-geojson
#pol13 = dpt['features'][12]['geometry']['coordinates']
#pol69 = dpt['features'][69]['geometry']['coordinates']
#pol75 = dpt['features'][75]['geometry']['coordinates']
pol13 = {dpt[12]['properties']['code'] + ' ' + dpt[12]['properties']['nom'] : 
         dpt[12]['geometry']['coordinates']}
pol69 = {dpt[69]['properties']['code'] + ' ' + dpt[69]['properties']['nom'] : 
         dpt[69]['geometry']['coordinates']}
pol75 = {dpt[75]['properties']['code'] + ' ' + dpt[75]['properties']['nom'] : 
         dpt[75]['geometry']['coordinates']}
pol1 = [[[0.0,1.0], [1.0,2.0], [1.0,1.0], [0.0,1.0]]]
pol1centre = [0.6666666666666666, 1.3333333333333333]
pol2 = [[[0.0,2.0], [2.0,2.0], [1.0,1.0], [0.0,2.0]]]
dpt2 = (ES.loc_valName, [pol1, pol2])
dpt3 = (ES.loc_valName, [pol75, pol69, pol13])
pparis       = [2.4, 48.9]
plyon        = [4.8, 45.8]
pmarseille   = [5.4, 43.3]
paris       = [2.35, 48.87]
parisn      = json.dumps({'loca1' : paris})
lyon        = [4.83, 45.76]
marseille   = [5.38, 43.3]
mini_PL     = [2.35, 45.76]
maxi_PLM    = [5.38, 48.87]
obs_1       = (ES.type, ES.obs_classES)
truc_mach   = ("truc", "machin")
prop_pm25   = dict([(ES.prp_propType,"PM25"), (ES.prp_unit, "kg/m3")])
prop_pm10   = dict([(ES.prp_propType,"PM10"), (ES.prp_unit, "kg/m3")])
prop_co2    = dict([(ES.prp_propType,"CO2"), (ES.prp_unit, "kg/m3")])
pprop_pm25   = dict([(ES.prp_propType,"PM25"), (ES.prp_unit, "kg/m3"), (ES.prp_appli, "air")])
pprop_pm10   = dict([(ES.prp_propType,"PM10"), (ES.prp_unit, "kg/m3"), (ES.prp_appli, "air"), ("truc", "machin")])
matin = [ datetime(2020, 2, 4, 8), datetime(2020, 2, 4, 12)]
midi  = [ datetime(2020, 2, 4, 12), datetime(2020, 2, 4, 14)]
aprem  = [ datetime(2020, 2, 4, 14), datetime(2020, 2, 4, 18)]
travail = [matin, aprem]
pt1 = datetime(2020, 2, 4, 12, 5, 0)
pt2 = datetime(2020, 5, 4, 12, 5, 0)
pt3 = datetime(2020, 7, 4, 12, 5, 0)
tnull = datetime(1970, 1, 1, 0, 0, 0)
snull = (tnull.isoformat(), tnull.isoformat())
t1 = datetime(2021, 2, 4, 12, 5, 0)
t1n = json.dumps({'date1' : t1.isoformat()})
t2 = datetime(2021, 7, 4, 12, 5, 0)
t3 = datetime(2021, 5, 4, 12, 5, 0)
r1 = ResultValue('{"er":2}')
r2 = ResultValue([23, [1, 2, -1]])
r3 = ResultValue(["coucou", [1, 2, -1]])
r4 = ResultValue(41.2)
r5 = ResultValue(18)
r6 = ResultValue([41, [2, 2, 0]])
r7 = ResultValue([18, [1, 2, 1]])
s1 = [t1, t2]
#ndat1 = (ES.dat_valName[2], "date1")
#ndat2 = (ES.dat_valName[2], ["1date1", "2date2"])
#ndat3 = (ES.dat_valName[2], ["1date1", "2date2", "3date3"])
dat1 = (ES.dat_valName, {'date1' : t1.isoformat()})
dat2 = (ES.dat_valName, [t1.isoformat(), t2.isoformat()])
dat3 = (ES.dat_valName, [{'date1' : t1.isoformat()}, t2.isoformat(), t3.isoformat()])
dat3ord = (ES.dat_valName, [{'date1' : t1.isoformat()}, t3.isoformat(), t2.isoformat()])
dat3sn = (ES.dat_valName, [t1.isoformat(), t2.isoformat(), t3.isoformat()])
pdat3 = (ES.dat_valName, [pt1.isoformat(), pt2.isoformat(), pt3.isoformat()])
prop1 = (ES.prp_valName, prop_pm10)
prop2 = (ES.prp_valName, [prop_pm25, prop_pm10])
prop2ord = (ES.prp_valName, [prop_pm10, prop_pm25])
prop3 = (ES.prp_valName, [prop_pm25, prop_pm10, prop_co2])
pprop2 = (ES.prp_valName, [pprop_pm25, pprop_pm10])
loc1 = (ES.loc_valName, {'paris' : paris})
loc1sn = (ES.loc_valName, paris)
loc2 = (ES.loc_valName, [paris, lyon])
loc3 = (ES.loc_valName, [{'paris' : paris}, lyon, marseille])
loc3sn = (ES.loc_valName, [paris, lyon, marseille])
ploc3 = (ES.loc_valName, [pparis, plyon, pmarseille])
res2 = (ES.res_valName, [[41, [2, 2, 0]], [18, [1, 2, 1]]])

def _option_simple(ob1):
    ob1.option["json_ESobs_class"] = False
    ob1.option["json_prp_type"] = False
    ob1.option["json_param"] = True
    ob1.option["json_elt_type"] = False
    ob1.option["json_obs_val"] = True
    ob1.option["json_obs_attrib"] = False
    ob1.option["json_res_index"] = False
    ob1.option["json_info_type"] = False
    ob1.option["json_info_nval"] = False
    ob1.option["json_info_autre"] = False
    ob1.option["json_info_box"] = False
    ob1.option["json_info_res_classES"] = False

def _majType_avec_option(ob1, maj_index):
    ob1.majType()
 
def _envoi_mongo(ob):
    url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
    r = rq.post(url, data=ob.to_json())  
    print("réponse : ", r.text, "\n")
    return r.status_code

class TestExemples(unittest.TestCase):      # !!! exemples
    def test_first_observation(self) :
        # cas simple + présentation
        ob=Observation(('morning', 'paris', ' Temp', 'high'))
        ob.append('morning', 'lyon', ' Temp', 'low')
        ob.append('morning', 'marseille', ' Temp', 'very high')
        ob.view(True, False, False, False)
        ob.voxel()
        ob.majList(ResultValue, [25, 10, 35]) 
        ob.plot()
        # valeur numériques + choropleth
        print(ob.setLocation)
        ob.majList(LocationValue, [lyon, marseille, paris])
        ob.view(True, False, True, False)
        choro = ob.choropleth()
        choro.save("test.html")
        print(ob.setLocation)
        ob.majList(LocationValue, [pol75, pol69, pol13])
        ob.view(True, False, True, False)
        choro = ob.choropleth()
        choro.save("test.html")
        # ajout dimension 2, infos globales
        ob.append('morning', 'paris', 'Humidity', 30, equal='name')
        ob.append('morning', 'marseille', 'Humidity', '60', equal='name')
        ob.view(True, False, False, False)
        ob.voxel()
        ob.plot()
        # ajout dimension 3 + export dataarray, dataframe
        ob.append('afternoon', 'paris', ' Temp', 28, equal='name')
        ob.append('afternoon', 'lyon', ' Temp', 15, equal='name')
        ob.majList(LocationValue, [lyon, marseille, paris])   # i.e. paris = [2.35, 48.87]
        print(ob.setDatation)
        ob.majList(DatationValue, ["2021-05-05T10", "2021-05-05T16"])
        ob.view(prp=False, width=15)
        ob.voxel()
        ob.plot()       
        print(ob.to_xarray(numeric=True))
        pprint(json.loads(ob.json), indent=2)
        ob._info(string=False)

@unittest.skipIf(simple, "test unitaire")
class TestObsUnitaire(unittest.TestCase):
    '''Unit tests for `ES.ESValue`, `ES.ESObs`, `ES.ESElement` '''
    opt = ES.mOption.copy()

    def test_TimeSlot(self):
        s1 = TimeSlot(datetime(2001, 2, 3))
        s = TimeSlot('"2001-02-03T00:00:00"')
        self.assertTrue(s==s1)
        s = TimeSlot([datetime(2001, 2, 3), datetime(2001, 2, 1)])
        s1 = TimeSlot(['2001-02-03T00:00:00', datetime(2001, 2, 1)])
        s2 = TimeSlot('["2001-02-03T00:00:00","2001-02-01T00:00:00"]')
        self.assertTrue(s==s1==s2)
        s = TimeSlot('[["2001-02-03T00:00:00","2001-02-01T00:00:00"], ["2001-02-05T00:00:00","2001-02-06T00:00:00"]]')
        self.assertTrue(s.type == 'slot')
        self.assertTrue(TimeSlot([matin, aprem]).instant == TimeSlot(midi).instant)
        self.assertTrue(TimeSlot([matin, aprem]).bounds == TimeSlot([matin, midi, aprem]).bounds)
        
    def test_ResultValue(self):
        self.opt["json_res_index"] = True
        self.assertEqual(ResultValue("coucou").json(self.opt), '["coucou", [-1, -1, -1]]')
        self.assertEqual(ResultValue(["coucou", [1, 2, -1]]).json(self.opt), '["coucou", [1, 2, -1]]')
        self.assertEqual(ResultValue("coucou", [1, 2, -1]).json(self.opt), '["coucou", [1, 2, -1]]')
        self.assertEqual(ResultValue('{"er":2}', [1, 2, -1]).json(self.opt), '[{"er": 2}, [1, 2, -1]]')
        #self.assertEqual(ResultValue('{"er":2}', [1, 2, -1]), ResultValue(ResultValue('{"er":2}', [1, 2, -1])))
        self.assertEqual(ResultValue('{"er":2}').json(self.opt), '[{"er": 2}, [-1, -1, -1]]')
        self.assertEqual(ResultValue('[3,2]', [1, 2, -1]).json(self.opt), '["[3, 2]", [1, 2, -1]]') 
        self.assertEqual(ResultValue('[3,2]').json(self.opt), '["[3, 2]", [-1, -1, -1]]')
        self.assertEqual(ResultValue(21).json(self.opt), '[21, [-1, -1, -1]]')
        self.assertEqual(ResultValue([23, [1, 2, -1]]).json(self.opt), '[23, [1, 2, -1]]')
        self.assertEqual(ResultValue(23, [1, 2, -1]).json(self.opt), '[23, [1, 2, -1]]')
        self.assertEqual(ResultValue(2.1).json(self.opt), '[2.1, [-1, -1, -1]]')
        self.assertEqual(ResultValue([2.3, [1, 2, -1]]).json(self.opt), '[2.3, [1, 2, -1]]') 
        self.opt["json_res_index"] = False
        self.assertEqual(ResultValue("coucou").json(self.opt), '"coucou"')
        self.assertEqual(ResultValue(["coucou", [1, 2, -1]]).json(self.opt), '"coucou"')
        self.assertEqual(ResultValue('{"er":2}').json(self.opt), '{"er": 2}')
        self.assertEqual(ResultValue('[{"er":2}, [1, 2, -1]]').json(self.opt), '{"er": 2}')
        self.assertEqual(ResultValue(22).json(self.opt), '22')
        self.assertEqual(ResultValue([23, [1, 2, -1]]).json(self.opt), '23')
        self.assertEqual(ResultValue(2.2).json(self.opt), '2.2')
        self.assertEqual(ResultValue([2.3, [1, 2, -1]]).json(self.opt), '2.3')
        self.opt["json_res_index"] = True

    def test_locationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(LocationValue(lyon).json(self.opt), json.dumps(lyon)) 
        self.assertEqual(LocationValue(lyon), LocationValue(LocationValue(lyon)))
        self.assertTrue(LocationValue(lyon) > LocationValue(paris))
        self.assertEqual(LocationValue(pol1).json(self.opt), json.dumps(pol1centre)) 
        self.opt["json_loc_point"]=False 
        self.assertTrue(LocationValue(paris).shap == LocationValue({'paris':paris}).shap ==
                        LocationValue(name='paris', shape=LocationValue._gshape(paris)).shap)
        self.assertTrue(LocationValue('paris').name == LocationValue({'paris':paris}).name ==
                        LocationValue(name='paris', shape=LocationValue._gshape(paris)).name)
        #self.assertEqual(LocationValue(pol1).json(self.opt), json.dumps(pol1)) # !!! à traiter point / polygon
        self.assertEqual(LocationValue.Cuboid(*LocationValue(paris).bounds).bounds, 
                         LocationValue({'box':paris}).bounds)
    def test_DatationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(DatationValue(t1), DatationValue(DatationValue(t1)))
        self.assertEqual(DatationValue(t1).json(string=False), t1.isoformat()) 
        self.assertTrue(DatationValue(t1) < DatationValue(t2))
        self.assertEqual(DatationValue(json.loads(t1n)).json(), t1n)
        self.opt["json_dat_name"] = True
        self.opt["json_dat_instant"] = True
        self.assertEqual(DatationValue(json.loads(t1n)).json(self.opt), t1n) 
        self.assertTrue(DatationValue(t1).slot == DatationValue({'t1':t1}).slot ==
                        DatationValue(name='t1', slot=t1).slot)
        self.assertTrue(DatationValue('t1').name == DatationValue({'t1':t1}).name ==
                        DatationValue(name='t1', slot=t1).name)
        
    def test_propertyValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(PropertyValue().json(self.opt), '{}') 
        self.opt["json_prp_type"] = False
        self.assertEqual(PropertyValue({ES.prp_propType : "PM25"}).json(self.opt), 
                         '{"'+ES.prp_propType+'": "PM25", "unit": "kg/m3"}')
        self.assertEqual(PropertyValue(pprop_pm10).json(self.opt), json.dumps(pprop_pm10))
        #self.opt["json_prp_type"] = True
        #self.assertEqual(PropertyValue(pprop_pm10).json(self.opt), 
        #                 json.dumps({list(pprop_pm10.keys())[0]: list(pprop_pm10.values())[0]}))
        
    def test_nameValue(self):
        self.assertEqual(DatationValue('recre').json(string=False), 'recre') 
        #self.opt["json_dat_instant"] = False
        #self.opt["json_dat_name"] = False
        #self.assertEqual(DatationValue('recre').json(self.opt), tnull.isoformat())
        self.opt["json_prp_type"] = False
        self.opt["json_prp_name"] = True
        self.assertEqual(PropertyValue(pprop_pm25).json(self.opt), json.dumps(pprop_pm25))
        self.assertEqual(PropertyValue('test').json(self.opt), '"test"')
        self.opt["json_loc_name"] = True
        self.assertEqual(LocationValue(lyon).json(self.opt), json.dumps(lyon))
        self.assertEqual(LocationValue('test').json(self.opt), '"test"')
        #ob1 = Observation(json.dumps(dict((obs_1, truc_mach, ndat3, loc3, prop2, _res(9)))))
        #_option_simple(ob1)
        #ob1.option["json_loc_name"] = True
        #self.assertEqual(['loc0', 'loc1', 'loc2'], json.loads(ob1.to_json())[ES.loc_valName[2]])
        
    def test_setValue_setName(self):
        val = LocationValue(lyon)
        val.setValue(LocationValue([4,5]))
        self.assertEqual(val.vPoint(), [4,5])
        val.setValue(LocationValue([[6,7], [7,8], [8,6]]))
        self.assertEqual(val.shap, LocationValue._gshape([[6,7], [7,8], [8,6]]))
        val.setName('truc')
        self.assertEqual(val.name, 'truc')     
        val = DatationValue(t1)
        val.setValue(t2)
        self.assertEqual(val.instant, t2)
        val.setValue(DatationValue(s1))
        self.assertEqual(val.vInterval(False), s1)
        val.setName('truc')
        self.assertEqual(val.name, 'truc')
    
    def test_ESSet_box(self):
        self.assertEqual(ESSet(PropertyValue, [prop_pm10, prop_pm25]).jsonSet(self.opt), json.dumps([prop_pm10, prop_pm25])) 
        self.assertEqual(ESSetLocation(paris).boundingBox().bounds, (paris[0], paris[1], paris[0], paris[1]))
        self.assertEqual(ESSetLocation([paris, lyon, marseille]).boundingBox().bounds,
                         (paris[0], marseille[1], marseille[0], paris[1]))
        self.assertEqual(ESSetDatation([t1, t2, t3]).boundingBox().bounds, (t1.isoformat(), t2.isoformat()))
        self.assertEqual(ESSetDatation(t1).boundingBox().bounds, (t1.isoformat(), t1.isoformat()))
        
    def test_ESSetLocation(self):
        da = ESSetLocation(pObs=Observation(), jObj={ES.loc_valName:[paris, lyon, marseille]})
        da = ESSetLocation({ES.loc_classES:{ES.loc_valName:[paris, lyon, marseille], 'truc':'machin'}})
        self.assertEqual(da.mAtt['truc'], 'machin') 
        self.assertEqual(ESSetLocation([paris])[0].vPoint(), paris)
        self.assertEqual(ESSetLocation([paris, lyon])[1].vPoint(), lyon)
        self.assertEqual(ESSetLocation([[paris, lyon]])[0].shap.type, 'MultiPoint')
        self.assertEqual(ESSetLocation([[[paris, lyon, marseille, paris]]])[0].shap.type, 'Polygon')
    
    def test_ESSetDatation(self):
        #da1 = ESSetDatation(pObs=Observation(), jObj={ES.dat_valName:[t1, t2, t3]})
        self.assertEqual(ESSetDatation([t1])[0].instant, t1)
        self.assertEqual(ESSetDatation([t1, t2])[1].instant, t2)
        self.assertEqual(ESSetDatation([[t1, t2]])[0].vInterval(False)[1], t2)
        self.assertEqual(ESSetDatation([[t1, t2]])[0].slot.slot[0][1], t2)

    def test_ESSetResult(self):
        da3 = ESSetResult(pObs=Observation(), jObj={ES.res_valName:[r2, r2]})
        self.assertEqual(json.loads('{'+da3.json(self.opt)+'}')[ES.res_valName], r2.value)
        self.assertEqual(ESSetResult([r2])[0].value, r2.value)
        self.assertEqual(ESSetResult([r2, 25])[1].value, 25)
        self.assertEqual(ESSetResult(['name', 25])[0].value, 'name')

    def test_ESObs(self):
        da2 = ESSetProperty(pObs=Observation(), jObj={ES.prp_valName:[prop_pm10, prop_pm25], ES.prp_upperValue :'254'})
        self.opt["json_prp_type"] = False
        self.assertEqual(json.loads('{'+da2.json(self.opt)+'}')[ES.prp_valName], [prop_pm10, prop_pm25]) 
        self.assertEqual(da2.mAtt[ES.prp_upperValue], '254') 
        
    def test_ESElement(self):
        el = ESElement()
        el2 = ESElement()
        el2.setAtt('tric', 'meoc')
        el.setAtt('truc', 'mec')
        el.addComposant(el2)
        self.assertTrue(el.element('tric') == None)
        self.assertFalse(el.element('null') == None)

@unittest.skipIf(simple, "test observation")
class TestBytes(unittest.TestCase):
    '''Unit tests for bytes conversion '''
    
    def test_location_bytes(self):
        d5 = ESSetLocation(pObs=Observation(), jObj={ES.loc_valName:["paris", "lyon", "marseille"]})
        d4 = ESSetLocation(pObs=Observation())
        d4.from_bytes(d5.to_bytes(True))
        self.assertEqual(d4.valueList[2].name, "marseille")
        d5 = ESSetLocation(pObs=Observation(), jObj={ES.loc_valName:[paris, lyon, marseille]})
        d4 = ESSetLocation(pObs=Observation())
        d4.from_bytes(d5.to_bytes())
        self.assertEqual(d4.valueList[2].vPoint()[0], marseille[0])

    def test_datation_bytes(self):
        d5 = ESSetDatation(pObs=Observation(), jObj={ES.dat_valName:["t1", "t2", "t3"]})
        d4 = ESSetDatation(pObs=Observation())
        d4.from_bytes(d5.to_bytes(True))
        self.assertEqual(d4.valueList[2].name, "t3")
        d5 = ESSetDatation(pObs=Observation(), jObj={ES.dat_valName:[t1, t2, t3]})
        d4 = ESSetDatation(pObs=Observation())
        d4.from_bytes(d5.to_bytes())
        self.assertEqual(d4.valueList[2].instant, t3)
        
    def test_property_bytes(self):
        da2 = ESSetProperty(pObs=Observation(), jObj={ES.prp_valName:[pprop_pm10, pprop_pm25]})
        da1 = ESSetProperty(pObs=Observation())
        da1.from_bytes(da2.to_bytes())
        self.assertEqual(da1.valueList[1].application, pprop_pm25[ES.prp_appli])

    def test_result_bytes(self):
        da3 = ESSetResult(pObs=Observation(), jObj={ES.res_valName:[r4, r5]})
        da2 = ESSetResult(pObs=Observation())
        da2.from_bytes(da3.to_bytes())
        self.assertEqual(da2.valueList[1].value, r5.value)
        da3 = ESSetResult(pObs=Observation(), jObj={ES.res_valName:[r6, r7]})
        da2 = ESSetResult(pObs=Observation())
        da2.from_bytes(da3.to_bytes(False, True))
        self.assertEqual(da2.valueList[0].value, r6.value)
        self.assertEqual(da2.valueList[0].ind, r6.ind)
        self.assertEqual(da2.valueList[1].value, r7.value)
        self.assertEqual(da2.valueList[1].ind, r7.ind)
        #ob2.option["json_res_index"]=True
        da2 = ESSetResult(pObs=Observation())
        da2.from_bytes(da3.to_bytes(False, True, ES.nullDict, ['CO2', 'CO2']), ['CO2', 'CO2'])
        self.assertEqual(da2.valueList[1].value, r7.value)
        da2 = ESSetResult(pObs=Observation())
        da2.from_bytes(da3.to_bytes(False, True, ES.nullDict, ['CO2','PM25']), ['CO2','PM25'])
        self.assertEqual(round(da2.valueList[1].value, 1), round(r7.value, 1))
        da2 = ESSetResult(pObs=Observation())
        da2.from_bytes(da3.to_bytes(False, False, ES.nullDict, ['CO2','PM25']), ['CO2','PM25'])
        self.assertEqual(round(da2.valueList[1].value, 1), round(r7.value, 1))
        
    def test_observation_bytes(self):
        ob1 = Observation(json.dumps(dict((obs_1, dat1, loc1, prop2, _res(2)))))
        ob2 = Observation()
        ob2.from_bytes(ob1.to_bytes())
        ob2.majType()
        self.assertEqual(ob1.to_bytes(), ob2.to_bytes())
        ob1 = Observation(json.dumps(dict((obs_1, dat1, loc1, prop1, _res(1)))))
        ob2 = Observation()
        ob2.from_bytes(ob1.to_bytes())
        ob2.majType()
        self.assertEqual(ob1.to_bytes(), ob2.to_bytes())
        ob1 = Observation(json.dumps(dict((obs_1, dat3, loc3, prop2, res2))))
        ob2 = Observation()
        ob2.from_bytes(ob1.to_bytes())
        ob2.majType()
        self.assertEqual(ob1.to_bytes(), ob2.to_bytes())
        ob2 = Observation()
        ob1.mAtt[ES.obs_reference] = 25
        ob1.option['bytes__resformat'] = ob2.option['bytes__resformat'] = 'uint32'
        ob2.from_bytes(ob1.to_bytes())
        ob2.majType()
        self.assertEqual(ob1.to_bytes(), ob2.to_bytes())
        self.assertEqual(ob1.mAtt[ES.obs_reference], ob2.mAtt[ES.obs_reference])

@unittest.skipIf(simple, "test observation")
class TestObservation(unittest.TestCase):           # !!! test observation
    '''Unit tests for `ES.ESObservation.Observation` '''

    def test_obs_creation(self):
        obs1 = Observation()
        self.assertEqual(obs1.classES,                   ES.obs_classES)
        self.assertEqual(ESSetDatation(pObs=obs1).classES,    ES.dat_classES)
        self.assertEqual(ESSetResult(pObs=obs1).classES,      ES.res_classES)
        self.assertEqual(ESSetProperty(pObs=obs1).classES,    ES.prp_classES)
        self.assertEqual(ESSetLocation(pObs=obs1).classES,    ES.loc_classES)
      
        ob = Observation(json.dumps(dict([obs_1, _res(9)])))
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName], _val(9))

        ob  = Observation(dict((obs_1, dat1, loc1, prop3, _res(3))), order='ldp')        
        ob1 = Observation(dict((dat1, loc1, prop3, _res(3))), order='ldp')    
        ob2 = Observation({dat1[0] : dat1[1]}, {loc1[0]:loc1[1]}, {prop3[0]:prop3[1]}, 
                          {_res(3)[0]:_res(3)[1]}, order='ldp')
        ob3 = Observation(datation={dat1[0] : dat1[1]}, location={loc1[0]:loc1[1]}, 
                          property={prop3[0]:prop3[1]}, result={_res(3)[0]:_res(3)[1]}, 
                          order='ldp')
        ob4 = Observation(datation=ESSetDatation({dat1[0] : dat1[1]}), 
                          location=ESSetLocation({loc1[0]:loc1[1]}), 
                          property=ESSetProperty({prop3[0]:prop3[1]}), 
                          result=ESSetResult({_res(3)[0]:_res(3)[1]}), order='ldp')
        ob5 = Observation([[dat1[1]], [loc1[1]], prop3[1], _res(3)[1]], order='ldp')
        ob6 = Observation(datation=[dat1[1]], location=[loc1[1]], 
                          property=prop3[1], result=_res(3)[1], order='ldp')
        ob7 = Observation([[dat1[1]], [loc1[1]], prop3[1], _res(3)[1]], order='ldp', datation=[dat1[1]])
        ob8 = Observation({dat1[0] : dat1[1]}, {loc1[0]:loc1[1]}, {prop3[0]:prop3[1]}, 
                          {_res(3)[0]:_res(3)[1]}, location=loc2[1], order='ldp')   
        self.assertTrue(ob.json  == ob1.json == ob2.json == ob3.json == ob4.json ==
                        ob5.json == ob6.json == ob7.json == ob8.json)
        ob  = Observation()
        ob1 = Observation({})
        ob2 = Observation([])
        self.assertTrue(ob.to_json()==ob1.to_json()==ob2.to_json())
        ob=Observation(('ce matin', 'paris', 'pm10', 'fort'))
        ob1=Observation()
        ob1.append('ce matin', 'paris', 'pm10', 'fort')
        ob2=Observation(datation=['ce matin'], location=['paris'], property=['pm10'], result=['fort'])
        self.assertTrue(ob.to_json()==ob1.to_json()==ob2.to_json())
        
    def test_obs_loc_iloc_maj(self):
        ob = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6))))
        self.assertEqual(ob.iLoc(1,1,1), ob.loc(dat3[1][1], loc3[1][1], prop2[1][1]))
        ob.majValue(LocationValue(loc3[1][1]), loc3[1][2])
        self.assertEqual(ob.setLocation[1], ob.setLocation[2])
        self.assertEqual(ob.indexLoc(ResultValue(5), string=False)["full"], 5)
        self.assertEqual(ob.indexLoc(DatationValue("2021-02-04T12:05:00"), string=False)["value"], 0)
        self.assertEqual(ob.indexLoc(LocationValue("paris"), string=False)["name"], 0)
        
    def test_obs_vList(self):
        ob1 = Observation(dict((truc_mach, dat3, loc3)))
        self.assertEqual(ob1.setDatation.vListName[0], 'date1')
        self.assertEqual(ob1.setDatation.vListName[1], 'dat1')
        self.assertEqual(ob1.setLocation.vListPoint, [paris, lyon, marseille])
        self.assertEqual(ob1.setDatation.vListInstant, [t1, t2, t3])
        ob1 = Observation(dict((truc_mach, dat3, dpt2)))
        self.assertEqual(ob1.setLocation.vListPoint[0], pol1centre)

    def test_obs_simple(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3))))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3)),    json.loads(ob1.to_json()))
        ob1 = Observation(dict((obs_1, truc_mach, loc3)))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, loc3)),    json.loads(ob1.to_json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, prop2))))
        _option_simple(ob1)
        ob1.option["json_prp_type"] = False
        self.assertEqual(dict((obs_1, truc_mach, prop2)),    json.loads(ob1.to_json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, _res(9)))))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, _res(9))),    json.loads(ob1.to_json()))
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(9))))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(9))),json.loads(ob1.to_json()))
        
    def test_obs_att(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, 
                                           (ES.obs_reference, 25), (ES.prp_upperValue,'254'),
                                           _res(9)))))
        self.assertEqual(ob1.mAtt['truc'], 'machin')
        self.assertEqual(ob1.mAtt[ES.obs_reference], 25)
        self.assertEqual(ob1.setProperty.mAtt[ES.prp_upperValue], '254')

    def test_obs_options(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(9)))))
        _option_simple(ob1)
        ob1.option["json_res_index"] = True
        self.assertEqual(json.loads(ob1.to_json())[ES.res_valName][0], [_val(9)[0], ES.nullInd])
        ob1.option["json_ESobs_class"] = True
        self.assertTrue(ES.dat_classES in json.loads(ob1.to_json()))
        self.assertTrue(ES.res_classES in json.loads(ob1.to_json()))
        self.assertTrue(ES.loc_classES in json.loads(ob1.to_json()))
        self.assertTrue(ES.prp_classES in json.loads(ob1.to_json()))
        ob1.option["json_elt_type"] = True
        self.assertTrue(ES.type + ES.dat_classES in json.loads(ob1.to_json())[ES.dat_classES])
        self.assertTrue(ES.type + ES.res_classES in json.loads(ob1.to_json())[ES.res_classES])
        self.assertTrue(ES.type + ES.loc_classES in json.loads(ob1.to_json())[ES.loc_classES])
        self.assertTrue(ES.type + ES.prp_classES in json.loads(ob1.to_json())[ES.prp_classES])
        ob1.option["json_obs_val"] = False
        self.assertTrue(ES.dat_classES in json.loads('{' + ob1.to_json() + '}'))
        ob1.option["json_obs_val"] = True
        ob1.option["json_obs_attrib"] = True
        self.assertTrue(ES.obs_attributes in json.loads(ob1.to_json()))
        ob1.option["json_info_type"] = True
        ob1.option["json_info_nval"] = True
        ob1.option["json_info_autre"] = True
        ob1.option["json_info_box"] = True
        ob2 = Observation(ob1.to_json())
        self.assertTrue(ES.type in json.loads(ob2.to_json()))
        
    def test_obs_maj_type(self):
        maj = [False, True]
        for maj_index in maj:
            ob = Observation()
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 0 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 1 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, dat3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 2 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, loc1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 10 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc1, dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 11 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc1, dat3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 12 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 20 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3, dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 21 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3, dat3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 22 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, _res(1)))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 0 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 1 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), dat3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 2 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 10 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1, dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 11 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1, dat3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 12 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 20 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc3, dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 21 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc3, dat3))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 22 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc3, dat2))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 22 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(9)))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 0 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(9), dat1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 1 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(3), dat3, prop1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 102 and ob.complet and ob.setResult.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(6), dat3, prop1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 102 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc1, prop1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 110 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc1, dat1, prop1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 111 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc1, dat3, prop1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 112 and ob.complet and ob.setResult.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(6), loc1, dat3, prop1))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 112 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(6), loc3, prop2))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 220 and ob.complet and ob.setResult.axes == [1, 2])
            ob = Observation(json.dumps(dict((obs_1, _res(9), loc3, prop2))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 220 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(9), loc3, dat1, prop2))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 221 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(6), loc3, dat1, prop2))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 224 and ob.complet and ob.setResult.axes == [1, 2])
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 228 and ob.complet and ob.setResult.axes == [0, 1, 2])
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(9)))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 222 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, dat3, loc3, prop2, _res(6)))))
            _majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 225 and ob.complet and ob.setResult.axes == [10, 2])
            #ob.option["json_res_index"] = True
            #print(ob.to_json(), '\n')

    def test_obs_dim(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat2, loc3, prop3, _res(6)))), order='xd')
        self.assertTrue(ob1.score == 227 and ob1.complet and ob1.setResult.axes == [0, 21])
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc2, prop3, _res(6)))), order='lx')
        self.assertTrue(ob1.score == 226 and ob1.complet and ob1.setResult.axes == [20, 1])
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop3, _res(3)))), order='x')
        self.assertTrue(ob1.score == 222 and ob1.complet and ob1.setResult.axes == [120])

    def test_obs_majListName_majListValue(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18))))
        ob1.majList(LocationValue, [pparis, plyon, pmarseille], name=False)
        self.assertEqual(ob1.setLocation.valueList[2].vPoint(), pmarseille)
        ob1.majList(DatationValue, [pt1, pt2, pt3], name=False)
        self.assertEqual(ob1.setDatation.valueList[2].instant, pt3)
        ob1.majList(LocationValue, ['paris', 'lyon', 'marseille'], 'name')
        self.assertEqual(ob1.setLocation.valueList[2].name, 'marseille')

    def test_obs_majIndex_iLoc(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18))))
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))), order='lpd')
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))), order='pdl')
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '9')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6)))), order='xp')
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6)))), order='px')
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat2, loc3, prop3, _res(6)))), order='xd')
        self.assertEqual(ob1.iLoc(0,1,1)[ES.res_classES], '2')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc2, prop3, _res(6)))), order='lx')
        self.assertEqual(ob1.iLoc(0,1,0)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop3, _res(3)))), order='x')
        self.assertEqual(ob1.iLoc(1,1,1)[ES.res_classES], '1')

    def test_obs_sort(self):
        ob = Observation(dict((obs_1, dat3, dpt3, prop2, _res(6))), order='px')
        test = ob.iLoc(1,1,0)
        ob.sort(cross = False)
        self.assertEqual(ob.iLoc(2,1,1), test)
        ob.sort()
        self.assertEqual(ob.iLoc(2,2,1), test)
        ob.sort(cross = False, order = 'ldp')
        self.assertEqual(ob.iLoc(2,1,1), test)
        ob.sort(order = 'ldp')
        self.assertEqual(ob.iLoc(1,1,1), test)
        
    def test_obs_add(self):
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))))
        ob.option["json_prp_type"] = False
        ob.option["json_loc_name"] = ob.option["json_dat_name"] = ob.option["json_prp_name"] = True
        obp = Observation(json.dumps(dict((obs_1, truc_mach, pdat3, ploc3, pprop2, _res(18)))))
        obp.option["json_prp_type"] = False
        obp.option["json_loc_name"] = obp.option["json_dat_name"] = obp.option["json_prp_name"] = True
        obc = copy.copy(ob)
        obc.option["json_prp_type"] = False
        obc.option["add_equal"] = "value"
        obc.option["json_loc_name"] = obc.option["json_dat_name"] = obc.option["json_prp_name"] = True
        obc += ob
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName], json.loads(obc.to_json())[ES.res_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.dat_valName], json.loads(obc.to_json())[ES.dat_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.loc_valName], json.loads(obc.to_json())[ES.loc_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.prp_valName], json.loads(obc.to_json())[ES.prp_valName])
        ob2 = ob + ob
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName], json.loads(ob2.to_json())[ES.res_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.dat_valName], json.loads(ob2.to_json())[ES.dat_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.loc_valName], json.loads(ob2.to_json())[ES.loc_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.prp_valName], json.loads(ob2.to_json())[ES.prp_valName])
        obc = copy.copy(ob)
        obc += obp
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName] + json.loads(obp.to_json())[ES.res_valName], 
                         json.loads(obc.to_json())[ES.res_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.dat_valName] + json.loads(obp.to_json())[ES.dat_valName],
                         json.loads(obc.to_json())[ES.dat_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.loc_valName] + json.loads(obp.to_json())[ES.loc_valName],
                         json.loads(obc.to_json())[ES.loc_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.prp_valName] + json.loads(obp.to_json())[ES.prp_valName],
                         json.loads(obc.to_json())[ES.prp_valName])
        ob2 = ob + obp
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName] + json.loads(obp.to_json())[ES.res_valName], 
                         json.loads(ob2.to_json())[ES.res_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.dat_valName] + json.loads(obp.to_json())[ES.dat_valName],
                         json.loads(ob2.to_json())[ES.dat_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.loc_valName] + json.loads(obp.to_json())[ES.loc_valName],
                         json.loads(ob2.to_json())[ES.loc_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.prp_valName] + json.loads(obp.to_json())[ES.prp_valName],
                         json.loads(ob2.to_json())[ES.prp_valName])
        obp2 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, pprop2, _res(18)))))
        obp2.option["json_prp_type"] = False
        ob2 = ob + obp2
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName] + json.loads(obp.to_json())[ES.res_valName], 
                         json.loads(ob2.to_json())[ES.res_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.dat_valName], json.loads(ob2.to_json())[ES.dat_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.loc_valName], json.loads(ob2.to_json())[ES.loc_valName])
        self.assertEqual(json.loads(ob.to_json())[ES.prp_valName] + json.loads(obp2.to_json())[ES.prp_valName],
                         json.loads(ob2.to_json())[ES.prp_valName])

    def test_obs_extend(self):
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2))))
        obp = Observation(json.dumps(dict((obs_1, _res(18)))))
        ob.extend(obp)
        self.assertEqual(json.loads(ob.to_json())[ES.res_valName], json.loads(obp.to_json())[ES.res_valName])
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2))))
        obp = Observation(json.dumps(dict((obs_1, ploc3, _res(18)))))
        obc = copy.copy(ob)
        ob.extend(obp)
        self.assertEqual(json.loads(ob.to_json())[ES.loc_valName], json.loads(obc.to_json())[ES.loc_valName])

    def test_sensor(self):
        obs = Observation()
        nprop1 = obs.addValue(PropertyValue(prop_pm25))
        for i in range(6): # simule une boucle de mesure
            '''obs.addValueSensor(ResultValue(45+i), 
                                DatationValue(datetime(2021, 6, 4+i, 12, 5).isoformat()),
                                LocationValue([14+i, 40]),
                                nprop1)'''
            obs.append(DatationValue(datetime(2021, 6, 4+i, 12, 5).isoformat()),
                       LocationValue([14+i, 40]), nprop1, ResultValue(45+i))
        obs.majType()
        obs.option["json_ESobs_class"] = True
        obs.option["json_elt_type"] = True
        obs.option["json_info_type"] = True
        self.assertEqual(json.loads(obs.to_json())[ES.information]["typeobs"], ES.obsCat[122])
        
class TestExports(unittest.TestCase):
    '''Unit tests for `ES.ESObservation.Observation` exports '''

    @unittest.skipIf(mongo, "test envoi mongo")
    def test__envoi_mongo(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), order='xp')
        self.assertEqual(_envoi_mongo(ob), 200)

    def test_geo_interface(self):
        ob = Observation(dict([obs_1, loc3]))
        _resloc = (tuple(paris), tuple(lyon), tuple(marseille))
        _resgeo = dict([(ES.type,"MultiPoint"), ("coordinates",_resloc)])
        self.assertEqual(ob.__geo_interface__, _resgeo)
        self.assertEqual(ob.__geo_interface__["coordinates"], _resloc)
        ob.option["json_loc_point"] = False
        self.assertEqual(ob.__geo_interface__, _resgeo)
        ob = Observation(dict((obs_1, dpt2, dat1)))
        dpt2pt = {'type': 'Polygon', 'coordinates': (((0.5, 1.5), (0.0, 2.0),
          (1.0, 2.0), (2.0, 2.0), (1.0, 1.0), (0.0, 1.0), (0.5, 1.5)),)}
        self.assertEqual(ob.__geo_interface__, dpt2pt)
        ob.option["json_loc_point"] = False
        #dpt2pol = {'type': 'MultiPolygon', 'coordinates': [(((0.0, 1.0), (1.0, 2.0), (1.0, 1.0), (0.0, 1.0)),),
        #                                                   (((0.0, 2.0), (2.0, 2.0), (1.0, 1.0), (0.0, 2.0)),)]}
        #self.assertEqual(ob.__geo_interface__, dpt2pol)  # !!! multiponints pas multipolygon

    def test_obs_polygon(self):
        ob = Observation(json.dumps(dict((obs_1, dat3, dpt2, prop2, _res(6)))))
        ob.option["json_loc_point"] = False
        #self.assertEqual(json.dumps(ob.__geo_interface__),           # !!! multiponints pas multipolygon
        #                 json.dumps({"type": "MultiPolygon", "coordinates": dpt2[1]}))
        
    def test_xarray(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), order='xp')
        self.assertTrue(ob.to_xarray()[2,1].item() == ResultValue(2))
        ob.setResult.full()
        self.assertTrue(ob.to_xarray()[2,1,1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop1, _res(3))), order='xp')
        self.assertTrue(ob.to_xarray()[1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop3, _res(3))), order='dlp')
        self.assertTrue(ob.to_xarray()[1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(18))), order='dlp')
        self.assertTrue(ob.to_xarray()[2,1,0].item() == ResultValue(9))
        ob = Observation(dict((obs_1, dat3, loc2, prop1, _res(6))), order='dlp')
        self.assertTrue(ob.to_xarray()[2,0].item() == ResultValue(2))
        
    @unittest.skipIf(plot, "test plot")
    def test_plot(self):
        ob = Observation(dict((obs_1, dat3ord, loc3, prop1, _res(9))), order='ldp')
        self.assertTrue(ob.plot(line=True, size =5) == None)
        self.assertTrue(ob.plot(line=False, size =5) == None)
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(18))), order='dlp')
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        self.assertTrue(ob.voxel(sort=True) == None)
        ob.full()
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), order='xp')
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        self.assertTrue(ob.voxel(sort=True) == None)
        ob.full()
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        ob = Observation(dict((obs_1, dat3, loc2, prop3, _res(6))), order='xl')
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        self.assertTrue(ob.voxel(sort=True) == None)
        ob.full()
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        ob = Observation(dict((obs_1, dat2, loc3, prop3, _res(6))), order='xd')
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        self.assertTrue(ob.voxel(sort=True) == None)
        ob.full()
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        ob = Observation(dict((obs_1, dat3, loc3, prop3, _res(3))), order='xp')
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        self.assertTrue(ob.voxel(sort=True) == None)
        ob.full()
        self.assertTrue(ob.plot(line=True) == None)
        self.assertTrue(ob.plot(line=False) == None)
        ob = Observation(dict((obs_1, dat1, loc3, prop3, _res(3))), order='xp')
        self.assertTrue(ob.plot(line=True) == None)
        ob = Observation(dict((obs_1, dat3, loc1, prop3, _res(3))), order='xp')
        self.assertTrue(ob.plot(line=True) == None)
        ob = Observation(dict((obs_1, dat3, loc3, prop1, _res(3))), order='xp')
        self.assertTrue(ob.plot(line=True) == None)
        ob = Observation(dict((obs_1, dat1, loc1, prop3, _res(3))), order='xp')
        self.assertTrue(ob.plot(line=True) == None)

    def test_exports(self):
        ob = Observation(json.dumps(dict((obs_1, dat3, dpt3, prop1, _res(3)))), order='px')
        #ob.majType()
        self.assertTrue(type(ob.to_xarray()) != type(None))
        #self.assertTrue(type(ob.to_dataFrame()) != type(None))
        #self.assertTrue(ob.choropleth() != None)
        #self.assertTrue(type(ob.to_geoDataFrame()) != type(None))
        self.assertTrue(ob.jsonFeature != '')


if __name__ == '__main__':
    unittest.main(verbosity=2)