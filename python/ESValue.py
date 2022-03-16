# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module groups the classes of the objects used in the `ES.Observation` module :
    
- `DatationValue`,
- `LocationValue`,
- `PropertyValue`,
- `ResultValue`

and the parent class :
    
- `ESValue`

# What is the ESValue Object ?

The ESValue is a class dedicated to Environmental data (such as dates, location or 
measurable properties) and groups common properties and concepts  :
    
- each ESValue can have three levels of representation : textual, simplified and complete
- ESValue has common function (getters, setters, boundary, conversion, export)
- each ESValue can have additional function or attribute

<img src="./ESValue_common.png" width="800">

ESValue is build around two attributes :
    
- 'name' which is a simple String
- 'value' which corresponds to a more or less complex object :
    
    - DatationValue : value is a TimeSlot Object which represent a set of time intervals
    - LocationValue : value is a Shapely Geometry which represent a set of polygons
    - PropertyValue : value is a simple dictionary which specifies all the characteristics of a property
    - ResultValue   : value can be any object

<img src="./ESValue_class.png" width="800">

"""
import json, geojson, struct, shapely.geometry
from datetime import datetime
from ESconstante import ES
from geopy import distance
#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/Slot')
from timeslot import TimeSlot
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/openLocationCode')
from openlocationcode import encode
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')

class ESValueEncoder(json.JSONEncoder):
    def default(self, value) :
        return value.json(json_string=False)
    
class ESValue:
    """
    This class is the parent class for each kind of values 
     (`DatationValue`, `LocationValue`, `PropertyValue`, `ResultValue`)

    *Attributes* :
    
    - **name**  : name  of `ESValue.ESValue` objects
    - **value** : value of `ESValue.ESValue` objects
    - `bounds` (@property) : boundary  of `ESValue.ESValue` objects
    - `simple` (@property) : simplified value of `ESValue.ESValue` objects
     
    The methods defined in this class are : 

    - `cast` (@staticmethod)
    - `getValue`
    - `getName`
    - `isEqual`
    - `isNotNull`
    - `json`
    - `setName`
    - `setValue`
    - `vName`
    - `vSimple`
    """   
    def __init__(self, val, name):
        '''Initialize 'name' and 'value' attribute'''
        self.name = ES.nullName
        self.value = self.nullValue()
        if type(val) == str : 
            try: val=json.loads(val)
            except: pass
        self._init(val)
        if self.name == ES.nullName and type(name) == str and name != ES.nullName : self.name = name

    def __eq__(self, other): 
        return self.value == other.value and self.name == other.name

    def __lt__(self, other): 
        if self.value == other.value : return self.name <  other.name
        else : return self.value < other.value
     
    def __repr__(self): return self.json(json_string=True)

    def __copy__(self): return self.__class__(self)

    def __hash__(self): return hash(self.json())

    @property
    def bounds(self):
        '''list or tuple (@property) 
            DatationValue : datetime.isoformat boundingBox (tmin, tmax)
            LocationValue : boundingBox (minx, miny, maxx, maxy)
            Other ESValue : () '''        
        try :
            return self.value.bounds
        except :
            return ()
    
    @staticmethod
    def cast(value, ValueClass):
        '''
        tranform a value in a list of `ESValue`

        *Parameters*
        
        - **value** : value to transform
        - **ValueClass** : `ESValue` class
        
        *Returns*
        
        - **list** : list of `ESValue`
        '''
        if type(value) == list :
            try : 
                return [ValueClass(val) for val in value]
            except :
                return [ValueClass(value)]
        else : return  [ValueClass(value)]
    
    def getValue(self) : 
        ''' return self.value object ''' 
        return self.value

    def getName(self) : 
        ''' return self.name object ''' 
        return self.name

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
        ListESValue = [LocationValue, DatationValue, PropertyValue, ResultValue]
        if   self.__class__ in ListESValue  : 
            nullValue  = self.value  == self.__class__.nullValue()
            equalValue = self.value  == other.value
        else : equalValue = False
        return  (name and     value and equalName  and equalValue) or \
                (name and not value and equalName  and not nullName) or \
                (not name and value and equalValue and not nullValue)

    def isNotNull(self): 
        '''return boolean. True if the 'ESValue' is not a NullValue'''
        return self != self.__class__()
    
    def json(self, **kwargs): 
        '''
        Export in Json format (string or dict). 
        
        *Parameters*
        
        - **json_string** : boolean (default True) - choice for return format (string if True, dict else)
        - **json_res_index** : boolean - include index (for ResultValue)
                
        *Returns* :  string or dict '''
        option = ES.mOption | kwargs
        if self.name == ES.nullName :                   js =  self._jsonValue(**option)
        elif self.value == self.__class__.nullValue() : js =  self.name
        else :                                          js = {self.name : self._jsonValue(**option)}        
        if option['json_string'] : return json.dumps(js, ensure_ascii=False)
        else : return js
    
    def setName(self, nam):
        '''
        Set the Name of the `ESValue`

        *Parameters*
        
        - **nam** : string - value to set
        
        *Returns* : None'''
        if nam != ES.nullName : self.name = nam

    def setValue(self, val):
        '''
        Set a new Value

        *Parameters*
        
        - **val** : compatible ESValue - New ESValue
        
        *Returns* : None'''        
        self.value  = self.__class__(val).value

    @property
    def simple(self): 
        '''vSimple object (@property) '''
        return self.vSimple(string=False)    

    def vSimple(self, string=False): 
        ''' Return the vSimple of the `ESValue`  '''
        return self.__class__.vSimple(self, string=string)
              
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
    
    - **value** : TimeSlot object (instant, interval or list of interval)
    - **name** : String
     
    The methods defined in this class are : 

    *getters*

    - `getInstant`
    - `getInterval`
    - `vSimple`
    - `vInterval`
    
    *conversion (static method)*

    - `Instant`
    - `Interval`

    *exports - imports*

    - `from_bytes`
    - `to_bytes`
    """
    valName     = ES.dat_valName

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
        ESValue.__init__(self, val, name)
        if self.value == self.__class__.nullValue() and TimeSlot(slot) != TimeSlot() : self.value = TimeSlot(slot)

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
        if self.value.type == 'instant': return self.value. slot[0][0]
        else : return None 
    
    def getInterval(self) : 
        '''[datetime t1, datetime t2] if 'interval', none else'''
        if self.value.type == 'interval': return self.value. slot[0]
        else : return None 

    @staticmethod
    def Instant(arg):
        '''DatationValue built with a compatible TimeSlot arg (static method)'''
        return DatationValue(slot=[arg, arg], name='instant')

    @staticmethod
    def Interval(minMax):
        '''DatationValue built with a compatible TimeSlot [arg1, arg2] (static method)'''
        return DatationValue(slot=TimeSlot([minMax[0], minMax[1]]), name='interval')

    @staticmethod
    def nullValue() : return TimeSlot(ES.nullDate)
    #def nullValue() : return TimeSlot()
    
    def to_bytes(self):
        '''
        Export in binary format. 
        
        *Returns*
        
        - **bytes** : binary representation of the `DatationValue` (datetime)
        '''
        return struct.pack('<HBBBBB', self.simple.year, self.simple.month,
                           self.simple.day, self.simple.hour,
                           self.simple.minute, self.simple.second)
        
    def vInterval(self, string=True): 
        '''[t1, t2] with t1, t2 - Mini, maxi of the DateSlot (timestamp or datetime). 
        
        *Parameters*
        
        - **string** : boolean (default True) - choice for return format (timestamp if True, datetime else)
                
        *Returns*
        
        - **JSON with timestamp or list with datetime**
        '''
        if string : return json.dumps([self.value.interval[0].isoformat(), self.value.interval[0].isoformat()])
        else : return self.value.interval
            
    def vSimple(self, string=False) : 
        '''datetime (@property) : middle of the TimeSlot'''
        if string : return self.value.instant.isoformat()
        else : return self.value.instant


    def _init(self, val = ES.nullDate):
        ''' DatationValue creation '''
        if type(val) == DatationValue:
            self.value = val.value
            self.name = val.name
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]
        self.value = TimeSlot(val)
        if self.value == TimeSlot() : 
            if type(val) == str and self.name == ES.nullName : self.name = val
            self.value = TimeSlot(ES.nullDate) #!!!!!

    def _jsonValue(self, **kwargs): return self.value.json(string=False)
    
    @staticmethod
    def _Box(minMax): return DatationValue.Interval(minMax)
    
