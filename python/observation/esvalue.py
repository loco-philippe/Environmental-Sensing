# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

The `python.observation.esvalue` module contains the `python.observation.esvalue_base.ESValue` subclasses

ESValue is build around two attributes :

- 'name' which is a simple String
- 'value' which corresponds to a more or less complex object :

    - 'DatationValue' : value is a TimeSlot Object which represent a set of time intervals
    - 'LocationValue' : value is a Shapely Geometry which represent a set of polygons
    - 'PropertyValue' : value is a simple dictionary which specifies all the characteristics of a property
    - 'NamedValue'    : value can be any simple object
    - 'ExternValue'   : value can be any other object

<img src="https://loco-philippe.github.io/ES/ESValue_class.png" width="800">

This module groups the classes of the objects used in the `python.observation.esobservation` module :

- `DatationValue`,
- `LocationValue`,
- `PropertyValue`,
- `NamedValue`
- `ExternValue`

and the parent class :

- `python.observation.esvalue_base.ESValue`

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
import geojson
import shapely.geometry
import datetime
from geopy import distance
from copy import copy
from openlocationcode import openlocationcode

from observation.esconstante import ES, _classval
from observation.esvalue_base import ESValueEncoder, ESValue
from observation.timeslot import TimeSlot


class DatationValue(ESValue):   # !!! début ESValue
    # %% dat
    """
    This class represent Time (instant, interval or set of intervals).

    *Attributes (for @property see methods)* :

    - **value** : TimeSlot object (instant, interval or list of interval)
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `DatationValue.Simple`  (instant)
    - `DatationValue.Box`     (interval)
    - `DatationValue.from_obj`(see  `ESValue.from_obj`)


    *getters*

    - `DatationValue.getInstant`
    - `DatationValue.getInterval`
    - `DatationValue.vSimple`
    - `DatationValue.vInterval`
    - `DatationValue.link`    
    """
    @classmethod
    def Simple(cls, instant):
        '''DatationValue built with a time value (instant) '''
        return cls(slot=TimeSlot(instant), name='instant')

    @classmethod
    def Box(cls, bounds):
        '''DatationValue built from a tuple or list box coordinates (tmin, tmax)'''
        if isinstance(bounds, cls):
            bound = bounds.bounds
        else:
            bound = bounds
        return cls(val=TimeSlot(bound), name='interval')

    @classmethod
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.dat_clsName, simple=False)

    def __init__(self, val=ES.nullDate, name=ES.nullName):
        '''
        DatationValue constructor.

        *Parameters*

        - **val** :  compatible Timeslot Value (default nullDate)
        - **name** :  string (default nullName)
        '''
        ESValue.__init__(self)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
            return
        if not val is None:
            try:
                self.value = TimeSlot(val)
            except:
                if not name:
                    name = val
                else:
                    raise ESValueError('name and val inconsistent')
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName:
            self.name = name

    @staticmethod
    def boundingBox(listValue):
        ''' return a tuple (datmin, datmax) with bounds values'''
        return [min([val.value.slot[0].start for val in listValue]),
                max([val.value.slot[len(val.value) - 1].end for val in listValue])]
        # return (TimeSlot.form(self.slot[0].start), TimeSlot.form(self.slot[len(self) - 1].end))

    def getInstant(self):
        '''return datetime if 'instant', none else'''
        if self.value.stype == 'instant':
            return self.value. slot[0][0]
        return None

    def getInterval(self):
        '''return [datetime t1, datetime t2] if 'interval', none else'''
        if self.value.stype == 'interval':
            return self.value. slot[0]
        return None

    def link(self, other):
        '''
        return the link (string) between self.value and other.value :
        - equals     : if self and other are the same
        - disjoint   : if self's intervals and other's intervals are all disjoint
        - within     : if all self's intervals are included in other's intervals
        - contains   : if all other's intervals are included in self's intervals
        - intersects : in the others cases'''
        if self.isEqual(other, name=False):
            return 'equals'
        return self.value.link(other.value)[0]

    @staticmethod
    def nullValue():
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

    def vSimple(self, string=False, **kwargs):
        """return a datetime : middle of the TimeSlot."""
        if string:
            return self.value.instant.isoformat(**kwargs)
        return self.value.instant

    def _jsonValue(self, **option):
        '''return a json/cbor/dict for the value (TimeSlot) '''
        return self.value.json(**option)


