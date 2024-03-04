# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 09:46:05 2024

@author: a lab in the Air
"""
from decimal import Decimal
import numpy as np
from datetime import datetime, date, time
from pprint import pprint
from json_ntv import Ntv
import pandas as pd
from shapely.geometry import Point, LinearRing
import ntv_pandas as npd
from numpy_ntv_connector import read_json, read_json_tab, to_json, to_json_tab
from data_array import Darray

example =[
    [1, 2],
    [[1, 2], [0, 1]],
    [[10, 20], [1, 2]],
    [[[10, 20], [1, 2]], [0, 1]]
]

for ex in example:
    da = Darray.read_list(ex)
    print(type(da), len(da))
    print(da.data, da.ref, da.coding)
    print(da.values)
