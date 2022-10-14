# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.iindex_interface` module contains the `IindexInterface` class
(`observation.iindex.Iindex` methods).
"""
# %% declarations
import json
import datetime
import numpy as np
import cbor2

from esconstante import ES
from esvalue_base import ESValueEncoder
from util import util, identity


class IindexError(Exception):
    ''' Iindex Exception'''
    # pass

class IindexEncoder(json.JSONEncoder):
    """new json encoder for Iindex and Ilist"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        option = {'encoded': False, 'encode_format': 'json'}
        if o.__class__.__name__ in ('Ilist', 'TimeSlot'):
            return o.json(**option)
        if issubclass(o.__class__, ESValue):
            return o.json(**option)
        try:
            return o.to_json(**option)
        except:
            try:
                return o.__to_json__()
            except:
                return json.JSONEncoder.default(self, o)



class IindexInterface:
    '''this class includes Iindex methods'''

    @staticmethod
    def encodeobj(codeclist, keyslist=None, name=None, fullcodec=False, simpleval=False,
                  codecval=False, typevalue=None, parent=ES.nullparent, listunic=False, **kwargs):
        '''
        Return a formatted object with values, keys and codec.
        - Format can be json, bson or cbor
        - object can be string, bytes or dict

        *Parameters*
        - **codeclist** : list of codec ESValue to encode
        - **keyslist** : list (default = None) - int keys to encode, None if no keys 
        - **name** : string (default = None) - name to encode, None if no name 
        - **fullcodec** : boolean (default False) - if True, use a full codec
        - **typevalue** : string (default None) - type to convert values
        - **parent** : int (default ES.nullparent) - Ilist index linked to
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
                            fullcodec=fullcodec, untyped=option['untyped'],
                            geojson=option['geojson']) for cc in codeclist]
        if len(js) == 1 and isinstance(js[0], str):
            listunic = True
        if len(codlis) == 1 and not listunic and not isinstance(codlis[0], list):
            codlis = codlis[0]
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
            return json.dumps(js, cls=IindexEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor':
            return cbor2.dumps(js, datetime_as_timestamp=True,
                               timezone=datetime.timezone.utc, canonical=True)
        return js

    def json(self, keys=None, typevalue=None, fullcodec=False, simpleval=False,
             codecval=False, parent=ES.nullparent, **kwargs):
        '''Return a formatted object (string, bytes or dict) for the Iindex

        *Parameters*

        - **keys** : list (default None) - list: List of keys to include - None:
        no list - else: Iindex keys
        - **typevalue** : string (default None) - type to convert values
        - **fullcodec** : boolean (default False) - if True, use a full codec
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
        return self.to_obj(keys=keys, typevalue=typevalue, fullcodec=fullcodec,
                           codecval=codecval, simpleval=simpleval, parent=parent,
                           **option)

    def to_numpy(self, func=None, codec=False, npdtype=None, **kwargs):
        '''
        Transform Iindex in a Numpy array.

        *Parameters*

        - **func** : function (default None) - function to apply for each value of the Iindex.
        If func is the 'index' string, values are replaced by raw values.
        - **npdtype** : string (default None) - numpy dtype for the Array ('object' if None)
        - **kwargs** : parameters to apply to the func function

        *Returns* : Numpy Array'''
        if len(self) == 0:
            raise IindexError("Ilist is empty")
        if npdtype is None:
            npdtype = np.dtype('object')
        else:
            npdtype = np.dtype(npdtype)
        if func is None:
            func = identity
        if func == 'index':
            return np.array(list(range(len(self))))
        if not codec:
            values = util.funclist(self.values, func, **kwargs)
        else:
            values = util.funclist(self.codec, func, **kwargs)
        if isinstance(values[0], (str, datetime.datetime)):
            try:
                return np.array(values, dtype=np.datetime64)
            except:
                return np.array(values, dtype=npdtype)
        return np.array(values, dtype=npdtype)

    def to_obj(self, keys=None, typevalue=None, fullcodec=False, simpleval=False,
               codecval=False, parent=ES.nullparent, name=True, listunic=False, **kwargs):
        '''Return a formatted object (string, bytes or dict) for the Iindex

        *Parameters*

        - **keys** : list (default None) - list: List of keys to include - None:
        no list - else: Iindex keys
        - **typevalue** : string (default None) - type to convert values
        - **fullcodec** : boolean (default False) - if True, use a full codec
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
        if keys and isinstance(keys, list):
            keyslist = keys
        elif keys and not isinstance(keys, list):
            keyslist = self.keys
        else:
            keyslist = None
        if not name or self.name == ES.defaultindex:
            idxname = None
        else:
            idxname = self.name
        if fullcodec:
            codeclist = self.values
            keyslist = None
            parent = ES.nullparent
        else:
            codeclist = self.codec
        if typevalue:
            dtype = ES.valname[typevalue]
        else:
            dtype = None
        return IindexInterface.encodeobj(codeclist, keyslist, idxname, fullcodec, simpleval,
                              codecval, dtype, parent, listunic, **kwargs)

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
