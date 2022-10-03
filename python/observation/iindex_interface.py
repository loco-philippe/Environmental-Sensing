# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.iindex_interface` module contains the `IindexInterface` class 
(`observation.iindex.Iindex` methods).
"""
#%% declarations
from util import util
import json
import datetime
import numpy as np

from esconstante import ES
from util import identity
from esvalue_base import ESValueEncoder

class IindexError(Exception):
    ''' Iindex Exception'''
    #pass

class IindexInterface:

    def json(self, keys=None, typevalue=None, fullcodec=False, simpleval=False, 
             codecval=False, parent=ES.nullparent, **kwargs):
        '''Return a formatted object (string, bytes or dict) for the Iindex

        *Parameters*

        - **keys** : list (default None) - list: List of keys to include - None: no list - else: Iindex keys
        - **typevalue** : string (default None) - type to convert values
        - **fullcodec** : boolean (default False) - if True, use a full codec
        - **simpleval** : boolean (default False) - if True, only codec is included
        - **parent** : integer (default None) - index number of the parent in indexset

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **untyped** : boolean (default True) - include dtype in the json if True

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'untyped': True,
                  'codif': {} } | kwargs        
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
        if len(self) == 0: raise IindexError("Ilist is empty")
        if npdtype is None: npdtype = np.dtype('object')
        else: npdtype = np.dtype(npdtype)
        if func is None : func = identity
        if func == 'index' : return np.array(list(range(len(self))))
        if not codec: values = util.funclist(self.values, func, **kwargs)
        else:  values = util.funclist(self.codec, func, **kwargs)
        if isinstance(values[0], (str, datetime.datetime)):
            try: return np.array(values, dtype=np.datetime64)
            except : return np.array(values, dtype=npdtype)
        return np.array(values, dtype=npdtype)

    def to_obj(self, keys=None, typevalue=None, fullcodec=False, simpleval=False, 
               codecval=False, parent=ES.nullparent, name=True, listunic=False, **kwargs):
        '''Return a formatted object (string, bytes or dict) for the Iindex

        *Parameters*

        - **keys** : list (default None) - list: List of keys to include - None: no list - else: Iindex keys
        - **typevalue** : string (default None) - type to convert values
        - **fullcodec** : boolean (default False) - if True, use a full codec
        - **name** : boolean (default True) - if False, name is not included
        - **codecval** : boolean (default False) - if True, only list of codec values is included
        - **simpleval** : boolean (default False) - if True, only value (without name) is included
        - **listunic** : boolean (default False) - if False, when len(result)=1 return value not list
        - **parent** : integer (default None) - index number of the parent in indexset

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **untyped** : boolean (default False) - include dtype if True

        *Returns* : string, bytes or dict'''
        if   keys and     isinstance(keys, list):   keyslist = keys
        elif keys and not isinstance(keys, list):   keyslist = self.keys
        else:                                       keyslist = None
        if not name or self.name == ES.defaultindex:    idxname     = None
        else:                                           idxname     = self.name
        if fullcodec:                       
                                            codeclist   = self.values 
                                            keyslist    = None 
                                            parent      = ES.nullparent
        else:                               codeclist   = self.codec
        if typevalue:                       dtype       = ES.valname[typevalue]
        else:                               dtype       = None
        return util.encodeobj(codeclist, keyslist, idxname, fullcodec, simpleval, 
                              codecval, dtype, parent, listunic, **kwargs)    

    def vlist(self, func, *args, extern=True, **kwargs):
        '''
        Apply a function to values and return the result.

        *Parameters*

        - **func** : function - function to apply to values
        - **args, kwargs** : parameters for the function
        - **extern** : if True, the function is apply to external values, else internal

        *Returns* : list of func result'''
        if extern: return util.funclist(self.val, func, *args, **kwargs)
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
        if string: return json.dumps([util.cast(val, 'simple', string=string) for val in self.values],
                                   cls=ESValueEncoder)    
        return [util.cast(val, 'simple', string=string) for val in self.values]

