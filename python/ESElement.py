# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 13:24:02 2021

@author: philippe@loco-labs.io

This module contains the `ESElement` parent class of the `ES.ESObs.ESObs` and
`ES.ESObservation.Observation` classes. 
"""
import json
from ESconstante import ES

class ESElement:
    """
    
    *Attributes* :
    
    - **mAtt** : dict with properties of an instance
    - **typeES** : String, define the nature of an `ESElement`
    - **classES** : String, define the level of class
    - **pComposant** : list of `ESElement` included in the `ESElement`
    - **pContenant** : list of `ESElement` containing the `ESElement`
    
    The methods defined in this class are : 

    - `addComposant`
    - `element`
    - `getAttAll`
    
    
    - `isESAtt`(@staticmethod)
    - `isESObs`(@staticmethod)
    - `isUserAtt`(@staticmethod)
    
    
    """
    def __init__(self):
        self.mAtt = dict()
        self.typeES = "null"
        self.classES = "null"
        self.pComposant = list()
        self.pContenant = list()

    def __repr__(self):
        txt = object.__repr__(self) + '\n'
        txt += f"classES, typeES : {self.classES} {self.typeES} \n"
        for k, v in self.mAtt.items(): txt += f"{k} : {v} \n"
        if (len(self.pComposant) > 0): txt += f"nombre de composants {len(self.pComposant)} \n"
        if (len(self.pContenant) > 0): txt += f"nombre de contenants {len(self.pContenant)} \n"
        return txt
    
    def addComposant(self, pCompos):
        '''Link two `ESElement` 
        
        *Parameters*
        
        - **pCompos** : `ESElement` to include
        
        *Returns*
        
        - **None**
        '''
        self.pComposant.append(pCompos)
        pCompos.pContenant.append(self)

    def element(self, comp) :
        """Return `ESElement` included with a specific 'classES' or 'typeES'
        
        *Parameters*
        
        - **comp** : string to search
        
        *Returns*
        
        - **ESElement found**
        """
        for cp in self.pComposant:
            if (cp.typeES == comp or cp.classES == comp): return cp
            elif (cp.element(comp) != None): return cp.element(comp)
        return None

    def getAttAll(self, key):
        """Return mAtt value in a global hierachy
        
        *Parameters*
        
        - **key** : string to search
        
        *Returns*
        
        - **value found**
        """
        if self.isAtt(key): return self.mAtt[key];
        for compo in self.pComposant:
            if (compo.getAttAll(key) != ES.nullAtt): return compo.getAttAll(key)
        return ES.nullAtt

    @staticmethod
    def isESObs(esClass, jObj):
        """Identify if 'jObj' include 'esClass' keys
        
        *Parameters*
        
        - **jObj** : dict to be evaluated
        
        *Returns*
        
        - **Boolean**
        """        
        if type(jObj) == esClass : return True
        if type(jObj) != dict : return False
        for key, value in jObj.items():
            if key == esClass: return True
            for val, classES in ES.mValObs.items():
                if key == val and esClass == classES:  return True
            for val, classES in ES.mTypeAtt.items():
                if key == val and esClass == classES:  return True
        return False

    @staticmethod
    def isESAtt(esClass, key):
        """identify if 'key' is included in 'esClass'
        
        *Parameters*
        
        - **esClass** : string for an ESClass attribute
        - **key** : string to search
        
        *Returns*
        
        - **Boolean**
        """        
        for k,v in ES.mTypeAtt.items():
            if v == esClass and k == key: return True
        return False

    @staticmethod
    def isUserAtt(key):
        """identify if 'key' is included in any `ESElement` attribute
        
        *Parameters*
        
        - **key** : string to search
        
        *Returns*
        
        - **Boolean**
        """                
        for k,v in ES.mTypeAtt.items():
            if k == key: return False
        for k,v in ES.mValObs.items():
            if k == key: return False
        return True

    
    def _jsonAtt(self, **option):
        att = dict()
        for k, v in self.mAtt.items():
            if k in list(ES.mTypeAtt.keys()) : 
                if v not in ES.nullValues : att[k] = v
            else: att[k] = v
        return att