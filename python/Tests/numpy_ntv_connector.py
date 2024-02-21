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
    option = kwargs
    jso = json.loads(jsn) if isinstance(jsn, str) else jsn
    ntv = Ntv.from_obj(jso)
    if ntv.type_str == 'ndarray':
        return NdarrayConnec.to_obj_ntv(ntv.ntv_value, **option)
    return NdarrayConnec.to_obj_ntv(ntv.ntv_value, **option)


def to_json(ndarray, **kwargs):
    ''' convert Numpy ndarray to JSON text or JSON Value.

    *parameters*
    - **meta** : dict (default none) - names and values of axes
    - **dtype** : Boolean (default True) - including dtype

    '''
    option = {'encoded': False, 'header': True, 'meta': None, 'dtype': True,
              'name': None, 'extension':None} | kwargs

    jsn = NdarrayConnec.to_json_ntv(ndarray, **option)[0]
    name = '' if not option['name'] else option['name']
    extension = '[' + option['extension'] + ']' if option['extension'] else ''
    if option['header'] or option['name'] or option['extension']:
        head = ':xndarray' if option['meta'] else ':ndarray'
        jsn = {name + head + extension: jsn}
    if option['encoded']:
        return json.dumps(jsn)
    return jsn

def to_json_tab(ndarray, meta=None, header=True):
    period = ndarray.shape
    dim = ndarray.ndim
    coefi = ndarray.size
    coef = []
    for per in period:
        coefi = coefi // per
        coef.append(coefi)
    
    meta = meta if meta else {}   
    axe_n = meta['axes'] if 'axes' in meta else ['axe' + str(i) for i in range(dim)]
    axe_v = meta['axevars'] if 'axevars' in meta else [
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
    return (nda.reshape(shape), {'axes': list(axes_n), 'axevars': list(axes_v)})

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
        
        data = ntv_value
        axes = None
        if isinstance(ntv_value, dict):
            data = ntv_value['data']
            axes = {key:val for key, val in ntv_value.items() if key != 'data'} 
        dtype, data = data if (len(data) == 2 and isinstance(data[0], str) 
                               and len(data[1]) > 1) else (None, data)
        np_data = np.array(data, dtype=dtype)       
        return (np_data, axes) if axes else np_data

    @staticmethod
    def to_json_ntv(value, name=None, typ=None, **kwargs):
        ''' convert a ndarray (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : ndarray values
        - **meta** : dict (default none) - names and values of axes
        - **dtype** : Boolean (default True) - including dtype
        '''
        axes = kwargs.get('meta')
        opt_dtype = kwargs.get('dtype', True)
        data = [value.dtype.name, value.tolist()] if opt_dtype else value.tolist()
        typ = NdarrayConnec.clas_typ if not typ else typ
        if axes: 
            return ({'data': data} | axes, name, typ)
        return (data, name, typ) 