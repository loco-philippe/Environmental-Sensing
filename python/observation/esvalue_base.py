# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

The `observation.esvalue_base` is a module dedicated to structured data (such as dates,
location or measurable properties) and groups common properties and concepts.

ESValue is build around two attributes :

- 'name' which is a simple String
- 'value' which corresponds to a more or less complex object :

    - DatationValue : value is a TimeSlot Object which represent a set of time intervals
    - LocationValue : value is a Shapely Geometry which represent a set of polygons
    - PropertyValue : value is a simple dictionary which specifies all the characteristics of a property
    - NamedValue    : value can be any simple object
    - ExternValue   : value can be any other object

<img src="https://loco-philippe.github.io/ES/ESValue_class.png" width="800">

This module groups the classes of the objects used in the `observation.esobservation` module :

- `DatationValue`,
- `LocationValue`,
- `PropertyValue`,
- `NamedValue`
- `ExternValue`

and the parent class :

- `ESValue`

Documentation is available in other pages :
    
- The concepts of 'ES value' are describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/ESValue).
- The non-regression tests are at 
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_esvalue.py)
- Examples are 
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples)
- The Json Standard for ESValue is define 
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/ESJSON-Standard.pdf)



"""
import json
import re
import datetime
from json import JSONDecodeError
import cbor2
from copy import copy

from esconstante import ES, _classval
from timeslot import TimeInterval

ListESValue = ['LocationValue', 'DatationValue',
               'PropertyValue', 'NamedValue', 'ExternValue']
ListESValueSlot = ListESValue + ['TimeSlot']


class ESValueEncoder(json.JSONEncoder):
    """add a new json encoder for ESValue"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        option = {'encoded': False, 'encode_format': 'json'}
        try:
            return o.json(**option)
        except:
            try:
                return o.__to_json__()
            except:
                return json.JSONEncoder.default(self, o)


class ESValue:
    """
    This class is the parent class for each kind of values
     (`DatationValue`, `LocationValue`, `PropertyValue`, `NamedValue`, `ExternValue`)

    *Attributes* :

    - **name**  : name  of `ESValue.ESValue` objects
    - **value** : value of `ESValue.ESValue` objects
    - `ESValue.bounds` (@property) : boundary  of `ESValue.ESValue` objects
    - `ESValue.simple` (@property) : simplified value of `ESValue.ESValue` objects

    The methods defined in this class are :

    **binary predicates**

    - `ESValue.contains`
    - `ESValue.equals`
    - `ESValue.intersects`
    - `ESValue.within`
    - `ESValue.disjoint`
    - `ESValue.isEqual`
    - `ESValue.isNotNull`
    - `ESValue.isName`

    **other methods**

    - `ESValue.boundingBox` (@classmethod)
    - `ESValue.from_obj` (@classmethod)
    - `ESValue.boxUnion`
    - `ESValue.getValue`
    - `ESValue.getName`
    - `ESValue.json`
    - `ESValue.setName`
    - `ESValue.setValue`
    - `ESValue.simple`
    - `ESValue.to_float`
    - `ESValue.to_obj`
    - `ESValue.valClassName`
    - `ESValue.vName`
    - `ESValue.vSimple`
    """
# %% constructor
    @staticmethod
    # def from_obj(bs, classname=ES.nam_clsName):
    def from_obj(bs, classname=None, simple=True):
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
        if classname:
            simple = False
        classn, name, val = ESValue._decodevalue(bs)
        if classname == ES.ext_clsName and classn:
            val = _classval()[classn](val)
        if val.__class__.__name__ in ES.ESclassName:
            return val
        if not simple and classn in [ES.ili_clsName, ES.iin_clsName, ES.obs_clsName]:
            classn = ES.ext_clsName
        if (not classn or classn == ES.ES_clsName) and classname != ES.ES_clsName:
            classn = classname
        if (not classn or classn == ES.ES_clsName) and classname == ES.ES_clsName:
            classn =  ES.nam_clsName
        if not simple and not classn:
            classn = ESValue.valClassName(val)
        if classn in ES.ESvalName:
            return _classval()[classn](val, name)
        if classn in ES.valname:
            return _classval()[classn].obj(val)
        # return ESValue._castsimple(val)
        return ESValue._castsimple(bs)

    def __init__(self, val=None, name=None, className=None):
        '''Initialize 'name' and 'value' attribute'''
        self.name = ES.nullName
        self.value = self.nullValue()

