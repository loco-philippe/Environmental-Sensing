# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 11:01:54 2021

@author: a179227
"""
from tabulate import tabulate
from pymongo import MongoClient, GEOSPHERE
from pprint import pprint
from ESObservation import Observation
from ESValue import LocationValue
import json
import bson
#from bson.codec_options import CodecOptions

# Requires the PyMongo package# https://api.mongodb.com/python/current
# pathClient = 'mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/test'
def clientMongo(user='ESobsUser', pwd='observation', site='esobs.gwpay.mongodb.net/test'):
    auth        = 'authSource=admin'
    replicaSet  = 'replicaSet=atlas-13vws6-shard-0'
    readPref    = 'readPreference=primary'
    appName     = 'appname=MongoDB%20Compass'
    ssl         = 'ssl=true'  
    st = 'mongodb+srv://' + user +':' + pwd + '@' + site + \
            '?' + auth + \
            '&' + replicaSet + \
            '&' + readPref + \
            '&' + appName + \
            '&' + ssl    
    return MongoClient(st)

client = clientMongo()
collec = client['test_obs']['observation']
collec.create_index([('information.geobox', GEOSPHERE)])

match = {'$match' : {'information.geobox': {'$exists': True}}}
proj  = { '$project' :{'type':'$information.typeobs', 'geobox':'$information.geobox', '_id':0}}
res = collec.aggregate([match, proj])
print(tabulate(list(res)))

polygon = LocationValue.Box((4,19,7,22)).__geo_interface__
match = {'$match' : {'information.geobox': {'$geoWithin': {'$geometry' : polygon}}}}
proj  = { '$project' :{'type':'$information.typeobs', 'geobox':'$information.geobox', '_id':0}}
print(tabulate(list(collec.aggregate([match, proj]))))

match = {'$match' : {'information.geobox': {'$geoIntersects': {'$geometry' : polygon}}}}
print(tabulate(list(collec.aggregate([match, proj]))))

point = {'type': 'Point', 'coordinates': [5.5, 20.5]}
match = {'$match' : {'information.geobox': {'$geoIntersects': {'$geometry' : point}}}}
print(tabulate(list(collec.aggregate([match, proj]))))

#point = LocationValue.Box((5.5,20.5,5.5,20.5)).__geo_interface__
#match = {'$match' : {'information.geobox': {'$geoIntersects': {'$geometry' : point}}}}
#print(tabulate(list(collec.aggregate([match, proj]))))

'''match   = {'$match' : {'propertyList.property': 'Temp'}}
proj    = { '$project' :{'type':'$information.typeobs', 'score':'$information.score', '_id':0}}
res = collec.aggregate([match, proj])

for r in res : pprint(r)
'''
'''res = collec.aggregate([match, proj])

for r in res : pprint(r)

#match2   = {'$match' : {'property.propertyList.property': {'$regex' : 'PM'}}}
match2   = {'$match' :{ '$text': { '$search' : "temp" } } }
proj2    = { '$project' :{'type':'$type',
                          #'typeobs':'$information.typeobs', 
                          'property':'$property', 
                          'location':'$location',
                          'datation':'$datation',
                          'result':'$result',
                          '_id':0}}
res2 = collec.aggregate([match2, proj2])
#r = dict(res2)
print(type(res2))
#print(type(r))
for r in res2 : 
    print(type(r))
    print(r)
    #ob = Observation(json.dumps(r))
    #print(ob.json)
'''
'''
{'information.locationBox.0' : {$gte : 5, $lt : 8}, 'information.locationBox.2' : {$lt : 7}} 
'''

'''def dumps(file, dic):
    with open(file, "wb") as b_file :   b_file.write(bson.BSON.encode(dic))

def loads(file):
    with open(file, "rb") as b_file : byt = b_file.read()
    return bson.BSON.decode(byt)

def gendicarray(name, lenarray, eltarray):
    arr = []
    for i in range(lenarray):
        arr.append([eltarray, eltarray, eltarray, eltarray, eltarray])
    return { name : arr}
'''
''' exemple

a = [[1,2,3], [4,5,6]]

by = np.array(a).tobytes()
bs = bson.BSON.encode({'a': by})

dic=bson.BSON.decode(bs)
abis = np.frombuffer(dic['a'], dtype='int32').reshape((2,3)).tolist()

obs = db.observation
res = obs.insert_one(il.bson())
obs.find_one({"_id":res.inserted_id})

'''


'''    
name = 'test'
lenarray = 100
eltarray = 1.2


import numpy as np

res = [len(np.full((5,10**i), eltarray).tobytes()) for i in range(5)]
print(res)
res = [len(bson.BSON.encode(gendicarray(name, 10**i, eltarray))) for i in range(5)]
print(res)

dic = bson.BSON.decode(bson.BSON.encode(gendicarray(name, 10, eltarray)))
'''