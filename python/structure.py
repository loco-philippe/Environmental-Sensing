# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 12:00:11 2021

@author: a179227
"""
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime as dt

d1 = dt.fromisoformat('2021-05-04T12:05:00')
d2 = dt.fromisoformat('2021-05-03T10:05:00')
d3 = dt.fromisoformat('2021-05-03T12:05:00')
d4 = dt.fromisoformat('2021-05-08T12:05:00')
phenomenonTime =[d1, d2]
prop = [{"PropertyType":"PM10","unit":"mg/m3"},{"PropertyType":"PM25","unit":"mg/m3"}]
coordtxt = ["[14, 42.3]", "[16, 44.3]"]
coordinates = [[14, 42.3], [16, 44.3]]
value = "1,2,3,4,5,6,7,8"
nvalue = np.fromstring(value, sep = ',').reshape(2,2,2)
value2 = "10,20,30,40,50,60,70,80"
nvalue2 = np.fromstring(value2, sep = ',').reshape(2,2,2)
lat = np.array(coordinates)[:,0]
lon = np.array(coordinates)[:,1]
ds = xr.Dataset({"value": (["prop", "time", "loc"], nvalue)},
                coords={"lon": (["loc"], lon),
                        "lat": (["loc"], lat),
                        "time": phenomenonTime,
                        "prop": prop,
                        "loc": coordtxt})
dx = xr.DataArray(data= nvalue, 
                  dims= ["prop", "time", "loc"],
                  coords={"lon": (["loc"], lon),
                          "lat": (["loc"], lat),
                          "time": phenomenonTime,
                          "prop": prop},
                  name= "dx",
                  attrs = {"descr" : "test phiphi"})
dx.sortby(['time', 'lon'], ascending = True)
dy = xr.DataArray(data= nvalue2, 
                  dims= ["prop", "time", "loc"],
                  coords={"lon": (["loc"], lon),
                          "lat": (["loc"], lat),
                          "time": [d3, d4],
                          "prop": prop},
                  name= "dy",
                  attrs = {"descr" : "test phiphi"})
dz = xr.merge([dx, dy])
dc = dx.combine_first(dy)
seq = dc.isel(prop=0, loc=0)
poll = seq.prop.values[()]['PropertyType']