class LocationValue(ESValue):              # !!! début LocationValue
    # %% loc
    """
    This class represent the Location of an Observation (point, polygon).

    *Attributes (for @property see methods)* :

    - **value** : Shapely object (point, polygon)
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `LocationValue.Simple`   (point)
    - `LocationValue.Box`
    - `LocationValue.from_obj` (see  `ESValue.from_obj`)

    *getters (@property)*

    - `LocationValue.coords`
    - `LocationValue.coorInv`

    *getters*

    - `LocationValue.getPoint`
    - `LocationValue.vSimple`
    - `LocationValue.vPointInv`
    - `LocationValue.vPointX`
    - `LocationValue.vPointY`
    - `LocationValue.vCodePlus`
    - `LocationValue.link`
    """
    @classmethod
    def Simple(cls, coord):
        '''return LocationValue built with tuple or list coordinates (x,y)'''
        return cls(shape=shapely.geometry.Point(*coord), name='point')

    @classmethod
    def Box(cls, bounds, ccw=True):
        '''return LocationValue built with tuple or list box coordinates (minx, miny, maxx, maxy)'''
        if isinstance(bounds, cls):
            bound = bounds.bounds
        else:
            bound = bounds
        return cls(val=shapely.geometry.box(*bound, ccw), name='box')

    @classmethod
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.loc_clsName, simple=False)

    def __init__(self, val=ES.nullCoor, name=ES.nullName):
        '''
        LocationValue constructor.

        *Parameters*

        - **val** :  compatible shapely.geometry.Point (or Polygon) Value (default nullCoor)
        - **name** :  string (default nullName)
        '''
        ESValue.__init__(self)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
            return
        if isinstance(val, (shapely.geometry.multipoint.MultiPoint,
                            shapely.geometry.point.Point,
                            shapely.geometry.polygon.Polygon,
                            shapely.geometry.multipolygon.MultiPolygon)):
            self.value = val
        elif not val is None:
            if isinstance(val, str) and not name:
                name = val
            else:
                self.value = self._gshape(val)
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName:
            self.name = name

    def __lt__(self, other):
        ''' return minimal distance between a fixed point'''
        if self.__class__.__name__ != other.__class__.__name__:
            return hash(self) < hash(other)
        # if self.coorInv == ES.nullCoor:
        if self.coorInv == other.coorInv:
            return self.name < other.name
        return distance.distance(self.coorInv, ES.distRef) <  \
            distance.distance(other.coorInv, ES.distRef)

    @property
    def __geo_interface__(self):
        return json.loads(json.dumps(self.value.__geo_interface__, cls=ESValueEncoder))

    @staticmethod
    def boundingBox(listValue):
        ''' return a tuple (xmin, ymin, xmax, ymax) with bounds values'''
        return [min([val.value.bounds[0] for val in listValue]),
                min([val.value.bounds[1] for val in listValue]),
                max([val.value.bounds[2] for val in listValue]),
                max([val.value.bounds[3] for val in listValue])]

    @property
    def coords(self):
        ''' return geoJson coordinates (list)'''
        if isinstance(self.value, shapely.geometry.polygon.Polygon):
            coords = [list(self.value.exterior.coords)]
        elif isinstance(self.value, shapely.geometry.point.Point):
            coords = list(self.value.coords[0])
        elif isinstance(self.value, shapely.geometry.linestring.LineString):
            coords = list(self.value.coords)
        else:
            coords = ES.nullCoor
        return json.loads(json.dumps(coords, cls=ESValueEncoder))

    @property
    def coorInv(self):
        '''list (@property) : vSimple inverse coordinates [vSimple[1], vSimple[0]]'''
        return [self.vSimple()[1], self.vSimple()[0]]

    def getPoint(self):
        ''' return a list with point coordinates [x, y] if the shape is a point, else none'''
        if isinstance(self.value, shapely.geometry.point.Point):
            return [self.value.x, self.value.y]
        return None

    def link(self, other):
        '''
        return the link (string) between self.value and other.value :
        - equals     : if self and other are the same
        - disjoint   : if self's shape and other's shape are disjoint
        - within     : if other's shape contains self's shape
        - contains   : if self's shape contains other's shape
        - intersects : in the others cases'''
        if self.isEqual(other, name=False):
            return 'equals'
        if self.value.equals(other.value):
            return 'equals'
        if self.value.contains(other.value):
            return 'contains'
        if self.value.within(other.value):
            return 'within'
        if self.value.disjoint(other.value):
            return 'disjoint'
        if self.value.intersects(other.value):
            return 'intersects'

    @staticmethod
    def nullValue():
        ''' return nullPosition value'''
        return LocationValue._gshape(ES.nullCoor)

    def vCodePlus(self):
        ''' return CodePlus value (string) of the point property value'''
        return openlocationcode.encode(self.vSimple(False)[1], self.vSimple(False)[0])

    def vSimple(self, string=False):
        ''' return simple value (centroid coordinates for the shape : 
            [x, y]) in a string format or in a object format'''
        if string:
            return json.dumps([round(self.value.centroid.x, 5), round(self.value.centroid.y, 5)], cls=ESValueEncoder)
        return [round(self.value.centroid.x, 5), round(self.value.centroid.y, 5)]

    def vPointInv(self, string=False):
        ''' return point (property) with inversed vSimple coordinates in a string format or
        in a list format [y, x]'''
        if string:
            return json.dumps([self.vSimple()[1], self.vSimple()[0]], cls=ESValueEncoder)
        return [self.vSimple()[1], self.vSimple()[0]]

    def vPointX(self):
        ''' return point (property) coordinates x '''
        return self.vSimple()[0]

    def vPointY(self):
        ''' return point (property) coordinates y '''
        return self.vSimple()[1]

    def _jsonValue(self, **kwargs):
        ''' return geoJson coordinates'''
        if 'geojson' in kwargs and kwargs['geojson']:
            return self.__geo_interface__
        return self.coords

    @staticmethod
    def _gshape(coord):
        ''' transform a GeoJSON coordinates (list) into a shapely geometry'''
        if isinstance(coord, tuple):
            coor = json.dumps(list(coord), cls=ESValueEncoder)
        elif isinstance(coord, list):
            coor = json.dumps(coord, cls=ESValueEncoder)
        elif isinstance(coord, dict):
            coor = json.dumps(coord, cls=ESValueEncoder)
        elif isinstance(coord, str):
            coor = coord
        else:
            coor = copy(coord)
        for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
            try:
                return shapely.geometry.shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coor + '}'))
            except:
                pass
        raise ESValueError('coordinates unconsistent')
        return None


