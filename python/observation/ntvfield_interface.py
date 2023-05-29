# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `python.observation.ntvfield_interface` module contains the `NtvfieldInterface` class
(`python.observation.ntvfield.Ntvfield` methods).
"""
# %% declarations
import json
import datetime
import numpy as np
import pandas as pd
import cbor2

from observation.esconstante import ES
from observation.esvalue_base import ESValueEncoder
from observation.util import util, identity
from json_ntv.ntv import Ntv, NtvSingle, NtvList


class CborDecoder(json.JSONDecoder):
    ''' Cbor extension for integer keys (codification keys)'''

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.codecbor)

    def codecbor(self, dic):
        dic2 = {}
        for k, v in dic.items():
            try:
                k2 = int(k)
            except:
                k2 = k
            dic2[k2] = v
        return dic2


class NtvfieldError(Exception):
    ''' Ntvfield Exception'''
    # pass


class NtvfieldEncoder(json.JSONEncoder):
    """new json encoder for Ntvfield and Ntvdataset"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        option = {'encoded': False, 'encode_format': 'json'}
        if o.__class__.__name__ in ('Ntvdataset', 'TimeSlot', 'Ndataset', 'Sdataset'):
            return o.json(**option)
        #if issubclass(o.__class__, ESValue):
        #    return o.json(**option)
        try:
            return o.to_json(**option)
        except:
            try:
                return o.__to_json__()
            except:
                return json.JSONEncoder.default(self, o)


