# -*- coding: utf-8 -*-
"""
Created on Sun May 28 19:34:03 2023

@author: a lab in the Air
"""
from observation.field import Field
from json_ntv import Ntv, NtvSingle, NtvJsonEncoder
import json
    
class Nfield(Field):
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

    def __str__(self):
        '''return json string format'''
        return str(self.to_ntv(modecodec='full'))
        #return '    ' + self.to_obj(encoded=True, modecodec='full', untyped=False) + '\n'
        
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
    def n_to_i(ntv, fast=False):
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
    
class Sfield(Field):
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

    def __str__(self):
        '''return json string format'''
        return str({self.name: self.l_to_e(self.values)})
        #return '    ' + self.to_obj(encoded=True, modecodec='full', untyped=False) + '\n'
        
    @staticmethod
    def l_to_i(lis, fast=False):
        ''' converting a list of external values to a list of internal values'''
        if fast:
            return lis
        return [Sfield.s_to_i(val, fast) for val in lis]
    
    @staticmethod
    def s_to_i(val, fast=False):
        '''converting an external value to an internal value'''
        if fast:
            return val
        if val is None or isinstance(val, bool):
            return json.dumps(val)
        if isinstance(val, list):
            return Sfield._tupled(val)
        if isinstance(val, dict):
            return json.dumps(val, cls=NtvJsonEncoder)
        return val    
    
    @staticmethod
    def n_to_i(ntv_lis, fast=False):
        ''' converting a NtvList value to an internal value'''
        if isinstance(ntv_lis, list) and len(ntv_lis) == 0:
            return []
        if isinstance(ntv_lis, list) and ntv_lis[0].__class__.__name__ in ('NtvSingle', 'NtvList'):
            #return [Sfield.n_to_i(ntv.val, fast) for ntv in ntv_lis]
            return [Sfield.n_to_i(ntv.to_obj(), fast) for ntv in ntv_lis]
        return  Sfield.s_to_i(ntv_lis, fast)
    
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
        if val in ('null', 'false', 'true'):
            return json.loads(val)
        #if val is None or isinstance(val, bool):
        #    return json.dumps(val)
        if isinstance(val, tuple):
            return Sfield._listed(val)
        if isinstance(val, str) and len(val) > 0 and val[0] == '{':
            return json.loads(val)
        return val
    
    @staticmethod
    def i_to_n(val):
        ''' converting an internal value to a NTV value'''
        return Ntv.obj(Sfield.s_to_e(val))

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