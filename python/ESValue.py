# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module groups together the classes of the objects used in the `ES.ESObs` module :
    
- `ES.ESValue.DatationValue`,
- `ES.ESValue.LocationValue`,
- `ES.ESValue.PropertyValue`,
- `ES.ESValue.ResultValue`

the parent classes :
    
- `ES.ESValue.ESValue`, 
- `ES.ESValue.ESIndexValue`.

and the `ES.ESValue.ESSet` class.   
"""

import json, geojson, struct, numpy, pandas, shapely, copy
from datetime import datetime
from ESconstante import ES #, _identity
#from shapely.geometry import shape #, mapping
from ESElement import isESAtt, isUserAtt
from geopy import distance
#from ESObservation import Observation
#import ESObservation
from openlocationcode import encode
from ESSlot import TimeSlot

def _gshape(coord):
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
      `ES.ESValue.ResultValue`)
    """
    '''def mini(x, y):
        if type(x) == LocationValue: mm = LocationValue([min(x.vPoint()[0], y.vPoint()[0]), min(x.vPoint()[1], y.vPoint()[1])])
        elif type(x) == DatationValue: mm = DatationValue(min(x.instant, y.instant))
        else : mm = x
        return mm

    def maxi(x, y):
        if type(x) == LocationValue:
            mm = LocationValue([max(x.vPoint()[0], y.vPoint()[0]), max(x.vPoint()[1], y.vPoint()[1])])
        elif type(x) == DatationValue: mm = DatationValue(max(x.instant, y.instant))  
        else : mm = x
        return mm'''
    
    def __init__(self):
        self.name = ES.nullName
        self.ValueClass = type(self)

    def vName(self, genName=ES.nullName):  
        if self.name == ES.nullName : return genName
        else : return self.name
    
    def majName(self, nam):
        #name = str(nam)
        #☺if type(name) != str : name = str(name)
        #if name != '' : self.name = name
        if nam != '' : self.name = nam

    def isEqual(self, val, name=True, value=True):
        equalName = self.name == val.name
        nullName  = self.name == ES.nullName
        if   type(self) == LocationValue : 
            nullValue  = self.shap  == _gshape(ES.nullCoor)
            equalValue = self.shap  == val.shap
        elif type(self) == DatationValue : 
            equalValue = self.slot  == val.slot
            nullValue  = self.slot  == TimeSlot()
        elif type(self) == PropertyValue : 
            equalValue = self == val
            nullValue = self == PropertyValue()
        elif type(self) == ResultValue :
            equalValue = self.value == val.value
            nullValue  = self.value != 'null' 
        else : equalValue = False
        return  (name and value and equalName and equalValue) or \
                (name and not value and equalName and not nullName) or \
                (not name and value and equalValue and not nullValue)
                #(not name or (name and equalName)) and (not value or (value and equalValue))
        '''equal = self.name != ES.nullName and self.name == val.name
        if not equal :
            if   type(self) == LocationValue and self.shap != _gshape(ES.nullCoor) :
                equal = self.shap  == val.shap
            elif type(self) == DatationValue and self.slot != TimeSlot() : 
                equal = self.slot  == val.slot
            elif type(self) == PropertyValue and self != PropertyValue() : 
                equal = self == val
            elif type(self) == ResultValue   and self.value != 'null' :
                equal = self.value == val.value
        return equal'''
    
    def majValue(self, val):
        if   type(self) == LocationValue : self.shap  = LocationValue(val).shap
        elif type(self) == DatationValue : self.slot  = DatationValue(val).slot
        elif type(self) == ResultValue   : self.value = ResultValue  (val).value
        '''if type(val) == LocationValue :
                if not simple and val.shap != None and val.shap != _gshape(ES.nullCoor) : 
                self.shap = val.shap
                self.point = [self.shap.centroid.x, self.shap.centroid.y]
                if simple and val.point != ES.nullCoor : self.point = val.point'''
        '''elif type(val) == DatationValue :
            if not simple and val.slot != [ES.nullDate, ES.nullDate] : 
                self.slot = val.slot
                self.instant = self.slot[0] + (self.slot[1] - self.slot[0]) / 2
            if simple and val.instant != ES.nullDate : self.instant = val.instant'''

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