class PropertyValue(ESValue):              # !!! début ESValue
    # %% prp
    """
    This class represents the Property of an Observation.

    *Attributes (for @property see methods)* :

    - **value** : dict
    - **name** : String

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `PropertyValue.Simple`   (property type)
    - `PropertyValue.Box`      (set of property type)
    - `PropertyValue.from_obj` (see  `ESValue.from_obj`)

    *getters*

    - `PropertyValue.vSimple`
    - `PropertyValue.link`
    """
    @classmethod
    def Simple(cls, prp, name='simple', prp_dict=False):
        '''PropertyValue built with a value (property type) '''
        return cls(val={ES.prp_type: prp}, name=name, prp_dict=prp_dict)

    @classmethod
    def Box(cls, prp, name='box', prp_dict=False):
        '''PropertyValue built with a value (property type) '''
        return cls(val={ES.prp_type: prp}, name=name, prp_dict=prp_dict)

    @classmethod
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.prp_clsName, simple=False)

    def __init__(self, val=ES.nullPrp, name=ES.nullName, prp_dict=False):
        '''
        PropertyValue constructor.

        *Parameters*

        - **val** :  property dict or json string (default nullPrp)
        - **name** :  string (default nullName)
        - **prp_dict** : boolean(default False) - if True type property has to be in the type dictionary
        '''
        ESValue.__init__(self)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
            return
        if not val is None and name == ES.prp_type:
            name = None
            val = {ES.prp_type: val}
        elif isinstance(val, str) and isinstance(name, str) and name != ES.nullName:
            val = {name: val}
        if isinstance(val, dict):
            if len(val) > 0 and isinstance(list(val.values())[0], dict):
                self.name = list(val.keys())[0]
                self.value |= val[list(val.keys())[0]]
            else:
                self.value |= val
        elif isinstance(val, str):
            name = val
        # elif not val is None: raise ESValueError('type data not compatible with PropertyValue')
        # else: raise ESValueError('type data not compatible with PropertyValue')

        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName:
            self.name = name
        if not ES.prp_type in self.value:
            raise ESValueError("type property not defined")
        if not isinstance(self.value[ES.prp_type], list):
            if prp_dict and not self.value[ES.prp_type] in ES.prop:
                raise ESValueError(
                    "property not present in standard dictionnary")
            if prp_dict:
                self.value[ES.prp_unit] = ES.prop[self.value[ES.prp_type]][5]

    def __lt__(self, other):
        """lower if string simple value + name is lower"""
        if self.__class__.__name__ != other.__class__.name:
            return hash(self) < hash(other)
        return self.simple + self.name < other.simple + other.name

    @staticmethod
    def boundingBox(listValue):
        ''' return a tuple with 'prp' values'''
        return [val.value['prp'] for val in listValue]

    def link(self, other):
        '''
        return the link (string) between self.value and other.value :
        - equals     : if self and other are the same
        - disjoint   : if the self's key/val are all different from other's key/val
        - within     : if all self's key/val are included in other's key/val
        - contains   : if all other's key/val are included in self's key/val
        - intersects : in the others cases'''
        if self.isEqual(other, name=False):
            return 'equals'
        sprp = self._setprp(self.value[ES.prp_type])
        oprp = self._setprp(other.value[ES.prp_type])
        if oprp == sprp:
            union = other.value | self.value
            union2 = self.value | other.value
            if union == self.value and union2 == self.value:
                return 'within'
            if union == other.value and union2 == other.value:
                return 'contains'
            if union == union2:
                return 'disjoint'
            return 'intersects'
        if sprp == sprp | oprp:
            return 'contains'
        if oprp == sprp | oprp:
            return 'within'
        if oprp & sprp == set():
            return 'disjoint'
        else:
            return 'intersects'
        return 'undefined'

    @staticmethod
    def nullValue():
        ''' return nullPrp value'''
        return {ES.prp_type: ES.nullDict, ES.prp_unit: ES.prop[ES.nullDict][5]}

    def vSimple(self, string=False):
        ''' return simple value (type for the property) in a string format or in a object format'''
        simple = ES.nullDict
        if ES.prp_type in self.value:
            simple = self.value[ES.prp_type]
        if string:
            return json.dumps(simple, cls=ESValueEncoder)
        return simple

    def _jsonValue(self, **kwargs):
        option = {'encoded': False} | kwargs
        li = {}
        for k, v in self.value.items():
            if k in [ES.prp_type, ES.prp_unit, ES.prp_sampling, ES.prp_appli, ES.prp_EMFId]:
                if v != ES.nullDict:
                    li[k] = v
            elif k in [ES.prp_period, ES.prp_interval, ES.prp_uncertain]:
                if v != ES.nullInt:
                    li[k] = v
            else:
                li[k] = v
        if option['encoded']:
            return json.dumps(li, ensure_ascii=False, cls=ESValueEncoder)
        return li

    @staticmethod
    def _setprp(val):
        if isinstance(val, list):
            return set(val)
        return {val}