class LocationValue(ESValue):              # !!! début LocationValue
    """
    This class represent the Location of an Observation (point, polygon).
    
    *Attributes (for @property see methods)* :
    
    - **value** : Shapely object (instant, interval or list of interval)
    - **name** : String
     
    The methods defined in this class are : 

    *getters (@property)*

    - `coords`
    - `coorInv`

    *getters*

    - `getPoint`
    - `vSimple`
    - `vPointInv`
    - `vPointX`
    - `vPointY`
    - `vCodePlus`
    
    *conversion (static method)*

    - `Point`
    - `Cuboid`

    *exports - imports*

    - `from_bytes`
    - `to_bytes`

    """
    valName     = ES.loc_valName
    
    def __init__(self, val=ES.nullCoor, shape=None, name=ES.nullName):
        '''Several LocationValue creation modes :
        
        - LocationValue({name : coord}) where coord is a GeoJSON or list coordinates format
        - LocationValue(coord) where coord is a is a GeoJSON or list coordinates format
        - LocationValue(name) where name is a string
        - LocationValue(locval) where locval is a LocationValue object (copy) 
        - LocationValue(shape=shape, name=name) where shape is a shapely.geometry.Point 
        (or Polygon) and name is a string
        '''
        ESValue.__init__(self, val, name)
        if self.value == self.nullValue() and shape != None : self.value = shape
    
    def __lt__(self, other): 
        if self.coorInv==ES.nullCoor : return self.name <  other.name
        else : return distance.distance(self.coorInv, ES.distRef) <  \
                      distance.distance(other.coorInv, ES.distRef)

    @property
    def coords(self):
        ''' return geoJson coordinates'''
        if type(self.value) == shapely.geometry.polygon.Polygon:  
            coords = [list(self.value.exterior.coords)]
        elif type(self.value) == shapely.geometry.point.Point:
            coords = list(self.value.coords)[0]
        elif type(self.value) == shapely.geometry.linestring.LineString:  
            coords = list(self.value.coords)
        else : coords = ES.nullCoor
        return json.loads(json.dumps(coords))
    
    @property
    def coorInv(self):  
        '''list (@property) : vSimple inverse coordinates [vSimple[1], vSimple[0]]'''
        return [self.vSimple()[1], self.vSimple()[0]]
    
    @staticmethod
    def Cuboid(minMax, ccw=True):
        '''LocationValue built with shapely.geometry.box parameters (static method)'''
        return LocationValue(shape=shapely.geometry.box(*minMax, ccw), name='box')

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
    
    def getPoint(self) : 
        ''' return a list with point coordinates [x, y] if the shape is a point ''' 
        if type(self.value) == shapely.geometry.point.Point : return [self.value.x, self.value.y]

    @staticmethod
    def nullValue() : return LocationValue._gshape(ES.nullCoor)

    @staticmethod
    def Point(x, y):
        '''LocationValue built with a compatible TimeSlot arg (static method)'''
        return LocationValue(shape=shapely.geometry.Point(x, y), name='point')

    def to_bytes(self):
        '''Export in binary format. 
        
        *Returns*
        
        - **bytes** : binary representation of the `LocationValue` (point coordinates)
        '''
        return struct.pack('<ll',round(self.vSimple()[0]*10**7), round(self.vSimple()[1]*10**7))
        
    def vCodePlus(self) : 
        ''' return CodePlus value (string) of the point property value''' 
        return encode(self.vSimple(False)[1], self.vSimple(False)[0]) 
    
    def vSimple(self, string=False): 
        ''' return simple value (centroid coordinates for the shape : [x, y]) in a string format or in a object format''' 
        if string : return json.dumps([self.value.centroid.x, self.value.centroid.y])
        else : return [self.value.centroid.x, self.value.centroid.y]
    
    def vPointInv(self, string=False):  
        ''' return point (property) inversed coordinates in a string format or
        in a list format [y, x]''' 
        return [self.vSimple()[1], self.vSimple()[0]]

    def vPointX(self) : 
        ''' return point (property) coordinates x ''' 
        return self.vSimple()[0]
    
    def vPointY(self) : 
        ''' return point (property) coordinates y ''' 
        return self.vSimple()[1]

    @staticmethod
    def _Box(minMax): return LocationValue.Cuboid(minMax)
    
    def _jsonValue(self, **kwargs): return self.coords

    def _init(self, val=ES.nullCoor):
        ''' LocationValue creation '''
        if type(val) == LocationValue :
            self.value = val.value
            self.name = val.name
            return
        elif type(val) == dict :
            self.name, val = list(val.items())[0]   
        shap = self._gshape(val)
        if shap == None :
            if type(val) == str and self.name == ES.nullName : self.name = val
        else : self.value = shap

    @staticmethod
    def _gshape(coord):
        ''' transform a GeoJSON coordinates (list) into a shapely geometry'''
        if type(coord) == list:  coor = json.dumps(coord)
        elif type(coord) == str: coor = coord
        else: coor = coord.__copy__()
        for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
            try:
                return shapely.geometry.shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coor + '}'))
            except: pass

