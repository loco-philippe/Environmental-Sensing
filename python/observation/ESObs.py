# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: philippe@loco-labs.io

An `ESObs.Obs` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
 
The Obs Object is built around three main bricks :
    
- Ilist Object which deal with indexing,
- ESValue Object which integrate the specificities of environmental data,
- Tools dedicated to particular domains ([Shapely](https://shapely.readthedocs.io/en/stable/manual.html) 
for location, TimeSlot for Datation)

The `ES.ESObs` module contains the `Obs` class.

Documentation is available in other pages :

- The concept of 'observation' is describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Observation).
- The concept of 'indexed list' is describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression test are at 
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_observation.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples/Observation)


"""
from ESconstante import ES
#import ESValue
from ESValue import LocationValue, DatationValue, PropertyValue, \
    ExternValue, ESValue, ESValueEncoder
import datetime
import json, folium
from ilist import Ilist
from iindex import Iindex
from util import util, IindexEncoder, CborDecoder
import cbor2
from copy import copy

#from ESValue import _EsClassValue

class Obs(Ilist) :
    """
    An `Obs` is derived from `ES.Ilist` object.

    *Additional attributes (for @property see methods)* :

    - **name** : textual description
    - **id** : textual identity 
    - **param** : namedValue dictionnary (external data)

    The methods defined in this class (included inherited) are :

    *constructor (@classmethod))*

    - `Obs.Idic`
    - `Obs.Std`
    - `ES.ilist.Ilist.Iobj`
    - `Obs.from_obj`
    - `ES.ilist.Ilist.from_file`

    *dynamic value (getters @property)*

    - `Obs.bounds`
    - `Obs.jsonFeature`
    - `Obs.setLocation`
    - `Obs.setDatation`
    - `Obs.setProperty`
    - `Obs.setResult`

    *dynamic value inherited (getters @property)*

    - `ES.ilist.Ilist.extidx`
    - `ES.ilist.Ilist.extidxext`
    - `ES.ilist.Ilist.idxname`
    - `ES.ilist.Ilist.idxref`
    - `ES.ilist.Ilist.idxlen`
    - `ES.ilist.Ilist.iidx`
    - `ES.ilist.Ilist.keys`
    - `ES.ilist.Ilist.lenindex`
    - `ES.ilist.Ilist.lenidx`
    - `ES.ilist.Ilist.lidx`
    - `ES.ilist.Ilist.lidxrow`
    - `ES.ilist.Ilist.lvar`
    - `ES.ilist.Ilist.lvarrow`
    - `ES.ilist.Ilist.lname`
    - `ES.ilist.Ilist.lunicname`
    - `ES.ilist.Ilist.lunicrow`
    - `ES.ilist.Ilist.setidx`
    - `ES.ilist.Ilist.tiidx`
    - `ES.ilist.Ilist.textidx`
    - `ES.ilist.Ilist.textidxext`

    *global value (getters @property)*

    - `ES.ilist.Ilist.complete`
    - `ES.ilist.Ilist.consistent`
    - `ES.ilist.Ilist.dimension`
    - `ES.ilist.Ilist.lencomplete`
    - `ES.ilist.Ilist.primary`
    - `ES.ilist.Ilist.zip`

    *selecting - infos methods*

    - `ES.ilist.Ilist.couplingmatrix`
    - `ES.ilist.Ilist.idxrecord`
    - `ES.ilist.Ilist.indexinfos`
    - `ES.ilist.Ilist.indicator`
    - `ES.ilist.Ilist.iscanonorder`
    - `ES.ilist.Ilist.isinrecord`
    - `ES.ilist.Ilist.keytoval`
    - `ES.ilist.Ilist.loc`
    - `ES.ilist.Ilist.nindex`
    - `ES.ilist.Ilist.record`
    - `ES.ilist.Ilist.recidx`
    - `ES.ilist.Ilist.recvar`
    - `ES.ilist.Ilist.valtokey`

    *add - update methods*

    - `ES.ilist.Ilist.add`
    - `ES.ilist.Ilist.addindex`
    - `ES.ilist.Ilist.append`
    - `Obs.appendObs`
    - `ES.ilist.Ilist.delindex`
    - `ES.ilist.Ilist.delrecord`
    - `ES.ilist.Ilist.renameindex`
    - `ES.ilist.Ilist.setvar`
    - `ES.ilist.Ilist.setname`
    - `ES.ilist.Ilist.updateindex`    
    
    *structure management - methods*

    - `ES.ilist.Ilist.applyfilter`
    - `ES.ilist.Ilist.coupling`
    - `ES.ilist.Ilist.full`
    - `ES.ilist.Ilist.getduplicates`
    - `ES.ilist.Ilist.merge`
    - `ES.ilist.Ilist.reindex`
    - `ES.ilist.Ilist.reorder`
    - `ES.ilist.Ilist.setfilter`
    - `ES.ilist.Ilist.sort`
    - `ES.ilist.Ilist.swapindex`
    - `ES.ilist.Ilist.setcanonorder`
    - `ES.ilist.Ilist.tostdcodec`
    
    *exports methods*

    - `Obs.choropleth`
    - `ES.ilist.Ilist.json`
    - `ES.ilist.Ilist.plot`
    - `ES.ilist.Ilist.to_csv`
    - `ES.ilist.Ilist.to_file`
    - `Obs.to_obj`
    - `Obs.to_xarray`
    - `ES.ilist.Ilist.to_dataFrame`
    - `ES.ilist.Ilist.view`
    - `ES.ilist.Ilist.vlist`
    - `ES.ilist.Ilist.voxel`
        
    """

#%% constructor
    def __init__(self, listidx=None, name=None, id=None, param=None, length=None, var=None, reindex=True, 
                 typevalue=ES.def_clsName, context=True):
        '''
        Obs constructor

        *Parameters*

        - **listidx**  : list (default None) - list of compatible Iindex data
        - **typevalue**: str (default ES.def_clsName) - default value class (None or NamedValue)
        - **var**      : int (default None) - row of the variable
        - **length**   : int (default None) - number of records (row)
        - **name**     : string (default None) - Obs name
        - **id**       : string (default None) - Identification string
        - **param**    : dict (default None) - Dict with parameter data or user's data
        - **context** : boolean (default True) - if False, only codec and keys are included
        - **reindex** : boolean (default True) - if True, default codec for each Iindex'''
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

        - **idxdic** : dict (default None) - dict of Iindex element (Iindex name : list of Iindex values)
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
        return cls(listidx=listidx, length=length, name=name, id=None, param=param, 
                   var=0, context=True)

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
        return cls(listidx=Ilist.Iobj(data, reindex=reindex, context=context), 
                   name=name, id=id, param=param, context=context, reindex=reindex)

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
    def __geo_interface__(self):
        '''**dict (@property)** : return the union of Location geometry (see shapely)'''
        codecgeo = self.nindex('location').codec
        if len(codecgeo) == 0: return ""
        if len(codecgeo) == 1: return codecgeo[0].value.__geo_interface__
        else: 
            collec = codecgeo[0].value
            for loc in codecgeo[1:]: collec = collec.union(loc.value)
            return collec.__geo_interface__

    @property
    def jsonFeature(self):
        '''
        **string (@property)** : "FeatureCollection" with Location geometry'''
        if self.setLocation :
            geo = self.__geo_interface__
            if geo['type'] == "MultiPolygon": typ = "Polygon"
            else : typ = "Point"
            lis = list(dict((("type", typ), ("coordinates", geo['coordinates'][i]))) 
                       for i in range(len(geo['coordinates'])))
            fea = list(dict((("type","Feature"), ("id", i), ("geometry", lis[i]))) 
                       for i in range(len(geo['coordinates'])))
            return json.dumps(dict((("type","FeatureCollection"), ("features",fea))), 
                              cls=ESValueEncoder)
        else: return ''
    
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
        Add an `Obs` as a new Result `ES.ESValue` with bounding box for the Index `ES.ESValue`

        *Parameters*

        - **obs** : Obs object
        - **fillvalue** : object value used for default value

        *Returns*

        - **int** : last index in the `Obs`
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

    def choropleth(self, name="choropleth"):
        '''
        Display `Obs` on a folium.Map (only with dimension=1)

        - **name** : String, optionnal (default 'choropleth') - Name of the choropleth

        *Returns* : None'''
        if self.dimension == 1 :
            m = folium.Map(location=self.setLocation[0].coorInv, zoom_start=6)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name=name,
                data=self.to_xarray(numeric=True).to_dataframe(name='obs'),
                key_on="feature.id",
                columns = ['location_row', 'obs'],
                fill_color="OrRd",
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight = 2,
                legend_name="test choropleth"
            ).add_to(m)
            folium.PolyLine(
                util.funclist(self.nindex('location'), LocationValue.vPointInv)
            ).add_to(m)
            folium.LayerControl().add_to(m)
            return m
        return None

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

    def to_xarray(self, info=False, idx=None, fillvalue='?', fillextern=True,
                  lisfunc=None, numeric=False, npdtype=None, **kwargs):
        '''
        Complete the Obs and generate a Xarray DataArray with the dimension define by idx.

        *Parameters*

        - **info** : boolean (default False) - if True, add _dict attributes to attrs Xarray
        - **idx** : list (default none) - list of idx to be completed. If [],
        self.primary is used.
        - **fillvalue** : object (default '?') - value used for the new extval
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **lisfunc** : function (default none) - list of function to apply to indexes before export
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values.
        - **npdtype** : string (default None) - numpy dtype for the DataArray ('object' if None)
        - **kwargs** : parameter for lisfunc

        *Returns* : DataArray '''
        return Ilist.to_xarray(self, info=info, idx=idx, fillvalue=fillvalue, 
                              fillextern=fillextern, lisfunc=lisfunc, name=self.name,
                              numeric=numeric, npdtype=npdtype, attrs=self.param, **kwargs)
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
            if isinstance(v, str) and (v == "null" or v =='')   : ldel.append(k)
            if isinstance(v, list) and v == ES.nullCoor         : ldel.append(k)
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

class ObsError(Exception) :
    pass

