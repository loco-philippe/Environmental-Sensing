# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: Philippe@loco-labs.io

The `ES.ESObservation` module contains the main class
of Environmental Sensing : `Observation` class.

"""
from ESObs import ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult
from ESElement import ESElement
from ESconstante import ES
from ESValue import LocationValue, DatationValue, PropertyValue, \
    ResultValue
from shapely.geometry import shape
from datetime import datetime
import json, folium, struct, copy, csv
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


_EsObs: list = [ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult]
'''ordered list for classES '''  

_EsValue: list = [DatationValue, LocationValue, PropertyValue]
'''ordered list for ESValue '''  

_EsObsDict: dict = {ES.dat_classES : ESSetDatation, 
                   ES.loc_classES : ESSetLocation,
                   ES.prp_classES : ESSetProperty,
                   ES.res_classES : ESSetResult}
'''dict classES : ESObs '''  
        
class Observation(ESElement):
    """
    An `Observation` is made up of objects from the `ES.ESObs` class
     which each describe a dimension of this object.
    
    *Attributes (for @property see methods)* :

    - **complet** : Boolean, True if the number of ResultValue is consistent with 
    the number of LocationValue, DatationValue and PropertyValue
    - **option** : Dictionnary with options
    - **userAtt** : namedValue dictionnary
    - **name** : textual description
    - **mAtt** : namedValue dictionnary (inherited from ESElement)
    - **parameter** : namedValue dictionnary (inherited from ESElement)
    - **mAtt[reference]** : number of the reference Observation used to complete the actual Observation

    The methods defined in this class are : 
    
    *property (getters)*
    
    - `Observation.setLocation`
    - `Observation.setDatation`
    - `Observation.setProperty`
    - `Observation.setResult`
    - `Observation.bounds`
    - `Observation.jsonFeature`
    - `Observation.score`
    - `Observation.typeObs`
    - `Observation.nValueObs`
    - `Observation.json`
    
    *add value*
    
    - `Observation.append`
    - `Observation.appendList`
    - `Observation.appendObs`
    - `Observation.addESObs`
    - `Observation.addAttributes`
    - `Observation.addResultValue`
    - `Observation.addListResultValue`
    - `Observation.addValue`
    - `Observation.addListValue`
    
    *update value*
    
    - `Observation.majList`
    - `Observation.majType`
    - `Observation.majValue`
    
    *selecting*
    
    - `Observation.indexLoc`
    - `Observation.iLoc`
    - `Observation.loc`
    
    *management*
    
    - `Observation.extend`
    - `Observation.full`
    - `Observation.sort`
    - `Observation.find`
    
    *visualization*
    
    - `Observation.voxel`
    - `Observation.plot`
    - `Observation.view`
    - `Observation.choropleth`
    
    *exports - imports*
    
    - `Observation.to_csv`
    - `Observation.to_dataFrame`
    - `Observation.to_xarray`
    - `Observation.to_json`
    - `Observation.from_json`
    - `Observation.to_bytes`
    - `Observation.from_bytes`

    """
    def __init__(self, *args, order = 'dlp', **kwargs):
        '''
        Several Observation creation modes :
        
        - Observation(dictESValue1, dictESValue2, ...) where dictESValue = {ESValuename : value}
        - Observation({ESObs1, ESObs2, ...})
        - Observation(ObsJSON)
        - Observation([ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult]) where ESSet can be :
            [ESValue1, ESValue2,...] or [ESValue] or ESValue
        - Observation(datation=ESSetDatation, location=ESSetLocation,
                      property=ESSetProperty, result=ESSetResult)
        
        *Note : the parameter 'order' is used only when an ESSetResult without Index is in arguments. 
        It indicates the order for the Index creation ('d' for Datation, 'l' for Location, 'p' for Property).*
        '''
        ESElement.__init__(self)
        self.name = "observation du " + datetime.now().isoformat()
        self.option = ES.mOption.copy()
        self.mAtt[ES.obs_reference] = 0
        self.complet = False
        self.mAtt[ES.obs_resultTime] = "null"
        self.classES = ES.obs_classES
        self.typeES = ES.obs_typeES
        self.mAtt[ES.obs_id] = "null"
        self._initESObs(*args, **kwargs)
        self.majType(order)
        self.parameter = "null"

    @property
    def __geo_interface__(self):
        '''dict (@property) : geometry (see shapely)'''
        if self.setLocation : 
            collec = self.setLocation.vListShap[0]
            first = True
            for shap in self.setLocation.vListShap :
                if not first : collec = collec.union(shap)
                first = False
            return collec.__geo_interface__
        else : return ""

    def __copy__(self):
        ''' Copy all the data, included ESObs ans ESValue'''
        return copy.deepcopy(self)

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
        equal = self.option["add_equal"]
        if other.setResult != None and other.setResult.maxIndex > -1:
            for resVal in other.setResult.valueList:
                ndat = self.addValue(other.setDatation.valueList[resVal.ind[idat]], equal)
                nloc = self.addValue(other.setLocation.valueList[resVal.ind[iloc]], equal)
                nprp = self.addValue(other.setProperty.valueList[resVal.ind[iprp]], equal)
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
    

    def addAttributes(self, js):        # !!! methodes externes
        '''
        Add informations attached to `Observation`

        *Parameters*
        
        - **js** : Dict - Keys are Observation keys or users keys.
        
        *Returns*
        
        - **None**
        '''
        if type(js) != dict: return
        for k, v in js.items():
            if (ESElement.isESAtt(ES.obs_classES, k) or ESElement.isUserAtt(k)) \
                and k != ES.type : self.mAtt[k] = v
            if k == ES.parameter: 
                try:  self.parameter = json.dumps(v)
                except:  self.parameter = "null"

    def addESObs(self, js, classES = None) :
        '''
        Add one or more new `ES.ESObs` attached to `Observation`. 
        The ES.ESObs child class is defined by classES or if None by the js structure.

        *Parameters*
        
        - **js** : ES.ESObs compatible type
        - **classES** : string, optional (default None) - value of the ES.ESObs ESclass attributes
        
        *Returns*
        
        - **None**
        '''
        if classES in (None, ES.dat_classES) and ESElement.isESObs(ES.dat_classES, js) \
            and self.setDatation == None: ESSetDatation(pObs=self, jObj=js)
        if classES in (None, ES.loc_classES) and ESElement.isESObs(ES.loc_classES, js) \
            and self.setLocation == None: ESSetLocation(pObs=self, jObj=js)
        if classES in (None, ES.prp_classES) and ESElement.isESObs(ES.prp_classES, js) \
            and self.setProperty == None: ESSetProperty(pObs=self, jObj=js)
        if classES in (None, ES.res_classES) and ESElement.isESObs(ES.res_classES, js) \
            and self.setResult   == None: ESSetResult  (pObs=self, jObj=js)

    def addListResultValue(self, listEsValue):
        '''
        Add a list of new `ES.ESValue.ResultValue` in the `ES.ESObs.ESSetResult`.

        *Parameters*
        
        - **listEsValue** : list of `ES.ESValue.ResultValue`
        
        *Returns*
        
        - **None**
        '''
        if type(listEsValue) != list : return
        if self.setResult == None: resSet = ESSetResult(pObs=self)
        else: resSet = self.setResult
        for val in listEsValue : resSet.addValue(ResultValue, ResultValue(val))

    def addListValue(self, ValueClass, listEsValue, equal="full"):
        '''
        Add a list of new `ES.ESValue` in a `ES.ESValue.ESSet`.

        *Parameters*
        
        - **ValueClass** : name of the selected class ES.ESValue
        - **listEsValue** : list of ES.ESValue
        
        *Returns*
        
        - **None**
        '''
        for val in listEsValue : self.addValue(ValueClass(val), equal )
        
    def addResultValue(self, esValue, equal="full"):
        '''
        Add a new `ES.ESValue.ResultValue` in the `ES.ESObs.ESSetResult`

        *Parameters*
        
        - **esValue** : data compatible with ES.ESValue.ResultValue
        - **equal** : criteria used to compare ESValue ('full', 'name', 'value')
        
        *Returns*
        
        - **Int** : last index in the `ES.ESValue.ESSet` valueList.
        '''
        return self.setResult.addValue(esValue, equal)
    
    def addValue(self, esValue, equal="full"):
            '''
            Add a new `ES.ESValue` in the `ES.ESValue.ESSet`
    
            *Parameters*
            
            - **esValue** : ES.ESValue
            - **equal** : criteria used to compare ESValue ('full', 'name', 'value')
            
            *Returns*
            
            - **Int** : last index in the `ES.ESValue.ESSet` valueList.
            '''
            if type(esValue)== PropertyValue:
                if self.setProperty == None: ESSetProperty(pObs=self)
                return self.setProperty.addValue(esValue, equal)
            elif type(esValue)== LocationValue:
                if self.setLocation == None: ESSetLocation(pObs=self)
                return self.setLocation.addValue(esValue, equal)
            elif type(esValue)== DatationValue:
                if self.setDatation == None: ESSetDatation(pObs=self)
                return self.setDatation.addValue(esValue, equal)
            else: return None
            
    def append(self, dat, loc, prp, res, equal="full") :
        '''
        Add a new `ES.ESValue.ResultValue` with or without other `ESObs`
        
        *Parameters*
        
        - **dat, loc, prp** :
        
            integer for the index of an existant `ES.ESValue.ESIndexValue`  
            or compatible Value for an existing or a new `ES.ESValue`
            
        - **res** : new `ES.ESValue.ResultValue`
        
        *Returns*
        
        - **int** : last index in the `ES.ESValue.ESSet` valueList.
        '''
        arg = [dat, loc, prp]
        ind = [0,0,0]
        for i in range(3) :
            if type(arg[i]) == int : ind[i] = arg[i]
            else : ind[i] = self.addValue(_EsValue[i](arg[i]), equal)
        self._addValueObservation(ind[0], ind[1], ind[2], res)
        self.majType()
        
    def appendList(self, listDat, listLoc, listPrp, listVal, equal="full"):
        '''
        Add a list of new `ES.ESValue.ResultValue` 
        
        *Parameters* (see appen function)
        
        - **listVal** : list of ES.ESValue.ResultValue compatible type
        - **listDat, listLoc, listPrp** : list of index or Value to define a `ES.ESValue`
        
        *Returns*

        - **None**
        '''
        if len(listVal)==len(listDat)==len(listLoc)==len(listPrp) :
            for i in range(len(listVal)) :
                self.append(listDat[i], listLoc[i], listPrp[i], listVal[i])

    def appendObs(self, obs, equal="full") :
        '''
        Add an `Observation` as a new `ES.ESValue.ResultValue` with other `ES.ESValue`
        
        *Parameters*
        
        - **obs** : Observation
        
        *Returns*
        
        - **int** : last index in the `ES.ESValue.ESSet` valueList.
        '''
        #arg = [obs.setDatation.boundingBox, obs.setLocation.boundingBox, 
        #       obs.setProperty[0]]
        ind = [0,0,0]
        arg = obs.bounds
        for i in range(3) :
            if type(arg[i]) == int : ind[i] = arg[i]
            else : ind[i] = self.addValue(_EsValue[i](arg[i]), equal)
        self._addValueObservation(ind[0], ind[1], ind[2], obs)
        self.majType()
        
    @property
    def bounds(self):
        '''tuple (@property) : Observation boundingBox (xmin, ymin, xmax, ymax).'''
        bound = [None, None, None]
        #if self.setLocation : return shape(self).bounds
        if self.setDatation : bound[0] = self.setDatation.boundingBox
        if self.setLocation : bound[1] = self.setLocation.boundingBox
        if self.setProperty : bound[2] = self.setProperty[0]
        return bound

    def choropleth(self, name="choropleth"):
        '''
        Display `Observation` on a folium.Map (only with dim=1)

        - **name** : String, optionnal (default 'choropleth') - Name of the choropleth
            
        *Returns*
        
        - **folium.Map**
        '''
        if self.setResult.dim == 1 or self.setResult.dim // 10 == 1:
            m = folium.Map(location=self.setLocation.valueList[0].coorInv, zoom_start=6)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name=name,
                data=self.to_dataFrame(complet=True, numeric=True),
                key_on="feature.id",
                columns = ['locran', 'Observation'],
                fill_color="OrRd",
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight = 2,
                legend_name="test choropleth"
            ).add_to(m)
            folium.PolyLine(
                self.setLocation.vList(LocationValue.vPointInv)
            ).add_to(m)
            folium.LayerControl().add_to(m)
            return m
        return None

    def extend(self, other):
        '''
        Copy `ES.ESObs` from other to self (if it daesn't exist)

        *Parameters*
        
        - **other** : object Observation to copy
        
        *Returns*
        
        - **None**
        '''
        for p in other.pComposant :
            if self.element(p.classES) == None : self.addComposant(p)
        self.majType()    
        
    def find(self, crit = None): 
        '''
        Finds `ES.ESValue` that meets a given criteria.

        *Parameters*
        
        - **crit** : to be define.
         
        *Returns*
        
        - **Observation** : New Observation
        '''
        return None
    
    def from_bytes(self, byt, order='dlp'):
        '''
        Complete an empty `Observation` with binary data. 
        
        *Parameters*
        
        - **byt** : binary representation of an Observation
        - **order** : string - indicates the order for the Index creation 
        ('d' for Datation, 'l' for Location, 'p' for Property).*
        
        *Returns*
        
        - **None**
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
                    if self.setProperty != None :
                        propList = [self.setProperty.valueList[i].pType 
                                    for i in range(self.setProperty.nValue)]
                    else : propList = []
                else :
                    [nPrp, nDat, nLoc, nRes] = self.nValueObs
                    es.from_bytes(byt[idx:], [])
                    es.majIndex(es.nValue, nPrp, nDat, nLoc)
                    if self.setProperty != None :
                        propList = [self.setProperty.valueList[es.valueList[i].ind[2]].pType 
                                    for i in range(self.setProperty.nValue)]
                    else : propList = []
                    es.__init__()
            else: return
            if code_el < 4 : 
                idx += es.from_bytes(byt[idx:])
            else :
                idx += es.from_bytes(byt[idx:], propList)
        self.majType(order)
    
    def from_json(self, js, order='dlp'):
        '''
        Complete an `Observation` with json data. 
        
        *Parameters*
        
        - **js** : string - ObsJSON data
        - **order** : string - indicates the order for the Index creation 
        ('d' for Datation, 'l' for Location, 'p' for Property).*
        
        *Returns*
        
        - **None**
        '''
        try: dic=json.loads(js)
        except: return
        self._initDict(dic)
        self.majType(order)
                
    def full(self, maj=True, allAxes=True) : 
        '''
        Add empty `ES.ESValue.ResultValue` to have a 'complete' `Observation`

        *Parameters*
        
        - **maj** : boolean (default True) - If True, add value to 
        Observation, else return valueList. The default is True.
        - **allAxes** : boolean (default True) - If True, axes are 
        completed with empty ES.ESObs 
        
        *Returns*
        
        - **list** : empty list if maj is True, else `ES.ESObs.ESSetResult` value.List
        '''
        if allAxes :
            if self.setDatation == None: ESSetDatation(pObs=self)
            if self.setLocation == None: ESSetLocation(pObs=self)
            if self.setProperty == None: ESSetProperty(pObs=self)        
        return self.setResult.full(maj)
    
    def iLoc(self, idat, iloc, iprp, json=True):
        '''
        Return the `ES.ESValue` values for an `ES.ESValue.ESIndexValue`. 

        *Parameters*
        
        - **idat, iloc, iprp** : ES.ESValue.ESIndexValue
        - **json** : Boolean (default True) - Return JSON string if True

        *Returns*
        
        - **dict** : ES.ESValue or JSON of each ES.ESObs
        '''
        if not self.complet or type(idat) != int or type(iloc) != int or type(iprp) != int: return dict()
        dic = dict()
        if self.setDatation != None and idat < self.setDatation.nValue: 
            if json : dic[ES.dat_classES] = self.setDatation.valueList[idat].json(**self.option)
            else : dic[ES.dat_classES] = self.setDatation.valueList[idat]
        if self.setLocation != None and iloc < self.setLocation.nValue: 
            if json : dic[ES.loc_classES] = self.setLocation.valueList[iloc].json(**self.option)
            else: dic[ES.loc_classES] = self.setLocation.valueList[iloc]
        if self.setProperty != None and iprp < self.setProperty.nValue: 
            if json : dic[ES.prp_classES] = self.setProperty.valueList[iprp].json(**self.option)
            else : dic[ES.prp_classES] = self.setProperty.valueList[iprp]
        if self.setResult != None : 
            for i in range(self.setResult.nValue) : 
                if self.setResult.valueList[i].ind == [idat, iloc, iprp] : 
                    if json : dic[ES.res_classES] = self.setResult.valueList[i].json(**self.option)
                    else : dic[ES.res_classES] = self.setResult.valueList[i]
        return dic
    
    def indexLoc(self, esValue, string=True):
        '''
        Return the index of a `ES.ESValue` in a `ES.ESObs`
        
        *Parameters*
        
        - **esValue** : `ES.ESValue`, 
        - **string** : Boolean (default True) - Return type (JSON if True, dict if False)
        
        *Returns*

        - **dict or string** : {'full' : indFull, 'name' : indName, 'value' : indValue }
            - indFull : integer for the first index value with name and value equality
            - indName : integer for the first index value with name equality
            - indFull : integer for the first index value with value equality
        '''        
        if type(esValue)== PropertyValue and self.setProperty != None:
            ind = self.setProperty.indexLoc(esValue)
        elif type(esValue)== LocationValue and self.setLocation != None: 
            ind = self.setLocation.indexLoc(esValue)
        elif type(esValue)== DatationValue and self.setDatation != None: 
            ind = self.setDatation.indexLoc(esValue)
        elif type(esValue)== ResultValue and self.setResult != None: 
            ind = self.setResult.indexLoc(esValue)
        else: return None   
        if string : return json.dumps(ind)
        else : return ind
            
    @property
    def json(self):
        ''' string (@property) : ObsJSON - complete JSON Observation whit index 
        and whitout informations'''
        return self.to_json(json_string=True, json_info=False, json_res_index=True,
                            json_param=True)
    
    @property
    def jsonFeature(self):
        ''' string (@property) : "FeatureCollection" with ESSetLocation geometry'''
        if self.setLocation : 
            geo = self.__geo_interface__
            if geo['type'] == "MultiPolygon": typ = "Polygon"
            else : typ = "Point"
            lis = list(dict((("type", typ), ("coordinates", geo['coordinates'][i]))) for i in range(len(geo['coordinates'])))
            fea = list(dict((("type","Feature"), ("id", i), ("geometry", lis[i]))) for i in range(len(geo['coordinates'])))
            return json.dumps(dict((("type","FeatureCollection"), ("features",fea))))            
        else: return ''  
            
    def loc(self, valDat, valLoc, valPrp, json=True):
        '''
        Return the `ES.ESValue` values for a DatationValue, LocationValue, PropertyValue. 

        *Parameters*
        
        - **valdat, valloc, valprp** : DatationValue, LocationValue, PropertyValue

        *Returns*
        
        - **dict** : ES.ESValue of each ES.ESObs
        '''
        if not self.complet : return dict()
        return self.iLoc(self.setDatation.indexLoc(valDat)['full'],
                         self.setLocation.indexLoc(valLoc)['full'], 
                         self.setProperty.indexLoc(valPrp)['full'])

    def majList(self, ValueClass, listVal, name=False):
        '''
        Modify a list of one attribute (name or value) in an `ES.ESObs`

        *Parameters*
        
        - **ValueClass** : class ES.ESValue 
        - **listVal** : list of values
        - **name** : boolean (default True) - True for 'name' and False for 'value'
        
        *Returns*
        
        - **None**
        '''
        if ValueClass == DatationValue and self.setDatation != None : 
            self.setDatation.majList(listVal, name)
        elif ValueClass == LocationValue and self.setLocation != None : 
            self.setLocation.majList(listVal, name)
        elif ValueClass == PropertyValue and self.setProperty != None : 
            self.setProperty.majList(listVal, name)
        elif ValueClass == ResultValue and self.setResult != None : 
            self.setResult.majList(listVal, name)

    def majType(self, order = 'dlp'):
        '''
        Generate the `Observation` and associates `ES.ESObs` 
        characteristics (e.g. complet, score, dim...) and the index for `ES.ESValue.ResultValue` data.
        
        *Parameters*
        
        - **order** : String (default 'dlp') - Result ordering for result without index. 
        The order is define with three letters : l (location), d (datation), p (property).
            
        *Returns*
        
        - **None**
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

    def majValue(self, esValue, newEsValue, equal="full"):
        '''
        Update the value of an existing `ES.ESValue` by that of the `ES.ESValue.ESSet`

        *Parameters*
        
        - **esValue** : ESValue
        - **equal** : criteria used to compare ESValue ('full', 'name', 'value')
        
        *Returns*
        
        - **Int** : index in the ESSet valueList.
        '''
        index = None
        if   type(esValue)== PropertyValue and self.setProperty != None : 
            index = self.setProperty.indexLoc(esValue)[equal]
            if index != None: self.setProperty[index].setValue(newEsValue)
        elif type(esValue)== LocationValue and self.setLocation != None : 
            index = self.setLocation.indexLoc(esValue)[equal]
            if index != None: self.setLocation[index].setValue(newEsValue)
        elif type(esValue)== DatationValue and self.setDatation != None : 
            index = self.setDatation.indexLoc(esValue)[equal]
            if index != None: self.setDatation[index].setValue(newEsValue)
        elif type(esValue)== ResultValue and self.setResult != None : 
            index = self.setResult.indexLoc(esValue)[equal]
            if index != None: self.setResult[index].setValue(newEsValue)
        return index
        
    @property 
    def nValueObs(self):
        '''list (@property) : lenght of `ES.ESObs.ESSetProperty`, `ES.ESObs.ESSetDatation`, 
                `ES.ESObs.ESSetLocation`, `ES.ESObs.ESSetResult`.'''
        nPrp = nDat = nLoc = nRes = 0
        if self.setResult   != None: nRes = self.setResult.nValue
        if self.setLocation != None: nLoc = self.setLocation.nValue
        if self.setDatation != None: nDat = self.setDatation.nValue
        if self.setProperty != None: nPrp = self.setProperty.nValue
        return [nPrp, nDat, nLoc, nRes]

    def plot(self, switch = False, line = True, sort = True, size = 5, 
             marker='o', maxname=20):
        '''
        This function visualize an `Observation` with line or colormesh.
        
        *Parameters*
        
        - **switch** : Boolean (default False) - Switch between x and y axis.        
        - **line** : Boolean (default True) - Choice line or colormesh.
        - **sort** : Boolean (defaut True) - Sort along an axis or not.
        - **size** : Int (default 5) - Size of the figure to plot.
        - **marker** : Char (default 'o') - Symbol for each point.
        - **maxname** : String (default 20) - maximum length for string
        
        *Returns*
        
        - **None**
        '''
        if self.setResult.maxIndex == -1 : return
        obx = self.to_xarray(numeric = True, complet=True, sort=sort, maxname=maxname)
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
                              hue=obx.dims[order[1]]+'str', size=size, marker=marker)
            else: 
                try : 
                    obx.plot(x=obx.dims[order[0]]+ext[order[0]], y=obx.dims[order[1]]+ext[order[1]], 
                         xticks=list(obx.coords[obx.dims[order[0]]+ext[order[0]]].values), 
                         yticks=list(obx.coords[obx.dims[order[1]]+ext[order[1]]].values), 
                         size = size)
                except :
                    obx.plot(size=size)
                    
        elif len(obx.dims) == 3:       
            if line :
                obx = obx.set_index(prp = "prpstr", loc="locstr")
                obx.sortby(["dat","loc","prp"]).plot.line(x="dat", col="prp", 
                                                          xticks=list(obx.coords['dat'].values), 
                                                          col_wrap=2, size=size,
                                                          marker=marker)
            else :
                obx = obx.set_index(prp = "prpstr", loc="locran")
                obx.sortby(["dat","loc","prp"]).plot(x="dat", y="loc", col="prp", 
                                                     col_wrap=2, size=size, 
                                                     xticks=list(obx.coords['dat'].values), 
                                                     yticks=list(obx.coords['loc'].values))
        plt.show()
        
    @property
    def score(self):
        '''
        integer (@property) : Observation type (calculated from `ES.ESSetResult` dim 
        and `Observation` nValueObs). The score is a codification of the number of ESValue for each ESObs. 
        E.g., score=122 means one PropertyValue (1), several LocationValue (2), 
        several DatationValue (2)
        '''
        [nPrp, nDat, nLoc, nRes] = self.nValueObs
        score = min(max(min(nPrp, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2), -1), 229);
        if self.setResult == None or (self.setResult.error or self.setResult.maxIndex == -1 or \
           self.setResult.nInd[0] > nDat or self.setResult.nInd[1] > nLoc or self.setResult.nInd[2] > nPrp):
               return score
        if score == 22  and self.setResult.dim == 2:	score = 23
        if score == 122 and self.setResult.dim == 2:	score = 123
        if score == 202 and self.setResult.dim == 2:	score = 203
        if score == 212 and self.setResult.dim == 2:	score = 213
        if score == 220 and self.setResult.dim == 2:	score = 223
        if score == 221 and self.setResult.dim == 2:	score = 224
        if score == 222 and self.setResult.dim == 3:	score = 228
        if score == 222 and self.setResult.dim == 2 and 2 in self.setResult.axes:	score = 225
        if score == 222 and self.setResult.dim == 2 and 1 in self.setResult.axes:	score = 226
        if score == 222 and self.setResult.dim == 2 and 0 in self.setResult.axes:	score = 227
        return score

    @property
    def setDatation(self):  
        '''object `ES.ESObs.ESSetDatation` (@property) if exists, None otherwise.'''
        return self.element(ES.dat_classES)
    
    @property
    def setLocation(self):
        '''object `ES.ESObs.ESSetLocation` (@property) if exists, None otherwise.'''
        return self.element(ES.loc_classES)
    
    @property
    def setProperty(self):  
        '''object `ES.ESObs.ESSetProperty` (@property) if exists, None otherwise.'''
        return self.element(ES.prp_classES)
    
    @property
    def setResult(self):  
        '''object `ES.ESObs.ESSetResult` (@property) if exists, None otherwise.'''
        return self.element(ES.res_classES)

    def sort(self, order = 'dlp', cross = True, sortRes = True, sort = [[], [], []]): 
        '''
        Modify the order of `ES.ESValue`.

        *Parameters*
        
        - **order** : string (default 'dlp') - Ordered list to follow (d:dat, l:loc, p:prp).
        - **cross** : boolean (default True) - If True, synchronize the order 
        to have a less dimension.
        - **sortRes** : boolean (default True) - If True, sort Result.
        - **sort** : list (default [[], [], []]) - If empty, order is follow, 
        if not sorting follows the list provided.
        
        *Returns*
        
        - **None**
        '''
        if self.setResult == None or not self.setResult.isIndex : return
        tr = tri = [[], [], []]
        orde = [ES.nax[order[0]], ES.nax[order[1]], ES.nax[order[2]]]
        # ordre de tri de chacun des axes
        for i in range(3) : tri[i] = self._sortSet(i, sort[i], False)
        npInd = np.array(self.setResult.vListIndex)
        # modification de l'ordre de tri pour les axes liés
        if cross:
            for ax in self.setResult.axes : 
                if ax > 100 : 
                    tri[orde[1]] = self._sortAlign(npInd, tri[orde[0]], orde[0], orde[1])
                    tri[orde[2]] = self._sortAlign(npInd, tri[orde[0]], orde[0], orde[2])
                elif ax > 9 :
                    (first, second) = (ax//10, ax%10)
                    if orde.index(second) < orde.index(first) : (first, second) = (second, first)
                    tri[second] = self._sortAlign(npInd, tri[first], first, second)
        # mise à jour des axes
        for i in range(3) : tr[i] = self._sortSet(i, tri[i])
        # mise à jour des index de result
        for resVal in self.setResult.valueList :
            for i in range(3) : resVal.ind[i] = tr[i].index(resVal.ind[i])
        # tri de result
        if sortRes : self.setResult.sort()
    
    def to_bytes(self):
        '''
        Export in binary format. 
        
        *Returns*
        
        - **bytes** : binary representation of the `Observation`
        '''
        byt = bytes()
        code_el = ES.codeb[self.classES] 
        byt += struct.pack('<B', (code_el << 5) | self.mAtt[ES.obs_reference])
        if self.setDatation != None: 
            byt += self.setDatation.to_bytes(self.option["json_dat_name"])
        if self.setLocation != None: 
            byt += self.setLocation.to_bytes(self.option["json_loc_name"])
        if self.setProperty != None: 
            byt += self.setProperty.to_bytes(self.option["json_prp_name"])
        if self.setResult != None: 
            if self.setProperty != None :
                propList = [self.setProperty.valueList[i].pType 
                            for i in range(self.setProperty.nValue)]
            else : propList = []
            byt += self.setResult.to_bytes(False, self.option["json_res_index"], 
                                           self.option["bytes_res_format"], propList)
        return byt
        
    def to_csv(self, file, name=True, dat=True, loc=True, prp=True, lenres=0) :
        '''
        Generate csv file to display `Observation` data.

        *Parameters*
        
        - **file** : string - file name (with path)
        - **name** : boolean (default True) - Display name for `ES.ESValue`
        - **dat**  : boolean (default True) - Display value for `ES.ESValue.DatationValue`
        - **loc**  : boolean (default True) - Display value for `ES.ESValue.LocationValue`
        - **prp**  : boolean (default True) - Display value for `ES.ESValue.PropertyValue`
        - **lenres** : int (default 0) - Number of raws (all if 0)
            
        *Returns*
        
        - **None**
        '''
        tab = self._to_tab(name, dat, loc, prp, lenres)
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for lign in tab : writer.writerow(lign)
        
    def to_dataFrame(self, dataArray=True, sort=True, complet=False, name=True,
                  info=False, numeric=False, fullAxes=False, func=ES._identity,
                  arrayname='Observation'):
        '''
        Convert `Observation` to pandas.DataFrame with the smallest dimension. 
        
        *Parameters*
        
        - **dataArray** : Boolean (default True) - DataArray ou DataSet
        - **sort** : Boolean (default True) - Sort along an axis
        - **complet** : Boolean (default False) - Generate all the DataArray.Coords or only one.
        - **name** : Boolean (default True) - Add name Coords.
        - **info** : Boolean (default False) - Generate a specific Coords with Observation characteristics.
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values. 
        - **fullAxes** : Boolean (default False) - Include all the axes if True.
        - **func** : String (default function identity) - Name of the function 
        applied to each `ES.ESValue.ResultValue`
        - **arrayname** : String (default 'Observation') - Name of the Dataframe
            
        *Returns*
        
        - **pandas.DataFrame**
        '''
        if self.setResult.dim > 0 : 
            return self.to_xarray(dataArray=dataArray, sort=sort, complet=complet, 
                                  name=name, info=info, numeric=numeric, 
                                  fullAxes=fullAxes, func=func, arrayname=arrayname
                                  ).to_dataframe(name=arrayname)
        else : return None


    def to_json(self, **kwargs): 
        '''
        Export in Json format. 
        
        *Parameters (optional)*
        
        - **json_string**    : Boolean - return format (string or dict)
        - **json_res_index** : Boolean - include index for ResultValue
        - **json_param**     : Boolean - include ESObs Parameter
        - **json_info**      : Boolean - include ESObs Information with all information
        - **json_info_type** : Boolean - include in ESObs Information the type of ESObs
        - **json_info_nval** : Boolean - include in ESObs Information the lenght of ESObs
        - **json_info_box**  : Boolean - include in ESObs Information the bounding box
        - **json_info_other**: Boolean - include in ESObs Information the other information

        *Returns*
        
        - **string or dict** : Json string or dict
        '''
        option = self.option | kwargs
        option2 = option | {'json_string' : False}
        dic = { ES.type : ES.obs_classES }
        if self.mAtt[ES.obs_id] != ES.nullAtt: dic[ES.obs_id] = self.mAtt[ES.obs_id]
        dic |= self._jsonAtt(**option2)
        for cp in self.pComposant:
            dic |= cp.json(**option2)        
        if option["json_param"] and self.parameter != ES.nullAtt: 
            dic[ES.parameter] = self.parameter
        dic |= self._info(**option2) 
        if option['json_string'] : return json.dumps(dic)
        else : return dic
    
    def to_xarray(self, dataArray=True, sort=True, complet=False, name=True,
                  info=False, numeric=False, fullAxes=False, func=ES._identity,
                  arrayname='Observation', maxname=20):
        '''
        Convert `Observation` to DataArray or DataSet with the smallest dimension. 
        
        *Parameters*
        
        - **dataArray** : Boolean (default True) - DataArray ou DataSet
        - **sort** : Boolean (default True) - Sort along an axis
        - **complet** : Boolean (default False) - Generate all the DataArray.Coords or only one.
        - **name** : Boolean (default True) - Add name Coords.
        - **info** : Boolean (default False) - Generate a specific Coords with Observation characteristics.
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values. 
        - **fullAxes** : Boolean (default False) - Include all the axes if True.
        - **func** : String (default function identity) - Name of the function 
        applied to each `ES.ESValue.ResultValue`
        - **arrayname** : String (default 'Observation') - Name of the Dataframe
        - **maxname** : String (default 20) - maximum length for string
        
        *Returns*
        
        - **xarray.DataArray or xarray.DataSet**
        '''
        if self.setResult.maxIndex == -1 : return None
        if sort : self.sort()
        xList = self._xlist(squeeze= not fullAxes, fullAxes=fullAxes, func=func,
                            maxname=maxname)
        attrs = self._xAttrs()
        coord = self._xCoord(xList, attrs, dataArray, complet, name, numeric, fullAxes)
        axes=self.setResult._triAxe(maj=False, fullAxes=fullAxes)
        dims = [ES.axes[ax] for ax in axes]
        if numeric  : xres = xList['resval']
        else        : xres = xList['res']
        if dataArray and info :
            return xr.DataArray(xres, coord, dims, attrs=attrs['info'], name=arrayname)
        elif dataArray and not info :
            return xr.DataArray(xres, coord, dims, name=arrayname)
        return None

    @property
    def typeObs(self):
        '''
        string (@property) : Observation type (calculated from `Observation` score)
        '''
        [nPrp, nDat, nLoc, nRes] = self.nValueObs
        if self.setResult == None or (self.setResult.error or self.setResult.maxIndex == -1 or \
           self.setResult.nInd[0] > nDat or self.setResult.nInd[1] > nLoc or self.setResult.nInd[2] > nPrp):
               return ES.obsCat[-1]
        return ES.obsCat[self.score]

    def view(self, name=True, dat=True, loc=True, prp=True, lenres=0, width=15, sep = '_') :
        '''
        Generate tabular list to display `Observation` data.

        *Parameters*
        
        - **name** : boolean (default True) - Display name for `ES.ESValue`
        - **dat**  : boolean (default True) - Display value for `ES.ESValue.DatationValue`
        - **loc**  : boolean (default True) - Display value for `ES.ESValue.LocationValue`
        - **prp**  : boolean (default True) - Display value for `ES.ESValue.PropertyValue`
        - **lenres** : Integer (default : 0) - Number of raws (all if 0)
        - **width** : Integer (default 15) - Number of characters displayed for each attribute.
        - **sep** : Char (default '_') - Separation between header and raws

        *Returns*
        
        - **None**
        '''
        tab = self._to_tab(name, dat, loc, prp, lenres)
        septab = ''
        for i in range(width-2) : septab += sep
        separator = [ septab for val in tab[0]] 
        first=True
        forms = '{:<'+str(width)+'.'+str(width-1)+'}'
        formf = '{!s:<'+str(width)+'.'+str(width-1)+'}'
        for lign in tab :
            for val in lign :
                if type(val)==str : print(forms.format(val), end='')
                else : print(formf.format(val), end='')
            print('')
            if first : 
                for val in separator :
                    print(val.ljust(width), end='')
                print('')
                first = False

    def voxel(self, sort=False):
        '''
        Visualize `ES.ESValue.ResultValue` in a cube with voxels.
        
        *Parameters*
        
        - **sort** : Boolean (default False) - Sort along axis.
        
        *Returns*
        
        - **None**
        '''
        if self.setResult.maxIndex == -1 : return        
        obc = copy.deepcopy(self)
        if sort : obc.sort()
        obc.full()
        obx = obc.to_xarray(numeric = False, complet=True, sort=sort, fullAxes=True, func=ResultValue.isNotNull)
        obp = obx #>=0
        obp.set_index(loc='locran', dat='datran', prp='prpran')
        ax = plt.figure().add_subplot(projection='3d')
        ax.voxels(obp, edgecolor='k')
        ax.set_xticks(np.arange(self.setDatation.nValue))
        ax.set_yticks(np.arange(self.setLocation.nValue))
        ax.set_zticks(np.arange(self.setProperty.nValue))
        ax.set(xlabel='dat (index)', ylabel='loc (index)', zlabel='prp (index)')
        plt.show()

    def _addValueObservation(self, idat, iloc, iprp, val): #!!!methods intern
        '''
        Add a new `ES.ESValue.ResultValue` 
        
        **idat, iloc, iprp** : integer, ES.ESValue.ESIndexValue
        **val** : ES.ESValue.ResultValue compatible type
        **return** int : last index in the `ES.ESValue.ESSet` valueList.
        '''
        if self.setResult == None: ESSetResult(pObs=self)
        return self.addResultValue(ResultValue(val, [idat, iloc, iprp]))

    def _infoType(self):
        ''' Add information's key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.json_type_obs] = self.typeObs
        if self.setLocation != None :
            if self.setLocation.nValue > 1 : 
                dcinf[ES.json_type_loc] = ES.multi + self.setLocation.typeES
            else :
                dcinf[ES.json_type_loc] = self.setLocation.typeES
        if self.setDatation != None :
            if self.setDatation.nValue > 1 : 
                dcinf[ES.json_type_dat] = ES.multi + self.setDatation.typeES
            else :
                dcinf[ES.json_type_dat] = self.setDatation.typeES
        if self.setProperty != None :
            if self.setProperty.nValue > 1 : 
                dcinf[ES.json_type_prp] = ES.multi + self.setProperty.typeES
            else :
                dcinf[ES.json_type_prp] = self.setProperty.typeES
        if self.setResult != None :
            if self.setResult.nValue > 1 : 
                dcinf[ES.json_type_res] = ES.multi + self.setResult.typeES
            else :
                dcinf[ES.json_type_res] = self.setResult.typeES
        return dcinf
    
    def _infoNval(self):
        ''' Add valueList lenght to dict dcinf'''
        dcinf = dict()
        if self.setLocation != None : dcinf[ES.json_nval_loc] = self.setLocation.nValue
        if self.setDatation != None : dcinf[ES.json_nval_dat] = self.setDatation.nValue
        if self.setProperty != None : dcinf[ES.json_nval_prp] = self.setProperty.nValue
        if self.setResult   != None : dcinf[ES.json_nval_res] = self.setResult.nValue
        return dcinf
    
    def _infoBox(self):
        ''' Add box informations's key-value to dict dcinf'''
        dcinf = dict()
        if self.setLocation != None and self.setLocation.nValue > 0:
            dcinf[ES.loc_box] = list(self.setLocation.boundingBox.bounds)
        if self.setDatation != None and self.setDatation.nValue > 0:
            dcinf[ES.dat_box] = list(self.setDatation.boundingBox.bounds)
        return dcinf
    
    def _infoOther(self):
        ''' Add other's information key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.obs_complet] = self.complet
        dcinf[ES.obs_score]   = self.score
        if self.setResult != None :
            dcinf[ES.res_mRate] = self.setResult.measureRate
            dcinf[ES.res_dim]   = self.setResult.dim
            dcinf[ES.res_axes]  = self.setResult.axes
        return dcinf
    
    def _info(self, **kwargs):
        ''' Create json string with dict datas'''
        option = self.option | kwargs
        dcinf = dict()
        if option["json_info"] or option["json_info_type"] : dcinf |= self._infoType()
        if option["json_info"] or option["json_info_nval"] : dcinf |= self._infoNval()
        if option["json_info"] or option["json_info_box"]  : dcinf |= self._infoBox()
        if option["json_info"] or option["json_info_other"]: dcinf |= self._infoOther()
        ldel =[]
        for k,v in dcinf.items() :
            if type(v) == str and (v == "null" or v =='')   : ldel.append(k)
            if type(v) == list and v == ES.nullCoor         : ldel.append(k) 
        for k in ldel :         del dcinf[k]
        if len(dcinf) != 0 : dcinf = {ES.information : dcinf }
        if option["json_string"] :
            if len(dcinf) == 0 :    return ""
            else :                  return json.dumps(dcinf)
        else: return dcinf
    
    def _initESObs(self, *args, **kwargs) :
        ''' ESObs creation '''
        for arg in args :
            if type(arg) == str :       # creation à partir d'un json "key : [liste]"
                try: js=json.loads(arg)
                except: return
                if ES.type not in list(js) or js[ES.type] != ES.obs_classES : return
                self._initDict(js)
            elif type(arg) == dict :    # creation à partir d'un dict "key : [liste]"
                js = arg.copy()
                self._initDict(js)
            elif type(arg) == list :    # création à partir d'un jeu de valeur [[dat], [loc], [prp], [res]]
                if len(arg) == 4 : 
                    for i in range(4) :
                        if self.element(ES.esObsClass[i]) == None : _EsObs[i](arg[i], self)
            elif type(arg) == tuple :   # creation uniquement d'un jeu de données dat, loc, prp, res
                self.append(arg[0], arg[1], arg[2], arg[3])
        for k in kwargs :
            if k in ES.esObsClass and self.element(k) == None and type(kwargs[k]) in _EsObs: 
                self.addComposant(kwargs[k])
            elif k in ES.esObsClass and self.element(k) == None : 
                _EsObsDict[k](kwargs[k], self)

    def _initDict(self, js) :
        ''' attributes and ESObs creation '''
        if ES.obs_id in list(js): self.mAtt[ES.obs_id] = js[ES.obs_id]
        if ES.obs_attributes in list(js): 
            if type(js[ES.obs_attributes]) == dict: js = js[ES.obs_attributes]
            else: return
        self.addAttributes(js)
        self.addESObs(js)
    

    @staticmethod
    def _sortAlign(npInd, list1, ind1, ind2):
        return [int(npInd[list(npInd[:,ind1]).index(i),:][ind2])  for i in list1]    
    
    def _sortSet(self, ax, tri=[], update=True):
        ''' sort the ES.ESObs define by the ax parameter '''
        if ax == 0 and self.setDatation != None : return self.setDatation.sort(tri, update)
        if ax == 1 and self.setLocation != None : return self.setLocation.sort(tri, update)
        if ax == 2 and self.setProperty != None : return self.setProperty.sort(tri, update)
        return [0]
    
    def _xlist(self, squeeze=True, fullAxes=False, func=ES._identity, maxname=0):
        '''list generation for Xarray'''
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
            xList['datins'] = self.setDatation.to_numpy(func = DatationValue.vInstant)
            xList['datnam'] = self.setDatation.to_numpy(func = DatationValue.vName)
            xList['datran'] = np.arange(len(xList['dat']))
        if self.setProperty != None: 
            xList['prp']    = self.setProperty.to_numpy()
            xList['prpstr'] = self.setProperty.to_numpy(func = PropertyValue.json)
            xList['prptyp'] = self.setProperty.to_numpy(func = PropertyValue.vType)
            xList['prpnam'] = self.setProperty.to_numpy(func = PropertyValue.vName)
            xList['prpran'] = np.arange(len(xList['prp']))
        if self.setResult  != None: 
            if fullAxes : ind='obs'
            else : ind='axe'
            xList['res']    = self.setResult.to_numpy(squeeze=squeeze, ind=ind, func = func)
            xList['resval'] = self.setResult.to_numpy(squeeze=squeeze, ind=ind, func = ResultValue.to_float)
            xList['resstr'] = self.setResult.to_numpy(squeeze=squeeze, ind=ind, func = ResultValue.json)
            xList['resnam'] = self.setResult.to_numpy(squeeze=squeeze, ind=ind, func = ResultValue.vName)
            xList['resran'] = self.setResult.to_numpy(squeeze=squeeze, ind=ind, func = 'index')
            #xList['resran'] = np.arange(len(xList['res']))
        if maxname > 0 :
            for key,lis in xList.items() :
                if key[3:6] in ['str', 'nam', 'typ']:
                    for i in range(len(lis)) : lis[i] = lis[i][0:maxname]
        return xList

    def _xAttrs(self) :
        ''' attrs generation for Xarray'''
        attrs = ES.xattrs
        attrs['info'] = self._info(json_string=False, json_info_type=True,
                                   json_info_nval  =False, json_info_box =True, 
                                   json_info_other =False)["information"]
        return attrs

    def _xCoord(self, xList, attrs, dataArray, complet, name, numeric, fullAxes=False) :
        ''' Coords generation for Xarray'''
        coord = {}
        if fullAxes : 
            for key, val in xList.items() :
                if key[:3] != 'res' : 
                    coord[key] = (key[:3], val, attrs[key[:3]])
                    if key == 'loclon' : coord[key] = (coord[key][0], val, attrs['lon'])
                    if key == 'loclat' : coord[key] = (coord[key][0], val, attrs['lat'])
        else :
            for key, val in xList.items() :
                if key[:3] != 'res' and \
                    self.setResult._axeCoor(ES.nax[key[:3]]) != None and \
                    (complet or len(key) == 3 or (name and key[3:6] == 'nam') or \
                     key == 'loclon' or key == 'loclat'):
                    coord[key] = ([ES.axes[self.setResult._axeCoor(ES.nax[key[:3]])]], val, attrs[key[:3]])
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
            if 'dat' in coord.keys() : coord['dat'] = (coord['dat'][0], xList['datins'], coord['dat'][2])
            if 'prp' in coord.keys() : coord['prp'] = (coord['prp'][0], xList['prpran'], coord['prp'][2])
        return coord
    

    def _to_tab(self, name=True, dat=True, loc=True, prp=True, lenres=0):
        ''' data preparation for view or csv export'''
        if self.setResult == None : return
        tab = list()
        resList = []
        if self.setDatation != None : 
            if name : resList.append('datation name')
            if dat  : resList.append('datation instant')
        if self.setLocation != None : 
            if name : resList.append('location name')
            if loc  : resList.append('location coor x')
            if loc  : resList.append('location coor y')
        if self.setProperty != None : 
            if name : resList.append('property name')
            if prp  : resList.append('property type')
        resList.append('result value')
        tab.append(resList)
        if lenres == 0 : lenres = len(self.setResult)
        for i in range(min(lenres, len(self.setResult))) :
            res = self.setResult[i]
            resList = []
            if self.setDatation != None : 
                if name : resList.append(self.setDatation.valueList[res.ind[0]].name)
                if dat  : resList.append(self.setDatation.valueList[res.ind[0]].vInstant(string=True))
            if self.setLocation != None : 
                if name : resList.append(self.setLocation.valueList[res.ind[1]].name)
                if loc  : resList.append(self.setLocation.valueList[res.ind[1]].vPoint()[0])
                if loc  : resList.append(self.setLocation.valueList[res.ind[1]].vPoint()[1])
            if self.setProperty != None : 
                if name : resList.append(self.setProperty.valueList[res.ind[2]].name)
                if prp  : resList.append(self.setProperty.valueList[res.ind[2]].pType)
            resList.append(res.value)
            tab.append(resList)
        return tab            
   
