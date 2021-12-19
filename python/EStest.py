# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: a179227
"""
from ESElement import ESElement, ESObject, ESObs
from ESComponent import ResultValue, LocationValue, ESValue, DatationValue, PropertyValue, gshape
from datetime import datetime
from ESObservation import Observation
from ESObs import Result, Location, Datation, Property, \
    ESSet, ESSetDatation, ESSetProperty, ESSetResult, ESSetLocation
import requests as rq
from copy import copy
import json, folium
from ESconstante import ES
from EStestunitaire import paris, lyon, res_, marseille, mini_PL, maxi_PLM, \
    val_, obs_1, truc_mach, prop_pm25, res2, prop3, dpt3, \
    prop_pm10, t1, t2, t3, r1, r2, r3, dat1, prop1, loc1, dat2, dat3, prop2, loc3
import os
import struct
import numpy as np

def test_erreur():
    ob = Observation(dict((obs_1, dat3, dpt3, prop2, res_(6))), 'px')
    '''ob.option["json_res_index"] = True
    print(ob.json(), '\n')
    ob.sort(cross=False)
    print(ob.json(), '\n')
    
    return'''
    
    #ob.option["json_res_index"] = True
    test = ob.iloc(1,1,0)
    print(ob.json(), '\n')
    print(ob.iloc(1,1,0), '\n')
    #ob.sorting()
    ob.sort(cross = False)
    print(' normal ')
    print(ob.json(), '\n')
    print(ob.iloc(2,1,1), ob.iloc(2,1,1)==test, '\n')
    #ob.crossSorting()
    ob.sort()
    print(' avec cross et order = 0 1 2 ')
    print(ob.json(), '\n')
    print(ob.iloc(2, 2, 1), ob.iloc(2, 2, 1)==test, '\n') #xxxxxxx
    #ob.option['sort_order'] =[1,0,2]
    #ob.sorting()
    #ES.debug = True
    ob.sort(cross = False, order = [1,0,2])
    #ob.option["json_res_index"] = True
    print(' normal 2')
    print(ob.json(), '\n')
    print(ob.iloc(2,1,1), ob.iloc(2,1,1)==test, '\n')
    #ob.crossSorting()
    #ES.debug = False
    ob.sort(order = [1,0,2])
    print(' avec cross et order = 1 0 2 ')
    print(ob.json(), '\n')
    print(ob.iloc(1, 1, 1), ob.iloc(1, 1, 1)==test, '\n') #xxxxxx
    
def test_struct():
    
    val = 1.21e-3
    print('to_bytes', val, struct.pack('<e', val).hex('-'), struct.unpack('<e', struct.pack('<e', val))[0])
    print('to_bytes', val, 1+val, struct.pack('<ee', val, 1+val).hex('-'), struct.unpack('<ee', struct.pack('<ee', val, 1+val)))
    be = struct.pack('<e', val)
    
    val = "pépé4meme"
    print('to_bytes', val, str.encode(val), str.encode(val).hex('-'), bytes.decode(str.encode(val)))
    bv = str.encode(val)
    print(bv.__len__(), struct.pack('<l',bv.__len__()).hex('-'), hex(bv[1:3][1]))
    len24 = struct.pack('<l',bv.__len__())[0:3]
    len32 = len24 + b'\x00'
    print(len24.hex('-'), len32.hex('-'), struct.unpack('<l', len32)[0])
    print(bytes.decode(bv[0:3]))
    bt = be+bv
    print(bt.hex('-'))
    print(struct.unpack('e',bt[0:2])[0], bytes.decode(bt[2:]))
    return

def test_unit():
    print(os.getcwd())
    with open('../json/france-geojson/departements-version-simplifiee.geojson') as f: dp = f.read()
    dpt = json.loads(dp)
    pol13 = dpt['features'][12]['geometry']['coordinates']
    pol69 = dpt['features'][69]['geometry']['coordinates']
    pol75 = dpt['features'][75]['geometry']['coordinates']
    pol1 = [[[0,1], [1,2], [1,1], [0,1]]]
    pol2 = [[[0,2], [2,2], [1,1], [0,1]]]
    dpt2 = (ES.loc_valName[0], [pol1, pol2])
    #print(gshape('[[[0, 1], [1, 2], [0,1]]]'))
    #ob1 = Observation(json.dumps(dict((obs_1, dpt2))))
    #ob1 = Observation(json.dumps(dict((obs_1, dat2, dpt2, prop2, res_(4)))))
    dpt3 = (ES.loc_valName[0], [pol75, pol69, pol13])
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
def cible():
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
        "Property":{"PropertyList":[{"pType":"PM10","unit":"mg/m3"},{"pType":"PM25","unit":"mg/m3"}]},\
        "Datation":{"DateTime":["5-4-2021T12:5:0","7-4-2021T12:5:0"]},\
        "Result":{"Value":[[47,[0,0,0]],[247,[1,0,1]],[49,[0,0,1]]]}}}'
    cible2 = '{"type":"observation","id" : "xxxxx", \
        "relatedObsId" : "rrrr",\
        "process":{"typeprocess":"sensor"},\
        "interest":{"description":"mesure truc bidule","context":"apres l ete"},\
        "parameter":{"truc":"machin"},\
        "name":"essai 7",\
        "coordinates":[14,42.3],\
        "PropertyList":[{"pType":"PM10","unit":"mg/m3"},{"pType":"PM25","unit":"mg/m3"}],\
        "DateTime":["5-4-2021T12:5:0","7-4-2021T12:5:0"],\
        "Value":[[47,[0,0,0]],[247,[1,0,1]],[49,[0,0,1]]]}'   
    cible3 = '{"type":"observation", \
        "relatedObsId" : "rrrr",\
        "DateTime":["5-4-2021T12:5:0","7-4-2021T12:5:0"],\
        "Value":[[47,[0,0,0]],[247,[1,0,1]],[49,[0,0,1]]]}'

if __name__ == "__main__":
    test_erreur()