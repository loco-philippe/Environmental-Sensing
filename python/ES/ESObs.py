# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: philippe@loco-labs.io

An `ESObservation.Observation` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
 
The Observation Object is built around three main bricks :
    
- Ilist Object which deal with indexing,
- ESValue Object which integrate the specificities of environmental data,
- Tools dedicated to particular domains ([Shapely](https://shapely.readthedocs.io/en/stable/manual.html) 
for location, TimeSlot for Datation)

The `ES.ESObservation` module contains the `Observation` class.

Documentation is available in other pages :

- The concept of 'observation' is describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Observation).
- The concept of 'indexed list' is describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression test are at 
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_observation.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples/Observation)


"""
from ESconstante import ES, _classval
#import ESValue
from ESValue import LocationValue, DatationValue, PropertyValue, \
    NamedValue, ExternValue, ESValue, ESValueEncoder
from timeslot import TimeSlot
import datetime
import json, folium, copy, csv, bson, math
import numpy as np
import xarray as xr
import struct
#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/iList')
from ilist import Ilist
from iindex import Iindex
from util import util, IindexEncoder, CborDecoder
#import ilist
from tabulate import tabulate
import cbor2
from copy import copy

#from ESValue import _EsClassValue

class Obs(Ilist) :
    """
    An `Observation` is derived from `ES.ilist` object.

    *Additional attributes (for @property see methods)* :

    - **name** : textual description
    - **id** : textual identity 
    - **param** : namedValue dictionnary (external data)

    The methods defined in this class are :
    """

#%% constructor
    def __init__(self, listidx=None, name=None, id=None, param=None, length=None, var=None, reindex=True, 
                 typevalue=ES.def_clsName, context=True):
        '''
        Several Observation creation modes :

        - Observation(dictESValue1, dictESValue2, ...) where dictESValue = {ESValuename : value}
        - Observation({ObsDict}) where ObsDict is a dictionnary with the same data as an ObsJSON
        - Observation(ObsJSON) where ObsJSON is a string with the JSON format
        - Observation(ObsBSON) where ObsBSON is a bytes with the BSON format
        - Observation([ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult]) where ESSet is a list of ESValue :
            [ESValue1, ESValue2,...] or [ESValue] or ESValue
        - Observation(datation=ESSetDatation, location=ESSetLocation,
                      property=ESSetProperty, result=ESSetResult)

        - **context** : boolean (default True) - if False, only codec and keys are included'''
        if isinstance(listidx, Obs): 
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.lvarname = [name for name in listidx.lvarname]
            if not listidx.param is None: self.param = {k:v for k,v in listidx.param.items()}
            else: self.param = param
            self.name = listidx.name
            self.id = listidx.id
            return
        if isinstance(listidx, Ilist): 
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.lvarname = [name for name in listidx.lvarname]
            self.param = param
            self.name = name
            self.id = id
            return
        if not listidx: Ilist.__init__(self)
        else: Ilist.__init__(self, listidx=listidx, length=length, var=var, 
                             reindex=reindex, typevalue=typevalue, context=context)
        if ES.res_classES in self.lname: self.lvarname = [ES.res_classES]
        self.name = name
        self.id = id
        self.param = param

    @classmethod
    def Idic(cls, idxdic=None, typevalue=ES.def_clsName, name=None, id=None, param=None, var=None):
        '''
        Obs constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **fullcodec** : boolean (default False) - full codec if True
        - **var** :  int (default None) - row of the variable
        - **name**     : string (default None) - Observation name
        - **id**       : string (default None) - Identification string
        - **param**    : dict (default None) - Dict with parameter data or user's data'''  
        if ES.res_classES in idxdic: var = list(idxdic.keys()).index(ES.res_classES)
        listidx = Ilist.Idic(idxdic, typevalue=typevalue, var=var)
        return cls(listidx=listidx, name=name, id=id, param=param, context=True)
        
    @classmethod
    def Std(cls, result=None, datation=None, location=None, property=None, 
            name=None, id=None, param=None):
        '''
        Generate an Obs Object with standard indexes

        *Parameters*

        - **datation** : compatible Iindex (default None) - index for DatationValue
        - **location** : compatible Iindex (default None) - index for LocationValue
        - **property** : compatible Iindex (default None) - index for PropertyValue
        - **result  ** : compatible Iindex (default None) - index for Variable(NamedValue)
        - **name**     : string (default None) - Observation name
        - **id**       : string (default None) - Identification string
        - **param**    : dict (default None) - Dict with parameter data or user's data'''
        listidx = []
        length = -1
        if result is None: 
            listidx.append([ES.res_classES,[]])
            length = 0
        else: listidx.append(Iindex.Iext(result  , ES.res_classES))
        if datation is None: listidx.append([ES.dat_classES,[]])
        else: listidx.append(Iindex.Iext(datation, ES.dat_classES))
        if location is None: listidx.append([ES.loc_classES,[]]) 
        else: listidx.append(Iindex.Iext(location, ES.loc_classES))
        if property is None: listidx.append([ES.prp_classES,[]]) 
        else: listidx.append(Iindex.Iext(property, ES.prp_classES))
        return cls(listidx=listidx, length=length, name=name, id=None, param=param, var=0, context=True)

    @classmethod
    def from_obj(cls, bs=None, reindex=True, context=True):
        '''
        Generate an Obs Object from a bytes, string or dic value

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        if not bs: bs = []
        if   isinstance(bs, bytes): dic = cbor2.loads(bs)
        elif isinstance(bs, str)  : dic = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, dict) : dic = bs
        else: raise ObsError("the type of parameter is not available")
        if ES.id in dic:    id = dic[ES.id]
        else:               id = None
        if id and not isinstance(id, str): raise ObsError('id is not a str')
        if ES.param in dic: param = dic[ES.param]
        else:               param = None
        if param and not isinstance(param, dict): raise ObsError('param is not a dict')
        if ES.name in dic:  name = dic[ES.name]
        else:               name = None
        if name and not isinstance(name, str): raise ObsError('name is not a str')
        if ES.data in dic:  data = dic[ES.data]
        else:               data = None
        if data and not isinstance(data, list): raise ObsError('data is not a list')
        return cls(listidx=Ilist.Iobj(data), name=name, id=id, param=param, context=context)

#%% special
    def __copy__(self):
        ''' Copy all the data '''
        return Obs(self)

    def __str__(self):
        '''return string format for var and lidx'''
        if self.name: stro = ES.name + ': ' + self.name + '\n'
        else: stro = ''
        if self.id: stro += ES.id + ': ' + self.id + '\n'
        stri = Ilist.__str__(self)
        if not stri == '': stro += ES.data + ':\n' + stri
        for idx in self.lidx: stri += str(idx)
        if self.param: stro += ES.param + ':\n    ' + json.dumps(self.param) + '\n'
        return stro

    def __eq__(self, other):
        ''' equal if all attribut and Ilist are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and self.name == other.name \
            and self.id == other.id and self.param == other.param  \
            and Ilist.__eq__(self, other)

    def __hash__(self): 
        '''return sum of all hash(Iindex)'''
        return hash(self.param) + hash(self.id) + hash(self.name) + Ilist.__hash__(self)

#%% properties
    @property
    def bounds(self):
        '''
        **list of `ES.ESValue` (@property)** : `ES.ESValue` bounding box for each axis.'''
        bound = [None, None, None]
        if self.setDatation : bound[0] = ESValue.boundingBox(self.setDatation).bounds
        if self.setLocation : bound[1] = ESValue.boundingBox(self.setLocation).bounds
        if self.setProperty : bound[2] = ESValue.boundingBox(self.setProperty).bounds
        return bound

    @property
    def setDatation(self):
        '''**list (@property)** : list of codec values in the datation index'''
        if self.nindex(ES.dat_classES): return self.nindex(ES.dat_classES).codec
        return None

    @property
    def setLocation(self):
        '''**list (@property)** : list of codec values in the location index'''
        if self.nindex(ES.loc_classES): return self.nindex(ES.loc_classES).codec
        return None

    @property
    def setProperty(self):
        '''**list (@property)** : list of codec values in the property index'''
        if self.nindex(ES.prp_classES): return self.nindex(ES.prp_classES).codec
        return None

    @property
    def setResult(self):
        '''
        **list (@property)** : list of codec values in the result index'''
        if self.nindex(ES.res_classES): return self.nindex(ES.res_classES).codec
        return None

#%% methods
    def appendObs(self, obs, unique=False, fillvalue='-') :
        '''
        Add an `Observation` as a new Result `ES.ESValue` with bounding box for the Index `ES.ESValue`

        *Parameters*

        - **obs** : Observation
        - **fillvalue** : object value used for default value

        *Returns*

        - **int** : last index in the `Observation`
        '''
        record = [fillvalue] * len(self.lname)
        if ES.dat_classES in self.lname:
            record[self.lname.index(ES.dat_classES)] = DatationValue.Box(obs.bounds[0])
        if ES.loc_classES in self.lname:
            record[self.lname.index(ES.loc_classES)] = LocationValue.Box(obs.bounds[1])
        if ES.prp_classES in self.lname:
            record[self.lname.index(ES.prp_classES)] = PropertyValue.Box(obs.bounds[2])
        if ES.res_classES in self.lname:
            record[self.lname.index(ES.res_classES)] = ExternValue(obs)
        return self.append(record, unique=unique)

    def to_obj(self, **kwargs):
        '''Return a formatted object (json string, cbor bytes or json dict). 

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **fullcodec** : boolean (default False) - if True, each index is with a full codec
        - **defaultcodec** : boolean (default False) - if True, each index is whith a default codec
        - **name** : boolean (default False) - if False, default index name are not included

        - **json_res_index** : Boolean - include index for Variable
        - **json_param**     : Boolean - include Obs Param
        - **json_info**      : Boolean - include all infos
        - **json_info_type** : Boolean - include info_type
        - **json_info_nval** : Boolean - include the lenght of Iindex
        - **json_info_box**  : Boolean - include the bounding box
        - **json_info_other**: Boolean - include the other infos

        *Returns* : string, bytes or dict'''
        option = {'fullcodec': False, 'defaultcodec': False, 'encoded': False, 
                  'encode_format': 'json', 'codif': ES.codeb, 'name': False,
                  'json_param': False, 'json_info': False, 'json_info_type': False,
                  'json_info_nval': False, 'json_info_box': False, 
                  'json_info_other': False} | kwargs
        option2 = option | {'encoded': False, 'encode_format': 'json'}
        dic = { ES.type : ES.obs_classES }
        if self.id: dic[ES.obs_id] = self.id
        if self.name: dic[ES.obs_name] = self.name
        if self.param: dic[ES.obs_param] = self.param
        dic[ES.obs_data] = Ilist.to_obj(self,**option2)
        if option["json_param"] and self.param:
            dic[ES.obs_param] = self.param
        dic |= self._info(**option)
        if option['codif'] and option['encode_format'] != 'cbor':
            js2 = {}
            for k,v in dic.items():
                if k in option['codif']: js2[option['codif'][k]] = v
                else: js2[k] = v
        else: js2 = dic
        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(js2, cls=IindexEncoder)
        #if option['encoded'] and option['encode_format'] == 'bson':
        #    return bson.encode(js2)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(js2, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return dic


#%% internal
    def _info(self, **kwargs):
        ''' Create json dict with info datas'''
        option = ES.mOption | kwargs
        dcinf = dict()
        if option["json_info"] or option["json_info_nval"] : 
            dcinf |= dict(zip(['len-'+name for name in self.lname], self.indexlen))
        if option["json_info"] or option["json_info_box"]  : 
            dcinf |= self._infoBox(**option)
        if option["json_info"] or option["json_info_other"]: 
            dcinf |= self._infoOther()
        ldel =[]
        for k,v in dcinf.items() :
            if type(v) == str and (v == "null" or v =='')   : ldel.append(k)
            if type(v) == list and v == ES.nullCoor         : ldel.append(k)
        for k in ldel: del dcinf[k]
        if len(dcinf) == 0 :    return ""
        return {ES.information : dcinf }

    def _infoBox(self, **option):
        ''' Add box informations's key-value to dict dcinf'''
        dcinf = dict()
        if self.setLocation:
            dcinf[ES.loc_box] = list(ESValue.boundingBox(self.setLocation).bounds)
            dcinf[ES.geo_box] = ESValue.boundingBox(self.setLocation).__geo_interface__
        if self.setProperty: dcinf[ES.prp_box] = list(ESValue.boundingBox(self.setProperty).bounds)
        if self.setDatation:
            bound = ESValue.boundingBox(self.setDatation).bounds
            if option["encode_format"] == 'json': dcinf[ES.dat_box] = list(bound)
            else: dcinf[ES.dat_box] = [datetime.datetime.fromisoformat(bound[0]),
                                       datetime.datetime.fromisoformat(bound[1])]
        return dcinf

    def _infoOther(self):
        ''' Add other's information key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.obs_complet] = self.complete
        #dcinf[ES.obs_score]   = self.score
        #dcinf[ES.res_mRate]   = self.rate
        dcinf[ES.res_dim]     = self.dimension
        dcinf[ES.res_axes]    = [self.idxname[i] for i in self.primary]
        return dcinf


"""
#%% special
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

    def __getitem__(self, ind):
        ''' return ResValue item'''
        return self.ilist[ind]

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        #self.ilist += other.ilist
        self.ilist.iadd(other.ilist, unique=self.option["unic_index"])
        self.option = other.option | self.option
        self.mAtt = other.mAtt | self.mAtt
        return self

    def __add__(self, other):
        ''' Add other's values to self's values and return a new Observation'''
        obres = self.__copy__()
        obres.__iadd__(other)
        return obres

    def __len__(self): return len(self.ilist)

    def __repr__(self):
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(self.ilist.lenidx) + ']'

    def __to_bytes__(self, **option):
        return self.to_json(encoded=option['encoded'], encode_format='bson',
                            json_info=False, json_res_index=True, json_param=True)

