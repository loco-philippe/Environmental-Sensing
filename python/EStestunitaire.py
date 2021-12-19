# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: a179227
"""
import unittest

from ESElement import ESElement
from ESComponent import ResultValue, LocationValue, DatationValue, PropertyValue, ESValue, gshape
from ESObservation import Observation
from ESObs import ESSet, ESSetDatation, ESSetProperty, ESSetResult, ESSetLocation
from copy import copy
from ESconstante import ES
import json
import requests as rq
from datetime import datetime

#import cartopy.crs as ccrs
#import matplotlib.pyplot as plt
#import folium
#import geojson
#import numpy as np
#from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, \
#    asPoint, asPolygon, asMultiPoint, asMultiPolygon, shape

# datas-----------------------------------------------------------------------
def val_(n): return list(i for i in range(n))
def res_(n): return (ES.res_valName[0], val_(n))
with open('../json/france-geojson/departements-version-simplifiee.geojson') as f: 
    dp = f.read()
dpt = json.loads(dp)
pol13 = dpt['features'][12]['geometry']['coordinates']
pol69 = dpt['features'][69]['geometry']['coordinates']
pol75 = dpt['features'][75]['geometry']['coordinates']
pol1 = [[[0.0,1.0], [1.0,2.0], [1.0,1.0], [0.0,1.0]]]
pol1centre = [0.6666666666666666, 1.3333333333333333]
pol2 = [[[0.0,2.0], [2.0,2.0], [1.0,1.0], [0.0,2.0]]]
dpt2 = (ES.loc_valName[1], [pol1, pol2])
dpt3 = (ES.loc_valName[1], [pol75, pol69, pol13])
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
dat1 = (ES.dat_valName[0], {'date1' : t1.isoformat()})
dat2 = (ES.dat_valName[0], [t1.isoformat(), t2.isoformat()])
dat3 = (ES.dat_valName[0], [{'date1' : t1.isoformat()}, t2.isoformat(), t3.isoformat()])
dat3sn = (ES.dat_valName[0], [t1.isoformat(), t2.isoformat(), t3.isoformat()])
pdat3 = (ES.dat_valName[0], [pt1.isoformat(), pt2.isoformat(), pt3.isoformat()])
prop1 = (ES.prp_valName[0], prop_pm10)
prop2 = (ES.prp_valName[1], [prop_pm25, prop_pm10])
prop3 = (ES.prp_valName[0], [prop_pm25, prop_pm10, prop_co2])
pprop2 = (ES.prp_valName[0], [pprop_pm25, pprop_pm10])
loc1 = (ES.loc_valName[0], {'paris' : paris})
loc2 = (ES.loc_valName[0], [paris, lyon])
loc3 = (ES.loc_valName[0], [{'paris' : paris}, lyon, marseille])
loc3sn = (ES.loc_valName[0], [paris, lyon, marseille])
ploc3 = (ES.loc_valName[0], [pparis, plyon, pmarseille])
res2 = (ES.res_valName[0], [[41, [2, 2, 0]], [18, [1, 2, 1]]])

def option_simple(ob1):
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

def majType_avec_option(ob1, maj_index):
    ob1.majType()
 
def envoi_mongo(ob):
    url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
    r = rq.post(url, data=ob.json())  
    print("réponse : ", r.text, "\n")

simple = False

@unittest.skipIf(simple, "test unitaire")
class TestObsUnitaire(unittest.TestCase):
    opt = ES.mOption.copy()
    def test_ResultValue(self):
        self.opt["json_res_index"] = True
        self.assertEqual(ResultValue("coucou").json(self.opt), '["coucou", [-1, -1, -1]]')
        self.assertEqual(ResultValue(["coucou", [1, 2, -1]]).json(self.opt), '["coucou", [1, 2, -1]]')
        self.assertEqual(ResultValue("coucou", [1, 2, -1]).json(self.opt), '["coucou", [1, 2, -1]]')
        self.assertEqual(ResultValue('{"er":2}', [1, 2, -1]).json(self.opt), '[{"er": 2}, [1, 2, -1]]')
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
        self.assertEqual(ESValue.mini(LocationValue(lyon), LocationValue(paris)).json(self.opt), json.dumps(mini_PL))
        self.assertEqual(LocationValue(pol1).json(self.opt), json.dumps(pol1centre)) 
        self.opt["json_loc_point"]=False 
        self.assertEqual(LocationValue(pol1).json(self.opt), json.dumps(pol1)) 
        
    def test_DatationValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(DatationValue(t1), DatationValue(DatationValue(t1)))
        self.assertEqual(DatationValue(t1).json(self.opt), t1.isoformat()) 
        self.assertEqual(ESValue.maxi(DatationValue(t1), DatationValue(t2)).json(self.opt), t2.isoformat()) 
        self.opt["json_dat_instant"] = False
        self.assertEqual(DatationValue(json.loads(t1n)).json(self.opt), t1.isoformat()) 
        self.opt["json_dat_name"] = True
        self.opt["json_dat_instant"] = True
        self.assertEqual(DatationValue(json.loads(t1n)).json(self.opt), t1n) 
        

    def test_propertyValue(self):
        self.opt = ES.mOption.copy()
        self.assertEqual(PropertyValue().json(self.opt), '{}') 
        self.opt["json_prp_type"] = False
        self.assertEqual(PropertyValue({ES.prp_propType : "PM25"}).json(self.opt), '{"'+ES.prp_propType+'": "PM25"}')
        self.assertEqual(PropertyValue(pprop_pm10).json(self.opt), json.dumps(pprop_pm10))
        self.opt["json_prp_type"] = True
        self.assertEqual(PropertyValue(pprop_pm10).json(self.opt), 
                         json.dumps({list(pprop_pm10.keys())[0]: list(pprop_pm10.values())[0]}))
        
    def test_nameValue(self):
        self.assertEqual(DatationValue('recre').json(), tnull.isoformat()) 
        self.opt["json_dat_instant"] = False
        self.opt["json_dat_name"] = False
        self.assertEqual(DatationValue('recre').json(self.opt), tnull.isoformat())
        self.opt["json_prp_type"] = False
        self.opt["json_prp_name"] = True
        self.assertEqual(PropertyValue(pprop_pm25).json(self.opt), json.dumps(pprop_pm25))
        self.assertEqual(PropertyValue('test').json(self.opt), "test")
        self.opt["json_loc_name"] = True
        self.assertEqual(LocationValue(lyon).json(self.opt), json.dumps(lyon))
        self.assertEqual(LocationValue('test').json(self.opt), "test")
        #ob1 = Observation(json.dumps(dict((obs_1, truc_mach, ndat3, loc3, prop2, res_(9)))))
        #option_simple(ob1)
        #ob1.option["json_loc_name"] = True
        #self.assertEqual(['loc0', 'loc1', 'loc2'], json.loads(ob1.json())[ES.loc_valName[2]])
        
    def test_majValue_majName(self):
        val = LocationValue(lyon)
        val.majValue(LocationValue([4,5]), True)
        self.assertEqual(val.point, [4,5])
        val.majValue(LocationValue([[6,7], [7,8], [8,6]]), False)
        self.assertEqual(val.shap, gshape([[6,7], [7,8], [8,6]]))
        val.majName('truc')
        self.assertEqual(val.name, 'truc')     
        val = DatationValue(t1)
        val.majValue(DatationValue(t2), True)
        self.assertEqual(val.instant, t2)
        val.majValue(DatationValue(s1), False)
        self.assertEqual(val.slot, s1)
        val.majName('truc')
        self.assertEqual(val.name, 'truc')
    
    def test_ESSet(self):
        self.assertEqual(ESSet(DatationValue, [t1, t2, t3])[1], ESSet(DatationValue, [t1, t2, t3]).maxiBox()) 
        self.assertEqual(ESSet(LocationValue, [paris, lyon, marseille]).maxiBox(), LocationValue(maxi_PLM)) 
        self.assertEqual(ESSet(PropertyValue, [prop_pm10, prop_pm25]).jsonSet(self.opt), json.dumps([prop_pm10, prop_pm25])) 
        self.assertEqual(ESSet(LocationValue, [LocationValue(paris)]).maxiBox(), LocationValue(paris)) 

    def test_ESObs(self):
        da1 = ESSetDatation(Observation(), {ES.dat_valName[0]:[t1, t2, t3]})
        self.assertEqual(da1[1], da1.maxiBox()) 
        da2 = ESSetProperty(Observation(), {ES.prp_valName[0]:[prop_pm10, prop_pm25], ES.prp_upperValue :'254'})
        self.opt["json_prp_type"] = False
        self.assertEqual(json.loads('{'+da2.json(self.opt)+'}')[ES.prp_valName[1]], [prop_pm10, prop_pm25]) 
        self.assertEqual(da2.mAtt[ES.prp_upperValue], '254') 
        da3 = ESSetResult(Observation(), {ES.res_valName[0]:[r2, r2]})
        self.assertEqual(json.loads('{'+da3.json(self.opt)+'}')[ES.res_valName[0]], r2.value)
        da4 = ESSetLocation(Observation(), {ES.loc_valName[0]:[paris, lyon, marseille]})
        self.assertEqual(da4.maxiBox(), LocationValue(maxi_PLM)) 
        da5 = ESSetLocation(Observation(), {ES.loc_classES:{ES.loc_valName[0]:[paris, lyon, marseille], 'truc':'machin'}})
        self.assertEqual(da5.mAtt['truc'], 'machin') 
        
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
    
    def test_location_bytes(self):
        #d5 = ESSetLocation(Observation(), {ES.loc_valName[2]:["paris", "lyon", "marseille"]})
        d5 = ESSetLocation(Observation(), {ES.loc_valName[0]:["paris", "lyon", "marseille"]})
        d4 = ESSetLocation(Observation())
        d4.from_bytes(d5.to_bytes(True))
        self.assertEqual(d4.valueList[2].name, "marseille")
        d5 = ESSetLocation(Observation(), {ES.loc_valName[0]:[paris, lyon, marseille]})
        d4 = ESSetLocation(Observation())
        d4.from_bytes(d5.to_bytes())
        self.assertEqual(d4.valueList[2].point[0], marseille[0])

    def test_datation_bytes(self):
        #d5 = ESSetDatation(Observation(), {ES.dat_valName[2]:["t1", "t2", "t3"]})
        d5 = ESSetDatation(Observation(), {ES.dat_valName[0]:["t1", "t2", "t3"]})
        d4 = ESSetDatation(Observation())
        d4.from_bytes(d5.to_bytes(True))
        self.assertEqual(d4.valueList[2].name, "t3")
        d5 = ESSetDatation(Observation(), {ES.dat_valName[0]:[t1, t2, t3]})
        d4 = ESSetDatation(Observation())
        d4.from_bytes(d5.to_bytes())
        self.assertEqual(d4.valueList[2].instant, t3)
        
    def test_property_bytes(self):
        da2 = ESSetProperty(Observation(), {ES.prp_valName[0]:[pprop_pm10, pprop_pm25]})
        da1 = ESSetProperty(Observation())
        da1.from_bytes(da2.to_bytes())
        self.assertEqual(da1.valueList[1].application, pprop_pm25[ES.prp_appli])

    def test_result_bytes(self):
        da3 = ESSetResult(Observation(), {ES.res_valName[0]:[r4, r5]})
        da2 = ESSetResult(Observation())
        da2.from_bytes(da3.to_bytes())
        self.assertEqual(da2.valueList[1].value, r5.value)
        da3 = ESSetResult(Observation(), {ES.res_valName[0]:[r6, r7]})
        da2 = ESSetResult(Observation())
        da2.from_bytes(da3.to_bytes(False, True))
        self.assertEqual(da2.valueList[0].value, r6.value)
        self.assertEqual(da2.valueList[0].ind, r6.ind)
        self.assertEqual(da2.valueList[1].value, r7.value)
        self.assertEqual(da2.valueList[1].ind, r7.ind)
        #ob2.option["json_res_index"]=True
        da2 = ESSetResult(Observation())
        da2.from_bytes(da3.to_bytes(False, True, 'null', ['CO2', 'CO2']), ['CO2', 'CO2'])
        self.assertEqual(da2.valueList[1].value, r7.value)
        da2 = ESSetResult(Observation())
        da2.from_bytes(da3.to_bytes(False, True, 'null', ['CO2','PM25']), ['CO2','PM25'])
        self.assertEqual(round(da2.valueList[1].value, 1), round(r7.value, 1))
        da2 = ESSetResult(Observation())
        da2.from_bytes(da3.to_bytes(False, False, 'null', ['CO2','PM25']), ['CO2','PM25'])
        self.assertEqual(round(da2.valueList[1].value, 1), round(r7.value, 1))
        
    def test_observation_bytes(self):
        ob1 = Observation(json.dumps(dict((obs_1, dat1, loc1, prop2, res_(2)))))
        ob2 = Observation()
        ob2.from_bytes(ob1.to_bytes())
        ob2.majType()
        self.assertEqual(ob1.to_bytes(), ob2.to_bytes())
        ob1 = Observation(json.dumps(dict((obs_1, dat1, loc1, prop1, res_(1)))))
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
        ob1.option['bytes_res_format'] = ob2.option['bytes_res_format'] = 'uint32'
        ob2.from_bytes(ob1.to_bytes())
        ob2.majType()
        self.assertEqual(ob1.to_bytes(), ob2.to_bytes())
        self.assertEqual(ob1.mAtt[ES.obs_reference], ob2.mAtt[ES.obs_reference])

@unittest.skipIf(simple, "test observation")
class TestObservation(unittest.TestCase):

    def test_obs_vList(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3)))
        self.assertEqual(ob1.setDatation.vListName[0], 'date1')
        self.assertEqual(ob1.setDatation.vListName[1], 'dat1')
        self.assertEqual(ob1.setLocation.vListPoint, [paris, lyon, marseille])
        self.assertEqual(ob1.setDatation.vListInstant, [t1.isoformat(), t2.isoformat(), t3.isoformat()])
        ob1 = Observation(dict((obs_1, truc_mach, dat3, dpt2)))
        self.assertEqual(ob1.setLocation.vListPoint[0], pol1centre)

    def test_obs_simple(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3sn)),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, loc3))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, loc3sn)),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, prop2))))
        option_simple(ob1)
        ob1.option["json_prp_type"] = False
        self.assertEqual(dict((obs_1, truc_mach, prop2)),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, res_(9)))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, res_(9))),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3sn, loc3sn, prop2, res_(9))),json.loads(ob1.json()))
        
    def test_obs_att(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, 
                                           (ES.obs_reference, 25), (ES.prp_upperValue,'254'),
                                           res_(9)))))
        self.assertEqual(ob1.mAtt['truc'], 'machin')
        self.assertEqual(ob1.mAtt[ES.obs_reference], 25)
        self.assertEqual(ob1.setProperty.mAtt[ES.prp_upperValue], '254')

    def test_obs_options(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
        option_simple(ob1)
        ob1.option["json_res_index"] = True
        self.assertEqual(json.loads(ob1.json())[ES.res_valName[0]][0], [val_(9)[0], ES.nullInd])
        ob1.option["json_ESobs_class"] = True
        self.assertTrue(ES.dat_classES in json.loads(ob1.json()))
        self.assertTrue(ES.res_classES in json.loads(ob1.json()))
        self.assertTrue(ES.loc_classES in json.loads(ob1.json()))
        self.assertTrue(ES.prp_classES in json.loads(ob1.json()))
        ob1.option["json_elt_type"] = True
        self.assertTrue(ES.type + ES.dat_classES in json.loads(ob1.json())[ES.dat_classES])
        self.assertTrue(ES.type + ES.res_classES in json.loads(ob1.json())[ES.res_classES])
        self.assertTrue(ES.type + ES.loc_classES in json.loads(ob1.json())[ES.loc_classES])
        self.assertTrue(ES.type + ES.prp_classES in json.loads(ob1.json())[ES.prp_classES])
        ob1.option["json_obs_val"] = False
        self.assertTrue(ES.dat_classES in json.loads('{' + ob1.json() + '}'))
        ob1.option["json_obs_val"] = True
        ob1.option["json_obs_attrib"] = True
        self.assertTrue(ES.obs_attributes in json.loads(ob1.json()))
        ob1.option["json_info_type"] = True
        ob1.option["json_info_nval"] = True
        ob1.option["json_info_autre"] = True
        ob1.option["json_info_box"] = True
        ob2 = Observation(ob1.json())
        self.assertTrue(ES.type in json.loads(ob2.json()))
        
    def test_obs_maj_type(self):
        maj = [False, True]
        for maj_index in maj:
            ob = Observation()
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 0 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 1 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 2 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, loc1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 10 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc1, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 11 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc1, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 12 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 20 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 21 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 22 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, res_(1)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 0 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 1 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 2 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 10 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc1, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 11 and ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc1, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 12 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 20 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 21 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 22 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3, dat2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 22 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(9)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 0 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(9), dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 1 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(3), dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 102 and ob.complet and ob.setResult.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, res_(6), dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 102 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(3), loc1, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 110 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(3), loc1, dat1, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 111 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(3), loc1, dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 112 and ob.complet and ob.setResult.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, res_(6), loc1, dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 112 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(6), loc3, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 220 and ob.complet and ob.setResult.axes == [1, 2])
            ob = Observation(json.dumps(dict((obs_1, res_(9), loc3, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 220 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(9), loc3, dat1, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 221 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, res_(6), loc3, dat1, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 224 and ob.complet and ob.setResult.axes == [1, 2])
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 228 and ob.complet and ob.setResult.axes == [0, 1, 2])
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 222 and not ob.complet and ob.setResult.axes == [])
            ob = Observation(json.dumps(dict((obs_1, dat3, loc3, prop2, res_(6)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 225 and ob.complet and ob.setResult.axes == [2, 10])
            #envoi_mongo(ob)
            #ob.option["json_res_index"] = True
            #print(ob.json(), '\n')

    def test_obs_dim(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat2, loc3, prop3, res_(6)))),'xd')
        self.assertTrue(ob1.score == 227 and ob1.complet and ob1.setResult.axes == [0, 21])
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc2, prop3, res_(6)))),'lx')
        self.assertTrue(ob1.score == 226 and ob1.complet and ob1.setResult.axes == [1, 20])
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop3, res_(3)))),'x')
        self.assertTrue(ob1.score == 222 and ob1.complet and ob1.setResult.axes == [120])

    def test_obs_majListName_majListValue(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18))))
        ob1.majList(LocationValue, [pparis, plyon, pmarseille], 'base')
        self.assertEqual(ob1.setLocation.valueList[2].point, pmarseille)
        ob1.majList(DatationValue, [pt1, pt2, pt3], 'base')
        self.assertEqual(ob1.setDatation.valueList[2].instant, pt3)
        ob1.majList(LocationValue, ['paris', 'lyon', 'marseille'], 'name')
        self.assertEqual(ob1.setLocation.valueList[2].name, 'marseille')

    def test_obs_majIndex_iloc(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18))))
        self.assertEqual(ob1.iloc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18)))),'lpd')
        self.assertEqual(ob1.iloc(0,0,1)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18)))),'pdl')
        self.assertEqual(ob1.iloc(0,0,1)[ES.res_classES], '9')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(6)))),'xp')
        self.assertEqual(ob1.iloc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(6)))),'px')
        self.assertEqual(ob1.iloc(0,0,1)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat2, loc3, prop3, res_(6)))),'xd')
        self.assertEqual(ob1.iloc(0,1,1)[ES.res_classES], '2')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc2, prop3, res_(6)))),'lx')
        self.assertEqual(ob1.iloc(0,1,0)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop3, res_(3)))),'x')
        self.assertEqual(ob1.iloc(1,1,1)[ES.res_classES], '1')

    def test_obs_sort(self):
        ob = Observation(dict((obs_1, dat3, dpt3, prop2, res_(6))), 'px')
        test = ob.iloc(1,1,0)
        ob.sort(cross = False)
        self.assertEqual(ob.iloc(2,1,1), test)
        ob.sort()
        self.assertEqual(ob.iloc(2,2,1), test)
        ob.sort(cross = False, order = [1,0,2])
        self.assertEqual(ob.iloc(2,1,1), test)
        ob.sort(order = [1,0,2])
        self.assertEqual(ob.iloc(1,1,1), test)
        
    def test_obs_creation(self):
        obs1 = Observation()
        self.assertEqual(obs1.classES,                   ES.obs_classES)
        self.assertEqual(ESSetDatation(obs1).classES,    ES.dat_classES)
        self.assertEqual(ESSetResult(obs1).classES,      ES.res_classES)
        self.assertEqual(ESSetProperty(obs1).classES,    ES.prp_classES)
        self.assertEqual(ESSetLocation(obs1).classES,    ES.loc_classES)
      
        ob = Observation(json.dumps(dict([obs_1, res_(9)])))
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]], val_(9))

    def test_obs_add(self):
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18)))))
        ob.option["json_prp_type"] = False
        ob.option["json_loc_name"] = ob.option["json_dat_name"] = ob.option["json_prp_name"] = True
        obp = Observation(json.dumps(dict((obs_1, truc_mach, pdat3, ploc3, pprop2, res_(18)))))
        obp.option["json_prp_type"] = False
        obp.option["json_loc_name"] = obp.option["json_dat_name"] = obp.option["json_prp_name"] = True
        obc = copy(ob)
        obc.option["json_prp_type"] = False
        obc.option["json_loc_name"] = obc.option["json_dat_name"] = obc.option["json_prp_name"] = True
        obc += ob
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]], json.loads(obc.json())[ES.res_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.dat_valName[0]], json.loads(obc.json())[ES.dat_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.loc_valName[0]], json.loads(obc.json())[ES.loc_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.prp_valName[1]], json.loads(obc.json())[ES.prp_valName[1]])
        ob2 = ob + ob
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]], json.loads(ob2.json())[ES.res_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.dat_valName[0]], json.loads(ob2.json())[ES.dat_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.loc_valName[0]], json.loads(ob2.json())[ES.loc_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.prp_valName[1]], json.loads(ob2.json())[ES.prp_valName[1]])
        obc = copy(ob)
        obc += obp
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]] + json.loads(obp.json())[ES.res_valName[0]], 
                         json.loads(obc.json())[ES.res_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.dat_valName[0]] + json.loads(obp.json())[ES.dat_valName[0]],
                         json.loads(obc.json())[ES.dat_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.loc_valName[0]] + json.loads(obp.json())[ES.loc_valName[0]],
                         json.loads(obc.json())[ES.loc_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.prp_valName[1]] + json.loads(obp.json())[ES.prp_valName[1]],
                         json.loads(obc.json())[ES.prp_valName[1]])
        ob2 = ob + obp
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]] + json.loads(obp.json())[ES.res_valName[0]], 
                         json.loads(ob2.json())[ES.res_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.dat_valName[0]] + json.loads(obp.json())[ES.dat_valName[0]],
                         json.loads(ob2.json())[ES.dat_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.loc_valName[0]] + json.loads(obp.json())[ES.loc_valName[0]],
                         json.loads(ob2.json())[ES.loc_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.prp_valName[1]] + json.loads(obp.json())[ES.prp_valName[1]],
                         json.loads(ob2.json())[ES.prp_valName[1]])
        obp2 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, pprop2, res_(18)))))
        obp2.option["json_prp_type"] = False
        ob2 = ob + obp2
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]] + json.loads(obp.json())[ES.res_valName[0]], 
                         json.loads(ob2.json())[ES.res_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.dat_valName[0]], json.loads(ob2.json())[ES.dat_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.loc_valName[0]], json.loads(ob2.json())[ES.loc_valName[0]])
        self.assertEqual(json.loads(ob.json())[ES.prp_valName[1]] + json.loads(obp2.json())[ES.prp_valName[1]],
                         json.loads(ob2.json())[ES.prp_valName[1]])

    def test_obs_extend(self):
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2))))
        obp = Observation(json.dumps(dict((obs_1, res_(18)))))
        ob.extend(obp)
        self.assertEqual(json.loads(ob.json())[ES.res_valName[0]], json.loads(obp.json())[ES.res_valName[0]])
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2))))
        obp = Observation(json.dumps(dict((obs_1, ploc3, res_(18)))))
        obc = copy(ob)
        ob.extend(obp)
        self.assertEqual(json.loads(ob.json())[ES.loc_valName[0]], json.loads(obc.json())[ES.loc_valName[0]])

    def test_sensor(self):
        obs = Observation()
        nprop1 = obs.addValue(PropertyValue(prop_pm25))
        for i in range(6): # simule une boucle de mesure
            nres = obs.addValueSensor(ResultValue(45+i), 
                                DatationValue(datetime(2021, 6, 4+i, 12, 5).isoformat()),
                                LocationValue([14+i, 40]),
                                nprop1)
        obs.majType()
        obs.option["json_ESobs_class"] = True
        obs.option["json_elt_type"] = True
        self.assertEqual(json.loads(obs.json())[ES.information]["typeobs"], ES.obsCat[122])
        
    def test_geo_interface(self):
        ob = Observation(json.dumps(dict([obs_1, loc3])))
        res_loc = (tuple(paris), tuple(lyon), tuple(marseille))
        res_geo = dict([(ES.type,"MultiPoint"), ("coordinates",res_loc)])
        self.assertEqual(ob.__geo_interface__, res_geo)
        self.assertEqual(ob.__geo_interface__["coordinates"], res_loc)
        ob.option["json_loc_point"] = False
        self.assertEqual(ob.__geo_interface__, res_geo)
        ob = Observation(json.dumps(dict((obs_1, dpt2, dat1))))
        dpt2pt = {'type': 'MultiPoint', 'coordinates': ((0.666667, 1.333333), (1.0, 1.666667))}
        self.assertEqual(ob.__geo_interface__, dpt2pt)
        ob.option["json_loc_point"] = False
        dpt2pol = {'type': 'MultiPolygon', 'coordinates': [(((0.0, 1.0), (1.0, 2.0), (1.0, 1.0), (0.0, 1.0)),),
                                                           (((0.0, 2.0), (2.0, 2.0), (1.0, 1.0), (0.0, 2.0)),)]}
        self.assertEqual(ob.__geo_interface__, dpt2pol)

    def test_obs_polygon(self):
        ob = Observation(json.dumps(dict((obs_1, dat3, dpt2, prop2, res_(6)))))
        ob.option["json_loc_point"] = False
        self.assertEqual(json.dumps(ob.__geo_interface__), 
                         json.dumps({"type": "MultiPolygon", "coordinates": dpt2[1]}))
        
    def test_exports(self):
        ob = Observation(json.dumps(dict((obs_1, dat3, dpt3, prop1, res_(3)))), 'px')
        #ob.majType()
        self.assertTrue(type(ob.to_xarray()) != type(None))
        self.assertTrue(type(ob.to_dataFrame()) != type(None))
        self.assertTrue(ob.choropleth() != None)
        #self.assertTrue(type(ob.to_geoDataFrame()) != type(None))
        self.assertTrue(ob.jsonFeature != '')


if __name__ == '__main__':
    unittest.main(verbosity=2)