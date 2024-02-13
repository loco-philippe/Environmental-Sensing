# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 15:54:47 2024

@author: a lab in the Air
"""

import numpy as np
from cfield import Cutil
from dataset import Sdataset

a = np.arange(1,25).reshape((2,3,2,2))
leng = a.size
dim = a.ndim
period = a.shape
data = a.flatten().tolist()

coefi = leng // period[0]
coef = [coefi]

for per in period[1:]:
    coefi = coefi // per
    coef.append(coefi)

name = ['axe' +str(i) for i in range(dim)]

js = { name[i]: [list(range(period[i])), [coef[i]]] for i in range(dim)} | {'val': data}

keys = [Cutil.keysfromcoef(coe, per, leng) for coe, per in zip(coef, period)]
print(coef)
print(js)
nt = Sdataset.ntv(js)

print(nt.to_ntv())
#print(keys)