#%% properties
    @property
    def bounds(self):
        '''
        **list of `ES.ESValue` (@property)** : `ES.ESValue` bounding box for each axis.'''
        bound = [None, None, None]
        #if self.setDatation : bound[0] = self._boundingBox(DatationValue, self.setDatation)
        #if self.setLocation : bound[1] = self._boundingBox(LocationValue, self.setLocation)
        if self.setDatation : bound[0] = self._boundingBox(self.setDatation)
        if self.setLocation : bound[1] = self._boundingBox(self.setLocation)
        if self.setProperty : bound[2] = self.setProperty[0]
        return bound

    @property
    def json(self):
        '''
        **string (@property)** : JSON Observation (ObsJSON format) whit index
        and whitout informations'''
        return self.to_json(encoded=True, encode_format='json',
                            json_info=False, json_res_index=True, json_param=True)

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
            return json.dumps(dict((("type","FeatureCollection"), ("features",fea))), cls=ESValueEncoder)
        else: return ''

    @property
    def nValueObs(self):
        '''
        **list (@property)** : lenght of axes [datation, location, properety, result].'''
        nvalue =[]
        for esclass in ES.esObsClass[0:3] :
            nval = 0
            for i in range(len(self.ilist.idxlen)) :
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
    def typeObs(self):
        '''
        **string (@property)** : Observation type (calculated from the score)'''
        if self.consistent : return ES.obsCat[self.score]
        else : return ES.obsCat[-1]
