# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 15:54:47 2024

@author: a lab in the Air
"""

import numpy as np
from cfield import Cutil
from dataset import Sdataset
from field import Sfield
import ntv_pandas as npd
from ntv_util import NtvUtil, NtvConnector
from json_ntv import Ntv

def to_json(ndarray, axes=None, name=None, ntv=None ):
    
    ntv_t = ':xndarray' if axes and ntv == 'ndarray' else ':ndarray' if ntv== 'ndarray' else ':tab' if ntv == 'tab' else ''
    if ntv_t == ':tab':
        value = to_json_tab(ndarray, axes, name)
        name = ntv_t
    else: 
        #name = ntv_t if not name else name + ntv_t
        name = '' if not name else name
        data = {name + ':' + ndarray.dtype.name: ndarray.tolist()}
        value = data | axes if axes else data
    if name:
        return { name: value}
    return value
        

def to_json_tab(ndarray, axes=None, name=None):
    period = ndarray.shape
    dim = ndarray.ndim

    coefi = ndarray.size // period[0]
    coef = [coefi]
    for per in period[1:]:
        coefi = coefi // per
        coef.append(coefi)
        
    axes_name = list(axes) if axes else ['axe' + str(i) for i in range(dim)]
    axes_value = list(axes.values()) if axes else [list(range(period[i])) for i in range(dim)]
    axes = {name: [val, [coe]] for name, val, coe in zip(axes_name, axes_value, coef)}
    name = 'val' if not name else name
    return axes | {name: ndarray.flatten().tolist()}    

def from_json_tab(js):
    ntv = Ntv.obj(js)
    if len(ntv) == 0:
        return
    decode = [list(NtvUtil.decode_ntv_tab(ntvf, Sfield.ntv_to_val)) for ntvf in ntv]
    leng = max(field[6] for field in decode)
    format_fields = NtvConnector.format_field(decode, leng)    
    
    shape = []
    index = None
    for ind, (forma, field) in enumerate(zip(format_fields, decode)):
        if forma == 'primary':
            shape.append(len(field[2]))
        else:
            index = ind
    return np.array(decode[index][2]).reshape(shape)


'''a = np.arange(1,25).reshape((2,3,2,2))
js = to_json_tab(a, axes)
print(js)
nt = Sdataset.ntv(js)

print(nt.to_ntv())
print(npd.read_json(js))
print(from_json_tab(js))'''