class NamedValue (ESValue):               # !!! début ResValue
    # %% nam
    '''This class represent a simple value with an associated string.

    *Attributes (for @property see methods)* :

    - **value** : any json object
    - **name** : String

    The methods defined in this class are :

    *constructor*

    - `NamedValue.from_obj` (see  `ESValue.from_obj`)

    *getters*

    - `NamedValue.vSimple`
    '''
    @classmethod
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.nam_clsName, simple=False)

    def __init__(self, val=ES.nullVal, name=ES.nullName):
        '''
        NamedValue constructor.

        *Parameters*

        - **val** :  any simple object (default nullVal)
        - **name** : string (default nullName)
        '''
        ESValue.__init__(self)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
            return
        self.value = ESValue._castsimple(val)
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName:
            self.name = name

    @staticmethod
    def nullValue():
        ''' return nullVal value'''
        return ES.nullVal

    def vSimple(self, string=False):
        '''return float value in string or object format'''
        from util import util
        if string:
            return str(util.cast(self.value, dtype='simple'))
        return util.cast(self.value, dtype='simple')

    def _jsonValue(self, **option):
        '''return the value '''
        if isinstance(self.value, (int, str, float, bool, list, dict,
                                   datetime.datetime, type(None), bytes)):
            return self.value
        if isinstance(self.value, tuple):
            return list(self.value)


