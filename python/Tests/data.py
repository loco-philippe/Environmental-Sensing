# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 21:36:10 2022

@author: a179227
"""
import datetime
from observation import Observation, Ilist

dat = 'datation'
loc = 'location'
prp = 'property'
res = 'result'

def polygon(coor): return [[[coor[0], coor[1]], [round(coor[0]+0.01, 2), coor[1]],
                            [round(coor[0]+0.01, 2), round(coor[1]+0.01, 2)],
                            [coor[0], round(coor[1]+0.01, 2)]]]

lyon       = ['lyon',        [4.83, 45.76], '69']
marseille  = ['marseille',   [5.38, 43.30], '13']
paris      = ['paris',       [2.35, 48.87], '75']
strasbourg = ['strasbourg',  [7.75, 48.59], '67']
lille      = ['lille',       [3.06, 50.63], '59']
bordeaux   = ['bordeaux',    [-0.58,44.84], '33']
nantes     = ['nantes',      [-1.55,47.22], '44'] 
toulouse   = ['toulouse',    [1.44, 43.61], '31']
clermont   = ['clermont',    [3.08, 45.78], '63']
nice       = ['nice',        [7.19, 43.71], '06']

ville      = [lyon, marseille, paris, strasbourg, lille, bordeaux, nantes, toulouse, 
              clermont, nice]
ville_nom  = [v[0] for v in ville]
ville_coor = [v[1] for v in ville]
ville_pol  = [polygon(v[1]) for v in ville]
ville_dpt  = [v[2] for v in ville]
ville_v    = [[ville_coor, ville_pol][i % 2][i] for i in range(len(ville))]
ville_nv   = [{n: d} for n,d in zip(ville_nom, ville_v)]
ville_mix  = [[ville_v, ville_nv][i % 2][i] for i in range(len(ville))]
ville_mix  = [(ville_v[::2] + ville_nv[1::2])[i] for i in [0,5,1,6,2,7,3,8,4,9]]

an         = ['an',          1, 1]
femmes     = ['femmes',      8, 3]
travail    = ['travail',     1, 5]
victoire   = ['victoire',    8, 5]
solstice   = ['solstice',    21, 6]
fetenat    = ['fetenat',     14, 7]
assomption = ['assomption',  15, 8]
toussaint  = ['toussaint',   1, 11]
armistice  = ['armistice',   11,11]
noel       = ['noel',        25,12]

date       = [an, femmes, travail, victoire, solstice, fetenat, assomption, toussaint,
              armistice, noel]

date_nom   = [d[0] for d in date]
date_inst  = [datetime.datetime(2022, d[2], d[1]) for d in date]
date_inter = [[datetime.datetime(2022, d[2], d[1]), datetime.datetime(2022, d[2], d[1]+5)] for d in date]
date_slot  = [[[datetime.datetime(2022, d[2], d[1]), datetime.datetime(2022, d[2], d[1]+1)],
              [datetime.datetime(2022, d[2], d[1]+3), datetime.datetime(2022, d[2], d[1]+4)]] for d in date]
date_v     = [[date_inst, date_inter, date_slot][i % 3][i] for i in range(len(date))]
date_nv    = [{n: d} for n,d in zip(date_nom, date_v)]
date_mix   = [[date_v, date_nv][i % 2][i] for i in range(len(date))]

pm25       = [ 'pm2.5',      {'prp': 'PM25', 'unit': 'kg/m3', 'sampling': 'instantaneous', 'domain': 'air',   'type': 'pollutant'}]
pm10       = [ 'pm10' ,      {'prp': 'PM10', 'unit': 'kg/m3', 'sampling': 'instantaneous', 'domain': 'air',   'type': 'pollutant'}]
pm01       = [ 'pm1'  ,      {'prp': 'PM01', 'unit': 'kg/m3', 'sampling': 'instantaneous', 'domain': 'air',   'type': 'pollutant'}]
tempair    = [ 'temp air',   {'prp': 'tema', 'unit': '°C',    'sampling': 'mean'         , 'domain': 'air',   'type': 'physic'   }]
tempwat    = [ 'temp water', {'prp': 'temw', 'unit': '°C',    'sampling': 'mean'         , 'domain': 'water', 'type': 'physic'   }]
pressure   = [ 'pressure',   {'prp': 'prea', 'unit': 'kPa',   'sampling': 'mean'         , 'domain': 'air',   'type': 'physic'   }]
humidity   = [ 'humidity',   {'prp': 'huma', 'unit': '%',     'sampling': 'instantaneous', 'domain': 'air',   'type': 'physic'   }]

env        = [pm25, pm10, pm01, tempair, tempwat, pressure, humidity]
env_nom    = [p[0] for p in env]
env_dic    = [p[1] for p in env]
env_type   = [{'prp': p['prp']} for p in env_dic]
env_v      = [[env_dic, env_type][i % 2][i] for i in range(len(env))]
env_nv     = [{n: d} for n,d in zip(env_nom, env_v)]
env_mix    = [[env_v, env_nv][i % 2][i] for i in range(len(env))]

def ent(n): return list(range(n))
def nom(n): return ['value' + str(i) for i in range(n)]
def dic(n): return [{'valmin': i, 'valmax': i + 2} for i in range(n)]
def lis(n): return [list(range(i % 5)) for i in range(n)]
#def mix_v(n): return [[ent, nom, dic, lis][i % 4](n)[i] for i in range(n)]
def mix_v(n): return [[ent, nom, lis][i % 3](n)[i] for i in range(n)]
def mix_nv(n): return [{'result': d} for d in mix_v(n)]
def mix_mix(n): return [[mix_v(n), mix_v(n), mix_nv(n)][i % 3][i] for i in range(n)]

def obs(obj): return Observation.Iobj({'data': obj})

print(obs([[dat, date_mix[:3]], [loc, ville_mix[1:4], 0], [prp, env_mix[0:2]], 
           [res, mix_mix(6), -1]]), end='\n')
il = Ilist.Iobj([[dat, date_mix[:3]], [loc, ville_mix[1:4], 0], [prp, env_mix[0:2]], 
           [res, mix_mix(6), -1]])
print(il, end='\n')

il.to_xarray()


