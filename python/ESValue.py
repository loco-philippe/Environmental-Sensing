# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module groups together the classes of the objects used in the `ES.ESObs` module.
"""
import json, geojson, struct, numpy, pandas, shapely
from datetime import datetime
from ESconstante import ES, mDistRef, identity
#from shapely.geometry import shape #, mapping
from ESElement import isESAtt, isUserAtt
from geopy import distance

def gshape(coord):
    if type(coord) == list:  coor = json.dumps(coord)
    elif type(coord) == str: coor = coord
    else: coor = coord.copy()
    for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
    #for tpe in ["MultiPoint", "Polygon", "MultiPolygon"]:
        try:
            s = shapely.geometry.shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coor + '}'))
            return s
        except: s = None
    return s

class ESValue:
    """
    This class is the parent class for each kind of values 
     (`ES.ESValue.DatationValue`, `ES.ESValue.LocationValue`, `ES.ESValue.PropertyValue`,
      `ES.ESValue.ResultValue`,
    """
    def mini(x, y):
        if type(x) == LocationValue: mm = LocationValue([min(x.point[0], y.point[0]), min(x.point[1], y.point[1])])
        elif type(x) == DatationValue: mm = DatationValue(min(x.instant, y.instant))
        else : mm = x
        return mm

    def maxi(x, y):
        if type(x) == LocationValue:
            mm = LocationValue([max(x.point[0], y.point[0]), max(x.point[1], y.point[1])])
        elif type(x) == DatationValue: mm = DatationValue(max(x.instant, y.instant))  
        else : mm = x
        return mm
    
    def __init__(self):
        self.name = ES.nullName

    def vName(self, genName=ES.nullName):  
        if self.name == ES.nullName : return genName
        else : return self.name
    
    def majName(self, nam):
        name = str(nam)
        #☺if type(name) != str : name = str(name)
        if name != '' : self.name = name

    def majValue(self, val, simple = True):
        if type(val) == LocationValue :
            if not simple and val.shap != None and val.shap != gshape(ES.nullCoor) : 
                self.shap = val.shap
                self.point = [self.shap.centroid.x, self.shap.centroid.y]
            if simple and val.point != ES.nullCoor : self.point = val.point
        elif type(val) == DatationValue :
            if not simple and val.slot != [ES.nullDate, ES.nullDate] : 
                self.slot = val.slot
                self.instant = self.slot[0] + (self.slot[1] - self.slot[0]) / 2
            if simple and val.instant != ES.nullDate : self.instant = val.instant

    def to_strBytes(self, simple = False):
        bval = str.encode(self.name)
        if simple : return str.encode(self.name)
        else : return struct.pack('>B',bval.__len__()) + bval
        
    def from_strBytes(self, byt, simple = False):
        if simple : 
            siz = byt.__len__()
            name = bytes.decode(byt)
        else : 
            siz = struct.unpack('>B', byt[0:1])[0]
            name = bytes.decode(byt[1: siz + 1])
        self.init(name)
        return siz + 1
                
class ESIndexValue(ESValue):
    """
    Classe liée à la structure interne
    """
    def __init__(self, ind):
        self.ind = ind

class DatationValue(ESValue):
    """
    Classe liée à la structure interne
    """
    #nullName    = ES.dat_nullName
    valName     = ES.dat_valName
    #valueName   = ES.dat_valueName
    valueType   = ES.dat_valueType

    def __init__(self, val = ES.nullDate):
        ESValue.__init__(self)
        self.slot = [ES.nullDate, ES.nullDate]
        self.instant = ES.nullDate
        self.init(val)
        
    def init(self, val = ES.nullDate):
        if type(val) == DatationValue :
            self.instant = val.instant
            self.slot = val.slot
            self.name = val.name
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]   
        slot = self.initSlot(val)
        if slot == [ES.nullDate, ES.nullDate] : 
            if type(val) == str and self.name == ES.nullName : self.name = val
        elif slot[0] == slot[1] : self.instant = slot[0]
        else : self.slot = slot

    def initSlot(self, val= ES.nullDate):
        if   type(val) == DatationValue:  return val.slot
        elif type(val) == list: 
            if type(val[0]) == datetime : return val
            else : return [datetime.fromisoformat(str(val[0])), datetime.fromisoformat(str(val[1]))]
        elif type(val) == datetime: return [val, val]
        elif type(val) == numpy.datetime64 :
            sl = pandas.Timestamp(val).to_pydatetime()
            return [sl, sl]                    
        elif type(val) == pandas._libs.tslibs.timestamps.Timestamp :
            sl = val.to_pydatetime()
            return [sl, sl]                    
        elif type(val) == str: 
            try:
                sl = datetime.fromisoformat(val)
                slo = [sl, sl]
            except:
                try:
                    val2 = json.loads(val)
                    slo = [datetime.fromisoformat(val2[0]),
                           datetime.fromisoformat(val2[1])]
                except:
                    sl = ES.nullDate
                    slo = [sl, sl]
            return slo
        else: 
            sl = ES.nullDate
            return [sl, sl]
        
    def __lt__(self, other): 
        return self.instant < other.instant
 
    def __eq__(self, other): 
        return self.instant == other.instant and self.slot == other.slot and self.name == other.name
        #or (self.name[0:3] == self.nullName and other.name[0:3] == self.nullName))

    def __repr__(self): return self.json()

    def getInstant(self) : return self.instant
    
    def getSlot(self) : return self.slot

    def vInstant(self, option = ES.mOption, string = False) : #string=False):  
        if self.slot != [ES.nullDate, ES.nullDate] : val = [self.slot[0], self.slot[1]]
        else: val =  self.instant
        if option["json_dat_instant"]:
            if self.instant != ES.nullDate : val =  self.instant
            elif self.slot != [ES.nullDate, ES.nullDate] : 
                val =  (self.slot[0] + (self.slot[1] - self.slot[0]) / 2)
        if   string and type(val) == dict : return [val[0].isoformat(), val[1].isoformat()]
        elif string and type(val) != dict : return val.isoformat()
        else : return val

    def json(self, option = ES.mOption): 
        val = self.vInstant(option, string=True)
        if option["json_dat_name"] and self.name != ES.nullName :
            if val != ES.nullDate.isoformat():  return json.dumps({self.name : val})
            else :                              return self.name
        else : 
            if type(val) == str :               return val
            else :                              return json.dumps(val)

    def to_bytes(self):
        return struct.pack('<HBBBBB', self.instant.year, self.instant.month,
                           self.instant.day, self.instant.hour,
                           self.instant.minute, self.instant.second)
        
    def from_bytes(self, byt):
        dt = struct.unpack('<HBBBBB', byt[0:7])
        self.init(datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]))
        return 7

class LocationValue(ESValue):
    """
    Classe liée à la structure interne
    """
    #nullName    = ES.nullName
    valName     = ES.loc_valName
    valueType   = ES.loc_valueType

    def __init__(self, val=ES.nullCoor, geo=True, cart=True):
        ESValue.__init__(self)
        self.point = ES.nullCoor
        self.shap = None
        self.geod = geo
        self.carto = cart
        self.init(val)
    
    def init(self, val=ES.nullCoor):
        if type(val) == LocationValue :
            self.shap = val.shap
            self.point = val.point
            self.name = val.name
            self.geod = val.geod
            self.carto = val.carto
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]   
        shap = gshape(val)
        if shap == None :
            if type(val) == str and self.name == ES.nullName : self.name = val
        elif type(shap) == shapely.geometry.point.Point : self.point = [shap.x, shap.y]
        else : self.shap = shap
        #self.shap = gshape(val)
        #self.point = ES.nullCoor
        #if self.shap != None: self.point = [self.shap.centroid.x, self.shap.centroid.y]
        #elif type(val) == str and self.name == ES.nullName : self.name = val

    def __eq__(self, other): return self.point == other.point and self.geod == other.geod \
        and self.carto == other.carto and self.shap == other.shap and self.name == other.name
        #or (self.name[0:3] == self.nullName and other.name[0:3] == self.nullName))

    #def __repr__(self): return object.__repr__(self) + '\n' + self.json()
    def __repr__(self): return self.json()

    def __lt__(self, other): 
        return distance.distance(self.coorInv, mDistRef) <  distance.distance(other.coorInv, mDistRef)
    
    @property
    def coorInv(self):  return [self.vPoint()[1], self.vPoint()[0]]
    
    def getShap(self) : return self.shap
    
    def getPoint(self) : return self.point
    
    def vPoint(self, option = ES.mOption):  
        val = ES.nullCoor
        if self.shap != None :              val =  self.shap.__geo_interface__[ES.coordinates]
        else:                               val =  self.point
        if option["json_loc_point"]:
            if self.point != ES.nullCoor :  val =  self.point
            elif self.shap != None :        val = [self.shap.centroid.x, self.shap.centroid.y]
        return val

    def vPointX(self, option = ES.mOption) : return self.vPoint(option)[0]
    def vPointY(self, option = ES.mOption) : return self.vPoint(option)[1]

    def json(self, option = ES.mOption): 
        val = self.vPoint(option)
        if option["json_loc_name"] and self.name != ES.nullName :
            if val != ES.nullCoor: return json.dumps({self.name : val})
            else : return self.name
        else : return json.dumps(val)

    def to_bytes(self):
        return struct.pack('<ll',round(self.point[0]*10**7), round(self.point[1]*10**7))
        
    def from_bytes(self, byt):
        pt = list(struct.unpack('<ll', byt[0:8]))
        self.init(list((pt[0] *10**-7, pt[1] *10**-7)))
        return 8

class PropertyValue(ESValue):
    """
    Classe liée à la structure interne
    """
    #nullName    = ES.prp_nullName
    valName     = ES.prp_valName
    valueType   = ES.prp_valueType
    
    def __init__(self, val={}):
        ESValue.__init__(self)
        self.name           = ES.nullName
        self.pType          = "null"
        self.unit           = "null"
        self.sampling       = "null"
        self.application    = "null"
        self.period         = 0
        self.interval       = 0
        self.uncertain      = 0
        self.EMFId          = "null"
        self.detail         = dict()
        self.init(val)
    
    def init(self, val={}):
        if type(val) == dict :
            for k, v in val.items():
                if   ES.prp_propType == k : self.pType       = v
                elif ES.prp_unit     == k : self.unit        = v
                elif ES.prp_sampling == k : self.sampling    = v
                elif ES.prp_appli    == k : self.application = v
                elif ES.prp_period   == k : self.period      = v
                elif ES.prp_interval == k : self.interval    = v
                elif ES.prp_uncertain== k : self.uncertain   = v
                elif ES.prp_EMFId    == k : self.EMFId       = v
                else : self.detail[k] = v
        elif type(val) == str : self.name = val

    def __eq__(self, other): return self.pType == other.pType and \
        self.unit == other.unit and self.sampling == other.sampling and \
        self.application == other.application and self.EMFId == other.EMFId and \
        self.detail == other.detail and self.name == other.name
        #or (self.name[0:3] == self.nullName and other.name[0:3] == self.nullName)))

    def __repr__(self): return self.json(ES.mOption)

    def __lt__(self, other): 
        return self.pType + self.name < other.pType + other.name

    def json(self, option = ES.mOption): 
        li = dict()
        if (self.pType != "null"):   li[ES.prp_propType] = self.pType
        if not option["json_prp_type"] : 
            if (self.unit != "null"):           li[ES.prp_unit]     = self.unit
            if (self.sampling != "null"):       li[ES.prp_sampling] = self.sampling
            if (self.application != "null"):    li[ES.prp_appli]    = self.application
            if (self.period != 0):              li[ES.prp_period]   = self.period
            if (self.interval != 0):            li[ES.prp_interval] = self.interval
            if (self.uncertain != 0):           li[ES.prp_uncertain]= self.uncertain
            if (self.EMFId != "null"):          li[ES.prp_EMFId]    = self.EMFId
            li |= self.detail
        if option["json_prp_name"] and self.name != ES.nullName : 
            if li == {} : return self.name
            else : li[ES.prp_name] = self.name 
        return json.dumps(li, ensure_ascii=False)

    def to_bytes(self):
        byt = struct.pack('<BBBLLB', ES.prop[self.pType][0], 
                           ES.sampling[self.sampling],
                           ES.application[self.application],
                           self.period,
                           self.interval,
                           self.uncertain * 2
                           )
        return byt[0:6] +byt[7:10] + byt[11:12]
        
    def from_bytes(self, byt):
        bytl = byt[0:6] + b'\x00' +byt[6:9] + b'\x00' + byt[9:10]
        prp = struct.unpack('<BBBLLB', bytl)
        self.pType      = ES.cnum[prp[0]]
        self.unit       = ES.prop[ES.cnum[prp[0]]][5]
        self.sampling   = ES.invSampling[prp[1]]
        self.application = ES.invApplication[prp[2]]
        self.period     = prp[3]
        self.interval   = prp[4]
        self.uncertain  = prp[5] // 2
        return 10

class ResultValue (ESIndexValue):
    """
    Classe liée à la structure interne
    """
    valName     = ES.res_valName
    valueType   = ES.res_valueType

    def __init__(self, val = None, ind = ES.nullInd):
        ESIndexValue.__init__(self, ind)
        ESValue.__init__(self)
        #self.value = 'null' 
        self.init(val, ind)
        
        
    def init(self, val = None, ind = ES.nullInd):
        if type(val) == str : 
            try: js=json.loads(val)
            except:
                self.setValue(val)
                return
            if (type(js) == list and ind != ES.nullInd): self.setValue(json.dumps(js))
            elif (type(js) == list and ind == ES.nullInd): 
                if type(js[1]) == list: self.setIndValue(js)
                else: self.setValue(json.dumps(js))
            elif (type(js) == float or type(js) == int): self.setValue(js)
            else : self.setValue(json.dumps(js))
        elif type(val) == list : self.setIndValue(val)
        elif type(val) == ResultValue : 
            self.value = val.value
            self.ind = val.ind
        elif (type(val) == float or type(val) == int): self.setValue(val)
        else : self.setValue(json.dumps(val))
        if type(ind) == list and ind != ES.nullInd and self.ind == ES.nullInd : self.ind = ind

    def __eq__(self, other): return self.value == other.value

    def __lt__(self, other):         
        o = ES.mOption["sort_order"]
        return self.ind[o[0]] < other.ind[o[0]] or \
              (self.ind[o[0]] == other.ind[o[0]] and self.ind[o[1]] <  other.ind[o[1]]) or \
              (self.ind[o[0]] == other.ind[o[0]] and self.ind[o[1]] == other.ind[o[1]] and self.ind[o[2]] < other.ind[o[2]])

    #def __repr__(self): return object.__repr__(self) + '\n' + self.json()
    def __repr__(self): return  self.json(ES.mOption)

    def setIndValue(self, val):
        if (type(val) == list) : 
            self.setValue(val[0])
            self.ind = val[1]
        else : self.value = None

    def setValue(self, val):
        if (type(val) in [str, int, float]) : self.value = val
        else : self.value = json.dumps(val)

    def json(self, option = ES.mOption): 
        if (type(self.value) == str and json.dumps(self.value)[1:-1]!=self.value):
            if option["json_res_index"]: return '[' + self.value + ', ' + json.dumps(self.ind) + ']'
            else: return self.value
        else:
            if option["json_res_index"] : return json.dumps([self.value, self.ind])
            else: return json.dumps(self.value)
    
    def to_bytes(self, resIndex = False, prp = "null"):
        formaPrp = ES.prop[prp][1]
        dexp = ES.prop[prp][3]
        bexp = ES.prop[prp][4]
        val = self.value * 10**-dexp * 2**-bexp
        if resIndex : return struct.pack('<BBB' + formaPrp,  self.ind[0],
                                         self.ind[1], self.ind[2], val)
        else : return struct.pack('<' + formaPrp, val)
        
    def from_bytes(self, byt, resInd = False, prp = "null"):
        formaPrp = ES.prop[prp][1]
        leng = ES.prop[prp][2]
        dexp = ES.prop[prp][3]
        bexp = ES.prop[prp][4]        
        if resInd :
            dt = struct.unpack('<BBB'+ formaPrp, byt[0:leng + 3])
            self.init(dt[3] * 10**dexp * 2**bexp, [dt[0], dt[1], dt[2]])
            return 3 + leng
        else :
            self.init(struct.unpack('<'+ formaPrp, byt[0:leng])[0] * 10**dexp * 2**bexp)
            return leng

    def to_float(self):
        if self.value == None :         return float('nan')
        elif type(self.value)==str:
            if self.value == 'null':    return float('nan')
            else : 
                try:                    return float(self.value)
                except:                 return float('nan')
        else :                          return float(self.value)           

ValueCod = [ None, LocationValue, DatationValue, PropertyValue, 
            LocationValue, DatationValue, PropertyValue]
    
class ESSet:
    """
    Classe liée à la structure interne
    """

    def __init__(self, ValueClass = None, jObj = None):
        if ValueClass == None: return
        self.valueList = list()
        self.iSort = list()
        self.nValue = 0
        if  type(jObj) == list :
            try :
                for val in jObj : self.addValue(ValueClass, val)
            except : self.addValue(ValueClass, jObj)
        elif jObj == None : return 
        else : self.addValue(ValueClass, jObj)

    def initESSet(self, ValueClass, jObj):
        if type(jObj) == dict:
            userAtt = False
            jDat = jObj.copy()
            for k, v in jDat.items():   # si mot-clef ESobs
                if k == self.classES: 
                    jDat = v
                    userAtt = True
            for k, v in jDat.items(): # attributs
                if isESAtt(self.classES, k) or (userAtt and isUserAtt(k)): self.mAtt[k] = v
            for vName in ValueClass.valName:   # valeurs
                if vName in list(jDat): ESSet.__init__(self, ValueClass, jDat[vName])
        elif type(jObj) == ValueClass or jObj == None: 
            ESSet.__init__(self, ValueClass, jObj)
    
    @property
    def vListName(self):
        return [self.valueList[i].vName(ES.vName[self.classES] + str(i)) for i in range(self.nValue)]

    def vList(self, func=identity):
        return [func(self.valueList[i]) for i in range(self.nValue)]
        
    def majListName(self, listName):
        for i in range(self.nValue) : self.valueList[i].majName(listName[min(i,len(listName))])

    def majListValue(self, ValueClass, listVal, simple = True):
        for i in range(self.nValue) : self.valueList[i].majValue(ValueClass(listVal[min(i,len(listVal))]), simple)
        
    def addValue(self, ValueClass, value):
        if type(value) == ValueClass : val = value
        else: val = ValueClass(value)
        if ValueClass == ResultValue :
            if val.ind != ES.nullInd :
                for i in range(len(self.valueList)):
                    if self.valueList[i].ind == val.ind : return i                
            self.valueList.append(val)
        else :
            for i in range(len(self.valueList)):
                if self.valueList[i] == val and ES.mOption["unic_index"]: return i
            self.valueList.append(val)
        self.nValue = len(self.valueList)
        return len(self.valueList) - 1

    def jsonESSet(self, ES_valName, option):
        try:
            if len(self.valueList) == 0: return ""
        except: return""
        elt_type_nb = 0
        if option["json_elt_type"] : elt_type_nb = min(2, self.nValue)
        js = ""
        if option["json_ESobs_class"]: js = '"' + self.classES + '":{'
        js += self.jsonAtt(elt_type_nb) 
        js += '"' + ES_valName + '":' + self.jsonSet(option) + ","
        if js[-1] == ',': js = js[:-1]
        if option["json_ESobs_class"]: js += '}' 
        return js

    def jsonSet(self, option) :
        if len(self.valueList) == 0 : return ""
        if len(self.valueList) == 1 : return self.valueList[0].json(option)
        li = list()
        for i in range(self.nValue): 
            try: li.append(json.loads(self.valueList[i].json(option)))
            except: li.append(self.valueList[i].json(option))    
        return json.dumps(li)

    def to_bytes(self, nameES = False, resIndex = False, forma = 'null', prpList = []):
        byt = bytes()
        offset = 3 * (not nameES)
        code_el = ES.codeb[self.classES] # type de ESobs
        if code_el < 4 : code_ES = ES.codeb[self.mAtt[ES.type]] + offset # choix name ou value
        else : code_ES = ES.prop[forma][0]     
        if code_el == 4 and resIndex : code_el = 5
        unique = self.nValue == 1 
        oct1 = (code_el << 5) | (unique << 4) | code_ES
        byt += struct.pack('<B', oct1)
        if not unique : byt += struct.pack('<H', self.nValue)
        for i in range(self.nValue) :
            prp = forma
            if forma == 'null' and prpList == [] : prp = "null"
            if (nameES and code_el < 4) or (code_el > 3 and forma == "UTF-8") : 
                byt += self.valueList[i].to_strBytes()
            elif not nameES and code_el < 4 : byt += self.valueList[i].to_bytes()
            elif code_el < 6 : 
                #if forma == 'null' and prpList != [] : prp = prpList[i]
                if forma == 'null' and prpList != [] : prp = prpList[self.valueList[i].ind[2]]
                byt += self.valueList[i].to_bytes(resIndex, prp)
        return byt
    
    def from_bytes(self, byt, prpList = []):  #prplist complète si sans index
        code_ES =  byt[0] & 0b00001111
        unique  = (byt[0] & 0b00010000) >> 4
        code_el = (byt[0] & 0b11100000) >> 5
        nameES = not(code_ES // 3)
        forma = 'null'
        if code_el > 3 : forma = ES.cnum[code_ES]
        resIndex = code_el == 5
        nVal = 1
        idx = 1
        n = 0
        if not unique : 
            nVal = struct.unpack('<H',byt[1:3])[0]
            idx = 3
        for i in range(nVal):
            if   code_el < 4 : esValue = ValueCod[code_ES]
            elif code_el < 6 : esValue = ResultValue
            esVal = esValue()
            prp = forma
            if forma == 'null' and prpList == [] : prp = "null"
            #if prpList == [] : prp = "null"
            if (nameES and code_el < 4) or (code_el > 3 and forma == "utf-8") : 
                n = esVal.from_strBytes(byt[idx:])
            elif not nameES and code_el < 4 : n = esVal.from_bytes(byt[idx:])
            elif code_el < 6 and not resIndex: 
                if forma == 'null' and prpList != [] : prp = prpList[i]
                n = esVal.from_bytes(byt[idx:], resIndex, prp)
            elif code_el < 6 and resIndex : 
                nPrp = struct.unpack('<BBB',byt[idx:idx+3])[2]
                if forma == 'null' and prpList != [] : prp = prpList[nPrp]
                n = esVal.from_bytes(byt[idx:], resIndex, prp)
            self.addValue(esValue, esVal)
            idx += n
        return idx
        
    def __len__(self): 
        try: return len(self.valueList)
        except : return 0
    
    def __getitem__(self, key): return self.valueList[key]
    
    def	__setitem__(self, key, value): self.valueList[key] = value

    def __repr__(self): return object.__repr__(self) + '\n' + self.jsonSet(ES.mOption) + '\n'

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

    def sort(self, order = [], update = True):
        if order == [] :
            listInd = sorted(list(zip(self.valueList, list(range(self.nValue)))))
            valueTri, indTri = zip(*listInd)
            if update : self.valueList = list(valueTri)
        else :
            if update : self.valueList = [self.valueList[order[i]] for i in range(len(self.valueList))]
            indTri = order
        return list(indTri)
        
'''class TimeSlot:
    def __init__(self, val= ES.nullDate):
        if   type(val) == DatationValue:
            self.slot1 = val.slot.slot1
            self.slot2 = val.slot.slot2
        elif type(val) == list:  
            self.slot1 = datetime.fromisoformat(val[0])
            self.slot2 = datetime.fromisoformat(val[1])
        elif type(val) == datetime: 
            self.slot1 = val
            self.slot2 = self.slot1
        elif type(val) == numpy.datetime64 :
            self.slot1 = pandas.Timestamp(val).to_pydatetime()
            self.slot2 = self.slot1                    
        elif type(val) == pandas._libs.tslibs.timestamps.Timestamp :
            self.slot1 = val.to_pydatetime()
            self.slot2 = self.slot1            
        elif type(val) == str: 
            try:
                self.slot1 = datetime.fromisoformat(val)
                self.slot2 = self.slot1
            except:
                try:
                    val2 = json.loads(val)
                    self.slot1 = datetime.fromisoformat(val2[0])
                    self.slot2 = datetime.fromisoformat(val2[1])
                except:
                    self.slot1= ES.nullDate
                    self.slot2 = self.slot1
        else: 
            self.slot1= ES.nullDate
            self.slot2 = self.slot1

    def __repr__(self): return object.__repr__(self) + '\n' + self.json()

    def __eq__(self, other): return self.slot1 == other.slot1 and self.slot2 == other.slot2

    def json(self): return json.dumps([self.slot1.isoformat(), self.slot2.isoformat()])
    @property
    def centroid(self): return self.slot1 + (self.slot2 - self.slot1) / 2'''

        