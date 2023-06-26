# -*- coding: utf-8 -*-
"""
Created on Sun May 28 19:34:03 2023

@author: a lab in the Air
"""
from observation.ntvfield import Ntvfield
from json_ntv import Ntv, NtvSingle
import json
    
class Nfield(Ntvfield):
    ''' Nfield is a child class of NtvField where values are NTV objects

    The methods defined in this class are conversion methods:
    
    *converting external value to internal value:*
    
    - `Nfield.l_to_i`
    - `Nfield.s_to_i`

    *converting internal value to external value:*
    
    - `Nfield.l_to_e`
    - `Nfield.s_to_e`

    *converting internal value / NTV value:*
    
    - `Nfield.i_to_n`
    - `Nfield.n_to_i`

    *extract the name of the value:*

    - `Nfield.i_to_name`
    '''
    def __init__(self, codec=None, name=None, keys=None,
                 lendefault=0, reindex=False, fast=False):
        super().__init__(codec=codec, name=name, keys=keys,
                     lendefault=lendefault, reindex=reindex, fast=fast)

    @staticmethod
    def l_to_i(lis, fast=False):
        ''' converting a list of external values to a list of internal values
        
        *Parameters*

        - **fast**: boolean (default False) - list is created with a list of json values 
        without control'''
        if fast:
            return [NtvSingle(val, fast=True) for val in lis]
        return [Ntv.from_obj(val) for val in lis]

    @staticmethod
    def s_to_i(val, fast=False):
        '''converting an external value to an internal value

        *Parameters*

        - **fast**: boolean (default False) - list is created with a list of json values 
        without control'''
        if fast:
            return NtvSingle(val, fast=True)        
        return Ntv.from_obj(val)

    @staticmethod
    def n_to_i(ntv):
        ''' converting a NTV value to an internal value'''
        return ntv

    @staticmethod
    def l_to_e(lis, fast=False):
        ''' converting a list of internal values to a list of external values'''
        return [ntv.to_obj() for ntv in lis]    

    @staticmethod
    def s_to_e(val, fast=False):
        '''converting an internal value to an external value'''
        return val.to_obj()

    @staticmethod
    def i_to_n(val):
        ''' converting an internal value to a NTV value'''
        return val

    @staticmethod
    def i_to_name(val):
        ''' return the name of the internal value'''
        return val.name   
    
class Sfield(Ntvfield):
    ''' Sfield is a child class of NtvField where inner and outer values are same

    The methods defined in this class are conversion methods:
    
    *converting external value to internal value:*
    
    - `Nfield.l_to_i`
    - `Nfield.s_to_i`

    *converting internal value to external value:*
    
    - `Nfield.l_to_e`
    - `Nfield.s_to_e`

    *converting internal value / NTV value:*
    
    - `Nfield.i_to_n`
    - `Nfield.n_to_i`

    *extract the name of the value:*

    - `Nfield.i_to_name`
    '''    
    def __init__(self, codec=None, name=None, keys=None,
                 lendefault=0, reindex=False, fast=False):
        super().__init__(codec=codec, name=name, keys=keys,
                     lendefault=lendefault, reindex=reindex, fast=fast)
        
    @staticmethod
    def l_to_i(lis, fast=False):
        ''' converting a list of external values to a list of internal values'''
        if fast:
            return lis
        return [Sfield.s_to_i(val) for val in lis]
    
    @staticmethod
    def s_to_i(val, fast=False):
        '''converting an external value to an internal value'''
        if fast:
            return val
        if isinstance(val, list):
            return Sfield._tupled(val)
        if isinstance(val, dict):
            return json.dumps(val)
        return val    
    
    @staticmethod
    def n_to_i(ntv_lis):
        ''' converting a NTV value to an internal value'''
        return [ntv.val for ntv in ntv_lis]
    
    @staticmethod
    def l_to_e(lis, fast=False):
        ''' converting a list of internal values to a list of external values'''
        if fast:
            return lis
        return [Sfield.s_to_e(val) for val in lis]
    
    @staticmethod
    def s_to_e(val, fast=False):
        '''converting an internal value to an external value'''
        if fast:
            return val
        if isinstance(val, tuple):
            return Sfield._listed(val)
        if isinstance(val, str) and len(val) > 0 and val[0] == '{':
            return json.loads(val)
        return val
    
    @staticmethod
    def i_to_n(val):
        ''' converting an internal value to a NTV value'''
        return Ntv.obj(val)

    @staticmethod
    def i_to_name(val):
        ''' return the name of the internal value'''
        return ''
    
    @staticmethod
    def _tupled(lis):
        '''transform a list of list in a tuple of tuple'''
        return tuple([val if not isinstance(val, list) else Sfield._tupled(val) for val in lis])

    @staticmethod
    def _listed(lis):
        '''transform a tuple of tuple in a list of list'''
        return [val if not isinstance(val, tuple) else Sfield._listed(val) for val in lis]