# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 21:36:10 2022

@author: a179227
"""
import datetime
from observation import Observation as Obs, Ilist
from pprint import pprint

# %% fonctions


def polygon(coor, l=0.1): return [[[coor[0]-l, coor[1]-l/2], [round(coor[0]+l, 2), coor[1]-l/2],
                                   [round(coor[0]+l, 2),
                                    round(coor[1]+l/2, 2)],
                                   [coor[0]-l, round(coor[1]+l/2, 2)]]]


def date_inst(dj=0, h=0, m=0, s=0): return [datetime.datetime(
    2022, d[2], min(30, d[1]+dj), h, m, s) for d in date]


def date_inter(dj=0, h=0, m=0, s=0):
    return [[d1, d2] for d1, d2 in zip(date_inst(dj, h, m, s), date_inst(dj+2, h, m, s))]


def date_slot(dj=0, h=0, m=0, s=0):
    return [[i1, i2] for i1, i2 in zip(date_inter(0, h, m, s), date_inter(dj+3, h, m, s))]


def ent(n):
    return list(range(n))


def nom(n, name='value'):
    return [name + str(i) for i in range(n)]


def dic(n):
    return [{'valmin': i, 'valmax': i + 2} for i in range(n)]


def lis(n):
    return [list(range(i % 5)) for i in range(n)]


def mix_v(n):
    return [[ent, nom, lis][i % 3](n)[i] for i in range(n)]


def mix_nv(n):
    return [{'resul': d} for d in mix_v(n)]


def mix_mix(n): return [[mix_v(n), mix_v(n), mix_nv(n)]
                        [i % 3][i] for i in range(n)]


def param_val(typeval, date='2022-10-20'):
    return {'date': date, 'project': 'dataref', 'type': typeval, 'context': {'version': 'v0', 'origin': 'data.py'}}


# %% villes
lyon = ['lyon',             [4.83, 45.76], '69']
marseille = ['marseille',   [5.38, 43.30], '13']
paris = ['paris',           [2.35, 48.87], '75']
strasbourg = ['strasbourg', [7.75, 48.59], '67']
lille = ['lille',           [3.06, 50.63], '59']
bordeaux = ['bordeaux',     [-0.58, 44.84], '33']
nantes = ['nantes',         [-1.55, 47.22], '44']
toulouse = ['toulouse',     [1.44, 43.61], '31']
clermont = ['clermont',     [3.08, 45.78], '63']
nice = ['nice',             [7.19, 43.71], '06']

ville = [nice, marseille, toulouse, bordeaux, nantes, paris, lille, strasbourg,
         lyon, clermont]
ville_nom = [v[0] for v in ville]
ville_coor = [v[1] for v in ville]
ville_pol = [polygon(v[1]) for v in ville]
ville_dpt = [v[2] for v in ville]
ville_v = [[ville_coor, ville_pol][i % 2][i] for i in range(len(ville))]
ville_nv = [{n: d} for n, d in zip(ville_nom, ville_v)]
ville_mix = [[ville_v, ville_nv][i % 2][i] for i in range(len(ville))]

# %% dates
an = ['an',          1, 1]
femmes = ['femmes',      8, 3]
travail = ['travail',     1, 5]
victoire = ['victoire',    8, 5]
solstice = ['solstice',    21, 6]
fetenat = ['fetenat',     14, 7]
assomption = ['assomption',  15, 8]
toussaint = ['toussaint',   1, 11]
armistice = ['armistice',   11, 11]
noel = ['noel',        25, 12]

date = [an, femmes, travail, victoire, solstice, fetenat, assomption, toussaint,
        armistice, noel]
date_nom = [d[0] for d in date]
date_jour = [d[1] for d in date]
date_mois = [d[2] for d in date]
date_v = [[date_inst(), date_inter(), date_slot()][i % 3][i]
          for i in range(len(date))]
date_nv = [{n: d} for n, d in zip(date_nom, date_v)]
date_mix = [[date_v, date_nv][i % 2][i] for i in range(len(date))]

# %% propriétés
pm25 = ['pm2.5',        {'prp': 'PM25', 'unit': 'kg/m3',
                         'sampling': 'instantaneous', 'domain': 'air',   'type': 'pollutant'}]
pm10 = ['pm10',         {'prp': 'PM10', 'unit': 'kg/m3',
                         'sampling': 'instantaneous', 'domain': 'air',   'type': 'pollutant'}]
pm01 = ['pm1',          {'prp': 'PM01', 'unit': 'kg/m3',
                         'sampling': 'instantaneous', 'domain': 'air',   'type': 'pollutant'}]
tempair = ['temp air',  {'prp': 'tema', 'unit': '°C',
                         'sampling': 'mean', 'domain': 'air',   'type': 'physic'}]
tempwat = ['temp water', {'prp': 'temw', 'unit': '°C',
                          'sampling': 'mean', 'domain': 'water', 'type': 'physic'}]
pressure = ['pressure', {'prp': 'prea', 'unit': 'kPa',
                         'sampling': 'mean', 'domain': 'air',   'type': 'physic'}]
humidity = ['humidity', {'prp': 'huma', 'unit': '%',
                         'sampling': 'instantaneous', 'domain': 'air',   'type': 'physic'}]

env = [pm25, pm10, pm01, tempair, tempwat, pressure, humidity]
env_nom = [p[0] for p in env]
env_dic = [p[1] for p in env]
env_type = [{'prp': p['prp']} for p in env_dic]
env_v = [[env_dic, env_type][i % 2][i] for i in range(len(env))]
env_nv = [{n: d} for n, d in zip(env_nom, env_v)]
env_mix = [[env_v, env_nv][i % 2][i] for i in range(len(env))]

# %% signalement
intensite = ['très faible', 'faible', 'moyenne', 'élevée', 'très élevée']
nuisance = ['odeur air', 'tubidité eau', 'fumée', 'bruit']

# %% Observation :
dat = 'datation'
loc = 'location'
prp = 'property'
res = 'result'

def ob_mixte_2(dl=7, prop=4):
    return Obs([[dat,           date_mix[:dl % 10 + 1]],
                [loc,           ville_mix[:dl % 10 + 1], 0],
                [prp,           env_mix[:prop % 7 + 1]],
                [res,           mix_mix((dl % 10 + 1) * (prop % 7 + 1)), -1],
                ['mois',        date_mois[:dl % 10 + 1], 0],
                ['ville',       ville_nom[:dl % 10 + 1], 0],
                ['structure',   ['mixte']]],
               name='test1', param=param_val('dim2')).setcanonorder().sort()


def ob_mesure(res=None, jour=1, mois=1, lieu=0, prop=0):
    return Obs([[prp, [env_v[prop % 7]]],
                [dat, [datetime.datetime(2022, 1 + mois % 12, 1 + jour % 28)]],
                [loc, [ville_nv[lieu % 10]]],
                ['result', [res]],
                ['ville', [ville_nom[lieu % 10]]],
                ['jour', [1 + jour % 28]],
                ['mois', [1 + mois % 12]],
                ['structure', ['mesure']]],
               name='mesure' + str(jour + mois * 10),
               param=param_val('dim3')).setcanonorder().sort()


def ob_fixe(dj=0):
    return Obs([[prp, env_v[0:3]],
                [dat, [date_inst(dj=dj, h=i)[0] for i in range(24)]],
                [loc, [ville_nv[1]]],
                [res, [10+.1*i for i in range(24)] + [20+.1*i for i in range(24)] +
                    [30+.1*i for i in range(24)], -1],
                ['heure', list(range(24)), 1],
                ['mois', [date_mois[0]]],
                ['structure', ['fixe']]],
               name='mesures horaires station fixe 3 polluants-' + str(dj),
               param=param_val('dim2')).setcanonorder().sort()


def ob_mob_1(d=0):
    return Obs([[prp, [env_v[0]]],
                [dat, [date_inst(dj=i, h=12)[d] for i in range(10)]],
                [loc, ville_mix, 1],
                ['ville', ville_nom, 2],
                [res, [11+.1*i for i in range(10)], -1],
                ['jour', list(range(1, 11)), 1],
                ['mois', [date_mois[0]]],
                ['structure', ['mobile']]],
               name='mesures mobiles, 1 polluant-' + str(d),
               param=param_val('dim1')).setcanonorder().sort()


def ob_mobile(d=0):
    return Obs([[prp, env_v[0:2]],
                [dat, [date_inst(dj=i, h=12)[d] for i in range(10)]],
                [loc, ville_mix, 1],
                ['ville', ville_nom, 2],
                [res, [11+.1*i for i in range(10)] +
                 [21+.1*i for i in range(10)], -1],
                ['jour', list(range(1, 11)), 1],
                ['mois', [date_mois[0]]],
                ['structure', ['mobile']]],
               name='mesures mobiles, 2 polluants-' + str(d),
               param=param_val('dim2')).setcanonorder().sort()


def ob_multi(dj=0):
    return Obs([[prp, env_v[0:2]],
                [dat, [date_inst(dj=dj, h=i)[0] for i in range(10)]],
                [loc, ville_nv[:5]],
                ['ville', ville_nom[:5], 2],
                [res, [10+.1*i for i in range(50)] +
                 [20+.1*i for i in range(50)], -1],
                ['heure', list(range(10)), 1],
                ['mois', [date_mois[0]]],
                ['structure', ['multi']]],
               name='mesures horaires multi-stations, 2 polluants' + str(dj),
               param=param_val('dim3')).setcanonorder().sort()


def ob_signal(jour=1, mois=1, lieu=0, nuis=0, intens=0):
    return Obs([['nuisance', [nuisance[nuis % 4]]],
                [dat, [datetime.datetime(2022, mois, jour)]],
                [loc, [ville_nv[lieu]]],
                ['intensite', [intensite[intens % 5]], -1],
                ['ville', [ville_nom[lieu]], 2],
                ['jour', [jour], 1],
                ['mois', [mois]],
                ['structure', ['signal']]],
               name='signalement' + str(jour+mois*10),
               param=param_val('dim3')).setcanonorder().sort()

# %% Exemples :

def exemples():
    # mesure mixte :
    pprint(ob_mixte_2().json())
    print(ob_mixte_2(3, 3).view(lenres=30, width=20))
    
    # mesure unitaire :
    pprint(ob_mesure().json())
    print(ob_mesure(2).view(lenres=30, width=20))
    
    # mesures horaires station fixe, 3 polluants :
    pprint(ob_fixe().json())
    print(ob_fixe(2).view(lenres=30, width=20))
    
    # mesures mobile, 1 polluants :
    pprint(ob_mob_1().json())
    print(ob_mob_1(1).view(width=20))
    m = ob_mob_1(1).choropleth()
    m.save('choro.html')
    
    # mesures mobile, 2 polluants :
    pprint(ob_mobile().json())
    print(ob_mobile(1).view(width=20))
    
    # mesure horaires multi-stations, 2 polluants :
    pprint(ob_multi().json())
    print(ob_multi(2).view(lenres=30, width=20))
    
    # signalement :
    pprint(ob_signal().json())
    print(ob_signal(2).view(lenres=30, width=20))

# %% principal

exemples()

# jeu de tests
liste_obs_mixte = []
for i in range(20):
    liste_obs_mixte += [ob_mixte_2(i, i)]

liste_obs_tests = []
for i in range(10):
    liste_obs_tests += [ob_mesure(res=i, jour=i, mois=1, lieu=0, prop=0)]
    liste_obs_tests += [ob_mesure(res=10+i, jour=i, mois=1, lieu=i+1, prop=1)]
    liste_obs_tests += [ob_mesure(res=100+i, jour=i, mois=1, lieu=i+1, prop=i)]


print(len(liste_obs_mixte), len(liste_obs_tests))