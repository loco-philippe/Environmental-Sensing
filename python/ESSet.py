# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module groups together the classes of the objects used in the `ES.ESObs` module :
    
- `ES.ESValue.DatationValue`,
- `ES.ESValue.LocationValue`,
- `ES.ESValue.PropertyValue`,
- `ES.ESValue.ResultValue`

the parent classes :
    
- `ES.ESValue.ESValue`, 
- `ES.ESValue.ESIndexValue`.

and the `ES.ESValue.ESSet` class.   
"""

import json, struct, copy
from ESconstante import ES #, _identity
from ESElement import isESAtt, isUserAtt
from ESValue import LocationValue, DatationValue, PropertyValue, ResultValue

ValueCod = [ None, LocationValue, DatationValue, PropertyValue, 
            LocationValue, DatationValue, PropertyValue]

class ESSet:        # !!! ESSet
    """
    Classe liée à la structure interne
    """

    def __init__(self, ValueClass = None, jObj = None):
        if ValueClass == None: return
        self.ValueClass = ValueClass
        self.valueList = list()
        if  type(jObj) == list :
            try :
                for val in jObj : self.addValue(val)
            except : self.addValue(jObj)
        elif jObj == None : return 
        else : self.addValue(jObj)

    def initESSet(self, ValueClass, jObj):
        if type(jObj) == dict:
            userAtt = False
            jDat = jObj.copy()
            for k, v in jDat.items():   # si mot-clef ESobs
                if k == self.classES: 
                    jDat = v
                    userAtt = True
            for k, v in jDat.items(): # attributs
                if isESAtt(self.classES, k) or (userAtt and isUserAtt(k)): self.mAtt[k] = v
            if ValueClass.valName in list(jDat):    # si valeurs simple ou detaillee précisée
                    ESSet.__init__(self, ValueClass, jDat[ValueClass.valName]) 
            else :  ESSet.__init__(self, ValueClass, jObj)
        else :      ESSet.__init__(self, ValueClass, jObj)
    
    @property
    def vListName(self):
        return [self.valueList[i].vName(ES.vName[self.classES] + str(i)) for i in range(self.nValue)]

    def vList(self, func=ES._identity):
        return [func(self.valueList[i]) for i in range(self.nValue)]
        
    def majListName(self, listVal):
        if len(listVal) != self.nValue : return
        for i in range(self.nValue) : self.valueList[i].setName(self.ValueClass(listVal[i]).name)

    def majList(self, listVal, name=False):
        if name : self.majListName(listVal)
        else : self.majListValue(listVal)
        
    def majListValue(self, listVal):
        if len(listVal) != self.nValue : return
        for i in range(self.nValue) : self.valueList[i].setValue(self.ValueClass(listVal[i]))
        
    def addValue(self, value, equal = 'full'):
        if type(value) == self.ValueClass : val = value
        else: val = self.ValueClass(value)
        if self.ValueClass == ResultValue :
            ind = self.indexResLoc(val)
            if ind != None : return 
            '''if val.ind != ES.nullInd :
                for i in range(len(self.valueList)):
                    if self.valueList[i].ind == val.ind : return i'''      
            #self.valueList.append(val)
        else :
            ind = self.indexLoc(val)[equal]
            if ES.mOption["unic_index"] and ind != -1 : return ind
            '''for i in range(len(self.valueList)):
                #if self.valueList[i] == val and ES.mOption["unic_index"]: return i
                if self.valueList[i].isEqual(val) and ES.mOption["unic_index"]: return i'''
        self.valueList.append(val)
        return len(self.valueList) - 1

    def indexResLoc(self, val):
        if self.ValueClass == ResultValue :
            if val.ind != ES.nullInd :
                for i in range(len(self.valueList)):
                    if self.valueList[i].ind == val.ind : return i     
                    
    def indexLoc(self, val):
        ind = {'full' : -1, 'name' : -1, 'value' : -1}
        for i in range(len(self.valueList)):
            if self.valueList[i].isEqual(self.ValueClass(val), name=True, value=True): 
                ind['full'] = ind['name'] = ind['value'] = i
                return ind
            if self.valueList[i].isEqual(self.ValueClass(val), name=True, value=False) \
                and ind['name'] == -1: 
                    ind['name'] = i
            if self.valueList[i].isEqual(self.ValueClass(val), name=False, value=True) \
                and ind['value'] == -1: 
                    ind['value'] = i
        return ind
            #if self.valueList[i].isEqual(self.ValueClass(val)): return i
        
    @property
    def nValue(self): return len(self.valueList)
        
    def jsonESSet(self, ES_valName, option):
        try:
            if len(self.valueList) == 0: return ""
        except: return""
        elt_type_nb = 0
        if option["json_elt_type"] : elt_type_nb = min(2, self.nValue)
        js = ""
        if option["json_ESobs_class"]: js = '"' + self.classES + '":{'
        js += self._jsonAtt(elt_type_nb) 
        js += '"' + ES_valName + '":' + self.jsonSet(option) + ","
        if js[-1] == ',': js = js[:-1]
        if option["json_ESobs_class"]: js += '}' 
        return js

    def jsonSet(self, option) :
        if self.ValueClass in [DatationValue, LocationValue] :
            if len(self.valueList) == 0 : return ""
            if len(self.valueList) == 1 : return self.valueList[0].json(string=True) 
            li = list()
            for i in range(self.nValue): 
                li.append(self.valueList[i].json(string=False))
            return json.dumps(li)
        else :
            if len(self.valueList) == 0 : return ""
            #if len(self.valueList) == 1 : return self.valueList[0].json(option) 
            if len(self.valueList) == 1 : return self.valueList[0].json() 
            li = list()
            for i in range(self.nValue): 
                try: li.append(json.loads(self.valueList[i].json(option)))
                except: li.append(self.valueList[i].json(option))
                #try: li.append(json.loads(self.valueList[i].json()))
                #except: li.append(self.valueList[i].json())    
            return json.dumps(li)

    def to_bytes(self, nameES = False, resIndex = False, forma = ES.nullDict, prpList = []):
        byt = bytes()
        offset = 3 * (not nameES)
        code_el = ES.codeb[self.classES] # type de ESobs
        if code_el < 4 : code_ES = ES.codeb[self.mAtt[ES.type]] + offset # choix name ou value
        else : code_ES = ES.prop[forma][0]     
        if code_el == 4 and resIndex : code_el = 5
        unique = self.nValue == 1 
        oct1 = (code_el << 5) | (unique << 4) | code_ES
        byt += struct.pack('<B', oct1)
        if not unique : byt += struct.pack('<H', self.nValue)
        for i in range(self.nValue) :
            prp = forma
            if forma == ES.nullDict and prpList == [] : prp = ES.nullDict
            if (nameES and code_el < 4) or (code_el > 3 and forma == "UTF-8") : 
                byt += self.valueList[i]._to_strBytes()
            elif not nameES and code_el < 4 : byt += self.valueList[i].to_bytes()
            elif code_el < 6 : 
                #if forma == 'null' and prpList != [] : prp = prpList[i]
                if forma == ES.nullDict and prpList != [] : prp = prpList[self.valueList[i].ind[2]]
                byt += self.valueList[i].to_bytes(resIndex, prp)
        return byt
    
    def from_bytes(self, byt, prpList = []):  #prplist complète si sans index
        code_ES =  byt[0] & 0b00001111
        unique  = (byt[0] & 0b00010000) >> 4
        code_el = (byt[0] & 0b11100000) >> 5
        nameES = not(code_ES // 3)
        forma = ES.nullDict
        if code_el > 3 : forma = ES.invProp[code_ES]
        resIndex = code_el == 5
        nVal = 1
        idx = 1
        n = 0
        if not unique : 
            nVal = struct.unpack('<H',byt[1:3])[0]
            idx = 3
        for i in range(nVal):
            if   code_el < 4 : esValue = ValueCod[code_ES]
            elif code_el < 6 : esValue = ResultValue
            esVal = esValue()
            prp = forma
            if forma == ES.nullDict and prpList == [] : prp = ES.nullDict
            #if prpList == [] : prp = "null"
            if (nameES and code_el < 4) or (code_el > 3 and forma == "utf-8") : 
                n = esVal._from_strBytes(byt[idx:])
            elif not nameES and code_el < 4 : n = esVal.from_bytes(byt[idx:])
            elif code_el < 6 and not resIndex: 
                if forma == ES.nullDict and prpList != [] : prp = prpList[i]
                n = esVal.from_bytes(byt[idx:], resIndex, prp)
            elif code_el < 6 and resIndex : 
                nPrp = struct.unpack('<BBB',byt[idx:idx+3])[2]
                if forma == ES.nullDict and prpList != [] : prp = prpList[nPrp]
                n = esVal.from_bytes(byt[idx:], resIndex, prp)
            #self.addValue(esValue, esVal)
            self.addValue(esVal)
            idx += n
        return idx
        
    def __len__(self): 
        try: return len(self.valueList)
        except : return 0
    
    def __getitem__(self, key): return self.valueList[key]
    
    def __setitem__(self, key, value): self.valueList[key] = value

    def __repr__(self): return object.__repr__(self) + '\n' + self.jsonSet(ES.mOption) + '\n'

    def boundingBox(self):
        #box = copy.deepcopy(self.valueList[0])
        val = copy.deepcopy(self.valueList[0].value)
        for i in range(1,self.nValue): val = val.union(self.valueList[i].value)
        return self.ValueClass._Box(*val.bounds)

    def sort(self, order = [], update = True):
        if order == [] :
            listInd = sorted(list(zip(self.valueList, list(range(self.nValue)))), key= lambda z : z[0])
            valueTri, indTri = zip(*listInd)
            if update : self.valueList = list(valueTri)
        else :
            if update : self.valueList = [self.valueList[order[i]] for i in range(len(self.valueList))]
            indTri = order
        return list(indTri)
        
