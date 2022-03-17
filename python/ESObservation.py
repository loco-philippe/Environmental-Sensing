# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: Philippe@loco-labs.io

The `ES.ESObservation` module contains the main class
of Environmental Sensing : `Observation` class.

"""
from ESconstante import ES
from ESValue import LocationValue, DatationValue, PropertyValue, \
    ResultValue, ESValue, ESValueEncoder
from datetime import datetime
import json, folium, copy, csv
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/iList')
from ilist import Ilist

_EsClassValue: dict = {ES.dat_classES : DatationValue, 
                       ES.loc_classES : LocationValue,
                       ES.prp_classES : PropertyValue,
                       ES.res_classES : ResultValue}
'''dict classES : ESValue class '''  

class Observation :
    """
    An `Observation` is made up of `ES.ilist` object which describe the axes of this object.
    
    *Attributes (for @property see methods)* :

    - **option** : Dictionnary with options
    - **ilist** : Ilist object (data and axes)
    - **name** : textual description
    - **mAtt** : namedValue dictionnary (internal parameters)
    - **parameter** : namedValue dictionnary (external data)

    The methods defined in this class are : 
    
    *property (getters)*
    
    - `Observation.axes`
    - `Observation.bounds`
    - `Observation.complet`
    - `Observation.consistent`
    - `Observation.dimension`
    - `Observation.json`
    - `Observation.jsonFeature`
    - `Observation.nValueObs`
    - `Observation.rate`
    - `Observation.score`
    - `Observation.setDatation`    
    - `Observation.setLocation`
    - `Observation.setProperty`
    - `Observation.setResult`
    - `Observation.typeObs`
    
    *add value*
    
    - `Observation.addAttributes`
    - `Observation.append`
    - `Observation.appendList`
    - `Observation.appendObs`
    
    *update value*
    
    - `Observation.majList`
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
    
    - `Observation.choropleth`
    - `Observation.voxel`
    - `Observation.plot`
    - `Observation.view`
    
    *exports - imports*
    
    - `Observation.to_csv`
    - `Observation.to_dataFrame`
    - `Observation.to_numpy`
    - `Observation.to_xarray`
    - `Observation.to_json`
    - `Observation.from_json`
    - `Observation.to_bytes`              # à voir
    - `Observation.from_bytes`            # à voir

    """
    def __init__(self, *args, order = [], idxref = [], **kwargs):
        '''
        Several Observation creation modes :
        
        - Observation(dictESValue1, dictESValue2, ...) where dictESValue = {ESValuename : value}
        - Observation({ObsDict}) where ObsDict is a dictionnary with the same data as an ObsJSON
        - Observation(ObsJSON) where ObsJSON is a string with the ObsJSON format
        - Observation([ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult]) where ESSet is a list of ESValue :
            [ESValue1, ESValue2,...] or [ESValue] or ESValue
        - Observation(datation=ESSetDatation, location=ESSetLocation,
                      property=ESSetProperty, result=ESSetResult)
        
        *Note : the parameters 'idxref' and 'order' are used only when an ESSetResult without Index is in arguments. 
        'order' indicates the order for the Index creation and 'idxref' the linked index (0 for Datation, 1 for Location, 2 for Property).*
        '''
        kwargs |= {'order' : order, 'idxref' : idxref}
        self.name = "observation du " + datetime.now().isoformat()
        self.option = ES.mOption.copy()
        self.mAtt = {}
        self.ilist = Ilist()
        self.mAtt[ES.obs_reference] = 0
        self.mAtt[ES.obs_resultTime] = "null"
        self.mAtt[ES.obs_id] = "null"
        self._initObs(*args, **kwargs)
        self.parameter = ES.nullAtt        # json

    
    def _initObs(self, *args, **kwargs):
        ''' data creation '''
        dic = {}
        if len(args) == 0 and len(kwargs) == 2 : args = [{}]
        for arg in args :
            if type(arg) == str :       # creation à partir d'un json "key : [liste]"
                try: arg=json.loads(arg)
                except: pass
            if type(arg) == dict :      # creation à partir d'un dict "key : [liste]"
                for k,v in arg.items() : 
                    if k not in dic : dic |= {k:v}
        if dic != {} or len(args) == 0 or args == [{}] :
            for k,v in kwargs.items() : 
                if k not in dic : dic |= {k:v}
            self._initDict(dic)
            return            
        for arg in args :
            if type(arg) == list and len(arg) == 4 :    # création à partir d'un jeu de valeur [[dat], [loc], [prp], [res]]
                self._initList(arg, **kwargs)
                return
            elif type(arg) == tuple :   # creation uniquement d'un jeu de données dat, loc, prp, res
                self.append(arg[0], arg[1], arg[2], arg[3])
                
    def _initDict(self, js) :
        ''' data creation in dict mode'''
        if ES.obs_id in list(js): self.mAtt[ES.obs_id] = js[ES.obs_id]
        if ES.obs_attributes in list(js): 
            if type(js[ES.obs_attributes]) == dict: js = js[ES.obs_attributes]
            else: return
        dicidx = {}
        dicres = {} 
        idxref = []
        order = []
        for classES in ES.esObsClass[0:3] :
            if classES in list(js) : 
                dicidx[classES] = ESValue.cast(js[classES], _EsClassValue[classES])
        if ES.res_classES in list(js) : dicres[ES.res_classES] = js[ES.res_classES]
        if 'order' in list(js) : order = js['order']
        if 'idxref' in list(js) : idxref = js['idxref']
        (v, seti, ii, vname, iname) = Ilist._initdict(dicres, dicidx, order, idxref)
        res = ESValue.cast(v, ResultValue)
        self.ilist = Ilist(res, seti, ii, vname, iname, defaultidx=False)
        self.addAttributes(js)

    def _initList(self, lis, **kwargs) :
        '''data creation in list mode '''
        if 'order' in kwargs : order = kwargs['order']
        else : order = []
        if 'idxref' in kwargs : idxref = kwargs['idxref']
        else : idxref = []
        self.ilist = Ilist.Iset(ESValue.cast(lis[3], ResultValue), 
                                [ESValue.cast(lis[0], DatationValue),
                                 ESValue.cast(lis[1], LocationValue),
                                 ESValue.cast(lis[2], PropertyValue)], 
                                order, idxref, ES.esObsClass[3], ES.esObsClass[0:3],
                                defaultidx=False)  

    def __copy__(self):
        ''' Copy all the data, included ESValue'''
        return copy.deepcopy(self)

    @property
    def __geo_interface__(self):
        '''dict (@property) : return the union of geometry (see shapely)'''
        if self.setLocation : 
            collec = self.vListValue(ES.loc_classES)[0]
            first = True
            for shap in self.vListValue(ES.loc_classES) :
                if not first : collec = collec.union(shap)
                first = False
            return collec.__geo_interface__
        else : return ""

    def __ior__(self, other):
        ''' Add other's index to self's index'''
        self.option = other.option | self.option
        self.mAtt = other.mAtt | self.mAtt
        self.ilist |= other.ilist
        newindex = []
        nameES = self.ilist.idxname
        if ES.dat_classES in nameES: newindex.append(nameES.index(ES.dat_classES))
        if ES.loc_classES in nameES: newindex.append(nameES.index(ES.loc_classES))
        if ES.prp_classES in nameES: newindex.append(nameES.index(ES.prp_classES))
        self.ilist.swapindex(newindex)
        return self
    
    def __or__(self, other):
        ''' Add other's index to self's index and return a new Observation'''
        obres = self.__copy__()
        obres.__ior__(other)
        return obres

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        self.ilist += other.ilist
        self.option = other.option | self.option
        self.mAtt = other.mAtt | self.mAtt
        return self
    
    def __add__(self, other):
        ''' Add other's values to self's values and return a new Observation'''
        obres = self.__copy__()
        obres.__iadd__(other)
        return obres

    def __len__(self): return len(self.ilist)
    
    @property               # !!!       properties
    def axes(self):
        '''
        **list of integer (@property)** : list of independant axes in the Observation
        (0 for Datation, 1 for Location, 2 for Property)'''
        axes =[]
        for i in self.ilist.axes :
            axes.append(ES.esObsClass.index(self.ilist.idxname[i]))
        return axes

    @property
    def bounds(self):
        '''
        **list of `ES.ESValue` (@property)** : `ES.ESValue` bounding box for each axis.'''
        bound = [None, None, None]
        if self.setDatation : bound[0] = self._boundingBox(DatationValue, self.setDatation)
        if self.setLocation : bound[1] = self._boundingBox(LocationValue, self.setLocation)
        if self.setProperty : bound[2] = self.setProperty[0]
        return bound

    @property
    def complet(self):
        '''
        **boolean (@property)** : True if self.ilist is complete (if the number of ResultValue is consistent with 
        the number of LocationValue, DatationValue and PropertyValue)'''
        return self.ilist.complete

    @property
    def consistent(self):
        '''
        **boolean (@property)** : True if Observation is consistent (no duplicate index) '''
        return self.ilist.consistent

    @property
    def dimension(self):
        '''
        **integer (@property)** : number of independant axes in the Observation'''
        return self.ilist.dimension

    @property
    def json(self):
        ''' 
        **string (@property)** : JSON Observation (ObsJSON format) whit index 
        and whitout informations'''
        return self.to_json(json_string=True, json_info=False, json_res_index=True,
                            json_param=True)

    @property
    def jsonFeature(self):
        ''' 
        **string (@property)** : "FeatureCollection" with ESSetLocation geometry'''
        if self.setLocation : 
            geo = self.__geo_interface__
            if geo['type'] == "MultiPolygon": typ = "Polygon"
            else : typ = "Point"
            lis = list(dict((("type", typ), ("coordinates", geo['coordinates'][i]))) for i in range(len(geo['coordinates'])))
            fea = list(dict((("type","Feature"), ("id", i), ("geometry", lis[i]))) for i in range(len(geo['coordinates'])))
            return json.dumps(dict((("type","FeatureCollection"), ("features",fea))))            
        else: return ''  
            
    @property 
    def nValueObs(self):
        '''
        **list (@property)** : lenght of axes [datation, location, properety, result].'''
        nvalue =[]
        for esclass in ES.esObsClass[0:3] :
            nval = 0
            for i in range(self.ilist.lenidx) :
                if self.ilist.idxname[i] == esclass : nval = self.ilist.idxlen[i]
            nvalue.append(nval)
        nvalue.append(self.ilist.setvallen)
        return nvalue
    
    @property
    def rate(self):
        '''
        **float (@property)** : ratio number measure / number measure if complete'''
        return self.ilist.rate

    @property
    def score(self):
        '''
        **integer (@property)** : Observation type (calculated from dimension , nValueObs and idxref). 
        The score is a codification of the number of ESValue for each axis. 
        E.g., score=122 means one PropertyValue (1), several LocationValue (2), 
        several DatationValue (2)'''
        [ nDat, nLoc, nPrp, nRes] = self.nValueObs
        score = min(max(min(nPrp, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2), -1), 229);
        if self.setResult == None or not self.consistent : return score
        if score == 22  and self.dimension == 2:	score = 23
        if score == 122 and self.dimension == 2:	score = 123
        if score == 202 and self.dimension == 2:	score = 203
        if score == 212 and self.dimension == 2:	score = 213
        if score == 220 and self.dimension == 2:	score = 223
        if score == 221 and self.dimension == 2:	score = 224
        if score == 222 and self.dimension == 3:	score = 228
        if score == 222 and self.dimension == 2 and 2 in self.ilist.idxref == [0,0,2]:	score = 225
        if score == 222 and self.dimension == 2 and 1 in self.ilist.idxref == [0,1,0]:	score = 226
        if score == 222 and self.dimension == 2 and 0 in self.ilist.idxref == [0,1,1]:	score = 227
        return score

    @property
    def setDatation(self): 
        '''
        **list (@property)** : list of values in the datation axis'''
        try : return self.ilist.setidx[self.ilist.idxname.index(ES.dat_classES)]
        except : return None

    @property
    def setLocation(self): 
        '''
        **list (@property)** : list of values in the location axis'''
        try : return self.ilist.setidx[self.ilist.idxname.index(ES.loc_classES)]
        except : return None
    
    @property
    def setProperty(self): 
        '''
        **list (@property)** : list of values in the property axis'''
        try : return self.ilist.setidx[self.ilist.idxname.index(ES.prp_classES)]
        except : return None

    @property
    def setResult(self): 
        '''
        **list (@property)** : list of values in the result axis'''
        try : return self.ilist.extval
        except : return None
        
    @property
    def typeObs(self):
        '''
        **string (@property)** : Observation type (calculated from the score)'''
        if self.consistent : return ES.obsCat[self.score]
        else : return ES.obsCat[-1]

    def addAttributes(self, js):        # !!! methodes externes
        '''
        Add informations attached to `Observation`

        *Parameters*
        
        - **js** : Dict - Keys are Observation keys (dict mAtt) or users keys (dict parameter).
        
        *Returns*
        
        - **None**  '''
        if type(js) != dict: return
        for k, v in js.items():
            if (self._isESAtt(ES.obs_classES, k) or k not in ES.reserved) and k != ES.type : 
                self.mAtt[k] = v
            if k == ES.parameter: 
                try:  self.parameter = json.dumps(v)
                except:  self.parameter = ES.nullAtt

    def append(self, dat, loc, prp, res, unique=False, equal='full') :
        '''
        Add a new `ES.ESValue.ResultValue`
        
        *Parameters*
        
        - **dat, loc, prp** :
        
            integer for the index of an existant `ES.ESValue`
            or compatible Value for an existing `ES.ESValue`
            or compatible Value for a new `ES.ESValue`
            
        - **res** : new `ES.ESValue.ResultValue`
        - **unique** : boolean (default False), if False, duplicate index is allowed
        - **equal** : string (default 'full'), if 'full', two ESValue are equal if all the attributes are equal,
        if 'name', two ESValue are equal if only the names are equal.
        
        *Returns*
        
        - **int** : last index in the result valueList.  '''
        self.ilist.idxname = ES.esObsClass[0:3]
        self.ilist.valname = ES.esObsClass[3]
        if   equal == 'full':
            self.ilist.append(ResultValue(res), 
                          [DatationValue(dat), LocationValue(loc), PropertyValue(prp)],
                          unique=unique)
        elif equal == 'name':
            datv = DatationValue(dat)
            for val in self.setDatation :
                if ESValue.isEqual(val, DatationValue(dat), name=True, value=False): 
                    datv = val
                    break
            locv = LocationValue(loc)
            for val in self.setLocation :
                if ESValue.isEqual(val, LocationValue(loc), name=True, value=False): 
                    locv = val
                    break
            prpv = PropertyValue(prp)
            for val in self.setProperty :
                if ESValue.isEqual(val, PropertyValue(prp), name=True, value=False): 
                    prpv = val
                    break
            self.ilist.append(ResultValue(res), [datv,locv, prpv], unique=unique)
        return len(self.ilist) - 1        

    def appendList(self, listDat, listLoc, listPrp, listVal, unique=False, equal='full'):
        '''
        Add a list of new `ES.ESValue.ResultValue` 
        
        *Parameters*
        
        - **listVal** : list of ES.ESValue.ResultValue compatible type
        - **listDat, listLoc, listPrp** : list of index or Value to define a `ES.ESValue`
        - **unique** : boolean (default False), if False, duplicate index is allowed
        - **equal** : string (default 'full'), if 'full', two ESValue are equal if all the attributes are equal,
        if 'name', two ESValue are equal if only the names are equal.
        
        *Returns* 
        
        - **None**        '''
        if len(listVal)==len(listDat)==len(listLoc)==len(listPrp) :
            for i in range(len(listVal)) :
                self.append(listDat[i], listLoc[i], listPrp[i], listVal[i], unique=unique, equal=equal)

    def appendObs(self, obs, unique=False, equal='full') :
        '''
        Add an `Observation` as a new `ES.ESValue.ResultValue` with bounding box for the other `ES.ESValue`
        
        *Parameters*
        
        - **obs** : Observation
        
        *Returns*
        
        - **int** : last index in the `Observation`
        '''
        self.append(obs.bounds[0], obs.bounds[1], obs.bounds[2], obs, unique=unique, equal=equal)

    def choropleth(self, name="choropleth"):
        '''
        Display `Observation` on a folium.Map (only with dim=1)

        - **name** : String, optionnal (default 'choropleth') - Name of the choropleth
            
        *Returns*
        
        - **folium.Map**  '''
        if self.dimension == 1 :
            m = folium.Map(location=self.setLocation[0].coorInv, zoom_start=6)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name=name,
                data=self.to_dataFrame(numeric=True),
                key_on="feature.id",
                columns = ['locran', 'Observation'],
                fill_color="OrRd",
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight = 2,
                legend_name="test choropleth"
            ).add_to(m)
            folium.PolyLine(
                self.vList('location', func=LocationValue.vPointInv)
            ).add_to(m)
            folium.LayerControl().add_to(m)
            return m
        return None

    def extend(self, classES, listValue, index):
        '''
        Copy axis from other `Observation` to self `Observation` (if it daesn't exist)

        *Parameters*
        
        - **other** : object Observation to copy
        
        *Returns*
        
        - **None**  '''
        if classES in self.ilist.idxname : raise ObservationError("duplicated index")
        if len(index) != len(self) : raise ObservationError("index lenght not equal")
        self.ilist.addlistidx(classES, listValue, index)
        newindex = []
        nameES = self.ilist.idxname
        if ES.dat_classES in nameES: newindex.append(nameES.index(ES.dat_classES))
        if ES.loc_classES in nameES: newindex.append(nameES.index(ES.loc_classES))
        if ES.prp_classES in nameES: newindex.append(nameES.index(ES.prp_classES))
        self.ilist.swapindex(newindex)
        
    def from_json(self, js):
        '''
        Complete an empty `Observation` with json data. 
        
        *Parameters*
        
        - **js** : string - ObsJSON data
        
        *Returns*
        
        - **None**        '''
        try: dic=json.loads(js)
        except: return
        self._initDict(dic)
                
    def full(self, minind=True, fillvalue=None, inplace=False) : 
        '''
        Add empty `ES.ESValue.ResultValue` to have a 'complete' `Observation`

        *Parameters*
        
        - **inplace** : boolean (default False) - If True, add values to 
        Observation, else return new Observation.
        - **minind** : boolean (default True) - If True, independent axes are 
        completed with fillvalue, else all axes are completed
        - **fillvalue** : value used to complete the Observation
        
        *Returns*
        
        - **Observation** : new observation if not inplace, else None.
        '''
        if fillvalue is None : fillvalue = ResultValue.nullValue()
        if minind == True : axes = self.ilist.axes
        else : axes = list(range(self.ilist.lenidx))
        if inplace :
            self.ilist.full(axes=axes, fillvalue=fillvalue, inplace=inplace)
            return None
        else : 
            newobs = Observation()
            newobs.ilist     = self.ilist.full(axes=axes, fillvalue=fillvalue, inplace=inplace)
            newobs.mAtt      = self.mAtt
            newobs.parameter = self.parameter
            newobs.option    = self.option 
            return newobs    
    
    def iLoc(self, idat, iloc, iprp, json=True):
        '''
        Return the `ES.ESValue` values for an `ES.ilist.Ilist` index. 

        *Parameters*
        
        - **idat, iloc, iprp** : `ES.ilist.Ilist` index value
        - **json** : Boolean (default True) - Return JSON string if True

        *Returns*
        
        - **dict** : dict or JSON of each ES.ESValue (dat, loc, prp, res)  '''
        dic = dict()
        if self.ilist.lenidx != 3 : raise ObservationError("iloc not available ")
        try : res = self.ilist.iloc([idat, iloc, iprp])
        except : return dic
        if res is None : return dic
        extidx = self.ilist.iidxtoext([idat, iloc, iprp])
        dic[ES.dat_classES] = extidx[0]
        dic[ES.loc_classES] = extidx[1]
        dic[ES.prp_classES] = extidx[2]
        if json : dic[ES.res_classES] = res.json(**self.option)
        else    : dic[ES.res_classES] = res         
        return dic

    def indexLoc(self, esValue, string=True):
        '''
        Return the index of a `ES.ESValue` in a `ES.ilist.Ilist` index
        
        *Parameters*
        
        - **esValue** : `ES.ESValue`, 
        - **string** : Boolean (default True) - Return type (JSON if True, dict if False)
        
        *Returns*

        - **dict or string** : {'full' : indFull, 'name' : indName, 'value' : indValue }
            - indFull : integer for the first index value with name and value equality
            - indName : integer for the first index value with name equality
            - indFull : integer for the first index value with value equality  '''        
        if   type(esValue)== PropertyValue : lis = self.setProperty
        elif type(esValue)== LocationValue : lis = self.setLocation
        elif type(esValue)== DatationValue : lis = self.setDatation
        elif type(esValue)== ResultValue   : lis = self.setResult
        else: return None
        ind = {'full' : -1, 'name' : -1, 'value' : -1}
        for i in range(len(lis)):
            if lis[i].isEqual(esValue, name=True, value=True): 
                ind['full'] = ind['name'] = ind['value'] = i
                return ind
            if lis[i].isEqual(esValue, name=True, value=False) and ind['name'] == -1: 
                ind['name'] = i
            if lis[i].isEqual(esValue, name=False, value=True) and ind['value'] == -1: 
                ind['value'] = i
        if string : return json.dumps(ind)
        else : return ind
            
    def loc(self, valDat, valLoc, valPrp, json=True):
        '''
        Return the `ES.ESValue` values for a DatationValue, LocationValue, PropertyValue. 

        *Parameters*
        
        - **valdat, valloc, valprp** : DatationValue, LocationValue, PropertyValue

        *Returns*
        
        - **dict** : dict or JSON of each ES.ESValue (dat, loc, prp, res)  '''
        index = self.ilist.extidxtoi([DatationValue(valDat),LocationValue(valLoc),PropertyValue(valPrp)])
        return self.iLoc(index[0], index[1], index[2])

    def majList(self, ValueClass, listVal, name=False):
        '''
        Modify an attribute (name or value) in an axis list.

        *Parameters*
        
        - **ValueClass** : class ES.ESValue 
        - **listVal** : new list of values
        - **name** : boolean (default True) - True for 'name' and False for 'value'
        
        *Returns*
        
        - **None**  '''
        if ValueClass == DatationValue and self.setDatation != None : 
            newlistVal = Observation._majList(self.setDatation, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.dat_classES)] = newlistVal
        elif ValueClass == LocationValue and self.setLocation != None : 
            newlistVal = Observation._majList(self.setLocation, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.loc_classES)] = newlistVal
        elif ValueClass == PropertyValue and self.setProperty != None : 
            newlistVal = Observation._majList(self.setProperty, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.prp_classES)] = newlistVal
        elif ValueClass == ResultValue and self.setResult != None : 
            newlistVal = Observation._majList(self.setResult, listVal, name)
            self.ilist.extval = newlistVal

    def majValue(self, esValue, newEsValue, equal="full"):
        '''
        Update the value of an existing `ES.ESValue` by a new `ES.ESValue`

        *Parameters*
        
        - **esValue** : ESValue to update
        - **newEsValue** : new ESValue
        - **equal** : criteria used to compare ESValue ('full', 'name', 'value')
        
        *Returns*
        
        - **Int** : index in the ESSet valueList.  '''
        index = self.indexLoc(esValue)[equal]
        if   type(esValue) == PropertyValue : setClass = self.setProperty
        elif type(esValue) == LocationValue : setClass = self.setLocation
        elif type(esValue) == DatationValue : setClass = self.setDatation
        elif type(esValue) == ResultValue   : setClass = self.setResult
        else : setClass = None
        if  setClass != None and index != None: setClass[index].setValue(newEsValue)
        return index

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
        
        - **None**  '''
        if not self.ilist.consistent : return
        obx = self.to_xarray(numeric = True, maxname=maxname)
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
                obx.sortby(["dat","loc","prp"]
                           ).plot.line(x="dat", col="prp", xticks=list(obx.coords['dat'].values), 
                                       col_wrap=2, size=size, marker=marker)
            else :
                obx = obx.set_index(prp = "prpstr", loc="locran")
                obx.sortby(["dat","loc","prp"]
                           ).plot(x="dat", y="loc", col="prp", col_wrap=2, size=size, 
                                  xticks=list(obx.coords['dat'].values), yticks=list(obx.coords['loc'].values))
        plt.show()
        

    def sort(self, order=[], reindex=True): 
        '''
        Modify the order of `ES.ESValue`.

        *Parameters*
        
        - **order** : list (default []) - Ordered list to follow (0:dat, 1:loc, 2:prp).
        - **reindex** : boolean (default True) - calculate new index values.
        
        *Returns*
        
        - **None**        '''
        self.ilist.sort(order=order, reindex=reindex)

    def to_csv(self, file, json=True, name=True, dat=True, loc=True, prp=True, res=True, lenres=0) :
        '''
        Generate csv file to display `Observation` data.

        *Parameters*
        
        - **file** : string - file name (with path)
        - **json** : boolean (default True) - Display json for `ES.ESValue`
        - **name** : boolean (default True) - Display name for `ES.ESValue`
        - **dat**  : boolean (default True) - Display value for `ES.ESValue.DatationValue`
        - **loc**  : boolean (default True) - Display value for `ES.ESValue.LocationValue`
        - **prp**  : boolean (default True) - Display value for `ES.ESValue.PropertyValue`
        - **res**  : boolean (default True) - Display value for `ES.ESValue.ResultValue`
        - **lenres** : int (default 0) - Number of raws (all if 0)
            
        *Returns*
        
        - **None**        '''
        tab = self._to_tab(json, name, dat, loc, prp, res, lenres)
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for lign in tab : writer.writerow(lign)
        
    def to_dataFrame(self, info=False, numeric=False, ind='axe', fillvalue='?', func=ES._identity,
                  name='Observation'):
        '''
        Convert `Observation` to pandas.DataFrame with the smallest dimension. 
        
        *Parameters*
        
        - **info** : Boolean (default False) - Generate a specific Coords with Observation characteristics.
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values. 
        - **ind** : String (default 'axe') - 'axe' only independant axes, 'all' : all the axes.
        - **fillvalue** : Object (default '?') used to complete result
        - **func** : String (default function identity) - Name of the function to apply to the result values
        - **name** : String (default 'Observation') - Name of the Dataframe
            
        *Returns*
        
        - **pandas.DataFrame**        '''
        if self.ilist.consistent : 
            return self.to_xarray(info=info, numeric=numeric, fillvalue=fillvalue,
                                  func=func, name=name, ind=ind
                                  ).to_dataframe(name=name)
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
        
        - **string or dict** : Json string or dict        '''
        option = self.option | kwargs
        option2 = option | {'json_string' : False, 'json_mode' : 'vi'}
        dic = { ES.type : ES.obs_classES }
        if self.mAtt[ES.obs_id] != ES.nullAtt: dic[ES.obs_id] = self.mAtt[ES.obs_id]
        dic |= self._jsonAtt(**option2)
        dic |= self.ilist.json(**option2, cls=ESValueEncoder)
        if option["json_param"] and self.parameter != ES.nullAtt: 
            dic[ES.parameter] = self.parameter
        dic |= self._info(**option2) 
        if option['json_string'] : return json.dumps(dic, cls=ESValueEncoder)
        else : return dic

    def to_numpy(self, func=None, ind='axe', fillvalue='?', **kwargs):
        '''
        Convert `Observation` to Numpy array. 
        
        *Parameters*
        
        - **ind** : String (default 'axe') - 'axe' only independant axes, 'all' : all the axes, 'flat' : one dimension
        - **fillvalue** : Object (default '?') used to complete result
        - **func** : String (default function identity) - Name of the function to apply to the result values
        
        *Returns*
        
        - **Numpy array**    '''
        return self.ilist.to_numpy(func=func, ind=ind, fillvalue=fillvalue, **kwargs)

    def to_xarray(self, info=False, numeric=False, ind='axe', fillvalue='?',
                  name='Observation', maxname=20, func=None, **kwargs):
        '''
        Convert `Observation` to DataArray. 
        
        *Parameters*
        
        - **info** : Boolean (default False) - Generate a specific Coords with Observation characteristics.
        - **ind** : String (default 'axe') - 'axe' only independant axes, 'all' : all the axes, 'flat' : one dimension
        - **fillvalue** : Object (default '?') used to complete result
        - **func** : String (default function identity) - Name of the function applied to each `ES.ESValue.ResultValue`
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values. 
        - **name** : String (default 'Observation') - Name of the xArray
        - **maxname** : String (default 20) - maximum length for string
        
        *Returns*
        
        - **xarray.DataArray**        '''
        if not self.ilist.consistent : raise ObservationError("Ilist not consistent")
        if ind == 'axe' : axes = self.ilist.axes
        else : axes = list(range(self.ilist.lenidx))        
        ilf = self.ilist.full(axes=axes, fillvalue=fillvalue)
        ilf.sort(order=self.axes)
        xList = self._xlist(maxname=maxname)
        attrs = ES.xattrs | {'info' : self._info(json_string=False, json_info_type=True,
                                   json_info_nval  =False, json_info_box =True, 
                                   json_info_other =False)["information"]}
        coord = self._xCoord(xList, attrs, ilf.idxref, numeric)
        dims = [ES.vName[ilf.idxname[ax]] for ax in ilf.axes]
        if numeric : data = ilf._tonumpy(ilf.extval, func = ResultValue.to_float).reshape(ilf.axeslen)
        else : data = ilf._tonumpy(ilf.extval, func=func, **kwargs).reshape(ilf.axeslen)
        if not info : return xr.DataArray(data, coord, dims, name=name)
        else : return xr.DataArray(data, coord, dims, attrs=attrs['info'], name=name)

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
        
        - **None**        '''
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
            
    def vList(self, idxname, func=ES._identity):
        '''
        Generate a list of value for an axis.

        *Parameters*
        
        - **idxname** : string - Name of the axis (datation, location, property, result)
        - **func** : String (default function identity) - Name of the function applied to each `ES.ESValue`

        *Returns*
        
        - **list** : list of the values      '''
        if idxname == ES.res_classES : 
            if func == 'index': return [i for i in range(len(self))]
            else :              return [func(val) for val in self.ilist.extval]            
        else : 
            ind = self.ilist.idxname.index(idxname)
            if func == 'index': return [i for i in range(self.ilist.idxlen[ind])]
            else :              return [func(self.ilist.setidx[ind][i]) for i in range(self.ilist.idxlen[ind])]

    def vListName(self, idxname):
        '''
        Generate a list of value name for an axis.

        *Parameters*
        
        - **idxname** : string - Name of the axis (datation, location, property, result)

        *Returns*
        
        - **list** : list of the value name      ''' 
        if idxname == ES.res_classES : 
            return [self.ilist.extval[i].vName(ES.vName[idxname] + str(i)) for i in range(len(self.ilist.extval))]
        else :
            ind = self.ilist.idxname.index(idxname)
            return [self.ilist.setidx[ind][i].vName(ES.vName[idxname] + str(i)) for i in range(self.ilist.idxlen[ind])]

    def vListSimple(self, idxname):
        '''
        Generate a list of simple value (see `ES.ESValue` vSimple method) for an axis.

        *Parameters*
        
        - **idxname** : string - Name of the axis (datation, location, property, result)

        *Returns*
        
        - **list** : list of the simple value      '''
        return self.vList(idxname, ESValue.vSimple)
    
    def vListValue(self, idxname):
        '''
        Generate a list of value (see `ES.ESValue` getValue method) for an axis.

        *Parameters*
        
        - **idxname** : string - Name of the axis (datation, location, property, result)

        *Returns*
        
        - **list** : list of the values      '''
        return self.vList(idxname, func = ESValue.getValue)

    def voxel(self, sort=False):
        '''
        Visualize `ES.ESValue.ResultValue` in a cube with voxels.
        
        *Parameters*
        
        - **sort** : Boolean (default False) - Sort along axis.
        
        *Returns*
        
        - **None**
        '''
        if not self.ilist.consistent : return        
        obc = copy.deepcopy(self)
        if sort : obc.sort()
        obc.ilist.full()
        obx = obc.to_xarray(numeric = False, func=ResultValue.isNotNull)
        obp = obx #>=0
        obp.set_index(loc='locran', dat='datran', prp='prpran')
        ax = plt.figure().add_subplot(projection='3d')
        ax.voxels(obp, edgecolor='k')
        ax.set_xticks(np.arange(self.nValueObs[0]))
        ax.set_yticks(np.arange(self.nValueObs[1]))
        ax.set_zticks(np.arange(self.nValueObs[2]))
        ax.set(xlabel='dat (index)', ylabel='loc (index)', zlabel='prp (index)')
        plt.show()

    @staticmethod              # !!!!!! methodes internes
    def _boundingBox(ValueClass, listValue):
        ''' return a `ES.ESValue.ESValue` object with bounds values'''
        val = copy.deepcopy(listValue[0].value)
        for i in range(1,len(listValue)): val = val.union(listValue[i].value)
        return ValueClass._Box(val.bounds)

    def _infoType(self):
        ''' Add information's key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.json_type_obs] = self.typeObs
        for i in range(4) :
            if     self.nValueObs[i] > 1 : dcinf[ES.json_type[i]] = ES.multi + ES.esObsClass[i]
            else :                         dcinf[ES.json_type[i]] =            ES.esObsClass[i]
        return dcinf
    
    def _infoNval(self):
        ''' Add valueList lenght to dict dcinf'''
        dcinf = dict()
        for i in range(4) : dcinf[ES.json_nval[i]] = self.nValueObs[i]
        return dcinf
    
    def _infoBox(self):                 # !!!!!! à faire
        ''' Add box informations's key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.loc_box] = []
        dcinf[ES.dat_box] = []
        return dcinf
    
    def _infoOther(self):
        ''' Add other's information key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.obs_complet] = self.complet
        dcinf[ES.obs_score]   = self.score
        dcinf[ES.res_mRate]   = self.rate
        dcinf[ES.res_dim]     = self.dimension
        dcinf[ES.res_axes]    = self.axes
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

    @staticmethod
    def _isESAtt(esClass, key):
        """identify if 'key' is included in 'esClass'
        
        *Parameters*
        
        - **esClass** : string for an ESClass attribute
        - **key** : string to search
        
        *Returns*
        
        - **Boolean**        """        
        for k,v in ES.mTypeAtt.items():
            if k == key: return True
        return False

    def _jsonAtt(self, **option):
        ''' generate a dict with mAtt attributes'''
        att = dict()
        for k, v in self.mAtt.items():
            if k in list(ES.mTypeAtt.keys()) : 
                if v not in ES.nullValues : att[k] = v
            else: att[k] = v
        return att

    @staticmethod
    def _majList(listVal, newlistVal, name=False):
        ''' update value or name in a list of `ES.ESValue` '''
        if name :   return Observation._majListName (listVal, newlistVal)
        else :      return Observation._majListValue(listVal, newlistVal)

    @staticmethod        
    def _majListName(listVal, newlistVal):
        ''' update name in a list of `ES.ESValue` '''
        if len(listVal) != len(newlistVal) : return
        if type(newlistVal[0]) == str :
            for i in range(len(listVal)) : listVal[i].setName(newlistVal[i])
        else : 
            for i in range(len(listVal)) : listVal[i].setName(type(listVal[i])(newlistVal[i]).name)
        return listVal
    
    @staticmethod
    def _majListValue(listVal, newlistVal):
        ''' update value in a list of `ES.ESValue` '''
        if len(listVal) != len(newlistVal) : return
        for i in range(len(listVal)) : listVal[i].setValue(type(listVal[i])(newlistVal[i]))
        return listVal

    def _to_tab(self, json=True, name=True, dat=True, loc=True, prp=True, res=True, lenres=0):
        ''' data preparation for view or csv export'''
        if self.setResult == None : return
        tab = list()
        resList = []
        if self.setDatation != None : 
            if json : resList.append('datation')
            if name : resList.append('datation name')
            if dat  : resList.append('datation instant')
        if self.setLocation != None : 
            if json : resList.append('location')
            if name : resList.append('location name')
            if loc  : resList.append('location coor x')
            if loc  : resList.append('location coor y')
        if self.setProperty != None : 
            if json : resList.append('property')
            if name : resList.append('property name')
            if prp  : resList.append('property type')
        if self.setResult != None : 
            if json : resList.append('result')
            if name : resList.append('result name')
            if res :  resList.append('result value')
        tab.append(resList)
        if lenres == 0 : lenres = len(self.setResult)
        for i in range(min(lenres, len(self.setResult))) :
            resList = []
            if self.setDatation != None : 
                idat = self.ilist.idxname.index(ES.dat_classES)
                if json : resList.append(self.setDatation[self.ilist.iidx[idat][i]].json(json_string=True))
                if name : resList.append(self.setDatation[self.ilist.iidx[idat][i]].name)
                if dat  : resList.append(self.setDatation[self.ilist.iidx[idat][i]].vSimple(string=True))
            if self.setLocation != None : 
                iloc = self.ilist.idxname.index(ES.loc_classES)
                if json : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].json(json_string=True))
                if name : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].name)
                if loc  : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].vSimple()[0])
                if loc  : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].vSimple()[1])
            if self.setProperty != None : 
                iprp = self.ilist.idxname.index(ES.prp_classES)
                if json : resList.append(self.setProperty[self.ilist.iidx[iprp][i]].json(json_string=True))
                if name : resList.append(self.setProperty[self.ilist.iidx[iprp][i]].name)
                if prp  : resList.append(self.setProperty[self.ilist.iidx[iprp][i]].simple)
            if self.setResult != None : 
                if json : resList.append(self.setResult[i].json(json_string=True))
                if name : resList.append(self.setResult[i].name)
                if res  : resList.append(self.setResult[i].value)
            tab.append(resList)
        return tab            

    def _xCoord(self, xList, attrs, idxref, numeric) :
        ''' Coords generation for Xarray'''
        coord = {}
        for key, val in xList.items() :
            if key[:3] != 'res' : 
                axe = ES.axes[idxref[ES.nax[key[:3]]]]
                coord[key] = (axe, val, attrs[key[:3]])
                if key == 'loclon' : coord[key] = (coord[key][0], val, attrs['lon'])
                if key == 'loclat' : coord[key] = (coord[key][0], val, attrs['lat'])
        if numeric :
            if 'loc' in coord.keys() : coord['loc'] = (coord['loc'][0], xList['locran'], coord['loc'][2])
            if 'dat' in coord.keys() : coord['dat'] = (coord['dat'][0], xList['datins'], coord['dat'][2])
            if 'prp' in coord.keys() : coord['prp'] = (coord['prp'][0], xList['prpran'], coord['prp'][2])
        return coord
    
    def _xlist(self, maxname=0):
        '''list generation for Xarray'''
        xList = {}
        if self.setLocation != None and len(self.setLocation) > 1: 
            xList['loc']    = self.ilist._tonumpy(self.setLocation)
            xList['locstr'] = self.ilist._tonumpy(self.setLocation, func = LocationValue.json)
            xList['loclon'] = self.ilist._tonumpy(self.setLocation, func = LocationValue.vPointX)
            xList['loclat'] = self.ilist._tonumpy(self.setLocation, func = LocationValue.vPointY)
            xList['locnam'] = self.ilist._tonumpy(self.setLocation, func = LocationValue.vName)
            xList['locran'] = np.arange(len(xList['loc']))
        if self.setDatation != None and len(self.setDatation) > 1: 
            xList['dat']    = self.ilist._tonumpy(self.setDatation)
            xList['datstr'] = self.ilist._tonumpy(self.setDatation, func = DatationValue.json)
            xList['datins'] = self.ilist._tonumpy(self.setDatation, func = DatationValue.vSimple)
            xList['datnam'] = self.ilist._tonumpy(self.setDatation, func = DatationValue.vName)
            xList['datran'] = np.arange(len(xList['dat']))
        if self.setProperty != None and len(self.setProperty) > 1: 
            xList['prp']    = self.ilist._tonumpy(self.setProperty)
            xList['prpstr'] = self.ilist._tonumpy(self.setProperty, func = PropertyValue.json)
            xList['prptyp'] = self.ilist._tonumpy(self.setProperty, func = PropertyValue.vSimple)
            xList['prpnam'] = self.ilist._tonumpy(self.setProperty, func = PropertyValue.vName)
            xList['prpran'] = np.arange(len(xList['prp']))
        if maxname > 0 :
            for key,lis in xList.items() :
                if key[3:6] in ['str', 'nam', 'typ']:
                    for i in range(len(lis)) : lis[i] = lis[i][0:maxname]
        return xList

class ObservationError(Exception) :
    pass
