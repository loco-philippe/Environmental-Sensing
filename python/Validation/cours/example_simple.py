# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 10:49:19 2022

@author: philippe@loco-labs.io

objet : exemple sur l'analyse des index
points identifiés :
    - type d'index : unique, dérivé, couplé, indépendant
    - ratio de couplage : max 1 crossed, min 0 coupled ou derived
    - regroupement d'index
    - analyse de matrice de couplage
    - complémentation de données
    - génération de xarray

    
"""

import os, math
os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/ES')
from ilist import Ilist
from pprint import pprint

chemin = 'C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/validation/cours/'
file    = chemin + 'example simple.csv'
filebin = chemin + 'example simple.il'

#%% introduction
simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'skyler', 'saul'],
                             'year' : [ 2000 ,  2020,   2021  ,  2000 ]})
print(simple._dict()['coupled axes'])        # name and year are coupled (link 1 to 1)

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'skyler', 'saul'],
                             'year' : [ 2000 ,  2021,   2021  ,  2000 ]})
print(simple._dict()['derived axes'])        # year is derived from name (link 1 to n)

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'skyler', 'saul'],
                             'year' : [ 2000 ,  2000,   2021  ,  2021 ]})
print(simple._dict()['primary axes'])        # year and name are not coupled

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'skyler', 'saul'],
                             'year' : [ 2000 ,  2001,   2002  ,  2002 ]})
print(simple.couplingmatrix()[0][1])         # year and name are linked at 83%
print(simple._couplinginfo(simple.iidx[0], simple.iidx[1])) # dist_to_min = 1

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'skyler', 'saul', 'gus'],
                             'year' : [ 2000 ,  2000,   2002  ,  2002 , 2002]})
print(simple.couplingmatrix()[0][1])         # year and name are linked at 33%
print(simple._couplinginfo(simple.iidx[0], simple.iidx[1])) # dist_to_max = 1

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'skyler', 'saul'],
                             'year' : [ 2000 ,  2000,   2002  ,  2002 ]})
simple.mergeidx([0,1])                       # coupling name and year
print(simple.dimension)                      # dimension = 1

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'gus', 'saul'],
                             'year' : [ 2000 ,  2000,  2021,  2021 ]})
print(simple.dimension, simple.complete)     # it can be transformed into matrix 2x2

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'gus'],
                             'year' : [ 2000 ,  2000,  2021]})
print(simple.dimension, simple.complete)     # it can not be transformed into matrix 2x2

simple = Ilist.Iedic(dicidx={'name' : ['saul', 'gus', 'gus'],
                             'year' : [ 2000 ,  2000,  2021]}).full()
print(simple.dimension, simple.complete)     # it can be transformed into matrix 2x2
print(simple)                                # a new value is added


#%% data
annew = Ilist.Iedic({'notes'     : [14, 12, 13, 15, 17, 18]}, 
                    {'course'    : ['english', 'english', 'math', 'math', 'english', 'math'],
                     'trimester' : ['t3', 't4', 't3', 't4', 't2', 't2'],
                     'name'      : ['anne', 'anne', 'anne', 'anne','anne', 'anne'],
                     'group'     : ['gr1', 'gr1', 'gr2', 'gr2', 'gr1', 'gr2'],
                     'semester'  : ['s2', 's2', 's2', 's2', 's1', 's1'],
                     'month'     : ['sep', 'dec', 'sep', 'sep', 'apr', 'apr']})  

#%% analysis
print('\n',annew._dict(addproperty=False))  # axes analysis : three primary axes
annew.couplingmatrix('matrix.txt')      # coupling ratio between two axes :
                                        # - high coupling between trim and month (83%)
                                        # - no coupling between trim and course (0%)
# see analysis in excel file

#%% update axes
annew.mergeidx([1,5])                   # add a new coupling index (trimester + month)
print('\n', annew._dict(addproperty=False))  # axes analysis : now two primary axes 
annefull = annew.full()                 # complete data to have matrix data
annefull.to_csv()                       # export data to csv file
annew.swapindex([0,1,2,3,4,5])          # remove the new index 6

#%% export xarray
print('\n', annew.to_xarray(dimmax=2, name='dim 2', fillvalue=math.nan))   # choice to have two dimensions
print('\n', annew.to_xarray(dimmax=3, name='dim 3', fillvalue=math.nan))   # choice to have three dimensions
