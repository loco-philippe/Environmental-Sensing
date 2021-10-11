# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: a179227
"""

from ESElement import ESObs
from ESconstante import ES
from ESComponent import LocationValue, TimeValue, ESSet, PropertyValue, ResultValue
import numpy as np

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
        self.nd = 0
        self.nl = 0
        self.np = 0
        self.measureRate = 0.0
        self.samplingRate = 0.0
        self.nEch = 0
        self.dim = 0
    
class Datation(ESObs):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.boxMin = TimeValue()
        self.boxMax = TimeValue()
        self.classES = ES.dat_classES
        
class ESSetDatation(ESSet, Datation):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs = None, jObj = None):
        Datation.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.dat_valueType
        self.initESSet(TimeValue, jObj)
        self.majMeta()
        pass

    def __repr__(self):
        return object.__repr__(self) + '\n' + self.json(True, True, True) + '\n'

    def json(self, obs_class, elt_type, res_index):
        return self.jsonESSet(ES.dat_valueName, obs_class, elt_type, res_index)

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

    def __repr__(self): return self.json(True, True, True) + '\n'

    def json(self, obs_class, elt_type, res_index):       
        return self.jsonESSet(ES.prp_valueName, obs_class, elt_type, res_index)

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

    def __repr__(self): return object.__repr__(self) + '\n' + self.json(True, True, True) + '\n'

    def json(self, obs_class, elt_type, res_index, geojson = False):
        return self.jsonESSet(ES.loc_valueName, obs_class, elt_type, False, geojson)

    def analyse(self):
        '''
        calcul de bbox
        '''
        self.boxMax = self.maxiBox()
        self.boxMin = self.miniBox()

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
        return object.__repr__(self) + '\n' + self.json(True, True, True) + '\n'

    def json(self, obs_class, elt_type, res_index):
        return self.jsonESSet(ES.res_valueName, obs_class, elt_type, res_index)

    def getMaxIndex(self):
        maxInd = -1
        for val in self.valueList: maxInd = max(maxInd, max(val.ind))
        return maxInd

    def resetIndexRes(self):
        for val in self.valueList : val.ind = [ -1, -1, -1]

    def majIndex(self, nRes, nPrp, nDat, nLoc):
        il = ida = ip = 0
        if self.getMaxIndex() > -1 : return
        if nRes == nPrp * nDat * nLoc :
            for i in range(nRes) :
                if nLoc * nPrp > 0 :
                    ida = i // (nLoc * nPrp) 
                    il = (i % (nLoc * nPrp)) // nPrp 
                    if nPrp > 0: ip = (i % (nLoc * nPrp)) % nPrp 
                self.valueList[i].ind = [ ida, il, ip ]
        elif nRes == nPrp * nDat and nRes == nPrp * nLoc:
            for i in range(nRes) :
                if nPrp > 0 :
                    idloc = i // nPrp
                    ip = i % nPrp   
                    if nRes == nPrp * nDat : ida = idloc
                    if nRes == nPrp * nLoc : il = idloc            
                self.valueList[i].ind = [ ida, il, ip ]
                #print(nRes, i, [ ida, il, ip ], self.valueList[i])

    def analyse(self):
        '''
        calcul de :
            nd, nl, np : max des indices loc, dat, prop
            nech : nombre de de couple (dat, loc) documenté
            dim : dimension 0, 1, 2
            error : indices incohérents
            sampling rate : taux de couple (dat, loc) documenté
            measure rate : taux de triplet (dat, loc, prop) documenté
        '''
        idat = 0; iloc = 1; iprp = 2
        if min(min(val.ind[idat], val.ind[iloc], val.ind[iprp]) for val in self.valueList) == -1 :
            self.dim = min(self.nValue, 2) - 1
            self.nEch = self.nValue
        else :
            self.dim = 2
            self.nd = 1 + max(val.ind[idat] for val in self.valueList)
            self.nl = 1 + max(val.ind[iloc] for val in self.valueList)
            self.np = 1 + max(val.ind[iprp] for val in self.valueList)
            nres = np.zeros((self.nd, self.nl, self.np), dtype=int)
            for val in self.valueList:
                nres[val.ind[0], val.ind[1], val.ind[2]] += 1
            self.error = nres.max() > 1
            nres2 = np.minimum(np.sum(nres, axis=2), 1)      
            self.nEch = int(np.sum(nres2))
            if np.sum(nres) < 2: self.dim = 0
            elif max(np.sum(nres2, axis=0)) == 1 : self.dim = 1
            elif max(np.sum(nres2, axis=1)) == 1 : self.dim = 1
            self.measureRate = np.sum(nres) / self.np / (nres.size/self.np)**(self.dim/2)
            self.samplingRate = self.nEch / nres2.size**(self.dim/2)

            '''if self.dim == 2:
                self.measureRate = np.sum(nres) / nres.size
                self.samplingRate = self.nEch / nres2.size
            elif self.dim == 1:
                self.measureRate = np.sum(nres) / self.np / (nres.size/self.np)**0.5
                self.samplingRate = self.nEch / nres2.size**0.5
            else :
                self.measureRate = 1.0
                self.samplingRate = 1.0'''

    '''def majIndic(self, ech, dimension, datU, locU):
        self.nEch = ech
        self.dim = dimension
        self.nDatUse = datU
        self.nLocUse = locU
        #self.mAtt[ES.res_nEch] = self.nEch
        #self.mAtt[ES.res_dim]  = self.dim'''

    '''def majIndexRes(self, nRes, nMeas, nDat, nLoc, nEch, dim):
        il = ida = ip = 0
        if self.getMaxIndex() > -1 : return
        if nRes == nMeas * nDat * nLoc and dim == 2:
            for i in range(nRes) :
                if nLoc * nMeas > 0 :
                    ida = i // (nLoc * nMeas) 
                    il = (i % (nLoc * nMeas)) // nMeas 
                    if nMeas > 0: ip = (i % (nLoc * nMeas)) % nMeas 
                self.valueList[i].ind = [ ida, il, ip ]
        elif (nRes == nMeas * nDat or nRes == nMeas * nLoc) and dim == 1:
            for i in range(nRes) :
                if nMeas > 0 :
                    idloc = i // nMeas
                    ip = i % nMeas 
                    if nRes == nMeas * nDat : ida = idloc
                    if nRes == nMeas * nLoc : il = idloc            
                self.valueList[i].ind = [ ida, il, ip ]'''

    '''def setBox(self, maxi, mini):
        self.boxMax = maxi
        self.boxMin = mini;
        #self.mAtt[ES.dat_boxMin]= self.boxMin.json(True)
        #self.mAtt[ES.dat_boxMax]= self.boxMax.json(True)'''

    '''def setBox(self, maxi, mini):
        self.boxMax = maxi
        self.boxMin = mini;
        #self.mAtt[ES.loc_boxMin]= self.boxMin.json(True)
        #self.mAtt[ES.loc_boxMax]= self.boxMax.json(True)'''

