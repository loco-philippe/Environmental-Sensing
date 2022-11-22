# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.ilist_analysis` module contains the `Analysis` class.
"""

# %% declarations
from copy import copy

from util import util


class Analysis:
    '''this class analyses relationships included in a tabular object 
    (Pandas DataFrame, Ilist, Observation, list of list).
    
    *Attributes* :

    - **iobj** : Ilist or Observation associated to the Analysis object
    - **hashi** : internal Id of the iobj
    - **matrix** : square matrix with relationship properties between two fields
    - **infos** : list of characteristics (matrix synthesis)
    - **primary** : list of 'primary' fields row 
    - **crossed** : list of 'crossed' fields row 

    The methods defined in this class are :

    - `Analysis.getinfos`
    - `Analysis.getmatrix`
    - `Analysis.getprimary`
    - `Analysis.getcrossed`
    '''
    # %% methods
    def __init__(self, iobj):
        '''Analysis constructor.

         *Parameters*

        - **iobj** : object - tabular object (Pandas DataFrame, Ilist, Observation, 
        list of list)
        
        Note: The Analysis data can be update only if tabular object is Ilist or 
        Observation.
        '''
        if iobj.__class__.__name__ in ('Ilist', 'Observation'): 
            self.iobj = iobj
        else: 
            from ilist import Ilist
            self.iobj = Ilist.obj(iobj)
        self.hashi   = None
        self.matrix  = None
        self.infos   = None
        self.primary = None
        self.crossed = None
    
    def getinfos(self, keys=None):
        '''return attribute infos

         *Parameters*

        - **keys** : list or tuple (default None) - list of attributes to returned'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        if not keys:
            return self.infos
        return [{k: v for k, v in inf.items() if k in keys} for inf in self.infos]
    
    def getmatrix(self, name=None):
        '''return attribute matrix or only one value of the matrix defined by two names
        
         *Parameters*

        - **name** : list or tuple (default None) - list of two fields names        
        '''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        if not name or not isinstance(name, list):
            return self.matrix
        if name[0] in self.iobj.idxname:
            ind0 = self.iobj.idxname.index(name[0])
            if len(name) == 1:
                return self.matrix[ind0]
            if len(name) > 1 and name[1] in self.iobj.idxname:
                return self.matrix[ind0][self.iobj.idxname.index(name[1])]
        return None
    
    def getprimary(self):
        '''return attribute primary'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        return self.primary

    def getcrossed(self):
        '''return attribute crossed'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        return self.crossed

    # %% internal methods
    def _actualize(self, forcing=False):
        #t0=time()
        self.matrix = self._setmatrix()
        self.infos = self._setinfos()
        self.primary = [self.infos.index(idx) for idx in self.infos if idx['cat'] == 'primary']
        self.crossed = [idx for idx in self.primary if self.infos[idx]['typecoupl'] == 'crossed']
        self.hashi = self.iobj._hashi()
        #print('update ', time()-t0, self.primary, str(self.hashi))

    def _setinfos(self):
        '''set and return attribute 'infos'. 
        Infos is an array with infos of each index :
            - num, name, cat, typecoupl, diff, parent, pname, pparent, linkrate'''
        lenidx = self.iobj.lenidx
        infos = [{} for i in range(lenidx)]
        for i in range(lenidx):
            infos[i]['num'] = i
            infos[i]['name'] = self.iobj.idxname[i]
            infos[i]['typecoupl'] = 'null'
            minrate, minparent = Analysis._min_rate_parent(
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

    def _setmatrix(self):
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
    
    @staticmethod
    def _min_rate_parent(mati, ind, lenself, lenidx):
        '''return minrate and minparent for the Index define by ind'''
        minrate = 1.00
        mindiff = lenself
        disttomin = None
        minparent = ind
        for j in range(lenidx):
            if mati[j]['typecoupl'] == 'derived':
                minrate = 0.00
                if mati[j]['diff'] < mindiff:
                    mindiff = mati[j]['diff']
                    minparent = j
            elif mati[j]['typecoupl'] == 'linked' and minrate > 0.0:
                if not disttomin or mati[j]['disttomin'] < disttomin:
                    disttomin = mati[j]['disttomin']
                    minrate = mati[j]['rate']
                    minparent = j
            if j < ind:
                if mati[j]['typecoupl'] == 'coupled':
                    minrate = 0.00
                    minparent = j
                    break
                if mati[j]['typecoupl'] == 'crossed' and minrate > 0.0:
                    if not disttomin or mati[j]['disttomin'] < disttomin:
                        disttomin = mati[j]['disttomin']
                        minrate = mati[j]['rate']
                        minparent = j
        return (minrate, minparent)

