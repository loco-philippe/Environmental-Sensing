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
    '''This class analyses relationships included in a tabular object 
    (Pandas DataFrame, Ilist, Observation, list of list).
    
    The Analysis class includes the following functions:
    - identification and qualification of the relationships between Iindex,
    - generation of the global properties of the structure
    - data actualization based on structure updates
    
    *Attributes* :

    - **iobj** : Ilist or Observation associated to the Analysis object
    - **hashi** : internal Id of the iobj
    - **matrix** : square matrix with relationship properties between two fields
    - **infos** : list of characteristics (matrix synthesis)
    - **primary** : list of 'primary' fields row 
    - **secondary** : list of 'secondary' fields row 
    - **lvarname** : list of 'variable' fields name 

    The methods defined in this class are :

    - `Analysis.actualize`
    - `Analysis.getinfos`
    - `Analysis.getmatrix`
    - `Analysis.getvarname`
    - `Analysis.getsecondary`
    - `Analysis.getprimary`
    - `Analysis.getpartition`
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
        self.infos      = None
        self.primary    = None
        self.secondary  = None
        self.lvarname   = None
        self.partition  = []
    
    def actualize(self, partition=None):
        ''' update all data with new values of iobj
        
         *Parameters*

        - **partition** : list of int (default None) - partition to be used '''
        #t0=time()
        self.matrix = self._setmatrix()
        self._setinfos()
        self._setparent()
        self._setpartition()
        self._setinfospartition(partition)
        infosidx = [idx for idx in self.infos if idx['cat'] != 'variable']
        self.primary = [infosidx.index(idx) for idx in infosidx if idx['cat'] == 'primary']
        self.hashi = self.iobj._hashi()
        self.lvarname = [idx['name'] for idx in self.infos if idx['cat'] == 'variable']
        coupledvar = [idx['name'] for idx in self.infos if idx['cat'] == 'coupled' 
                    and self.infos[idx['parent']]['cat'] == 'variable']
        self.lvarname += coupledvar
        self.secondary = [idx['num'] for idx in self.infos if idx['cat'] == 'secondary']
        coupledsec = [idx['num'] for idx in self.infos if idx['cat'] == 'coupled' 
                    and self.infos[idx['parent']]['cat'] in ('primary', 'secondary')]
        self.secondary += coupledsec
        #print('update ', time()-t0, self.primary, str(self.hashi))
    
    def getinfos(self, keys=None):
        '''return attribute infos

         *Parameters*

        - **keys** : string, list or tuple (default None) - list of attributes to returned
        if 'all' or None, all attributes are returned
        if 'struct', only structural attributes are returned'''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        if keys == 'struct':
            keys = ['num', 'name', 'cat', 'child', 'crossed', 'distparent',
                    'diffdistparent', 'typecoupl', 'parent', 'pparent', 'linkrate']
        if not keys or keys == 'all':
            return self.infos
        return [{k: v for k, v in inf.items() if k in keys} for inf in self.infos]
    
    def getmatrix(self, name=None):
        '''return attribute matrix or only one value of the matrix defined by two names
        
         *Parameters*

        - **name** : list or tuple (default None) - list of two fields names        
        '''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        if not name or not isinstance(name, list):
            return self.matrix
        if name[0] in self.iobj.indexname:
            ind0 = self.iobj.indexname.index(name[0])
            if len(name) == 1:
                return self.matrix[ind0]
            if len(name) > 1 and name[1] in self.iobj.indexname:
                return self.matrix[ind0][self.iobj.indexname.index(name[1])]
        return None
    
    def getvarname(self):
        '''return variable Iindex name'''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        return self.lvarname

    def getprimary(self):
        '''return attribute primary'''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        return self.primary

    def getsecondary(self):
        '''return attribute secondary'''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        return self.secondary

    def getpartition(self):
        '''return attribute partition'''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        return self.partition

    def tree(self, width=5, lname=20):
        '''return a string with a tree of derived Iindex.
                
         *Parameters*

        - **lname** : integer (default 20) - length of the names        
        - **width** : integer (default 5) - length of the lines        
        '''
        if self.hashi != self.iobj._hashi():
            self.actualize()
        child = [None] * (len(self.infos) + 1)
        for i in range(len(self.infos)):
            parent = self.infos[i]['parent']
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
    def _setmatrix(self):
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
    
    def _setinfos(self):
        '''set and return attribute 'infos'. 
        Infos is an array with infos of each index :
            - num, name, cat, child, crossed, distparent, diffdistparent, 
            typecoupl, parent, pparent, linkrate'''
        lenindex = self.iobj.lenindex
        leniobj = len(self.iobj)
        self.infos = [{} for i in range(lenindex)]
        for i in range(lenindex):
            self.infos[i]['num'] = i
            self.infos[i]['name'] = self.iobj.lname[i]           
            self.infos[i]['cat'] = 'null'
            self.infos[i]['parent'] = -1
            self.infos[i]['distparent'] = -1
            self.infos[i]['pparent'] = -2
            self.infos[i]['diffdistparent'] = leniobj
            self.infos[i]['linkrate'] = 0
            self.infos[i]['child'] = []
            self.infos[i]['crossed'] = []
            self.infos[i] |= self.iobj.lindex[i].infos
            if self.infos[i]['typecodec'] == 'unique':
                self.infos[i]['pparent'] = -1
                self.infos[i]['cat'] = 'unique'
        for i in range(lenindex):
            for j in range(i+1, lenindex):
                if self.matrix[i][j]['typecoupl'] == 'coupled' and \
                  self.infos[j]['parent'] == -1:
                    self.infos[j]['parent'] = i
                    self.infos[j]['distparent'] = i
                    self.infos[j]['diffdistparent'] = 0
                    self.infos[j]['cat'] = 'coupled'
                    self.infos[i]['child'].append(j)
        return

    def _setinfospartition(self, partition=None):
        '''add partition data into infos attribute'''
        if not partition is None and not partition in self.partition:
            raise AnalysisError('partition is not a valid partition')
        lenindex = self.iobj.lenindex
        infosp = self.infos
        if not partition and len(self.partition) > 0:
            partition = self.partition[0]
        if partition:
            for i in partition:
                infosp[i]['cat'] = 'primary'
                infosp[i]['pparent'] = i
        for i in range(lenindex): 
            if infosp[i]['cat'] == 'null':
                util.pparent2(i, infosp)
                if infosp[i]['pparent'] == -1 and partition:
                    infosp[i]['cat'] = 'variable'
                else:
                    infosp[i]['cat'] = 'secondary'
        for i in range(lenindex): 
            if infosp[i]['cat'] == 'coupled':
                infosp[i]['pparent'] = infosp[infosp[i]['parent']]['pparent']
            
    def _setparent(self):
        '''set parent (Iindex with minimal diff) for each Iindex'''
        lenindex = self.iobj.lenindex
        leniobj = len(self.iobj)
        for i in range(lenindex):
            mindiff = leniobj
            ratemin = 1
            distparent =  None
            parent = None
            infoi = self.infos[i]
            if not infoi['cat'] in ['unique', 'coupled']:
                for j in range(lenindex):
                    matij = self.matrix[i][j]
                    if i != j and self.infos[j]['parent'] != i and \
                      matij['typecoupl'] in ('coupled', 'derived') and \
                      matij['diff'] < mindiff:
                        mindiff = matij['diff']
                        parent = j
                    elif i != j and matij['typecoupl'] == 'crossed' and \
                      self.infos[j]['cat'] != 'coupled':
                        infoi['crossed'].append(j)
                    if i != j and self.infos[j]['distparent'] != i and \
                      matij['typecoupl'] in ('coupled', 'derived', 'linked', 'crossed') and \
                      matij['rate'] < ratemin:
                        ratemin = matij['rate']
                        distparent = j
                if not parent is None:
                    infoi['parent'] = parent
                    self.infos[parent]['child'].append(i)      
                if not distparent is None:
                    infoi['distparent'] = distparent
                    infoi['diffdistparent'] = self.matrix[i][distparent]['diff']
                    infoi['linkrate'] = self.matrix[i][distparent]['rate']
        return    

    def _dic_noeud(self, n, child, lname):
        '''generate a dict with nodes data defined by 'child' '''
        if n == -1:
            #lis = ['root*-*' + str(len(self.iobj))]
            lis = ['root*(' + str(len(self.iobj)) + ')']
        else:
            #name = self.infos[n]['name'].ljust(lname)[0:lname] + '---' + \
            #       str(self.infos[n]['lencodec'])
            name = self.infos[n]['name'] + ' (' + str(self.infos[n]['lencodec']) + ')'
            lis = [name.replace(' ', '*').replace("'",'*')]
        if child[n+1]:
            for ch in child[n+1]:
                if ch != n:
                    lis.append(self._dic_noeud(ch, child, lname))
        return {str(n).ljust(2,'*'): lis}
    
    def _setpartition(self):
        '''set partition (list of Iindex partitions)'''
        brother = {idx['num']:idx['crossed'] for idx in self.infos if idx['crossed']}
        self.partition = []
        chemin = []
        for cros in brother:
            chemin = []
            self._addchemin(chemin, cros, 1, brother)
        #print('partition : ', self.partition)
        childroot = [idx['num'] for idx in self.infos 
                     if idx['parent'] == -1 and idx['typecodec'] == 'complete']
        if childroot: self.partition.append(childroot)
        return None
    
    def _addchemin(self, chemin, node, lchemin, brother):
        '''extend 'chemin' with new nodes and add it to 'partition' ''' 
        if lchemin == len(self.iobj) and node == chemin[0] and \
          max(Counter(zip(*[self.iobj.lindex[idx].keys for idx in chemin])).values()) == 1:
            part = sorted(chemin)
            if not part in self.partition:
                if not self.partition or len(part) > len(self.partition[0]):
                    self.partition.insert(0, part)
                else:
                    self.partition.append(part)
        if node in chemin[1:]: 
            return
        lnode = self.infos[node]['lencodec']
        if lchemin * lnode <= len(self.iobj):
            newchemin = chemin + [node]
            for broth in brother[node]:
                self._addchemin(newchemin, broth, lchemin * lnode, brother)

class AnalysisError(Exception):
    ''' Analysis Exception'''
    # pass        