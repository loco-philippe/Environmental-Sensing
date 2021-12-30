# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: Philippe@loco-labs.io

The `ES.ESObservation` module contains the main class
of Environmental Sensing : `ES.ESObservation.Observation` class.
"""
from ESObs import ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult
from ESElement import ESObject, isESObs, isESAtt, isUserAtt
from ESconstante import ES #, Es, identity
from ESValue import LocationValue, DatationValue, PropertyValue, \
    ResultValue, _gshape
from shapely.geometry import shape
import json, folium, struct, copy
import numpy as np
import xarray as xr
#import geopandas as gp
import matplotlib.pyplot as plt

class Observation(ESObject):
    """
    An `ES.ESObservation.Observation` is made up of objects from the `ES.ESObs` class
     which each describe a dimension of this object.
    
    Attributes :
    -----------
        - complet : consistency between Result and Datation, Location, Property
        - score : Observation structure codification
        - option : option 
        - setLocation : shortcut to ESSetLocation (@property)
        - setDatation : shortcut to ESSetDatation (@property)
        - setProperty : shortcut to ESSetProperty (@property)
        - setResult   : shortcut to ESSetResult   (@property)
        - nValueObs   : lenght of ESObs
        - name : textual description (inherited from ESObject)
        - typeES : 'observation' (inherited from ESElement)
        - classES : 'observation' (inherited from ESElement)
        - metaType : 'ESObject' (inherited from ESElement)
        - mAtt : namedValue dictionnary (inherited from ESElement)
        - userAtt : namedValue dictionnary (inherited from ESElement)
        - pComposant : list of ESObs (inherited from ESElement)
        - pContenant : empty list (inherited from ESElement)
        - parameter : namedValue dictionnary (inherited from ESElement)

    """
    #def __init__(self, jso = {}, order = 'dlp'):
    def __init__(self, *args, order = 'dlp', **kwargs):
        ESObject.__init__(self)
        self.option = ES.mOption.copy()
        '''Dictionnary with options. '''
        self.mAtt[ES.obs_reference] = 0
        ''' Attribut décrivant une `Observation` de référence utilisée pour compléter l'Observation actuelle.'''
        self.score = -1
        ''' Integer : Number of ESValue for each ESObs. For example, 122 means one PropertyValue (1), 
        several LocationValue (2), several DatationValue (2).'''
        self.complet = False
        ''' Boolean : True if the number of ResultValue is consistent with the number of 
        LocationValue, DatationValue and PropertyValue.'''
        self.mAtt[ES.obs_resultTime] = "null"
        self.classES = ES.obs_classES
        self.typeES = ES.obs_typeES
        self.mAtt[ES.type] = "obsError"
        self.mAtt[ES.obs_id] = "null"
        for arg in args :
            if type(arg) in (dict, str) : self._init(arg)
            else : self.addESObs(arg)
        for k in kwargs :
            if type(kwargs[k]) in (ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult) :
                self.addComposant(kwargs[k])
            else : self.addESObs(kwargs[k], k)
        self.majType(order)
    
    def _init(self, jso) :
        ''' attributes and ESObs creation '''
        if type(jso) == str :
            try:
                js=json.loads(jso)
            except:
                return
        elif type(jso) == dict :
            js = jso.copy()
        else : return
        if js == {}: return
        if type(jso) == str and (ES.type not in list(js) or js[ES.type] != ES.obs_classES): return
        if ES.obs_id in list(js): self.mAtt[ES.obs_id] = js[ES.obs_id]
        if ES.obs_attributes in list(js): 
            if type(js[ES.obs_attributes]) == dict: js = js[ES.obs_attributes]
            else: return
        self.addAttributes(js)
        self.addESObs(js)
    
    def addESObs(self, js, classES = None) :
        '''
        Add a new `ES.ESObs` attached to `ES.ESObservation.Observation`. 
        The ES.ESObs child class is defined by classES or if None by the js structure.

        Parameters
        ----------
        js : ES.ESObs compatible type
        classES : string, optional
            value of the ES.ESObs ESclass attributes. The default is None.
        Returns
        -------
        None.

        '''
        if classES in (None, ES.dat_classES) and isESObs(ES.dat_classES, js): 
            ESSetDatation(pObs=self, jObj=js)
        if classES in (None, ES.loc_classES) and isESObs(ES.loc_classES, js): 
            ESSetLocation(pObs=self, jObj=js)
        if classES in (None, ES.prp_classES) and isESObs(ES.prp_classES, js): 
            ESSetProperty(pObs=self, jObj=js)
        if classES in (None, ES.res_classES) and isESObs(ES.res_classES, js): 
            ESSetResult  (pObs=self, jObj=js)

    def addAttributes(self, js):
        '''
        Add informations attached to `ES.ESObservation.Observation`

        Parameters
        ----------
        js : Dictionnary
            Keys are Observation keys or users keys.
        Returns
        -------
        None
        '''
        if type(js) != dict: return
        for k, v in js.items():
            if isESAtt(ES.obs_classES, k) or isUserAtt(k): self.mAtt[k] = v
            if k == ES.parameter: 
                try:  self.parameter = json.dumps(v)
                except:  self.parameter = "null"

    @property
    def bounds(self):
        '''tuple : Observation boundingBox (xmin, ymin, xmax, ymax).'''
        if self.setLocation : return shape(self).bounds
        else : return None

    @property
    def __geo_interface__(self):
        '''dict : geometry (see shapely)'''
        if self.setLocation : 
            return _gshape(self.setLocation.jsonSet(self.option)).__geo_interface__
            #return gshape(self.setLocation.geoInterface(self.option)).__geo_interface__
            '''return gshape(json.dumps(json.loads('{' \
                        #+ self.setLocation.json(False, False, False, False)\
                        + self.setLocation.geoInterface(self.option)\
                        #+ '}')["coordinates"])).__geo_interface__
                        + '}')[ES.loc_valName[indice]])).__geo_interface__'''
        else : return ""

    @property
    def jsonFeature(self):
        ''' string : "FeatureCollection" with geometry in the Observation'''
        if self.setLocation : 
            geo = self.__geo_interface__
            if geo['type'] == "MultiPolygon": typ = "Polygon"
            else : typ = "Point"
            lis = list(dict((("type", typ), ("coordinates", geo['coordinates'][i]))) for i in range(len(geo['coordinates'])))
            fea = list(dict((("type","Feature"), ("id", i), ("geometry", lis[i]))) for i in range(len(geo['coordinates'])))
            return json.dumps(dict((("type","FeatureCollection"), ("features",fea))))            
        else: return ''  
            
    @property
    def setLocation(self):
        '''object `ES.ESObs.ESSetLocation` if exists, None otherwise.'''
        return self.element(ES.loc_classES)
    @property
    def setDatation(self):  
        '''object `ES.ESObs.ESSetDatation` if exists, None otherwise.'''
        return self.element(ES.dat_classES)
    
    @property
    def setProperty(self):  
        '''object `ES.ESObs.ESSetProperty` if exists, None otherwise.'''
        return self.element(ES.prp_classES)
    
    @property
    def setResult(self):  
        '''object `ES.ESObs.ESSetResult` if exists, None otherwise.'''
        return self.element(ES.res_classES)

    def __copy__(self):
        return copy.deepcopy(self)
        '''opt = self.option
        self.option["json_obs_val"] = True
        cop = Observation(self.json())
        self.option = opt
        cop.option = opt
        return cop'''

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        other_opt = other.option
        self_opt = self.option
        ndat = nloc = nprp = 0
        idat = 0; iloc = 1; iprp = 2
        other.option["maj_index"] = True
        other.majType()
        self.option["maj_index"] = True
        self.majType()
        if other.setResult != None and other.setResult.getMaxIndex() > -1:
            for resVal in other.setResult.valueList:
                ndat = self.addValue(other.setDatation.valueList[resVal.ind[idat]])
                nloc = self.addValue(other.setLocation.valueList[resVal.ind[iloc]])
                nprp = self.addValue(other.setProperty.valueList[resVal.ind[iprp]])
                resv = ResultValue(resVal.value)
                resv.ind = [ndat, nloc, nprp]
                self.addResultValue(resv)
            self.majType()
        other.option = other_opt
        self.option = self_opt
        return self
    
    def __add__(self, other):
        ''' Add other's values to self's values in a new Observation'''
        obres = self.__copy__()
        obres.__iadd__(other)
        return obres
    
    def extend(self, obs):
        '''
        Copy `ES.ESObs` from obs to self (if it daesn't exist)

        Parameters
        ----------
        obs : object ES.ESObservation.Observation to copy
        Returns
        -------
        None.
        '''
        for p in obs.pComposant :
            if self.element(p.classES) == None : self.addComposant(p)
        self.majType()    
        
    def addResultValue(self, esValue):
        '''
        Add a new `ES.ESValue.ResultValue` in the `ES.ESObs.ESSetResult`

        Parameters
        ----------
        esValue : ES.ESValue.ResultValue
        Returns
        -------
        Int : last index in the `ES.ESValue.ESSet` valueList.
        '''
        return self.element(ES.res_valueType).addValue(ResultValue, esValue)
    
    def addValue(self, esValue):
        '''
        Add a new `ES.ESValue` in the `ES.ESValue.ESSet`

        Parameters
        ----------
        esValue : ES.ESValue
        Returns
        -------
        Int : last index in the `ES.ESValue.ESSet` valueList.
        '''
        if type(esValue)== PropertyValue:
            if self.element(ES.prp_valueType) == None: ESSetProperty(pObs=self)
            return self.element(ES.prp_valueType).addValue(PropertyValue, esValue)
        elif type(esValue)== LocationValue:
            if self.element(ES.loc_valueType) == None: ESSetLocation(pObs=self)
            return self.element(ES.loc_valueType).addValue(LocationValue, esValue)
        elif type(esValue)== DatationValue:
            if self.element(ES.dat_valueType) == None: ESSetDatation(pObs=self)
            return self.element(ES.dat_valueType).addValue(DatationValue, esValue)
        else: return 0

    def addListResultValue(self, listEsValue):
        '''
        Add a list of new `ES.ESValue.ResultValue` in the `ES.ESObs.ESSetResult`.

        Parameters
        ----------
        listEsValue : list of `ES.ESValue.ResultValue`
        Returns
        -------
        None
        '''
        if type(listEsValue) != list : return
        if self.element(ES.res_valueType) == None: resSet = ESSetResult(pObs=self)
        else: resSet = self.setResult
        for val in listEsValue : resSet.addValue(ResultValue, ResultValue(val))
            #self.addResultValue(ResultValue(val) )

    def majList(self, ValueClass, listVal, info = 'name'):
        '''
        Modify a list of one attribute (name or value) in an `ES.ESObs`

        Parameters
        ----------
        ValueClass : class ES.ESObs 
        listVal : list of values
        info : string, optional, 
            Attribute. The default is 'name'. 
        Returns
        -------
        None
        '''
        if ValueClass == DatationValue and self.setDatation != None : 
            if info == 'name': self.setDatation.majListName(listVal)
            else : self.setDatation.majListValue(ValueClass, listVal, info == 'base')
        elif ValueClass == LocationValue and self.setLocation != None : 
            if info == 'name': self.setLocation.majListName(listVal)
            else : self.setLocation.majListValue(ValueClass, listVal, info == 'base')
        elif ValueClass == PropertyValue and self.setProperty != None : 
            if info == 'name': self.setProperty.majListName(listVal)

    def addListValue(self, ValueClass, listEsValue):
        '''
        Add a list of new `ES.ESValue` in a `ES.ESValue.ESSet`.

        Parameters
        ----------
        ValueClass : name of the selected class ES.ESValue
        listEsValue : list of ES.ESValue
        Returns
        -------
        None
        '''
        for val in listEsValue : self.addValue(ValueClass(val) )
        
    def addValueObservation(self, val, idat, iloc, iprp):
        '''
        Add a new `ES.ESValue.ResultValue` 
        
        Parameters
        ----------
        val : ES.ESValue.ResultValue compatible type
        idat, iloc, iprp : integer, ES.ESValue.ESIndexValue
        Returns
        -------
        Int : last index in the `ES.ESValue.ESSet` valueList.
        '''
        if self.element(ES.res_valueType) == None: ESSetResult(pObs=self)
        return self.addResultValue(ResultValue(val, [idat, iloc, iprp]))

    def addListValueObservation(self, listVal, listIdat, listIloc, listIprp):
        '''
        Add a list of new `ES.ESValue.ResultValue` 
        
        Parameters
        ----------
        listVal : list of ES.ESValue.ResultValue compatible type
        listIdat, listIloc, listIprp : list of integer in ES.ESValue.ESIndexValue
        Returns
        -------
        None
        '''
        if len(listVal)==len(listIdat)==len(listIloc)==len(listIprp) :
            for i in range(len(listVal)) :
                self.addResultValue(ResultValue(listVal[i], [listIdat[i], listIloc[i], listIprp[i]]))

    def addValueSensor(self, resVal, datVal, locVal, nprp):
        '''
        Add `ES.ESValue.ResultValue`,  `ES.ESValue.DatationValue`,  `ES.ESValue.LocationValue`
        for a defined property.

        Parameters
        ----------
        resVal : ES.ESValue.ResultValue compatible type, 
        datVal : ES.ESValue.DatationValue compatible type
        locVal : ES.ESValue.LocationValue compatible type
        nprp : integer, index of the ES.ESValue.PropertyValue
        Returns
        -------
        Int : last index in the `ES.ESValue.ESSet` valueList.

        '''
        return self.addValueObservation(resVal, self.addValue(DatationValue(datVal)), 
                                        self.addValue(LocationValue(locVal)), nprp)

    def json(self): 
        '''
        Export in Json format. 
        
        Returns
        -------
        string : Json string 

        '''
        if self.option["json_elt_type"]: option_type = 1
        else: option_type = 0
        js =""
        if self.option["json_obs_val"]: js = "{"
        js += '"' + ES.type +'":"' + ES.obs_classES +'",'
        if self.mAtt[ES.obs_id] != "null": js += '"' + ES.obs_id + '":"' + self.mAtt[ES.obs_id] + '",'
        if self.option["json_obs_attrib"]: js += '"' + ES.obs_attributes + '":{'
        js += self._jsonAtt(option_type)
        for cp in self.pComposant:
            js += cp.json(self.option)
            if js[-1] != ',': js += ","
        if self.option["json_param"] and self.parameter != "null": 
            js += '"' + ES.parameter +'":' + self.parameter + ','
        jsInfo = self._jsonInfo(self.option["json_info_type"], self.option["json_info_nval"],
                            self.option["json_info_box"], self.option["json_info_autre"])
        if jsInfo != "" : js +=  jsInfo + ','
        if js[-1] == ',': js = js[:-1]
        if self.option["json_obs_attrib"]: js += "}"
        if self.option["json_obs_val"]:    js += "}"
        return js
    
    def to_bytes(self):
        '''
        Export in binary format. 
        
        Returns
        -------
        bytes : binary representation of the ES.ESObservation.Observation

        '''
        byt = bytes()
        code_el = ES.codeb[self.classES] 
        byt += struct.pack('<B', (code_el << 5) | self.mAtt[ES.obs_reference])
        if self.setProperty != None: 
            byt += self.setProperty.to_bytes(self.option["json_prp_name"])
        if self.setLocation != None: 
            byt += self.setLocation.to_bytes(self.option["json_loc_name"])
        if self.setDatation != None: 
            byt += self.setDatation.to_bytes(self.option["json_dat_name"])
        if self.setResult != None: 
            propList = [self.setProperty.valueList[i].pType 
                        for i in range(self.setProperty.nValue)]
            byt += self.setResult.to_bytes(False, self.option["json_res_index"], 
                                           self.option["bytes_res_format"], propList)
        return byt
        
    def from_bytes(self, byt):
        '''
        Complete an empty `ES.ESObservation.Observation` with binary data. 
        
        Parameters
        -------
        byt : binary representation of an ES.ESObservation.Observation
        Returns
        -------
        None
        '''
        code_ob = (byt[0] & 0b11100000) >> 5
        self.mAtt[ES.obs_reference] = byt[0] & 0b00011111
        if code_ob != ES.codeb[self.classES]: return
        idx = 1
        while idx < byt.__len__() :
            code_el = (byt[idx] & 0b11100000) >> 5
            #forma =  byt[idx] & 0b00001111
            if   code_el == 1: es = ESSetLocation(pObs=self)
            elif code_el == 2: es = ESSetDatation(pObs=self)
            elif code_el == 3: es = ESSetProperty(pObs=self)
            elif code_el < 6:
                es = ESSetResult(pObs=self)
                if code_el == 5: 
                    propList = [self.setProperty.valueList[i].pType 
                            for i in range(self.setProperty.nValue)]
                else :
                    es.from_bytes(byt[idx:], [])
                    es.majIndex(es.nValue, self.setProperty.nValue, 
                            self.setDatation.nValue, self.setLocation.nValue)
                    propList = [self.setProperty.valueList[es.valueList[i].ind[2]].pType
                            for i in range(es.nValue)]
                    es.__init__()
            else: return
            if code_el < 4 : 
                idx += es.from_bytes(byt[idx:])
            else :
                idx += es.from_bytes(byt[idx:], propList)
    
    def _jsonInfoTypes(self, dcinf):
        ''' Add information's key-value to dict dcinf'''
        dcinf[ES.json_type_obs] = self.mAtt[ES.type]
        if self.setLocation != None :
            if self.setLocation.nValue > 1 : 
                dcinf[ES.json_type_loc] = ES.multi + self.setLocation.mAtt[ES.type]
            else :
                dcinf[ES.json_type_loc] = self.setLocation.mAtt[ES.type]
        if self.setDatation != None :
            if self.setDatation.nValue > 1 : 
                dcinf[ES.json_type_dat] = ES.multi + self.setDatation.mAtt[ES.type]
            else :
                dcinf[ES.json_type_dat] = self.setDatation.mAtt[ES.type]
        if self.setProperty != None :
            if self.setProperty.nValue > 1 : 
                dcinf[ES.json_type_prp] = ES.multi + self.setProperty.mAtt[ES.type]
            else :
                dcinf[ES.json_type_prp] = self.setProperty.mAtt[ES.type]
        if self.setResult != None :
            if self.setResult.nValue > 1 : 
                dcinf[ES.json_type_res] = ES.multi + self.setResult.mAtt[ES.type]
            else :
                dcinf[ES.json_type_res] = self.setResult.mAtt[ES.type]

    def _jsonInfoNval(self, dcinf):
        ''' Add valueList lenght to dict dcinf'''
        if self.setLocation != None : dcinf[ES.json_nval_loc] = self.setLocation.nValue
        if self.setDatation != None : dcinf[ES.json_nval_dat] = self.setDatation.nValue
        if self.setProperty != None : dcinf[ES.json_nval_prp] = self.setProperty.nValue
        if self.setResult   != None : dcinf[ES.json_nval_res] = self.setResult.nValue

    def _jsonInfoBox(self, dcinf):
        ''' Add box informations's key-value to dict dcinf'''
        if self.setLocation != None :
            dcinf[ES.loc_boxMin] = self.setLocation.boxMin.point
            dcinf[ES.loc_boxMax] = self.setLocation.boxMax.point
        if self.setDatation != None :
            dcinf[ES.dat_boxMin] = self.setDatation.boxMin.json(ES.mOption)
            dcinf[ES.dat_boxMax] = self.setDatation.boxMax.json(ES.mOption)

    def _jsonInfoAutre(self, dcinf):
        ''' Add other's information key-value to dict dcinf'''
        dcinf[ES.obs_complet] = self.complet
        dcinf[ES.obs_score] = self.score
        if self.setResult != None :
            dcinf[ES.res_mRate] = self.setResult.measureRate
            dcinf[ES.res_dim] = self.setResult.dim
            dcinf[ES.res_axes] = self.setResult.axes

    def _jsonInfo(self, types, nval, box, autre):
        ''' Create json string with dict datas'''
        dcinf = dict()
        if types :  self._jsonInfoTypes(dcinf)
        if nval :   self._jsonInfoNval(dcinf)
        if box :    self._jsonInfoBox(dcinf)
        if autre:   self._jsonInfoAutre(dcinf)
        ldel =[]
        for k,v in dcinf.items() :
            if type(v) == str and (v == "null" or v =='')   : ldel.append(k)
            if type(v) == list and v == ES.nullCoor         : ldel.append(k) 
        for k in ldel :         del dcinf[k]
        if len(dcinf) == 0 :    return ""
        else :                  return '"' +ES.information + '":' + json.dumps(dcinf)

    @property 
    def nValueObs(self):
        '''list : lenght of `ES.ESObs.ESSetProperty`, `ES.ESObs.ESSetDatation`, 
                `ES.ESObs.ESSetLocation`, `ES.ESObs.ESSetResult`.'''
        nPrp = nDat = nLoc = nRes = 0
        if self.setResult   != None: nRes = self.setResult.nValue
        if self.setLocation != None: nLoc = self.setLocation.nValue
        if self.setDatation != None: nDat = self.setDatation.nValue
        if self.setProperty != None: nPrp = self.setProperty.nValue
        return [nPrp, nDat, nLoc, nRes]

    def iloc(self, idat, iloc, iprp):
        '''
        Return the `ES.ESValue` values for an `ES.ESValue.ESIndexValue`. 

        Parameters
        ----------
        idat, iloc, iprp : ES.ESValue.ESIndexValue

        Returns
        -------
        dictionnary, ES.ESValue of each ES.ESObs
        '''
        if not self.complet : return dict()
        dic = dict()
        if self.setDatation != None and idat < self.setDatation.nValue: 
            dic[ES.dat_classES] = self.setDatation.valueList[idat].json(self.option)
        if self.setLocation != None and iloc < self.setLocation.nValue: 
            dic[ES.loc_classES] = self.setLocation.valueList[iloc].json(self.option)
        if self.setProperty != None and iprp < self.setProperty.nValue: 
            dic[ES.prp_classES] = self.setProperty.valueList[iprp].json(self.option)
        if self.setResult != None : 
            for i in range(self.setResult.nValue) : 
                if self.setResult.valueList[i].ind == [idat, iloc, iprp] : 
                    dic[ES.res_classES] = self.setResult.valueList[i].json(self.option)
        return dic
    
    @property
    def typeObs(self):
        '''
        string : Observation type (calculated from ES.ESSetResult diam and ES.ESObservation.Observation score)
        '''
        [nPrp, nDat, nLoc, nRes] = self.nValueObs
        self.score = min(max(min(nPrp, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2), -1), 229);
        if self.setResult == None or (self.setResult.error or self.setResult.getMaxIndex() == -1 or \
           self.setResult.nInd[0] > nDat or self.setResult.nInd[1] > nLoc or self.setResult.nInd[2] > nPrp):
               return ES.obsCat[-1]
        if self.score == 22  and self.setResult.dim == 2:	self.score = 23
        if self.score == 122 and self.setResult.dim == 2:	self.score = 123
        if self.score == 202 and self.setResult.dim == 2:	self.score = 203
        if self.score == 212 and self.setResult.dim == 2:	self.score = 213
        if self.score == 220 and self.setResult.dim == 2:	self.score = 223
        if self.score == 221 and self.setResult.dim == 2:	self.score = 224
        if self.score == 222 and self.setResult.dim == 3:	self.score = 228
        if self.score == 222 and self.setResult.dim == 2 and 2 in self.setResult.axes:	self.score = 225
        if self.score == 222 and self.setResult.dim == 2 and 1 in self.setResult.axes:	self.score = 226
        if self.score == 222 and self.setResult.dim == 2 and 0 in self.setResult.axes:	self.score = 227
        return ES.obsCat[self.score]

    @staticmethod
    def _sortAlign(npInd, list1, ind1, ind2):
        return [int(npInd[list(npInd[:,ind1]).index(i),:][ind2])  for i in list1]    
    
    def full(self, maj=True) : 
        '''
        Add empty `ES.ESValue.ResultValue` to have a 'complete' `ES.ESObservation.Observation`

        Parameters
        ----------
        maj : boolean, optional
            If True, add value to Observation, else return listValue. The default is True.
        Returns
        -------
        empty list if maj is True, else `ES.ESObs.ESSetResult` listValue.
        '''
        return self.setResult.full(maj)
    
    def sort(self, order = 'dlp', cross = True, sort = [[], [], []]): 
        '''
        Modify the order of `ES.ESValue`.

        Parameters
        ----------
        order : string, optional
            Ordered list to follow (d:dat, l:loc, p:prp). The default is 'dlp'.
        cross : boolean, optional
            If True, synchronize the order to have a less dimension. The default is True.
        sort : list, optional
            If empty, order is follow, if not sorting follows the list provided. The default is empty [[], [], []].
        Returns
        -------
        None.
        '''
        if self.setResult == None or not self.setResult.isIndex() : return
        tr = tri = [[], [], []]
        orde = [ES.nax[order[0]], ES.nax[order[1]], ES.nax[order[2]]]
        # ordre de tri de chacun des axes
        for i in range(3) : tri[i] = self._sortSet(i, sort[i], False)
        npInd = np.array(self.setResult.vListIndex)
        if cross:
            for ax in self.setResult.axes : 
                if ax > 100 : 
                    tri[orde[1]] = self._sortAlign(npInd, tri[orde[0]], orde[0], orde[1])
                    tri[orde[2]] = self._sortAlign(npInd, tri[orde[0]], orde[0], orde[2])
                elif ax > 9 :
                    (first, second) = (ax//10, ax%10)
                    if orde.index(second) < orde.index(first) : (first, second) = (second, first)
                    tri[second] = self._sortAlign(npInd, tri[first], first, second)
        for i in range(3) : tr[i] = self._sortSet(i, tri[i])
        for resVal in self.setResult.valueList :
            for i in range(3) : resVal.ind[i] = tr[i].index(resVal.ind[i])
        self.setResult.sort()
    
    def _sortSet(self, ax, tri = [], update = True):
        if ax == 0 and self.setDatation != None : return self.setDatation.sort(tri, update)
        if ax == 1 and self.setLocation != None : return self.setLocation.sort(tri, update)
        if ax == 2 and self.setProperty != None : return self.setProperty.sort(tri, update)
        return [0]
    
    def majType(self, order = 'dlp'):
        '''
        Generate the `ES.ESObservation.Observation` and associates `ES.ESObs` 
        characteristics (e.g. complet, score, dim...) and the index for `ES.ESValue.ResultValue` data.
        
        Parameters
        ----------
        order : String, optional
            Result ordering for result without index. The order is define with
            three letters : l (location), d (datation), p (property). The default is 'dlp'.
        Returns
        -------
        None.
        '''
        [nprp, ndat, nloc, nRes] = self.nValueObs
        nPrp = max(1, nprp)
        nDat = max(1, ndat)
        nLoc = max(1, nloc)
        if len(order) == 3 : 
            self.complet = nRes == nLoc * nDat * nPrp \
                        or nRes == nDat * nPrp == nDat * nLoc \
                        or nRes == nLoc * nPrp == nLoc * nDat \
                        or nRes == nPrp * nLoc == nPrp * nDat \
                        or nRes == nLoc == nDat == nPrp
        if len(order) == 2 : 
            self.complet = nRes == nDat * nPrp == nDat * nLoc \
                        or nRes == nLoc * nPrp == nLoc * nDat \
                        or nRes == nPrp * nLoc == nPrp * nDat \
                        or nRes == nLoc == nDat == nPrp
        if len(order) == 1 : 
            self.complet = nRes == nLoc == nDat == nPrp
        
        if self.complet: self.setResult.majIndex(nRes, nPrp, nDat, nLoc, order)
        if self.setResult   != None: self.setResult.  analyse()
        if self.setLocation != None: self.setLocation.analyse()
        if self.setDatation != None: self.setDatation.analyse()
        self.mAtt[ES.type] = self.typeObs

    def _xlist(self):
        xList = {}
        if self.setLocation != None: 
            xList['loc']    = self.setLocation.to_numpy()
            xList['locstr'] = self.setLocation.to_numpy(func = LocationValue.json)
            xList['loclon'] = self.setLocation.to_numpy(func = LocationValue.vPointX)
            xList['loclat'] = self.setLocation.to_numpy(func = LocationValue.vPointY)
            xList['locnam'] = self.setLocation.to_numpy(func = LocationValue.vName)
            xList['locran'] = np.arange(len(xList['loc']))
        if self.setDatation != None: 
            xList['dat']    = self.setDatation.to_numpy()
            xList['datstr'] = self.setDatation.to_numpy(func = DatationValue.json)
            xList['datnam'] = self.setDatation.to_numpy(func = DatationValue.vName)
            xList['datran'] = np.arange(len(xList['dat']))
        if self.setProperty != None: 
            xList['prp']    = self.setProperty.to_numpy()
            xList['prpstr'] = self.setProperty.to_numpy(func = PropertyValue.json)
            xList['prpnam'] = self.setProperty.to_numpy(func = PropertyValue.vName)
            xList['prpran'] = np.arange(len(xList['prp']))
        if self.setResult  != None: 
            xList['res']    = self.setResult.to_numpy()
            xList['resval'] = self.setResult.to_numpy(func = ResultValue.to_float)
            xList['resstr'] = self.setResult.to_numpy(func = ResultValue.json)
            xList['resnam'] = self.setResult.to_numpy(func = ResultValue.vName)
            xList['resran'] = np.arange(len(xList['res']))
        return xList

    def _xAttrs(self) :
        attrs = ES.xattrs
        attrs['info']   = json.loads("{" + self._jsonInfo(True, False, True, False) + "}")["information"]
        return attrs

    def _axeCoor(self, nValAxe) :
        for ax in self.setResult.axes :
            if ax > 100 : return ax
            if ax < 9 and nValAxe == ax : return ax
            elif ax > 9 and (nValAxe == ax//10 or nValAxe == ax%10) : return ax
        return None
    
    def _xCoord(self, xList, attrs, dataArray, complet, numeric) :
        #nax = {'dat' : 0, 'loc' : 1, 'prp' : 2}
        coord = {}
        for key, val in xList.items() :
            if key[:3] != 'res' and self._axeCoor(ES.nax[key[:3]]) != None \
                and (complet or (not complet and len(key) == 3)):
                coord[key] = ([ES.axes[self._axeCoor(ES.nax[key[:3]])]], val, attrs[key[:3]])
                if key == 'loclon' : coord[key] = (coord[key][0], val, attrs['lon'])
                if key == 'loclat' : coord[key] = (coord[key][0], val, attrs['lat'])
        for ax in self.setResult.axes :
            if ax > 9 :
                le = len(xList[ES.axes[ax%10]])
                coord[ES.axes[ax]] = ([ES.axes[ax]], np.arange(le))
                if ax > 100 : lis = [str(xList['datstr'][i]) + xList['locstr'][i] + 
                                     xList['prpstr'][i] for i in range(le)]
                else : lis = [str(xList[ES.axes[ax%10]+'str'][i]) + 
                              str(xList[ES.axes[ax//10]+'str'][i]) for i in range(le)]
                coord[ES.axes[ax]+'str'] = ([ES.axes[ax]], lis)
        if numeric :
            if 'loc' in coord.keys() : coord['loc'] = (coord['loc'][0], xList['locran'], coord['loc'][2])
            if 'dat' in coord.keys() : coord['dat'] = (coord['dat'][0], xList['datstr'], coord['dat'][2])
            if 'prp' in coord.keys() : coord['prp'] = (coord['prp'][0], xList['prpran'], coord['prp'][2])
        return coord
    

    def to_xarray(self, dataArray = True, sort = True, complet = False, info = False, numeric = False):
        '''
        Convert `ES.ESObservation.Observation` to DataArray or DataSet with the smallest dimension. 
        
        Parameters
        ----------
        dataArray : Boolean, optional
            DataArray ou DataSet. The default is True.
        sort : Boolean, optional
            Sort along an axis. The default is True.
        complet : Boolean, optional
            Generate all the DataArray.Coords or only one. The default is False.
        info : Boolean, optional
            Generate a specific Coords with Observation characteristics. The default is False.
        numeric : Boolean, optional
            Generate a numeric DataArray.Values. The default is False.
        Returns
        -------
        xarray.DataArray or xarray.DataSet.
        '''
        if self.setResult.getMaxIndex() == -1 : return None
        if sort : self.sort()
        xList = self._xlist()
        attrs = self._xAttrs()
        coord = self._xCoord(xList, attrs, dataArray, complet, numeric = False)
        self.setResult.triAxe()
        dims = [ES.axes[ax] for ax in self.setResult.axes]
        if numeric  : xres = xList['resval']
        else        : xres = xList['res']
        if dataArray and info :
            return xr.DataArray(xres, coord, dims, attrs=attrs['info'])
        elif dataArray and not info :
            return xr.DataArray(xres, coord, dims)
        return None

    def voxel(self, sort=False):
        '''
        Visualize `ES.ESValue.ResultValue` in a cube with voxels.
        
        Parameters
        ----------
        sort : Boolean, optional
            Sort along axis. The default is False.
        Returns
        -------
        None.
        '''
        if self.setResult.getMaxIndex() == -1 : return        
        obc = copy.deepcopy(self)
        obc.setResult.full()
        obx = obc.to_xarray(numeric = True, complet=True, sort=sort)
        obp = obx>=0
        obp.set_index(loc='locran', dat='datran', prp='prpran')
        ax = plt.figure().add_subplot(projection='3d')
        ax.voxels(obp, edgecolor='k')
        ax.set_xticks(np.arange(self.setDatation.nValue))
        ax.set_yticks(np.arange(self.setLocation.nValue))
        ax.set_zticks(np.arange(self.setProperty.nValue))
        ax.set(xlabel='dat (index)', ylabel='loc (index)', zlabel='prp (index)')
        plt.show()
        
    def plot(self, switch = False, line = True, sort = True, size = 5, marker='o'):
        '''
        This function visualize an `ES.ESObservation.Observation` with line or colormesh.
        
        Parameters
        ----------
        switch : Boolean, optional
            Switch between x and y axis. The default is False.
        line : Boolean, optional
            Choice line or colormesh. The default is True.
        sort : Boolean, optional
            Sort along an axis. The default is True.
        size : Integer, optional
            Size of the figure to plot. The default is 5.
        marker : Character, optional
            Synbol for each point. The default is 'o'.
        Returns
        -------
        None.
        '''
        if self.setResult.getMaxIndex() == -1 : return
        obx = self.to_xarray(numeric = True, complet=True, sort=sort)
        if len(obx.dims) == 1:
                obx.plot.line(x=obx.dims[0]+'str', size=size, marker=marker)
        elif len(obx.dims) == 2:
            order = [0,1]
            ext = ['', '']
            for i in (0,1):
                if obx.dims[i] == 'dat' : ext[i] = 'str'
                elif str(obx.coords[obx.dims[i]].dtype)[0] != 'i': ext[i] = 'ran'
            if switch : [order[0], order[1]] = [order[1], order[0]]
            if line :   
                obx.plot.line(x=obx.dims[order[0]]+ 'str', 
                              xticks=list(obx.coords[obx.dims[0]+'str'].values), 
                              #hue=obx.dims[order[1]]+ext[order[1]], size=size, marker=marker)
                              hue=obx.dims[order[1]]+'str', size=size, marker=marker)
            else: 
                obx.plot(x=obx.dims[order[0]]+ext[order[0]], y=obx.dims[order[1]]+ext[order[1]], 
                         xticks=list(obx.coords[obx.dims[order[0]]+ext[order[0]]].values), 
                         yticks=list(obx.coords[obx.dims[order[1]]+ext[order[1]]].values), 
                         size = size)
            #τobg = self.to_geoDataFrame()
            #for i in range(len(self.setProperty)): obg.plot(obg.columns.array[i], legend=True)
        elif len(obx.dims) == 3:       
            if line :
                obx = obx.set_index(prp = "prpstr", dat="datstr", loc="locstr")
                obx.sortby(["dat","loc","prp"]).plot.line(x="dat", col="prp", 
                                                          xticks=list(obx.coords['dat'].values), 
                                                          col_wrap=2, size=size,
                                                          marker=marker)
            else :
                obx = obx.set_index(prp = "prpstr", dat="datstr", loc="locran")
                obx.sortby(["dat","loc","prp"]).plot(x="dat", y="loc", col="prp", 
                                                     col_wrap=2, size=size, 
                                                     xticks=list(obx.coords['dat'].values), 
                                                     yticks=list(obx.coords['loc'].values))
            #obg = self.to_geoDataFrame()
            #for i in range(len(self.setProperty)): obg.plot(obg.columns.array[i], legend=True)
            #plt.legend(obx.coords['locstr'].to_index().to_list())
        plt.show()

    def to_dataFrame(self):
        if self.setResult.dim > 0 : return self.to_xarray(False).to_dataframe()
        else : return None

    def choropleth(self):
        if self.setResult.dim == 1 or self.setResult.dim // 10 == 1:
            m = folium.Map(location=self.setLocation.valueList[0].coorInv, zoom_start=6)
            folium.PolyLine(
                list(self.setLocation.valueList[i].coorInv for i in range(len(self.setLocation.valueList)))
            ).add_to(m)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name="test choropleth",
                data=self.to_dataFrame(),
                key_on="feature.id",
                #columns=["point", json.loads(self.setProperty[0].json(False))[ES.prp_propType]],
                columns=["point", json.loads(self.setProperty[0].json(ES.mOption))[ES.prp_propType]],
                fill_color="BuGn",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="test choropleth"
            ).add_to(m)
            folium.LayerControl().add_to(m)
            return m
        return None