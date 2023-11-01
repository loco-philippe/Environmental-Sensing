# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 2023

@author: philippe@loco-labs.io

The `python.observation.dataset__analysis` module contains the `DatasetAnalysis` class
(`python.observation.dataset.Dataset` methods).
"""

# %% declarations
import csv
import math
import json

from json_ntv.ntv import NtvList, NtvJsonEncoder
from observation.field import Field
from observation.util import util
from tab_analysis import AnaDataset, Util

class DatasetAnalysis:
    '''This class is the interface class with the tab_analysis module.'''
    
    @property 
    def _analysis(self):
        return AnaDataset(self.to_analysis(True))         

    @property
    def lvarname(self):
        ''' list of variable Field name'''
        return Util.view(self._analysis.variable, mode='id')
    
    @property
    def anafields(self):
        ''' list of AnaField'''
        return self._analysis.fields
    
    @property 
    def partitions(self):
        return self._analysis.partitions('index')         

    @property 
    def dimension(self):
        return self._analysis.dimension    
    
    @property
    def lvarname(self):
        ''' list of variable Field name'''
        return Util.view(self._analysis.variable, mode='id')
    
    def tree(self, mode='derived', width=5, lname=20, string=True):
        '''return a string with a tree of derived Field.

         *Parameters*

        - **lname** : integer (default 20) - length of the names        
        - **width** : integer (default 5) - length of the lines        
        - **string** : boolean (default True) - if True return str else return dict
        - **mode** : string (default 'derived') - kind of tree :
            'derived' : derived tree
            'distance': min distance tree
        '''
        return self._analysis.tree(mode=mode, width=width, lname=lname, string=string)
    
    def indicator(self, fullsize=None, size=None):
        '''generate size indicators: ol (object lightness), ul (unicity level), 
        gain (sizegain)

        *Parameters*

        - **fullsize** : int (default none) - size with full codec
        - **size** : int (default none) - size with existing codec

        *Returns* : dict'''
        if not fullsize:
            fullsize = len(self.to_obj(encoded=True, modecodec='full'))
        if not size:
            size = len(self.to_obj(encoded=True))
        return self._analysis.indicator(fullsize, size)

