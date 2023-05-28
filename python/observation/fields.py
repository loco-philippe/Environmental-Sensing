# -*- coding: utf-8 -*-
"""
Created on Sun May 28 19:34:03 2023

@author: a lab in the Air
"""
from ntvfield import Ntvfield
from json_ntv import Ntv

    
class Nfield(Ntvfield):
    
    def __init__(self, codec=None, name=None, keys=None, typevalue=None,
                 lendefault=0, reindex=False, castobj=True):
        super().__init__(codec=codec, name=name, keys=keys, typevalue=typevalue,
                     lendefault=lendefault, reindex=reindex, castobj=castobj)

    @staticmethod
    def l_to_i(lis):
        return [Ntv.obj(val) for val in lis]

    @staticmethod
    def s_to_i(val):
        return Ntv.obj(val)

    @staticmethod
    def n_to_i(ntv):
        return ntv

    @staticmethod
    def l_to_e(lis):
        return [ntv.to_obj() for ntv in lis]    

    @staticmethod
    def s_to_e(val):
        return val.to_obj()

    @staticmethod
    def i_to_n(val):
        return val
    
class Sfield(Ntvfield):
    
    def __init__(self, codec=None, name=None, keys=None, typevalue=None,
                 lendefault=0, reindex=False, castobj=True):
        super().__init__(codec=codec, name=name, keys=keys, typevalue=typevalue,
                     lendefault=lendefault, reindex=reindex, castobj=castobj)
        
    @staticmethod
    def l_to_i(lis):
        return lis
    
    @staticmethod
    def s_to_i(val):
        return val
    
    @staticmethod
    def n_to_i(ntv_lis):
        return [ntv.val for ntv in ntv_lis]
    
    @staticmethod
    def l_to_e(lis):
        return lis
    
    @staticmethod
    def i_to_n(val):
        return Ntv.obj(val)
    