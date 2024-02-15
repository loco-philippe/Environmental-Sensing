# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 15:54:47 2024

@author: a lab in the Air
"""

import numpy as np

from field import Sfield, Nfield

from ntv_util import NtvUtil, NtvConnector
from json_ntv import Ntv

def to_json(ndarray, axes=None):
    data = ndarray.tolist()
    dtype = ndarray.dtype.name
    if axes: 
        axes_name = list(axes)
        axes_values = list(axes.values())
        return {'data': [data, dtype], 'xnames': axes_name, 
                'xvalues': axes_values}
    return [data, dtype]
        
def from_json(js):
    if isinstance(js, dict):
        return (np.array(js['data'][0], dtype=js['data'][1]), 
                {name: val for name, val in zip(js['xnames'], js['xvalues'])})
    return np.array(js[0], dtype=js[1])

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

def from_json_tab(js):
    
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
