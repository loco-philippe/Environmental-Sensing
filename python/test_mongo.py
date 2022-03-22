# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 11:01:54 2021

@author: a179227
"""
from pymongo import MongoClient
from pprint import pprint
from ESObservation import Observation
import json

# Requires the PyMongo package# https://api.mongodb.com/python/current
# pathClient = 'mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/test'
user        = 'ESobsUser'
pwd         = 'observation'
site        = 'esobs.gwpay.mongodb.net/test'

auth        = 'authSource=admin'
replicaSet  = 'replicaSet=atlas-13vws6-shard-0'
readPref    = 'readPreference=primary'
appName     = 'appname=MongoDB%20Compass'
ssl         = 'ssl=true'

baseMongo   = 'test_obs'
collection  = 'observation'

st = 'mongodb+srv://' + user +':' + pwd + '@' + site + \
        '?' + auth + \
        '&' + replicaSet + \
        '&' + readPref + \
        '&' + appName + \
        '&' + ssl

client  = MongoClient(st)
collec  = client[baseMongo][collection]

match   = {'$match' : {'propertyList.property': 'Temp'}}
proj    = { '$project' :{'type':'$information.typeobs', 'score':'$information.score', '_id':0}}

res = collec.aggregate([match, proj])

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
