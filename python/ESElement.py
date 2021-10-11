# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 13:24:02 2021

@author: a179227
"""
import json
from datetime import datetime
from ESconstante import ES, mTypeAtt, mValObs

def isESObs(esClass, jObj):
    esObs = False
    for key, value in jObj.items():
        if key == esClass: esObs = True
        for val, classES in mValObs.items():
            if key == val and esClass == classES:  esObs = True
    return esObs


def isESAtt(esClass, key):
    for k,v in mTypeAtt.items():
        if v == esClass and k == key: return True
    return False

'''def deserialize(jsonStr):
    return json.loads(jsonStr)
'''
class ESElement:
    """
    Classe liée à la structure interne
    """
    def __init__(self):
        self.mAtt = dict()
        self.mAtt[ES.type] = "null"
        self.typeES = "null"
        self.classES = "null"
        self.metaType = "null"
        self.parameter = "null"
        self.pComposant = list()
        self.pContenant = list()

    def __repr__(self):
        txt = object.__repr__(self) + '\n'
        txt += f"metatype, classES, typeES : {self.metaType} {self.classES} {self.typeES} \n"
        for k, v in self.mAtt.items(): txt += f"{k} : {v} \n"
        if (len(self.pComposant) > 0): txt += f"nombre de composants {len(self.pComposant)} \n"
        if (len(self.pContenant) > 0): txt += f"nombre de contenants {len(self.pContenant)} \n"
        return txt
    
    def setAtt(self, key, value):
        self.mAtt[key] = value
    
    '''        
    def getAtt(self, key):
        if self.isAtt(key): return  self.mAtt[key]
        else: return "null"
    
    def isAtt(self, key):
        return key in self.mAtt
    '''
    def getAttAll(self, key):
        if self.isAtt(key): return self.mAtt[key];
        for compo in self.pComposant:
            if (compo.getAttAll(key) != "null"): return compo.getAttAll(key)
        return "null";

    def addComposant(self, pCompos):
        self.pComposant.append(pCompos)
        pCompos.pContenant.append(self)

    def element(self, comp) :
        for cp in self.pComposant:
            if (cp.typeES == comp or cp.classES == comp or cp.metaType == comp or cp.mAtt[ES.type] == comp):
                return cp
            elif (cp.element(comp) != None): return cp.element(comp)
        return None

    def majMeta(self):
        #for ct in self.pContenant:
            #if (ct.typeES == ES.obs_typeES): ct.majType()
        pass

    def jsonAtt(self, elt_type_nb):
        att = dict()
        for k,v in self.mAtt.items():
            if k in list(mTypeAtt.keys()) and v != "null":
                if k != ES.type and elt_type_nb > 0 : att[k] = v
                elif k == ES.type :
                    if elt_type_nb == 1 : att[k + self.classES] = v
                    elif elt_type_nb == 2 : att[k + self.classES] = ES.multi + v
                    elif elt_type_nb == -1 : att[k] = v
                    elif elt_type_nb == -2 : att[k] = ES.multi + v
            if k[0] == '$' and v != "null": att[k] = v
        if len(att) == 0 : return ""
        return json.dumps(att)[1:-1] + ","

class ESObject(ESElement):
    """
    Classe liée à la structure interne
    """
    def __init__(self):
        ESElement.__init__(self)
        self.metaType = ES.obj_metaType
        self.name = "observtion du " + datetime.now().isoformat()
        
class ESObs(ESElement):
    """
    Classe liée à la structure interne
    """
    def __init__(self, pObs=None):
        ESElement.__init__(self)
        self.metaType = ES.obs_metaType
        self.nValue = 0
        if (pObs != None): pObs.addComposant(self)