class NtvfieldInterface:
    '''this class includes Ntvfield methods :

    - `NtvfieldInterface.json`
    - `NtvfieldInterface.to_obj`
    - `NtvfieldInterface.to_dict_obj`
    - `NtvfieldInterface.to_numpy`
    - `NtvfieldInterface.to_pandas`
    - `NtvfieldInterface.vlist`
    - `NtvfieldInterface.vName`
    - `NtvfieldInterface.vSimple`
    '''

    """@staticmethod
    def decodetype(decobj, lenparent=None):
        '''Return the Ntvfield type of a decoded json value

        *Parameters*

        - **decobj** : tuple with decoding data (see decodeobj method)
        - **lenparent** : integer(default None) - parent length to compare to decoded codec length

        *Returns* 

        - **string** : name of the Ntvfield type'''
        codec, parent, keys = decobj[2:5]

        if parent < 0 and not keys:
            if len(codec) == 1:
                return 'unique'
            if lenparent and len(codec) == lenparent:
                return 'root coupled'
            if not lenparent:
                raise NtvfieldError(
                    "lenparent is necessary to define the format")
            return 'primary'
        if parent >= 0 and not keys:
            if lenparent and len(codec) == lenparent:
                return 'coupled'
            if not lenparent:
                raise NtvfieldError(
                    "lenparent is necessary to define the format")
            return 'periodic derived'
        if len(keys) == lenparent and len(codec) < lenparent and parent < 0:
            return 'root derived'
        if len(keys) < lenparent and parent >= 0 and len(codec) < lenparent:
            return 'derived'
        raise NtvfieldError("data are inconsistenty to define the format")
        return"""

    """@staticmethod
    def decodeobj(bs=None, classname=None, context=True):
        '''Generate a tuple data from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **classname** : string(default None) - classname to convert codec data
        - **context** : boolean (default True) - if False, only codec and keys are included

        *Returns* 

        - **tuple** : name, dtype, codec, parent, keys, isfullindex, isparent
            name (None or string): name of the Ntvfield
            dtype (None or string): type of data
            codec (list): lilst of Ntvfield codec values
            parent (int): Ntvfield parent or ES.nullparent
            keys (None or list): Ntvfield keys
            isfullindex (boolean): True if Ntvfield is full (len(keys) = len(self))
            isparent(boolean): True if parent is >= 0
            '''
        if bs is None:
            #return (None, None, [], ES.nullparent, None, False, False, False)
            return (None, None, [], ES.nullparent, None, False, False)
        if isinstance(bs, bytes):
            lis = cbor2.loads(bs)
        elif isinstance(bs, str) and bs[0] in ['{', '[', '"']:
            lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list):
            lis = bs
        else:
            lis = [bs]
        if not isinstance(lis, list):
            lis = [lis]

        if not lis:  # format empty
            return (None, None, [], ES.nullparent, None, False, False)
        if context and (not isinstance(lis[0], (str, dict, list)) or len(lis) > 3):
            return (None, None, NtvfieldInterface.decodecodec(lis, classname),
                    ES.nullparent, None, False, False)
        if not context and len(lis) > 2:
            return (None, None, NtvfieldInterface.decodecodec(lis, classname),
                    ES.nullparent, None, False, False)
        if len(lis) == 3 and isinstance(lis[0], (str, dict)) and isinstance(lis[1], list) \
                and isinstance(lis[2], (list, int)) and context:
            return (*NtvfieldInterface.decodecontext(lis[0]),
                    NtvfieldInterface.decodecodec(lis[1], classname),
                    *NtvfieldInterface.decodekeys(lis[2]))
        if len(lis) == 2 and isinstance(lis[0], (str, dict)) and isinstance(lis[1], list) \
                and context:
            return (*NtvfieldInterface.decodecontext(lis[0]),
                    NtvfieldInterface.decodecodec(
                        lis[1], classname), ES.nullparent, None, False, False)
        if len(lis) == 2 and isinstance(lis[0], (tuple, list)) \
                and NtvfieldInterface.iskeysobj(lis[1]):
            return (None, None, NtvfieldInterface.decodecodec(lis[0], classname),
                    *NtvfieldInterface.decodekeys(lis[1]))
        return (None, None, NtvfieldInterface.decodecodec(lis, classname), ES.nullparent,
                None, False, False)"""

    """@staticmethod
    def decodecodec(codecobj, classname=ES.nam_clsName):
        '''Generate a codec list from a json value'''
        return [ESValue.from_obj(val, classname=classname) for val in codecobj]

    @staticmethod
    def decodecontext(context):
        '''Generate a tuple (name, dtype) from a json value'''
        if isinstance(context, dict) and len(context) == 1:
            name, dtype = list(context.items())[0][0]
            if isinstance(name, str) and isinstance(dtype, str) and dtype in ES.typeName.keys():
                return (name, ES.typeName[dtype])
            raise NtvfieldError('name or typevalue is unconsistent')
        if context in ES.typeName.keys():
            return (context, ES.typeName[context])
        if isinstance(context, str):
            return (context, None)
        raise NtvfieldError('name or typevalue is unconsistent')

    @staticmethod
    def decodekeys(keys):
        '''Generate a tuple (parent, keys, isfullindex, isparent, isvar) from a json value'''
        if isinstance(keys, int):
            keys = [keys]
        if isinstance(keys, list) and len(keys) == 0:
            return (ES.notcrossed, keys, False, False)
        if isinstance(keys, list) and len(keys) == 1 and isinstance(keys[0], int)\
                and keys[0] < 0:
            return (keys[0], None, False, False)
        if isinstance(keys, list) and len(keys) == 1 and isinstance(keys[0], int)\
                and keys[0] >= 0:
            return (keys[0], None, False, True)
        if isinstance(keys, list) and len(keys) == 2 and isinstance(keys[0], int)\
                and isinstance(keys[1], list) and keys[0] < 0:
            return (keys[0], keys[1], True, False)
        if isinstance(keys, list) and len(keys) == 2 and isinstance(keys[0], int)\
                and isinstance(keys[1], list) and keys[0] >= 0:
            return (keys[0], keys[1], False, True)
        if isinstance(keys, list) and len(keys) > 1:
            return (ES.notcrossed, keys, True, False)
        raise NtvfieldError('parent or keys is unconsistent')"""

    @classmethod 
    def decode_ntv(cls, field, encode_format='json'):
        '''Generate a tuple data from a Ntv value(bytes, string, json, Ntv object)

        *Parameters*

        - **field** : bytes, string json or Ntv object to convert
        - **encode_format** : string (default 'json') - format to convert ntv_value

        *Returns* 

        - **tuple** : name, dtype, codec, parent, keys, coef, leng
            name (None or string): name of the Ntvfield
            dtype (None or string): type of data
            codec (list): list of Ntvfield codec values
            parent (None or int): Ntvfield parent or None
            keys (None or list): Ntvfield keys
            coef (None or int): coef if primary Ntvfield else None
            leng (int): length of the Ntvfield
        '''
        if field is None:
            return (None, None, [], ES.nullparent, None, None, 0)
        if isinstance(field, bytes):
            lis = cbor2.loads(field)
        elif isinstance(field, str) and field[0] in ['{', '[', '"']:
            lis = json.loads(field) 
        else:
            lis = field

        ntv = Ntv.obj(lis)
        typ = ntv.type_str if ntv.ntv_type else None
        nam = ntv.name
        val = ntv.val
        if isinstance(ntv, NtvSingle):
            #return (nam, typ, [Ntv.from_obj(val)], None, None, None, 1)
            return (nam, typ, [cls.s_to_i(val)], None, None, None, 1)
        if len(ntv) == 0:
            #return (nam, typ, val, None, None, None, 0)
            return (nam, typ, cls.n_to_i(val), None, None, None, 0)
        if len(ntv) > 3 or isinstance(ntv[0], NtvSingle):
            #return (nam, typ, val, None, None, None, len(ntv))
            return (nam, typ, cls.n_to_i(val), None, None, None, len(ntv))
        if len(ntv) == 1:
            #return (nam, typ, [Ntv.from_obj(val)[0]], None, None, None, 1)
            return (nam, typ, [cls.s_to_i(val)[0]], None, None, None, 1)

        ntvc = ntv[0]
        leng = max(len(ind) for ind in ntv)
        typc = ntvc.type_str if ntvc.ntv_type else None
        valc = ntvc.val
        if len(ntv) == 3 and isinstance(ntv[1], NtvSingle) and \
            isinstance(ntv[1].val, (int, str)) and not isinstance(ntv[2], NtvSingle) and \
            isinstance(ntv[2][0].val, int):
            #return (nam, typc, valc, ntv[1].val, ntv[2].to_obj(), None, leng)
            return (nam, typc, cls.n_to_i(valc), ntv[1].val, ntv[2].to_obj(), None, leng)
        if len(ntv) == 2 and len(ntv[1]) == 1 and \
            isinstance(ntv[1].val, (int, str)):
            #return (nam, typc, valc, ntv[1].val, None, None, leng) 
            return (nam, typc, cls.n_to_i(valc), ntv[1].val, None, None, leng) 
        if len(ntv) == 2 and len(ntv[1]) == 1 and isinstance(ntv[1].val, list):
            leng = leng * ntv[1][0].val
            #return (nam, typc, valc, None, None, ntv[1][0].val, leng) 
            return (nam, typc, cls.n_to_i(valc), None, None, ntv[1][0].val, leng) 
        if len(ntv) == 2 and len(ntv[1]) > 1  and isinstance(ntv[1][0].val, int):
            #return (nam, typc, valc, None, ntv[1].to_obj(), None, leng)
            return (nam, typc, cls.n_to_i(valc), None, ntv[1].to_obj(), None, leng)
        return (nam, typ, val, None, None, None, len(ntv))

    @staticmethod 
    def encodecoef(lis):
        '''Generate a repetition coefficient for periodic list'''
        if len(lis) < 2:
            return 0
        coef = 0
        period = max(lis) + 1
        for i in range(1,len(lis)):
            coef = i
            if lis[i-1] != lis[i]:
                break
        periodic_lis = [ (ikey % (coef * period)) // coef for ikey in range(len(lis))]
        if lis == periodic_lis:
            return coef
        return 0
    
    """@staticmethod
    def encodeobj(codeclist, keyslist=None, name=None, simpleval=False,
                  codecval=False, typevalue=None, parent=ES.nullparent,
                  listunic=False, modecodec='optimize', **kwargs):
        '''
        Return a formatted object with values, keys and codec.
        - Format can be json, bson or cbor
        - object can be string, bytes or dict

        *Parameters*
        - **modecodec** : string (default 'optimize') - json mode
        - **codeclist** : list of codec ESValue to encode
        - **keyslist** : list (default = None) - int keys to encode, None if no keys
        - **name** : string (default = None) - name to encode, None if no name
        - **typevalue** : string (default None) - type to convert values
        - **parent** : int (default ES.nullparent) - Ntvdataset index linked to
        - **listunic** : boolean (default False) - if False, when len(result)=1 return value not list
        - **codecval** : boolean (default False) - if True, only list of codec values is included
        - **simpleval** : boolean (default False) - if True, only value (without name) is included

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **untyped** : boolean (default False) - include dtype in the json if True
        - **geojson** : boolean (default False) - geojson for LocationValue if True

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'untyped': False,
                  'codif': {}, 'typevalue': typevalue, 'geojson': False} | kwargs
        js = []
        if not codecval:
            if name and typevalue:
                js.append({name: typevalue})
            elif name:
                js.append(name)
            elif typevalue:
                js.append(typevalue)
        codlis = [util.json(cc, encoded=False, typevalue=None, simpleval=simpleval,
                            modecodec=modecodec, untyped=option['untyped'],
                            geojson=option['geojson']) for cc in codeclist]
        js.append(codlis)
        if not codecval:
            if parent >= 0 and keyslist:
                js.append([parent, keyslist])
            elif parent != ES.nullparent:
                js.append(parent)
            elif keyslist:
                js.append(keyslist)
        if len(js) == 1:
            js = js[0]
        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(js, cls=NtvfieldEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor':
            return cbor2.dumps(js, datetime_as_timestamp=True,
                               timezone=datetime.timezone.utc, canonical=True)
        return js"""

    """@staticmethod
    def iskeysobj(obj):
        if isinstance(obj, int):
            return True
        if not isinstance(obj, list):
            return False
        if len(obj) == 0:
            return True
        if not isinstance(obj[0], int):
            return False
        if len(obj) == 1:
            return True
        if len(obj) > 2 and not isinstance(obj[1], int):
            return False
        if len(obj) == 2 and isinstance(obj[1], int):
            return True
        if len(obj) == 2 and isinstance(obj[1], list):
            obj = obj[1]
        if not isinstance(obj, list):
            return False
        for i in range(len(obj)):
            if not isinstance(obj[i], int):
                return False
        return True"""

    def json(self, keys=None, typevalue=None, modecodec='optimize', simpleval=False,
             codecval=False, parent=ES.nullparent, **kwargs):
        '''Return a formatted object (string, bytes or dict) for the Ntvfield

        *Parameters*

        - **keys** : list (default None) - list: List of keys to include - None:
        no list - else: Ntvfield keys
        - **typevalue** : string (default None) - type to convert values
        - **modecodec** : string (default 'optimize') - json mode
        - **simpleval** : boolean (default False) - if True, only codec is included
        - **parent** : integer (default None) - index number of the parent in indexset

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **untyped** : boolean (default True) - include dtype in the json if True

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'untyped': True,
                  'codif': {}} | kwargs
        return self.to_obj(keys=keys, typevalue=typevalue, modecodec=modecodec,
                           codecval=codecval, simpleval=simpleval, parent=parent,
                           **option)

    def to_dict_obj(self, typevalue=None, simpleval=False, modecodec='optimize', **kwargs):
        option = {'encoded': False, 'encode_format': 'json', 'untyped': False,
                  'codif': {}, 'geojson': False} | kwargs
        dic = {}
        if self.typevalue:
            dic['type'] = self.typevalue
        ds = pd.Series(range(len(self.keys)), index=self.keys, dtype='int64')
        dic['value'] = [{'record': ds[i].tolist(),
                         'codec': util.json(cod, encoded=False, typevalue=None,
                                            simpleval=simpleval, modecodec=modecodec,
                                            untyped=option['untyped'], datetime=False,
                                            geojson=option['geojson'])}
                        for i, cod in enumerate(self.codec)]
        return {self.name: dic}

    def to_numpy(self, func=None, codec=False, npdtype=None, **kwargs):
        '''
        Transform Ntvfield in a Numpy array.

        *Parameters*

        - **func** : function (default None) - function to apply for each value of the Ntvfield.
        If func is the 'index' string, values are replaced by raw values.
        - **npdtype** : string (default None) - numpy dtype for the Array ('object' if None)
        - **kwargs** : parameters to apply to the func function

        *Returns* : Numpy Array'''
        return self.to_pandas(func=func, codec=codec, npdtype=npdtype, numpy=True, **kwargs)

    def to_ntv(self, modecodec='optimize', codecval=False, def_type=None, keys=None, parent=None, name=True):
        '''Return a Ntv field value

        *Parameters (kwargs)*

        - **modecodec** : string (default 'optimize') - if 'full', index is with a full codec
        if 'default' index has keys, if 'optimize' keys are optimized, 
        - **codecval** : boolean (default False) - if True, only list of codec values is included
        - **def_type** : string (default 'json') - default ntv_type for NtvList or NtvSet
        - **name** : boolean (default False) - if False, default index name are not included
        - **keys** : list (default None) - used only with 'optimize' mode
        - **parent** : int or str (default None) - used only with 'optimize' mode

        *Returns* : Ntv object'''
        leng = len(self)
        codec = self.i_to_n(self.codec)
        idxname = None if self.name == '$default' or not name else self.name       
        '''if len(self.codec) == 1:
            return NtvSingle(self.codec[0].ntv_value, idxname, self.codec[0].ntv_type)
        if codecval:
            return NtvList(self.codec, idxname, ntv_type=def_type)
        if len(self.codec) == leng or modecodec == 'full':
            return NtvList(self.values, idxname, ntv_type=def_type)
        if modecodec == 'default':
            return NtvList([NtvList(self.codec, ntv_type=def_type), 
                            NtvList(self.keys, ntv_type='json')], idxname, ntv_type='json')
        if modecodec == 'optimize':
            ntv_value = [NtvList(self.codec, ntv_type=def_type)]'''
        if len(codec) == 1:
            return NtvSingle(codec[0].ntv_value, idxname, codec[0].ntv_type)
        if codecval:
            return NtvList(codec, idxname, ntv_type=def_type)
        if len(codec) == leng or modecodec == 'full':
            return NtvList(self.values, idxname, ntv_type=def_type)
        if modecodec == 'default':
            return NtvList([NtvList(codec, ntv_type=def_type), 
                            NtvList(self.keys, ntv_type='json')], idxname, ntv_type='json')
        if modecodec == 'optimize':
            ntv_value = [NtvList(codec, ntv_type=def_type)]
            if not parent is None:
                ntv_value.append(NtvSingle(parent, ntv_type='json'))
            if keys:
                ntv_value.append(NtvList(keys, ntv_type='json'))    
            elif parent is None:
                ntv_value.append(NtvList(self.keys, ntv_type='json'))
            return NtvList(ntv_value, idxname, ntv_type='json')                

    """def to_obj(self, keys=None, typevalue=None, simpleval=False, modecodec='optimize',
               codecval=False, parent=ES.nullparent, name=True, listunic=False,
               **kwargs):
        '''Return a formatted object (string, bytes or dict) for the Ntvfield

        *Parameters*

        - **modecodec** : string (default 'optimize') - json mode
        - **keys** : list (default None) - list: List of keys to include - None or False:
        no list - else: Ntvfield keys
        - **typevalue** : string (default None) - type to convert values
        - **name** : boolean (default True) - if False, name is not included
        - **codecval** : boolean (default False) - if True, only list of codec values is included
        - **simpleval** : boolean (default False) - if True, only value (without name) is included
        - **listunic** : boolean (default False) - if False, when len(result)=1
        return value not list
        - **parent** : integer (default None) - index number of the parent in indexset

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **untyped** : boolean (default False) - include dtype if True
        - **geojson** : boolean (default False) - geojson for LocationValue if True

        *Returns* : string, bytes or dict'''
        keyslist = None
        if not name or self.name == ES.defaultindex:
            idxname = None
        else:
            idxname = self.name
        if modecodec == 'full':
            codeclist = self.values
            keyslist = None
        elif modecodec == 'default':
            codeclist = self._codec
            keyslist = self._keys
        else:
            codeclist = self._codec
            if keys and isinstance(keys, list):
                keyslist = keys
            elif keys and not isinstance(keys, list):
                keyslist = self._keys
        if typevalue:
            dtype = ES.valname[typevalue]
        else:
            dtype = None
        return NtvfieldInterface.encodeobj(codeclist, keyslist, idxname, simpleval,
                                         codecval, dtype, parent, listunic,
                                         modecodec, **kwargs)"""

    def to_pandas(self, func=None, codec=False, npdtype=None,
                  series=True, index=True, numpy=False, **kwargs):
        '''
        Transform Ntvfield in a Pandas Series, Pandas DataFrame or Numpy array.

        *Parameters*

        - **func** : function (default None) - function to apply for each value of the Ntvfield.
        If func is the 'index' string, values are replaced by raw values.
        - **npdtype** : string (default None) - numpy dtype for the Array ('object' if None)
        - **series** : boolean (default True) - if True, return a Series. 
        If False return a DataFrame
        - **index** : boolean (default True) - if True, index is keys.
        - **numpy** : boolean (default False) - if True, return a Numpy array.
        - **kwargs** : parameters to apply to the func function

        *Returns* : Pandas Series, Pandas DataFrame, Numpy Array'''
        if len(self) == 0:
            raise NtvfieldError("Ntvdataset is empty")
        if npdtype:
            npdtype = np.dtype(npdtype)
        else:
            npdtype = 'object'
        if func is None:
            func = identity
        if func == 'index':
            return np.array(list(range(len(self))))
        if not codec:
            values = util.funclist(self.values, func, **kwargs)
        else:
            values = util.funclist(self._codec, func, **kwargs)
        npdtype1 = npdtype
        if isinstance(values[0], (datetime.datetime)):
            npdtype1 = np.datetime64
        # else:
        #    npdtype=None
        pdindex = None
        if index:
            pdindex = self._keys
        try:
            if numpy:
                return np.array(values, dtype=npdtype1)
            if series:
                return pd.Series(values, dtype=npdtype1,
                                 index=pdindex, name=self.name)
            return pd.DataFrame(pd.Series(values, dtype=npdtype1,
                                          index=pdindex, name=self.name))
        except:
            if numpy:
                return np.array(values, dtype=npdtype)
            if series:
                return pd.Series(values, dtype=npdtype,
                                 index=pdindex, name=self.name)
            return pd.DataFrame(pd.Series(values, dtype=npdtype,
                                          index=pdindex, name=self.name))

    def vlist(self, func, *args, extern=True, **kwargs):
        '''
        Apply a function to values and return the result.

        *Parameters*

        - **func** : function - function to apply to values
        - **args, kwargs** : parameters for the function
        - **extern** : if True, the function is apply to external values, else internal

        *Returns* : list of func result'''
        if extern:
            return util.funclist(self.val, func, *args, **kwargs)
        return util.funclist(self.values, func, *args, **kwargs)

    def vName(self, default=ES.nullName, maxlen=None):
        '''
        Return the list of name for ESValue data .

        *Parameters*

        - **default** : value return if no name is available
        - **maxlen** : integer (default None) - max length of name

        *Returns* : list of name founded'''
        return [util.cast(val, dtype='name', default=default, maxlen=maxlen) for val in self.values]

    def vSimple(self, string=False):
        '''
        Apply a vSimple function to values and return the result.

        *Parameters*

        - **string** : boolean(default False) - if True the values returned are string

        *Returns* : list of vSimple values (string or not)'''
        if string:
            return json.dumps([util.cast(val, 'simple', string=string) for val in self.values],
                              cls=ESValueEncoder)
        return [util.cast(val, 'simple', string=string) for val in self.values]
