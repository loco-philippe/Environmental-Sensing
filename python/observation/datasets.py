# -*- coding: utf-8 -*-
"""
Created on Mon May 29 21:48:33 2023

@author: a lab in the Air
"""

from ntvdataset import Ntvdataset
from fields import Nfield, Sfield


class Ndataset(Ntvdataset):
    
    def __init__(self, listidx=None, reindex=True):
        super().__init__(listidx=listidx, reindex=reindex)
        
    @staticmethod 
    def field_class():
        return Nfield
    
class Sdataset(Ntvdataset):
    
    def __init__(self, listidx=None, reindex=True):
        super().__init__(listidx=listidx, reindex=reindex)
        
    @staticmethod 
    def field_class():
        return Sfield