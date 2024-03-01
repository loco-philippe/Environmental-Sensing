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

example =[[[1,2], 'int64'],
          [[True, False], 'bool'],
          #[['1+2j', 1], 'complex'],
          [['test1', 'test2'], 'str_'], 
          [['2022-01-01T10:05:21.0002'], 'datetime64'],
          [['2022-01-01', '2023-01-01'], 'datetime64[D]'],
          [['2022-01', '2023-01'], 'datetime64[M]'],
          [['2022', '2023'], 'datetime64[Y]'],
          [[1,2], 'timedelta64[D]'],
          [[b'abc\x09', b'abc'], 'bytes'],
          [[time(10, 2, 3)], 'object'],
          [pd.array([[1,2], [3,4]]), 'object'],
          [[{'one':1}, {'two':2}], 'object'],
          [[None], 'object'],
          [[Decimal('10.2')], 'object'],
          [[np.array([1, 2], dtype='int64'), np.array(['test1'], dtype='str_')], 'object'],
          [[Point([1,2]), Point([3,4])], 'object'],
          [[LinearRing([[0, 0], [0, 1], [1, 1]])], 'object'],
          [pd.array([pd.Series([1,2,3])]), 'object'],
          [pd.array([pd.DataFrame({'::date': ['1964-01-01', '1985-02-05'], 
                           'names::string': ['john', 'eric']})]), 'object' ],
          []]

for ex in example:
    if len(ex) == 0:
        print(to_json(np.array([])))
    else:
        print(to_json(np.array(ex[0], dtype=ex[1])))

example = [['int64[kg]', [[1, 2], [3,4]]],
           ['int', [[1, 2], [3,4]]],
           ['json', [1, 'two']],
           ['month', [1, 2]],
           ['base16', ['1F23', '236A5E']],
           ['duration', ['P3Y6M4DT12H30M5S']],
           ['uri', ['geo:13.4125,103.86673']],
           ['email', ['John Doe <jdoe@mac.example>']],
           ['ipv4', ['192.168.1.1']]
           ]
print()
for ex in example:
        print(to_json(np.array(ex[1]), typ=ex[0]))

                            