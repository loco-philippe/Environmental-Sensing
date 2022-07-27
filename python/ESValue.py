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

The ESValue is a class dedicated to structured data (such as dates, location or
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
import json, geojson, shapely.geometry, re
import datetime
from json import JSONDecodeError 
from ESconstante import ES, _classval
from geopy import distance
from timeslot import TimeSlot
from openlocationcode import encode
import cbor2

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

    - `from_obj` (@classmethod)
    - `bounds`
    - `boxUnion`
    - `getValue`
    - `getName`
    - `json`
    - `setName`
    - `setValue`
    - `simple`
    - `to_float`
    - `vClassName`
    - `vName`
    - `vSimple`
    """
#%% constructor               
    @staticmethod
    def from_obj(bs, classname=ES.nam_clsName):
        '''Generate an ESValue Object from a bytes, json or dict object
        Several configurations for bs parameters (name and type are string) :
            - {name : value}
            - name
            - object
            - {type : {name: value}}
            - {type : name}
            - {type : value}

        *Parameters*

        - **bs** : bytes, string or dict data to convert

        *Returns* :  ESValue object '''        
        classn, name, val = ESValue._decodevalue(bs)
        if val.__class__.__name__ in ES.ESclassName: return val
        if not classn and val.__class__.__name__ == ES.ili_clsName: 
            classn = ES.ili_clsName
        if classn == ES.ili_clsName and (name or classname == ES.ext_clsName):
            return ExternValue(val, name, classn)
        if not classn: classn = classname
        if not classn and name: classn = ES.nam_clsName
        if classn in ES.ESvalName: 
            return _classval()[classn](val, name)
        if classn in ES.valname:   
            return _classval()[classn](val)
        return val 
    
    def __init__(self, val, name=None, className=None):
        '''Initialize 'name' and 'value' attribute'''
        self.name = ES.nullName
        self.value = self.nullValue()
        self.EStype = 0

#%% special
    def __eq__(self, other):
        '''equal if value and name are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and \
            self.value == other.value and self.name == other.name

    def __lt__(self, other):
        '''lower if value is lower. If values are equal, self is lower if name is lower'''
        if self.value == other.value : return self.name <  other.name
        return self.value < other.value

    def __str__(self):
        '''return json string format'''
        js = self.json(encoded=False)
        if not isinstance(js, str): return str(js)
        return js

    def __repr__(self):
        '''return classname and type of value (n, v, nv)'''
        if not self.isNotNull(): return self.__class__.__name__ + '[]'       
        if not self.name: return self.__class__.__name__ + '[v]'       
        if self.value == self.nullValue(): return self.__class__.__name__ + '[n]'       
        else: return self.__class__.__name__ + '[nv]'

    def __copy__(self):
        '''return a new object with the same attributes'''
        return self.__class__(self)

    def __hash__(self): 
        '''return hash(name) + hash(value)'''
        return hash(self.name) + hash(str(self.value))

#%% binary predicates
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

    def isEqual(self, other, name=True, value=True):
        '''Compare two `ESValue`

        *Parameters*

        - **other** : ESValue
        - **name** : boolean (default True) - Include Name in comparison
        - **value** : boolean (default True) - Include Value in comparison

        *Returns*

        - **boolean** : Result of the comparison '''
        equalName = self.name == other.name
        nullName  = self.name == ES.nullName
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


#%% methods
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
        return a new `ESValue` with :
            name : parameters
            value : union between box(self) and box(other)
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
                
    def getValue(self) :
        ''' return self.value object '''
        return self.value

    def getName(self) :
        ''' return self.name object '''
        return self.name

    def json(self, **kwargs):
        '''
        Export in json/cbor format (string or dict).

        *Parameters*

        - **untyped** : boolean (default False) - include dtype in the json if True
        - **encoded** : boolean (default True) - choice for return format (string/bytes if True, dict else)
        - **encode_format**    : string (default 'json')- choice for return format (json, cbor)

        *Returns* :  string or dict '''
        option = ES.mOption | kwargs
        option2 = option | {'encoded': False}
        if not self.name or self.name == ES.nullName :  
            js =  self._jsonValue(**option2)
        elif not self.value or self.value == self.__class__.nullValue() : 
            js =  self.name
        else :                                          
            js = {self.name : self._jsonValue(**option2)}
        if option['untyped']: js = {ES.valname[self.__class__.__name__]: js}
        if option['encoded'] and option['encode_format'] != 'cbor': return json.dumps(js, cls=ESValueEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': return cbor2.dumps(js)
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
        '''return vSimple object (@property) '''
        return self.vSimple(string=False)

    def to_float(self):
        '''return a converted float value or nan'''
        if self.value == None :         return float('nan')
        if type(self.value)==str:
            if self.value == ES.nullAtt:return float('nan')
            try:                        return float(self.value)
            except:                     return float('nan')
        return float(self.value)

    def vSimple(self, string=False):
        ''' Return the vSimple of the `ESValue` (string or object) '''
        return self.__class__.vSimple(self, string=string)

    @staticmethod
    def valClassName(val):
        '''return the calculate ESValue Class of val (string)'''
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

    def vName(self, default=ES.nullName):
        '''
        Return the Name of the `ESValue`

        *Parameters*

        - **default** : string (default nullName) - Return value if nullName

        *Returns*

        - **str** : Name of the ESValue
        '''
        if self.name == ES.nullName : return default
        return self.name

    @staticmethod
    def _decodevalue(bs):
        ''' return tuple (class, name, val). If single value, it's val'''
        bs2 =       None
        name =      None
        classname = None
        val =       None
        if isinstance(bs, bytes): bs = cbor2.loads(bs)
        if isinstance(bs, str) and bs.lstrip() and bs.lstrip()[0] in ('{', '[', '('): 
            try: bs = json.loads(bs)
            except JSONDecodeError: pass
        if not isinstance(bs, dict): val = bs
        elif isinstance(bs, dict) and len(bs) > 1: val = bs
        elif list(bs.keys())[0] in ES.typeName:
            classname = ES.typeName[list(bs.keys())[0]]
            bs2 = bs[list(bs.keys())[0]]
        else: bs2 = bs
        if bs2: 
            if not isinstance(bs2, dict): val=bs2
            elif isinstance(bs2, dict) and len(bs2) > 1: val = bs2
            else: 
                name = list(bs2.keys())[0]
                val  = bs2[name]
        return (classname, name, val)
    
class DatationValue(ESValue):   # !!! début ESValue
#%% dat
    """
    This class represent Time (instant, interval or set of intervals).

    *Attributes (for @property see methods)* :

    - **value** : TimeSlot object (instant, interval or list of interval)
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Simple`  (instant)
    - `Box`     (interval)
    - `from_obj`(see  `ESValue.from_obj`)
        

    *getters*

    - `getInstant`
    - `getInterval`
    - `vSimple`
    - `vInterval`
    - `link`
    
    *conversion (static method)*

    - `link`
    
    """
    @classmethod
    def Simple(cls, instant):
        '''DatationValue built with a time value (instant) '''
        return cls(slot=TimeSlot(instant), name='instant')

    @classmethod
    def Box(cls, bounds):
        '''DatationValue built from a tuple or list box coordinates (tmin, tmax)'''
        if isinstance(bounds, cls): bound = bounds.bounds
        else : bound = bounds
        return cls(val=TimeSlot(bound), name='interval')

    @classmethod 
    def from_obj(cls, bs): 
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.dat_clsName)
    
    def __init__(self, val=ES.nullDate, name=ES.nullName):
        '''
        DatationValue constructor.

        *Parameters*

        - **val** :  compatible Timeslot Value (default nullDate)
        - **name** :  string (default nullName)
        '''
        ESValue.__init__(self, val, name)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
        elif val: 
            value = TimeSlot(val)
            if value: self.value = value 
            elif not value and not name: name = val
            elif not value and name: raise ESValueError('name and val inconsistent')
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName : 
            self.name = name
        if self.value == TimeSlot(ES.nullDate): self.EStype = 0
        else: self.EStype = ES.ntypevalue[self.value.stype]
        if self.name != ES.nullName: self.EStype += 100

    def getInstant(self) :
        '''return datetime if 'instant', none else'''
        if self.value.stype == 'instant': return self.value. slot[0][0]
        return None

    def getInterval(self) :
        '''return [datetime t1, datetime t2] if 'interval', none else'''
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
    def nullValue() : 
        ''' return nullDate value'''
        return TimeSlot(ES.nullDate)

    def vInterval(self, encoded=True, encode_format='json'):
        """return [t1, t2] with t1, t2 - Mini, maxi of the TimeSlot (timestamp or datetime).

        *Parameters*

        - **encode_format**    : string (default 'json')- choice for return format (json, cbor)

        *Returns*

        - **JSON with timestamp or list with datetime**
        """
        return self.value.Bounds.json(encoded=encoded, encode_format=encode_format)

    def vSimple(self, string=False) :
        """return a datetime : middle of the TimeSlot."""
        if string : return self.value.instant.isoformat()
        return self.value.instant

    def _jsonValue(self, **option):
        '''return a json/cbor/dict for the value (TimeSlot) '''
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

    - `Simple`   (point)
    - `Box`
    - `from_obj` (see  `ESValue.from_obj`)
    
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
    """
    @classmethod
    def Simple(cls, coord):
        '''return LocationValue built with tuple or list coordinates (x,y)'''
        return cls(shape=shapely.geometry.Point(*coord), name='point')

    @classmethod
    def Box(cls, bounds, ccw=True):
        '''return LocationValue built with tuple or list box coordinates (minx, miny, maxx, maxy)'''
        if isinstance(bounds, cls): bound = bounds.bounds
        else : bound = bounds
        return cls(val=shapely.geometry.box(*bound, ccw), name='box')

    @classmethod 
    def from_obj(cls, bs): 
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.loc_clsName)
    
    def __init__(self, val=ES.nullCoor, name=ES.nullName):
        '''
        LocationValue constructor.

        *Parameters*

        - **val** :  compatible shapely.geometry.Point (or Polygon) Value (default nullCoor)
        - **name** :  string (default nullName)
        '''        
        ESValue.__init__(self, val, name)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
        elif isinstance(val, (shapely.geometry.multipoint.MultiPoint, 
                              shapely.geometry.point.Point,
                              shapely.geometry.polygon.Polygon, 
                              shapely.geometry.multipolygon.MultiPolygon)):
            self.value = val
        elif val: 
            value = self._gshape(val)
            if value: self.value = value 
            elif not value and not name: name = val
            elif not value and name: raise ESValueError('name and val inconsistent')
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName : 
            self.name = name
        if self.value and self.value != self.nullValue():
            self.EStype = ES.ntypevalue[self.value.geom_type.lower()]
        if self.name != ES.nullName: self.EStype += 100

    def __lt__(self, other):
        ''' return minimal distance between a fixed point'''
        if self.coorInv==ES.nullCoor : return self.name <  other.name
        return distance.distance(self.coorInv, ES.distRef) <  \
                      distance.distance(other.coorInv, ES.distRef)
    @property
    def __geo_interface__(self):
        return json.loads(json.dumps(self.value.__geo_interface__, cls=ESValueEncoder))

    @property
    def coords(self):
        ''' return geoJson coordinates (list)'''
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

    def getPoint(self) :
        ''' return a list with point coordinates [x, y] if the shape is a point, else none'''
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
    def nullValue() :
        ''' return nullPosition value'''
        return LocationValue._gshape(ES.nullCoor)

    def vCodePlus(self) :
        ''' return CodePlus value (string) of the point property value'''
        return encode(self.vSimple(False)[1], self.vSimple(False)[0])

    def vSimple(self, string=False):
        ''' return simple value (centroid coordinates for the shape : 
            [x, y]) in a string format or in a object format'''
        if string :
            return json.dumps([self.value.centroid.x, self.value.centroid.y], cls=ESValueEncoder)
        return [self.value.centroid.x, self.value.centroid.y]

    def vPointInv(self, string=False):
        ''' return point (property) with inversed vSimple coordinates in a string format or
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

    - `Simple`   (property type)
    - `Box`      (set of property type)
    - `from_obj` (see  `ESValue.from_obj`)
    
    *getters*

    - `vSimple`

    *functions*

    - `link`
    """
    @classmethod
    def Simple(cls, prp, name='simple', prp_dict=False):
        '''PropertyValue built with a value (property type) '''
        return cls(val = {ES.prp_type: prp}, name=name, prp_dict=prp_dict)

    @classmethod
    def Box(cls, prp, name='box', prp_dict=False):
        '''PropertyValue built with a value (property type) '''
        return cls(val = {ES.prp_type: prp}, name=name, prp_dict=prp_dict)

    @classmethod 
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_json(bs, ES.prp_clsName)
    
    def __init__(self, val=ES.nullPrp, name=ES.nullName, prp_dict=False):
        '''
        PropertyValue constructor.

        *Parameters*

        - **val** :  property dict or json string (default nullPrp)
        - **name** :  string (default nullName)
        - **prp_dict** : boolean(default False) - if True type property has to be in the type dictionary
        '''
        ESValue.__init__(self, val, name)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
        elif isinstance(val, dict):
            if len(val) > 0 and isinstance(list(val.values())[0], dict):
                    self.name = list(val.keys())[0]
                    self.value |= val[list(val.keys())[0]]
            else:   self.value |= val
        elif isinstance(val, str): name = val
        else: raise ESValueError('type data not compatible with PropertyValue')
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName : 
            self.name = name
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
    def nullValue() : 
        ''' return nullPrp value'''
        return {ES.prp_type: ES.nullDict, ES.prp_unit: ES.prop[ES.nullDict][5]}

    def vSimple(self, string=False):
        ''' return simple value (type for the property) in a string format or in a object format'''
        simple = ES.nullDict
        if ES.prp_type in self.value : simple = self.value[ES.prp_type]
        if string : return json.dumps(simple, cls=ESValueEncoder)
        return simple

    def _jsonValue(self, **kwargs):
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

    @staticmethod
    def _setprp(val):
        if isinstance(val, list): return set(val)
        return {val}


class NamedValue (ESValue):               # !!! début ResValue
#%% res
    '''This class represent a simple value with an associated string.

    *Attributes (for @property see methods)* :

    - **value** : any json object
    - **name** : String

    The methods defined in this class are :

    *constructor*

    - `from_obj` (see  `ESValue.from_obj`)
    
    *getters*

    - `vSimple`
    '''
    @classmethod 
    def from_obj(cls, bs): 
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.nam_clsName)
    
    def __init__(self, val = ES.nullVal, name=ES.nullName):
        '''
        NamedValue constructor.

        *Parameters*

        - **val** :  any simple object (default nullVal)
        - **name** : string (default nullName)
        '''
        ESValue.__init__(self, val, name)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
        elif isinstance(val, (int, str, float, bool, tuple, datetime.datetime, type(None), bytes)) :
            self.value = val
        elif isinstance(val, list) :
            self.value = tuple(val)
        elif isinstance(val, dict) :
            self.value = json.dumps(val)
        else: 
            self.value = val
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName : 
            self.name = name
        if self.value != self.nullValue(): self.EStype = 32
        if self.name != ES.nullName: self.EStype += 100

    @staticmethod
    def nullValue() : 
        ''' return nullVal value'''
        return ES.nullVal

    def vSimple(self, string=False) :
        '''return float value in string or object format'''
        if string : return str(self.to_float())
        return self.to_float()

    def _jsonValue(self, **option) :
        '''return the value '''
        if type(self.value) in [int, str, float, bool, list, tuple, dict, datetime.datetime, type(None), bytes]:
            return self.value


class ExternValue (ESValue):               # !!! début ResValue
#%% ext
    '''This class represent a complex (extern) value with an associated string.

    *Attributes (for @property see methods)* :

    - **value** : any object
    - **name** : String

    The methods defined in this class are :

    *constructor*

    - `from_obj` (see  `ESValue.from_obj`)
    
    *getters*

    - `vSimple`
    '''
    @classmethod 
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.ext_clsName)
    
    def __init__(self, val = ES.nullVal, name=ES.nullName, className=ES.nullName):
        '''
        NamedValue constructor.

        *Parameters*

        - **val** :  any simple object (default nullVal)
        - **name** : string (default nullName)

        '''
        ESValue.__init__(self, val, name, className)
        if isinstance(val, ExternValue):
            self.name = val.name
            self.value = val.value
        else:
            if not className and val.__class__.__name__ == ES.ili_clsName: 
                className = ES.ili_clsName
            self.value = _classval()[className](val)
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName : 
            self.name = name
        self.EStype = ES.ntypevalue[ES.valname[ESValue.valClassName(val)]]
        if self.name != ES.nullName: self.EStype += 100

    @staticmethod
    def nullValue() : 
        ''' return nullVal value'''
        return ES.nullVal

    def vSimple(self, string=False) :
        '''return conversion from value to float'''
        if string : return str(self.to_float())
        return self.to_float()

    def _jsonValue(self, **option) :
        '''return a json object for the value '''
        if isinstance(self.value, (int, str, float, bool, list, tuple, dict, datetime.datetime, type(None), bytes)):
            return self.value
        if isinstance(self.value, (DatationValue, LocationValue, PropertyValue, NamedValue, ExternValue)):
            return self.value.json(encoded=False, encode_format='json')
        try: return self.value.to_json(encoded=False, encode_format='json',
                                    json_info=False, json_res_index=True, json_param=True)
        except : return object.__repr__(self.value)


class ESValueError(Exception):
#%% ES except
    ''' ESValue Exception'''


"""@classmethod
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
        else : return  [ValueClass(value)]"""
        
"""        def __to_bytes__(self, **option):
            js = self.json(encoded=False, encode_format='cbor')
            if option['encoded']: return bson.encode(js)
            return js

        @staticmethod
        def __from_bytes__(bs):
            if not isinstance(bs, (bytes, dict)): raise ESValueError("parameter is not dict or bytes")
            if isinstance(bs, bytes): dic = cbor2.loads(bs)
            else: dic = bs
            return dic"""
        
"""def _to_strBytes(self, simple=False, mini=False):
            '''not available'''
            bval = str.encode(self.name)
            if simple and mini : 
                #form='{:<'+str(ES.miniStr)+'}' 
                #return str.encode(form.format(self.name[0:ES.miniStr]))
                return str.encode(self.name[0:ES.miniStr].ljust(ES.miniStr))
            if simple and not mini : return bval
            return struct.pack('>B', len(bval)) + bval

        def _from_strBytes(self, byt, simple=False):
            '''not available'''
            if simple :
                siz = len(byt) - 1
                name = bytes.decode(byt).rstrip()          
            else :
                siz = struct.unpack('>B', byt[0:1])[0]
                name = bytes.decode(byt[1: siz + 1]).rstrip()
            self._init(name)
            return siz + 1"""
        
"""        def from_bytes(self, byt, mini=False):
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
            return 7"""
"""    def to_bytes(self, mini=False):
        '''
        Export in binary format.

        *Returns*

        - **bytes** : binary representation of the `DatationValue` (datetime)
        '''
        if mini: return struct.pack('<HBB', self.simple.year, self.simple.month,
                           self.simple.day)
        return struct.pack('<HBBBBB', self.simple.year, self.simple.month,
                           self.simple.day, self.simple.hour,
                           self.simple.minute, self.simple.second)"""
"""    def from_bytes(self, byt, mini=False):
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

    def to_bytes(self, mini=False):
        '''Export in binary format.

        *Returns*

        - **bytes** : binary representation of the `LocationValue` (point coordinates)
        '''
        return struct.pack('<ll',round(self.vSimple()[0]*10**7), round(self.vSimple()[1]*10**7))

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
    
    def from_bytes(self, byt, forma = ES.nullDict):
        formaPrp = ES.prop[forma][1]
        leng = ES.prop[forma][2]
        dexp = ES.prop[forma][3]
        bexp = ES.prop[forma][4]        
        self.__init__(val=struct.unpack('<'+ formaPrp, byt[0:leng])[0] * 10**dexp * 2**bexp)
        return leng
    
    def to_bytes(self, forma = ES.nullDict):
        formaPrp = ES.prop[forma][1]
        dexp = ES.prop[forma][3]
        bexp = ES.prop[forma][4]
        val = self.value * 10**-dexp * 2**-bexp
        return struct.pack('<' + formaPrp, val)
    
    def _init(self, val=None, className=None):
        '''if isinstance(val, dict) :
            self.name, val = list(val.items())[0]'''
        if   isinstance(val, (int, str, float, bool, tuple, datetime.datetime, type(None), bytes)) :
            self.value = val
        elif isinstance(val, list) :
            self.value = tuple(val)
        elif isinstance(val, dict) :
            self.value = json.dumps(val)
        else: 
            try:
                self.name = val.name
                self.value = val.value
            except:
                self.value = val

    def _init(self, val=None, className=None):
        if isinstance(val, ExternValue):
            self.name = val.name
            self.value = val.value
        else:
            if type(val) == dict and len(val) == 1:
                self.name, val = list(val.items())[0]
            #self.value = _classval()[ESValue.valClassName(val)](val)
            self.value = _classval()[className](val)

"""