# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: philippe@loco-labs.io

An object of the `ESObs` module is a component of an `ES.ESObservation.Observation` object

This module include the parent classes :
    
- `ESObs` : parent class of the others
- `Datation`,
- `Location`,
- `Property`,
- `Result`  

and the child classes :
    
- `ESSEtDatation`,
- `ESSEtLocation`,
- `ESSEtProperty`,
- `ESSEtResult`  

"""

#from ESElement import ESObs
from ESElement import ESElement, isESAtt, isUserAtt
from ESconstante import ES #, identity
from datetime import datetime
from ESValue import LocationValue, DatationValue, PropertyValue, ResultValue   #, ESSet
from ESSet import ESSet
import numpy as np
import copy

class ESObs(ESElement):
    """
    Parent Class of `Datation`, `Location`, `Property`, `Result`
    
    *Attributes (for @property see methods)* :
    
    - None
     
    The methods defined in this class are : 

    - `observation` (@property) Observation linked to `ESObs`
    """
    def __init__(self, pObs=None):
        ''' This method initialize the link with the `ES.ESObservation.Observation` '''
        ESElement.__init__(self)
        if (pObs != None): pObs.addComposant(self)

    @property
    def observation(self):
        ''' return the Observation linked to the `ESObs` '''
        for cont in self.pContenant :
            if cont.classES == ES.obs_classES : return cont
        return None

    def _initESSet(self, ValueClass, jObj):
        ''' creation and initialization of `ESSet` '''
        if type(jObj) == dict:
            userAtt = False
            jDat = jObj.copy()
            for k, v in jDat.items():   # si mot-clef ESobs
                if k == self.classES: 
                    jDat = v
                    userAtt = True
            for k, v in jDat.items(): # attributs
                if isESAtt(self.classES, k) or (userAtt and isUserAtt(k)): self.mAtt[k] = v
            if ValueClass.valName in list(jDat):    # si valeurs simple ou detaillee précisée
                    ESSet.__init__(self, ValueClass, jDat[ValueClass.valName]) 
            else :  ESSet.__init__(self, ValueClass, jObj)
        else :      ESSet.__init__(self, ValueClass, jObj)

class Datation(ESObs):
    """
    Parent Class of `ESSetDatation` (no attributes, no methods)
    """
    def __init__(self, pObs=None):
        ''' Initialize the 'classES' attribute '''
        ESObs.__init__(self, pObs)
        self.classES = ES.dat_classES

class Location(ESObs):
    """
    Parent Class of `ESSetLocation` (no attributes, no methods)
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.classES = ES.loc_classES

class Property(ESObs):
    """
    Parent Class of `ESSetLocation` (no attributes, no methods)
    """
    def __init__(self, pObs=None):
        ESObs.__init__(self, pObs)
        self.classES = ES.prp_classES

class Result(ESObs):
    """
    Parent Class of `ESSetResult`.
    
    *Attributes* :
    
    - error : boolean, indicate if the Result is consistent
    - axes : array of integer with value 0, 1, 2, 10, 20, 21, 120
     
    No methods defined in this class
    """
    def __init__(self, pObs=None):
        ''' initialize error (True) and axes ([])'''
        ESObs.__init__(self, pObs)
        self.classES = ES.res_classES
        self.error = True
        self.axes = []
            
class ESSetDatation(ESSet, Datation):   # !!! début ESSet
    """
    This class represent the list of DatationValues.
    
    *Attributes * : None (inherited from parent classes)
     
    The methods defined in this class are : 

    *property (getters)*

    - `vListInstant`
    - `vListSlot`

    *export*

    - `json`
    - `to_numpy`
    """
    def __init__(self, jObj = None, pObs = None):
        Datation.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.dat_valueType
        self._initESSet(DatationValue, jObj)
        self.majMeta()

    def __repr__(self):
        return '\n' + self.json(ES.mOption) + '\n'

    def analyse(self):
        ''' not implemnted'''
        pass

    def json(self, option = ES.mOption):
        '''call `ESSet.ESSet.jsonESSet` '''
        return self.jsonESSet(ES.dat_valName, option)

    def to_numpy(self, func=ES._identity):
        datList = self.vList(func)
        if type(datList[0]) == str :
            try : datetime.fromisoformat(datList[0])
            except : return np.array(datList)
            return np.array(datList, dtype=np.datetime64)
        elif type(datList[0]) == datetime : return np.array(datList, dtype=np.datetime64)
        else: return np.array(datList)

    @property
    def vListInstant(self, string=False):
        return [val.vInstant(string=string) for val in self.valueList]

    @property
    def vListSlot(self):
        return [val.vSlot() for val in self.valueList]

        