class DatationValue(ESValue):   # !!! début ESValue
    valName     = ES.dat_valName
    valueType   = ES.dat_valueType
    
    def __init__(self, val=ES.nullDate, slot=TimeSlot(), name=ES.nullName):
        ESValue.__init__(self)
        self.slot = TimeSlot()
        self.init(val)
        if self.slot == TimeSlot() and slot != TimeSlot() : self.slot = TimeSlot(slot)
        if self.name == ES.nullName and name != ES.nullName : self.name = name

    def init(self, val = ES.nullDate):
        if type(val) == DatationValue:
            self.slot = val.slot
            self.name = val.name
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]
        self.slot = TimeSlot(val)
        if self.slot == TimeSlot() : 
            if type(val) == str and self.name == ES.nullName : self.name = val

    def __lt__(self, other): 
        if self.slot == other.slot : return self.name <  other.name
        else : return self.slot < other.slot
 
    def __eq__(self, other): 
        return self.slot == other.slot and self.name == other.name

    def __repr__(self): return self.json(string=True)

    def getInstant(self) : 
        if self.slot.type == 'instant': return self.slot.slot[0][0]
        else : return None 
    
    def getInterval(self) : 
        if self.slot.type == 'interval': return self.slot.slot[0]
        else : return None 

    @property
    def bounds(self):
        return self.slot.bounds

    def Interval(*args):
        return DatationValue(slot=TimeSlot([args[0], args[1]]), name='box')

    def Instant(arg):
        return DatationValue(slot=[arg, arg], name='point')

    def _Box(*args): return DatationValue.Interval(*args)
    
    @property
    def value(self): return self.slot

    @property 
    def vInterval(self): return self.slot.interval
            
    @property 
    def instant(self) : return self.slot.instant
        #return self.vInstant(string=False)

    def vInstant(self, string=True) :
        if string : return self.slot.instant.isoformat()
        else : return self.slot.instant

    def json(self, option=ES.mOption, string=True): 
        if self.name == ES.nullName : js = self.slot.json(string=False)
        elif self.slot == TimeSlot() : js = self.name
        else : js = {self.name : self.slot.json(string=False)}
        if string : return json.dumps(js)
        else : return js
                    
        '''val = self.vInstant(string=True)
        if option["json_dat_name"] and self.name != ES.nullName :
            if val != ES.nullDate.isoformat():  return json.dumps({self.name : val})
            else :                              return json.dumps(self.name)
        else : 
            if type(val) == str :               return val
            else :                              return json.dumps(val)'''

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

    def __init__(self, val=ES.nullCoor, shape=None, name=ES.nullName, geo=True, cart=True):
        ESValue.__init__(self)
        #self.point = ES.nullCoor
        #self.shap = None
        self.shap = _gshape(ES.nullCoor)
        self.geod = geo
        self.carto = cart
        self.init(val, shape, name)
    
    def init(self, val=ES.nullCoor, shape=None, name=ES.nullName):
        if type(val) == LocationValue :
            self.shap = val.shap
            #self.point = val.point
            self.name = val.name
            self.geod = val.geod
            self.carto = val.carto
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]   
        shap = _gshape(val)
        if shap == None :
            if type(val) == str and self.name == ES.nullName : self.name = val
        #elif type(shap) == shapely.geometry.point.Point : self.point = [shap.x, shap.y]
        else : self.shap = shap
        if self.shap == _gshape(ES.nullCoor) and shape != None : self.shap = shape
        if self.name == ES.nullName and name != ES.nullName : self.name = name

    def __eq__(self, other): return self.geod == other.geod \
        and self.carto == other.carto and self.shap == other.shap and self.name == other.name
        # and self.point == other.point 
        #or (self.name[0:3] == self.nullName and other.name[0:3] == self.nullName))

    #def __repr__(self): return object.__repr__(self) + '\n' + self.json()
    def __repr__(self): return self.json()

    def __lt__(self, other): 
        if self.coorInv==ES.nullCoor : return self.name <  other.name
        else : return distance.distance(self.coorInv, ES.distRef) <  distance.distance(other.coorInv, ES.distRef)
    
    @property
    def coorInv(self):  return [self.vPoint()[1], self.vPoint()[0]]
    
    def vPointInv(self):  return [self.vPoint()[1], self.vPoint()[0]]

    def getShap(self) : return self.shap

    def getPoint(self) : 
        if type(self.shap) == shapely.geometry.point.Point : return [self.shap.x, self.shap.y]
        #return self.point
    
    def vCodePlus(self,  option = ES.mOption) : 
        return encode(self.vPoint(option)[1], self.vPoint(option)[0]) 
    
    @property
    def bounds(self):
        return self.shap.bounds

    def Cuboid(*args):
        return LocationValue(shape=shapely.geometry.box(*args), name='box')

    def _Box(*args): return LocationValue.Cuboid(*args)

    def Point(*args):
        return LocationValue(shape=shapely.geometry.Point(*args), name='point')

    @property
    def value(self): return self.shap
 
    def vShap(self): return self.shap
        #if self.shap != None : return self.shap
        #else : return _gshape(self.point)
    #def vShapCoor(self) : 
        #return json.loads(json.dumps(list(self.shap.coords)))
        #return numpy.asarray(self.shap.coords).tolist()[0]
    
    def vPoint(self):  
        return [self.shap.centroid.x, self.shap.centroid.y]
        '''val = ES.nullCoor
        if self.shap != None :              val =  self.shap.__geo_interface__[ES.coordinates]
        else:                               val =  self.point
        if option["json_loc_point"]:
            if self.point != ES.nullCoor :  val =  self.point
            elif self.shap != None :        val = [self.shap.centroid.x, self.shap.centroid.y]
        return val'''

    def vPointX(self) : return self.vPoint()[0]
    def vPointY(self) : return self.vPoint()[1]

    def json(self, option=ES.mOption, string=True): 
        if self.name == ES.nullName : js = self.vPoint()
        elif self.vPoint() == ES.nullCoor : js = self.name
        else : js = {self.name : self.vPoint()}
        if string : return json.dumps(js)
        else : return js

    '''def json(self, option = ES.mOption): 
        #val = self.vShap()
        val = self.vPoint(option)
        if option["json_loc_name"] and self.name != ES.nullName :
            if val != ES.nullCoor: return json.dumps({self.name : val})
            else : return json.dumps(self.name)
        else : return json.dumps(val)'''

    def to_bytes(self):
        return struct.pack('<ll',round(self.vPoint()[0]*10**7), round(self.vPoint()[1]*10**7))
        #return struct.pack('<ll',round(self.point[0]*10**7), round(self.point[1]*10**7))
        
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
        elif type(val) == PropertyValue :
            self.name           = val.name
            self.pType          = val.pType
            self.unit           = val.unit
            self.sampling       = val.sampling
            self.application    = val.application
            self.period         = val.period
            self.interval       = val.interval
            self.uncertain      = val.uncertain
            self.EMFId          = val.EMFId
            self.detail         = val.detail
        

    def __eq__(self, other): return self.pType == other.pType and \
        self.unit == other.unit and self.sampling == other.sampling and \
        self.application == other.application and self.EMFId == other.EMFId and \
        self.detail == other.detail and self.name == other.name
        #or (self.name[0:3] == self.nullName and other.name[0:3] == self.nullName)))

    def __repr__(self): return self.json(ES.mOption)

    def __lt__(self, other): 
        return self.pType + self.name < other.pType + other.name

    '''def json(self, option = ES.mOption): 
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
            if li == {} : return json.dumps(self.name)
            else : li[ES.prp_name] = json.dumps(self.name) 
        return json.dumps(li, ensure_ascii=False)'''

    def jsonDict(self, string=True): 
        li = dict()
        if (self.pType != "null"):   li[ES.prp_propType] = self.pType
        if (self.unit != "null"):           li[ES.prp_unit]     = self.unit
        if (self.sampling != "null"):       li[ES.prp_sampling] = self.sampling
        if (self.application != "null"):    li[ES.prp_appli]    = self.application
        if (self.period != 0):              li[ES.prp_period]   = self.period
        if (self.interval != 0):            li[ES.prp_interval] = self.interval
        if (self.uncertain != 0):           li[ES.prp_uncertain]= self.uncertain
        if (self.EMFId != "null"):          li[ES.prp_EMFId]    = self.EMFId
        li |= self.detail
        if string : return json.dumps(li, ensure_ascii=False)
        else : return li

    def json(self, option=ES.mOption, string=True): 
        if self.name == ES.nullName : js = self.jsonDict(False)
        elif self.jsonDict(False) == {} : js = self.name
        else : js = {self.name : self.jsonDict(False)}
        if string : return json.dumps(js,  ensure_ascii=False)
        else : return js

    def vType(self): return self.name + self.pType
    
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
        self.pType      = ES.invProp[prp[0]]
        self.unit       = ES.prop[ES.invProp[prp[0]]][5]
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
            self.name = val.name
            self.value = val.value
            self.ind = val.ind
        elif (type(val) == float or type(val) == int): self.setValue(val)
        else : 
            from ESObservation import Observation
            if type(val) == Observation : self.setValue(val.name)
            else : self.setValue(json.dumps(val))
        if type(ind) == list and ind != ES.nullInd and self.ind == ES.nullInd : self.ind = ind

    def __eq__(self, other): return self.value == other.value

    def __lt__(self, other):  
        order = ES.mOption["sort_order"]
        o = [ES.nax[order[0]], ES.nax[order[1]], ES.nax[order[2]]]
        #o = ES.mOption["sort_order"]
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

    def isNotNull(self): return self!=ResultValue()

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
    
