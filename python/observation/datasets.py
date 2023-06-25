# -*- coding: utf-8 -*-
"""
Created on Mon May 29 21:48:33 2023

@author: a lab in the Air
"""

from observation.ntvdataset import Ntvdataset
from observation.fields import Nfield, Sfield


class Ndataset(Ntvdataset):
    
    field_class = Nfield
    
    def __init__(self, listidx=None, reindex=True):
        super().__init__(listidx=listidx, reindex=reindex)
        
    
class Sdataset(Ntvdataset):
    
    field_class = Sfield

    def __init__(self, listidx=None, reindex=True):
        super().__init__(listidx=listidx, reindex=reindex)
        