class PropertyValue(ESValue):              # !!! début ESValue
    """
    This class represent the Property of an Observation.
    
    *Attributes (for @property see methods)* :
    
    - **value** : dict
    - **name** : String
     
    The methods defined in this class are : 

    *getters*

    - `vSimple`
    
    *exports - imports*

    - `from_bytes`
    - `to_bytes`

    """
    valName     = ES.prp_valName

    def __init__(self, val=ES.nullPrp, name=ES.nullName):
        ESValue.__init__(self, val, name)

    
    def __lt__(self, other): 
        return self.simple + self.name < other.simple + other.name

    def from_bytes(self, byt):
        bytl = byt[0:6] + b'\x00' +byt[6:9] + b'\x00' + byt[9:10]
        prp = struct.unpack('<BBBLLB', bytl)
        self.value[ES.prp_type]       = ES.invProp[prp[0]]
        self.value[ES.prp_unit]       = ES.prop[ES.invProp[prp[0]]][5]
        self.value[ES.prp_sampling]   = ES.invSampling[prp[1]]
        self.value[ES.prp_appli]      = ES.invApplication[prp[2]]
        self.value[ES.prp_period]     = prp[3]
        self.value[ES.prp_interval]   = prp[4]
        self.value[ES.prp_uncertain]  = prp[5] // 2
        return 10

    @staticmethod
    def nullValue() : return {ES.prp_type: ES.nullDict, ES.prp_unit: ES.prop[ES.nullDict][5]}
    
    def vSimple(self, string=False): 
        ''' return simple value (type for the property) in a string format or in a object format''' 
        if ES.prp_type in self.value : simple = self.value[ES.prp_type]
        else : simple = ES.nullDict
        if string : return json.dumps(simple)
        else : return simple
        
    def to_bytes(self):
        if ES.prp_sampling in self.value : sampling = self.value[ES.prp_sampling]
        else : sampling = ES.nullDict
        if ES.prp_appli in self.value    : appli    = self.value[ES.prp_appli]
        else : appli    = ES.nullDict
        if ES.prp_period in self.value   : period   = self.value[ES.prp_period]
        else : period   = ES.nullVal
        if ES.prp_interval in self.value : interval = self.value[ES.prp_interval]
        else : interval = ES.nullVal
        if ES.prp_uncertain in self.value: uncertain= self.value[ES.prp_uncertain]
        else : uncertain = ES.nullVal
        byt = struct.pack('<BBBLLB', ES.prop[self.simple][0], 
                           ES.sampling[sampling],
                           ES.application[appli],
                           period, interval, uncertain * 2 )
        return byt[0:6] +byt[7:10] + byt[11:12]
        
    def _jsonValue(self, **kwargs): return self._jsonDict(False)
      
    def _init(self, val={}):
        if type(val) == dict : self.value |= val
        elif type(val) == str : self.name = val
        elif type(val) == PropertyValue : 
            self.value = val.value
            self.name  = val.name
        self.value[ES.prp_unit] = ES.prop[self.value[ES.prp_type]][5]

    def _jsonDict(self, string=True): 
        li = dict()
        for k, v in self.value.items() :
            if   k in [ES.prp_type, ES.prp_unit, ES.prp_sampling, ES.prp_appli, ES.prp_EMFId] :
                if v != ES.nullDict: li[k] = v
            elif k in [ES.prp_period, ES.prp_interval, ES.prp_uncertain] :
                if v != ES.nullVal : li[k] = v
            else : li[k] = v
        if string : return json.dumps(li, ensure_ascii=False)
        else : return li

