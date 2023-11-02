# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:34:02 2023

@author: a lab in the Air
"""
from time import time
from observation import Sdataset, Analysis
import pandas as pd
import ntv_pandas

itinerance_5 = pd.read_csv('test_itinerance5.csv', sep=',', low_memory=False)

t0 = time()
il = Sdataset(itinerance_5)
il.delindex(il.lname[0])
print(time()-t0)

t0 = time()
ila = il._analysis
print(time()-t0)

t0 = time()
#il = Sdataset.ntv([[1,2,3,4], [5,6,7,8], [0,0,1,1]])
print(len(il))
print(il[0])
print(il.lname)
print(ila.category)
print(time()-t0)

t0 = time()
print(ila.tree())
print(time()-t0)

t0 = time()