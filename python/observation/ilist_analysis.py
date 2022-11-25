# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.ilist_analysis` module contains the `Analysis` class.
"""

# %% declarations
from copy import copy
import pprint
from collections import Counter

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
    - `Analysis.tree`
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
        self.hashi      = None
        self.matrix     = None
        self.matrix2     = None
        self.infos      = None
        self.infos2      = None
        #self.primary    = None
        self.primary2    = None
        #self.crossed    = None      # à supprimer
        self.partition  = []
    
    def getinfos2(self, keys=None):
        '''return attribute infos

         *Parameters*

        - **keys** : list or tuple (default None) - list of attributes to returned'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        if not keys:
            return self.infos2
        return [{k: v for k, v in inf.items() if k in keys} for inf in self.infos2]
    
    def getmatrix2(self, name=None):
        '''return attribute matrix or only one value of the matrix defined by two names
        
         *Parameters*

        - **name** : list or tuple (default None) - list of two fields names        
        '''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        if not name or not isinstance(name, list):
            return self.matrix2
        if name[0] in self.iobj.indexname:
            ind0 = self.iobj.indexname.index(name[0])
            if len(name) == 1:
                return self.matrix2[ind0]
            if len(name) > 1 and name[1] in self.iobj.indexname:
                return self.matrix2[ind0][self.iobj.indexname.index(name[1])]
        return None
    
    def getvarname(self):
        '''return variable Iindex name'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        return self.lvarname

    """def getprimary(self):
        '''return attribute primary'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        return self.primary"""

    def getprimary3(self):
        '''return attribute primary'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        return self.primary3

    """def getcrossed(self):
        '''return attribute crossed'''
        if self.hashi != self.iobj._hashi():
            self._actualize()
        return self.crossed"""

    def tree(self, width=5, lname=20):
        '''return a string with a tree of derived Iindex.
                
         *Parameters*

        - **lname** : integer (default 20) - length of the names        
        - **width** : integer (default 5) - length of the lines        
        '''
        #from pprint import pformat        
        if self.hashi != self.iobj._hashi():
            self._actualize()
        child = [None] * (len(self.infos2) + 1)
        for i in range(len(self.infos2)):
            parent = self.infos2[i]['parent']
            if child[parent + 1] is None:
                child[parent + 1] = []
            child[parent + 1].append(i)
        tr = self._dic_noeud(-1, child, lname)
        tre = pprint.pformat(tr, indent=0, width=width)
        tre = tre.replace('---', ' - ')
        tre = tre.replace('*', ' ')
        for c in ["'", "\"", "{", "[", "]", "}", ","]: 
            tre = tre.replace (c, "")
        return tre
    
    # %% internal methods
    def _actualize(self, forcing=False, partition=None):
        #t0=time()
        #self.matrix = self._setmatrix()
        #self.infos = self._setinfos()
        #self._setparent()
        self.matrix2 = self._setmatrix2()
        self._setinfos2()
        self._setparent2()
        self._setpartition()
        self._setinfospartition(partition)
        #self.primary = [self.infos.index(idx) for idx in self.infos if idx['cat'] == 'primary']
        self.primary2 = [idx['num'] for idx in self.infos2 if idx['cat'] == 'primary']
        infosidx = [idx for idx in self.infos2 if idx['cat'] != 'variable']
        self.primary3 = [infosidx.index(idx) for idx in infosidx if idx['cat'] == 'primary']
        #self.crossed = [idx for idx in self.primary if self.infos[idx]['typecoupl'] == 'crossed']
        self.hashi = self.iobj._hashi()
        self.lvarname = [idx['name'] for idx in self.infos2 if idx['cat'] == 'variable']
        coupledvar = [idx['name'] for idx in self.infos2 if idx['cat'] == 'coupled' 
                    and self.infos2[idx['parent']]['cat'] == 'variable']
        self.lvarname += coupledvar
        self.secondary = [idx['num'] for idx in self.infos2 if idx['cat'] == 'secondary']
        coupledsec = [idx['num'] for idx in self.infos2 if idx['cat'] == 'coupled' 
                    and self.infos2[idx['parent']]['cat'] in ('primary', 'secondary')]
        self.secondary += coupledsec
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
            infos[i]['pparent'] = -2
            #infos[i]['pparent'] = 0
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
    
    def _setmatrix2(self):
        '''set and return matrix attributes (coupling infos between each idx)'''
        lenindex = self.iobj.lenindex
        mat = [[None for i in range(lenindex)] for i in range(lenindex)]
        for i in range(lenindex):
            for j in range(i, lenindex):
                mat[i][j] = self.iobj.lindex[i].couplinginfos(self.iobj.lindex[j])
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

    def _setinfos2(self):
        '''set and return attribute 'infos'. 
        Infos is an array with infos of each index :
            - num, name, cat, typecoupl, diff, parent, pname, pparent, linkrate'''
        lenindex = self.iobj.lenindex
        self.infos2 = [{} for i in range(lenindex)]
        for i in range(lenindex):
            self.infos2[i]['parent'] = -1
            self.infos2[i]['child'] = []
            self.infos2[i]['crossed'] = []
            self.infos2[i]['num'] = i
            self.infos2[i]['name'] = self.iobj.lname[i]           
            self.infos2[i]['cat'] = 'null'
            self.infos2[i]['pparent'] = -2
            self.infos2[i] |= self.iobj.lindex[i].infos
            if self.infos2[i]['typecodec'] == 'unique':
                self.infos2[i]['pparent'] = -1
                self.infos2[i]['cat'] = 'unique'
        for i in range(lenindex):
            for j in range(i+1, lenindex):
                if self.matrix2[i][j]['typecoupl'] == 'coupled' and \
                  self.infos2[j]['parent'] == -1:
                    self.infos2[j]['parent'] = i
                    self.infos2[j]['cat'] = 'coupled'
                    self.infos2[i]['child'].append(j)
        return

    def _setinfospartition(self, partition=None):
        '''set and return attribute 'infos'. 
        Infos is an array with infos of each index :
            - num, name, cat, typecoupl, diff, parent, pname, pparent, linkrate'''
        if not partition is None and not partition in self.partition:
            raise AnalysisError('partition is not a valid partition')
        lenindex = self.iobj.lenindex
        infosp = self.infos2
        if not partition and len(self.partition) > 0:
            partition = self.partition[0]
        if partition:
            for i in partition:
                infosp[i]['cat'] = 'primary'
                infosp[i]['pparent'] = i
        for i in range(lenindex): 
            '''if infosp[i]['typecodec'] == 'unique':   #!!!
                infosp[i]['pparent'] = -1
                infosp[i]['cat'] = 'unique'
            elif not i in partition:'''
            if infosp[i]['cat'] == 'null':
                util.pparent2(i, infosp)
                if infosp[i]['pparent'] == -1 and partition:
                    infosp[i]['cat'] = 'variable'
                else:
                    infosp[i]['cat'] = 'secondary'
        for i in range(lenindex): 
            if infosp[i]['cat'] == 'coupled':
                infosp[i]['pparent'] = infosp[infosp[i]['parent']]['pparent']
            
    def _setparent2(self):
        '''set parent (Iindex with minimal diff) for each Iindex'''
        lenindex = self.iobj.lenindex
        lenself = len(self.iobj)
        for i in range(lenindex):
            mindiff = lenself
            parent = None
            infoi = self.infos2[i]
            if not infoi['cat'] in ['unique', 'coupled']:
                for j in range(lenindex):
                    matij = self.matrix2[i][j]
                    if i != j and self.infos2[j]['parent'] != i and \
                      matij['typecoupl'] in ('coupled', 'derived') and \
                      matij['diff'] < mindiff:
                        mindiff = matij['diff']
                        parent = j
                    elif i != j and matij['typecoupl'] == 'crossed' and \
                      self.infos2[j]['cat'] != 'coupled':
                        infoi['crossed'].append(j)
                if not parent is None:
                    infoi['parent'] = parent
                    #infoi['pname2'] = self.iobj.lname[parent]
                    self.infos2[parent]['child'].append(i)      
        return    

    def _setparent(self):
        '''set parent (Iindex with minimal diff) for each Iindex'''
        lenidx = self.iobj.lenidx
        lenself = len(self.iobj)
        for i in range(lenidx):
            self.infos[i]['parent'] = -1
            self.infos[i]['child'] = []
            self.infos[i]['crossed'] = []
        for i in range(lenidx):
            mindiff = lenself
            parent = -1
            infoi = self.infos[i]
            if infoi['typecodec'] != 'unique':
                for j in range(lenidx):
                    matij = self.matrix[i][j]
                    if i != j and self.infos[j]['parent'] != i and \
                      matij['typecoupl'] in ('coupled', 'derived') and \
                      matij['diff'] < mindiff:
                        mindiff = matij['diff']
                        parent = j
                    elif i != j and matij['typecoupl'] == 'crossed':
                        infoi['crossed'].append(j)
                infoi['parent'] = parent
                infoi['pname2'] = self.iobj.lname[parent]
                self.infos[parent]['child'].append(i)
        return

    def _dic_noeud(self, n, child, lname):
        if n == -1:
            lis = ['root*-*' + str(len(self.iobj))]
        else:
            name = self.infos2[n]['name'].ljust(lname)[0:lname] + '---' + \
                   str(self.infos2[n]['lencodec'])
            lis = [name.replace(' ', '*').replace("'",'*')]
        if child[n+1]:
            for ch in child[n+1]:
                if ch != n:
                    lis.append(self._dic_noeud(ch, child, lname))
        return {str(n).ljust(2,'*'): lis}
    
    def _setpartition(self):
        '''set partition (list of Iindex partitions)'''
        brother = {idx['num']:idx['crossed'] for idx in self.infos2 if idx['crossed']}
        self.partition = []
        chemin = []
        for cros in brother:
            chemin = []
            self._addchemin(chemin, cros, 1, brother)
        childroot = [idx['num'] for idx in self.infos2 
                     if idx['parent'] == -1 and idx['typecodec'] == 'complete']
        self.partition.append(childroot)
        return None
    
    def _addchemin(self, chemin, node, lchemin, brother):
        if lchemin == len(self.iobj) and node == chemin[0] and \
          max(Counter(zip(*[self.iobj.lindex[idx] for idx in chemin])).values()) == 1:
            part = sorted(chemin)
            if not part in self.partition:
                if not self.partition or len(part) > len(self.partition[0]):
                    self.partition.insert(0, part)
                else:
                    self.partition.append(part)
        if node in chemin[1:]: 
            return
        lnode = self.infos2[node]['lencodec']
        if lchemin * lnode <= len(self.iobj):
            newchemin = chemin + [node]
            for broth in brother[node]:
                self._addchemin(newchemin, broth, lchemin * lnode, brother)

class AnalysisError(Exception):
    ''' Analysis Exception'''
    # pass        