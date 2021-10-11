# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: a179227
"""
import unittest

from ESElement import ESElement
from ESComponent import ResultValue, LocationValue, TimeValue, PropertyValue, ESValue
from ESObservation import Observation
from ESObs import Result, Location, Datation, Property, \
    ESSet, ESSetDatation, ESSetProperty, ESSetResult, ESSetLocation
from copy import copy
from ESconstante import ES

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import folium
import geojson
import numpy as np
import json
import geojson
import requests as rq
from datetime import datetime

from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, \
    asPoint, asPolygon, asMultiPoint, asMultiPolygon, shape

# datas-----------------------------------------------------------------------
def val_(n): return list(i for i in range(n))
def res_(n): return (ES.res_valueName, val_(n))
with open('../json/france-geojson/departements-version-simplifiee.geojson') as f: 
    dp = f.read()
dpt = json.loads(dp)
pol13 = dpt['features'][12]['geometry']['coordinates']
pol69 = dpt['features'][69]['geometry']['coordinates']
pol75 = dpt['features'][75]['geometry']['coordinates']
pol1 = [[[0.0,1.0], [1.0,2.0], [1.0,1.0], [0.0,1.0]]]
pol2 = [[[0.0,2.0], [2.0,2.0], [1.0,1.0], [0.0,2.0]]]
dpt2 = (ES.loc_valueName, [pol1, pol2])
dpt3 = (ES.loc_valueName, [pol75, pol69, pol13])
pparis       = [2.4, 48.9]
plyon        = [4.8, 45.8]
pmarseille   = [5.4, 43.3]
paris       = [2.35, 48.87]
lyon        = [4.83, 45.76]
marseille   = [5.38, 43.3]
mini_PL     = [2.35, 45.76]
maxi_PLM    = [5.38, 48.87]
obs_1       = (ES.type, ES.obs_classES)
truc_mach   = ("$truc", "machin")
prop_pm25   = dict([(ES.prp_propType,"PM25"), (ES.prp_unit, "ppm")])
prop_pm10   = dict([(ES.prp_propType,"PM10"), (ES.prp_unit, "ppm")])
pprop_pm25   = dict([(ES.prp_propType,"PM25"), (ES.prp_unit, "ppm"), (ES.prp_appli, "app")])
pprop_pm10   = dict([(ES.prp_propType,"PM10"), (ES.prp_unit, "ppm"), (ES.prp_appli, "app")])
pt1 = datetime(2020, 2, 4, 12, 5, 0)
pt2 = datetime(2020, 5, 4, 12, 5, 0)
pt3 = datetime(2020, 7, 4, 12, 5, 0)
t1 = datetime(2021, 2, 4, 12, 5, 0)
t2 = datetime(2021, 5, 4, 12, 5, 0)
t3 = datetime(2021, 7, 4, 12, 5, 0)
r1 = ResultValue('{"er":2}')
r2 = ResultValue([23, [1, 2, -1]])
r3 = ResultValue(["coucou", [1, 2, -1]])
dat1 = (ES.dat_valueName, t1.isoformat())
dat2 = (ES.dat_valueName, [t1.isoformat(), t2.isoformat()])
dat3 = (ES.dat_valueName, [t1.isoformat(), t2.isoformat(), t3.isoformat()])
pdat3 = (ES.dat_valueName, [pt1.isoformat(), pt2.isoformat(), pt3.isoformat()])
prop1 = (ES.prp_valueName, prop_pm10)
prop2 = (ES.prp_valueName, [prop_pm25, prop_pm10])
pprop2 = (ES.prp_valueName, [pprop_pm25, pprop_pm10])
loc1 = (ES.loc_valueName, paris)
loc3 = (ES.loc_valueName, [paris, lyon, marseille])
ploc3 = (ES.loc_valueName, [pparis, plyon, pmarseille])

def option_simple(ob1):
    ob1.option["json_ESobs_class"] = False
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

    def test_ResultValue(self):
        self.assertEqual(ResultValue("coucou").json(True), '["coucou", [-1, -1, -1]]')
        self.assertEqual(ResultValue("coucou").json(False), '"coucou"')
        self.assertEqual(ResultValue(["coucou", [1, 2, -1]]).json(False), '"coucou"')
        self.assertEqual(ResultValue(["coucou", [1, 2, -1]]).json(True), '["coucou", [1, 2, -1]]')
        self.assertEqual(ResultValue("coucou", [1, 2, -1]).json(True), '["coucou", [1, 2, -1]]')
        self.assertEqual(ResultValue('{"er":2}', [1, 2, -1]).json(True), '[{"er": 2}, [1, 2, -1]]')
        self.assertEqual(ResultValue('{"er":2}').json(True), '[{"er": 2}, [-1, -1, -1]]')
        self.assertEqual(ResultValue('{"er":2}').json(False), '{"er": 2}')
        self.assertEqual(ResultValue('[{"er":2}, [1, 2, -1]]').json(False), '{"er": 2}')
        self.assertEqual(ResultValue('[3,2]', [1, 2, -1]).json(True), '["[3, 2]", [1, 2, -1]]') 
        self.assertEqual(ResultValue('[3,2]').json(True), '["[3, 2]", [-1, -1, -1]]')
        self.assertEqual(ResultValue(21).json(True), '[21, [-1, -1, -1]]')
        self.assertEqual(ResultValue(22).json(False), '22')
        self.assertEqual(ResultValue([23, [1, 2, -1]]).json(False), '23')
        self.assertEqual(ResultValue([23, [1, 2, -1]]).json(True), '[23, [1, 2, -1]]')
        self.assertEqual(ResultValue(23, [1, 2, -1]).json(True), '[23, [1, 2, -1]]')
        self.assertEqual(ResultValue(2.1).json(True), '[2.1, [-1, -1, -1]]')
        self.assertEqual(ResultValue(2.2).json(False), '2.2')
        self.assertEqual(ResultValue([2.3, [1, 2, -1]]).json(False), '2.3')
        self.assertEqual(ResultValue([2.3, [1, 2, -1]]).json(True), '[2.3, [1, 2, -1]]') 

    def test_locationValue(self):
        self.assertEqual(LocationValue(lyon).json(True), json.dumps(lyon)) 
        self.assertEqual(ESValue.mini(LocationValue(lyon), LocationValue(paris)).json(True), json.dumps(mini_PL)) 

    def test_timeValue(self):
        self.assertEqual(TimeValue(t1).json(True), t1.isoformat()) 
        self.assertEqual(ESValue.maxi(TimeValue(t1), TimeValue(t2)).json(True), t2.isoformat()) 

    def test_propertyValue(self):
        self.assertEqual(PropertyValue().json(True), '{}') 
        self.assertEqual(PropertyValue({ES.prp_propType : "PM25"}).json(True), '{"'+ES.prp_propType+'": "PM25"}') 

    def test_ESSet(self):
        self.assertEqual(ESSet(TimeValue, [t1, t2, t3])[2], ESSet(TimeValue, [t1, t2, t3]).maxiBox()) 
        self.assertEqual(ESSet(LocationValue, [paris, lyon, marseille]).maxiBox(), LocationValue(maxi_PLM)) 
        self.assertEqual(ESSet(PropertyValue, [prop_pm10, prop_pm25]).jsonSet(True), json.dumps([prop_pm10, prop_pm25])) 
        self.assertEqual(ESSet(LocationValue, [LocationValue(paris)]).maxiBox(), LocationValue(paris)) 

    def test_ESObs(self):
        da1 = ESSetDatation(Observation(), {ES.dat_valueName:[t1, t2, t3]})
        self.assertEqual(da1[2], da1.maxiBox()) 
        da2 = ESSetProperty(Observation(), {ES.prp_valueName:[prop_pm10, prop_pm25]})
        self.assertEqual(json.loads('{'+da2.json(False, False, False)+'}')[ES.prp_valueName], [prop_pm10, prop_pm25]) 
        da3 = ESSetResult(Observation(), {ES.res_valueName:[r2, r2]})
        self.assertEqual(json.loads('{'+da3.json(False, False, False)+'}')[ES.res_valueName], r2.value)
        da4 = ESSetLocation(Observation(), {ES.loc_valueName:[paris, lyon, marseille]})
        self.assertEqual(da4.maxiBox(), LocationValue(maxi_PLM)) 
        
    def test_ESElement(self):
        el = ESElement()
        el2 = ESElement()
        el2.setAtt('tric', 'meoc')
        el.setAtt('truc', 'mec')
        el.addComposant(el2)
        self.assertTrue(el.element('tric') == None)
        self.assertFalse(el.element('null') == None)


@unittest.skipIf(simple, "test observation")
class TestObservation(unittest.TestCase):

    def test_obs_simple(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3)),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, loc3))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, loc3)),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, prop2))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, prop2)),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, res_(9)))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, res_(9))),    json.loads(ob1.json()))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
        option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9))),json.loads(ob1.json()))
        
    def test_obs_options(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
        option_simple(ob1)
        ob1.option["json_res_index"] = True
        self.assertEqual(json.loads(ob1.json())[ES.res_valueName][0], [val_(9)[0], [-1, -1, -1]])
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
            self.assertTrue(ob.score == 0 and not ob.complet)
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
            self.assertTrue(ob.score == 100 and ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 101 and ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 102 and not ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 110 and ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc1, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 111 and ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc1, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 112 and not ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 120 and not ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3, dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 121 and not ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3, dat3))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 122 and not ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(1), loc3, dat2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 122 and not ob.complet and ob.setResult.dim == 0)
            ob = Observation(json.dumps(dict((obs_1, res_(9)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 200 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(9), dat1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 201 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(3), dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 202 and ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(6), dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 202 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(3), loc1, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 210 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(3), loc1, dat1, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 211 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(3), loc1, dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 212 and ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(6), loc1, dat3, prop1))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 212 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(6), loc3, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 220 and ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(9), loc3, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 220 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(9), loc3, dat1, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 221 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, res_(6), loc3, dat1, prop2))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 221 and ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 222 and ob.complet and ob.setResult.dim == 2)
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 222 and not ob.complet and ob.setResult.dim == 1)
            ob = Observation(json.dumps(dict((obs_1, dat3, loc3, prop2, res_(6)))))
            majType_avec_option(ob, maj_index)
            self.assertTrue(ob.score == 222 and ob.complet and ob.setResult.dim == 1)
            #envoi_mongo(ob)
            #ob.option["json_res_index"] = True
            #print(ob.json(), '\n')

    def test_obs_creation(self):
        obs1 = Observation()
        self.assertEqual(obs1.classES,              ES.obs_classES)
        self.assertEqual(ESSetDatation(obs1).classES,    ES.dat_classES)
        self.assertEqual(ESSetResult(obs1).classES,      ES.res_classES)
        self.assertEqual(ESSetProperty(obs1).classES,    ES.prp_classES)
        self.assertEqual(ESSetLocation(obs1).classES,    ES.loc_classES)
      
        ob = Observation(json.dumps(dict([obs_1, res_(9)])))
        self.assertEqual(json.loads(ob.json())[ES.res_valueName], val_(9))

    def test_obs_add(self):
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(18)))))
        obp = Observation(json.dumps(dict((obs_1, truc_mach, pdat3, ploc3, pprop2, res_(18)))))
        obc = copy(ob)
        obc += ob
        self.assertEqual(json.loads(ob.json())[ES.res_valueName], json.loads(obc.json())[ES.res_valueName])
        self.assertEqual(json.loads(ob.json())[ES.dat_valueName], json.loads(obc.json())[ES.dat_valueName])
        self.assertEqual(json.loads(ob.json())[ES.loc_valueName], json.loads(obc.json())[ES.loc_valueName])
        self.assertEqual(json.loads(ob.json())[ES.prp_valueName], json.loads(obc.json())[ES.prp_valueName])
        ob2 = ob + ob
        self.assertEqual(json.loads(ob.json())[ES.res_valueName], json.loads(ob2.json())[ES.res_valueName])
        self.assertEqual(json.loads(ob.json())[ES.dat_valueName], json.loads(ob2.json())[ES.dat_valueName])
        self.assertEqual(json.loads(ob.json())[ES.loc_valueName], json.loads(ob2.json())[ES.loc_valueName])
        self.assertEqual(json.loads(ob.json())[ES.prp_valueName], json.loads(ob2.json())[ES.prp_valueName])
        obc = copy(ob)
        obc += obp
        self.assertEqual(json.loads(ob.json())[ES.res_valueName] + json.loads(obp.json())[ES.res_valueName], 
                         json.loads(obc.json())[ES.res_valueName])
        self.assertEqual(json.loads(ob.json())[ES.dat_valueName] + json.loads(obp.json())[ES.dat_valueName],
                         json.loads(obc.json())[ES.dat_valueName])
        self.assertEqual(json.loads(ob.json())[ES.loc_valueName] + json.loads(obp.json())[ES.loc_valueName],
                         json.loads(obc.json())[ES.loc_valueName])
        self.assertEqual(json.loads(ob.json())[ES.prp_valueName] + json.loads(obp.json())[ES.prp_valueName],
                         json.loads(obc.json())[ES.prp_valueName])
        ob2 = ob + obp
        self.assertEqual(json.loads(ob.json())[ES.res_valueName] + json.loads(obp.json())[ES.res_valueName], 
                         json.loads(ob2.json())[ES.res_valueName])
        self.assertEqual(json.loads(ob.json())[ES.dat_valueName] + json.loads(obp.json())[ES.dat_valueName],
                         json.loads(ob2.json())[ES.dat_valueName])
        self.assertEqual(json.loads(ob.json())[ES.loc_valueName] + json.loads(obp.json())[ES.loc_valueName],
                         json.loads(ob2.json())[ES.loc_valueName])
        self.assertEqual(json.loads(ob.json())[ES.prp_valueName] + json.loads(obp.json())[ES.prp_valueName],
                         json.loads(ob2.json())[ES.prp_valueName])
        obp2 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, pprop2, res_(18)))))
        ob2 = ob + obp2
        self.assertEqual(json.loads(ob.json())[ES.res_valueName] + json.loads(obp.json())[ES.res_valueName], 
                         json.loads(ob2.json())[ES.res_valueName])
        self.assertEqual(json.loads(ob.json())[ES.dat_valueName], json.loads(ob2.json())[ES.dat_valueName])
        self.assertEqual(json.loads(ob.json())[ES.loc_valueName], json.loads(ob2.json())[ES.loc_valueName])
        self.assertEqual(json.loads(ob.json())[ES.prp_valueName] + json.loads(obp2.json())[ES.prp_valueName],
                         json.loads(ob2.json())[ES.prp_valueName])

    def test_obs_extend(self):
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2))))
        obp = Observation(json.dumps(dict((obs_1, res_(18)))))
        ob.extend(obp)
        self.assertEqual(json.loads(ob.json())[ES.res_valueName], json.loads(obp.json())[ES.res_valueName])
        ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2))))
        obp = Observation(json.dumps(dict((obs_1, ploc3, res_(18)))))
        obc = copy(ob)
        ob.extend(obp)
        self.assertEqual(json.loads(ob.json())[ES.loc_valueName], json.loads(obc.json())[ES.loc_valueName])

    def test_sensor(self):
        obs = Observation()
        nprop1 = obs.addValue(PropertyValue(prop_pm25))
        for i in range(6): # simule une boucle de mesure
            nres = obs.addValueSensor(ResultValue(45+i), 
                                TimeValue(datetime(2021, 6, 4+i, 12, 5).isoformat()),
                                LocationValue([14+i, 40]),
                                nprop1)
        obs.majType()
        obs.option["json_ESobs_class"] = True
        obs.option["json_elt_type"] = True
        self.assertEqual(json.loads(obs.json())[ES.information]["typeobs"], "obsPath")
        
    def test_geo_interface(self):
        ob = Observation(json.dumps(dict([obs_1, loc3])))
        res_loc = (tuple(paris), tuple(lyon), tuple(marseille))
        res_geo = dict([(ES.type,ES.multi+ES.loc_valueType), (ES.loc_valueName,res_loc)])
        self.assertEqual(ob.__geo_interface__, res_geo)
        self.assertEqual(ob.__geo_interface__[ES.loc_valueName], res_loc)

    def test_obs_polygon(self):
        ob = Observation(json.dumps(dict((obs_1, dat3, dpt2, prop2, res_(6)))))
        self.assertEqual(json.dumps(ob.__geo_interface__), 
                         json.dumps({"type": "MultiPolygon", "coordinates": dpt2[1]}))
        
    def test_exports(self):
        ob = Observation(json.dumps(dict((obs_1, dat3, dpt3, prop2, res_(6)))))
        ob.majType()
        self.assertTrue(ob.choropleth() != None)
        self.assertTrue(type(ob.to_dataFrame()) != type(None))
        self.assertTrue(type(ob.to_xarray()) != type(None))
        self.assertTrue(type(ob.to_geoDataFrame()) != type(None))
        self.assertTrue(ob.jsonFeature != '')


if __name__ == '__main__':
    unittest.main(verbosity=2)