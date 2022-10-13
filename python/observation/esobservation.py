# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: philippe@loco-labs.io

An `Observation` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
 
The `Observation` Object is built around three main bricks :
    
- Ilist Object which deal with indexing,
- ESValue Object which integrate the specificities of environmental data,
- Tools dedicated to particular domains ([Shapely](https://shapely.readthedocs.io/en/stable/manual.html) 
for location, TimeSlot for Datation)

The `observation.esobservation` module contains the `Observation` class.

Documentation is available in other pages :

- The concept of 'observation' is describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Observation).
- The concept of 'indexed list' is describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression test are at 
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_obs.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples/Observation)


"""
import datetime
import json
import folium
import cbor2
from copy import copy

from ilist import Ilist
from iindex import Iindex
from util import util, IindexEncoder, CborDecoder
from esconstante import ES
from esvalue import LocationValue, DatationValue, PropertyValue, ExternValue
from esvalue_base import ESValue, ESValueEncoder


class Observation(Ilist):
    """
    An `Observation` is derived from `observation.Ilist` object.

    *Additional attributes (for @property see methods)* :

    - **name** : textual description
    - **id** : textual identity 
    - **param** : namedValue dictionnary (external data)

    The methods defined in this class (included inherited) are :

    *constructor (@classmethod))*

    - `Observation.Idic`
    - `Observation.Std`
    - `observation.ilist.Ilist.Iobj`
    - `Observation.from_obj`
    - `observation.ilist.Ilist.from_file`

    *dynamic value (getters @property)*

    - `Observation.bounds`
    - `Observation.jsonFeature`
    - `Observation.setLocation`
    - `Observation.setDatation`
    - `Observation.setProperty`
    - `Observation.setResult`

    *dynamic value inherited (getters @property)*

    - `observation.ilist.Ilist.extidx`
    - `observation.ilist.Ilist.extidxext`
    - `observation.ilist.Ilist.idxname`
    - `observation.ilist.Ilist.idxref`
    - `observation.ilist.Ilist.idxlen`
    - `observation.ilist.Ilist.iidx`
    - `observation.ilist.Ilist.keys`
    - `observation.ilist.Ilist.lenindex`
    - `observation.ilist.Ilist.lenidx`
    - `observation.ilist.Ilist.lidx`
    - `observation.ilist.Ilist.lidxrow`
    - `observation.ilist.Ilist.lvar`
    - `observation.ilist.Ilist.lvarrow`
    - `observation.ilist.Ilist.lname`
    - `observation.ilist.Ilist.lunicname`
    - `observation.ilist.Ilist.lunicrow`
    - `observation.ilist.Ilist.setidx`
    - `observation.ilist.Ilist.tiidx`
    - `observation.ilist.Ilist.textidx`
    - `observation.ilist.Ilist.textidxext`

    *global value (getters @property)*

    - `observation.ilist.Ilist.complete`
    - `observation.ilist.Ilist.consistent`
    - `observation.ilist.Ilist.dimension`
    - `observation.ilist.Ilist.lencomplete`
    - `observation.ilist.Ilist.primary`
    - `observation.ilist.Ilist.zip`

    *selecting - infos methods*

    - `observation.ilist.Ilist.couplingmatrix`
    - `observation.ilist.Ilist.idxrecord`
    - `observation.ilist.Ilist.indexinfos`
    - `observation.ilist.Ilist.indicator`
    - `observation.ilist.Ilist.iscanonorder`
    - `observation.ilist.Ilist.isinrecord`
    - `observation.ilist.Ilist.keytoval`
    - `observation.ilist.Ilist.loc`
    - `observation.ilist.Ilist.nindex`
    - `observation.ilist.Ilist.record`
    - `observation.ilist.Ilist.recidx`
    - `observation.ilist.Ilist.recvar`
    - `observation.ilist.Ilist.valtokey`

    *add - update methods*

    - `observation.ilist.Ilist.add`
    - `observation.ilist.Ilist.addindex`
    - `observation.ilist.Ilist.append`
    - `Observation.appendObs`
    - `observation.ilist.Ilist.delindex`
    - `observation.ilist.Ilist.delrecord`
    - `observation.ilist.Ilist.renameindex`
    - `observation.ilist.Ilist.setvar`
    - `observation.ilist.Ilist.setname`
    - `observation.ilist.Ilist.updateindex`    

    *structure management - methods*

    - `observation.ilist.Ilist.applyfilter`
    - `observation.ilist.Ilist.coupling`
    - `observation.ilist.Ilist.full`
    - `observation.ilist.Ilist.getduplicates`
    - `observation.ilist.Ilist.merge`
    - `observation.ilist.Ilist.reindex`
    - `observation.ilist.Ilist.reorder`
    - `observation.ilist.Ilist.setfilter`
    - `observation.ilist.Ilist.sort`
    - `observation.ilist.Ilist.swapindex`
    - `observation.ilist.Ilist.setcanonorder`
    - `observation.ilist.Ilist.tostdcodec`

    *exports methods*

    - `Observation.choropleth`
    - `observation.ilist.Ilist.json`
    - `observation.ilist.Ilist.plot`
    - `observation.ilist.Ilist.to_csv`
    - `observation.ilist.Ilist.to_file`
    - `Observation.to_obj`
    - `Observation.to_xarray`
    - `observation.ilist.Ilist.to_dataframe`
    - `observation.ilist.Ilist.view`
    - `observation.ilist.Ilist.vlist`
    - `observation.ilist.Ilist.voxel`

    """

# %% constructor
    def __init__(self, listidx=None, name=None, id=None, param=None, length=None, var=None, reindex=True,
                 typevalue=ES.def_clsName, context=True):
        '''
        Observation constructor

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
        if isinstance(listidx, Observation):
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.lvarname = [name for name in listidx.lvarname]
            if not listidx.param is None:
                self.param = {k: v for k, v in listidx.param.items()}
            else:
                self.param = param
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
        if not listidx:
            Ilist.__init__(self)
        else:
            for i, idx in enumerate(listidx):
                if isinstance(idx, list) and len(idx) > 1 and idx[0]==ES.res_classES:
                    var=i
                    break
            Ilist.__init__(self, listidx=listidx, length=length, var=var,
                           reindex=reindex, typevalue=typevalue, context=context)
        #if ES.res_classES in self.lname:
        #    self.lvarname = [ES.res_classES]
        self.name = name
        self.id = id
        self.param = param

    @classmethod
    def Idic(cls, idxdic=None, typevalue=ES.def_clsName, name=None, id=None, param=None, var=None):
        '''
        Observation constructor (external dictionnary).

        *Parameters*

        - **idxdic** : dict (default None) - dict of Iindex element (Iindex name : list of Iindex values)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **fullcodec** : boolean (default False) - full codec if True
        - **var** :  int (default None) - row of the variable
        - **name**     : string (default None) - Observation name
        - **id**       : string (default None) - Identification string
        - **param**    : dict (default None) - Dict with parameter data or user's data'''
        if ES.res_classES in idxdic:
            var = list(idxdic.keys()).index(ES.res_classES)
        listidx = Ilist.Idic(idxdic, typevalue=typevalue, var=var)
        return cls(listidx=listidx, name=name, id=id, param=param, context=True)

    @classmethod
    def Std(cls, result=None, datation=None, location=None, property=None,
            name=None, id=None, param=None):
        '''
        Generate an Observation Object with standard indexes

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
            listidx.append([ES.res_classES, []])
            length = 0
        else:
            listidx.append(Iindex.Iext(result, ES.res_classES))
        if datation is None:
            listidx.append([ES.dat_classES, []])
        else:
            listidx.append(Iindex.Iext(datation, ES.dat_classES))
        if location is None:
            listidx.append([ES.loc_classES, []])
        else:
            listidx.append(Iindex.Iext(location, ES.loc_classES))
        if property is None:
            listidx.append([ES.prp_classES, []])
        else:
            listidx.append(Iindex.Iext(property, ES.prp_classES))
        return cls(listidx=listidx, length=length, name=name, id=None, param=param,
                   var=0, context=True)

    @classmethod
    def from_obj(cls, bs=None, reindex=True, context=True):
        '''
        Generate an Observation Object from a bytes, string or dic value

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        if not bs:
            bs = []
        if isinstance(bs, bytes):
            dic = cbor2.loads(bs)
        elif isinstance(bs, str):
            dic = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, dict):
            dic = bs
        else:
            raise ObsError("the type of parameter is not available")
        if ES.id in dic:
            id = dic[ES.id]
        else:
            id = None
        if id and not isinstance(id, str):
            raise ObsError('id is not a str')
        if ES.param in dic:
            param = dic[ES.param]
        else:
            param = None
        if param and not isinstance(param, dict):
            raise ObsError('param is not a dict')
        if ES.name in dic:
            name = dic[ES.name]
        else:
            name = None
        if name and not isinstance(name, str):
            raise ObsError('name is not a str')
        if ES.data in dic:
            data = dic[ES.data]
        else:
            data = None
        if data and not isinstance(data, list):
            raise ObsError('data is not a list')
        return cls(listidx=Ilist.Iobj(data, reindex=reindex, context=context),
                   name=name, id=id, param=param, context=context, reindex=reindex)

# %% special
    def __copy__(self):
        ''' Copy all the data '''
        return Observation(self)

    def __str__(self):
        '''return string format for var and lidx'''
        if self.name:
            stro = ES.name + ': ' + self.name + '\n'
        else:
            stro = ''
        if self.id:
            stro += ES.id + ': ' + self.id + '\n'
        stri = Ilist.__str__(self)
        if not stri == '':
            stro += ES.data + ':\n' + stri
        for idx in self.lidx:
            stri += str(idx)
        if self.param:
            stro += ES.param + ':\n    ' + json.dumps(self.param) + '\n'
        return stro

    def __eq__(self, other):
        ''' equal if all attribut and Ilist are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and self.name == other.name \
            and self.id == other.id and self.param == other.param  \
            and Ilist.__eq__(self, other)

    def __hash__(self):
        '''return sum of all hash(Iindex)'''
        return hash(self.param) + hash(self.id) + hash(self.name) + Ilist.__hash__(self)

# %% properties
    @property
    def bounds(self):
        '''
        **list of `observation.esvalue` (@property)** : `observation.esvalue` bounding box for each axis.'''
        bound = [None, None, None]
        if self.setDatation:
            bound[0] = ESValue.boundingBox(self.setDatation).bounds
        if self.setLocation:
            bound[1] = ESValue.boundingBox(self.setLocation).bounds
        if self.setProperty:
            bound[2] = ESValue.boundingBox(self.setProperty).bounds
        return bound

    @property
    def __geo_interface__(self):
        '''**dict (@property)** : return the union of Location geometry (see shapely)'''
        codecgeo = self.nindex('location').codec
        if len(codecgeo) == 0:
            return ""
        if len(codecgeo) == 1:
            return codecgeo[0].value.__geo_interface__
        else:
            collec = codecgeo[0].value
            for loc in codecgeo[1:]:
                collec = collec.union(loc.value)
            return collec.__geo_interface__

    @property
    def jsonFeature(self):
        '''
        **string (@property)** : "FeatureCollection" with Location geometry'''
        if self.setLocation:
            geo = self.__geo_interface__
            if geo['type'] == "MultiPolygon":
                typ = "Polygon"
            else:
                typ = "Point"
            lis = list(dict((("type", typ), ("coordinates", geo['coordinates'][i])))
                       for i in range(len(geo['coordinates'])))
            fea = list(dict((("type", "Feature"), ("id", i), ("geometry", lis[i])))
                       for i in range(len(geo['coordinates'])))
            return json.dumps(dict((("type", "FeatureCollection"), ("features", fea))),
                              cls=ESValueEncoder)
        else:
            return ''

    @property
    def setDatation(self):
        '''**list (@property)** : list of codec values in the datation index'''
        if self.nindex(ES.dat_classES):
            return self.nindex(ES.dat_classES).codec
        return None

    @property
    def setLocation(self):
        '''**list (@property)** : list of codec values in the location index'''
        if self.nindex(ES.loc_classES):
            return self.nindex(ES.loc_classES).codec
        return None

    @property
    def setProperty(self):
        '''**list (@property)** : list of codec values in the property index'''
        if self.nindex(ES.prp_classES):
            return self.nindex(ES.prp_classES).codec
        return None

    @property
    def setResult(self):
        '''
        **list (@property)** : list of codec values in the result index'''
        if self.nindex(ES.res_classES):
            return self.nindex(ES.res_classES).codec
        return None

# %% methods
    def appendObs(self, obs, unique=False, fillvalue='-'):
        '''
        Add an `Observation` as a new Result `observation.esvalue` with bounding box for the Index `observation.esvalue`

        *Parameters*

        - **obs** : Observation object
        - **fillvalue** : object value used for default value

        *Returns*

        - **int** : last index in the `Observation`
        '''
        record = [fillvalue] * len(self.lname)
        if ES.dat_classES in self.lname:
            record[self.lname.index(ES.dat_classES)
                   ] = DatationValue.Box(obs.bounds[0])
        if ES.loc_classES in self.lname:
            record[self.lname.index(ES.loc_classES)
                   ] = LocationValue.Box(obs.bounds[1])
        if ES.prp_classES in self.lname:
            record[self.lname.index(ES.prp_classES)
                   ] = PropertyValue.Box(obs.bounds[2])
        if ES.res_classES in self.lname:
            record[self.lname.index(ES.res_classES)] = ExternValue(obs)
        return self.append(record, unique=unique)

    def choropleth(self, name="choropleth"):
        '''
        Display `Observation` on a folium.Map (only with dimension=1)

        - **name** : String, optionnal (default 'choropleth') - Name of the choropleth

        *Returns* : None'''
        if self.dimension == 1:
            m = folium.Map(location=self.setLocation[0].coorInv, zoom_start=6)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name=name,
                data=self.to_xarray(numeric=True).to_dataframe(name='obs'),
                key_on="feature.id",
                columns=['location_row', 'obs'],
                fill_color="OrRd",
                fill_opacity=0.7,
                line_opacity=0.4,
                line_weight=2,
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
        dic = {ES.type: ES.obs_classES}
        if self.id:
            dic[ES.obs_id] = self.id
        if self.name:
            dic[ES.obs_name] = self.name
        if self.param:
            dic[ES.obs_param] = self.param
        dic[ES.obs_data] = Ilist.to_obj(self, **option2)
        if option["json_param"] and self.param:
            dic[ES.obs_param] = self.param
        dic |= self._info(**option)
        if option['codif'] and option['encode_format'] != 'cbor':
            js2 = {}
            for k, v in dic.items():
                if k in option['codif']:
                    js2[option['codif'][k]] = v
                else:
                    js2[k] = v
        else:
            js2 = dic
        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(js2, cls=IindexEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor':
            return cbor2.dumps(js2, datetime_as_timestamp=True,
                               timezone=datetime.timezone.utc, canonical=True)
        return dic

    def to_xarray(self, info=False, idx=None, fillvalue='?', fillextern=True,
                  lisfunc=None, numeric=False, npdtype=None, **kwargs):
        '''
        Complete the Observation and generate a Xarray DataArray with the dimension define by idx.

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
# %% internal

    def _info(self, **kwargs):
        ''' Create json dict with info datas'''
        option = ES.mOption | kwargs
        dcinf = dict()
        if option["json_info"] or option["json_info_nval"]:
            dcinf |= dict(
                zip(['len-'+name for name in self.lname], self.indexlen))
        if option["json_info"] or option["json_info_box"]:
            dcinf |= self._infoBox(**option)
        if option["json_info"] or option["json_info_other"]:
            dcinf |= self._infoOther()
        ldel = []
        for k, v in dcinf.items():
            if isinstance(v, str) and (v == "null" or v == ''):
                ldel.append(k)
            if isinstance(v, list) and v == ES.nullCoor:
                ldel.append(k)
        for k in ldel:
            del dcinf[k]
        if len(dcinf) == 0:
            return ""
        return {ES.information: dcinf}

    def _infoBox(self, **option):
        ''' Add box informations's key-value to dict dcinf'''
        dcinf = dict()
        if self.setLocation:
            dcinf[ES.loc_box] = list(
                ESValue.boundingBox(self.setLocation).bounds)
            dcinf[ES.geo_box] = ESValue.boundingBox(
                self.setLocation).__geo_interface__
        if self.setProperty:
            dcinf[ES.prp_box] = list(
                ESValue.boundingBox(self.setProperty).bounds)
        if self.setDatation:
            bound = ESValue.boundingBox(self.setDatation).bounds
            if option["encode_format"] == 'json':
                dcinf[ES.dat_box] = list(bound)
            else:
                dcinf[ES.dat_box] = [datetime.datetime.fromisoformat(bound[0]),
                                     datetime.datetime.fromisoformat(bound[1])]
        return dcinf

    def _infoOther(self):
        ''' Add other's information key-value to dict dcinf'''
        dcinf = dict()
        dcinf[ES.obs_complet] = self.complete
        #dcinf[ES.obs_score]   = self.score
        #dcinf[ES.res_mRate]   = self.rate
        dcinf[ES.res_dim] = self.dimension
        dcinf[ES.res_axes] = [self.idxname[i] for i in self.primary]
        return dcinf


class ObsError(Exception):
    pass
