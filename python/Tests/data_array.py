# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 11:14:40 2024

@author: a lab in the Air
"""

import numpy as np
from abc import ABC, abstractmethod

class Darray(ABC):
    ''' Representation of a one dimensional Array'''
    def __init__(self, data, ref=None, coding=None):
        if isinstance(data, Darray):
            self.data = data.data
            self.ref = data.ref
            self.coding = data.coding
            return
        self.data = np.array(data)
        self.ref = ref
        self.coding = np.array(coding)
        return
    
    def __repr__(self):
        '''return classname and number of value'''
        return self.__class__.__name__ + '[' + str(len(self)) + ']'
    
    def __str__(self):
        '''return json string format'''
        if len(self._codec) == 1:
            return self.to_json()

    def __eq__(self, other):
        ''' equal if class and values are equal'''
        return self.values == other.values

    def __len__(self):
        ''' len of values'''
        return self.len_val

    def __contains__(self, item):
        ''' item of values'''
        return item in self.values

    def __getitem__(self, ind):
        ''' return value item (value conversion)'''
        if isinstance(ind, tuple):
            return [copy(self.values[i]) for i in ind]
        # return self.values[ind]
        return copy(self.values[ind])       

    def __copy__(self):
        ''' Copy all the data '''
        return self.__class__(self)
    
    @abstractmethod
    def to_json(self):
        pass
    
    @abstractmethod
    def values(self):
        pass
    
    @abstractmethod
    def len_val(self):
        pass
    
def Dfull(Darray):    
    ''' Representation of a one dimensional Array with full representation'''
    def __init__(self, data):
        super().__init__(data)