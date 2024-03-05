# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:49:49 2024

@author: a lab in the Air
"""

import os
import datetime
import json
import configparser
from pathlib import Path
import pandas as pd
import numpy as np
from decimal import Decimal

from json_ntv.ntv import Ntv, NtvConnector, NtvList, NtvSingle
from json_ntv.ntv_util import NtvUtil
from json_ntv.ntv_connector import ShapelyConnec
from tab_dataset.cfield import Cfield
from data_array import Dfull, Dcomplete, Darray


def read_json(jsn, **kwargs):
    ''' convert JSON text or JSON Value to Numpy ndarray.

    *parameters*

    - **jsn** : JSON text or JSON value to convert
    '''
    option = {'noadd': False, 'header': True} | kwargs
    jso = json.loads(jsn) if isinstance(jsn, str) else jsn
    if isinstance(jso, dict) and len(jso) == 1:
        if 'xndarray' in list(jso)[0]:
            arr = XndarrayConnec.to_obj_ntv(list(jso.values())[0], **option)
            if option['header']:
                return {list(jso)[0]: arr}
            return arr
        else:
            arr = NdarrayConnec.to_obj_ntv(list(jso.values())[0], **option)
            if option['header']:
                return {arr[0] + ':' + list(jso)[0]: arr[1]}
            return arr 
    if isinstance(jso, list):
        option = {'noadd': False, 'header': False} | kwargs
        arr =  NdarrayConnec.to_obj_ntv(jso, **option)
        if option['header']:
            return {arr[0]: arr[1]}
        return arr
    return None


def to_json(ndarray, **kwargs):
    ''' convert Numpy ndarray to JSON text or JSON Value.

    *parameters*
    - **encoded** : Boolean (default False) - json value if False else json text
    - **header** : Boolean (default True) - including ndarray or xndarray type
    - **notype** : Boolean (default False) - including data type if True
    - **name** : string (default None) - name of the ndarray
    - **typ** : string (default None) - type of the NTV object,
    - **extension** : string (default None) - type extension
    - **add** : dict (default None) - additional data :
        - **attrs** : dict (default none) - metadata
        - **dims** : array (default none) - name of axis
        - **coords** : dict (default none) - dict of 'xndarray'
    '''
    option = {'encoded': False, 'format': 'full', 'header': True, 
              'name': None, 'typ': None, 'extension':None, 'notype': False, 
              'add': None} | kwargs
    if ndarray.__class__.__name__ == 'ndarray' and not kwargs.get('add'):
        jsn, nam, typ = NdarrayConnec.to_json_ntv(ndarray, **option)
    else:
        jsn, nam, typ = XndarrayConnec.to_json_ntv(ndarray, **option)        
    name = nam if nam else ''
    if option['header'] or name:
        typ = ':' + typ if option['header'] else '' 
        jsn = {name + typ : jsn}
    if option['encoded']:
        return json.dumps(jsn)
    return jsn

def to_json_tab(ndarray, add=None, header=True):
    period = ndarray.shape
    dim = ndarray.ndim
    coefi = ndarray.size
    coef = []
    for per in period:
        coefi = coefi // per
        coef.append(coefi)
    
    add = add if add else {}   
    axe_n = add['dims'] if 'dims' in add else ['dim_' + str(i) for i in range(dim)]
    axe_v = [add['coords'][axe] for axe in axe_n if axe in add['coords']] if 'coords' in add else []
    axe_v = [axe[-1] for axe in axe_v] if len(axe_v) == len(axe_n) else [
                      list(range(period[i])) for i in range(dim)]
    jsn = {nam: [var, [coe]] for nam, var, coe in zip(axe_n, axe_v, coef)} | {
           'data::' + ndarray.dtype.name: ndarray.flatten().tolist()}
    if header:
        return {':tab': jsn}
    return jsn

def read_json_tab(js):
    js = js[':tab'] if ':tab' in js else js
    shape = []
    axes_n = []
    axes_v = []
    coef = []
    nda = None
    for name, val in js.items():
        if len(val) == 2 and isinstance(val[1], list) and len(val[1]) == 1:
            shape.append(len(val[0]))
            coef.append(val[1])
            axes_v.append(val[0])
            axes_n.append(name)            
        else:
            spl = name.split('::')
            nda = np.array(val, dtype=spl[1]) if len(spl)==2 else np.array(val)
    coef, shape, axes_n, axes_v = list(zip(*sorted(zip(coef, shape, axes_n, 
                                                       axes_v), reverse=True)))
    return (nda.reshape(shape), {'dims': list(axes_n), 
            'coords': {axe_n: [axe_v] for axe_n, axe_v in zip(axes_n, axes_v)}})

class NdarrayConnec(NtvConnector):

    '''NTV connector for pandas DataFrame.

    One static methods is included:

    - to_listidx: convert a DataFrame in categorical data
    '''

    clas_obj = 'ndarray'
    clas_typ = 'ndarray'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):  # reindex=True, decode_str=False):
        ''' convert json ntv_value into a ndarray.

        *Parameters*

        - **index** : list (default None) - list of index values,
        - **alias** : boolean (default False) - if True, alias dtype else default dtype
        - **annotated** : boolean (default False) - if True, NTV names are not included.'''
        data = ntv_value[-1]
        match ntv_value[:-1]:
            case [ntv_type, shape]:
                param = (data, ntv_type, shape)
            case [ntv_type] if isinstance(ntv_type, str):
                param = (data, ntv_type, None)
            case [shape] if isinstance(shape, list):
                param = (data, None, shape)
            case _:
                param = (data, None, None)
        if kwargs.get('header', False):
            return (ntv_type, NdarrayConnec.to_array(*param))
        return NdarrayConnec.to_array(*param)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None, **kwargs):
        ''' convert a ndarray (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : ndarray values
        - **notype** : Boolean (default False) - including data type if False
        - **extension** : string (default None) - type extension
        '''    
        option = {'notype': False, 'extension': None, 'format': 'full'} | kwargs
        if len(value) == 0:
            return ([[]], name, 'ndarray')
        typ, ext = NpUtil.split_typ(typ)
        ext = ext if ext else option['extension']
        dtype = value.dtype.name
        dtype = value[0].__class__.__name__ if dtype == 'object' else dtype
        ntv_type = NpUtil.ntv_type(dtype, typ, ext)
        
        shape = list(value.shape)
        shape = shape if len(shape) > 1 else None 

        form = option['format']    
        if shape:
            js_val   = NpUtil.ntv_val(ntv_type, value.flatten(), form)
        else:
            js_val   = NpUtil.ntv_val(ntv_type, value, form)
            
        lis = [ntv_type if not option['notype'] else None, shape, js_val]
        return ([val for val in lis if not val is None], name, 'ndarray')

    @staticmethod
    def to_jsonv(value):
        ''' convert a 1D ndarray into json-value.'''    
        if len(value) == 0:
            return [[]]
        dtype = value.dtype.name
        dtype = value[0].__class__.__name__ if dtype == 'object' else dtype
        ntv_type = NpUtil.ntv_type(dtype, None, None)

        shape = list(value.shape)
        shape = shape if len(shape) > 1 else None 
        
        if shape:
            js_val   = NpUtil.ntv_val(ntv_type, value.flatten(), 'full')
        else:
            js_val   = NpUtil.ntv_val(ntv_type, value, 'full')

        lis = [ntv_type, shape, js_val]        
        return [val for val in lis if not val is None]

    @staticmethod
    def to_array(darray_js, ntv_type=None, shape=None):
        darray = Darray.read_list(darray_js)
        darray.data = NpUtil.convert(ntv_type, darray.data, tojson=False)
        return darray.values.reshape(shape)
 
class XndarrayConnec(NtvConnector):

    '''NTV connector for xndarray.

    One static methods is included:

    - to_listidx: convert a DataFrame in categorical data
    '''

    clas_obj = 'xndarray'
    clas_typ = 'xndarray'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):  # reindex=True, decode_str=False):
        ''' convert json ntv_value into a ndarray.

        *Parameters*

        - **index** : list (default None) - list of index values,
        - **alias** : boolean (default False) - if True, alias dtype else default dtype
        - **annotated** : boolean (default False) - if True, NTV names are not included.
        '''        
        np_data = NdarrayConnec.to_obj_ntv(ntv_value['data'])
        add = {key: val for key, val in ntv_value.items()
                if key in ('attrs', 'dims', 'coords')}
        return (np_data, add) if add and not kwargs['noadd'] else np_data

    @staticmethod
    def to_json_ntv(value, name=None, typ=None, **kwargs):
        ''' convert a xndarray (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : ndarray values
        - **notype** : Boolean (default False) - including data type if False
        - **name** : string (default None) - name of the ndarray
        - **extension** : string (default None) - type extension
        - **add** : dict (default None) - additional data :
            - **attrs** : dict (default none) - metadata
            - **dims** : array (default none) - name of axis
            - **coords** : dict (default none) - dict of 'xndarray'
        '''
        add = kwargs.get('add')
        dims = add.get('dims') if add else None
        attrs = add.get('attrs') if add else None
        coords = add.get('coords') if add else None
        dic = {'data': NdarrayConnec.to_json_ntv(value, kwargs=kwargs)[0], 
               'dims': dims, 'coords': coords, 'attrs': attrs}
        return ({key: val for key, val in dic.items() if not val is None},
                name, 'xndarray')

class NpUtil:
    '''ntv-ndarray utilities.'''

    DATATION_DT = {'date': 'datetime64[D]', 'year': 'datetime64[Y]',
                'yearmonth': 'datetime64[M]', 
                'datetime': 'datetime64[s]', 'datetime[ms]': 'datetime64[ms]',
                'datetime[us]': 'datetime64[us]', 'datetime[ns]': 'datetime64[ns]', 
                'datetime[ps]': 'datetime64[ps]', 'datetime[fs]': 'datetime64[fs]',
                'timedelta': 'timedelta64[s]', 'timedelta[ms]': 'timedelta64[ms]',
                'timedelta[us]': 'timedelta64[us]', 'timedelta[ns]': 'timedelta64[ns]', 
                'timedelta[ps]': 'timedelta64[ps]', 'timedelta[fs]': 'timedelta64[fs]',
                'timedelta[D]': 'timedelta64[D]', 'timedelta[Y]': 'timedelta64[Y]',
                'timedelta[M]': 'timedelta64[M]'}
    DT_DATATION = {val:key for key, val in DATATION_DT.items()}
    
    CONNECTOR_DT = {'field': 'Series', 'tab': 'DataFrame'}    
    DT_CONNECTOR = {val:key for key, val in CONNECTOR_DT.items()}
    
    PYTHON_DT = {'array': 'list',
                'object': 'dict', 'null': 'NoneType', 'decimal64': 'Decimal',
                'ndarray': 'ndarray'}
    DT_PYTHON = {val:key for key, val in PYTHON_DT.items()}

    OTHER_DT = {'boolean': 'bool', 'string': 'str'}
    DT_OTHER = {val:key for key, val in OTHER_DT.items()}
    
    LOCATION_DT = {'point': 'Point', 'line': 'LinearRing', 'polygon': 'Polygon'}
    DT_LOCATION = {val:key for key, val in LOCATION_DT.items()}
    
    DT_NUMBER = {'json': 'object', 'number': None, 'month': 'int', 'day': 'int',
                 'wday': 'int', 'yday': 'int', 'week': 'hour', 'minute': 'int',
                 'second': 'int'}
    DT_STRING = {'base16': 'str', 'base32': 'str', 'base64': 'str', 
                 'period': 'str', 'duration': 'str', 'jpointer': 'str',
                 'uri': 'str', 'uriref': 'str', 'iri': 'str', 'iriref': 'str',
                 'email': 'str', 'regex': 'str', 'hostname': 'str', 'ipv4': 'str',
                 'ipv6': 'str', 'file': 'str', 'geojson': 'str',}
    FORMAT_CLS = {'full': Dfull, 'complete': Dcomplete}
    
    @staticmethod 
    def add_ext(typ, ext):
        '''return extended typ'''
        ext = '['+ ext +']' if ext else ''
        return '' if not typ else typ + ext
    
    @staticmethod
    def split_typ(typ):
        '''return a tuple with typ and extension'''
        if not isinstance(typ, str):
            return (None, None) 
        spl = typ.split('[', maxsplit=1)
        return (spl[0], None) if len(spl) == 1 else (spl[0], spl[1][:-1])

    @staticmethod
    def convert(ntv_type, nda, tojson=True):
        ''' convert ndarray with external NTVtype.

        *Parameters*

        - **ntv_type** : string - NTVtype deduced from the ndarray name_type and dtype,
        - **nda** : ndarray to be converted.
        - **tojson** : boolean (default True) - apply to json function
        '''
        if tojson:
            match ntv_type:
                case dat if dat in NpUtil.DATATION_DT:
                    return nda.astype(NpUtil.DATATION_DT[dat]).astype(str)
                case 'bytes':
                    return nda.astype('bytes').astype(str)                
                case 'time':
                    return nda.astype(str)    
                case 'decimal64':
                    return nda.astype(float)  
                case 'geojson':
                    return np.frompyfunc(ShapelyConnec.to_geojson, 1, 1)(nda)
                case _:
                    return nda
        else:
            DTYPE = (NpUtil.DT_DATATION | NpUtil.DT_LOCATION | 
                     NpUtil.DT_CONNECTOR | NpUtil.DT_OTHER | NpUtil.DT_PYTHON |
                     NpUtil.DT_NUMBER | NpUtil.DT_STRING)
            match ntv_type:
                case dat if dat in NpUtil.DATATION_DT:
                    return nda.astype(NpUtil.DATATION_DT[dat])
                case std if std in NpUtil.OTHER_DT:
                    return nda.astype(NpUtil.OTHER_DT[std])                    
                case 'time':
                    return np.frompyfunc(datetime.time.fromisoformat, 1, 1)(nda)                   
                case 'decimal64':
                    return np.frompyfunc(Decimal, 1, 1)(nda)   
                case 'ndarray':
                    return np.frompyfunc(NdarrayConnec.to_obj_ntv, 1, 1)(nda) 
                case python if python in NpUtil.PYTHON_DT:
                    return nda.astype('object')
                case connec if connec in NpUtil.CONNECTOR_DT:
                    return np.fromiter([NtvConnector.uncast(nd, None, connec)[0]
                                        for nd in nda], dtype='object')
                case 'point' | 'line' | 'polygon' | 'geometry':
                    return np.frompyfunc(ShapelyConnec.to_geometry, 1, 1)(nda)
                case _:
                    type_base = NpUtil.split_typ(ntv_type)[0]
                    dtype = DTYPE.get(ntv_type, DTYPE.get(type_base, type_base))
                    return nda.astype(dtype)
        
    @staticmethod
    def ntv_val(ntv_type, nda, form):
        ''' convert a simple ndarray into NTV json-value.

        *Parameters*

        - **ntv_type** : string - NTVtype deduced from the ndarray, name_type and dtype,
        - **nda** : ndarray to be converted.
        - **form** : format of data ('full', 'complete', 'sparse', 'primary').
        '''
        if form == 'complete' and len(nda) < 2:
            raise NdarrayError("complete format is not available with ndarray length < 2")
        Format = NpUtil.FORMAT_CLS[form]
        darray = Format(nda)
        ref = darray.ref
        coding = darray.coding
        match ntv_type:
            case 'ndarray':
                #data = np.frompyfunc(NdarrayConnec.to_jsonv, 1, 1)(darray.data) 
                data = [NdarrayConnec.to_jsonv(nd) for nd in darray.data] 
            case connec if connec in NpUtil.CONNECTOR_DT:
                data = [NtvConnector.cast(nd, None, connec)[0] for nd in darray.data] 
            case 'point' | 'line' | 'polygon' | 'geometry':
                data = np.frompyfunc(ShapelyConnec.to_coord, 1, 1)(darray.data)
            case _:
                data = NpUtil.convert(ntv_type, darray.data).tolist()
        return Format(data, ref=ref, coding=coding).to_list()
    
    @staticmethod
    def ntv_type(dtype, typ, ext):
        ''' return NTVtype from dtype, additional type and extension.

        *Parameters*

        - **dtype** : string - dtype of the ndarray
        - **typ** : string - additional type
        - **ext** : string - type extension
        '''        
        DT_NTVTYPE = (NpUtil.DT_DATATION | NpUtil.DT_LOCATION | 
                      NpUtil.DT_OTHER | NpUtil.DT_CONNECTOR | NpUtil.DT_PYTHON)
        if typ:
            return NpUtil.add_ext(typ, ext)
        match dtype:
            case dat if dat in DT_NTVTYPE:
                return NpUtil.add_ext(DT_NTVTYPE[dat], ext)
            case string if string[:3] == 'str': 
                return NpUtil.add_ext('string', ext)
            case byte if byte[:5] == 'bytes': 
                return NpUtil.add_ext('bytes', ext)
            case _:
                return NpUtil.add_ext(dtype, ext)

    @staticmethod
    def dtype(ntv_type):
        ''' return (dtype, extension) from ntv_type'''
        return NpUtil.DATATION_DT.get(ntv_type)

class NdarrayError(Exception):
    '''Multidimensional exception'''