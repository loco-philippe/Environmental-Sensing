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

#read_json({':ndarray': ['int64', [1, 2]]})

example =[[[1,2], 'int64'],
          [[True, False], 'bool'],
          [['1+2j', 1], 'complex'],
          [['test1', 'test2'], 'str_'], 
          [['2022-01-01T10:05:21.0002', '2023-01-01T10:05:21.0002'], 'datetime64'],
          [['2022-01-01', '2023-01-01'], 'datetime64[D]'],
          [['2022-01', '2023-01'], 'datetime64[M]'],
          [['2022', '2023'], 'datetime64[Y]'],
          #[[1,2], 'timedelta64[D]'],
          [[b'abc\x09', b'abc'], 'bytes'],
          [[time(10, 2, 3), time(20, 2, 3)], 'object'],
          #[pd.array([[1,2], [3,4]]), 'object'],
          [[{'one':1}, {'two':2}], 'object'],
          [[None, None], 'object'],
          [[Decimal('10.5'), Decimal('20.5')], 'object'],
          [[Point([1,2]), Point([3,4])], 'object'],
          #[[LinearRing([[0, 0], [0, 1], [1, 1]]), LinearRing([[0, 0], [0, 10], [10, 10]])], 'object'],
          [[np.array([1, 2], dtype='int64'), np.array(['test1', 'test2'], dtype='str_')], 'object'],
          #[pd.array([pd.Series([1,2,3])]), 'object'],
          [pd.array([pd.DataFrame({'::date': ['1964-01-01', '1985-02-05'], 
                           'names::string': ['john', 'eric']}),
                     pd.DataFrame({'::date': ['1984-01-01', '1995-02-05'], 
                                      'names::string': ['anna', 'erich']})]), 'object' ],
          []]

for ex in example:
    if len(ex) == 0:
        print(to_json(np.array([])))
    else:
        #for format in ['complete']:
        arr = np.array(ex[0], dtype=ex[1])
        for format in ['full', 'complete']:
            js = to_json(arr, format=format)
            print(js)
            ex_rt = read_json(js, header=False)
            print(np.array_equal(ex_rt, arr),  ex_rt, ex_rt.dtype)

example = [['int64[kg]', [[1, 2], [3,4]]],
           ['int', [[1, 2], [3,4]]],
           ['json', [1, 'two']],
           ['month', [1, 2]],
           ['base16', ['1F23', '236A5E']],
           ['duration', ['P3Y6M4DT12H30M5S', 'P3Y6M4DT12H30M']],
           ['uri', ['geo:13.4125,103.86673', 'geo:13.41,103.86']],
           ['email', ['John Doe <jdoe@mac.example>', 'Anna Doe <adoe@mac.example>']],
           ['ipv4', ['192.168.1.1', '192.168.2.5']]
           ]
print()
for ex in example:
    for format in ['full', 'complete']:
        print(to_json(np.array(ex[1]), typ=ex[0], format=format))

                            