class ESSetLocation(ESSet, Location):
    """
    This class represent the list of LocationValues.
    
    *Attributes * : None (inherited from parent classes)
     
    The methods defined in this class are : 

    *property (getters)*

    - `vListCodePlus`
    - `vListPoint`
    - `vListShap`

    *export*

    - `json`
    - `to_numpy`
    """
    def __init__(self, jObj = None, pObs = None):
        Location.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.loc_valueType
        self._initESSet(LocationValue, jObj)
        self.majMeta()

    def __repr__(self): return '\n' + self.json(ES.mOption) + '\n'

    def analyse(self):
        ''' not implemnted'''
        pass

    def json(self, option = ES.mOption):       
        '''call `ESSet.ESSet.jsonESSet` '''
        return self.jsonESSet(ES.loc_valName, option)
    
    def to_numpy(self, func=ES._identity):
        return np.array(self.vList(func))
    
    @property
    def vListCodePlus(self):
        return [val.vCodePlus(self.observation.option) for val in self.valueList]

    @property
    def vListPoint(self):
        return [val.vPoint() for val in self.valueList]

    @property
    def vListShap(self):
        return [val.vShap() for val in self.valueList]

class ESSetProperty(ESSet, Property):
    """
    This class represent the list of PropertyValues.
    
    *Attributes * : None (inherited from parent classes)
     
    The methods defined in this class are : 

    *property (getters)*

    - `vListType`

    *export*

    - `json`
    - `to_numpy`
    """
    def __init__(self, jObj = None, pObs = None):
        Property.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.prp_valueType
        self._initESSet(PropertyValue, jObj)
        self.majMeta()

    def __repr__(self): return '\n' + self.json(ES.mOption) + '\n'

    def json(self, option = ES.mOption):       
        return self.jsonESSet(ES.prp_valName, option)

    def to_numpy(self, func=ES._identity):
        return np.array(self.vList(func))
    
    @property
    def vListType(self):
        return [val.vType() for val in self.valueList]

