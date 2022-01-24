# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 14:51:23 2021

@author: philippe@loco-labs.io

This module include the `ESSet` class, parent class of the objects used in the 
`ES.ESObs` module :
    
- `ES.ESValue.DatationValue`,
- `ES.ESValue.LocationValue`,
- `ES.ESValue.PropertyValue`,
- `ES.ESValue.ResultValue`  
"""

import json, struct, copy
from ESconstante import ES
from ESValue import LocationValue, DatationValue, PropertyValue, ResultValue

ValueCod = [ None, LocationValue, DatationValue, PropertyValue, 
            LocationValue, DatationValue, PropertyValue]

class ESSet:
    """
    This class represent a set of `ESValue.ESValue`.
    
    *Attributes (for @property see methods)* :
    
    - **ValueClass** : Name of the `ESValue.ESValue` Class
    - **valueList** : List of `ESValue.ESValue` objects
     
    The methods defined in this class are : 

    *property (getters)*

    - `boundingBox`
    - `nValue`
    - `vListName`

    *getters*

    - `indexLoc`
    - `vList`

    *add update manage*

    - `addValue`
    - `majListName`
    - `majList`
    - `majListValue`
    - `sort`

    *exports - imports*

    - `jsonESSet`
    - `from_bytes`
    - `to_bytes`
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

    def __len__(self): 
        try: return len(self.valueList)
        except : return 0
    
    def __getitem__(self, key): return self.valueList[key]
    
    def __setitem__(self, key, value): self.valueList[key] = value

    def __repr__(self): return object.__repr__(self) + '\n' + self._jsonSet(**ES.mOption) + '\n'

    def addValue(self, value, equal = 'full'):          # !!! fonctions externes
        if type(value) == self.ValueClass : val = value
        else: val = self.ValueClass(value)
        if self.ValueClass == ResultValue :
            ind = self._indexResLoc(val)
            if ind != None : return 
        else :
            ind = self.indexLoc(val)[equal]
            if ES.mOption["unic_index"] and ind != -1 : return ind
        self.valueList.append(val)
        return len(self.valueList) - 1

    @property
    def boundingBox(self):
        val = copy.deepcopy(self.valueList[0].value)
        for i in range(1,self.nValue): val = val.union(self.valueList[i].value)
        return self.ValueClass._Box(*val.bounds)

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
            self.addValue(esVal)
            idx += n
        return idx

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

    def jsonESSet(self, ES_valName, **option):
        if self.valueList == None or len(self.valueList) == 0: js = {}
        else : js = {ES_valName : self._jsonSet(**option)}
        if 'json_string' in option and  option['json_string'] : return json.dumps(js)
        else : return js
    
    def majList(self, listVal, name=False):
        if name : self.majListName(listVal)
        else : self.majListValue(listVal)
        
    def majListName(self, listVal):
        if len(listVal) != self.nValue : return
        for i in range(self.nValue) : self.valueList[i].setName(self.ValueClass(listVal[i]).name)

    def majListValue(self, listVal):
        if len(listVal) != self.nValue : return
        for i in range(self.nValue) : self.valueList[i].setValue(self.ValueClass(listVal[i]))
           
    @property
    def nValue(self): return len(self.valueList)

    def sort(self, order = [], update = True):
        if order == [] :
            listInd = sorted(list(zip(self.valueList, list(range(self.nValue)))), key= lambda z : z[0])
            valueTri, indTri = zip(*listInd)
            if update : self.valueList = list(valueTri)
        else :
            if update : self.valueList = [self.valueList[order[i]] for i in range(len(self.valueList))]
            indTri = order
        return list(indTri)
        
    def to_bytes(self, nameES = False, resIndex = False, forma = ES.nullDict, prpList = []):
        byt = bytes()
        offset = 3 * (not nameES)
        code_el = ES.codeb[self.classES] # type de ESobs
        if code_el < 4 : code_ES = ES.codeb[self.typeES] + offset # choix name ou value
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
                if forma == ES.nullDict and prpList != [] : prp = prpList[self.valueList[i].ind[2]]
                byt += self.valueList[i].to_bytes(resIndex, prp)
        return byt
    
    @property
    def vListName(self):
        return [self.valueList[i].vName(ES.vName[self.classES] + str(i)) for i in range(self.nValue)]

    def vList(self, func=ES._identity):
        if func == 'index': return [i for i in range(self.nValue)]
        else :              return [func(self.valueList[i]) for i in range(self.nValue)]
        
    def _indexResLoc(self, val):                # !!! fonctions internes
        if self.ValueClass == ResultValue :
            if val.ind != ES.nullInd :
                for i in range(len(self.valueList)):
                    if self.valueList[i].ind == val.ind : return i     

    def _jsonSet(self, **option) :
            if len(self.valueList) == 0 : return []
            elif len(self.valueList) == 1 : return self.valueList[0].json(**option) 
            else : return [val.json(**option) for val in self.valueList]
