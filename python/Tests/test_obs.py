# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `ES.test_obs` module contains the unit tests (class unittest) for the
Obs methods.
"""
import unittest

#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from ESValue import LocationValue, DatationValue, ESValue,\
    PropertyValue, NamedValue, ExternValue
from ESObs import Obs
from iindex import Iindex
from ESconstante import ES
import json, copy #, shapely
import requests as rq
import datetime
#from datetime import datetime
from pymongo import MongoClient
from pprint import pprint
from ilist import Ilist

# couverture tests (True if non passed)----------------------------------------
simple  = False  # False
plot    = True  # True
mongo   = False  # True

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
pol1centre = [0.66667, 1.33333]
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
pt1 = datetime.datetime(2020, 2, 4, 12, 5, 0).astimezone(datetime.timezone.utc)
pt2 = datetime.datetime(2020, 5, 4, 12, 5, 0).astimezone(datetime.timezone.utc)
pt3 = datetime.datetime(2020, 7, 4, 12, 5, 0).astimezone(datetime.timezone.utc)
tnull = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
snull = (tnull.isoformat(), tnull.isoformat())
t1 = datetime.datetime(2021, 2, 4, 12, 5, 0).astimezone(datetime.timezone.utc)
t1n = json.dumps({'date1' : t1.isoformat()})
t2 = datetime.datetime(2021, 7, 4, 12, 5, 0).astimezone(datetime.timezone.utc)
t3 = datetime.datetime(2021, 5, 4, 12, 5, 0).astimezone(datetime.timezone.utc)
"""r1 = ResultValue('{"er":2}')
r2 = ResultValue(23)
r3 = ResultValue("coucou")
r4 = ResultValue(41.2)
r5 = ResultValue(18)"""
r1 = NamedValue('{"er":2}')
r2 = NamedValue(23)
r3 = NamedValue("coucou")
r4 = NamedValue(41.2)
r5 = NamedValue(18)
s1 = [t1, t2]
dat1 = (ES.dat_classES, {'date1' : t1.isoformat()})
dat2 = (ES.dat_classES, [t1.isoformat(), t2.isoformat()])
dat3 = (ES.dat_classES, [{'date1' : t1.isoformat()}, t2.isoformat(), t3.isoformat()])
dat3d = (dat3[0], [dat3[1],0])
tdat3 = (ES.dat_classES, [{'date1' : t1}, t2, t3])
dat3ord = (ES.dat_classES, [{'date1' : t1.isoformat()}, t3.isoformat(), t2.isoformat()])
dat3sn = (ES.dat_classES, [t1.isoformat(), t2.isoformat(), t3.isoformat()])
pdat3 = (ES.dat_classES, [pt1.isoformat(), pt2.isoformat(), pt3.isoformat()])
prop1 = (ES.prp_classES, prop_pm10)
prop2 = (ES.prp_classES, [prop_pm25, prop_pm10])
prop2ord = (ES.prp_classES, [prop_pm10, prop_pm25])
prop3 = (ES.prp_classES, [prop_pm25, prop_pm10, prop_co2])
prop3d0 = (prop3[0], [prop3[1],0])
prop3d1 = (prop3[0], [prop3[1],1])
pprop2 = (ES.prp_classES, [pprop_pm25, pprop_pm10])
loc1 = (ES.loc_classES, {'paris' : paris})
loc1sn = (ES.loc_classES, paris)
loc2 = (ES.loc_classES, [paris, lyon])
loc3 = (ES.loc_classES, [{'paris' : paris}, lyon, marseille])
loc3d = (loc3[0], [loc3[1],0])
loc3sn = (ES.loc_classES, [paris, lyon, marseille])
ploc3 = (ES.loc_classES, [pparis, plyon, pmarseille])
res2 = (ES.res_classES, [[41, [2, 2, 0]], [18, [1, 2, 1]]])

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
    return [res.json(encoded=True, encode_format='json', json_res_index=True),
            res.dim, res.nMax,
            res.nInd, res.axes, res.maxIndex, res.isextIndex, res.measureRate,
            res.error, res.vListIndex, res.nValue, res.vListName, res.vListValue
            ,_sort(res)]

def _sort(res):
    li = res.sort()
    if type(li[0]) == int : return li
    else : return res.vListValue

#%% tests exemples
class TestExemples(unittest.TestCase):      # !!! exemples
    def test_first_observation(self) :
        # cas simple + présentation
        ob=Obs.Std('high', 'morning', 'paris', ' Temp')
        ob.append(['low', 'morning', 'lyon', ' Temp'])
        ob.append(['very high', 'morning', 'marseille', ' Temp'])
        #ob.view()
        ob.voxel()
        ob.nindex('result').setlistvalue([25, 10, 35])
        ob.plot()
        # valeur numériques + choropleth
        ob.nindex('location').setlistvalue([paris, lyon, marseille], valueonly=True)
        #ob.view()
        '''choro = ob.choropleth()'''       # !!! à voir
        #choro.save("test.html")
        ob.nindex('location').setlistvalue([pol75, pol69, pol13],  valueonly=True)
        #ob.view(width=40)
        '''choro = ob.choropleth()'''       # !!! à voir
        #choro.save("test.html")
        # ajout dimension 2, infos globales
        #ob.append([30, 'morning', 'paris', 'Humidity'], equal='name')
        morning = ob.setDatation[0]
        locparis, loclyon, locmarseille = ob.setLocation
        ob.append([30, morning, locparis, 'Humidity'])
        ob.append(['60', morning, locmarseille, 'Humidity'])
        #ob.view(location='n', width=40)
        ob.voxel()
        ob.plot()
        # ajout dimension 3 + export dataarray, dataframe
        ob.append([28, 'afternoon', locparis, ' Temp'])
        ob.append([15, 'afternoon', loclyon, ' Temp'])
        ob.nindex('location').setcodeclist([paris, lyon, marseille], valueonly=True)

        #print(ob.setDatation)
        ob.nindex('datation').setcodeclist(["2021-05-05T10", "2021-05-05T16"], valueonly=True)
        #ob.view(width=15)
        ob.voxel()
        ob.plot(order=[0,2,1])
        #print(ob.to_xarray(numeric=True))
        #pprint(ob.json(), indent=2)
        #pprint(ob.full(inplace=False).json())
        #ob._info(string=False)
    
    def test_observation_for_sensor(self) :
        #Case 1: Simple sensor
        time = "2021-05-05T10:08"
        coord = [[2.35, 48.87]]
        prop = {"prp":"Temp"}
        res = 25
        # Observation creation and encoding to Json or to binary data in the sensor
        ob_sensor = Obs.Std(res, time, coord, prop)
        payload1 = ob_sensor.json(encoded=True)    # if the payload is character payload
        #print(len(payload1), payload1)
        payload2 = ob_sensor.json(encoded=True, encode_format='cbor')     # if the payload is binary payload
        #print(len(payload2)) # 99 bytes
        # data decoding in the server
        ob_receive1 = Obs.Iobj(payload1)
        ob_receive2 = Obs.Iobj(payload2)
        #print(ob_receive1 == ob_receive2 == ob_sensor)   # it's True !!
        self.assertTrue(ob_receive1 == ob_receive2 == ob_sensor)   # it's True !!
        # and store it in the database (example with NoSQL DataBase)
        jsonStore = ob_receive1.json(json_info=True, encoded=True)   # add 'information' in the json to facilitate the research in the database
        #pprint(json.loads(jsonStore))
        #url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
        #r = rq.post(url, data=jsonStore)
        #print("réponse : ", r.status_code, "\n")

        #case 2 : Mobile sensor with one property
        obs_sensor = Obs.Std()
        prop1 = PropertyValue(prop_pm25)
        for i in range(6): # simule une boucle de mesure
            obs_sensor.append([ 45 + i, DatationValue(datetime.datetime(2021, 6, 4+i, 12, 5).isoformat()),
                       LocationValue([14.1+i, 40.2]), prop1])
        self.assertTrue(obs_sensor.dimension == 1 and len(obs_sensor) == 6)
        payload = obs_sensor.json(encoded=True, encode_format='cbor')     # if the payload is binary payload
        #print(len(payload)) # 41.8 bytes/measure
        # data decoding in the server
        obs_receive = Obs.Iobj(payload)
        #print(ob_receive1 == ob_receive2 == ob_sensor)   # it's True !!
        self.assertTrue(obs_receive == obs_sensor)   # it's True !!

        #case 3 : Mobile sensor with two properties
        obs_sensor = Obs.Std()
        prop1 = PropertyValue(prop_pm25)
        prop2 = PropertyValue(prop_pm10)
        for i in range(6): # simule une boucle de mesure
            date = DatationValue(datetime.datetime(2021, 6, 4+i, 12, 5).isoformat())
            loc = LocationValue([14.1+i, 40.2])
            obs_sensor.append([ 45 + i, date, loc, prop1])
            if i%3 == 0: obs_sensor.append([ 105 + i//3, date, loc, prop2])
        obs_sensor.full(fillvalue=None)
        self.assertTrue(obs_sensor.dimension == 2 and len(obs_sensor) == 12)
        payload = obs_sensor.json(encoded=True, encode_format='cbor')     # if the payload is binary payload
        #print(len(payload)) # 280 bytes (35 bytes/measure)
        # data decoding in the server
        obs_receive = Obs.Iobj(payload)
        #print(ob_receive1 == ob_receive2 == ob_sensor)   # it's True !!
        self.assertTrue(obs_receive == obs_sensor)   # it's True !!

        #case 4 : minimize data in operation
        # initialization phase (sensor or server) -> once
        coord = [2.3, 48.9]
        prop = {"prp":"Temp"}
        ob_init = Obs.Idic({'location': [coord], 'property': prop})
        #print(ob_init.json)
        # operation phase (sensor) -> regularly
        res = 25
        il_operat = Ilist.Idic({'res': [res]})
        payload1 = il_operat.json(encoded=True)    # if the payload is character payload
        #print(len(payload1), payload1)
        payload2 = il_operat.json(encoded=True, encode_format='cbor')     # if the payload is binary payload
        #print(len(payload2)) # 10 bytes
        # data decoding in the server
        il_receive1 = Ilist.Iobj(payload1)
        il_receive2 = Ilist.Iobj(payload2)
        date_receive = datetime.datetime(2021, 6, 4+i, 12, 5)
        #print(ob_receive1 == ob_receive2 == ob_sensor)   # it's True !!
        self.assertTrue(il_receive1 == il_receive2 == il_operat)   # it's True !!
        # complete observation
        ob_complet = Obs.Idic({'res': il_receive1, 'datation': date_receive, 
                               'location': [coord], 'property': prop}, var=0).merge()
        #print(ob_complet)

        #case 5 : Sensor with two properties (minimize data)
        coord = [2.3, 48.9]
        prop1 = {"prp":"PM25"}
        prop2 = {"prp":"PM10"}
        ob_init = Obs.Idic({'location': [coord], 'property': [prop1, prop2]})
        #sensor : Ilist acquisition
        il_sensor = Ilist.Idic({'res': [], 'datation':[], 
                                'property':[[prop1, prop2], []]}, var=0)
        for i in range(6): # simule une boucle de mesure
            date = datetime.datetime(2021, 6, 4+i, 12, 5)
            il_sensor.append([ 45 + i, date, prop1])
            if i%3 == 0: il_sensor.append([ 105 + i//3, date, prop2])
        il_sensor.full(fillvalue=None) 
        il_sensor.nindex('property').setcodeclist([None, None])
        self.assertTrue(il_sensor.dimension == 2 and len(obs_sensor) == 12)
        #send data
        payload = il_sensor.json(encoded=True, encode_format='cbor')     # if the payload is binary payload
        #print(len(payload)) # 88 bytes (11 bytes/measure)
        # data decoding in the server
        il_receive = Ilist.Iobj(payload, reindex=False)
        self.assertTrue(il_receive == il_sensor)   # it's True !!
        il_receive.nindex('property').setcodeclist([prop1, prop2])
        # complete observation
        ob_complet = Obs.Idic({'res': il_receive, 'location': [coord]}, var=0).merge().setcanonorder()
        #print(ob_complet.to_obj(encoded=True))
        self.assertTrue(ob_complet.dimension == 2 and ob_complet.complete)   # it's True !!
        #print(ob_complet.to_obj(encoded=True, json_info=True))
        
#%% tests unitaires
@unittest.skipIf(simple, "test Observation")
class TestObservation(unittest.TestCase):
    '''Unit tests for `ES.ESObs.Obs` '''

    def test_obs_creation_copy(self):
        listob = [Obs(), Obs(id='truc', listidx=[1,2,3]), Obs.from_obj({'data':[1,2,3]}),
                  Obs.Iobj({'data':[1,2,3], 'id':'truc'}), 
                  Obs.Iobj({'data':[1,2,3], 'id':'truc', 'param':{'date': '21-12'}}),
                  Obs.Std([11,12], 'dat1', ['loc1', 'loc2'], 'prp1', name='truc'),
                  Obs.Std(result=[10,20], datation='dat1', location=['loc1', 'loc2'], name='truc'),
                  Obs.Idic(dict((dat1, loc1, prop3, _res(3))), name='truc'),
                  Obs.Idic(dict((loc3, dat3d, prop2, 
                                 ('result', [{'file':'truc', 'path':'ertert'}, 1,2,3,4,['truc', 'rt']]))))]
        for ob in listob:
            self.assertEqual(Obs.Iobj(ob.to_obj()), ob)
            self.assertEqual(copy.copy(ob), ob)

        ob1 = Obs.Idic(dict((dat1, loc1, prop3, _res(3))))
        ob3 = Obs.Std(datation=dat1[1], location=loc1[1], property=prop3[1],
                              result=_res(3)[1])
        ob6 = Obs.Std(datation=[dat1[1]], location=[loc1[1]],
                          property=prop3[1], result=_res(3)[1])
        self.assertTrue(ob1 == ob3 == ob6)
        ob  = Obs()
        ob1 = Obs.Idic({})
        ob2 = Obs([])
        self.assertTrue(ob == ob1 == ob2)
        ob=Obs.Std('fort', 'ce matin', 'paris', 'pm10')
        ob1=Obs.Std([], [], [], [])
        ob1.append(['fort', 'ce matin', 'paris', 'pm10'])
        ob2=Obs.Std(datation=['ce matin'], location=['paris'], property=['pm10'], result=['fort'])
        self.assertTrue(ob == ob1 == ob2)

    def test_obs_loc_iloc_maj(self):
        ob = Obs.Idic(dict((dat3, loc3d, prop2, _res(6))), param=truc_mach)
        self.assertTrue([ob[3][3]] == 
                        ob.loc([datetime.datetime.fromisoformat(dat3[1][1]), loc3[1][1], 
                                prop2[1][1]]) ==
                        ob.loc([DatationValue(dat3[1][1]), LocationValue(loc3[1][1]), 
                                PropertyValue(prop2[1][1])], extern=False))
        ob.nindex('location').setcodecvalue(loc3[1][1], loc3[1][2])
        self.assertEqual(ob.nindex('location').codec[0], ob.nindex('location').codec[2])
        self.assertEqual(ob.setLocation[0], ob.setLocation[2])
        self.assertTrue (ob.nindex('result').loc(5) == 
                         ob.nindex('result').loc(NamedValue(5), extern=False) == [5])
        self.assertTrue (ob.nindex('datation').loc("2021-07-04T10:05:00") == 
                         ob.nindex('datation').loc(DatationValue("2021-07-04T10:05:00"), 
                                                   extern=False) == [2,3])

    def test_obs_vList(self):
        ob = Obs.Idic(dict((dat3, loc3)), param=truc_mach)
        self.assertEqual(ob.vlist(func=ESValue.vName, extern=False, index=ob.lname.index('datation'), default='now'),
                         ob.nindex('datation').vlist(func=ESValue.vName, extern=False, default='now'),
                         ob.nindex('datation').vName(default='now', maxlen=3) ==
                         ['dat', 'now', 'now'])
        self.assertEqual(ob.nindex('location').vSimple(), [paris, lyon, marseille])
        self.assertEqual(ob.nindex('datation').vSimple(), [t1, t2, t3])
        ob = Obs.Idic(dict((dat3, dpt2)), param=truc_mach)
        self.assertEqual(ob.nindex('location').vSimple()[0], pol1centre)
        ob = Obs.Idic(dict((dat3, loc3d, prop2, _res(6))))
        self.assertEqual(ob.nindex('result').vName(default='res'), ['res']*6)
        self.assertEqual(ob.nindex('result').vSimple(), [0, 1, 2, 3, 4, 5])


    def test_obs_options(self):
        ob = Obs.Idic(dict((dat3, loc3d, prop2, _res(6))))
        self.assertTrue(Obs.Iobj(ob.json()) == ob)
        option = dict()
        option["json_res_index"] = True
        option["json_info_type"] = True
        option["json_info_nval"] = True
        option["json_info_other"] = True
        option["json_info_box"] = True
        ob2 = Obs.Iobj(ob.json(**option))
        self.assertTrue(ES.type in ob2.json())
        self.assertEqual(ob2, ob)
        self.assertEqual(ob2.json(**option), ob.json(**option))

    def test_obs_dim(self):
        ob1 = Obs.Idic(dict((dat2, loc3, prop3d1, _res(6))))
        self.assertTrue(ob1.dimension == 2 and ob1.complete and ob1.primary == [0, 1])
        ob1 = Obs.Idic(dict((dat3, loc2, prop3d0, _res(6))))
        self.assertTrue(ob1.dimension == 2 and ob1.complete and ob1.primary == [0, 1])
        ob1 = Obs.Idic(dict((dat3, loc3, prop3, _res(3))))
        self.assertTrue(ob1.dimension == 1 and ob1.complete and ob1.primary == [0])


    def test_obs_majListName_majListValue(self):
        ob = Obs.Idic(dict((dat3, loc3, prop2, _res(18))))
        ob.nindex('location').setcodeclist([pparis, plyon, pmarseille], valueonly=True)
        self.assertEqual(ob.setLocation[2].vSimple(), pmarseille)
        ob.nindex('datation').setcodeclist([pt1, pt2, pt3], valueonly=True)
        self.assertEqual(ob.setDatation[2].simple, pt3)
        ob.nindex('location').setcodeclist(['paris', 'lyon', 'marseille'], nameonly=True)
        self.assertEqual(ob.setLocation[2].name, 'marseille')

    def test_append_obs(self):
        ob = Obs.Idic(dict((dat3, loc3d, prop2, _res(6))))
        ob1 = copy.copy(ob)
        ind = ob1.appendObs(ob)
        self.assertEqual(ob1.setResult[ind[3]].value, ob)
        self.assertEqual(ob1.setLocation[ind[1]].value, LocationValue.Box(ob.bounds[1]).value)
        ob1=Obs.Std()
        ob1.appendObs(ob)
        ob2=Obs.Iobj(ob1.to_obj(encode_format='json', encoded=False))

    def test_obs_sort(self):
        dat = d1, c2, d3 = [{'d1':t1}, {'c2':t2}, {'d3':t3}]
        loc = l1, m2, l3 = [{'l1':[1,2]}, {'m2':[2,3]}, {'l3':[3,4]}]
        prp = p2, p1     = [{'p2':prop_pm10}, {'p1':prop_pm25}]
        res = [[10, 11, 12, 13, 14, 15], -1]
        dic = {'location': [loc,2], 'property': prp, 'datation': dat, 'result': res}
        ob  = Obs.Idic(dic)
        self.assertEqual(ob.loc([l1, p1, d1])[0].value, 13)
        ob.sort(order=[0,2,1])
        self.assertEqual(ob.loc([l1, p1, d1])[0].value, 13)
        self.assertEqual(ob.lindex[0].vName()[:3], ['l1', 'l1', 'l3'])
        ob.sort(order=[2,0,1])
        self.assertEqual(ob.loc([l1, p1, d1])[0].value, 13)
        self.assertEqual(ob.lindex[2].vName()[:3], ['c2', 'c2', 'd1'])
        ob.sort([3])
        self.assertEqual(ob.loc([l1, p1, d1])[0].value, 13)
        self.assertEqual(ob.lindex[3].val, [10, 11, 12, 13, 14, 15])       
        ob.sort(order=[1,0,2])
        self.assertEqual(ob.loc([l1, p1, d1])[0].value, 13)
        self.assertEqual(ob.lindex[1].vName()[:4], ['p1', 'p1', 'p1', 'p2'])

    def test_obs_add(self):
        ob  = Obs.Idic(dict(( dat3,  loc3,  prop2, _res(18))), var=3)
        obp = Obs.Idic(dict((pdat3, ploc3, pprop2, _res(18))), var=3)
        obc = obp + ob
        self.assertEqual(set(obc.lindex[0].codec), set(obp.lindex[0].codec + ob.lindex[0].codec))
        self.assertEqual(obc.lindex[3].values, obp.lindex[3].values + ob.lindex[3].values)
        ob2 = ob + ob
        self.assertEqual(set(ob2.lindex[0].codec), set(ob.lindex[0].codec))
        self.assertEqual(obc.lindex[3].values, obp.lindex[3].values + ob.lindex[3].values) 
        self.assertFalse(ob2.consistent)


    def test_obs_full(self):
        ob=Obs.Idic({"datation": [[{"date1": "2021-02-04T12:05:00"},"2021-07-04T12:05:00", "2021-05-04T12:05:00"],
                                  [0,0,1,1,2,2]],
                     "location": [[{"paris": [2.35, 48.87]}, [4.83, 45.76], [5.38, 43.3]],
                                  [0,0,2,1,1,2]],
                     "property": [[{"prp": "PM25", "unit": "kg/m3"}, {"prp": "PM10", "unit": "kg/m3"}],
                                  [0,1,0,1,0,1]],
                     "result": [[0,1,2,3,4,5], -1]}, name='test1')
        ob1=ob.full(fillvalue=-1, inplace=False)
        rec=[{"date1": "2021-02-04T12:05:00"}, {"paris": [2.35, 48.87]}, 
             {"prp": "PM10", "unit": "kg/m3"}]
        self.assertTrue(ob.loc(rec) == ob1.loc(rec) == [NamedValue(1)])
        self.assertEqual(len(ob1), 18)
        ob.full(fillvalue=-1, inplace=True)
        self.assertEqual(ob, ob1)


    def test_obs_extend(self):
        obp = Obs.Idic(dict((_res(6), loc3, prop2)))
        obc = Obs.Idic(dict((_res(6), dat3, prop2)))
        ob  = Obs.Idic(dict((_res(6), dat3, (loc3[0], [loc3[1],1]), prop2)))
        obcc = obp | obc
        self.assertEqual(obcc, ob)
        ob = Obs.Iobj({'data':[list(_res(6))]})
        ob.addindex(['datation', ['matin'], [0,0,0,0,0,0]])
        ob.addindex(['location', ['paris', 'lyon', 'marseille'], [0,1,2,0,1,2]])
        ob.addindex(['property', ['pm10', 'pm25'], [0,1,0,1,0,1]])
        self.assertEqual(ob.primary, [1,2])
        self.assertTrue(ob.complete)

"""class TestImportExport(unittest.TestCase):
    '''Unit tests for `ES.ESObservation.Observation` import and export '''
    def test_json(self):
        res = ('result', [{'file':'truc', 'path':'ertert'}, 1,2,3,4,['truc', 'rt']])
        ob = Observation(dict((obs_1, loc3, dat3, prop2, res)), idxref={'location':'datation'})        
        for forma in ['json', 'bson', 'cbor']:
            for encoded in [False, True]:
                for codif in [ES.codeb, {}]:
                    self.assertEqual(Observation(ob.to_json(encoded=encoded, 
                        encode_format=forma, codif=codif)).to_json(encoded=False),
                         ob.to_json(encoded=False))

    def test_file(self):
        res = ('result', [{'file':'truc', 'path':'ertert'}, 1,2,3,4,['truc', 'rt']])
        ob = Observation(dict((obs_1, loc3, dat3, prop2, res)), idxref={'location':'datation'})
        ob.to_file('test.obs', encode_format='bson')
        self.assertEqual(Observation.from_file('test.obs').to_json(encoded=False),
                         ob.to_json(encoded=False))
        ob.to_file('test.obs', encode_format='json')
        self.assertEqual(Observation.from_file('test.obs').to_json(encoded=False),
                         ob.to_json(encoded=False))
        