#%% methods
    def addAttributes(self, js):
        '''
        Add informations attached to `Observation`

        *Parameters*

        - **js** : Dict - Keys are Observation keys (dict mAtt) or users keys (dict parameter).

        *Returns*

        - **None**  '''
        if type(js) != dict: return
        for k, v in js.items():
            if k not in [ES.type, ES.information] and (self._isESAtt(ES.obs_classES, k) or
                                                       k not in ES.reserved) :
                self.mAtt[k] = v
            if k == ES.parameter:
                try:  self.parameter = json.dumps(v, cls=ESValueEncoder)
                except:  self.parameter = ES.nullAtt

    def addJson(self, js):
        '''
        Complete an empty `Observation` with json data.

        *Parameters*

        - **js** : string - ObsJSON data

        *Returns*

        - **None**        '''
        try: dic=json.loads(js)
        except: return
        self._initDict(dic)

    def appendList(self, listDat, listLoc, listPrp, listVal, unique=False, equal='full'):
        '''
        Add a list of new `ES.ESValue` to Result

        *Parameters*

        - **listVal** : list of ES.ESValue compatible type
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
        Add an `Observation` as a new Result `ES.ESValue` with bounding box for the Index `ES.ESValue`

        *Parameters*

        - **obs** : Observation

        *Returns*

        - **int** : last index in the `Observation`
        '''
        #return self.append(obs.bounds[0], obs.bounds[1], obs.bounds[2], obs, unique=unique, equal=equal)
        return self.append(obs.bounds[0], obs.bounds[1], obs.bounds[2], ExternValue(obs), unique=unique, equal=equal)

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

    def filter(self, inplace=False, **filterdic):
        '''
        Remove `ES.ESValue` from Result that does not match the indexes filter.
        The filter is a list of tests of the form : "indexvalue.method(parameter) is True"
        where keyword "method : parameter" are given in the dictionnary. Filters are cumulatives.

        *Parameters*

        - **inplace** : boolean (default False) - If True, apply filter to
        Observation, else return new Observation.
        - **filterdic** : keyword arguments (keys is a ClassES and value is a dictionnary) .
                          where dict value contains keyword "method : parameter"

        *Returns*

        - **Observation** : new observation if not inplace, else None.
        '''
        setidxf = [list(range(self.ilist.idxlen[idx])) for idx in range(self.ilist.lenidx)]
        if filterdic is None or not isinstance(filterdic,  dict) :
            raise ObservationError("filter is not a dictionnary")
        for ESclass, dic in filterdic.items():
            if dic is None or not isinstance(dic,  dict) :
                raise ObservationError("filter is not a dictionnary")
            if ESclass not in ES.esObsClass : continue
            idx = self.ilist.idxname.index(ESclass)
            for test, value in dic.items():
                setidx = self.ilist._idxfilter(test, 'setidx', idx, value)
                setidxf[idx] = [i for i in setidxf[idx] if i in setidx]
        if inplace :
            self.ilist.setfilter(setidxf, inplace=inplace)
            return None
        newobs = Observation()
        newobs.ilist     = self.ilist.setfilter(setidxf, inplace=False)
        newobs.mAtt      = self.mAtt
        newobs.parameter = self.parameter
        newobs.option    = self.option
        return newobs

    @classmethod    
    def from_bytes(cls, byt):
        '''
        Generate `Observation` object from byte value.
        
        *Returns* : `Observation`'''
        iidx = []
        iidxref = {}
        nb_el   =  byt[0] & 0b00001111
        obsref  = (byt[0] & 0b00010000) >> 4
        code_el = (byt[0] & 0b11100000) >> 5
        idx = 1
        #ref_obs = None
        dic = {} 
        if obsref: 
            dic[ES.obs_reference] = struct.unpack('<H',byt[1:3])[0]           
            idx += 2
        nval=-1
        for i in range(nb_el):
            tup = cls._list_from_bytes(byt[idx:], nval)
            if i == 0 : nval = len(tup[1])
            idx += tup[0]
            if   tup[2] == ES.index: iidx.append(tup[1])
            elif tup[2] == ES.idxref: iidxref = tup[1]
            elif tup[2] not in dic: dic[tup[2]] = tup[1]
            elif tup[3]: 
                for i in range(len(tup[1])): dic[tup[2]][i].setName(tup[1][i].name)
            else: 
                for i in range(len(tup[1])): dic[tup[2]][i].setValue(tup[1][i].value)
        if iidx:    dic[ES.index]=iidx
        if iidxref:  dic[ES.idxref]={ES.invcodeb[k] : ES.invcodeb[v] for k,v in iidxref.items()}
        #print('dic : ', dic)
        return Observation(dic)
    
    @classmethod
    def from_file(cls, file) :
        '''
        Generate `Observation` object from file storage.

         *Parameters*

        - **file** : string - file name (with path)

        *Returns* : `Observation`'''
        with open(file, 'rb') as f: btype = f.read(22)
        if btype==bytes('{"' +ES.type+'": "' + ES.obs_classES +'"', 'UTF-8'):
            with open(file, 'r', newline='') as f: bjson = f.read()
        else:
            with open(file, 'rb') as f: bjson = f.read()
        return cls(bjson)

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

    def indexLoc(self, esValue, name, string=True):
        '''
        Return the index of a `ES.ESValue` in a `ES.ilist.Ilist` index or result

        *Parameters*

        - **esValue** : `ES.ESValue`,
        - **name** : index or result name
        - **string** : Boolean (default True) - Return type (JSON if True, dict if False)

        *Returns*

        - **dict or string** : {'full' : indFull, 'name' : indName, 'value' : indValue }
            - indFull : integer for the first index value with name and value equality
            - indName : integer for the first index value with name equality
            - indFull : integer for the first index value with value equality  '''
        if   name == ES.prp_classES:     lis = self.setProperty
        elif name == ES.loc_classES:     lis = self.setLocation
        elif name == ES.dat_classES:     lis = self.setDatation
        elif name == self.ilist.valname: lis = self.setResult
        else : return None
        '''if   type(esValue)== PropertyValue : lis = self.setProperty
        elif type(esValue)== LocationValue : lis = self.setLocation
        elif type(esValue)== DatationValue : lis = self.setDatation
        elif type(esValue)== ReesultValue   : lis = self.setResult
        else: return None'''
        ind = {'full' : -1, 'name' : -1, 'value' : -1}
        for i in range(len(lis)):
            if lis[i].isEqual(esValue, name=True, value=True):
                ind['full'] = ind['name'] = ind['value'] = i
                return ind
            if lis[i].isEqual(esValue, name=True, value=False) and ind['name'] == -1:
                ind['name'] = i
            if lis[i].isEqual(esValue, name=False, value=True) and ind['value'] == -1:
                ind['value'] = i
        if string : return json.dumps(ind, cls=ESValueEncoder)
        else : return ind

    def iObsIndex(self, ind):
        '''
        Return the `ES.ESValue` index values for an Observation row.

        *Parameters*

        - **ind** : row Observation (equivalent to Result row)
        - **json** : Boolean (default True) - Return JSON string if True

        *Returns*

        - **list** : index of each ES.ESValue [idat, iloc, iprp]  '''
        return self.ilist.tiidx[ind]


    def loc(self, valDat, valLoc, valPrp, json=True):
        '''
        Return the `ES.ESValue` values for a DatationValue, LocationValue, PropertyValue.

        *Parameters*

        - **valdat, valloc, valprp** : DatationValue, LocationValue, PropertyValue

        *Returns*

        - **dict** : dict or JSON of each ES.ESValue (dat, loc, prp, res)  '''
        index = self.ilist.extidxtoi([DatationValue(valDat),LocationValue(valLoc),PropertyValue(valPrp)])
        return self.iLoc(index[0], index[1], index[2])

    def sort(self, order=[], reindex=True):
        '''
        Modify the order of `ES.ESValue`.

        *Parameters*

        - **order** : list (default []) - Ordered list to follow (0:dat, 1:loc, 2:prp).
        - **reindex** : boolean (default True) - calculate new index values.

        *Returns*

        - **None**        '''
        
        self.ilist.sort(order=[self.ilist.idxname.index(num) for num in order], reindex=reindex)
    
    def to_bytes(self, option=ES.bytedict):
        '''
        Export in binary format. 
        
        *Returns*
        
        - **bytes** : binary representation of the `Observation`
        '''
        opt = ES.bytedict | option
        nb=0 
        il = self.ilist 
        index = not il.complete
        for name in il.idxname: #!!!!
            #if name in opt: nb += len(opt[name]) + 1
            if name in opt: nb += len(opt[name]) + index
        if il.valname in opt: nb += len(opt[il.valname])
        nb += il.complete
        obsref = not math.isnan(self.mAtt[ES.obs_reference])
        byt = struct.pack('<B', 0b11100000 | (obsref << 4) | nb) 
        if obsref:
            byt += struct.pack('<H', self.mAtt[ES.obs_reference])
        if il.valname in opt: 
            for typevalue in opt[il.valname]: 
                byt += self._list_to_bytes(il.extval, il.valname, typevalue)
        for i in range(il.lenidx):
            if il.idxname[i] in opt:
                for typevalue in opt[il.idxname[i]]: 
                    byt += self._list_to_bytes(il.setidx[i], il.idxname[i], typevalue)
                if not il.complete: byt += self._list_to_bytes(il.iidx[i], ES.index, ES.index)
        if il.complete: 
            iidxref={ES.codeb[k] : ES.codeb[v] for k,v in il.dicidxref.items()}
            byt += self._list_to_bytes(iidxref, ES.index, ES.idxref)
        return byt


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

    def to_file(self, file, **kwargs) :
        '''
        Generate obs file to display `Observation` data.

         *Parameters (kwargs)*

        - **file** : string - file name (with path)
        - **kwargs** : see 'to_json' parameters

        *Returns*

        - **Integer** : file lenght (bytes)  '''
        option = kwargs | {'encoded': True, 'json_res_index': True}
        data = self.to_json(**option)
        if kwargs['encode_format'] == 'bson':
            lendata = len(data)
            with open(file, 'wb') as f: f.write(data)
        else:
            lendata = len(bytes(data, 'UTF-8'))
            with open(file, 'w', newline='') as f: f.write(data)
        return lendata

    def to_json(self, **kwargs):
        '''
        Export in Bson or Json format.

        *Parameters (optional, default value in option attribute)*

        - **encoded**   : boolean - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string - choice for return format (bson, json, cbor)
        - **json_res_index** : Boolean - include index for Result
        - **json_param**     : Boolean - include ESObs Parameter
        - **json_info**      : Boolean - include ESObs Information with all information
        - **json_info_type** : Boolean - include in ESObs Information the type of ESObs
        - **json_info_nval** : Boolean - include in ESObs Information the lenght of ESObs
        - **json_info_box**  : Boolean - include in ESObs Information the bounding box
        - **json_info_other**: Boolean - include in ESObs Information the other information
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder

        *Returns*

        - **string or dict** : Json string or dict        '''
        option = self.option | kwargs
        option2 = option | {'encoded': False}
        #option2 = option | {'encoded': option['bjson_bson']}
        dic = { ES.type : ES.obs_classES }
        if self.mAtt[ES.obs_id] != ES.nullAtt: dic[ES.obs_id] = self.mAtt[ES.obs_id]
        dic |= self._jsonAtt(**option2)
        dic |= self.ilist.json(**option2)
        if self._orderIsDefault(dic['order']): dic.pop('order')
        if self._indexIsDefault(dic): 
            if 'index' in dic: dic.pop('index')
            if 'default index' in dic: dic.pop('default index')
        if option["json_param"] and self.parameter != ES.nullAtt:
            dic[ES.parameter] = self.parameter
        dic |= self._info(**option2)
        if option['codif'] and option['encode_format'] != 'bson':
            js2 = {}
            for k,v in dic.items():
                if k in option['codif']: js2[option['codif'][k]] = v
                else: js2[k] = v
        else: js2 = dic
        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(js2, cls=ESValueEncoder)
        if option['encoded'] and option['encode_format'] == 'bson':
            return bson.encode(js2)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(js2, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return dic

    def to_numpy(self, func=None, ind='axe', fillvalue=None, **kwargs):
        '''
        Convert `Observation` to Numpy array.

        *Parameters*

        - **ind** : String (default 'axe') - 'axe' only independant axes, 'all' : all the axes, 'flat' : one dimension
        - **fillvalue** : Object (default '?') used to complete result
        - **func** : String (default function identity) - Name of the function to apply to the result values

        *Returns*

        - **Numpy array**    '''
        return self.ilist.to_numpy(func=func, ind=ind, fillvalue=fillvalue, **kwargs)

    def vListValue(self, idxname):
        '''
        Generate a list of value (see `ES.ESValue` getValue method) for an axis.

        *Parameters*

        - **idxname** : string - Name of the axis (datation, location, property, result)

        *Returns*

        - **list** : list of the values      '''
        return self.vList(idxname, func = ESValue.getValue)

#%% internal
    @staticmethod
    def _boundingBox(listValue):
        ''' return a `ES.ESValue.ESValue` object with bounds values'''
        box = copy.deepcopy(listValue[0])
        for val in listValue:
            box = box.boxUnion(val)
        return box

    @staticmethod 
    def _indexIsDefault(dic):
        return ('index' in dic and 'default index' in dic and dic['index']==[dic['default index']]) or \
               (not 'index' in dic and 'default index' in dic) or \
               ('index' in dic and len(dic['index'][0]) <= 1)
    

    @staticmethod
    def _isESAtt(esClass, key):
        '''identify if 'key' is included in 'esClass'

        *Parameters*

        - **esClass** : string for an ESClass attribute
        - **key** : string to search

        *Returns*

        - **Boolean**        '''
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
    def _list_from_bytes(byt, nv=-1):
        lis=[]
        code_el = (byt[0] & 0b11100000) >> 5
        unique  = (byt[0] & 0b00010000) >> 4        
        code_ES =  byt[0] & 0b00001111
        #if byt[0:1] == struct.pack('<B', 0b11000000):
        if code_el == 6 and not unique:
            for i in range(nv):
                lis.append(struct.unpack('<B',byt[i+1:i+2])[0])
            return (nv+1, lis, ES.index, True)  
        if code_el == 6 and unique:
            dic = {}
            for i in range(code_ES):
                dic[struct.unpack('<B',byt[2*i+1:2*i+2])[0]] = struct.unpack('<B',byt[2*i+2:2*i+3])[0]
            return (2 * code_ES + 1, dic, ES.idxref,    True)
        nameES  = code_ES in ES.namevalue
        mini    = code_ES in ES.minivalue
        idx = nval = 1
        if not unique: 
            nval = struct.unpack('<H',byt[1:3])[0]
            idx += 2
        if code_el in [ES.codeb[ES.res_classES], ES.codeb[ES.res_value]]:
            code_el = ES.codeb[ES.res_classES]
        for i in range(nval):
            esVal = _classval()[ES.invcodeb[code_el]]()
            if nameES and mini: 
                n = esVal._from_strBytes(byt[idx:idx+ES.miniStr], simple=True)
            elif nameES and not mini: 
                n = esVal._from_strBytes(byt[idx:], simple=False)
            elif code_el == ES.codeb[ES.res_classES]: 
                n = esVal.from_bytes(byt[idx:], ES.invProp[code_ES])
            else: 
                n = esVal.from_bytes(byt[idx:], mini)
            lis.append(esVal)
            idx += n
        return (idx, lis, ES.invcodeb[code_el], nameES)  

    @staticmethod 
    def _list_to_bytes(eslist, classES, typevalue):
        unique = len(eslist) == 1 
        arg = None
        if typevalue in ES.prop:        
            arg = ES.prop[typevalue][0]
            codeEl = ES.codeb[ES.res_value]
        elif typevalue in ES.codevalue:   
            arg = ES.codevalue[typevalue]
            codeEl = ES.codeb[classES]
        elif typevalue in [ES.index, ES.idxref]: pass
        else: return ObservationError("typevalue not consistent")
        mini = typevalue in ES.codevalue and arg in ES.minivalue
        name = typevalue in ES.codevalue and arg in ES.namevalue        
        if typevalue == ES.index: 
            byt = struct.pack('<B', 0b11000000)
        elif typevalue == ES.idxref: 
            byt = struct.pack('<B', (ES.codeb[ES.index] << 5) | ((typevalue == ES.idxref) << 4) | len(eslist))
        else: 
            byt = struct.pack('<B', (codeEl << 5) | (unique << 4) | arg)
            if not unique : byt += struct.pack('<H', len(eslist))
        if name and mini: 
            for val in eslist: byt += val._to_strBytes(simple=True, mini=True)
        elif name and not mini: 
            for val in eslist: byt += val._to_strBytes(simple=False, mini=False)
        elif classES == ES.res_classES: 
            for val in eslist: byt += val.to_bytes(typevalue) 
        elif typevalue == ES.index:
            for val in eslist: byt += struct.pack('<B', val)        
        elif typevalue == ES.idxref:
            for key, val in eslist.items(): 
                byt += struct.pack('<B', key)
                byt += struct.pack('<B', val)
        else: 
            for val in eslist: byt += val.to_bytes(mini)
        return byt
    
    @staticmethod
    def _majList(listVal, newlistVal, name=False):
        ''' update value or name in a list of `ES.ESValue` '''
        if name :   return Observation._majListName (listVal, newlistVal)
        else :      return Observation._majListValue(listVal, newlistVal)

    @staticmethod
    def _majListName(listVal, newlistVal):
        ''' update name in a list of `ES.ESValue` '''
        if len(listVal) != len(newlistVal) :
            raise ObservationError("inconsistent length of the lists : " +
                                   str(len(listVal)) + " and " + str(len(newlistVal)))
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

    @staticmethod 
    def _orderIsDefault(order):
        if len(order) == 1: return True
        return order in [[ES.dat_classES, ES.loc_classES], [ES.dat_classES, ES.prp_classES],
                         [ES.loc_classES, ES.prp_classES], [ES.dat_classES, ES.loc_classES, ES.prp_classES]]


"""
class ObsError(Exception) :
    pass

