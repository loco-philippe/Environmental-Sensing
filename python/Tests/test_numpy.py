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
        return {':ndarray': [data, dtype], 'xnames': axes_name, 'xvalues': axes_values}
    return [data, dtype]
        
def from_json(js):
    if isinstance(js, dict):
        return (np.array(js[':ndarray'][0], dtype=js[':ndarray'][1]), 
                {name: val for name, val in zip(js['xnames'], js['xvalues'])})
    return (np.array(js[0], dtype=js[1]), {})

def to_json_tab(ndarray, axes=None):
    period = ndarray.shape
    dim = ndarray.ndim

    coefi = ndarray.size
    coef = []
    for per in period:
        coefi = coefi // per
        coef.append(coefi)
        
    axes_name = list(axes) if axes else ['axe' + str(i) for i in range(dim)]
    axes_value = list(axes.values()) if isinstance(axes, dict) else [list(range(period[i])) for i in range(dim)]
    axes = {name: [val, [coe]] for name, val, coe in zip(axes_name, axes_value, coef)}
    return axes | {'::' + ndarray.dtype.name: ndarray.flatten().tolist()}    

def from_json_tab(js):
    ntv = Ntv.obj(js)
    if len(ntv) == 0:
        return
    decode = [list(NtvUtil.decode_ntv_tab(ntvf, Sfield.l_to_i)) for ntvf in ntv]
    print(decode)
    print(type(decode[2][0]))
    #leng = max(field[6] for field in decode)
    #format_fields = NtvConnector.format_field(decode, leng)    
    
    shape = []
    axes_name = []
    axes_values = []
    coef = []
    ndarray = None
    for field in decode:
        if field[5]:
            shape.append(len(field[2]))
            coef.append(field[5])
            axes_values.append(field[2])
            axes_name.append(field[0])
        else:
            ndarray = np.array([ntv.val for ntv in field[2]], dtype=field[1])
    coef, shape, axes_name, axes_values = list(zip(*sorted(zip(coef, shape, axes_name, axes_values), reverse=True)))
    return (ndarray.reshape(shape), 
            {name: val for name, val in zip(axes_name, axes_values)})
