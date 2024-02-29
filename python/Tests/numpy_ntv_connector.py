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


from json_ntv.ntv import Ntv, NtvConnector, NtvList, NtvSingle
from json_ntv.ntv_util import NtvUtil
from json_ntv.ntv_connector import ShapelyConnec
from tab_dataset.cfield import Cfield


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
        else:
            arr = NdarrayConnec.to_obj_ntv(list(jso.values())[0], **option)
        if option['header']:
            return {list(jso)[0]: arr}
        return arr 
    if isinstance(jso, list):
        return NdarrayConnec.to_obj_ntv(jso, **option)
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
    option = {'encoded': False, 'header': True, 
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
        
        dtype = None
        shape = None
        data = ntv_value[-1]
        if len(ntv_value) == 3:
            dtype = ntv_value[0]
            shape = ntv_value[1]           
        elif len(ntv_value) == 2 and isinstance(ntv_value[0], str):
            dtype = ntv_value[0]
        elif len(ntv_value) == 2 and isinstance(ntv_value[0], list):
            shape = ntv_value[0]
        dtype=dtype.split('[')[0] if dtype else None
        return np.array(data, dtype=dtype).reshape(shape)

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
        typ, ext = NpUtil.split_typ(kwargs.get('typ'))
        ext = ext if ext else kwargs.get('extension')
        ntv_type = NpUtil.ntv_type(value.dtype.name, typ, ext)
        js_val   = NpUtil.ntv_val(ntv_type, value.flatten())
        print(type(js_val[0]), value.dtype.name)
        shape = list(value.shape)
        shape = shape if len(shape) > 1 else None 

        lis = [ntv_type if not kwargs.get('notype', False) else None, shape, js_val]
        return ([val for val in lis if not val is None], name, 'ndarray')

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
                'yearmonth': 'datetime64[M]', 'datetime': 'datetime64[s]',
                'duration': 'timedelta64[s]'}
    DT_DATATION = {val:key for key, val in DATATION_DT.items()}
    DT_OTHER = {'bool': 'boolean'}

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
        - **tojson** : boolean (default True) - apply to json function'''

        match ntv_type:
            case dat if dat in NpUtil.DATATION_DT:
                return nda.astype(NpUtil.DATATION_DT[dat]).astype(str)
            #case 'bool':
                
            case _:
                return nda
    
    @staticmethod
    def ntv_val(ntv_type, nda):
        ''' convert a simple ndarray into NTV json-value.

        *Parameters*

        - **ntv_type** : string - NTVtype deduced from the ndarray, name_type and dtype,
        - **nda** : ndarray to be converted.'''
        
        nda = NpUtil.convert(ntv_type, nda)
        return nda.tolist()
        '''if ntv_type in ['point', 'line', 'polygon', 'geometry', 'geojson']:
            return srs.to_list()
        if srs.dtype.name == 'object':
            return srs.to_list()
        return json.loads(srs.to_json(orient='records',
                                      date_format='iso', default_handler=str))

        return nda'''
    
    @staticmethod
    def ntv_type(dtype, typ, ext):
        ''' return NTVtype from dtype, additional type and extension.

        *Parameters*

        - **dtype** : string - dtype of the ndarray
        - **typ** : string - additional type
        - **ext** : string - type extension
        '''        
        DT_NTVTYPE = NpUtil.DT_DATATION | NpUtil.DT_OTHER
        ext = '['+ ext +']' if ext else ''
        if typ:
            return typ + ext
        match dtype:
            case dat if dat in DT_NTVTYPE:
                return DT_NTVTYPE[dat] + ext
            case _:
                return dtype + ext