# %% special
    def __eq__(self, other):
        '''equal if value and name are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and \
            self.value == other.value and self.name == other.name

    def __lt__(self, other):
        '''lower if vSimple is lower. If vSimple are equal, self is lower if name is lower'''
        if self.__class__.__name__ != other.__class__.__name__:
            return hash(self) < hash(other)
        simps = self.vSimple()
        simpo = other.vSimple()
        if simps == simpo:
            return self.name < other.name
        return simps < simpo

    def __str__(self):
        '''return json string format'''
        js = self.json(encoded=True)
        #js = self.json(encoded=False)
        # if not isinstance(js, str): return str(js)
        return js

    def __repr__(self):
        '''return classname and type of value (n, v, nv)'''
        if not self.isNotNull():
            return self.__class__.__name__ + '[]'
        if not self.name:
            return self.__class__.__name__ + '[v]'
        if self.value == self.nullValue():
            return self.__class__.__name__ + '[n]'
        else:
            return self.__class__.__name__ + '[nv]'

    def __copy__(self):
        '''return a new object with the same attributes'''
        return self.__class__(self)

    def __hash__(self):
        '''return hash(name) + hash(value)'''
        return hash(self.name) + hash(str(self.value))

# %% binary predicates
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

    def isNotNull(self, nullvalue=None):
        '''return boolean. True if the 'ESValue' is not a NullValue'''
        return self != self.__class__(nullvalue)

    def isEqual(self, other, name=True, value=True):
        '''Compare two `ESValue`

        *Parameters*

        - **other** : ESValue
        - **name** : boolean (default True) - Include Name in comparison
        - **value** : boolean (default True) - Include Value in comparison

        *Returns*

        - **boolean** : Result of the comparison '''
        equalName = self.name == other.name
        nullName = self.name == ES.nullName
        #ListESValue = [LocationValue, DatationValue, PropertyValue, NamedValue, ExternValue]
        # if   self.__class__ in ListESValue  :
        if self.__class__.__name__ in ListESValue:
            nullValue = self.value == self.__class__.nullValue()
            equalValue = self.value == other.value
        else:
            equalValue = False
        return (name and value and equalName and equalValue) or \
            (name and not value and equalName and not nullName) or \
            (not name and value and equalValue and not nullValue)

    def isName(self, pattern):
        '''check if a pattern (regex) is presenty in the ESValue name.'''
        return re.search(pattern, self.getName()) is not None


# %% methods

    @staticmethod
    def boundingBox(listValue):
        ''' return a `ESValue` object with bounds values'''
        box = copy(listValue[0])
        for val in listValue:
            box = box.boxUnion(val)
        return box

    @property
    def bounds(self):
        '''list or tuple (@property)
        - DatationValue : boundingBox (tmin, tmax)
        - LocationValue : boundingBox (minx, miny, maxx, maxy)
        - PropertyValue : boundingBox (list of type property)
        - Other ESValue : () '''
        try:
            if self.__class__.__name__ == 'PropertyValue':
                return tuple(self.value[ES.prp_type])
            return self.value.bounds
        except:
            return ()

    def boxUnion(self, other, name=''):
        '''return a new `ESValue` with :
        - name : parameters
        - value : union between box(self) and box(other)  '''
        if self.__class__.__name__ == 'PropertyValue':
            return self.__class__.Box(sorted(list(self._setprp(self.value[ES.prp_type]) |
                                                  self._setprp(other.value[ES.prp_type]))),
                                      name=name)
        sbox = self.Box(self. bounds).value
        obox = other.Box(other.bounds).value
        if   sbox == obox:
            ubox = sbox
        elif sbox.__class__.__name__ == 'Polygon' and sbox.covers(obox):
            ubox = sbox
        elif sbox.__class__.__name__ == 'Polygon' and obox.covers(sbox):
            ubox = obox
        else:
            ubox = sbox.union(obox)
        boxunion = self.__class__(val=self.Box(ubox.bounds))
        if name != '':
            boxunion.name = name
        return boxunion

    def getValue(self):
        ''' return self.value object '''
        return self.value

    def getName(self):
        ''' return self.name object '''
        return self.name

    def json(self, **kwargs):
        '''
        Export in json/cbor format (string or dict).

        *Parameters*

        - **untyped** : boolean (default False) - include dtype in the json if True
        - **encoded** : boolean (default True) - choice for return format (string/bytes if True, dict else)
        - **encode_format**    : string (default 'json')- choice for return format (json, cbor)
        - **simpleval** : boolean (default False) - if True, only value is included

        *Returns* :  string or dict '''
        return self.to_obj(**kwargs)

    def setName(self, nam):
        '''
        Set the Name of the `ESValue`

        *Parameters*

        - **nam** : string - value to set

        *Returns* : None'''
        self.name = nam

    def setValue(self, val):
        '''
        Set a new Value

        *Parameters*

        - **val** : compatible ESValue - New ESValue

        *Returns* : None'''
        ESval = self.__class__(val)
        self.value = ESval.value

    @property
    def simple(self):
        '''return vSimple object (@property) '''
        return self.vSimple(string=False)

    def to_float(self, **kwargs):
        '''return a converted float value or nan'''
        if self.value is None:
            return float('nan')
        if isinstance(self.value, str):
            if self.value == ES.nullAtt:
                return float('nan')
            try:
                return float(self.value)
            except:
                return float('nan')
        return float(self.value)

    def to_obj(self, **kwargs):
        '''
        Export in json/cbor format (string or dict).

        *Parameters*

        - **untyped** : boolean (default False) - include dtype in the json if True
        - **encoded** : boolean (default True) - choice for return format (string/bytes if True, dict else)
        - **encode_format** : string (default 'json')- choice for return format (json, cbor)
        - **simpleval** : boolean (default False)- if True only value

        *Returns* :  string or dict '''
        option = {'untyped': False, 'encoded': True, 'encode_format': 'json',
                  'simpleval': False} | kwargs
        option2 = option | {'encoded': False}
        if option['simpleval']:
            js = self._jsonValue(**option2)
        else:
            if not self.name or self.name == ES.nullName:
                js = self._jsonValue(**option2)
            elif self.value is None or self.value == self.__class__.nullValue():
                js = self.name
            else:
                js = {self.name: self._jsonValue(**option2)}
        if option['untyped']:
            js = {ES.valname[self.__class__.__name__]: js}
        if option['encoded'] and option['encode_format'] != 'cbor':
            return json.dumps(js, cls=ESValueEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor':
            return cbor2.dumps(js)
        return js

    def vSimple(self, string=False, **kwargs):
        ''' Return the vSimple of the `ESValue` (string or object) '''
        return self.__class__.vSimple(self, string=string)

    @staticmethod
    def ljson(listval, **kwargs):
        '''
        Export a list in json/cbor format (string or dict).

        *Parameters*

        - **untyped** : boolean (default False) - include dtype in the json if True
        - **encoded** : boolean (default True) - choice for return format (string/bytes if True, dict else)
        - **encode_format**    : string (default 'json')- choice for return format (json, cbor)
        - **simpleval** : boolean (default False) - if True, only value is included

        *Returns* :  list of string or dict '''
        return [val.to_obj(**kwargs) for val in listval]

    @staticmethod
    def valClassName(val):
        '''return the calculate ESValue Class of val (string)'''
        if val is None:
            return ES.nam_clsName
        # if isinstance(val,(DatationValue, LocationValue, PropertyValue, NamedValue,
        #                   ExternValue, TimeSlot)):
        if val.__class__.__name__ in ListESValueSlot:
            return val.__class__.__name__
        if val.__class__.__name__ in [ES.obs_clsName, ES.ili_clsName]:
            return ES.ext_clsName
        if val.__class__.__name__ == ES.tim_clsName:
            return ES.dat_clsName
        if isinstance(val, str):
            try:
                dic = json.loads(val)
            except:
                dic = val
        else:
            dic = val
        if isinstance(dic, (int, float, bool, list, str, tuple)):
            return ES.nam_clsName
        if isinstance(dic, dict) and len(dic) != 1:
            return ES.prp_clsName
        if isinstance(dic, dict) and len(dic) == 1 and list(dic.keys())[0] in ES.typeName.keys():
            return ES.typeName[list(dic.keys())[0]]
        if isinstance(dic, dict) and len(dic) == 1 and not list(dic.keys())[0] in ES.typeName.keys():
            if isinstance(list(dic.values())[0], (int, float, bool, list, str, dict)):
                return ES.nam_clsName
            return ESValue.valClassName(list(dic.values())[0])
        return ES.nam_clsName

    def vName(self, default=ES.nullName, **kwargs):
        '''
        Return the Name of the `ESValue`

        *Parameters*

        - **default** : string (default nullName) - Return value if nullName

        *Returns*

        - **str** : Name of the ESValue
        '''
        if self.name == ES.nullName:
            return default
        return self.name

    @staticmethod
    def _castsimple(val):
        ''' convert val in hashable val'''
        typeval = val.__class__.__name__
        if typeval == 'list':
            return ESValue._tupled(val)
        # if typeval == 'list': return tuple(val)
        # if typeval == 'dict' and len(val) <= 1: return val
        # if typeval == 'dict' and len(val) > 1: return str(val)
        # if typeval == 'dict': return str(val)
        if typeval == 'dict':
            return json.dumps(val, cls=ESValueEncoder)
        if typeval == 'str':
            try:
                return TimeInterval._dattz(datetime.datetime.fromisoformat(val))
            except ValueError:
                return val
        return val

    @staticmethod
    def uncastsimple(val):
        ''' convert val in hashable val'''
        typeval = val.__class__.__name__
        if typeval == 'tuple':
            return ESValue._listed(val)
        # if typeval == 'tuple': return list(val)
        if typeval == 'str' and len(val) > 0 and val[0] == '{':
            return json.loads(val)
        if typeval == 'datetime':
            return val.isoformat()
        return val

    @staticmethod
    def _tupled(idx):
        '''transform a list of list in a tuple of tuple'''
        return tuple([val if not isinstance(val, list) else ESValue._tupled(val) for val in idx])

    @staticmethod
    def _listed(idx):
        '''transform a tuple of tuple in a list of list'''
        return [val if not isinstance(val, tuple) else ESValue._listed(val) for val in idx]

    @staticmethod
    def _decodeclass(val):
        ''' return ESclassname of val'''
        clss = val.__class__.__name__
        if clss in ['bool', 'int', 'float']:
            return 'NamedValue'
        if clss == 'dict':
            return 'PropertyValue'
        if clss == 'str' and not (val.lstrip() and val.lstrip()[0] in ('{', '[', '(')):
            return 'NamedValue'
        try:
            from esvalue import DatationValue
            v = DatationValue(val)
            return 'DatationValue'
        except:
            try:
                from esvalue import LocationValue
                v = LocationValue(val)
                return 'LocationValue'
            except:
                try:
                    from esvalue import NamedValue
                    v = NamedValue(val)
                    return 'NamedValue'
                except:
                    return clss

    @staticmethod
    def _decodevalue(bs):
        ''' return tuple (class, name, val). If single value, it's val'''
        bs2 = None
        name = None
        classname = None
        val = None
        if isinstance(bs, bytes):
            bs = cbor2.loads(bs)
        if isinstance(bs, str) and bs.lstrip() and bs.lstrip()[0] in ('{', '[', '('):
            try:
                bs = json.loads(bs)
            except JSONDecodeError:
                pass
        if not isinstance(bs, dict):
            val = bs
        elif isinstance(bs, dict) and len(bs) != 1:
            val = bs
        elif list(bs.keys())[0] in ES.typeName:
            classname = ES.typeName[list(bs.keys())[0]]
            bs2 = bs[list(bs.keys())[0]]
        else:
            bs2 = bs
        if bs2 is None:
            return (classname, None, val)
        if classname == ES.obs_clsName:
            return (classname, None, bs2)
        if not isinstance(bs2, dict):
            val = bs2
        elif isinstance(bs2, dict) and len(bs2) > 1:
            val = bs2
        else:
            name = str(list(bs2.keys())[0])
            val = list(bs2.values())[0]
        return (classname, name, val)


class ESValueError(Exception):
    # %% ES except
    ''' ESValue Exception'''
    pass
