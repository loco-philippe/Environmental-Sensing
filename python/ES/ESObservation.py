# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: Philippe@loco-labs.io

The `ES.ESObservation` module contains the main class
of Environmental Sensing : `Observation` class.

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
import matplotlib.pyplot as plt
import struct
#import os
#os.chdir('C:/Users/a179227/OneDrive - Alliance/perso Wx/ES standard/python ESstandard/iList')
from ilist import Ilist, CborDecoder
#import ilist
from tabulate import tabulate
import cbor2

#from ESValue import _EsClassValue

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

    *getters*

    - `Observation.vList`
    - `Observation.vListName`
    - `Observation.vListSimple`
    - `Observation.vListValue`

    *add value*

    - `Observation.addAttributes`
    - `Observation.addJson`
    - `Observation.append`
    - `Observation.appendList`
    - `Observation.appendObs`

    *update value*

    - `Observation.majList`
    - `Observation.majValue`

    *selecting*

    - `Observation.indexLoc`
    - `Observation.iLoc`
    - `Observation.iObsIndex`
    - `Observation.loc`

    *management*

    - `Observation.extend`
    - `Observation.filter`
    - `Observation.full`
    - `Observation.sort`

    *visualization*

    - `Observation.choropleth`
    - `Observation.voxel`
    - `Observation.plot`
    - `Observation.view`

    *exports - imports*

    - `Observation.from_file`
    - `Observation.to_csv`
    - `Observation.to_dataFrame`
    - `Observation.to_json`
    - `Observation.to_numpy`
    - `Observation.to_file`
    - `Observation.to_xarray`
    - `Observation.to_bytes`              # à voir
    - `Observation.from_bytes`            # à voir

    """

#%% constructor
    def __init__(self, *args, order = [], idxref = {}, **kwargs):
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

        *Note : the parameters 'idxref' and 'order' are used only when an ESSetResult without Index is in arguments.
        'order' indicates the order for the Index creation and 'idxref' the linked index (0 for Datation, 1 for Location, 2 for Property).*
        '''
        kwargs |= {'order' : order, 'idxref' : idxref}
        self.name = "observation du " + datetime.datetime.now().isoformat()
        self.option = ES.mOption.copy()
        self.parameter = ES.nullAtt        # json
        self.ilist = Ilist()
        self.mAtt = {}
        #self.mAtt[ES.obs_reference] = 0
        self.mAtt[ES.obs_reference] = ES.nullVal
        self.mAtt[ES.obs_resultTime] = ES.nullAtt
        self.mAtt[ES.obs_id] = ES.nullAtt
        self._initObs(*args, **kwargs)

    @classmethod
    def Ilist(cls, ilist, name='', option=None, parameter=None, mAtt=None):
        obs = cls()
        obs.ilist = ilist 
        if name != '': obs.name = name
        if option: obs.option |= option
        if parameter: obs.parameter = parameter 
        if mAtt: obs.mAtt |= mAtt
        return obs
    
    def _initObs(self, *args, **kwargs):
        ''' data creation '''
        dic = {}
        if len(args) == 0 and len(kwargs) == 2 : args = [{}]
        for arg in args :
            if type(arg) == str :       # creation à partir d'un json "key : [liste]"
                try: arg=json.loads(arg, object_hook=CborDecoder().codecbor)
                except: pass
            elif isinstance(arg, bytes):
                if arg[len(arg)-1] != 0x00 and (arg[0] & 0b11100000) == 0b10100000:
                    dic=cbor2.loads(arg)
                else: dic = bson.decode(arg)
            if type(arg) == dict :      # creation à partir d'un dict "key : [liste]"
                for k,v in arg.items() :
                    if k not in dic : dic |= {k:v}
        if len(dic) == 1 and list(dic.keys())[0] == ES.obs_valName : dic = dic[ES.obs_valName] #!!!
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

    def _initDict(self, dic) :
        ''' data creation in dict mode'''
        js = {}
        for k,v in dic.items():
            if k in ES.invcodeb: js[ES.invcodeb[k]] = v
            else: js[k] = v
        if ES.obs_id in list(js): self.mAtt[ES.obs_id] = js[ES.obs_id]
        if ES.obs_attributes in list(js):
            if type(js[ES.obs_attributes]) == dict: js = js[ES.obs_attributes]
            else: return
        dicilist = {}
        order = []
        for classES in ES.esObsClass[0:3] :
            if classES in list(js) :
                dicilist[classES] =  js[classES]
                order.append(classES)
        if ES.res_classES in list(js) :
            dicilist[ES.res_classES] = js[ES.res_classES]
        if 'order' in list(js) and len(js['order'])>0: dicilist['order'] = js['order']
        else: dicilist['order'] = sorted(order)
        if 'idxref' in list(js) : dicilist['idxref'] = js['idxref']
        if 'index' in list(js) : dicilist['index'] = js['index']
        self.ilist = Ilist.from_obj(dicilist)
        ordern = sorted(self.ilist.idxname)
        if ordern != self.ilist.idxname: 
            self.ilist.swapindex([self.ilist.idxname.index(i) for i in ordern])
        self.addAttributes(js)
        
    def _initList(self, lis, **kwargs) :
        '''data creation in list mode '''
        if 'order' in kwargs : order = kwargs['order']
        else : order = ['datation', 'location', 'property']
        ordern = [ES.esObsClass.index(idx) for idx in order]
        if 'idxref' in kwargs : idxref = kwargs['idxref']
        else : idxref = {}
        idxrefn = [0,1,2]
        for key, val in idxref.items() :
            keyn = order.index(key)
            valn = order.index(val)
            idxrefn[max(keyn, valn)] = min(keyn, valn)
        self.ilist = Ilist.Iset(valiidx=lis[3],
                                setidx=[lis[0], lis[1], lis[2]], 
                                order=ordern, idxref=idxrefn, valname=ES.esObsClass[3], 
                                idxname=ES.esObsClass[0:3], defaultidx=False)

#%% special
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
    def axes(self):
        '''
        **list of integer (@property)** : list of independant axes in the Observation
        (0 for Datation, 1 for Location, 2 for Property)'''
        axes =[]
        for i in self.ilist.axes :
            if self.ilist.idxname[i] in ES.esObsClass:
                axes.append(ES.esObsClass.index(self.ilist.idxname[i]))
        return axes

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
    def complet(self):
        '''
        **boolean (@property)** : True if self.ilist is complete (if the number of 
        values is consistent with the number of index values)'''
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

    def append(self, dat, loc, prp, res, unique=False, equal='full', fast=False) :
        '''
        Add a new `ES.ESValue` to Result

        *Parameters*

        - **dat, loc, prp** : compatible Value for an existing or new `ES.ESValue`
        - **res** : compatible existing or new result `ES.ESValue`
        - **unique** : boolean (default False), if False, duplicate index is allowed
        - **equal** : string (default 'full'), if 'full', two ESValue are equal
            if all the attributes are equal, if 'name', two ESValue are equal if only the names are equal.
        - **fast** : boolean (default False) - Update whith ESValue and whithout reindex, equal=full

        *Returns*

        - **int** : last index in the result valueList (or 0 if fast).  '''
        self.ilist.idxname = ES.esObsClass[0:3]
        self.ilist.valname = ES.esObsClass[3]
        if fast :
            self.ilist.append(res, [dat, loc, prp], unique=unique, fast=fast)
            return 0
        if res.__class__.__name__ in _classval(): resvalue = res
        else: resvalue = _classval()[ESValue.valClassName(res)](res)
        datv = DatationValue(dat)
        locv = LocationValue(loc)
        prpv = PropertyValue(prp)
        if equal == 'full':
            #self.ilist.append(ReesultValue(res),
            self.ilist.append(resvalue, [datv, locv, prpv], unique=unique, fast=fast)
        elif equal == 'name':
            for val in self.setDatation :
                if ESValue.isEqual(val, datv, name=True, value=False):
                    datv = val
                    break
            for val in self.setLocation :
                if ESValue.isEqual(val, locv, name=True, value=False):
                    locv = val
                    break
            for val in self.setProperty :
                if ESValue.isEqual(val, prpv, name=True, value=False):
                    prpv = val
                    break
            #self.ilist.append(ReesultValue(res), [datv,locv, prpv], unique=unique, fast=fast)
            self.ilist.append(resvalue, [datv,locv, prpv], unique=unique, fast=fast)
        return len(self.ilist) - 1

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

    def full(self, minind=True, fillvalue=None, inplace=False) :
        '''
        Add empty Result `ES.ESValue` to have a 'complete' `Observation`

        *Parameters*

        - **inplace** : boolean (default False) - If True, add values to
        Observation, else return new Observation.
        - **minind** : boolean (default True) - If True, independent axes are
        completed with fillvalue, else all axes are completed
        - **fillvalue** : value used to complete the Observation

        *Returns*

        - **Observation** : new observation if not inplace, else None.
        '''
        if fillvalue is None : fillvalue = ES.nullVal #ReesultValue.nullValue()
        if minind == True : axes = self.ilist.axes
        else : axes = list(range(self.ilist.lenidx))
        if inplace :
            self.ilist.full(axes=axes, fillvalue=fillvalue, inplace=inplace)
            return None
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

    def majList(self, axename, listVal, name=False):
        '''
        Modify an attribute (name or value) in an axis list.

        *Parameters*

        - **axename** : index or result name
        - **listVal** : new list of values
        - **name** : boolean (default True) - True for 'name' and False for 'value'

        *Returns*

        - **None**  '''
        if axename == ES.dat_classES and self.setDatation != None :
            newlistVal = Observation._majList(self.setDatation, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.dat_classES)] = newlistVal
        elif axename == ES.loc_classES and self.setLocation != None :
            newlistVal = Observation._majList(self.setLocation, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.loc_classES)] = newlistVal
        elif axename == ES.prp_classES and self.setProperty != None :
            newlistVal = Observation._majList(self.setProperty, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.prp_classES)] = newlistVal
        elif axename == ES.res_classES and self.setResult != None :
            newlistVal = Observation._majList(self.setResult, listVal, name)
            self.ilist.extval = newlistVal

        '''if ValueClass == DatationValue and self.setDatation != None :
            newlistVal = Observation._majList(self.setDatation, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.dat_classES)] = newlistVal
        elif ValueClass == LocationValue and self.setLocation != None :
            newlistVal = Observation._majList(self.setLocation, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.loc_classES)] = newlistVal
        elif ValueClass == PropertyValue and self.setProperty != None :
            newlistVal = Observation._majList(self.setProperty, listVal, name)
            self.ilist.setidx[self.ilist.idxname.index(ES.prp_classES)] = newlistVal
        elif ValueClass == ReesultValue and self.setResult != None :
            newlistVal = Observation._majList(self.setResult, listVal, name)
            self.ilist.extval = newlistVal'''

    def majValue(self, esValue, newEsValue, name, equal="full"):
        '''
        Update the value of an existing `ES.ESValue` by a new `ES.ESValue`

        *Parameters*

        - **esValue** : ESValue to update
        - **newEsValue** : new ESValue
        - **name** : index or result name
        - **equal** : criteria used to compare ESValue ('full', 'name', 'value')

        *Returns*

        - **Int** : index in the ESSet valueList.  '''
        index = self.indexLoc(esValue, name)[equal]
        if   name == ES.prp_classES:     setClass = self.setProperty
        elif name == ES.loc_classES:     setClass = self.setLocation
        elif name == ES.dat_classES:     setClass = self.setDatation
        elif name == self.ilist.valname: setClass = self.setResult
        else : setClass = None
        
        '''index = self.indexLoc(esValue)[equal]
        if   type(esValue) == PropertyValue : setClass = self.setProperty
        elif type(esValue) == LocationValue : setClass = self.setLocation
        elif type(esValue) == DatationValue : setClass = self.setDatation
        elif type(esValue) == ReesultValue   : setClass = self.setResult
        else : setClass = None'''
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
                #obx = obx.set_index(prp = "prptyp", loc="locstr")
                obx = obx.set_index(prp = "prpstr", loc="locstr")
                obx.sortby(["dat","loc","prp"]
                           ).plot.line(x="dat", col="prp", xticks=list(obx.coords['dat'].values),
                                       col_wrap=2, size=size, marker=marker)
            else :
                #obx = obx.set_index(prp = "prptyp", loc="locran")
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

    def to_csv(self, file, **kwargs) :
        '''
        Generate csv file to display `Observation` data.

        *Parameters*

        - **file** : string - file name (with path)

        *Parameters (kwargs)*

        - **json** : boolean (default True) - Display json for `ES.ESValue`
        - **name** : boolean (default True) - Display name for `ES.ESValue`
        - **dat**  : boolean (default True) - Display value for `ES.ESValue.DatationValue`
        - **loc**  : boolean (default True) - Display value for `ES.ESValue.LocationValue`
        - **prp**  : boolean (default True) - Display value for `ES.ESValue.PropertyValue`
        - **res**  : boolean (default True) - Display value for Result `ES.ESValue`
        - **lenres** : int (default 0) - Number of raws (all if 0)

        *Returns*

        - **None**        '''
        option = {'json': True, 'name': True, 'dat': True, 'loc': True,
                  'prp': True, 'res': True, 'lenres': 0} | kwargs
        tab = self._to_tab(**option)
        size = 0
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for lign in tab : 
                writer.writerow(lign)
                size += len(lign)
        return size

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
        """if self._indexIsDefault(dic): 
            if 'index' in dic: dic.pop('index')
            if 'default index' in dic: dic.pop('default index')"""
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

    def to_xarray(self, info=False, numeric=False, ind='axe', fillvalue=None,
                  name='Observation', maxname=20, func=None, **kwargs):
        '''
        Convert `Observation` to DataArray.

        *Parameters*

        - **info** : Boolean (default False) - Generate a specific Coords with Observation characteristics.
        - **ind** : String (default 'axe') - 'axe' only independant axes, 'all' : all the axes, 'flat' : one dimension
        - **fillvalue** : Object (default '?') used to complete result
        - **func** : String (default function identity) - Name of the function applied to each Result `ES.ESValue`
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values.
        - **name** : String (default 'Observation') - Name of the xArray
        - **maxname** : String (default 20) - maximum length for string

        *Returns*

        - **xarray.DataArray**        '''
        if not self.ilist.consistent : raise ObservationError("Observation not consistent")
        if not self.ilist.extval : raise ObservationError("Observation empty")
        if ind == 'axe' : axes = self.ilist.axes
        else : axes = list(range(self.ilist.lenidx))
        ilf = self.ilist.full(axes=axes, fillvalue=fillvalue)
        ilf.sort(order=self.axes)
        #xList = self._xlist_old(maxname=maxname)
        xList = self._xlist(ilf, maxname=maxname)
        attrs = ES.xattrs | {'info' : self._info(encoded=False, json_info_type=True,
                                   json_info_nval  =False, json_info_box =True,
                                   json_info_other =False)["information"]}
        coord = self._xCoord(xList, attrs, ilf.idxref, numeric)
        dims = [ES.vName[ilf.idxname[ax]] for ax in ilf.axes]
        shape = [ilf.idxlen[axe] for axe in ilf.axes]
        if numeric : data = ilf._tonumpy(ilf.extval, func = ESValue.to_float).reshape(shape)
        else : data = ilf._tonumpy(ilf.extval, func=func, **kwargs).reshape(shape)
        #if numeric : data = ilf._tonumpy(ilf.extval, func = ReesultValue.to_float).reshape(ilf.axeslen)
        #else : data = ilf._tonumpy(ilf.extval, func=func, **kwargs).reshape(ilf.axeslen)
        if not info : return xr.DataArray(data, coord, dims, name=name)
        else : return xr.DataArray(data, coord, dims, attrs=attrs['info'], name=name)

    def view(self, **kwargs) :
        '''
        Generate tabular list to display `Observation` data.

        *Parameters (kwargs)*

        - **json** : boolean (default True) - Display json for `ES.ESValue`
        - **name** : boolean (default True) - Display name for `ES.ESValue`
        - **dat**  : boolean (default True) - Display value for `ES.ESValue.DatationValue`
        - **loc**  : boolean (default True) - Display value for `ES.ESValue.LocationValue`
        - **prp**  : boolean (default True) - Display value for `ES.ESValue.PropertyValue`
        - **lenres** : Integer (default : 0) - Number of raws (all if 0)
        - **width** : Integer (default 15) - Number of characters displayed for each attribute.
        - **tabulate params** : default 'tablefmt': 'simple', 'numalign': 'left', 'stralign': 'left',
                   'floatfmt': '.3f' - See tabulate module

        *Returns* : None '''
        opttab = {'json': True, 'name': True, 'dat': True, 'loc': True, 'prp': True, 'lenres': 0}
        optview = {'tablefmt': 'simple', 'numalign': 'decimal', 'stralign': 'left', 'floatfmt': '.2f'}
        option = opttab | optview | kwargs
        tab = self._to_tab(**{k: option[k] for k in opttab})
        width = ({'width': 15} | kwargs)['width']
        tab2 = [[ (lambda x : x[:width] if type(x)==str else x)(val) for val in lig] for lig in tab]
        print(tabulate(tab2, headers='firstrow', **{k: option[k] for k in optview}))

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
        Visualize Result `ES.ESValue` in a cube with voxels.

        *Parameters*

        - **sort** : Boolean (default False) - Sort along axis.

        *Returns*

        - **None**
        '''
        if not self.ilist.consistent : return
        obc = copy.deepcopy(self)
        if sort : obc.sort()
        obc.ilist.full()
        #obx = obc.to_xarray(numeric = False, func=ReesultValue.isNotNull)
        obx = obc.to_xarray(numeric = False, func=ESValue.isNotNull)
        obp = obx #>=0
        obp.set_index(loc='locran', dat='datran', prp='prpran')
        ax = plt.figure().add_subplot(projection='3d')
        ax.voxels(obp, edgecolor='k')
        ax.set_xticks(np.arange(self.nValueObs[0]))
        ax.set_yticks(np.arange(self.nValueObs[1]))
        ax.set_zticks(np.arange(self.nValueObs[2]))
        ax.set(xlabel='dat (index)', ylabel='loc (index)', zlabel='prp (index)')
        plt.show()

#%% internal
    @staticmethod
    def _boundingBox(listValue):
        ''' return a `ES.ESValue.ESValue` object with bounds values'''
        box = copy.deepcopy(listValue[0])
        for val in listValue:
            box = box.boxUnion(val)
        return box

    """@staticmethod 
    def _indexIsDefault(dic):
        return ('index' in dic and 'default index' in dic and dic['index']==[dic['default index']]) or \
               (not 'index' in dic and 'default index' in dic) or \
               ('index' in dic and len(dic['index'][0]) <= 1)"""
    
    def _info(self, **kwargs):
        ''' Create json dict with info datas'''
        option = self.option | kwargs
        dcinf = dict()
        if option["json_info"] or option["json_info_type"] : dcinf |= self._infoType()
        if option["json_info"] or option["json_info_nval"] : dcinf |= self._infoNval()
        if option["json_info"] or option["json_info_box"]  : dcinf |= self._infoBox(**option)
        if option["json_info"] or option["json_info_other"]: dcinf |= self._infoOther()
        ldel =[]
        for k,v in dcinf.items() :
            if type(v) == str and (v == "null" or v =='')   : ldel.append(k)
            if type(v) == list and v == ES.nullCoor         : ldel.append(k)
        for k in ldel :         del dcinf[k]
        if len(dcinf) == 0 :    return ""
        return {ES.information : dcinf }
        '''if len(dcinf) != 0 : dcinf = {ES.information : dcinf }
        if option["encoded"] :
            if len(dcinf) == 0 :    return ""
            else :                  return json.dumps(dcinf)
        else: return dcinf'''

    def _infoBox(self, **option):
        ''' Add box informations's key-value to dict dcinf'''
        dcinf = dict()
        if self.setLocation:
            dcinf[ES.loc_box] = list(self._boundingBox(self.setLocation).bounds)
            dcinf[ES.geo_box] = self._boundingBox(self.setLocation).__geo_interface__
        if self.setProperty: dcinf[ES.prp_box] = list(self._boundingBox(self.setProperty).bounds)
        if self.setDatation:
            bound = self._boundingBox(self.setDatation).bounds
            if option["encode_format"] == 'bson':
                dcinf[ES.dat_box] = [datetime.datetime.fromisoformat(bound[0]),
                                     datetime.datetime.fromisoformat(bound[1])]
            else : dcinf[ES.dat_box] = list(bound)
        return dcinf

    def _infoNval(self):
        ''' Add valueList lenght to dict dcinf'''
        dcinf = dict()
        for i in range(4) :
            if self.nValueObs[i] > 0 : dcinf[ES.json_nval[i]] = self.nValueObs[i]
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

    def _infoType(self):
        ''' Add information's key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.json_type_obs] = self.typeObs
        for i in range(4) :
            if   self.nValueObs[i] > 1 : dcinf[ES.json_type[i]] = ES.multi + ES.esObsClass[i]
            elif self.nValueObs[i] > 0 : dcinf[ES.json_type[i]] =            ES.esObsClass[i]
        return dcinf

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

    def _to_tab(self, **kwargs):
        ''' data preparation for view or csv export'''
        option = {'json': True, 'name': True, 'dat': True, 'loc': True,
                  'prp': True, 'res': True, 'lenres': 0} | kwargs
        json, name, dat, loc, prp, res, lenres = tuple(option.values())
        if self.setResult == None : return
        tab = list()
        resList = []
        if self.setDatation != None :
            if json : resList.append('datation')
            if name : resList.append('dat name')
            if dat  : resList.append('dat instant')
        if self.setLocation != None :
            if json : resList.append('location')
            if name : resList.append('loc name')
            if loc  : resList.append('loc coor x')
            if loc  : resList.append('loc coor y')
        if self.setProperty != None :
            if json : resList.append('property')
            if name : resList.append('prop name')
            if prp  : resList.append('prop type')
        if self.setResult != None :
            if json : resList.append('result')
            if name : resList.append('res name')
            if res :  resList.append('res value')
        tab.append(resList)
        if lenres == 0 : lenres = len(self.setResult)
        for i in range(min(lenres, len(self.setResult))) :
            resList = []
            if self.setDatation != None :
                idat = self.ilist.idxname.index(ES.dat_classES)
                if json : resList.append(self.setDatation[self.ilist.iidx[idat][i]].json(encoded=True, encode_format='json'))
                if name : resList.append(self.setDatation[self.ilist.iidx[idat][i]].name)
                if dat  : resList.append(self.setDatation[self.ilist.iidx[idat][i]].vSimple(string=True))
            if self.setLocation != None :
                iloc = self.ilist.idxname.index(ES.loc_classES)
                if json : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].json(encoded=True, encode_format='json'))
                if name : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].name)
                if loc  : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].vSimple()[0])
                if loc  : resList.append(self.setLocation[self.ilist.iidx[iloc][i]].vSimple()[1])
            if self.setProperty != None :
                iprp = self.ilist.idxname.index(ES.prp_classES)
                if json : resList.append(self.setProperty[self.ilist.iidx[iprp][i]].json(encoded=True, encode_format='json'))
                if name : resList.append(self.setProperty[self.ilist.iidx[iprp][i]].name)
                if prp  : resList.append(self.setProperty[self.ilist.iidx[iprp][i]].simple)
            if self.setResult != None :
                if json : resList.append(self.setResult[i].json(encoded=True, encode_format='json'))
                if name : resList.append(self.setResult[i].name)
                if res  : resList.append(self.setResult[i].value)
            tab.append(resList)
        return tab

    @staticmethod
    def _xCoord(xList, attrs, idxref, numeric) :
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

    """def _xlist_old(self, maxname=0):
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
        return xList"""

    @staticmethod 
    def _xlist(il, maxname=0):
        '''list generation for Xarray'''
        xList = {}
        setLocation = il.setname(ES.loc_classES)
        if setLocation != None and len(setLocation) > 1:
            xList['loc']    = il._tonumpy(setLocation)
            xList['locstr'] = il._tonumpy(setLocation, func = LocationValue.json)
            xList['loclon'] = il._tonumpy(setLocation, func = LocationValue.vPointX)
            xList['loclat'] = il._tonumpy(setLocation, func = LocationValue.vPointY)
            xList['locnam'] = il._tonumpy(setLocation, func = LocationValue.vName)
            xList['locran'] = np.arange(len(xList['loc']))
        setDatation = il.setname(ES.dat_classES)
        if setDatation != None and len(setDatation) > 1:
            xList['dat']    = il._tonumpy(setDatation)
            xList['datstr'] = il._tonumpy(setDatation, func = DatationValue.json)
            xList['datins'] = il._tonumpy(setDatation, func = DatationValue.vSimple)
            xList['datnam'] = il._tonumpy(setDatation, func = DatationValue.vName)
            xList['datran'] = np.arange(len(xList['dat']))
        setProperty = il.setname(ES.prp_classES)
        if setProperty != None and len(setProperty) > 1:
            xList['prp']    = il._tonumpy(setProperty)
            xList['prpstr'] = il._tonumpy(setProperty, func = PropertyValue.json)
            xList['prptyp'] = il._tonumpy(setProperty, func = PropertyValue.vSimple)
            xList['prpnam'] = il._tonumpy(setProperty, func = PropertyValue.vName)
            xList['prpran'] = np.arange(len(xList['prp']))
        if maxname > 0 :
            for key,lis in xList.items() :
                if key[3:6] in ['str', 'nam', 'typ']:
                    for i in range(len(lis)) : lis[i] = lis[i][0:maxname]
        return xList

class ObservationError(Exception) :
    pass

'''_classValue: dict = {        
        ES.obs_clsName: Observation,
        ES.dat_clsName: DatationValue,
        ES.loc_clsName: LocationValue,
        ES.prp_clsName: PropertyValue,
        ES.ext_clsName: ExternValue,
        ES.nam_clsName: NamedValue,
        ES.ili_clsName: Ilist,
        #ES.coo_clsName: coordinate,
        ES.tim_clsName: datetime.datetime,
        ES.slo_clsName: TimeSlot}        '''                             