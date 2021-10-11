# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: a179227
"""
import json, geojson
from datetime import datetime
from ESconstante import ES
from shapely.geometry import shape #, mapping
from ESElement import isESAtt

def gshape(coord):
    if type(coord) == list:  coor = json.dumps(coord)
    elif type(coord) == str: coor = coord
    else: coor = coord.copy()
    for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
        try:
            s = shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coor + '}'))
            return s
        except: s = None
    return s

class ESValue:
    """
    Classe liée à la structure interne
    """
    def mini(x, y):
        if type(x) == LocationValue: mm = LocationValue([min(x.coor[0], y.coor[0]), min(x.coor[1], y.coor[1])])
        elif type(x) == TimeValue: mm = TimeValue(min(x.dtVal, y.dtVal))
        else : mm = x
        return mm

    def maxi(x, y):
        if type(x) == LocationValue:
            mm = LocationValue([max(x.coor[0], y.coor[0]), max(x.coor[1], y.coor[1])])
        elif type(x) == TimeValue: mm = TimeValue(max(x.dtVal, y.dtVal))  
        else : mm = x
        return mm
    
    def __init__(self):
        #self.valueName = "null"
        #self.valueType = "null"
        pass

class ESIndexValue(ESValue):
    """
    Classe liée à la structure interne
    """
    def __init__(self, ind):
        self.ind = ind

class ResultValue (ESIndexValue):
    """
    Classe liée à la structure interne
    """
    valueName = ES.res_valueName
    valueType = ES.res_valueType

    def __init__(self, val = None, ind = [-1, -1, -1]):
        ESIndexValue.__init__(self, ind)
        if (type(val) == str) : 
            try: js=json.loads(val)
            except:
                self.setValue(val)
                return
            if (type(js) == list and ind != [-1, -1, -1]): self.setValue(json.dumps(js))
            elif (type(js) == list and ind == [-1, -1, -1]): 
                if type(js[1]) == list: self.setIndValue(js)
                else: self.setValue(json.dumps(js))
            elif (type(js) == float or type(js) == int): self.setValue(js)
            else : self.setValue(json.dumps(js))
        elif type(val) == list : self.setIndValue(val)
        elif type(val) == ResultValue : self.setValue(val.value)
        elif (type(val) == float or type(val) == int): self.setValue(val)
        else : self.setValue(json.dumps(val))

    def __eq__(self, other): return self.value == other.value

    def __repr__(self): return object.__repr__(self) + '\n' + self.json(True)

    def setIndValue(self, val):
        if (type(val) == list) : 
            self.setValue(val[0])
            self.ind = val[1]
        else : self.value = None

    def setValue(self, val):
        if (type(val) in [str, int, float]) : self.value = val
        else : self.value = json.dumps(val)

    def json(self, res_index):
        if (type(self.value) == str and json.dumps(self.value)[1:-1]!=self.value):
            if res_index: return '[' + self.value + ', ' + json.dumps(self.ind) + ']'
            else: return self.value
        else:
            if res_index : return json.dumps([self.value, self.ind])
            else: return json.dumps(self.value)
    
class LocationValue(ESValue):
    """
    Classe liée à la structure interne
    """
    valueName = ES.loc_valueName
    valueType = ES.loc_valueType

    def __init__(self, val=[-1, -1], geo=True, cart=True):
        self.shap = gshape(val)
        self.coor = [-1, -1]
        if self.shap != None: self.coor = [self.shap.centroid.x, self.shap.centroid.y]
        self.geod = geo
        self.carto = cart

    def __eq__(self, other): return self.coor == other.coor and self.geod == other.geod and self.carto == other.carto

    def __repr__(self): return object.__repr__(self) + '\n' + self.json(True)

    @property
    def coorInv(self):  return [self.coor[1], self.coor[0]]

    def json(self, res_index):
        if self.shap != None: return json.dumps(self.shap.__geo_interface__['coordinates'])
        else: return 'null'
        
class TimeValue(ESValue):
    """
    Classe liée à la structure interne
    """
    valueName = ES.dat_valueName
    valueType = ES.dat_valueType

    def __init__(self, val= datetime(1970, 1, 1)):
        if type(val)==datetime: self.dtVal = val
        elif type(val)==str: self.dtVal = datetime.fromisoformat(val)
        else: self.dtVal= datetime(1970, 1, 1)

    def __eq__(self, other): return self.dtVal == other.dtVal

    def __repr__(self): return object.__repr__(self) + '\n' + self.json(True)

    def json(self, res_index): return self.dtVal.isoformat()

class PropertyValue(ESValue):
    """
    Classe liée à la structure interne
    """
    valueName = ES.prp_valueName
    valueType = ES.prp_valueType
    
    def __init__(self, val={}):
        self.propertyType   = "null"
        self.unit           = "null"
        self.sampling       = "null"
        self.application    = "null"
        self.EMFId          = "null"
        if type(val) != dict : return
        if ES.prp_propType  in val : self.propertyType  = val[ES.prp_propType]
        if ES.prp_unit      in val : self.unit          = val[ES.prp_unit]
        if ES.prp_sampling  in val : self.sampling      = val[ES.prp_sampling]
        if ES.prp_appli     in val : self.application   = val[ES.prp_appli]
        if ES.prp_EMFId     in val : self.EMFId         = val[ES.prp_EMFId]

    def init(self, prp_propType, prp_unit, prp_sampling = "null", prp_appli = "null", prp_EMFId = "null")    :
        self.propertyType = prp_propType
        self.unit = prp_unit
        self.sampling = prp_sampling
        self.application = prp_appli
        self.EMFId = prp_EMFId

    def __eq__(self, other): return (self.propertyType == other.propertyType and 
        self.unit == other.unit and self.sampling == other.sampling and
        self.application == other.application and self.EMFId == other.EMFId)

    def __repr__(self): return self.json(True)

    def json(self, res_index):
        li = dict()
        if (self.propertyType != "null"):   li[ES.prp_propType] = self.propertyType
        if (self.unit != "null"):           li[ES.prp_unit]     = self.unit
        if (self.sampling != "null"):       li[ES.prp_sampling] = self.sampling
        if (self.application != "null"):    li[ES.prp_appli]    = self.application
        if (self.EMFId != "null"):          li[ES.prp_EMFId]    = self.EMFId
        return json.dumps(li)
    
class ESSet:
    """
    Classe liée à la structure interne
    """
    def __init__(self, ValueClass = None, jObj = None):
        if ValueClass == None: return
        self.valueList = list()
        self.nValue = 0
        if  type(jObj) == list :
            if ValueClass != LocationValue or \
               (ValueClass == LocationValue and \
               (type(jObj[0]) == list or type(jObj[0]) == LocationValue)): 
                    for val in jObj : self.addValue(ValueClass, val)
            elif ValueClass == LocationValue and \
                 (type(jObj[0]) != list and type(jObj[0]) != LocationValue):
                    self.addValue(ValueClass, jObj)
        elif jObj == None : return 
        else : self.addValue(ValueClass, jObj)

    def initESSet(self, ObsValue, jObj):
        if type(jObj) == dict:
            jDat = jObj.copy()
            for k, v in jDat.items(): 
                if k == self.classES: jDat = v
            for k, v in jDat.items():
                if isESAtt(self.classES, k): self.mAtt[k] = v
            if ObsValue.valueName in list(jDat): 
                ESSet.__init__(self, ObsValue, jDat[ObsValue.valueName])
        elif type(jObj) == ObsValue or jObj == None: ESSet.__init__(self, ObsValue, jObj)
       
    def jsonESSet(self, ES_valueName, obs_class, elt_type, res_index, geojs = False):
        if len(self.valueList) == 0: return ""
        if geojs : res_index = True
        elt_type_nb = 0
        if elt_type : elt_type_nb = min(2, self.nValue)
        if geojs : elt_type_nb = - elt_type_nb
        js = ""
        if geojs : js += '{'
        if obs_class: js = '"' + self.classES + '":{'
        js += self.jsonAtt(elt_type_nb) + '"' + ES_valueName
        js += '":' + self.jsonSet(res_index) + ","
        if js[-1] == ',': js = js[:-1]
        if obs_class: js += '}' 
        if geojs : js += '}'
        return js

    def addValue(self, ValueClass, value):
        if type(value) == ValueClass : val = value
        else: val = ValueClass(value)
        if ValueClass != ResultValue :
            for i in range(len(self.valueList)):
                if self.valueList[i] == val and ES.mOption["unic_index"]: return i
            self.valueList.append(val)
        if ValueClass == ResultValue :
            for i in range(len(self.valueList)):
                if self.valueList[i].ind == val.ind and val.ind != [-1, -1, -1]: return i                
            self.valueList.append(val)
        self.nValue = len(self.valueList)
        return len(self.valueList) - 1

    def __len__(self): return len(self.valueList)
    
    def __getitem__(self, key): return self.valueList[key]
    
    def	__setitem__(self, key, value): self.valueList[key] = value

    def __repr__(self): return object.__repr__(self) + '\n' + self.jsonSet(True) + '\n'

    def miniBox(self):
        if (len(self) < 1): return None
        minimum = self.valueList[0]
        for val in self.valueList: minimum = ESValue.mini(val, minimum)
        return minimum;

    def maxiBox(self):
        if (len(self) < 1): return None
        maximum = self.valueList[0]
        for val in self.valueList: maximum = ESValue.maxi(val, maximum)
        return maximum;

    def jsonSet(self, res_index):
        if len(self.valueList) == 0 : return ""
        if len(self.valueList) == 1 : return self.valueList[0].json(res_index)
        li = list()
        for val in self.valueList: 
            if (type(val) == TimeValue) : li.append(val.json(res_index))
            else : li.append(json.loads(val.json(res_index)))
        return json.dumps(li)
        
    '''def indicateur(self):
        idat = 0; iloc = 1; iprop = 2
        indic = [0,0,0,0]
        nEch = nEchDat = nEchLoc = maxi = dim = 0
        iProp = iDat = iLoc = nDat = nLoc = 0
        #trouve = False;
        if len(self.valueList) < 1 : return indic
        for val in self.valueList:
            iDat  = max(iDat,  val.ind[idat])
            iLoc  = max(iLoc,  val.ind[iloc])
            iProp = max(iProp, val.ind[iprop])
        for idt in range(iDat + 1):
            maxi = 0
            trouvedat = False
            for il in range(iLoc + 1):
                trouvedatloc = False
                for val in self.valueList:
                    if  not trouvedatloc and val.ind[idat] == idt and val.ind[iloc] == il :
                        trouvedatloc = True; trouvedat = True; nEch += 1; maxi += 1
            if trouvedat : nDat += 1
            nEchDat = max(nEchDat, maxi)
        for il in range(iLoc + 1):
            maxi = 0
            trouveloc = False
            for idt in range(iDat + 1):
                trouvedatloc = False
                for val in self.valueList:
                    if  not trouvedatloc and val.ind[idat] == idt and val.ind[iloc] == il :
                        trouvedatloc == True; trouveloc = True; maxi += 1
            if trouveloc : nLoc += 1
            nEchLoc = max(nEchLoc, maxi)
        if nEch > 1 :
            if (nEchLoc < 2 or nEchDat < 2) : dim = 1
            else: dim = 2
        indic[0] = nEch
        indic[1] = dim
        indic[2] = nDat
        indic[3] = nLoc
        return indic'''

