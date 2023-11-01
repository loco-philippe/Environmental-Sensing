# -*- coding: utf-8 -*-
"""
Created on Mon May 29 21:48:33 2023

@author: a lab in the Air
"""

from observation.dataset import Dataset
from observation.fields import Nfield, Sfield
from json_ntv import NtvConnector

class Ndataset(Dataset):
    
    field_class = Nfield
    
    """def __init__(self, listidx=None, reindex=True):
        super().__init__(listidx=listidx, reindex=reindex)"""
        
    
class Sdataset(Dataset):
    
    field_class = Sfield

    '''def __init__(self, listidx=None, reindex=True, fast=False):
        """if listidx.__class__.__name__ == 'DataFrame':
            lindex, leng = NtvConnector.connector()['DataFrameConnec'].to_listidx(listidx)
            listidx = [Sfield(field['codec'], field['name'], field['keys'], 
                              lendefault=leng, fast=fast) for field in lindex]"""
        super().__init__(listidx=listidx, reindex=reindex)
    '''    