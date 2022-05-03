# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `ES.test_observation` module contains the unit tests (class unittest) for all the
Environmental Sensing functions.
"""
import unittest

#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from ESValue import ResultValue, LocationValue, DatationValue, ESValue,\
    PropertyValue
from ESObservation import Observation
from ESconstante import ES
import json, copy #, shapely
import requests as rq
import datetime
#from datetime import datetime
from ilist import Ilist
from pymongo import MongoClient


# couverture tests (True if non passed)----------------------------------------
simple  = False  # False
plot    = True  # True
mongo   = True  # True

# datas-----------------------------------------------------------------------
def _val(n): return list(i for i in range(n))
def _res(n): return (ES.res_classES, _val(n))
def _dat(n): return (ES.dat_classES, [datetime.datetime(2000+i, 2, 4, 12, 5, 0) for i in range(n)])
def _loc(n): return (ES.loc_classES, [[5+i, 20+i] for i in range(n)])
with open('C:\\Users\\a179227\\OneDrive - Alliance\\perso Wx\\ES standard\\python ESstandard\\departements-version-simplifiee.geojson') as f:
    dp = f.read()
dpt = json.loads(dp)['features']
#https://github.com/gregoiredavid/france-geojson
pol13 = {dpt[12]['properties']['code'] + ' ' + dpt[12]['properties']['nom'] :
         dpt[12]['geometry']['coordinates']}
pol69 = {dpt[69]['properties']['code'] + ' ' + dpt[69]['properties']['nom'] :
         dpt[69]['geometry']['coordinates']}
pol75 = {dpt[75]['properties']['code'] + ' ' + dpt[75]['properties']['nom'] :
         dpt[75]['geometry']['coordinates']}
pol1 = [[[0.0,1.0], [1.0,2.0], [1.0,1.0], [0.0,1.0]]]
pol1centre = [0.6666666666666666, 1.3333333333333333]
pol2 = [[[0.0,2.0], [2.0,2.0], [1.0,1.0], [0.0,2.0]]]
dpt2 = (ES.loc_classES, [pol1, pol2])
dpt3 = (ES.loc_classES, [pol75, pol69, pol13])
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
prop_pm25   = dict([(ES.prp_type,"PM25"), (ES.prp_unit, "kg/m3")])
prop_pm10   = dict([(ES.prp_type,"PM10"), (ES.prp_unit, "kg/m3")])
prop_co2    = dict([(ES.prp_type,"CO2"), (ES.prp_unit, "kg/m3")])
pprop_pm25   = dict([(ES.prp_type,"PM25"), (ES.prp_unit, "kg/m3"), (ES.prp_appli, "air")])
pprop_pm10   = dict([(ES.prp_type,"PM10"), (ES.prp_unit, "kg/m3"), (ES.prp_appli, "air"), ("truc", "machin")])
matin = [ datetime.datetime(2020, 2, 4, 8), datetime.datetime(2020, 2, 4, 12)]
midi  = [ datetime.datetime(2020, 2, 4, 12), datetime.datetime(2020, 2, 4, 14)]
aprem  = [ datetime.datetime(2020, 2, 4, 14), datetime.datetime(2020, 2, 4, 18)]
travail = [matin, aprem]
pt1 = datetime.datetime(2020, 2, 4, 12, 5, 0)
pt2 = datetime.datetime(2020, 5, 4, 12, 5, 0)
pt3 = datetime.datetime(2020, 7, 4, 12, 5, 0)
tnull = datetime.datetime(1970, 1, 1, 0, 0, 0)
snull = (tnull.isoformat(), tnull.isoformat())
t1 = datetime.datetime(2021, 2, 4, 12, 5, 0)
t1n = json.dumps({'date1' : t1.isoformat()})
t2 = datetime.datetime(2021, 7, 4, 12, 5, 0)
t3 = datetime.datetime(2021, 5, 4, 12, 5, 0)
r1 = ResultValue('{"er":2}')
r2 = ResultValue(23)
r3 = ResultValue("coucou")
r4 = ResultValue(41.2)
r5 = ResultValue(18)
#r6 = ResultValue([41, [2, 2, 0]])
#r7 = ResultValue([18, [1, 2, 1]])
s1 = [t1, t2]
dat1 = (ES.dat_classES, {'date1' : t1.isoformat()})
dat2 = (ES.dat_classES, [t1.isoformat(), t2.isoformat()])
dat3 = (ES.dat_classES, [{'date1' : t1.isoformat()}, t2.isoformat(), t3.isoformat()])
dat3ord = (ES.dat_classES, [{'date1' : t1.isoformat()}, t3.isoformat(), t2.isoformat()])
dat3sn = (ES.dat_classES, [t1.isoformat(), t2.isoformat(), t3.isoformat()])
pdat3 = (ES.dat_classES, [pt1.isoformat(), pt2.isoformat(), pt3.isoformat()])
prop1 = (ES.prp_classES, prop_pm10)
prop2 = (ES.prp_classES, [prop_pm25, prop_pm10])
prop2ord = (ES.prp_classES, [prop_pm10, prop_pm25])
prop3 = (ES.prp_classES, [prop_pm25, prop_pm10, prop_co2])
pprop2 = (ES.prp_classES, [pprop_pm25, pprop_pm10])
loc1 = (ES.loc_classES, {'paris' : paris})
loc1sn = (ES.loc_classES, paris)
loc2 = (ES.loc_classES, [paris, lyon])
loc3 = (ES.loc_classES, [{'paris' : paris}, lyon, marseille])
loc3sn = (ES.loc_classES, [paris, lyon, marseille])
ploc3 = (ES.loc_classES, [pparis, plyon, pmarseille])
res2 = (ES.res_classES, [[41, [2, 2, 0]], [18, [1, 2, 1]]])

'''reslist = [ResultValue(21, 'test'), ResultValue(22, 'test2'),
           ResultValue(23, 'test3'), ResultValue(24, 'test4')]
ir5 = ResultValue(25)

resind = [[0,2,3,1], [2,1,3,0], [0,1,2,3]]
setres = ESIlistSet([reslist, resind]) '''

def _option_simple(ob1):
    ob1.option["json_param"]            = True
    ob1.option["json_res_index"]        = False
    ob1.option["json_info_type"]        = False
    ob1.option["json_info_nval"]        = False
    ob1.option["json_info_autre"]       = False
    ob1.option["json_info_box"]         = False
    ob1.option["json_info_res_classES"] = False

def _envoi_mongo_url(data):
    url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
    r = rq.post(url, data=data)
    print("réponse : ", r.text, "\n")
    return r.status_code

def _envoi_mongo_python(data):
    user        = 'ESobsUser'
    pwd         = 'observation'
    site        = 'esobs.gwpay.mongodb.net/test'

    st = 'mongodb+srv://' + user +':' + pwd + '@' + site + \
            '?' + 'authSource=admin' + \
            '&' + 'replicaSet=atlas-13vws6-shard-0' + \
            '&' + 'readPreference=primary' + \
            '&' + 'appname=MongoDB%20Compass' + \
            '&' + 'ssl=true'
    client  = MongoClient(st)

    baseMongo   = 'test_obs'
    collection  = 'observation'
    collec  = client[baseMongo][collection]
    return collec.insert_one(data).inserted_id
    #try : return collec.insert_one(data).inserted_id
    #except : return None

def _indic(res):
    return [res.json(bjson_format=True, bjson_bson=False, json_res_index=True),
            res.dim, res.nMax,
            res.nInd, res.axes, res.maxIndex, res.isextIndex, res.measureRate,
            res.error, res.vListIndex, res.nValue, res.vListName, res.vListValue
            ,_sort(res)]

def _sort(res):
    li = res.sort()
    if type(li[0]) == int : return li
    else : return res.vListValue

class TestExemples(unittest.TestCase):      # !!! exemples
    def test_first_observation(self) :
        # cas simple + présentation
        ob=Observation(('morning', 'paris', ' Temp', 'high'))
        ob.append('morning', 'lyon', ' Temp', 'low')
        ob.append('morning', 'marseille', ' Temp', 'very high')
        #ob.view(True, False, False, False)
        #ob.voxel()
        ob.majList(ResultValue, [25, 10, 35])
        #ob.plot()
        # valeur numériques + choropleth
        #print(ob.setLocation)
        #ob.majList(LocationValue, [lyon, marseille, paris])
        ob.majList(LocationValue, [paris, lyon, marseille])
        #ob.view(True, False, True, False)
        '''choro = ob.choropleth()'''       # !!! à voir
        #choro.save("test.html")
        print(ob.setLocation)
        ob.majList(LocationValue, [pol75, pol69, pol13])
        #ob.view(True, False, True, False)
        '''choro = ob.choropleth()'''       # !!! à voir
        #choro.save("test.html")
        # ajout dimension 2, infos globales
        ob.append('morning', 'paris', 'Humidity', 30, equal='name')
        ob.append('morning', 'marseille', 'Humidity', '60', equal='name')
        #ob.view(True, False, False, False)
        #ob.voxel()
        #ob.plot()
        # ajout dimension 3 + export dataarray, dataframe
        ob.append('afternoon', 'paris', ' Temp', 28, equal='name')
        ob.append('afternoon', 'lyon', ' Temp', 15, equal='name')
        ob.majList(LocationValue, [paris, lyon, marseille])   # i.e. paris = [2.35, 48.87]
        #print(ob.setDatation)
        ob.majList(DatationValue, ["2021-05-05T10", "2021-05-05T16"])
        ob.view(prp=False, width=15)
        ob.voxel()
        ob.plot()
        print(ob.to_xarray(numeric=True))
        #pprint(json.loads(ob.json), indent=2)
        #ob._info(string=False)

    '''def test_observation_for_sensor(self) :

        #Case 1: Simple sensor
        time = "2021-05-05T10:08"
        coord = [2.35, 48.87]
        prop = {"prp":"Temp"}
        res = 25.0
        # Observation creation and encoding to Json or to binary data in the sensor
        ob_sensor = Observation((time, coord, prop, res))
        payload1 = ob_sensor.to_json()           # if the payload is character payload
        #print(len(payload1), payload1)
        payload2 = ob_sensor.to_bytes()     # if the payload is binary payload
        #print(len(payload2), payload2)
        # data decoding in the server
        ob_receive1 = Observation()
        ob_receive1.from_json(payload1)
        ob_receive2 = Observation()
        ob_receive2.from_bytes(payload2)
        print(ob_receive2.json == ob_receive1.json == ob_sensor.json)   # it's True !!
        # and store it in the database (example with NoSQL DataBase)
        jsonStore = ob_receive1.to_json(storage=True)    # add 'information' in the json to facilitate the research in the database
        #pprint(json.loads(jsonStore))
        #url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
        #r = rq.post(url, data=jsonStore)
        #print("réponse : ", r.status_code, "\n")

        #case 2 : minimize data in operation
        # initialization phase (sensor or server) -> once
        coord = [2.35, 48.87]
        prop = {"prp":"Temp"}
        ob_init = Observation(location=coord, property=prop)
        #print(ob_init.json)
        # operation phase (sensor) -> regularly
        res = 25.0
        ob_operat = Observation(result=res)
        payload1 = ob_operat.to_json()           # if the payload is character payload
        #print(len(payload1), payload1)
        payload2 = ob_operat.to_bytes()     # if the payload is binary payload
        #print(len(payload2), payload2)      # the payload is only 4 bytes long !!
        # data decoding in the server
        ob_receive1 = Observation()
        ob_receive1.from_json(payload1)
        ob_receive2 = Observation()
        ob_receive2.from_bytes(payload2)
        print(ob_receive1.json == ob_receive2.json == ob_operat.json)   # it's True !!
        # complete observation
        ob_receive2.addValue(DatationValue(datetime.now()))
        ob_receive2.extend(ob_init)
        #print(ob_receive2.json)'''

@unittest.skipIf(simple, "test Observation")
class TestObservation(unittest.TestCase):           # !!! test observation
    '''Unit tests for `ES.ESObservation.Observation` '''

    def test_obs_creation(self):
        ob = Observation(json.dumps(dict([obs_1, _res(9)])))
        self.assertEqual(ob.to_json(bjson_format=False)[ES.res_classES], _val(9))

        ob  = Observation(dict((obs_1, dat1, loc1, prop3, _res(3))), order=['location', 'datation', 'property'])
        ob1 = Observation(dict((dat1, loc1, prop3, _res(3))), order=['location', 'datation', 'property'])
        ob2 = Observation({dat1[0] : dat1[1]}, {loc1[0]:loc1[1]}, {prop3[0]:prop3[1]},
                          {_res(3)[0]:_res(3)[1]})
        ob3 = Observation(datation=dat1[1], location=loc1[1], property=prop3[1],
                              result=_res(3)[1])
        ob5 = Observation([[dat1[1]], [loc1[1]], prop3[1], _res(3)[1]])
        ob6 = Observation(datation=[dat1[1]], location=[loc1[1]],
                          property=prop3[1], result=_res(3)[1])
        ob7 = Observation([[dat1[1]], [loc1[1]], prop3[1], _res(3)[1]], datation=[dat1[1]])
        ob8 = Observation({dat1[0] : dat1[1]}, {loc1[0]:loc1[1]}, {prop3[0]:prop3[1]},
                          {_res(3)[0]:_res(3)[1]}, location=loc2[1])
        self.assertTrue(ob.json  == ob1.json == ob2.json == ob3.json == # ob4.json ==
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
        ob=Observation()
        ob.addJson(json.dumps(dict((obs_1, _res(3), dat3))))
        ob1 = Observation(json.dumps(dict((obs_1, _res(3), dat3))))
        self.assertEqual(ob.json, ob1.json)
        res = ('result', [{'file':'truc', 'path':'ertert'}, 1,2,3,4,['truc', 'rt']])
        ob = Observation(dict((obs_1, loc3, dat3, prop2, res)), idxref={'location':'datation'})
        self.maxDiff = None 
        self.assertEqual(ob.to_json(bjson_format=False), Observation(ob.json).to_json(bjson_format=False))

    def test_obs_loc_iloc_maj(self):
        ob = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'}, order=['datation', 'property', 'location'])
        self.assertEqual(ob.iLoc(1,1,1), ob.loc(dat3[1][1], loc3[1][1], prop2[1][1]))
        ob.majValue(LocationValue(loc3[1][1]), loc3[1][2])
        self.assertEqual(ob.setLocation[1], ob.setLocation[2])
        self.assertEqual(ob.indexLoc(ResultValue(5), string=False)["full"], 5)
        self.assertEqual(ob.indexLoc(DatationValue("2021-02-04T12:05:00"), string=False)["value"], 0)
        self.assertEqual(ob.indexLoc(LocationValue("paris"), string=False)["name"], 0)

    def test_obs_vList(self):
        ob1 = Observation(dict((truc_mach, dat3, loc3)))
        self.assertEqual(ob1.vListName('datation')[0], 'date1')
        self.assertEqual(ob1.vListName('datation')[1], 'dat1')
        self.assertEqual(ob1.vListSimple('location'), [paris, lyon, marseille])
        self.assertEqual(ob1.vListSimple('datation'), [t1, t2, t3])
        ob1 = Observation(dict((truc_mach, dat3, dpt2)))
        self.assertEqual(ob1.vListSimple('location')[0], pol1centre)
        ob = Observation(dict((obs_1, dat3, dpt3, prop2, _res(6))), idxref={'location':'datation'}, order=['location', 'property', 'datation'])
        self.assertEqual(ob.vListName('result')[0], 'res0')
        self.assertEqual(ob.vListValue('result')[4], 4)

    def test_obs_simple(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3))))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, dat3)),    ob1.to_json(bjson_format=False))
        ob1 = Observation(dict((obs_1, truc_mach, loc3)))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, loc3)),    ob1.to_json(bjson_format=False))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, prop2))))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, prop2)),    ob1.to_json(bjson_format=False))
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, _res(9)))))
        _option_simple(ob1)
        self.assertEqual(dict((obs_1, truc_mach, _res(9))), ob1.to_json(bjson_format=False))
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'})
        dic=ob1.to_json(bjson_format=False)
        dic.pop('index')
        self.assertEqual(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6))), dic)

    def test_obs_att(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2,
                               (ES.obs_reference, 25), (ES.prp_upperValue,'254'),
                                           _res(6))), idxref={'location':'datation'})
        self.assertEqual(ob1.mAtt['truc'], 'machin')
        self.assertEqual(ob1.mAtt[ES.obs_reference], 25)
        self.assertEqual(ob1.mAtt[ES.prp_upperValue], '254')

    def test_obs_options(self):
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6)))), idxref={'location':'datation'})
        self.assertTrue(Observation(ob1.to_json(),idxref={'location':'datation'}), ob1.to_json())
        _option_simple(ob1)
        ob1.option["json_res_index"] = True
        ob1.option["json_info_type"] = True
        ob1.option["json_info_nval"] = True
        ob1.option["json_info_other"] = True
        ob1.option["json_info_box"] = True
        ob2 = Observation(ob1.to_json())
        ob2.option = ob1.option
        self.assertTrue(ES.type in json.loads(ob2.to_json()))
        self.assertEqual(ob2.to_json(bjson_format=False, bjson_bson=False), ob1.to_json(bjson_format=False, bjson_bson=False))

    def test_obs_maj_type(self):
        maj = [False, True]
        for maj_index in maj:
            ob = Observation()
            self.assertTrue(ob.score == 0 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, dat1))))
            self.assertTrue(ob.score == 1 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, dat3))))
            self.assertTrue(ob.score == 2 and not ob.complet )
            ob = Observation(json.dumps(dict((obs_1, loc1))))
            self.assertTrue(ob.score == 10 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc1, dat1))))
            self.assertTrue(ob.score == 11 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc1, dat3))))
            self.assertTrue(ob.score == 12 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3))))
            self.assertTrue(ob.score == 20 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3, dat1))))
            self.assertTrue(ob.score == 21 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, loc3, dat3))))
            self.assertTrue(ob.score == 22 and not ob.complet)
            ob = Observation(json.dumps(dict((obs_1, _res(1)))))
            self.assertTrue(ob.score == 0 and ob.complet and ob.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), dat1))))
            self.assertTrue(ob.score == 1 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(3), dat3))))
            self.assertTrue(ob.score == 2 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1))))
            self.assertTrue(ob.score == 10 and ob.complet and ob.axes == [1])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1, dat1))))
            self.assertTrue(ob.score == 11 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc1, dat3))))
            self.assertTrue(ob.score == 12 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc3))))
            self.assertTrue(ob.score == 20 and ob.complet and ob.axes == [1])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc3, dat1))))
            self.assertTrue(ob.score == 21 and ob.complet and ob.axes == [1])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc3, dat3))), idxref={'location': 'datation'})
            self.assertTrue(ob.score == 22 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(6), loc3, dat2))))
            self.assertTrue(ob.score == 23 and ob.complet and ob.axes == [0,1])
            ob = Observation(json.dumps(dict((obs_1, _res(9)))))
            self.assertTrue(ob.score == 0 and ob.complet and ob.axes == [])
            #ob = Observation(json.dumps(dict((obs_1, _res(9), dat1))))
            #self.assertTrue(ob.score == 1 and not ob.complet and ob.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(3), dat3, prop1))))
            self.assertTrue(ob.score == 102 and ob.complet and ob.axes == [0])
            #ob = Observation(json.dumps(dict((obs_1, _res(6), dat3, prop1))))
            #self.assertTrue(ob.score == 102 and not ob.complet and ob.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1, prop1))))
            self.assertTrue(ob.score == 110 and ob.complet and ob.axes == [1])
            ob = Observation(json.dumps(dict((obs_1, _res(1), loc1, dat1, prop1))))
            self.assertTrue(ob.score == 111 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc1, dat3, prop1))))
            self.assertTrue(ob.score == 112 and ob.complet and ob.axes == [0])
            #ob = Observation(json.dumps(dict((obs_1, _res(6), loc1, dat3, prop1))))
            #self.assertTrue(ob.score == 112 and not ob.complet and ob.axes == [])
            ob = Observation(json.dumps(dict((obs_1, _res(6), loc3, prop2))))
            self.assertTrue(ob.score == 223 and ob.complet and ob.axes == [1, 2])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc3, prop3))), idxref={'location': 'property'})
            self.assertTrue(ob.score == 220 and ob.complet and ob.axes == [1])
            ob = Observation(json.dumps(dict((obs_1, _res(3), loc3, dat1, prop3))), idxref={'property':'location'})
            self.assertTrue(ob.score == 221 and ob.complet and ob.axes == [1])
            ob = Observation(json.dumps(dict((obs_1, _res(6), loc3, dat1, prop2))))
            self.assertTrue(ob.score == 224 and ob.complet and ob.axes == [1, 2])
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))))
            self.assertTrue(ob.score == 228 and ob.complet and ob.axes == [0, 1, 2])
            ob = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop3, _res(3)))), idxref={'property':'datation', 'location':'datation'})
            self.assertTrue(ob.score == 222 and ob.complet and ob.axes == [0])
            ob = Observation(json.dumps(dict((obs_1, dat3, loc3, prop2, _res(6)))), idxref = {'location': 'datation'})
            self.assertTrue(ob.score == 225 and ob.complet and ob.axes == [0, 2])
            #ob.option["json_res_index"] = True
            #print(ob.to_json(), '\n')

    def test_obs_dim(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat2, loc3, prop3, _res(6))), idxref={'property':'location'})
        self.assertTrue(ob1.score == 227 and ob1.complet and ob1.axes == [0, 1])
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc2, prop3, _res(6))), idxref={'property':'datation'})
        self.assertTrue(ob1.score == 226 and ob1.complet and ob1.axes == [0, 1])
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop3, _res(3))), idxref={'property':'datation', 'location':'datation'})
        self.assertTrue(ob1.score == 222 and ob1.complet and ob1.axes == [0])

    def test_obs_majListName_majListValue(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18))))
        ob1.majList(LocationValue, [pparis, plyon, pmarseille], name=False)
        self.assertEqual(ob1.setLocation[2].vSimple(), pmarseille)
        ob1.majList(DatationValue, [pt1, pt2, pt3], name=False)
        self.assertEqual(ob1.setDatation[2].simple, pt3)
        ob1.majList(LocationValue, ['paris', 'lyon', 'marseille'], 'name')
        self.assertEqual(ob1.setLocation[2].name, 'marseille')

    def test_obs_majIndex_iLoc(self):
        ob1 = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18))))
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))), order=['location', 'property',  'datation'])
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18)))), order=['property',  'datation', 'location'])
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '9')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6)))), idxref={'location':'datation'}, order=['datation', 'property', 'location'])
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6)))), idxref={'location':'datation'}, order=['location', 'property', 'datation'])
        self.assertEqual(ob1.iLoc(0,0,1)[ES.res_classES], '1')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat2, loc3, prop3, _res(6)))), idxref={'property':'location'}, order=['location', 'datation', 'property'])
        self.assertEqual(ob1.iLoc(0,1,1)[ES.res_classES], '2')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc2, prop3, _res(6)))), idxref={'property':'datation'}, order=['location', 'datation', 'property'])
        self.assertEqual(ob1.iLoc(0,1,0)[ES.res_classES], '3')
        ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop3, _res(3)))), idxref={'property':'datation', 'location':'datation'})
        self.assertEqual(ob1.iLoc(1,1,1)[ES.res_classES], '1')

    def test_append_obs(self):
        ob = Observation(dict((obs_1, dat3, dpt3, prop2, _res(6))), idxref={'location':'datation'})
        ob1 = copy.copy(ob)
        ind = ob1.appendObs(ob)
        self.assertEqual(ob1.setResult[ind].value, ob)
        self.assertEqual(ob1.setLocation[ob1.iObsIndex(ind)[1]].value, ob.bounds[1].value) # ordre changeant
        ob1=Observation()
        ob1.appendObs(ob)
        ob2=Observation(ob1.to_json(bjson_bson=True, bjson_format=False))
        self.assertEqual(ob2.to_json(bjson_bson=True, bjson_format=False),
                         ob1.to_json(bjson_bson=True, bjson_format=False))
        ob2=Observation(ob1.to_json(bjson_bson=False, bjson_format=False))
        self.assertEqual(ob2.to_json(bjson_bson=False, bjson_format=False),
                         ob1.to_json(bjson_bson=False, bjson_format=False))
        ob2=Observation(ob1.json)
        self.assertEqual(ob2.to_json(bjson_bson=False, bjson_format=False),
                         ob1.to_json(bjson_bson=False, bjson_format=False))

    def test_obs_sort(self):
        dic = {'type': 'observation',
               'datation': ['d1', 'c2', 'd3'],
               'location': ['l1', 'm2', 'l3'],
               'property': ['p2', 'p1'],
               'result': [10, 11, 12, 13, 14, 15]}
        ob = Observation(dic, idxref={'location':'datation'}, order=['location', 'property', 'datation'])
        self.assertEqual(ob.loc('d1','l1', 'p1')['result'], '11')
        ob.sort(order=['location','datation', 'property'])
        self.assertEqual(ob.loc('d1','l1', 'p1')['result'], '11')
        self.assertEqual(ob.vListName('location'), ['l1', 'l3', 'm2'])
        ob.sort(order=['datation','location', 'property'])
        self.assertEqual(ob.loc('d1','l1', 'p1')['result'], '11')
        self.assertEqual(ob.vListName('datation'), ['c2', 'd1', 'd3'])       
        ob.sort()
        self.assertEqual(ob.loc('d1','l1', 'p1')['result'], '11')
        self.assertEqual(ob.vListValue('result'), [10, 11, 12, 13, 14, 15])       
        ob.sort(order=['property', 'datation','location'])
        self.assertEqual(ob.loc('d1','l1', 'p1')['result'], '11')
        self.assertEqual(ob.vListName('property'), ['p1', 'p2'])       

        '''ob = Observation(dict((obs_1, dat3, dpt3, prop2, _res(6))), idxref={'location':'datation'}, order=['location', 'property', 'datation'])
        self.assertEqual(ob.vListValue('result'), [0, 1, 2, 3, 4, 5])
        ob.sort(order=['location','datation', 'property'])
        self.assertEqual(ob.vListValue('result'), [3, 0, 4, 1, 5, 2])
        ob.sort(order=['datation','location', 'property'])
        self.assertEqual(ob.vListValue('result'), [3, 0, 5, 2, 4, 1])
        ob.sort()
        self.assertEqual(ob.vListValue('result'), [0, 1, 2, 3, 4, 5])
        ob.sort(order=['property', 'datation','location'])
        self.assertEqual(ob.vListValue('result'), [3, 5, 4, 0, 2, 1])'''

    def test_obs_add(self):
        ob  = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(18))))
        ob.option["json_loc_name"] = ob.option["json_dat_name"] = ob.option["json_prp_name"] = True
        obp = Observation(dict((obs_1, truc_mach, pdat3, ploc3, pprop2, _res(18))))
        obp.option["json_loc_name"] = obp.option["json_dat_name"] = obp.option["json_prp_name"] = True
        obc = copy.copy(ob)
        obc.option["add_equal"] = "value"
        obc.option["json_loc_name"] = obc.option["json_dat_name"] = obc.option["json_prp_name"] = True
        obc.option["unic_index"] = True
        obc += ob
        self.assertEqual(ob.to_json(bjson_format=False)[ES.res_classES], json.loads(obc.to_json())[ES.res_classES])
        self.assertEqual(ob.to_json(bjson_format=False)[ES.dat_classES], json.loads(obc.to_json())[ES.dat_classES])
        self.assertEqual(ob.to_json(bjson_format=False)[ES.loc_classES], json.loads(obc.to_json())[ES.loc_classES])
        self.assertEqual(ob.to_json(bjson_format=False)[ES.prp_classES], json.loads(obc.to_json())[ES.prp_classES])
        ob2 = ob + ob
        self.assertEqual(ob.to_json(bjson_format=False)[ES.res_classES], json.loads(ob2.to_json())[ES.res_classES])
        self.assertEqual(ob.to_json(bjson_format=False)[ES.dat_classES], json.loads(ob2.to_json())[ES.dat_classES])
        self.assertEqual(ob.to_json(bjson_format=False)[ES.loc_classES], json.loads(ob2.to_json())[ES.loc_classES])
        self.assertEqual(ob.to_json(bjson_format=False)[ES.prp_classES], json.loads(ob2.to_json())[ES.prp_classES])
        obc = copy.copy(ob)
        obc += obp
        self.assertEqual(set(ob.setResult   + obp.setResult),   set(obc.setResult))
        self.assertEqual(set(ob.setDatation + obp.setDatation), set(obc.setDatation))
        self.assertEqual(set(ob.setLocation + obp.setLocation), set(obc.setLocation))
        self.assertEqual(set(ob.setProperty + obp.setProperty), set(obc.setProperty))
        ob2 = ob + obp
        self.assertEqual(set(ob.setResult   + obp.setResult),   set(ob2.setResult))
        self.assertEqual(set(ob.setDatation + obp.setDatation), set(ob2.setDatation))
        self.assertEqual(set(ob.setLocation + obp.setLocation), set(ob2.setLocation))
        self.assertEqual(set(ob.setProperty + obp.setProperty), set(ob2.setProperty))
        obp2 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, pprop2, _res(18)))))
        ob2 = ob + obp2
        self.assertEqual(set(ob.setResult   + obp.setResult),    set(ob2.setResult))
        self.assertEqual(set(ob.setDatation), set(ob2.setDatation))
        self.assertEqual(set(ob.setLocation), set(ob2.setLocation))
        self.assertEqual(set(ob.setProperty + obp2.setProperty), set(ob2.setProperty))


    def test_obs_full(self):
        ob=Observation('{"type": "observation", \
                       "datation": [{"date1": "2021-02-04T12:05:00"},"2021-07-04T12:05:00", "2021-05-04T12:05:00"], \
                       "location": [{"paris": [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]], \
                       "property": [{"prp": "PM25", "unit": "kg/m3"}, {"prp": "PM10", "unit": "kg/m3"}], \
                       "result": [0,1,2,3,4,5],\
                       "index": [[0,0,1,1,2,2],[0,0,2,1,1,2],[0,1,0,1,0,1]]}')
        ob1=ob.full(fillvalue=ResultValue(-1))
        self.assertEqual(ob.iLoc(1,2,0), ob1.iLoc(1,2,0))
        self.assertEqual(len(ob1), 18)
        ob.full(fillvalue=ResultValue(-1), inplace=True)
        self.assertEqual(ob.json, ob1.json)


    def test_obs_extend(self):
        obp = Observation(dict((_res(6), loc3, prop2)))
        obc = Observation(dict((_res(6), dat3, prop2)))
        ob  = Observation(dict((_res(6), dat3, loc3, prop2)), idxref={'location':'datation'})
        obcc = obp | obc
        self.assertEqual(obcc.ilist, ob.ilist)
        ob = Observation(dict((_res(6), obs_1)))
        ob.extend('datation', ['matin'], [0,0,0,0,0,0])
        ob.extend('location', ['paris', 'lyon', 'marseille'], [0,1,2,0,1,2])
        ob.extend('property', ['pm10', 'pm25'], [0,1,0,1,0,1])
        self.assertEqual(ob.axes, [1,2])
        self.assertTrue(ob.complet)

    def test_sensor(self):
        obs = Observation()
        prop1 = PropertyValue(prop_pm25)
        for i in range(6): # simule une boucle de mesure
            obs.append(DatationValue(datetime.datetime(2021, 6, 4+i, 12, 5).isoformat()),
                       LocationValue([14+i, 40]), prop1, ResultValue(45+i))
        #obs.majType()
        obs.option["json_info_type"] = True
        self.assertEqual(json.loads(obs.to_json())[ES.information]["typeobs"], ES.obsCat[122])

class TestImportExport(unittest.TestCase):
    '''Unit tests for `ES.ESObservation.Observation` import and export '''

    def test_file(self):
        res = ('result', [{'file':'truc', 'path':'ertert'}, 1,2,3,4,['truc', 'rt']])
        ob = Observation(dict((obs_1, loc3, dat3, prop2, res)), idxref={'location':'datation'})
        ob.to_file('test.obs', bjson_bson=True)
        self.assertEqual(Observation.from_file('test.obs').to_json(bjson_format=False),
                         ob.to_json(bjson_format=False))
        ob.to_file('test.obs', bjson_bson=False)
        self.assertEqual(Observation.from_file('test.obs').to_json(bjson_format=False),
                         ob.to_json(bjson_format=False))
    def test_bytes(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), 
                         idxref={'datation':'location'})        
        opt = {ES.dat_classES : ['name', 'value'], ES.loc_classES : ['name', 'value'],
               ES.prp_classES : ['name', 'value'], ES.res_classES : ['uint8']}
        self.assertEqual(ob.json, Observation.from_bytes(ob.to_bytes(opt)).json)
        ob = Observation({  'type': 'observation',
                            'datation': [{'date1': '2021-02-04T12:05:00'},
                                         '2021-07-04T12:05:00',
                                         '2021-05-04T12:05:00'],
                            'location': [{'paris': [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]],
                            'property': [{'prp': 'PM25', 'unit': 'kg/m3'},
                                         {'prp': 'PM10', 'unit': 'kg/m3'}],
                            'result': [0, 1, 2, 3, 4, 5],
                            'index': [[0, 1, 0, 1, 2, 2], [0, 0, 1, 1, 2, 2], 
                                      [0, 1, 0, 1, 0, 1]]})
        self.assertEqual(ob.json, Observation.from_bytes(ob.to_bytes(opt)).json)

        
class TestExports(unittest.TestCase):
    '''Unit tests for `ES.ESObservation.Observation` exports '''

    @unittest.skipIf(mongo, "test envoi mongo")
    def test__envoi_mongo(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'})
        data = ob.to_json(bjson_format=False, bjson_bson=True, json_info=True)
        self.assertFalse(_envoi_mongo_python(data)==None)
        data = ob.to_json(bjson_format=True, bjson_bson=False, json_info=True)
        self.assertEqual(_envoi_mongo_url(data), 200)

    def test_geo_interface(self):
        ob = Observation(dict([obs_1, loc3]))
        _resloc = (tuple(paris), tuple(lyon), tuple(marseille))
        _resgeo = dict([(ES.type,"MultiPoint"), ("coordinates",_resloc)])
        self.assertEqual(ob.__geo_interface__, _resgeo)
        self.assertEqual(ob.__geo_interface__["coordinates"], _resloc)
        self.assertEqual(ob.__geo_interface__, _resgeo)
        ob = Observation(dict((obs_1, dpt2, dat1)))
        dpt2pt = {'type': 'Polygon', 'coordinates': (((0.5, 1.5), (0.0, 2.0),
          (1.0, 2.0), (2.0, 2.0), (1.0, 1.0), (0.0, 1.0), (0.5, 1.5)),)}
        self.assertEqual(ob.__geo_interface__, dpt2pt)

    def test_obs_polygon(self):
        ob = Observation(dict((obs_1, dat3, dpt2, prop2, _res(6))), idxref={'property':'location'})
        self.assertEqual(ob.__geo_interface__, {'type': 'Polygon',
                         'coordinates': (((0.5, 1.5), (0.0, 2.0), (1.0, 2.0),
                          (2.0, 2.0), (1.0, 1.0), (0.0, 1.0), (0.5, 1.5)),)})

    def test_to_numpy(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'}, order=['location', 'property', 'datation'])
        self.assertEqual(ob.to_numpy(func=ResultValue.vSimple, string=True)[0][1,1], '4.0')
        self.assertEqual(ob.to_numpy(func=ResultValue.vSimple, string=False)[0][1,1], 4.0)
        self.assertEqual(ob.to_numpy(func=ESValue.vName, genName='-')[0][1,1], '-')
        self.assertEqual(ob.to_numpy(func=ResultValue.vSimple, string=True, ind='all')[0][2,1,1], '2.0')

    def test_xarray(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'})
        self.assertTrue(ob.to_xarray()[2,1].item() == ResultValue(2))
        self.assertTrue(ob.to_xarray(numeric=True)[2,1].item() == 2.0)
        self.assertTrue(ob.to_xarray(ind='all')[2,2,1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop1, _res(3))), idxref={'location':'datation'})
        self.assertTrue(ob.to_xarray()[1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop3, _res(3))), idxref={'property':'datation', 'location':'datation'})
        self.assertTrue(ob.to_xarray()[1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(18))))
        self.assertTrue(ob.to_xarray()[2,1,0].item() == ResultValue(9))
        ob = Observation(dict((obs_1, dat3, loc2, prop1, _res(6))))
        self.assertTrue(ob.to_xarray()[2,0].item() == ResultValue(2))

    '''@unittest.skipIf(plot, "test plot")
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
        self.assertTrue(ob.plot(line=True) == None)'''

    def test_exports(self):
        #ob = Observation(dict((obs_1, dat3, dpt3, prop1, _res(3))), idxref={'location':'datation'})
        ob = Observation(dict((obs_1, dat3, dpt3, prop1, _res(3))), idxref={'location':'datation'})
        self.assertTrue(type(ob.to_xarray()) != type(None))
        self.assertTrue(type(ob.to_dataFrame()) != type(None))
        self.assertTrue(ob.choropleth() != None)
        #self.assertTrue(type(ob.to_geoDataFrame()) != type(None))
        self.assertTrue(ob.jsonFeature != '')

    def test_filter(self):
        dic = {'type': 'observation',
               'property': {'property': 'Temp', 'unit': 'deg C'},
               'location': [[14, 42], [15, 42], [16, 42], [17, 42], [18, 42], [19, 42]],
               'datation': [{'test':'2021-05-04T12:05:00'}, '2021-05-05T12:05:00',
                            '2021-05-06T12:05:00', '2021-05-07T12:05:00', '2021-05-08T12:05:00',
                            datetime.datetime(2021, 5, 9, 12, 5, 0)],
               'result':   [25, 26, 27, 28, 29, 30]}
               #             '2021-05-09T12:05:00'],
               #'result':   [25, 26, 27, 28, 29, 30]}
        ob = Observation(dic, idxref={'location':'datation'})
        ob.majList(DatationValue, ['name1', 'autre name', 'encore autre name3', '', '', ''], name=True)
        self.assertEqual(len(ob.filter(datation={'__lt__' : DatationValue(datetime.datetime(2021,5,8))} )), 4)
        self.assertEqual(len(ob.filter(datation={'equals' : DatationValue(datetime.datetime(2021,5,5,12,5))} )), 1)
        self.assertEqual(len(ob.filter(datation={'within' : DatationValue([datetime.datetime(2021,5,4), datetime.datetime(2021,5,6)])} )), 2)
        self.assertEqual(len(ob.filter(location={'intersects' : LocationValue([[[15,42], [17.5, 42], [15,42]]])} )), 3)
        self.assertEqual(len(ob.filter(datation={'within' : DatationValue([datetime.datetime(2021,5,4), datetime.datetime(2021,5,6)])},
                                       location={'intersects' : LocationValue([[[15,42], [17.5, 42], [15,42]]])} )), 1)
        self.assertEqual(len(ob.filter(datation={'within' : DatationValue([datetime.datetime(2021,5,4), datetime.datetime(2021,5,6)])},
                                       location={'within' : LocationValue.Box((14.5, 41, 17.5, 44))} )), 1)
        self.assertEqual(len(ob.filter(datation={'isName' : 'name.'} )), 2)
        self.assertEqual(len(ob.filter(datation={'within' : DatationValue([datetime.datetime(2021,5,4), datetime.datetime(2021,5,8)]),
                                                 'isName' : 'name'} )), 3)
        self.assertEqual(len(ob.filter(datation={'within' : DatationValue([datetime.datetime(2021,5,4), datetime.datetime(2021,5,8)]),    # 4
                                                 'isName' : 'name'},                                                    # 3
                                       location={'within' : LocationValue.Box((14.5, 41, 18.5, 44))} )), 2)

class TestInterne(unittest.TestCase):
    '''Unit tests for `ES.ESObservation.Observation` internal '''

    @unittest.skipIf(mongo, "test envoi mongo")
    def test__list_bytes(self):
        ob = Observation(dict((obs_1, truc_mach, dat3, loc3, prop2, _res(6))), 
                         idxref={'location':'datation'}, order=['datation', 'property', 'location'])
        lis  = ob.ilist.setidx[0]
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'datation', 'name'))[1]
        self.assertEqual(lis[0].name, lis2[0].name)
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'datation', 'namemini'))[1]
        self.assertEqual(lis[0].name, lis2[0].name)
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'datation', 'value'))[1]
        self.assertEqual(lis[0].value, lis2[0].value)
        lis  = ob.ilist.setidx[1]
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'location', 'name'))[1]
        self.assertEqual(lis[0].name, lis2[0].name)
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'location', 'value'))[1]
        self.assertEqual(lis[0].value, lis2[0].value)
        lis  = ob.ilist.setidx[2]
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'property', 'name'))[1]
        self.assertEqual(lis[0].name, lis2[0].name)
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'property', 'value'))[1]
        self.assertEqual(lis[0].value, lis2[0].value)
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'property', 'valuemini'))[1]
        self.assertEqual(lis[0].value, lis2[0].value)
        lis  = ob.ilist.extval
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'result', 'name'))[1]
        self.assertEqual(lis[0].name, lis2[0].name)
        lis2 = ob._list_from_bytes(ob._list_to_bytes(lis,'result', 'value'))[1]
        self.assertEqual(lis[0].value, lis2[0].value)
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
