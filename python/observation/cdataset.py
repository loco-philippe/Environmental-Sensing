# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:54:18 2023

@author: phili
"""
class Cdataset:

    def __init__(self, listidx=None, reindex=True):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        '''

        self.name     = self.__class__.__name__
        self.lindex   = []
        if listidx.__class__.__name__ in ['Dataset', 'Observation', 'Ndataset', 'Sdataset']:
            self.lindex = [copy(idx) for idx in listidx.lindex]
            return
        if not listidx:
            return
        self.lindex   = listidx
        if reindex:
            self.reindex()
        self.analysis.actualize()
        return
