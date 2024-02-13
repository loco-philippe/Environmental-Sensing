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

def to_json(ndarray):
    period = ndarray.shape
    dim = ndarray.ndim

    coefi = ndarray.size // period[0]
    coef = [coefi]
    for per in period[1:]:
        coefi = coefi // per
        coef.append(coefi)
    
    return { 'axe' + str(i) : [list(range(period[i])), [coef[i]]] 
            for i in range(dim)} | {'val': ndarray.flatten().tolist()}    

def ndarray(js):
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


a = np.arange(1,25).reshape((2,3,2,2))
js = to_json(a)
print(js)
nt = Sdataset.ntv(js)

print(nt.to_ntv())
print(npd.read_json(js))
print(ndarray(js))