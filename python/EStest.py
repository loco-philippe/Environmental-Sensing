# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: a179227
"""
from ESElement import ESElement, ESObject, ESObs
from ESComponent import ResultValue, LocationValue, ESValue, TimeValue, PropertyValue, gshape
from datetime import datetime
from ESObservation import Observation
from ESObs import Result, Location, Datation, Property, \
    ESSet, ESSetDatation, ESSetProperty, ESSetResult, ESSetLocation
import requests as rq
from copy import copy
import json, folium
from ESconstante import ES
from EStestunitaire import paris, lyon, res_, marseille, mini_PL, maxi_PLM, \
    val_1, val_, obs_1, coord_1, res_1, truc_mach, prop_pm25, \
    prop_pm10, t1, t2, t3, r1, r2, r3, dat1, prop1, loc1, res1, dat2, dat3, prop2, loc3
import os

print(os.getcwd())


with open('../json/france-geojson/departements-version-simplifiee.geojson') as f: dp = f.read()
dpt = json.loads(dp)
pol13 = dpt['features'][12]['geometry']['coordinates']
pol69 = dpt['features'][69]['geometry']['coordinates']
pol75 = dpt['features'][75]['geometry']['coordinates']
pol1 = [[[0,1], [1,2], [1,1], [0,1]]]
pol2 = [[[0,2], [2,2], [1,1], [0,1]]]
dpt2 = (ES.loc_valueName, [pol1, pol2])
#print(gshape('[[[0, 1], [1, 2], [0,1]]]'))
#ob1 = Observation(json.dumps(dict((obs_1, dpt2))))
#ob1 = Observation(json.dumps(dict((obs_1, dat2, dpt2, prop2, res_(4)))))
dpt3 = (ES.loc_valueName, [pol75, pol69, pol13])
#ob1 = Observation(json.dumps(dict((obs_1, dat3, dpt3, prop2, res_(6)))))
ob1 = Observation(json.dumps(dict((obs_1, dat3, loc3, prop2, res_(6)))))
#ob1.majType()
#print(ob1.json(), '\n')
ob1.majType()
ob1.option["json_info_type"] = True
ob1.option["json_info_nval"] = True
ob1.option["json_info_box"] = True
ob1.option["json_info_autre"] = True

print(ob1.json(), '\n')
'''m = ob1.choropleth()
if m != None: m.save("choro.html")
'''
'''
#def main():
ob1 = Observation(json.dumps(dict((obs_1, truc_mach, dat3, loc3, prop2, res_(9)))))
print(ob1.json(), '\n')
print(res_(9))
obs = Observation()
nprop1 = obs.addValue(PropertyValue({"property":"PM25", "unit":"ppm"}))
for i in range(6): # simule une boucle de mesure
    nres = obs.addValueSensor(ResultValue(45+i), 
                        TimeValue(datetime(2021, 6, 4+i, 12, 5).isoformat()),
                        LocationValue([14+i, 40]),
                        nprop1)
#ob3 = obs + ob1
#ob3 = ob1 + ob1
ob3 = copy(ob1)
print(ob3.json(), "copy")
ob3 += ob1
obs.option["json_res_index"] = True
print(obs.json(), '\n')
ob1.option["json_res_index"] = True
print(ob1.json(), '\n')
ob3.option["json_res_index"] = True
print(ob3.json())
obs.majType()
obs.option["json_ESobs_class"] = True
obs.option["json_elt_type"] = True
#res1 = obs.json()
#print(obs.json(), "\n")

obs.option["json_info_type"] = False
obs.option["json_info_nval"] = False
obs.option["json_info_box"] = False
obs.option["json_info_autre"] = False
res2 = obs.json()
#print(res2)
'''

cible1 = '{"type":"observation","id" : "xxxxx", "attributes":{\
    "relatedObsId" : "rrrr",\
    "process":{"typeprocess":"sensor"},\
    "interest":{"description":"mesure truc bidule","context":"apres l ete"},\
    "information":{"process":0,"interest":0,"complet":0,"ResultTime":"null","score":212,\
               "tauxMeasure":0.75,"tauxEchantillon":1,"typeobservation":"obsSequence",\
               "boudingBoxMax":[14,42.3],"boudingBoxMin":[14,42.3],"typelocation":"point",\
               "typeproperty":"multilist","timeBoxMax":"7-4-2021T12:5:0",\
               "timeBoxMin":"5-4-2021T12:5:0","typedatation":"multidate","dim":1,\
               "nEch":2,"typeresult":"multireal"},\
    "parameter":{"truc":"machin"},\
    "name":"essai 7",\
    "location":{"coordinates":[14,42.3]},\
    "Property":{"PropertyList":[{"PropertyType":"PM10","unit":"mg/m3"},{"PropertyType":"PM25","unit":"mg/m3"}]},\
    "Datation":{"DateTime":["5-4-2021T12:5:0","7-4-2021T12:5:0"]},\
    "Result":{"Value":[[47,[0,0,0]],[247,[1,0,1]],[49,[0,0,1]]]}}}'
cible2 = '{"type":"observation","id" : "xxxxx", \
    "relatedObsId" : "rrrr",\
    "process":{"typeprocess":"sensor"},\
    "interest":{"description":"mesure truc bidule","context":"apres l ete"},\
    "parameter":{"truc":"machin"},\
    "name":"essai 7",\
    "coordinates":[14,42.3],\
    "PropertyList":[{"PropertyType":"PM10","unit":"mg/m3"},{"PropertyType":"PM25","unit":"mg/m3"}],\
    "DateTime":["5-4-2021T12:5:0","7-4-2021T12:5:0"],\
    "Value":[[47,[0,0,0]],[247,[1,0,1]],[49,[0,0,1]]]}'   
cible3 = '{"type":"observation", \
    "relatedObsId" : "rrrr",\
    "DateTime":["5-4-2021T12:5:0","7-4-2021T12:5:0"],\
    "Value":[[47,[0,0,0]],[247,[1,0,1]],[49,[0,0,1]]]}'

#if __name__ == "__main__":
#    main()