class ExternValue (ESValue):               # !!! début ResValue
    # %% ext
    '''This class represent a complex (extern) value with an associated string.

    *Attributes (for @property see methods)* :

    - **value** : any object
    - **name** : String

    The methods defined in this class are :

    *constructor*

    - `ExternValue.from_obj` (see  `ESValue.from_obj`)

    *getters*

    - `ExternValue.vSimple`
    '''
    @classmethod
    def from_obj(cls, bs):
        ''' ESValue function (see ESValue.from_obj)'''
        return ESValue.from_obj(bs, ES.ext_clsName, simple=False)

    def __init__(self, val=ES.nullExternVal, name=ES.nullName, className=None):
        '''
        ExternValue constructor.

        *Parameters*

        - **val** :  any simple object (default nullVal)
        - **name** : string (default nullName)

        '''
        ESValue.__init__(self)
        if isinstance(val, self.__class__):
            self.name = val.name
            self.value = val.value
            return
        #self.value = ESValue.from_obj(val, classname=className)
        if val == ES.nullExternVal and name == ES.nullName:
            return
        if not className:
            className = val.__class__.__name__
        if className in _classval():
            self.value = _classval()[className](val)
        else:
            raise ESValueError('class name inconsistent with ExternValue')
        if self.name == ES.nullName and isinstance(name, str) and name != ES.nullName:
            self.name = name

    @staticmethod
    def nullValue():
        ''' return nullVal value'''
        return ES.nullExternVal

    def vSimple(self, string=False):
        '''return conversion from value to float'''
        from util import util
        if string:
            return str(util.cast(self.value, dtype='simple'))
        return util.cast(self.value, dtype='simple')

    def _jsonValue(self, **option):
        '''return a json object for the value '''
        if self.value.__class__.__name__ in ['Ntvfield', 'Ntvdataset', 'Observation']:
            return self.value.json(encoded=False, encode_format='json')
        if isinstance(self.value, (int, str, float, bool, list, tuple, dict, datetime.datetime, type(None), bytes)):
            return self.value
        if isinstance(self.value, (DatationValue, LocationValue, PropertyValue, NamedValue, ExternValue)):
            return self.value.json(encoded=False, encode_format='json')
        try:
            return self.value.to_json(encoded=False, encode_format='json',
                                      json_info=False, json_res_index=True, json_param=True)
        except:
            return object.__repr__(self.value)


class ESValueError(Exception):
    # %% ES except
    ''' ESValue Exception'''
    pass
