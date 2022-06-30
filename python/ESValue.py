# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module groups the classes of the objects used in the `ES.Observation` module :

- `DatationValue`,
- `LocationValue`,
- `PropertyValue`,
- `NamedValue`
- `ExternValue`

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
    - NamedValue    : value can be any Json value
    - ExternValue   : value can be any object

<img src="./ESValue_class.png" width="800">

"""
import json, geojson, struct, shapely.geometry, re, bson
import datetime
from ESconstante import ES, _classval
from geopy import distance
#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/Slot')
from timeslot import TimeSlot
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/openLocationCode')
from openlocationcode import encode
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')

class ESValueEncoder(json.JSONEncoder):
    """add a new json encoder for ESValue"""
    def default(self, o) :
        if isinstance(o, datetime.datetime) : return o.isoformat()
        option = {'encoded': False, 'encode_format': 'json'}
        try : return o.json(**option)
        except :
            try : return o.__to_json__()
            except : return json.JSONEncoder.default(self, o)

class ESValue:
    """
    This class is the parent class for each kind of values
     (`DatationValue`, `LocationValue`, `PropertyValue`, `NamedValue`, `ExternValue`)

    *Attributes* :

    - **name**  : name  of `ESValue.ESValue` objects
    - **value** : value of `ESValue.ESValue` objects
    - **EStype** : type of `ESValue.ESValue` objects
    - `bounds` (@property) : boundary  of `ESValue.ESValue` objects
    - `simple` (@property) : simplified value of `ESValue.ESValue` objects

    The methods defined in this class are :

    **binary predicates**

    - `contains`
    - `equals`
    - `intersects`
    - `within`
    - `disjoint`
    - `isEqual`
    - `isNotNull`
    - `isName`

    **other methods**

    - `cast` (@classmethod)
    - `from_json` (@classmethod)
    - `getValue`
    - `getName`
    - `json`
    - `setName`
    - `setValue`
    - `vName`
    - `vSimple`
    """
#%% special
    def __init__(self, val, name, className=None):
        '''Initialize 'name' and 'value' attribute'''
        self.name = ES.nullName
        self.value = self.nullValue()
        self.EStype = 0
        if type(val) == str :
            try: val=json.loads(val)
            except: pass
        self._init(val, className)
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName : self.name = name

    def __eq__(self, other):
        '''equal if value and name are equal'''
        if not issubclass(other.__class__, ESValue): return False
        if self.EStype != other.EStype: return False
        if self.EStype == 0:            return True
        if self.EStype == 100:          return self.name == other.name
        if self.EStype < 100:           return self.value == other.value
        return self.value == other.value and self.name == other.name

    def __lt__(self, other):
        '''lower if value is lower. If values are equal, self is lower if name is lower'''
        if self.value == other.value : return self.name <  other.name
        return self.value < other.value

    def __str__(self):
        '''return json string format'''
        return self.json(encoded=True, encode_format='json')

    def __repr__(self):
        #return self.__class__.__name__ + f'({self.json(encoded=True, encode_format="json")})'
        return self.__class__.__name__ + '[' + ES.invntypevalue[self.EStype] + ']'

    def __copy__(self):
        '''return a new object with the same attributes'''
        return self.__class__(self)

    #def __hash__(self): return hash(self.json())
    def __hash__(self): return hash(self.__repr__())

    def __to_bytes__(self, **option):
        #js = {self.__class__.__name__ : self.json(encoded=False, encode_format='bson')}
        js = self.json(encoded=False, encode_format='bson')
        if option['encoded']: return bson.encode(js)
        return js

    @staticmethod
    def __from_bytes__(bs):
        if not isinstance(bs, (bytes, dict)): raise ESValueError("parameter is not dict or bytes")
        if isinstance(bs, bytes): dic = bson.decode(bs)
        else: dic = bs
        return dic
        #ClassValue = eval(list(dic.keys())[0])
        #return ClassValue(list(dic.values())[0])

#%% methods
    @classmethod
    def from_json(cls, bs):
        if not isinstance(bs, (str, bytes, dict)): raise ESValueError("parameter is not string, dict or bytes")
        if isinstance(bs, bytes): dic = bson.decode(bs)
        else: dic = bs
        return cls(dic)

    @property
    def bounds(self):
        '''list or tuple (@property)
            DatationValue : boundingBox (tmin, tmax)
            LocationValue : boundingBox (minx, miny, maxx, maxy)
            PropertyValue : boundingBox (list of type property)
            Other ESValue : () '''
        try :
            if isinstance(self, PropertyValue): return tuple(self.value[ES.prp_type])
            return self.value.bounds
        except :
            return ()

    def boxUnion(self, other, name=''):
        '''
        return the union between box(self) and box(other) (new `ESValue`) with a new name.
        '''
        if self.__class__ == PropertyValue :
            return PropertyValue.Box(sorted(list(self._setprp(self.value[ES.prp_type]) |
                                          self._setprp(other.value[ES.prp_type]))),
                                     name=name)
        sbox = self.Box (self. bounds).value
        obox = other.Box(other.bounds).value
        if sbox == obox: ubox = sbox
        else : ubox = sbox.union(obox)
        boxunion = self.__class__(val=self.Box(ubox.bounds))
        if name != '': boxunion.name = name
        return boxunion

    @classmethod
    def cast(cls, value):
        '''
        tranform a value (unique or list) in a list of `ESValue`

        *Parameters*

        - **value** : value to transform

        *Returns*

        - **list** : list of `ESValue`
        '''
        ValueClass = cls
        if isinstance(value, list):
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
        #ListESValue = [LocationValue, DatationValue, PropertyValue, NamedValue, ReesultValue]
        ListESValue = [LocationValue, DatationValue, PropertyValue, NamedValue, ExternValue]
        if   self.__class__ in ListESValue  :
            nullValue  = self.value  == self.__class__.nullValue()
            equalValue = self.value  == other.value
        else : equalValue = False
        return  (name and     value and equalName  and equalValue) or \
                (name and not value and equalName  and not nullName) or \
                (not name and value and equalValue and not nullValue)

    def isName(self, pattern):
        '''check if a pattern (regex) is presenty in the ESValue name.'''
        return re.search(pattern, self.getName()) is not None

    def equals(self, other):
        '''check if self value equals other value (return a boolean).'''
        return self.link(other) == 'equals'

    def disjoint(self, other):
        '''check if self value is disjoint from other value (return a boolean).'''
        return self.link(other) == 'disjoint'

    def contains(self, other):
        '''check if self value contains other value (return a boolean).'''
        return self.link(other) == 'contains'

    def within(self, other):
        '''check if self value is within other value (return a boolean).'''
        return self.link(other) == 'within'

    def intersects(self, other):
        '''check if self value intersects other value (return a boolean).'''
        return self.link(other) == 'intersects'

    def isNotNull(self):
        '''return boolean. True if the 'ESValue' is not a NullValue'''
        return self != self.__class__()

    def json(self, **kwargs):
        '''
        Export in json/bson format (string or dict).

        *Parameters*

        - **encoded** : boolean (default True) - choice for return format (string/bytes if True, dict else)
        - **encode_format**    : string (default 'json')- choice for return format (bson, json, cbor)

        *Returns* :  string or dict '''
        option = ES.mOption | kwargs
        option2 = option | {'encoded': False}
        if self.name == ES.nullName :                   js =  self._jsonValue(**option2)
        elif self.value == self.__class__.nullValue() : js =  self.name
        else :                                          js = {self.name : self._jsonValue(**option2)}
        if option['encoded'] and option['encode_format'] != 'bson': return json.dumps(js, cls=ESValueEncoder)
        if option['encoded'] and option['encode_format'] == 'bson': return bson.encode(js)
        return js

    def setName(self, nam):
        '''
        Set the Name of the `ESValue`

        *Parameters*

        - **nam** : string - value to set

        *Returns* : None'''
        self.name = nam
        if nam != ES.nullName :
            if self.EStype < 100: self.EStype += 100
        else:
            if self.EStype >= 100: self.EStype -= 100

    def setValue(self, val):
        '''
        Set a new Value

        *Parameters*

        - **val** : compatible ESValue - New ESValue

        *Returns* : None'''
        ESval = self.__class__(val)
        self.value  = ESval.value
        self.EStype = ESval.EStype

    @property
    def simple(self):
        '''vSimple object (@property) '''
        return self.vSimple(string=False)

    def to_float(self):
        '''converts into a float value '''
        if self.value == None :         return float('nan')
        if type(self.value)==str:
            if self.value == ES.nullAtt:return float('nan')
            try:                        return float(self.value)
            except:                     return float('nan')
        return float(self.value)

    def vSimple(self, string=False):
        ''' Return the vSimple of the `ESValue`  '''
        return self.__class__.vSimple(self, string=string)

    @staticmethod
    def valClassName(val):
        '''return the ESValue Class Name of val '''
        if val is None: return ES.nam_clsName
        if isinstance(val,(DatationValue, LocationValue, PropertyValue, NamedValue, 
                           ExternValue, TimeSlot)):
            return val.__class__.__name__
        if val.__class__.__name__ in [ES.obs_clsName, ES.ili_clsName, ES.tim_clsName]:
            return val.__class__.__name__
        if isinstance(val, str):
            try: dic = json.loads(val)
            except: dic = val  
        else: dic = val
        if isinstance(dic, (int, float, bool, list, str, tuple)): 
            return ES.nam_clsName
        if isinstance(dic, dict) and len(dic) != 1: 
            return ES.nam_clsName
        if isinstance(dic, dict) and len(dic) == 1 and list(dic.keys())[0] in ES.typeName.keys(): 
            return ES.typeName[list(dic.keys())[0]]
        if isinstance(dic, dict) and len(dic) == 1 and not list(dic.keys())[0] in ES.typeName.keys(): 
            if isinstance(list(dic.values())[0], (int, float, bool, list, str, dict)): 
                return ES.nam_clsName
            return ESValue.valClassName(list(dic.values())[0])
        return ES.nam_clsName
        #return None

    def vName(self, genName=ES.nullName):
        '''
        Return the Name of the `ESValue`

        *Parameters*

        - **genName** : string (default nullName) - Return Name if nullName

        *Returns*

        - **str** : Name of the ESValue
        '''
        if self.name == ES.nullName : return genName
        return self.name

    def _to_strBytes(self, simple=False, mini=False):
        bval = str.encode(self.name)
        if simple and mini : 
            #form='{:<'+str(ES.miniStr)+'}' 
            #return str.encode(form.format(self.name[0:ES.miniStr]))
            return str.encode(self.name[0:ES.miniStr].ljust(ES.miniStr))
        if simple and not mini : return bval
        return struct.pack('>B', len(bval)) + bval

    def _from_strBytes(self, byt, simple=False):
        if simple :
            siz = len(byt) - 1
            name = bytes.decode(byt).rstrip()          
        else :
            siz = struct.unpack('>B', byt[0:1])[0]
            name = bytes.decode(byt[1: siz + 1]).rstrip()
        self._init(name)
        return siz + 1

class DatationValue(ESValue):   # !!! début ESValue
#%% dat
    """
    This class represent Time (instant, interval or set of intervals).

    *Attributes (for @property see methods)* :

    - **value** : TimeSlot object (instant, interval or list of interval)
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Simple` (instant)
    - `Box`    (interval)

    *getters*

    - `getInstant`
    - `getInterval`
    - `vSimple`
    - `vInterval`

    *conversion (static method)*

    - `link`

    *exports - imports*

    - `from_bytes`
    - `to_bytes`
    """
    valName     = ES.dat_valName

    @classmethod
    def Simple(cls, instant):
        '''DatationValue built with a time value (instant) '''
        return cls(slot=TimeSlot(instant), name='instant')

    @classmethod
    def Box(cls, bounds):
        '''DatationValue built from a tuple or list box coordinates (tmin, tmax)'''
        if isinstance(bounds, cls): bound = bounds.bounds
        else : bound = bounds
        return cls(slot=TimeSlot(bound), name='interval')

    def __init__(self, val=ES.nullDate, name=ES.nullName, slot=TimeSlot()):
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
        if self.value == self.__class__.nullValue() and TimeSlot(slot) != TimeSlot() :
            self.value = TimeSlot(slot)
        if self.value == TimeSlot(ES.nullDate): self.EStype = 0
        else: self.EStype = ES.ntypevalue[self.value.stype]
        if self.name != ES.nullName: self.EStype += 100

    def from_bytes(self, byt, mini=False):
        '''
        Complete an empty `DatationValue` with binary data.

        *Parameters*

        - **byt** : binary representation of a DatationValue (datetime)

        *Returns*

        - **int** : number of bytes used to decode a dateTime = 7
        '''
        if mini:
            dt = struct.unpack('<HBB', byt[0:4])
            self._init(datetime.datetime(dt[0], dt[1], dt[2]))
            return 4
        dt = struct.unpack('<HBBBBB', byt[0:7])
        self._init(datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]))
        return 7

    def getInstant(self) :
        '''datetime if 'instant', none else'''
        if self.value.stype == 'instant': return self.value. slot[0][0]
        return None

    def getInterval(self) :
        '''[datetime t1, datetime t2] if 'interval', none else'''
        if self.value.stype == 'interval': return self.value. slot[0]
        return None

    def link(self, other):
        '''
        return the link (string) between self.value and other.value :
        - equals     : if self and other are the same
        - disjoint   : if self's intervals and other's intervals are all disjoint
        - within     : if all self's intervals are included in other's intervals
        - contains   : if all other's intervals are included in self's intervals
        - intersects : in the others cases'''
        if self.isEqual(other, name=False) : return 'equals'
        return self.value.link(other.value)[0]


    @staticmethod
    def nullValue() : return TimeSlot(ES.nullDate)

    def to_bytes(self, mini=False):
        '''
        Export in binary format.

        *Returns*

        - **bytes** : binary representation of the `DatationValue` (datetime)
        '''
        if mini: return struct.pack('<HBB', self.simple.year, self.simple.month,
                           self.simple.day)
        return struct.pack('<HBBBBB', self.simple.year, self.simple.month,
                           self.simple.day, self.simple.hour,
                           self.simple.minute, self.simple.second)

    def vInterval(self, encoded=True, encode_format='json'):
        """[t1, t2] with t1, t2 - Mini, maxi of the TimeSlot (timestamp or datetime).

        *Parameters*

        - **encode_format**    : string (default 'json')- choice for return format (bson, json, cbor)

        *Returns*

        - **JSON with timestamp or list with datetime**
        """
        return self.value.Bounds.json(encoded=encoded, encode_format=encode_format)
        #if not encoded: return self.value.interval
        #if encode_format == 'json':
        #    return json.dumps([self.value.interval[0].isoformat(),
        #                       self.value.interval[1].isoformat()], cls=ESValueEncoder)

    def vSimple(self, string=False) :
        """datetime (@property) : middle of the TimeSlot."""
        if string : return self.value.instant.isoformat()
        return self.value.instant


    def _init(self, val=ES.nullDate, className=None):
        """DatationValue creation (value and name)."""
        if type(val) == DatationValue:
            self.value = val.value
            self.name = val.name
            return
        if type(val) == dict : self.name, val = list(val.items())[0]
        self.value = TimeSlot(val)
        if self.value == TimeSlot() :
            if type(val) == str and self.name == ES.nullName : self.name = val
            self.value = TimeSlot(ES.nullDate)
        self.EStype = ES.ntypevalue[self.value.stype]

    def _jsonValue(self, **option):
        '''return a json/bson dict for the value (TimeSlot) '''
        return self.value.json(**option)

class LocationValue(ESValue):              # !!! début LocationValue
#%% loc
    """
    This class represent the Location of an Observation (point, polygon).

    *Attributes (for @property see methods)* :

    - **value** : Shapely object (point, polygon)
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Simple` (point)
    - `Box`

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

    - `link`

    *exports - imports*

    - `from_bytes`
    - `to_bytes`

    """
    valName     = ES.loc_valName

    @classmethod
    def Simple(cls, coord):
        '''LocationValue built with tuple or list coordinates (x,y)'''
        return cls(shape=shapely.geometry.Point(*coord), name='point')

    @classmethod
    def Box(cls, bounds, ccw=True):
        '''LocationValue built with tuple or list box coordinates (minx, miny, maxx, maxy)'''
        if isinstance(bounds, cls): bound = bounds.bounds
        else : bound = bounds
        return cls(shape=shapely.geometry.box(*bound, ccw), name='box')

    def __init__(self, val=ES.nullCoor, name=ES.nullName, shape=None):
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
        if self.value != self.nullValue():
            self.EStype = ES.ntypevalue[self.value.geom_type.lower()]
        if self.name != ES.nullName: self.EStype += 100

    def __lt__(self, other):
        if self.coorInv==ES.nullCoor : return self.name <  other.name
        return distance.distance(self.coorInv, ES.distRef) <  \
                      distance.distance(other.coorInv, ES.distRef)
    @property
    def __geo_interface__(self):
        return json.loads(json.dumps(self.value.__geo_interface__, cls=ESValueEncoder))

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
        return json.loads(json.dumps(coords, cls=ESValueEncoder))

    @property
    def coorInv(self):
        '''list (@property) : vSimple inverse coordinates [vSimple[1], vSimple[0]]'''
        return [self.vSimple()[1], self.vSimple()[0]]

    def from_bytes(self, byt, mini=False):
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
        return None

    def link(self, other):
        '''
        return the link (string) between self.value and other.value :
        - equals     : if self and other are the same
        - disjoint   : if self's shape and other's shape are disjoint
        - within     : if other's shape contains self's shape
        - contains   : if self's shape contains other's shape
        - intersects : in the others cases'''
        if self.isEqual(other, name=False) :        return 'equals'
        if self.value.equals(other.value) :         return 'equals'
        if self.value.contains(other.value) :       return 'contains'
        if self.value.within(other.value) :         return 'within'
        if self.value.disjoint(other.value) :       return 'disjoint'
        if self.value.intersects(other.value) :     return 'intersects'


    @staticmethod
    def nullValue() : return LocationValue._gshape(ES.nullCoor)

    def to_bytes(self, mini=False):
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
        if string :
            return json.dumps([self.value.centroid.x, self.value.centroid.y], cls=ESValueEncoder)
        return [self.value.centroid.x, self.value.centroid.y]

    def vPointInv(self, string=False):
        ''' return point (property) inversed coordinates in a string format or
        in a list format [y, x]'''
        if string :
            return json.dumps([self.vSimple()[1], self.vSimple()[0]], cls=ESValueEncoder)
        return [self.vSimple()[1], self.vSimple()[0]]

    def vPointX(self) :
        ''' return point (property) coordinates x '''
        return self.vSimple()[0]

    def vPointY(self) :
        ''' return point (property) coordinates y '''
        return self.vSimple()[1]

    def _jsonValue(self, **kwargs):
        ''' return geoJson coordinates'''
        if 'geojson' in kwargs and kwargs['geojson'] : return self.__geo_interface__
        return self.coords

    def _init(self, val=ES.nullCoor, className=None):
        ''' LocationValue creation  (value and name)'''
        geom = (shapely.geometry.multipoint.MultiPoint, shapely.geometry.point.Point,
                shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon)
        if isinstance(val, geom):
            self.value = val
            return
        if isinstance(val, LocationValue):
            self.value = val.value
            self.name = val.name
            return
        if isinstance(val, dict): self.name, val = list(val.items())[0]
        shap = self._gshape(val)
        if shap is None:
            if isinstance(val, str) and self.name == ES.nullName: self.name = val
        else: self.value = shap

    @staticmethod
    def _gshape(coord):
        ''' transform a GeoJSON coordinates (list) into a shapely geometry'''
        if type(coord) == list:  coor = json.dumps(coord, cls=ESValueEncoder)
        elif type(coord) == str: coor = coord
        else: coor = coord.__copy__()
        for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
            try:
                return shapely.geometry.shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coor + '}'))
            except: pass
        return None

class PropertyValue(ESValue):              # !!! début ESValue
#%% prp
    """
    This class represents the Property of an Observation.

    *Attributes (for @property see methods)* :

    - **value** : dict
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Simple` (property type)
    - `Box`  (set of property type)

    *getters*

    - `vSimple`

    *functions*

    - `link`

    *exports - imports*

    - `from_bytes`
    - `to_bytes`

    """
    valName     = ES.prp_valName

    @classmethod
    def Simple(cls, prp, name='simple', prp_dict=False):
        '''PropertyValue built with a value (property type) '''
        return cls(val = {ES.prp_type: prp}, name=name, prp_dict=prp_dict)

    @classmethod
    def Box(cls, prp, name='box', prp_dict=False):
        '''PropertyValue built with a value (property type) '''
        return cls(val = {ES.prp_type: prp}, name=name, prp_dict=prp_dict)

    def __init__(self, val=ES.nullPrp, name=ES.nullName, prp_dict=False):
        '''Several PropertyValue creation modes :

        - PropertyValue({name : value}) where value is a property dict or json string
        - PropertyValue(js) where js is a json string
        - PropertyValue(name) where name is a string
        - PropertyValue(prpval) where prpval is a PropertyValue object (copy)

        prp_dict : boolean(default False) - if True type property has to be in the type dictionary
        '''
        ESValue.__init__(self, val, name)
        if not ES.prp_type in self.value: raise ESValueError("type property not defined")
        if isinstance(self.value[ES.prp_type], list):
            self.EStype = 24
        else:
            if prp_dict and not self.value[ES.prp_type] in ES.prop:
                raise ESValueError("property not present in standard dictionnary")
            if self.value == PropertyValue.nullValue(): self.EStype = 0
            elif len(self.value) == 0: self.EStype = 0
            elif len(self.value) == 1: self.EStype = 22
            elif len(self.value) == 2 and ES.prp_unit in self.value: self.EStype = 22
            else: self.EStype = 23
            if prp_dict : self.value[ES.prp_unit] = ES.prop[self.value[ES.prp_type]][5]
        if self.name != ES.nullName: self.EStype += 100


    def __lt__(self, other):
        """lower if string simple value + name is lower"""
        return self.simple + self.name < other.simple + other.name

    def from_bytes(self, byt, mini):
        if mini: 
            self.value[ES.prp_type]   = ES.invProp[struct.unpack('<B', byt[0:1])[0]]
            return 1
        bytl = byt[0:6] + b'\x00' +byt[6:9] + b'\x00' + byt[9:10]
        prp = struct.unpack('<BBBLLB', bytl)
        #for i in [3,4,5]:
        self.value[ES.prp_type]       = ES.invProp[prp[0]]
        self.value[ES.prp_unit]       = ES.prop[ES.invProp[prp[0]]][5]
        self.value[ES.prp_sampling]   = ES.invSampling[prp[1]]
        self.value[ES.prp_appli]      = ES.invApplication[prp[2]]
        self.value[ES.prp_period]     = prp[3]
        self.value[ES.prp_interval]   = prp[4]
        self.value[ES.prp_uncertain]  = prp[5] // 2
        return 10

    def link(self, other):
        '''
        return the link (string) between self.value and other.value :
        - equals     : if self and other are the same
        - disjoint   : if the self's key/val are all different from other's key/val
        - within     : if all self's key/val are included in other's key/val
        - contains   : if all other's key/val are included in self's key/val
        - intersects : in the others cases'''
        if self.isEqual(other, name=False) : return 'equals'
        sprp =self._setprp(self.value[ES.prp_type])
        oprp =self._setprp(other.value[ES.prp_type])
        if oprp == sprp:
            union = other.value | self.value
            union2 = self.value | other.value
            if union == self.value and union2 == self.value:   return 'within'
            if union == other.value and union2 == other.value: return 'contains'
            if union == union2:                                return 'disjoint'
            return 'intersects'
        if sprp == sprp | oprp: return 'contains'
        if oprp == sprp | oprp: return 'within'
        if oprp & sprp == set(): return 'disjoint'
        else: return 'intersects'
        return 'undefined'

    @staticmethod
    def _setprp(val):
        if isinstance(val, list): return set(val)
        return {val}

    @staticmethod
    def nullValue() : return {ES.prp_type: ES.nullDict, ES.prp_unit: ES.prop[ES.nullDict][5]}

    def vSimple(self, string=False):
        ''' return simple value (type for the property) in a string format or in a object format'''
        simple = ES.nullDict
        if ES.prp_type in self.value : simple = self.value[ES.prp_type]
        if string : return json.dumps(simple, cls=ESValueEncoder)
        return simple

    def to_bytes(self, mini):
        if mini: return struct.pack('<B', ES.prop[self.simple][0])
        if ES.prp_sampling in self.value : sampling = self.value[ES.prp_sampling]
        else : sampling = ES.nullDict
        if ES.prp_appli in self.value    : appli    = self.value[ES.prp_appli]
        else : appli    = ES.nullDict
        if ES.prp_period in self.value   : period   = self.value[ES.prp_period]
        #else : period   = ES.nullVal
        else : period   = ES.nullInt
        if ES.prp_interval in self.value : interval = self.value[ES.prp_interval]
        else : interval = ES.nullInt
        #else : interval = ES.nullVal
        if ES.prp_uncertain in self.value: uncertain= self.value[ES.prp_uncertain]
        else : uncertain = ES.nullInt
        #else : uncertain = ES.nullVal
        byt = struct.pack('<BBBLLB', ES.prop[self.simple][0],
                           ES.sampling[sampling],
                           ES.application[appli],
                           period, interval, uncertain * 2 )
        return byt[0:6] +byt[7:10] + byt[11:12]

    def _jsonValue(self, **kwargs):
        #return self._jsonDict(False)
        option = {'encoded' : False} | kwargs
        li = {}
        for k, v in self.value.items() :
            if   k in [ES.prp_type, ES.prp_unit, ES.prp_sampling, ES.prp_appli, ES.prp_EMFId] :
                if v != ES.nullDict: li[k] = v
            elif k in [ES.prp_period, ES.prp_interval, ES.prp_uncertain] :
                if v != ES.nullInt : li[k] = v
            else : li[k] = v
        if option['encoded']: return json.dumps(li, ensure_ascii=False, cls=ESValueEncoder)
        return li

    def _init(self, val={}, className=None):
        if isinstance(val, str) :
            try:  val = json.loads(val)
            except:
                self.name = val
                return
        if isinstance(val, dict):
            if len(val) > 0 and isinstance(val[list(val.keys())[0]], dict):
                                            self.name = list(val.keys())[0]
                                            self.value |= val[list(val.keys())[0]]
            else:                           self.value |= val
        elif isinstance(val, PropertyValue) :
            self.value = val.value
            self.name  = val.name
        else: raise ESValueError('type data not compatible with PropertyValue')
        return
        '''elif isinstance(val, str) :
            try:
                dic = json.loads(val)
                if isinstance(dic, dict):   self.value |= dic
                else:                       self.name = val
            except:                         self.name = val'''

class NamedValue (ESValue):               # !!! début ResValue
#%% res
    '''
    This class represent the Json objects.

    *Attributes (for @property see methods)* :

    - **value** : any json object
    - **name** : String

    The methods defined in this class are :

    *getters*

    - `vSimple`

    *exports - imports*

    - `from_bytes`
    - `to_bytes`

    '''
    valName     = ES.res_valName

    def __init__(self, val = ES.nullVal, name=ES.nullName):
        '''
        Several NamedValue creation modes :

        - NamedValue({name : value})
        - NamedValue(value)
        - NamedValue(namedval)

        where 'namedval' is a NamedValue(copy), 'value' is a json object and 'name' is a string.
        '''
        ESValue.__init__(self, val, name)
        if self.value != self.nullValue(): self.EStype = 32
        if self.name != ES.nullName: self.EStype += 100

    def from_bytes(self, byt, forma = ES.nullDict):
        formaPrp = ES.prop[forma][1]
        leng = ES.prop[forma][2]
        dexp = ES.prop[forma][3]
        bexp = ES.prop[forma][4]        
        self.__init__(val=struct.unpack('<'+ formaPrp, byt[0:leng])[0] * 10**dexp * 2**bexp)
        return leng

    @staticmethod
    def nullValue() : return ES.nullVal

    def to_bytes(self, forma = ES.nullDict):
        formaPrp = ES.prop[forma][1]
        dexp = ES.prop[forma][3]
        bexp = ES.prop[forma][4]
        val = self.value * 10**-dexp * 2**-bexp
        return struct.pack('<' + formaPrp, val)
    
    def vSimple(self, string=False) :
        '''float value'''
        if string : return str(self.to_float())
        return self.to_float()

    def _init(self, val=None, className=None):
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
        '''return a json/bson dict for the value '''
        if type(self.value) in [int, str, float, bool, list, dict, datetime.datetime, type(None), bytes]:
            return self.value
        '''if option['encode_format'] == 'bson':
            try : return self.value.__to_bytes__(encoded=False)
            except : raise ESValueError("impossible to apply __to_bytes__ method to object " + str(type(self.value)))
        '''
        '''try: return self.value.to_json(encoded=False, encode_format='json',
                                    json_info=False, json_res_index=True, json_param=True)
        except : return object.__repr__(self.value)'''

class ExternValue (ESValue):               # !!! début ResValue
#%% ext
    '''
    This class represent named value when value is an object.

    *Attributes (for @property see methods)* :

    - **value** : any kind of object
    - **name** : String

    The methods defined in this class are :

    *getters*

    - `vSimple`


    '''
    valName     = ES.res_valName

    def __init__(self, val = ES.nullVal, name=ES.nullName, className=ES.nullName):
        '''
        Several ExternValue creation modes :

        - ExternValue(className: {name: value})
        - ExternValue({className:value})
        - ExternValue({className:resval})

        where 'resval' is an ExternValue(copy), 'value' is an Object, 'name' is a string and
        'className' is the class name of the object.
        '''
        namedvalue = val
        if className == ES.nullName: className = ESValue.valClassName(val)
        if   isinstance(val, dict) and len(val) == 1 and list(val.keys())[0] in ES.typeName.keys(): 
            namedvalue = list(val.values())[0]

        ESValue.__init__(self, namedvalue, name, className)
        self.EStype = ES.ntypevalue[ES.valname[ESValue.valClassName(val)]]
        #if self.value != self.nullValue(): self.EStype = 32
        if self.name != ES.nullName: self.EStype += 100

    @staticmethod
    def nullValue() : return ES.nullVal

    def vSimple(self, string=False) :
        '''float value'''
        if string : return str(self.to_float())
        return self.to_float()

    def _init(self, val=None, className=None):
        if isinstance(val, ExternValue):
            self.name = val.name
            self.value = val.value
        else:
            if type(val) == dict and len(val) == 1:
                self.name, val = list(val.items())[0]
            #self.value = _classval()[ESValue.valClassName(val)](val)
            self.value = _classval()[className](val)

    def _jsonValue(self, **option) :
        '''return a json/bson dict for the value '''
        if type(self.value) in [int, str, float, bool, list, dict, datetime.datetime, type(None), bytes]:
            return self.value
        '''if option['encode_format'] == 'bson':
            try : return self.value.__to_bytes__(encoded=False)
            except : raise ESValueError("impossible to apply __to_bytes__ method to object " + str(type(self.value)))
        '''
        try: return self.value.to_json(encoded=False, encode_format='json',
                                    json_info=False, json_res_index=True, json_param=True)
        except : return object.__repr__(self.value)


class ESValueError(Exception):
#%% ES except
    ''' ESValue Exception'''
