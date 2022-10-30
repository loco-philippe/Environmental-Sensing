# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.ilist_structure` module contains the `IlistStructure` class
(`observation.ilist.Ilist` methods).
"""

# %% declarations
from copy import copy
import csv
import math

from esconstante import ES
from iindex import Iindex
from util import util
#from ilist import Ilist


class Analysis:
    '''this class includes Ilist methods'''
    # %% methods
    def __init__(self, iobj):
        self.iobj = iobj
        self.hashi = None
        self.matrix = None
        self.infos = None
        self.primary = None
        #self.actualize()
    
    def actualize(self, forcing=False):
        self.matrix = self.setmatrix()
        self.infos = self.setinfos()
        self.primary = [self.infos.index(idx) for idx in self.infos if idx['cat'] == 'primary']
        #self.hashi = hash(self.iobj)
        self.hashi = self.iobj._hashi()
        #print('update'+ str(self.hashi))
        
    def setinfos(self):
        '''set and return attribute 'infos'. 
        Infos is an array with infos of each index :
            - num, name, cat, typecoupl, diff, parent, pname, pparent, linkrate'''
        lenidx = self.iobj.lenidx
        infos = [{} for i in range(lenidx)]
        for i in range(lenidx):
            infos[i]['num'] = i
            infos[i]['name'] = self.iobj.idxname[i]
            infos[i]['typecoupl'] = 'null'
            minrate, minparent = self.iobj._min_rate_parent(
                self.matrix[i], i, len(self.iobj), lenidx)
            if self.iobj.lidx[i].infos['typecodec'] == 'unique':
                infos[i]['cat'] = 'unique'
                infos[i]['typecoupl'] = 'unique'
                infos[i]['parent'] = i
            elif minrate == 0.0:
                infos[i]['cat'] = 'secondary'
                infos[i]['parent'] = minparent
            else:
                infos[i]['cat'] = 'primary'
                infos[i]['parent'] = minparent
                if minparent == i:
                    infos[i]['typecoupl'] = 'crossed'
            if minparent != i:
                infos[i]['typecoupl'] = self.matrix[i][minparent]['typecoupl']
            infos[i]['linkrate'] = round(minrate, 2)
            infos[i]['pname'] = self.iobj.idxname[infos[i]['parent']]
            infos[i]['pparent'] = 0
            infos[i] |= self.iobj.lidx[i].infos
        for i in range(lenidx):
            util.pparent(i, infos)
        return infos

    def setmatrix(self):
        '''set and return matrix attributes (coupling infos between each idx)'''
        lenidx = self.iobj.lenidx
        mat = [[None for i in range(lenidx)] for i in range(lenidx)]
        for i in range(lenidx):
            for j in range(i, lenidx):
                mat[i][j] = self.iobj.lidx[i].couplinginfos(self.iobj.lidx[j])
            for j in range(i):
                mat[i][j] = copy(mat[j][i])
                if mat[i][j]['typecoupl'] == 'derived':
                    mat[i][j]['typecoupl'] = 'derive'
                elif mat[i][j]['typecoupl'] == 'derive':
                    mat[i][j]['typecoupl'] = 'derived'
                elif mat[i][j]['typecoupl'] == 'linked':
                    mat[i][j]['typecoupl'] = 'link'
                elif mat[i][j]['typecoupl'] == 'link':
                    mat[i][j]['typecoupl'] = 'linked'
        return mat

    def getinfos(self, keys=None):
        '''return attribute infos'''
        #if self.hashi != hash(self.iobj):
        if self.hashi != self.iobj._hashi():
            self.actualize()
        if not keys:
            return self.infos
        return [{k: v for k, v in inf.items() if k in keys} for inf in self.infos]
    
    def getmatrix(self):
        '''return attribute matrix'''
        #if self.hashi != hash(self.iobj):
        if self.hashi != self.iobj._hashi():
            self.actualize()
        return self.matrix

    def getprimary(self):
        '''return attribute primary'''
        #if self.hashi != hash(self.iobj):
        if self.hashi != self.iobj._hashi():
            self.actualize()
        return self.primary