class ESSetResult(ESSet, Result):
    """
    This class represent the list of PropertyValues.
    
    *Attributes * : None (inherited from parent classes)
     
    The methods defined in this class are : 

    *property (getters)*

    - `vListType`
    - `vListIndex`
    - `maxIndex`
    - `isIndex`
    - `measureRate`
    - `nMax`
    - `dim`
    - `nInd`

    *add update manage*

    - `analyse`
    - `full`
    - `majIndex`

    *export*

    - `json`
    - `to_numpy`
    """
    def __init__(self, jObj = None, pObs = None):
        Result.__init__(self, pObs)
        self.typeES = ES.set_typeES
        self.mAtt[ES.type] = ES.res_valueType
        self._initESSet(ResultValue, jObj)
        self.majMeta()

    def __repr__(self):
        return '\n' + self.json(ES.mOption) + '\n'

    def analyse(self):
        '''
        calcul de :
            axes : list des axes
            error : indices incohérents
        '''
        idat = 0; iloc = 1; iprp = 2
        nInd = self.nInd
        self.error = min(min(val.ind[idat], val.ind[iloc], val.ind[iprp]) for val in self.valueList) == -1
        if self.error : return
        self.axes = [0,1,2]
        for i in range(3):
            if nInd[i] == 1: 
                self.axes.remove(i)
        nres = np.zeros(nInd, dtype=int)
        for val in self.valueList: nres[val.ind[0], val.ind[1], val.ind[2]] += 1
        self.error = nres.max() > 1
        if self.dim > 1 and not self.error :
            ax = []
            for i in range(3):
                nres2 = np.minimum(np.sum(nres, axis=i), 1)      
                if (np.sum(nres2, axis=0) <= 1).all() and (np.sum(nres2, axis=1) <= 1).all() : 
                    ax.append(i)
            if len(ax) == 1 :
                self.axes.append(max (((ax[0]+1)%3) * 10 + ((ax[0]+2)%3), \
                                      ((ax[0]+2)%3) * 10 + ((ax[0]+1)%3)))
                if (ax[0]+1)%3 in self.axes : self.axes.remove((ax[0]+1)%3)
                if (ax[0]+2)%3 in self.axes : self.axes.remove((ax[0]+2)%3)
            elif len(ax) > 1 : self.axes = [120]
        self._triAxe()

    @property
    def dim(self) :
        ''' integer : dimension 0, 1, 2, 3'''
        dimension = len(self.axes)                
        if self.error : dimension = -1
        return dimension

    def full(self, maj=True):
        [nPrp, nDat, nLoc, nRes] = self.observation.nValueObs
        nPrp = max(1, nPrp)
        nDat = max(1, nDat)
        nLoc = max(1, nLoc)
        resComp = np.ones((nDat, nLoc, nPrp))
        for res in self.valueList: resComp[tuple(res.ind)] = 0
        nz = np.nonzero(resComp)
        full = copy.copy(self.valueList)
        if maj :
            for t in zip(list(nz[0]), list(nz[1]), list(nz[2])) : 
                self.valueList.append(ResultValue(ind=list(t)))
            self.observation.majType(order='dlp')
            return []
        else :
            full = copy.copy(self.valueList)
            for t in zip(list(nz[0]), list(nz[1]), list(nz[2])) : full.append(ResultValue(ind=list(t)))
            return full
    
    @property 
    def isIndex(self):
        for val in self.valueList: 
            if min(val.ind) == -1 : return False
        return True

    def json(self, option = ES.mOption):
        return self.jsonESSet(ES.res_valName, option)

    def majIndex(self, nRes, nPrp, nDat, nLoc, order = 'dlp'):
        if self.maxIndex > -1 : return
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
                
    @property 
    def maxIndex(self):
        maxInd = -1
        for val in self.valueList: maxInd = max(maxInd, max(val.ind))
        return maxInd

    @property
    def measureRate(self): return self.nValue / self.nMax

    @property
    def nInd(self):
        nInd = [0,0,0]
        for i in range(3) : nInd[i] = 1 + max(val.ind[i] for val in self.valueList)
        return nInd

    @property
    def nMax(self) :
        '''integer, nombre maxi de valeurs pour être complet'''
        nInd = self.nInd
        if   len(self.axes) == 3 : return nInd[0] * nInd[1] * nInd[2]
        elif len(self.axes) == 1 : return max(nInd) 
        elif len(self.axes) == 2 : return nInd[self.axes[0]%10] * nInd[self.axes[1]%10]
        else : return 1
        
    def to_numpy(self, func=ES._identity, ind='axe', squeeze=True):
        if type(ind) == str and ind == 'flat' : return np.array(self.vList(func))
        elif type(ind) == str and (ind == 'obs' or (ind == 'axe' and max(self.axes) < 9 )) :
            [nPrp, nDat, nLoc, nRes] = self.observation.nValueObs
            nPrp = max(1, nPrp)
            nDat = max(1, nDat)
            nLoc = max(1, nLoc)
            listFull = self.full(False)
            listInd = sorted(list(zip(listFull, list(range(len(listFull))))), key= lambda z : z[0])
            fullTri, indTri = zip(*listInd)
            if func == 'index': lis = [i for i in range(len(fullTri))]
            else :              lis = [func(fullTri[i]) for i in range(len(fullTri))]
            if squeeze :    return np.array(lis).reshape(nDat, nLoc, nPrp).squeeze()
            else :          return np.array(lis).reshape(nDat, nLoc, nPrp)
        elif type(ind) == str and ind == 'axe' :
            for ax in self.axes :
                if ax > 100 : return np.array(self.vList(func))
                elif ax > 9 :
                    lis = self._fullAxe(ax)
                    [nPrp, nDat, nLoc, nRes] = self.observation.nValueObs
                    nPrp = max(1, nPrp)
                    nDat = max(1, nDat)
                    nLoc = max(1, nLoc)
                    order = [nDat, nLoc, nPrp]
                    for res in lis :
                        res.ind[ax//10] = 0
                    if func == 'index': lis = [i for i in range(len(lis))]
                    else :              lis = [func(lis[i]) for i in range(len(lis))]
                    if len(self.axes) == 2 :
                        if (ax//10+2)%3 == self.axes[0] or (ax//10+1)%3 == self.axes[1] :
                                return np.array(lis).reshape(order[(ax//10+2)%3], order[(ax//10+1)%3])
                        else:   return np.array(lis).reshape(order[(ax//10+1)%3], order[(ax//10+2)%3])
                    return np.array(lis)           
        return np.array(())
    
    @property
    def vListIndex(self):
        return [val.ind for val in self.valueList]

    def _axeCoor(self, nValAxe) :
        for ax in self.axes :
            if ax > 100 : return ax
            if ax < 9 and nValAxe == ax : return ax
            elif ax > 9 and (nValAxe == ax//10 or nValAxe == ax%10) : return ax
        return None
    
    def _triAxe(self, maj=True, fullAxes=False):
        ''' if 0 in axes, 0 is in first place'''
        if maj : axes = self.axes
        else : axes = copy.deepcopy(self.axes)
        axes.sort()
        if fullAxes: axes=[0,1,2]
        elif len(axes) == 2 and axes[0] != 0 and axes[1] > 9 : 
            (axes[0], axes[1]) = (axes[1], axes[0])
        return axes

    def _resetIndexRes(self):
        for val in self.valueList : val.ind = ES.nullInd

    def _fullAxe(self, axe):
        if not self.observation.complet :               
            ob = copy.deepcopy(self.observation)
            nr = np.array(ob.setResult.vListIndex)
            ob.full()
            lis = ob.setResult.valueList
            dellis = []
            for i in range(len(lis)):
                if (lis[i].ind[axe//10], lis[i].ind[axe%10]) not in list(zip(list(nr[:,axe//10]), list(nr[:,axe%10]))) : dellis.append(i)
            dellis.sort(reverse=True)
            for i in dellis : lis.pop(i)
        else :
            lis = copy.deepcopy(self.valueList)
        lis.sort()
        return lis
        
                    