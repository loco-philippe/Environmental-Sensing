# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:54:18 2023

@author: phili
"""
class Cdataset:

    def __init__(self, listidx=None, name=None):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        '''

        self.name     = name
        self.lindex   = [] if listidx is None else listidx