class ResultValue (ESValue):               # !!! début ESValue
    '''
    This class represent the Result of an Observation.
    
    *Attributes (for @property see methods)* :
    
    - **value** : any kind of object
    - **ind** : list, index [location, datation, property]
    - **name** : String
     
    The methods defined in this class are : 

    *exports - imports*

    - `from_bytes`
    - `to_bytes`
    - `to_float`

    '''
    valName     = ES.res_valName

    def __init__(self, val = ES.nullVal, name=ES.nullName):
        '''
        Several ResultValue creation modes :
            
        - ResultValue({name : value}) 
        - ResultValue(value) 
        - ResultValue(resval) 
        - ResultValue(value, ind=ind, name=name) 
        
        where 'resval' is a ResultValue(copy), 'value' is a 'result' or ['result', 'ind'],
        'result' is an Object, 'ind' is a list with three integer and 'name' is a string.        
        '''
        ESValue.__init__(self, val, name)

    @staticmethod
    def nullValue() : return ES.nullVal
         
    def to_float(self):
        if self.value == None :         return float('nan')
        elif type(self.value)==str:
            if self.value == ES.nullAtt:return float('nan')
            else : 
                try:                    return float(self.value)
                except:                 return float('nan')
        else :                          return float(self.value)           

    def vSimple(self, string=False) : 
        '''float value'''
        if string : return str(self.to_float())
        else : return self.to_float()

    def _init(self, val = None):
        try : 
            self.name = val.name
            self.value = val.value
        except :
            if type(val) == dict :
                self.name, val = list(val.items())[0]   
            if type(val) == str : 
                self.value = val
            else: self.value = val

    def _jsonValue(self, **option) : 
        if type(self.value) in [str, int, float]: val = self.value 
        else : val = object.__repr__(self.value)
        return val 