class ESSet:        # !!! ESSet
    """
    Classe liée à la structure interne
    """

    def __init__(self, ValueClass = None, jObj = None):
        if ValueClass == None: return
        self.ValueClass = ValueClass
        self.valueList = list()
        ''' list : list of `ES.ESValue` '''
        #self.iSort = list()
        #self.nValue = 0
        #''' int : lenght of `ES.ESValue.ESSet.valueList` '''
        if  type(jObj) == list :
            try :
                for val in jObj : self.addValue(val)
            except : self.addValue(jObj)
        elif jObj == None : return 
        else : self.addValue(jObj)
        '''for val in jObj : self.addValue(ValueClass, val)
            except : self.addValue(ValueClass, jObj)
        elif jObj == None : return 
        else : self.addValue(ValueClass, jObj)'''

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
            #for vName in ValueClass.valName:   # si valeurs simple ou detaillee précisée 
            #    if vName in list(jDat): ESSet.__init__(self, ValueClass, jDat[vName])
            if ValueClass.valName in list(jDat):    # si valeurs simple ou detaillee précisée
                ESSet.__init__(self, ValueClass, jDat[ValueClass.valName]) # !!!        #elif type(jObj) == ValueClass or jObj == None : 
        #elif type(jObj) == ValueClass or jObj == None or type(jObj) == list :
        else :
            ESSet.__init__(self, ValueClass, jObj)
    
    @property
    def vListName(self):
        return [self.valueList[i].vName(ES.vName[self.classES] + str(i)) for i in range(self.nValue)]

    def vList(self, func=ES._identity):
        return [func(self.valueList[i]) for i in range(self.nValue)]
        
    def majListName(self, listVal):
        if len(listVal) != self.nValue : return
        #for i in range(self.nValue) : self.valueList[i].majName(listVal[i])
        for i in range(self.nValue) : self.valueList[i].majName(self.ValueClass(listVal[i]).name)

    def majList(self, listVal, name=False):
        if name : self.majListName(listVal)
        else : self.majListValue(listVal)
        
    def majListValue(self, listVal):
        if len(listVal) != self.nValue : return
        for i in range(self.nValue) : self.valueList[i].majValue(self.ValueClass(listVal[i]))
        
    def addValue(self, value, equal = 'full'):
    #def addValue(self, ValueClass, value):
        '''if type(value) == ValueClass : val = value
        else: val = ValueClass(value)
        if ValueClass == ResultValue :'''
        if type(value) == self.ValueClass : val = value
        else: val = self.ValueClass(value)
        if self.ValueClass == ResultValue :
            ind = self.indexResLoc(val)
            if ind != None : return 
            '''if val.ind != ES.nullInd :
                for i in range(len(self.valueList)):
                    if self.valueList[i].ind == val.ind : return i'''      
            #self.valueList.append(val)
        else :
            ind = self.indexLoc(val)[equal]
            if ES.mOption["unic_index"] and ind != -1 : return ind
            '''for i in range(len(self.valueList)):
                #if self.valueList[i] == val and ES.mOption["unic_index"]: return i
                if self.valueList[i].isEqual(val) and ES.mOption["unic_index"]: return i'''
        self.valueList.append(val)
        return len(self.valueList) - 1

    def indexResLoc(self, val):
        if self.ValueClass == ResultValue :
            if val.ind != ES.nullInd :
                for i in range(len(self.valueList)):
                    if self.valueList[i].ind == val.ind : return i     
                    
    def indexLoc(self, val):
        ind = {'full' : -1, 'name' : -1, 'value' : -1}
        for i in range(len(self.valueList)):
            if self.valueList[i].isEqual(self.ValueClass(val), name=True, value=True): 
                ind['full'] = ind['name'] = ind['value'] = i
                return ind
            if self.valueList[i].isEqual(self.ValueClass(val), name=True, value=False) \
                and ind['name'] == -1: 
                    ind['name'] = i
            if self.valueList[i].isEqual(self.ValueClass(val), name=False, value=True) \
                and ind['value'] == -1: 
                    ind['value'] = i
        return ind
            #if self.valueList[i].isEqual(self.ValueClass(val)): return i
        
    @property
    def nValue(self): return len(self.valueList)
        
    def jsonESSet(self, ES_valName, option):
        try:
            if len(self.valueList) == 0: return ""
        except: return""
        elt_type_nb = 0
        if option["json_elt_type"] : elt_type_nb = min(2, self.nValue)
        js = ""
        if option["json_ESobs_class"]: js = '"' + self.classES + '":{'
        js += self._jsonAtt(elt_type_nb) 
        js += '"' + ES_valName + '":' + self.jsonSet(option) + ","
        if js[-1] == ',': js = js[:-1]
        if option["json_ESobs_class"]: js += '}' 
        return js

    def jsonSet(self, option) :
        if self.ValueClass in [DatationValue, LocationValue] :
            if len(self.valueList) == 0 : return ""
            if len(self.valueList) == 1 : return self.valueList[0].json(string=True) 
            li = list()
            for i in range(self.nValue): 
                li.append(self.valueList[i].json(string=False))
            return json.dumps(li)
        else :
            if len(self.valueList) == 0 : return ""
            #if len(self.valueList) == 1 : return self.valueList[0].json(option) 
            if len(self.valueList) == 1 : return self.valueList[0].json() 
            li = list()
            for i in range(self.nValue): 
                try: li.append(json.loads(self.valueList[i].json(option)))
                except: li.append(self.valueList[i].json(option))
                #try: li.append(json.loads(self.valueList[i].json()))
                #except: li.append(self.valueList[i].json())    
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
        if code_el > 3 : forma = ES.invProp[code_ES]
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
            #self.addValue(esValue, esVal)
            self.addValue(esVal)
            idx += n
        return idx
        
    def __len__(self): 
        try: return len(self.valueList)
        except : return 0
    
    def __getitem__(self, key): return self.valueList[key]
    
    def __setitem__(self, key, value): self.valueList[key] = value

    def __repr__(self): return object.__repr__(self) + '\n' + self.jsonSet(ES.mOption) + '\n'

    def boundingBox(self):
        #box = copy.deepcopy(self.valueList[0])
        val = copy.deepcopy(self.valueList[0].value)
        for i in range(1,self.nValue): val = val.union(self.valueList[i].value)
        return self.ValueClass._Box(*val.bounds)

    def sort(self, order = [], update = True):
        if order == [] :
            listInd = sorted(list(zip(self.valueList, list(range(self.nValue)))), key= lambda z : z[0])
            valueTri, indTri = zip(*listInd)
            if update : self.valueList = list(valueTri)
        else :
            if update : self.valueList = [self.valueList[order[i]] for i in range(len(self.valueList))]
            indTri = order
        return list(indTri)
        
