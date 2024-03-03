# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 11:14:40 2024

@author: a lab in the Air
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from copy import copy

class Darray(ABC):
    ''' Representation of a one dimensional Array'''
    def __init__(self, data, ref=None, coding=None):
        if isinstance(data, Darray):
            self.data = data.data
            self.ref = data.ref
            self.coding = data.coding
            return
        self.data = np.array(data).reshape(-1)
        self.ref = ref
        self.coding = np.array(coding).reshape(-1)
        return
    
    def __repr__(self):
        '''return classname and number of value'''
        return self.__class__.__name__ + '[' + str(len(self)) + ']'
    
    def __str__(self):
        '''return json string format'''
        return 'str'

    def __eq__(self, other):
        ''' equal if values are equal'''
        return np.array_equal(self.values, other.values, equal_nan=False)

    def __len__(self):
        ''' len of values'''
        return self.len_val

    def __contains__(self, item):
        ''' item of values'''
        return item in self.values

    def __getitem__(self, ind):
        ''' return value item'''
        if isinstance(ind, tuple):
            return [copy(self.values[i]) for i in ind]
        # return self.values[ind]
        return copy(self.values[ind])       

    def __copy__(self):
        ''' Copy all the data '''
        return self.__class__(self)
    
    @staticmethod 
    def read_list(val):
        if len(val)==1:
            return Dfull(val)
        if len(val)==2:
            return Dcomplete(val[0], val[1])
    
    
    @abstractmethod
    def to_list(self):
        pass
    
    @property
    @abstractmethod
    def values(self):
        pass
    
    @property
    @abstractmethod
    def len_val(self):
        pass
    
class Dfull(Darray):    
    ''' Representation of a one dimensional Array with full representation'''
    def __init__(self, data, ref=None, coding=None):
        super().__init__(data, None, None)
    
    def to_list(self):
        return self.data.tolist()
    
    @property 
    def values(self):
        return self.data
    
    @property
    def len_val(self):
        return len(self.values)
    

class Dcomplete(Darray):    
    ''' Representation of a one dimensional Array with full representation'''
    def __init__(self, data, ref=None, coding=None):
        if coding is None:
            '''data = pd.Series(data).astype('category')
            coding = np.array(data.cat.codes)
            data = np.array(data.cat.categories)'''
            data, coding = np.unique(data, return_inverse=True)
        super().__init__(data, None, coding)
    
    def to_list(self):
        return [self.data.tolist(), self.coding.tolist()]
    
    @property 
    def values(self):
        return self.data[self.coding]
        '''categ = pd.CategoricalDtype(categories=pd.Series(self.data))
        return np.array(pd.Categorical.from_codes(codes=self.coding, dtype=categ))'''
    
    @property
    def len_val(self):
        return len(self.coding)
    