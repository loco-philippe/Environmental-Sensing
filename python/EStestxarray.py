# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: a179227
"""

from ESObservation import Observation
from ESconstante import ES
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import folium
import geojson
import numpy as np
import json
import geojson
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, \
    asPoint, asPolygon, asMultiPoint, asMultiPolygon, shape

#ax = plt.axes(projection=ccrs.Mollweide())
#plt.show()
         
def gshape(coord):
    for tpe in ["Point", "MultiPoint", "Polygon", "MultiPolygon"]:
        try:
            s = shape(geojson.loads('{"type":"' + tpe + '","coordinates":' + coord + '}'))
        except:
            s = None
        if s != None : return s.__geo_interface__
    return None
    '''try: cl = Point(np.array(coord))
    except : 
        try : cl = MultiPoint(np.array(coord))
        except: 
            try : cl = Polygon(np.array(coord))
            except : 
                try : cl = MultiPolygon(np.array(coord))
                except : 
                    cl = None
    return cl'''

print (gshape('[0,1]'))
print (gshape('[[0,1], [0,3], [1,1], [0,1]]'))
print (gshape('[[[0,1], [0,3], [1,1], [0,1]], [[0,0.5], [0.7, 0.5], [0.7, 0], [0,0.5]]]'))
print (gshape('[[[[0,1], [0,3], [1,1], [0,1]]]]'))
text_json = '{"type":"observation",\
                  "propertyList":[{"property":"PM10",  "unit" : "ppm"}, \
                                  {"property":"PM25",  "unit" : "ppm"}], \
                  "dateTime":["2021-05-04","2021-07-04T12:05","2021-02-04T12:05"], \
                  "coordinates":[[48.87, 2.35], [45.76, 4.83], [43.3, 5.38]], \
                  "value":[5, 25, 50, 4, 20, 40, 2, 10, 20,\
                           10, 50, 100, 8, 40, 80, 4, 20, 40]}'
                  #"value":[5, 25, 50, 45, 5, 40]}')
                  #"value":[5, 25, 50, 45, 5, 40]}')
                  #"coordinates":[14.0,42.2], \
text_json = '{"type":"observation","coordinates":[[48.87, 2.35], [45.76, 4.83], [43.3, 5.38]]}'
'''ob = Observation('{"type":"observation",\
                  "dateTime":"2021-05-04T12:05:00", \
                  "coordinates":[14.0,42.2], \
                  "propertyList":{"property":"PM10", "unit" : "ppm"}, \
                  "value": 120}')
                  #"value":[45, 5, 40]}')'''


ob = Observation(text_json)
print(gshape(json.dumps(json.loads('{' + ob.element(ES.loc_classES).json(False, False, False, False)+'}')["coordinates"])))

print(ob.__geo_interface__)
print (shape(ob))
print (ob.__geo_interface__['coordinates'])

'''ob.option["json_info_type"] = False
ob.option["json_info_nval"] = False
ob.option["json_info_box"] = False
ob.option["json_info_autre"] = False
ob.option["json_obs_attrib"] = False
ob.option["json_ESobs_class"] = False
ob.option["json_res_index"] = False
ob.option["maj_index"] = False
ob.majType()
print(ob.json(), '\n')
ob.option["json_info_type"] = True
ob.option["maj_index"] = True
ob.majType()
print(ob.json(), '\n')

obx = ob.xarray()
#obx = ob.xarray().set_index(loc="point", prop = "propstr")
print(obx)
ob = Observation(text_json)
ob.plot()
'''






'''obd = dim1Dataset(ob)
    print(obd)
    for data in obd : 
        if 'time' in obd[data].coords:  obd[data].sortby(['time']).plot.line(x = 'time', label = data)
    plt.ylabel("observation value")
    plt.legend()
    plt.show()   
    for data in obd : obd[data].plot.line(x = 'point', label = data)
    plt.ylabel("observation value")
    plt.legend()
    plt.show()'''
#print(obd)
#obd["PM25"].set_index(loc="lon").sortby(["loc","time"]).plot(size=5)

'''
from shapely.geometry import shape, Point, Polygon
pol2 = Polygon([[0, 0], [1, 1], [1, 0], [0, 0]])
pol2 = Polygon([[0, 0], [1, 1], [1, 0], [0, 0]], [[[0.5, 0.5], [0.8, 0.8], [0.8, 0.5], [0.5, 0.5]]])
data = {"type": "Polygon", "coordinates": [[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]], [[0.5, 0.5], [0.5, 0.8], [0.8, 0.8], [0.5, 0.5]]]}
data = {"type": "multiPolygon", "coordinates": [[[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]], [[0.5, 0.5], [0.5, 0.8], [0.8, 0.8], [0.5, 0.5]]]]}
data = {"type": "multiPolygon", "coordinates": [[[[0.0, 0.0], [0.0, -1.0], [-1.0, -1.0], [0.0, 0.0]]], [[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]], [[0.5, 0.5], [0.5, 0.8], [0.8, 0.8], [0.5, 0.5]]]]}
geom = shape(data)
geom
geom[0]
geom[1]

utilisation de geopandas
'''
