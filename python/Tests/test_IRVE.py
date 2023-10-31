# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:34:02 2023

@author: a lab in the Air
"""

from observation import Sdataset, Analysis
import pandas as pd
import ntv_pandas

itinerance_5 = pd.read_csv('test_itinerance5.csv', sep=',', low_memory=False)


il = Sdataset(itinerance_5)
il.delindex(il.lname[0])

#il = Sdataset.ntv([[1,2,3,4], [5,6,7,8], [0,0,1,1]])
print(len(il))
print(il[0])
print(il.lname)
print(il._analysis.category)

print(il.tree())