class TestExports(unittest.TestCase):
    '''Unit tests for `ES.ESObservation.Observation` exports '''

    @unittest.skipIf(mongo, "test envoi mongo")
    def test__envoi_mongo(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'})
        data = ob.to_json(encoded=False, encode_format='bson', json_info=True)
        self.assertFalse(_envoi_mongo_python(data)==None)
        data = ob.to_json(encoded=True, encode_format='json', json_info=True)
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
        '''self.assertEqual(ob.to_numpy(func=ResultValue.vSimple, string=True)[0][1,1], '4.0')
        self.assertEqual(ob.to_numpy(func=ResultValue.vSimple, string=False)[0][1,1], 4.0)
        self.assertEqual(ob.to_numpy(func=ResultValue.vSimple, string=True, ind='all')[0][2,1,1], '2.0')'''
        self.assertEqual(ob.to_numpy(func=NamedValue.vSimple, string=True)[0][1,1], '4.0')
        self.assertEqual(ob.to_numpy(func=NamedValue.vSimple, string=False)[0][1,1], 4.0)
        self.assertEqual(ob.to_numpy(func=NamedValue.vSimple, string=True, ind='all')[0][2,1,1], '2.0')
        self.assertEqual(ob.to_numpy(func=ESValue.vName, genName='-')[0][1,1], '-')

    def test_xarray(self):
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(6))), idxref={'location':'datation'})
        d1 = ob.setDatation[1]
        l1 = ob.setLocation[1]
        p0 = ob.setProperty[0]
        r110 = ob.setResult[2]
        self.assertTrue(ob.to_xarray().loc[d1,p0].item() == r110)
        self.assertTrue(ob.to_xarray(numeric=True).loc[d1.vSimple(), 1].item() == 2.0)
        self.assertTrue(ob.to_xarray(ind='all').loc[d1,l1,p0].item() == r110)
        ob = Observation(dict((obs_1, dat3, loc3, prop1, _res(3))), idxref={'location':'datation'})
        self.assertTrue(ob.to_xarray()[1].item() == NamedValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop3, _res(3))), idxref={'property':'datation', 'location':'datation'})
        self.assertTrue(ob.to_xarray()[1].item() == NamedValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(18))))
        self.assertTrue(ob.to_xarray()[2,1,0].item() == NamedValue(9))
        ob = Observation(dict((obs_1, dat3, loc2, prop1, _res(6))))
        self.assertTrue(ob.to_xarray()[2,0].item() == NamedValue(2))
        '''self.assertTrue(ob.to_xarray()[1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop3, _res(3))), idxref={'property':'datation', 'location':'datation'})
        self.assertTrue(ob.to_xarray()[1].item() == ResultValue(2))
        ob = Observation(dict((obs_1, dat3, loc3, prop2, _res(18))))
        self.assertTrue(ob.to_xarray()[2,1,0].item() == ResultValue(9))
        ob = Observation(dict((obs_1, dat3, loc2, prop1, _res(6))))
        self.assertTrue(ob.to_xarray()[2,0].item() == ResultValue(2))'''

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
        ob.majList(ES.dat_classES, ['name1', 'autre name', 'encore autre name3', '', '', ''], name=True)
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
    def test_plot(self):
        il3 = Ilist.Idic({'location': [[0,1], [4.83, 45.76], [5.38, 43.3]],
         'datation': [{'date1': '2021-02-04T11:05:00+00:00'},
           '2021-07-04T10:05:00+00:00',
           '2021-05-04T10:05:00+00:00'],
         'property': [{'prp': 'PM25', 'unit': 'kg/m3'},
          {'prp': 'PM10', 'unit': 'kg/m3'}],
         'result': [[{'ert':0}, 1, 2, 3, 4, 5, 6,7,8,9,10,11,12,13,14,15,16,17],-1]})
        ob3=Obs(il3)
        #ob3.swapindex([0,2,3,1])
        #obx = ob3.to_xarray(numeric = True, maxlen=8, lisfunc=[util.cast], dtype='str')
        ob3.plot(line=False)
        ob3.plot(line=True)
        ob3.plot(line=False, order=[1,0,2])
        ob3.plot(line=True, order=[1,0,2])
        ob3.plot(line=False, order=[2,1,0])
        ob3.plot(line=True, order=[2,1,0])
        ob3.plot(line=False, order=[0,2,1])
        ob3.plot(line=True, order=[0,2,1])
        
        il2 = Ilist.Idic({'locatio': [0, [4.83, 45.76], [5.38, 43.3]],
         'datatio': [[{'date1': '2021-02-04T11:05:00+00:00'},
           '2021-07-04T10:05:00+00:00',
           '2021-05-04T10:05:00+00:00'],
          0],
         'propert': [{'prp': 'PM25', 'unit': 'kg/m3'},
          {'prp': 'PM10', 'unit': 'kg/m3'}],
         'result': [[{'ert':0}, 1, 2, 3, 4, 5],-1]})
        ob2=Obs(il2)
        ob2.plot(line=False)
        ob2.plot(line=True)
        ob2.plot(line=False, order=[1,0])
        ob2.plot(line=True, order=[1,0])
        
        il2 = Ilist.Idic({'location': [[1,2], [4.83, 45.76], [5.38, 43.3]],
         'datation': [[{'date1': '2021-02-04T11:05:00+00:00'},
           '2021-07-04T10:05:00+00:00',
           '2021-05-04T10:05:00+00:00'],
          0],
         'property': [{'prp': 'PM25', 'unit': 'kg/m3'},
          {'prp': 'PM10', 'unit': 'kg/m3'}],
         'result': [[{'ert':0}, 1, 2, 3, 4, 5],-1]})
        ob2=Obs(il2)
        ob2.plot(line=False)
        ob2.plot(line=True)
        
        il1 = Ilist.Idic({'locatio': [0, [4.83, 45.76], [5.38, 43.3]],
         'datatio': [[{'date1': '2021-02-04T11:05:00+00:00'},
           '2021-07-04T10:05:00+00:00',
           '2021-05-04T10:05:00+00:00'],
          0],
         'result': [[{'ert':0}, 1, 2],-1]})
        ob1=Obs(il1)
        ob1.plot(line=True)
        ob1.plot(line=False)
        
        il1 = Ilist.Idic({'location': [[1,2], [4.83, 45.76], [5.38, 43.3]],
         'datation': [[{'date1': '2021-02-04T11:05:00+00:00'},
           '2021-07-04T10:05:00+00:00',
           '2021-05-04T10:05:00+00:00'],
          0],
         'result': [[{'ert':0}, 1, 2],-1]})
        ob1=Obs(il1)
        ob1.plot(line=True)
        ob1.plot(line=False)
""" 
       
if __name__ == '__main__':
    unittest.main(verbosity=2)