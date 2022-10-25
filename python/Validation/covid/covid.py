# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:36:22 2022

@author: philippe@loco-labs.io

Objet : Test opendata des données quotidiennes Covid par département
Points identifiés :
    - capacité de l'objet Ilist à traiter des volumes de données importants (1 million de données indexées)
    - temps de réponse linéaires / nombre de lignes (proportionnels sur les opérations de création)
    - temps de réponses d'un facteur 10 entre données simple et données ESValue
    - complémentation des données et génération Xarray opérationnel

api : https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/

"""
import os
os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from ilist import Ilist, identity
from observation import Observation
from time import time
import csv
from ESValue import LocationValue, DatationValue, PropertyValue, ResultValue, ESValue
from test_observation import _envoi_mongo_python
import datetime
import pandas as pd

chemin = 'C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/validation/covid/'

file = chemin + 'covid-hospit-2022-04-05-19h00.csv'
t0 = time()
typef = 'ES'
cmax=20000
ESval=False

#%% test pandas
t=time()
dt = {"dep":"string","sexe":"int","hosp":"int","rea":"int","rad":"int","dc":"int"}
df = pd.read_csv(file, sep=';', dtype=dt)
tf=time()
print('pandas : ', tf-t)


#%% analyse fichier CSV
print('départ : ', t0)
with open(file, newline='') as f:
    reader = csv.reader(f, delimiter=';')
    names = next(reader)
    prp = [PropertyValue.Simple(nam, name='') for nam in names]
    iprp = [3,4,8,9]
    data = [[], [], [], []]
    res = []
    c=0
    if ESval :
        for row in reader:
            c +=1
            loc = LocationValue('dpt' + str(row[0]))
            dat = DatationValue(row[2])
            for i in iprp:
                data[0].append(dat)
                data[1].append(loc)
                data[2].append(row[1])
                data[3].append(prp[i])
                res.append(ResultValue(Ilist._cast(row[i], 'int')))
            if c == cmax : break
    else :
        for row in reader:
            c +=1
            dat = Ilist._cast(row[2], 'datetime')
            loc = row[0]
            for i in iprp:
                data[0].append(dat)
                data[1].append(loc)
                data[2].append(row[1])
                data[3].append(i)
                res.append(Ilist._cast(row[i], 'int'))
            if c == cmax : break
t1 = time()
print('délai data: ', t1 - t0) # 1s pour c= 2000, 10s pour 20 000, 93s (1,5 mn) pour 230 000 (soit 1 142 000 lignes)
print('nombre de lignes : ', len(res))

#%% création Ilist
il = Ilist.ext(res, data, 'result', ['datation', 'location', 'sexe', 'property'], fast=True)
t2 = time()
print('délai il: ', t2 - t1) # 4s pour c= 2000, 37s pour 20 000, 360s (6 mn) pour 230 000 (soit 1 142 000 lignes)
# total : 1 mn pour 100 000 enregistrements Ilist

#%% stockage Ilist
#print(il.to_obj(encoded=False,  bjson_bson=True, fast=True))
il.to_file(chemin + 'il_numeric_bson_bidon.il', bjson_bson=True, fast=True)
il.to_file(chemin + 'il_numeric_json_bidon.il', bjson_bson=False, fast=True)
ilf=il.full()
ilf.to_file(chemin + 'ilf_numeric_bson_bidon.il', bjson_bson=True, fast=True)
ilf.to_file(chemin + 'ilf_numeric_json_bidon.il', bjson_bson=False, fast=True)
t2b = time()
print('délai file: ', t2b - t2)
'''
if ESval: setidxf = [[idx for idx in il.setidx[0] if idx.vSimple().year == 2020], il.setidx[1], il.setidx[2], il.setidx[3]]
else: setidxf = [[idx for idx in il.setidx[0] if idx.year == 2020], il.setidx[1], il.setidx[2], il.setidx[3]]
il2020 = il.setfilter(setidxf, inplace=False, index=False, fast=True)
t4 = time()
print('délai il2020: ', t4 - t2) # 3s pour c= 2000, 30s pour 20 000, 120s (2 mn) pour 440 725 sur 1 142 000 lignes)

if ESval: setidxf = [[idx for idx in il.setidx[0] if idx.vSimple().year == 2021], il.setidx[1], il.setidx[2], il.setidx[3]]
else: setidxf = [[idx for idx in il.setidx[0] if idx.year == 2021], il.setidx[1], il.setidx[2], il.setidx[3]]
il2021 = il.setfilter(setidxf, inplace=False, index=False, fast=True)
t5 = time()
print('délai il2021: ', t5 - t4)  # 3s pour c= 2000, 30s pour 20 000, 140s (2,3 mn) pour 440 725 sur 1 142 000 lignes)

if ESval: setidxf = [[idx for idx in il.setidx[0] if idx.vSimple().year == 2022], il.setidx[1], il.setidx[2], il.setidx[3]]
else: setidxf = [[idx for idx in il.setidx[0] if idx.year == 2022], il.setidx[1], il.setidx[2], il.setidx[3]]
il2022 = il.setfilter(setidxf, inplace=False, index=False, fast=True)
t6 = time()
print('délai il2022: ', t6 - t5) # 3s pour c= 2000, 30s pour 20 000, 39s  pour 144 875 sur 1 142 000 lignes)

#%% stockage
js = il.to_bytes()
_envoi_mongo_python(il2020.to_bytes(encoded=False))
t7 = time()
print('délai to_bytes: ', t7 - t6) # 144k pour c=2000, 1,5 Mo pour c=20000, 20,6 Mo au total (9 Mo pour 2021)
print("size : ", len(js))
if ESval: typef = 'ES'
else : typef = 'int'
il2020.to_file(chemin + 'il2020' + typef + str(cmax) + '.il')
il2021.to_file(chemin + 'il2021' + typef + str(cmax) + '.il')
il2022.to_file(chemin + 'il2022' + typef + str(cmax) + '.il')
t8 = time()
print('délai stockage: ', t8 - t7) #

il2020 = Ilist.from_file(chemin + 'il2020' + typef + str(cmax) + '.il')
il2021 = Ilist.from_file(chemin + 'il2021' + typef + str(cmax) + '.il')
il2022 = Ilist.from_file(chemin + 'il2022' + typef + str(cmax) + '.il')
if ESval:
    il2020.setidx[0] = DatationValue.cast(il2020.setidx[0])
    il2020.setidx[1] = LocationValue.cast(il2020.setidx[1])
    il2020.setidx[3] = PropertyValue.cast(il2020.setidx[3])
    il2020.extval    = ResultValue.  cast(il2020.extval)
    il2021.setidx[0] = DatationValue.cast(il2021.setidx[0])
    il2021.setidx[1] = LocationValue.cast(il2021.setidx[1])
    il2021.setidx[3] = PropertyValue.cast(il2021.setidx[3])
    il2021.extval    = ResultValue.  cast(il2021.extval)
    il2022.setidx[0] = DatationValue.cast(il2022.setidx[0])
    il2022.setidx[1] = LocationValue.cast(il2022.setidx[1])
    il2022.setidx[3] = PropertyValue.cast(il2022.setidx[3])
    il2022.extval    = ResultValue.  cast(il2022.extval)
t9 = time()
print('délai chargement: ', t9 - t8) # 4.8s

#%% export
if ESval: fillvalue = ResultValue()
else : fillvalue = 0
ilf2020=il2020.full(fillvalue=fillvalue)
t10 = time()
print('full 2020 : ', t10 - t9) # 39s pour ajouter 1156 res à 352 600 res, 70s pour ESValue

if ESval: np2020=ilf2020.to_numpy(func=ESValue.vSimple, fast=True)
else: np2020=ilf2020.to_numpy(fast=True)
t11 = time()
print('numpy 2020 : ', t11 - t10) # 39s pour ajouter 1156 res à 352 600 res

if ESval:
    function = [ESValue.vSimple, ESValue.vName, identity, ESValue.vSimple]
    ilx=il2020.to_xarray(ifunc=function)
t12 = time()
print('xarray 2020 : ', t12 - t11) # 39s pour ajouter 1156 res à 352 600 res

if ESval:
    res = ilx.loc["2020-03-23", "dpt06", '1', "dc"]
t13 = time()
print('xarray 2020 loc : ', t13 - t12) #

if ESval:
    sort=[i for i in range(len(il2020)) if il2020.iidx[2][i] ==0]
    il2020.reorder(sort)
    il2020.swapindex([0, 1, 3])
    ob2020 = Observation.Ilist(il2020)
    ob2020.to_file(chemin + 'ob2020' + typef + str(cmax) + '.ob', bjson_bson=True)
    ob20202=Observation.from_file(chemin + 'ob2020' + typef + str(cmax) + '.ob')
t14 = time()
print('ob 2020 write-read : ', t14 - t13)

if ESval:
    obx2020 = ob2020.to_xarray(numeric=True)
t15 = time()
print('ob xarray 2020 : ', t15 - t14)

if ESval:
    ob2020f=ob2020.filter(location={'isName' : 'dpt7.'}, 
                          datation={'within':DatationValue([datetime.datetime(2020,3,19),
                                                            datetime.datetime(2020,3,22)])})
    ob2020f.plot()
t16 = time()
print('ob filter plot : ', t16 - t15)

#%% synthèse
res = [t11-t0, t1-t0, t2-t1, t4-t2, t5-t4, t6-t5, t7-t6, t8-t7, t9-t8, t10-t9,
       t11-t10, t12-t11, t13-t12, t14-t13, t15-t14, t16-t15]
print(res)

print('délai total(mn) : ', (time() - t0)/60,  time() - t0)
'''