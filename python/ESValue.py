# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module groups the classes of the objects used in the `ES.ESObs` module :
    
- `DatationValue`,
- `LocationValue`,
- `PropertyValue`,
- `ResultValue`

the parent class :
    
- `ESValue`

"""

import json, geojson, struct, shapely
from datetime import datetime
from ESconstante import ES
from geopy import distance
from openlocationcode import encode
from ESSlot import TimeSlot

class ESValue:
    """
    This class is the parent class for each kind of values 
     (`DatationValue`, `LocationValue`, `PropertyValue`, `ResultValue`)
     
    The methods defined in this class are : 

    - `isEqual`
    - `setName`
    - `setValue`
    - `vName`

    """
    def __init__(self):
        '''This method initialize the 'name' and the 'ValueClass' attribute'''
        self.name = ES.nullName
        self.ValueClass = type(self)

    def isEqual(self, other, name=True, value=True):
        '''
        Compare two `ESValue`

        *Parameters*
        
        - **other** : ESValue
        - **name** : boolean (default True) - Include Name in comparison
        - **value** : boolean (default True) - Include Value in comparison
        
        *Returns*
        
        - **boolean** : Result of the comparison
        '''
        equalName = self.name == other.name
        nullName  = self.name == ES.nullName
        if   type(self) == LocationValue : 
            nullValue  = self.shap  == LocationValue._gshape(ES.nullCoor)
            equalValue = self.shap  == other.shap
        elif type(self) == DatationValue : 
            equalValue = self.slot  == other.slot
            nullValue  = self.slot  == TimeSlot()
        elif type(self) == PropertyValue : 
            equalValue = self == other
            nullValue = self == PropertyValue()
        elif type(self) == ResultValue :
            equalValue = self.value == other.value
            nullValue  = self.value != 'null' 
        else : equalValue = False
        return  (name and     value and equalName  and equalValue) or \
                (name and not value and equalName  and not nullName) or \
                (not name and value and equalValue and not nullValue)
    
    def setName(self, nam):
        '''
        Set the Name of the `ESValue`

        *Parameters*
        
        - **nam** : string - value to set
        
        *Returns*
        
        - **None**
        '''
        if nam != ES.nullName : self.name = nam

    def setValue(self, val):
        '''
        Set a new Value

        *Parameters*
        
        - **val** : compatible ESValue - New ESValue
        
        *Returns*
        
        - **None** 
        '''        
        if   type(self) == LocationValue : self.shap  = LocationValue(val).shap
        elif type(self) == DatationValue : self.slot  = DatationValue(val).slot
        elif type(self) == ResultValue   : self.value = ResultValue  (val).value

    def vName(self, genName=ES.nullName):  
        '''
        Return the Name of the `ESValue`

        *Parameters*
        
        - **genName** : string (default nullName) - Return Name if nullName
        
        *Returns*
        
        - **str** : Name of the ESValue
        '''
        if self.name == ES.nullName : return genName
        else : return self.name
    
    def _to_strBytes(self, simple = False):
        bval = str.encode(self.name)
        if simple : return bval
        else : return struct.pack('>B', bval.__len__()) + bval
        
    def _from_strBytes(self, byt, simple = False):
        if simple : 
            siz = byt.__len__()
            name = bytes.decode(byt)
        else : 
            siz = struct.unpack('>B', byt[0:1])[0]
            name = bytes.decode(byt[1: siz + 1])
        self._init(name)
        return siz + 1
                
class DatationValue(ESValue):   # !!! début ESValue
    """
    This class represent Time (instant, interval or set of intervals).
    
    *Attributes (for @property see methods)* :
    
    - **slot** : TimeSlot object (instant, interval or list of interval)
    - **name** : String
     
    The methods defined in this class are : 

    *property (getters)*

    - `bounds`
    - `instant`
    - `value`

    *getters*

    - `getInstant`
    - `getInterval`
    - `vInstant`
    - `vInterval`
    
    *conversion (static method)*

    - `Instant`
    - `Interval`

    *exports - imports*

    - `json`
    - `from_bytes`
    - `to_bytes`
    """
    valName     = ES.dat_valName
    valueType   = ES.dat_valueType
    
    def __init__(self, val=ES.nullDate, slot=TimeSlot(), name=ES.nullName):
        '''
        Several DatationValue creation modes :
        
        - DatationValue({name : timeSlot}) where timeSlot is a compatible TimeSlot Object
        - DatationValue(timeSlot) where timeSlot is a compatible TimeSlot Object
        - DatationValue(name) where name is a string
        - DatationValue(datval) where datval is a DatationValue object (copy)
        - DatationValue(slot=slot, name=name) where slot is a TimeSlot object 
        and name is a string
        
        '''
        ESValue.__init__(self)
        self.slot = TimeSlot()
        self._init(val)
        if self.slot == TimeSlot() and TimeSlot(slot) != TimeSlot() : self.slot = TimeSlot(slot)
        if self.name == ES.nullName and name != ES.nullName : self.name = name

    def __lt__(self, other): 
        if self.slot == other.slot : return self.name <  other.name
        else : return self.slot < other.slot
 
    def __eq__(self, other): 
        return self.slot == other.slot and self.name == other.name

    def __repr__(self): return self.json(string=True)

    @property
    def bounds(self):
        '''list (@property) : datetime.isoformat boundingBox [tmin, tmax]'''
        return self.slot.bounds

    def from_bytes(self, byt):
        '''
        Complete an empty `DatationValue` with binary data. 
        
        *Parameters*
        
        - **byt** : binary representation of a DatationValue (datetime)
        
        *Returns*
        
        - **int** : number of bytes used to decode a dateTime = 7
        '''
        dt = struct.unpack('<HBBBBB', byt[0:7])
        self._init(datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]))
        return 7

    def getInstant(self) : 
        '''datetime if 'instant', none else'''
        if self.slot.type == 'instant': return self.slot.slot[0][0]
        else : return None 
    
    def getInterval(self) : 
        '''[datetime t1, datetime t2] if 'interval', none else'''
        if self.slot.type == 'interval': return self.slot.slot[0]
        else : return None 

    @property 
    def instant(self) : 
        '''datetime (@property) : middle of the TimeSlot'''
        return self.slot.instant

    @staticmethod
    def Instant(arg):
        '''DatationValue built with a compatible TimeSlot arg (static method)'''
        return DatationValue(slot=[arg, arg], name='instant')

    @staticmethod
    def Interval(arg1, arg2):
        '''DatationValue built with a compatible TimeSlot [arg1, arg2] (static method)'''
        return DatationValue(slot=TimeSlot([arg1, arg2]), name='interval')

    def json(self, string=True): 
        '''
        Export in Json format (string or dict). 
        
        *Parameters*
        
        - **string** : boolean (default True) - choice for return formet (string if True, dict else)
                
        *Returns*
        
        - **string** : Json string 
        '''
        if self.name == ES.nullName : js = self.slot.json(string=False)
        elif self.slot == TimeSlot() : js = self.name
        else : js = {self.name : self.slot.json(string=False)}
        if string : return json.dumps(js)
        else : return js
                    
    def to_bytes(self):
        '''
        Export in binary format. 
        
        *Returns*
        
        - **bytes** : binary representation of the `DatationValue` (datetime)
        '''
        return struct.pack('<HBBBBB', self.instant.year, self.instant.month,
                           self.instant.day, self.instant.hour,
                           self.instant.minute, self.instant.second)
        
    @property
    def value(self): 
        '''TimeSlot (@property) : DatationValue slot'''
        return self.slot

    def vInterval(self, string=True): 
        '''[t1, t2] with t1, t2 - Mini, maxi of the DateSlot (timestamp or datetime). 
        
        *Parameters*
        
        - **string** : boolean (default True) - choice for return format (timestamp if True, datetime else)
                
        *Returns*
        
        - **JSON with timestamp or list with datetime**
        '''
        if string : return json.dumps([self.slot.interval[0].isoformat(), self.slot.interval[0].isoformat()])
        else : return self.slot.interval
            
    def vInstant(self, string=True) :
        '''Middle of the DatationValue slot (timestamp or datetime). 
        
        *Parameters*
        
        - **string** : boolean (default True) - choice for return format (timestamp if True, datetime else)
                
        *Returns*
        
        - **timestamp or datetime**
        '''
        if string : return self.slot.instant.isoformat()
        else : return self.slot.instant

    def _init(self, val = ES.nullDate):
        ''' DatationValue creation '''
        if type(val) == DatationValue:
            self.slot = val.slot
            self.name = val.name
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]
        self.slot = TimeSlot(val)
        if self.slot == TimeSlot() : 
            if type(val) == str and self.name == ES.nullName : self.name = val

    def _Box(*args): return DatationValue.Interval(*args)
    
class LocationValue(ESValue):              # !!! début LocationValue
    """
    This class represent the Location of an Observation (point, polygon).
    
    *Attributes (for @property see methods)* :
    
    - **shap** : Shapely object (instant, interval or list of interval)
    - **name** : String
     
    The methods defined in this class are : 

    *property (getters)*

    - `bounds`
    - `point`
    - `value`
    - `coorInv`

    *getters*

    - `getPoint`
    - `getShap`
    - `vPoint`
    - `vPointInv`
    - `vPointX`
    - `vPointY`
    - `vShap`
    - `vCodePlus`
    
    *conversion (static method)*

    - `Point`
    - `Cuboid`

    *exports - imports*

    - `json`
    - `from_bytes`
    - `to_bytes`

    """
    valName     = ES.loc_valName
    valueType   = ES.loc_valueType

    def __init__(self, val=ES.nullCoor, shape=None, name=ES.nullName):
        '''Several LocationValue creation modes :
        
        - LocationValue({name : coord}) where coord is a GeoJSON or list coordinates format
        - LocationValue(coord) where coord is a is a GeoJSON or list coordinates format
        - LocationValue(name) where name is a string
        - LocationValue(locval) where locval is a LocationValue object (copy) 
        - LocationValue(shape=shape, name=name) where shape is a shapely.geometry.Point 
        (or Polygon) and name is a string
        '''
        ESValue.__init__(self)
        self.shap = self._gshape(ES.nullCoor)
        self._init(val, shape, name)
    
    def __eq__(self, other): 
        return self.shap == other.shap and self.name  == other.name
    
    def __repr__(self): return self.json(string=True)

    def __lt__(self, other): 
        if self.coorInv==ES.nullCoor : return self.name <  other.name
        else : return distance.distance(self.coorInv, ES.distRef) <  \
                      distance.distance(other.coorInv, ES.distRef)
    
    @property
    def bounds(self):
        '''tuple (@property) : boundingBox (minx, miny, maxx, maxy)'''
        return self.shap.bounds

    @property
    def coorInv(self):  
        '''list (@property) : vPoint inverse coordinates [vPoint[1], vPoint[0]]'''
        return [self.vPoint()[1], self.vPoint()[0]]
    
    @staticmethod
    def Cuboid(minx, miny, maxx, maxy, ccw=True):
        '''LocationValue built with shapely.geometry.box parameters (static method)'''
        return LocationValue(shape=shapely.geometry.box(minx, miny, maxx, maxy, ccw), name='box')

    def from_bytes(self, byt):
        '''
        Complete an empty `LocationValue` with binary data (point)
        
        *Parameters*
        
        - **byt** : binary representation of a DatationValue (point)
        
        *Returns*
        
        - **int** : number of bytes used to decode a point = 8
        '''
        pt = list(struct.unpack('<ll', byt[0:8]))
        self._init(list((pt[0] *10**-7, pt[1] *10**-7)))
        return 8

    def getShap(self) : 
        ''' return self.shap object (shapely.geometry) ''' 
        return self.shap
    
    def getPoint(self) : 
        ''' return a list with point coordinates [x, y] if the shape is a point ''' 
        if type(self.shap) == shapely.geometry.point.Point : return [self.shap.x, self.shap.y]
        
    def json(self, option=ES.mOption, string=True): 
        ''' Export in Json format (string or dict). 
        
        *Parameters*
        
        - **string** : boolean (default True) - choice for return formet (string if True, dict else)
                
        *Returns*
        
        - **string** : Json string 
        '''
        if self.name == ES.nullName : js = self.vPoint()
        elif self.vPoint() == ES.nullCoor : js = self.name
        else : js = {self.name : self.vPoint()}
        if string : return json.dumps(js)
        else : return js

    @property
    def point(self): 
        '''list (@property) : centroid coordinates for the shape : [x, y]'''
        return [self.shap.centroid.x, self.shap.centroid.y]

    @staticmethod
    def Point(x, y):
        '''LocationValue built with a compatible TimeSlot arg (static method)'''
        return LocationValue(shape=shapely.geometry.Point(x, y), name='point')

    def to_bytes(self):
        '''Export in binary format. 
        
        *Returns*
        
        - **bytes** : binary representation of the `LocationValue` (point coordinates)
        '''
        return struct.pack('<ll',round(self.vPoint()[0]*10**7), round(self.vPoint()[1]*10**7))
        
    @property
    def value(self): 
        ''' return self.shap attribute''' 
        return self.shap
 
    def vCodePlus(self) : 
        ''' return CodePlus value (string) of the point property value''' 
        return encode(self.vPoint(False)[1], self.vPoint(False)[0]) 
    
    def vPoint(self, string=False): 
        ''' return point (property) coordinates in a string format or in a list format [x, y]''' 
        if string : return json.dumps(self.point)
        else : return self.point

    def vPointInv(self, string=False):  
        ''' return point (property) inversed coordinates in a string format or
        in a list format [y, x]''' 
        return [self.vPoint()[1], self.vPoint()[0]]

    def vPointX(self) : 
        ''' return point (property) coordinates x ''' 
        return self.vPoint()[0]
    
    def vPointY(self) : 
        ''' return point (property) coordinates y ''' 
        return self.vPoint()[1]

    def vShap(self): 
        ''' return self.shap object (shapely.geometry) ''' 
        return self.shap
    
    @staticmethod
    def _Box(*args): return LocationValue.Cuboid(*args)

    @staticmethod
    def _gshape(coord):
        ''' transform a GeoJSON coordinates (list) into a shapely geometry'''
        if type(coord) == list:  coor = json.dumps(coord)
        elif type(coord) == str: coor = coord
        else: coor = coord.copy()
        for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
            try:
                return shapely.geometry.shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coor + '}'))
            except: pass
    
    def _init(self, val=ES.nullCoor, shape=None, name=ES.nullName):
        ''' LocationValue creation '''
        if type(val) == LocationValue :
            self.shap = val.shap
            self.name = val.name
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]   
        shap = self._gshape(val)
        if shap == None :
            if type(val) == str and self.name == ES.nullName : self.name = val
        else : self.shap = shap
        if self.shap == self._gshape(ES.nullCoor) and shape != None : self.shap = shape
        if self.name == ES.nullName and name != ES.nullName : self.name = name

class PropertyValue(ESValue):              # !!! début ESValue
    """
    Classe liée à la structure interne
    """
    valName     = ES.prp_valName
    valueType   = ES.prp_valueType
    
    def __init__(self, val={}):
        ESValue.__init__(self)
        self.name           = ES.nullName
        self.pType          = ES.nullDict
        self.unit           = ES.nullDict
        self.sampling       = ES.nullDict
        self.application    = ES.nullDict
        self.period         = ES.nullVal
        self.interval       = ES.nullVal
        self.uncertain      = ES.nullVal
        self.EMFId          = ES.nullDict
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
        if self.unit == ES.nullDict : self.unit = ES.prop[self.pType][5]


    def __eq__(self, other): return self.pType == other.pType  and \
        self.sampling == other.sampling and \
        self.application == other.application and self.EMFId == other.EMFId and \
        self.detail == other.detail and self.name == other.name

    def __repr__(self): return self.json(ES.mOption)

    def __lt__(self, other): return self.pType + self.name < other.pType + other.name

    def _jsonDict(self, string=True): 
        li = dict()
        if self.pType       != ES.nullDict:   li[ES.prp_propType] = self.pType
        if self.unit        != ES.nullDict:   li[ES.prp_unit]     = self.unit
        if self.sampling    != ES.nullDict:   li[ES.prp_sampling] = self.sampling
        if self.application != ES.nullDict:   li[ES.prp_appli]    = self.application
        if self.period      != ES.nullVal:    li[ES.prp_period]   = self.period
        if self.interval    != ES.nullVal:    li[ES.prp_interval] = self.interval
        if self.uncertain   != ES.nullVal:    li[ES.prp_uncertain]= self.uncertain
        if self.EMFId       != ES.nullDict:   li[ES.prp_EMFId]    = self.EMFId
        li |= self.detail
        if string : return json.dumps(li, ensure_ascii=False)
        else : return li

    def json(self, option=ES.mOption, string=True): 
        if self.name == ES.nullName : js = self._jsonDict(False)
        elif self._jsonDict(False) == {} : js = self.name
        else : js = {self.name : self._jsonDict(False)}
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

class ResultValue (ESValue):               # !!! début ESValue
    """
    Classe liée à la structure interne
    """
    valName     = ES.res_valName
    valueType   = ES.res_valueType

    def __init__(self, val = None, ind = ES.nullInd):
        self.ind = ind
        ESValue.__init__(self)
        self._init(val, ind)
        
        
    def _init(self, val = None, ind = ES.nullInd):
        if type(val) == str : 
            try: js=json.loads(val)
            except:
                self._setValue(val)
                return
            if (type(js) == list and ind != ES.nullInd): self._setValue(json.dumps(js))
            elif (type(js) == list and ind == ES.nullInd): 
                if type(js[1]) == list: self.setIndValue(js)
                else: self._setValue(json.dumps(js))
            elif (type(js) == float or type(js) == int): self._setValue(js)
            else : self._setValue(json.dumps(js))
        elif type(val) == list : self.setIndValue(val)
        elif type(val) == ResultValue : 
            self.name = val.name
            self.value = val.value
            self.ind = val.ind
        elif (type(val) == float or type(val) == int): self._setValue(val)
        else : 
            from ESObservation import Observation
            if type(val) == Observation : self._setValue(val.name)
            else : self._setValue(json.dumps(val))
        if type(ind) == list and ind != ES.nullInd and self.ind == ES.nullInd : self.ind = ind

    def __eq__(self, other): return self.value == other.value

    def __lt__(self, other):  
        order = ES.mOption["sort_order"]
        o = [ES.nax[order[0]], ES.nax[order[1]], ES.nax[order[2]]]
        return self.ind[o[0]] < other.ind[o[0]] or \
              (self.ind[o[0]] == other.ind[o[0]] and self.ind[o[1]] <  other.ind[o[1]]) or \
              (self.ind[o[0]] == other.ind[o[0]] and self.ind[o[1]] == other.ind[o[1]] and self.ind[o[2]] < other.ind[o[2]])

    def __repr__(self): return  self.json(ES.mOption)

    def setIndValue(self, val):
        if (type(val) == list) : 
            self._setValue(val[0])
            self.ind = val[1]
        else : self.value = None

    def _setValue(self, val):
        if (type(val) in [str, int, float]) : self.value = val
        else : self.value = json.dumps(val)

    def json(self, option = ES.mOption): 
        if (type(self.value) == str and json.dumps(self.value)[1:-1]!=self.value):
            if option["json_res_index"]: return '[' + self.value + ', ' + json.dumps(self.ind) + ']'
            else: return self.value
        else:
            if option["json_res_index"] : return json.dumps([self.value, self.ind])
            else: return json.dumps(self.value)
    
    def to_bytes(self, resIndex = False, prp = ES.nullDict):
        formaPrp = ES.prop[prp][1]
        dexp = ES.prop[prp][3]
        bexp = ES.prop[prp][4]
        val = self.value * 10**-dexp * 2**-bexp
        if resIndex : return struct.pack('<BBB' + formaPrp,  self.ind[0],
                                         self.ind[1], self.ind[2], val)
        else : return struct.pack('<' + formaPrp, val)
        
    def from_bytes(self, byt, resInd = False, prp = ES.nullDict):
        formaPrp = ES.prop[prp][1]
        leng = ES.prop[prp][2]
        dexp = ES.prop[prp][3]
        bexp = ES.prop[prp][4]        
        if resInd :
            dt = struct.unpack('<BBB'+ formaPrp, byt[0:leng + 3])
            self._init(dt[3] * 10**dexp * 2**bexp, [dt[0], dt[1], dt[2]])
            return 3 + leng
        else :
            self._init(struct.unpack('<'+ formaPrp, byt[0:leng])[0] * 10**dexp * 2**bexp)
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
