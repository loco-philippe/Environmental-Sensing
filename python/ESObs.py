# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: a179227
"""

from ESElement import ESObs
from ESconstante import ES
from ESComponent import LocationValue, DatationValue, ESSet, PropertyValue, ResultValue #, gshape
import numpy as np

class Datation(ESObs):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.boxMin = DatationValue()
        self.boxMax = DatationValue()
        self.classES = ES.dat_classES

class Location(ESObs):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.boxMin = LocationValue()
        self.boxMax = LocationValue()
        self.classES = ES.loc_classES

class Property(ESObs):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.classES = ES.prp_classES

class Result(ESObs):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.classES = ES.res_classES
        self.error = True
        self.nInd = [0,0,0]
        self.measureRate = 0.0
        #self.samplingRate = 0.0
        #self.nEch = 0
        self.dim = -1
        self.axes = []
        self.nMax = 1
            
class ESSetDatation(ESSet, Datation):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs = None, jObj = None):
        Datation.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.dat_valueType
        self.initESSet(DatationValue, jObj)
        self.majMeta()
        pass

    @property
    def vListInstant(self):
        return [val.vInstant(self.observation.option) for val in self.valueList]

    def __repr__(self):
        return object.__repr__(self) + '\n' + self.json(ES.mOption) + '\n'

    def json(self, option):
        if option["json_dat_instant"] : dat_valName = ES.dat_valName[0]
        else : dat_valName = ES.dat_valName[1]
        return self.jsonESSet(dat_valName, option)

    def analyse(self):
        '''
        calcul de bbox
        '''
        self.boxMax = self.maxiBox()
        self.boxMin = self.miniBox()
        
class ESSetLocation(ESSet, Location):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs = None, jObj = None):
        Location.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.loc_valueType
        self.initESSet(LocationValue, jObj)
        self.majMeta()

    def __repr__(self): return object.__repr__(self) + '\n' + self.json(ES.mOption) + '\n'

    def json(self, option):       
        if option["json_loc_point"] : loc_valName = ES.loc_valName[0]
        else : loc_valName = ES.loc_valName[1]
        return self.jsonESSet(loc_valName, option)
    
    @property
    def vListPoint(self):
        return [val.vPoint(self.observation.option) for val in self.valueList]
    
    def analyse(self):
        '''
        calcul de bbox
        '''
        self.boxMax = self.maxiBox()
        self.boxMin = self.miniBox()

class ESSetProperty(ESSet, Property):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs = None, jObj = None):
        Property.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.prp_valueType
        self.initESSet(PropertyValue, jObj)
        self.majMeta()

    def __repr__(self): return self.json(ES.mOption) + '\n'

    def json(self, option):       
        if option["json_prp_type"] : prp_valName = ES.prp_valName[0]
        else : prp_valName = ES.prp_valName[1]
        return self.jsonESSet(prp_valName, option)

class ESSetResult(ESSet, Result):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs = None, jObj = None):
        Result.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.res_valueType
        self.initESSet(ResultValue, jObj)
        self.majMeta()

    def __repr__(self):
        #return object.__repr__(self) + '\n' + self.json(True, True, True) + '\n'
        return object.__repr__(self) + '\n' + self.json(ES.mOption) + '\n'

    @property
    def vListIndex(self):
        return [val.ind for val in self.valueList]
    

    def json(self, option):
        return self.jsonESSet(ES.res_valName[0], option)

    def getMaxIndex(self):
        maxInd = -1
        for val in self.valueList: maxInd = max(maxInd, max(val.ind))
        return maxInd

    def resetIndexRes(self):
        for val in self.valueList : val.ind = ES.nullInd

    def majIndex(self, nRes, nPrp, nDat, nLoc, order = 'dlp'):
        if self.getMaxIndex() > -1 : return
        n = {'d' : nDat, 'l' : nLoc, 'p' : nPrp, 'x' : -1}
        if nRes == nPrp * nDat * nLoc :
            if len(order) == 3:
                ind = {order[0] : 0, order[1] : 1, order[2] : 2}
                i = [0, 0, 0]
                n12 = n[order[1]] * n[order[2]]
                for ir in range(nRes) :
                    i[0] = ir // n12 
                    i[1] = (ir % n12) // n[order[2]] 
                    i[2] = (ir % n12) %  n[order[2]] 
                    self.valueList[ir].ind = [ i[ind['d']], i[ind['l']], i[ind['p']] ]
        elif nRes == nPrp and nDat == nLoc and nRes == nLoc :
            for ir in range(nRes) : self.valueList[ir].ind = [ir, ir, ir]
        else :
            if not 'x' in order : order = 'xp'
            n0 = n[order[0]]
            n1 = n[order[1]]
            if n0 == -1 : n0 = (nPrp + nDat + nLoc - n1) // 2
            else : n1 = (nPrp + nDat + nLoc - n0) // 2
            if nRes == n0 * n1 :
                ind = {order[0] : 0, order[1] : 1}
                i = [0, 0]
                if n1 > 0 :
                    for ir in range(nRes) :
                        i[0] = ir // n1
                        i[1] = ir %  n1
                        if not 'd' in ind.keys() : ind['d'] = ind['x']
                        if not 'l' in ind.keys() : ind['l'] = ind['x']
                        if not 'p' in ind.keys() : ind['p'] = ind['x']
                        self.valueList[ir].ind = [ i[ind['d']], i[ind['l']], i[ind['p']] ]
                
    def analyse(self):
        '''
        calcul de :
            nd, nl, np : max des indices loc, dat, prop
            dim : dimension 0, 1, 2, 3
            error : indices incohérents
            measure rate : taux de triplet (dat, loc, prop) documenté
        '''
        idat = 0; iloc = 1; iprp = 2
        self.error = min(min(val.ind[idat], val.ind[iloc], val.ind[iprp]) for val in self.valueList) == -1
        if self.error : return
        self.dim = 3
        self.axes = [0,1,2]
        self.nInd = [0,0,0]
        for i in range(3):
            self.nInd[i] = 1 + max(val.ind[i] for val in self.valueList)
            if self.nInd[i] == 1: 
                self.dim -= 1
                self.axes.remove(i)
        nres = np.zeros(self.nInd, dtype=int)
        for val in self.valueList: nres[val.ind[0], val.ind[1], val.ind[2]] += 1
        self.error = nres.max() > 1
        self.nMax = max(self.nInd)
        if self.dim > 1 and not self.error :
            ax = []
            for i in range(3):
                nres2 = np.minimum(np.sum(nres, axis=i), 1)      
                if (np.sum(nres2, axis=0) <= 1).all() and (np.sum(nres2, axis=1) <= 1).all() : 
                    ax.append(i)
            #if len(ax) == 3 : print(self.nInd)
            if len(ax) == 0 : self.nMax = self.nInd[0] * self.nInd[1] * self.nInd[2]
            elif len(ax) == 1 :
                self.axes.append(max (((ax[0]+1)%3) * 10 + ((ax[0]+2)%3), \
                                      ((ax[0]+2)%3) * 10 + ((ax[0]+1)%3)))
                if (ax[0]+1)%3 in self.axes : self.axes.remove((ax[0]+1)%3)
                if (ax[0]+2)%3 in self.axes : self.axes.remove((ax[0]+2)%3)
                self.nMax = self.nInd[ax[0]] * min (self.nInd[(ax[0]+1)%3], self.nInd[(ax[0]+2)%3])
            else : self.axes = [120]
        self.dim = len(self.axes)                
        self.measureRate = self.nValue / self.nMax
        if self.error : self.dim = -1
            