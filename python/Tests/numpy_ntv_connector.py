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
    ''' convert JSON text or JSON Value to pandas Series or Dataframe.

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
    ''' convert pandas Series or Dataframe to JSON text or JSON Value.

    *parameters*
    - **axes** : list or dict (default none) - names and values of axes
    - **dtype** : Boolean (default True) - including dtype

    '''
    option = {'encoded': False, 'header': True, 'axes': None, 'dtype': True} | kwargs

    jsn = NdarrayConnec.to_json_ntv(ndarray, **option)[0]
    head = ':ndarray'
    if option['header']:
        jsn = {head: jsn}
    if option['encoded']:
        return json.dumps(jsn)
    return jsn

def to_json_tab(ndarray, axes=None):
    period = ndarray.shape
    dim = ndarray.ndim

    coefi = ndarray.size
    coef = []
    for per in period:
        coefi = coefi // per
        coef.append(coefi)
        
    axes_nam = list(axes) if axes else ['axe' + str(i) for i in range(dim)]
    axes_val = list(axes.values()) if isinstance(axes, dict) else [
        list(range(period[i])) for i in range(dim)]
    axes = {nam: [val, [coe]] for nam, val, coe in zip(axes_nam, axes_val, coef)}
    return axes | {'value::' + ndarray.dtype.name: ndarray.flatten().tolist()}    

def read_json_tab(js):
    
    shape = []
    axes_name = []
    axes_values = []
    coef = []
    ndarray = None
    for name, value in js.items():
        if len(value) == 2 and isinstance(value[1], list) and len(value[1]) == 1:
            shape.append(len(value[0]))
            coef.append(value[1])
            axes_values.append(value[0])
            axes_name.append(name)            
        else:
            spl = name.split('::')
            ndarray = np.array(value, dtype=spl[1]
                               ) if len(spl)==2 else np.array(value)
    coef, shape, axes_name, axes_values = list(
        zip(*sorted(zip(coef, shape, axes_name, axes_values), reverse=True)))
    return (ndarray.reshape(shape), 
            {name: val for name, val in zip(axes_name, axes_values)})

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
            axes = {name: val for name, val in zip(ntv_value['xnames'], 
                                                   ntv_value['xvalues'])}            
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
        - **axes** : list or dict (default none) - names and values of axes
        - **dtype** : Boolean (default True) - including dtype
        '''
        axes = kwargs.get('axes')
        opt_dtype = kwargs.get('dtype', True)
        data = [value.dtype.name, value.tolist()] if opt_dtype else value.tolist()
        typ = NdarrayConnec.clas_typ if not typ else typ
        if axes: 
            axes_name = list(axes)
            axes_values = list(axes.values())
            return ({'data': data, 'xnames': axes_name, 'xvalues': axes_values},
                    name, typ)
        return (data, name, typ) 