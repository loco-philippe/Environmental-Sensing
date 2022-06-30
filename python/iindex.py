# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: a179227
"""
#%% declarations
from collections import Counter
from itertools import product
from copy import copy, deepcopy
from timeslot import TimeSlot
import datetime, cbor2
import json
import re
import numpy as np
from ESValue import LocationValue, DatationValue, PropertyValue, NamedValue
from ESValue import ESValue, ExternValue
from ilist import Ilist, IlistEncoder, CborDecoder
import math
from ESconstante import ES, _classval

def identity(*args, **kwargs):
    '''return the same value as args or kwargs'''
    if len(args) > 0 : return args[0]
    if len(kwargs) > 0 : return kwargs[list(kwargs.keys())[0]]
    return None

class Iindex:
#%% intro
    '''
    An `Iindex` is a representation of an index list .

    *Attributes (for @property see methods)* :

    - **values** : list of data to be indexed (dynamic value)
    - **name** : name of the list
    - **codec** : list of values for each key
    - **keys** : list of code values
    - **typevalue** : type of values

    The methods defined in this class are :

    *constructor (classmethod))*

    - `Iindex.Idic`
    - `Iindex.Iext`
    - `Iindex.from_parent`
    - `Iindex.from_obj`

    *dynamic value property (getters)*

    - `Iindex.values`
    - `Iindex.infos`

    *add - update methods*

    - `Iindex.append`    
    - `Iindex.setcodecvalue`   
    - `Iindex.setname`
    - `Iindex.setvalue`

    *transform methods*

    - `Iindex.coupling`
    - `Iindex.toextendcodec`
    - `Iindex.extendkeys`
    - `Iindex.reindex`
    - `Iindex.reorder`
    - `Iindex.sort`
    - `Iindex.tocrossed`
    - `Iindex.tocoupled`
    - `Iindex.tostdcodec`
    
    *idx property (getters)*

    - `Iindex.couplinginfos`
    - `Iindex.iscrossed`
    - `Iindex.iscoupled`
    - `Iindex.isderived`
    - `Iindex.islinked`
    - `Iindex.isvalue`
    - `Iindex.keytoval`
    - `Iindex.valtokey`   

    *export function*
    
    - `Iindex.to_obj`
    - `Iindex.to_numpy`   
    - `Iindex.vlist`
    '''
    _castfunc = {'datvalue':        DatationValue,
                 'locvalue':        LocationValue,
                 'prpvalue':        PropertyValue,
                 'namvalue':        NamedValue,
                 'extvalue':        ExternValue,
                 'slot':            TimeSlot,
                 #'ilist':           Ilist.from_obj,
                 #'observation':     Observation,
                 'datetime':        datetime.datetime.fromisoformat,
                 'coordinates':     LocationValue._gshape}
    _invcastfunc = {val:key for key,val in _castfunc.items()}

    def __init__(self, codec=None, name=None, keys=None, typevalue=None, 
                 lendefault=0, fast=True):
        '''
        Iindex constructor.

        *Parameters*

        - **codec** :  list (default None) - external different values of index (see data model)
        - **keys** :  list (default None)  - key value of index (see data model)
        - **name** : string (default None) - name of index (see data model)
        - **lendefault** : integer (default 0) - default len of the generic keys 
        if no keys is defined'''
        if isinstance(codec, Iindex):
            self.keys  = codec.keys
            self.codec = codec.codec
            self.name  = codec.name            
        else:
            if name and not typevalue:
                if name in ES.typeName: typevalue = ES.typeName[name]
                if name[0:2] == 'ES':   typevalue = ES.ES_clsName
            if not keys: keys =[]
            if not isinstance(keys, list): raise IindexError("keys not list")
            if lendefault > 0 and keys == []: keys = list(range(lendefault))
            if not name: name = 'default index'
            if not codec: codec =[]
            if not isinstance(codec, list): raise IindexError("codec not list")
            if codec == [] : codec = util.tocodec(keys, fast=fast)
            codec = util.castobj(codec, typevalue)
            self.keys  = keys
            self.codec = codec
            self.name  = name

    @classmethod
    def Iext(cls, values=None, name=None, typevalue=None, fast=True, fullcodec=False):
        '''
        Iindex constructor (external list).

        *Parameters*

        - **values** :  list (default None) - external values of index (see data model)
        - **name** : string (default None) - name of index (see data model)
        - **fullcodec** : boolean (default False) - full codec if True
        - **fast** : boolean (default False) - fast methods for simple values'''
        if not values: return cls(name=name, typevalue=typevalue)
        if isinstance(values, Iindex): return values
        if not isinstance(values, list): values = [values]
        if fullcodec: codec, keys = (values, [i for i in range(len(values))])
        else:  codec, keys = util.resetidx(values, fast)
        return cls(name=name, codec=codec, keys=keys, typevalue=typevalue, fast=fast)

    @classmethod
    def Idic(cls, dicvalues=None, typevalue=None, fast=True, fullcodec=False):
        '''
        Iindex constructor (external dictionnary).

        *Parameters*

        - **dicvalues** : {name : values}  (see data model)
        - **fullcodec** : boolean (default False) - full codec if True
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        is generated if no index is defined'''
        if not dicvalues: return cls.Iext(name=None, values=None, typevalue=typevalue, 
                                          fast=fast, fullcodec=fullcodec)
        if isinstance(dicvalues, Iindex): return dicvalues
        if not isinstance(dicvalues, dict): raise IindexError("dicvalues not dict")
        if len(dicvalues) != 1: raise IindexError("one key:values is required")
        name = list(dicvalues.keys())[0]
        values = dicvalues[name]
        return cls.Iext(name=name, values=values, typevalue=typevalue, 
                        fast=fast, fullcodec=fullcodec)

    @classmethod
    def from_parent(cls, codec, parent, name=None, fast=True):
        '''Generate an Iindex Object from specific codec and parent keys.

        *Parameters*

        - **codec** : list of objects 
        - **parent** : Iindex, parent of the new Iindex

        *Returns* : Iindex '''
        if isinstance(codec, Iindex): return codec
        #return Iindex(codec, name, util.tokeys(parent.values, fast=fast))
        return Iindex(codec, name, parent.keys, fast=fast)
    
    @classmethod
    def from_obj(cls, bs, extkeys=None, fast=True):
        '''Generate an Iindex Object from a bytes, json or dict value and from 
        a keys list (derived Iindex)

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **size** : length of Iindex
        - **extkeys** : list of int, string or dict data to convert

        *Returns* : Iindex '''
        if isinstance(bs, Iindex): return (-1, bs)
        codec, name, keys, typevalue, parent = util.decodeobj(bs)
        if extkeys and parent > -1 :  keys = Iindex.keysfromderkeys(extkeys, keys)
        elif extkeys and parent == -1 :  keys = extkeys
        if not keys: keys = list(range(len(codec)))
        return (parent, Iindex(codec=codec, name=name, keys=keys, 
                               typevalue=typevalue, fast=fast))
        
#%% special
    def __repr__(self):
        return self.__class__.__name__ + '[' + str(len(self)) + ']'

    """def stri(self):
        ''' return ival and iidx'''
        texLis = json.dumps(self.ival) + '\n'
        for idx in self.iidx : texLis += '\n' + json.dumps(idx)
        print(texLis)

    def stre(self):
        ''' return valname, extval, idxname and extidx'''
        option = {'encoded': False, 'encode_format': 'json', 'typevalue': True}
        texLis = json.dumps({self.valname: [self._json(val, **option) for val in self.extval]},
                            cls=IlistEncoder)+ '\n'
        for (idx, nam) in zip(self.extidx, self.idxname) :
            option |= {'typevalue': not nam in ES.esObsClass}
            texLis += '\n' + json.dumps({nam: [self._json(i, **option) for i in idx]}, 
                                        cls=IlistEncoder)
        return texLis"""
   
    def __str__(self):
        return self.name + ' : ' + self.values.__repr__() + '\n'

    def __eq__(self, other):
        ''' equal if values are equal'''
        try: return self.values == other.values
        except: return False

    def __len__(self):
        ''' len of values'''
        return len(self.keys)

    def __contains__(self, item):
        ''' item of values'''
        return item in self.values

    def __getitem__(self, ind):
        ''' return values item'''
        return self.values[ind]

    def __setitem__(self, ind, val):
        ''' modify values item'''
        if ind < 0 or ind >= len(self) : raise IindexError("out of bounds")
        self.setvalue(ind, val, fast=False)

    def __add__(self, other):
        ''' Add other's values to self's values in a new Iindex'''
        newiindex = self.__copy__()
        newiindex.__iadd__(other)
        return newiindex

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        values = self.values + other.values
        self.codec = util.tocodec(values, fast=False)
        self.keys  = util.tokeys(values, self.codec, fast=False)
        return self

    """def or__(self, other):
        ''' Add other's index to self's index in a new Ilist'''
        newilist = self.__copy__()
        newilist.__ior__(other)
        return newilist

    def ior__(self, other):
        ''' Add other's index to self's index'''
        if len(self) != len(other) : raise IlistError("the sizes are not equal")
        for i in range(other.lenidx):
            if other.idxname[i] not in self.idxname :
                self.addlistidx(other.idxname[i], other.setidx[i], other.iidx[i])
        return self"""

    def __copy__(self):
        ''' Copy all the data (deepcopy)'''
        return deepcopy(self)

#%% property
    @property
    def values(self):
        '''return values (see data model)'''
        return [self.codec[key] for key in self.keys]

    @property
    def infos(self):
        '''return lencodec, typeindex, rate, disttomin, disttomax,  (see data model)'''
        M = len(self)
        x = len(self.codec)
        typeindex = 'mixte'
        if   M == 0: 
            typeindex = 'null'
            rate = 0.0
            disttomin = disttomax = 0
        else:
            if M == 1: rate = 0.0
            else:      rate = (M - x) / (M - 1)
            if x == 1:   typeindex = 'unique' 
            elif x == M: typeindex = 'complete' 
            disttomin = x - 1
            disttomax = M - x
        return {'lencodec': x, 'typeindex': typeindex, 'rate': rate, 
                'disttomin': disttomin, 'disttomax': disttomax}

#%% methods

    def append(self, value, unique=True, fast=False):
        '''add a new value

        *Parameters*

        - **value** : new object value
        - **unique** :  boolean (default True) - If False, duplication codec if value is present
        - **fast** : boolean (default False) - Update whithout reindex

        *Returns* : key of value '''        
        if value in self.codec and unique: key = self.codec.index(value)
        else: 
            key = len(self.codec)
            self.codec.append(value)
        self.keys.append(key)
        return key
        
    def coupling(self, idx, derived=True, fast=True):
        '''
        Transform indexes in coupled or derived indexes (codec extension).

        *Parameters*

        - **idx** : index to be coupled or derived.
        - **derived** : boolean (default : True) - If True, idx is not changed.

        *Returns* : None'''
        if not isinstance(idx, list): index = [idx]
        else: index = idx
        #zp = zip(self.keys, idx.keys)
        #else:  
        #zp =           
        idxzip = Iindex.Iext(list(zip(*([self.keys] + [ix.keys for ix in index]))), fast=fast)
        self.tocoupled(idxzip)
        if not derived: 
            for ix in index: ix.tocoupled(idxzip)
        return len(self.codec)
    
    def couplinginfos(self, other, default=False, fast=True):
        '''return the coupling info between other (dict)

        *Parameters*

        - **other** : other index to compare
        - **default** : comparison with default codec 

        *Returns* : dict'''
        #print(self.name, other.name)
        if default: return util.couplinginfos(self.values, other.values, fast)
        if min(len(self), len(other)) == 0:
            return {'lencoupling': 0, 'rate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': 0, 'distmax': 0, 'diff': 0, 'typecoupl': 'null'}
        ls = len(self.codec)
        lo = len(other.codec)
        x0 = max(ls, lo)
        x1 = ls * lo
        diff = abs(ls - lo)
        if min(ls, lo) == 1: 
            if ls == 1: typec = 'derived'
            else: typec = 'derive'
            return {'lencoupling': x0, 'rate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': x0, 'distmax': x1, 'diff': diff, 'typecoupl': typec}
        x  = len(util.tocodec([tuple((v1,v2)) for v1, v2 in zip(self.keys, other.keys)], fast=fast))
        dic = {'lencoupling': x, 'rate': (x - x0) / (x1 - x0),
                'disttomin': x - x0,  'disttomax': x1 - x,
                'distmin': x0, 'distmax': x1, 'diff': diff}
        if   dic['rate'] == 0 and dic['diff'] == 0: dic['typecoupl'] = 'coupled'
        elif dic['rate'] == 0 and ls < lo:          dic['typecoupl'] = 'derived'
        elif dic['rate'] == 0 and ls > lo:          dic['typecoupl'] = 'derive'
        elif dic['rate'] == 1:                      dic['typecoupl'] = 'crossed'
        elif ls < lo:                               dic['typecoupl'] = 'linked'
        else:                                       dic['typecoupl'] = 'link'
        return dic

    def derkeys(self, parent):
        '''return derived keys from parent keys'''
        derkey  = [-1] * len(parent.codec)
        for i in range(len(self)):
            derkey[parent.keys[i]] = self.keys[i]
        if min(derkey) == -1:
            raise IindexError("parent is not a derive Iindex")
        return derkey
    
    @staticmethod
    def keysfromderkeys(parentkeys, derkeys):
        '''return keys from parent keys and derkeys'''
        return [derkeys[parentkeys[i]] for i in range(len(parentkeys))]
    
    def toextendcodec2(self, parent, inplace=True, fast=True):
        '''replace codec with extended codec from parent keys'''
        keys  = parent.keys
        codec = util.tocodec(self.values, keys, fast=fast)
        if inplace:
            self.codec = codec
            self.keys  = keys
            return self
        return Iindex(codec=codec, name=self.name, keys=keys)

    def toextendcodec(self, parent, inplace=True, fast=True):
        '''replace codec with extended codec from parent'''
        keys  = util.tokeys(parent.values, fast=fast)
        codec = util.tocodec(self.values, keys, fast=fast)
        if inplace:
            self.codec = codec
            self.keys  = keys
            return self
        return Iindex(codec=codec, name=self.name, keys=keys)
        
    def extendkeys(self, keys):
        '''add keys to the Iindex
        
        *Parameters*

        - **keys** : list of int (value present in Iindex keys)
        
        *Returns* : None '''
        if min(keys) < 0 or max(keys) > len(self.codec)-1: 
            raise IindexError('keys not consistent with codec')
        self.keys += keys
    
    def iscrossed(self, other):
        '''return True if is crossed to other'''
        return self.couplinginfos(other)['rate'] == 1.0

    def iscoupled(self, other):
        '''return True if is coupled to other'''
        info = self.couplinginfos(other)
        return info['diff'] == 0 and info['rate'] == 0

    def isderived(self, other):
        '''return True if is derived from other'''
        info = self.couplinginfos(other)
        return info['diff'] != 0 and info['rate'] == 0.0 

    def islinked(self, other):
        '''return True if is linked to other'''
        rate = self.couplinginfos(other)['rate']
        return rate < 1.0 and rate > 0.0

    def isvalue(self, value):
        ''' return True if value is in index values'''
        return value in self.values

    def keytoval(self, key):
        ''' return the first value of a key
        
        *Parameters*

        - **key** : key to convert into values

        *Returns*

        - **int** : first key finded (None else)'''
        if key > 0 and key < len(self.codec): return self.codec[key]
        return None

    def recordfromvalue(self, value):
        '''return a list of record number with value'''
        if not value in self.codec: raise IndexError('value not present')
        code = [cod for cod, val in zip(range(len(self.codec)), self.codec) if val == value]
        return [rec for rec, key in zip(range(len(self.keys )), self.keys ) if key in code ]
    
    def reindex(self, codec=None, fast=True):
        '''apply a reordered codec (return None)
        
        *Parameters*

        - **codec** : list (default None) - reordered codec to apply. If None, a new codec is calculated.
        - **fast** : boolean (default False) - If True, fast operation (reduction controls)'''
        if not codec: codec = util.tocodec(self.values, fast=fast)
        self.keys = util.reindex(self.keys, self.codec, codec, fast=fast)
        self.codec = codec
        return self
        
    def reorder(self, sort=None, inplace=True, fast=True):
        '''Change the Iindex order with a new order define by sort and reset the codec.

        *Parameters*

        - **sort** : int list (default None)- new record order to apply. If None, no change.
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Iindex is created.

        *Returns*

        - **None**, if inplace. **Iindex** if not inplace'''
        values      = util.reorder(self.values, sort)
        codec, keys = util.resetidx(values, fast=fast)
        if inplace :
            self.keys  = keys
            self.codec = codec
            return None
        return Iindex(name=self.name, codec=codec, keys=keys, fast=fast)
    
    def setcodecvalue(self, oldvalue, newvalue, dtype=None):
        '''update all the oldvalue values by newvalue

        *Parameters*

        - **oldvalue** : value to replace 
        - **newvalue** : new value to apply
        - **dtype** : str (default None) - cast to apply to the new value 

        *Returns* : int - last codec rank updated (-1 if None)'''
        rank = -1
        for i in range(len(self.codec)):
            if self.codec[i] == oldvalue: 
                self.codec[i] = util.cast(newvalue, dtype)
                rank = i
        return rank
    
    def setname(self, name):
        '''update the Iindex name (return None)
        
        *Parameters*

        - **name** : str to set into name '''
        if isinstance(name, str): self.name = name 
        
    def setvalue(self, ind, value, dtype=None, fast=True):
        '''update a value at the rank ind (and update codec and keys) 
        
        *Parameters*

        - **ind** : rank of the value 
        - **value** : new value 
        - **dtype** : str (default None) - cast to apply to the new value 
        - **fast** : boolean (default False) - Update whithout reindex

        *Returns* : None'''
        values = self.values
        values[ind] = util.cast(value, dtype)
        self.codec, self.keys = util.resetidx(values, fast)

    def sort(self, reverse=False, inplace=True, fast=True):
        '''Define new sorted index with ordered codec.

        *Parameters*

        - **reverse** : boolean (defaut False) - codec is sorted with reverse order
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        - **fast** : boolean (default False) - Update whithout reindex
        
        *Returns* : None'''
        if inplace:
            self.reindex(codec=sorted(self.codec, reverse=reverse, key=str), fast=fast)
            self.keys.sort()
            return None
        oldcodec    = self.codec
        codec       = sorted(oldcodec, reverse=reverse, key=str)
        return Iindex(name=self.name, codec=codec,
                      keys=sorted(util.reindex(self.keys, oldcodec, codec, fast=fast)),
                      fast=fast)

    @staticmethod
    def tocrossed(indexset):
        '''Add new values to obtain an indexset with only crossed Indexes

        *Parameters*

        - **indexset** : list of Iindex - list of indexes to be crossed.

        *Returns* : None'''
        if not indexset or not isinstance(indexset, list) or not isinstance(indexset[0], Iindex):
            raise IindexError('indexset is not a list of Iindex')
        keysset = util.idxfull(indexset)
        if not keysset: return
        for i in range(len(indexset)): indexset[i].extendkeys(keysset[i])

    def tocoupled(self, other, coupling=True, fast=True):
        '''
        Transform a derived index in a coupled index (keys extension) and add 
        new values to have the same length as other.

        *Parameters*

        - **other** : index to be coupled.
        - **coupling** : boolean (default True) - reindex if False

        *Returns* : None'''
        dic = util.idxlink(other.keys, self.keys)
        if not dic: raise IindexError("Iindex is not coupled or derived from other")
        #self.codec = [self.codec[dic[i]] for i in range(len(idx))]
        self.codec = [self.codec[dic[i]] for i in range(len(dic))]
        self.keys  = other.keys
        if not coupling: self.reindex(fast=fast)

    def tostdcodec(self, inplace=False, fast=True, full=True):
        '''
        Transform codec in full or in default codec.

        *Returns* : self or Iindex'''
        if full:
            codec = self.values
            keys  = list(range(len(codec)))
        else:
            codec = util.tocodec(self.values, fast=fast)
            keys  = util.reindex(self.keys, self.codec, codec, fast=fast)
        if inplace:
            self.codec = codec
            self.keys  = keys
            return self
        return Iindex(codec=codec, name=self.name, keys=keys, fast=fast)
    
    def to_numpy(self, func=identity, **kwargs):
        if len(self) == 0: raise IindexError("Ilist is empty")
        if func is None : func = identity
        if func == 'index' : return np.array(list(range(len(self.values))))
        values = util.funclist(self.values, func, **kwargs)
        if isinstance(values[0], str):
            try : datetime.datetime.fromisoformat(values[0])
            except : return np.array(values)
            return np.array(values, dtype=np.datetime64)
        if isinstance(values[0], datetime.datetime): 
            return np.array(values, dtype=np.datetime64)
        return np.array(values)

    def to_obj(self, keys=None, typevalue=None, parent=-1, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default True). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **keys** : list (default None) - list: List of keys to include - None: no list - else: Iindex keys
        - **typevalue** : string (default None) - type to convert values
        - **parent** : integer (default None) - index number of the parent in indexset

        *Returns* : string, bytes or dict'''
        if   keys and     isinstance(keys, list):   keyslist = keys
        elif keys and not isinstance(keys, list):   keyslist = self.keys
        else:                                       keyslist = None
        if self.name == 'default index': name = None
        else: name = self.name
        codeclist = self.codec
        return util.encodeobj(codeclist, keyslist, name, typevalue,
                               parent, **kwargs)    
    
    def valtokey(self, value):
        '''convert a value to a key 
        
        *Parameters*

        - **value** : value to convert

        *Returns*

        - **int** : first key finded (None else)'''
        if value in self.codec:  return self.codec.index(value)
        else: return None

    def vlist(self, func, *args, **kwargs):
        '''
        Apply a function to values and return the result.

        *Parameters*

        - **func** : function - function to apply to values
        - **args, kwargs** : parameters for the function
        - **idx** : integer - index to update (idx=-1 for extval)

        *Returns* : list of func result'''
        return util.funclist(self.values, func, *args, **kwargs)

class util:       
#%% internal
    c1 = re.compile('\d+\.?\d*[,\-_ ;:]')
    c2 = re.compile('[,\-_ ;:]\d+\.?\d*')

    @staticmethod
    def cast(val, dtype):
        ''' convert val in the type defined by the string dtype'''
        if not dtype :      return val
        if dtype == 'str':      return str(val)
        if dtype == 'int':
            try : return int(val.lstrip())
            except : return math.nan
        if dtype == 'float':
            try : return float(val.lstrip())
            except : return math.nan
        if dtype == 'datetime':
            try : return datetime.datetime.fromisoformat(val)
            except : return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        if dtype == 'coord':
            if util.c1.search(val) and util.c2.search(val) :
                return [float(util.c1.search(val)[0][:-1]), float(util.c2.search(val)[0][1:])]
            else : return [-1, -1]
        if dtype in ES.typeName:
            classdtype = _classval()[ES.typeName[dtype]]    
            if not isinstance(val, classdtype): return classdtype(val)            
        raise IindexError("dtype : " + dtype + " inconsistent with data")
        
    @staticmethod
    def castobj(lis, typevalue):
        if not lis: return lis
        if typevalue in ES.className and \
        not typevalue in [ES.ES_clsName, ES.obs_clsName, ES.ili_clsName]:
            return _classval()[typevalue].cast(lis)
        idx = copy(lis)
        for i in range(len(idx)):
            if idx[i].__class__.__name__ not in _classval() and \
                    (typevalue == ES.ES_clsName or 
                     ESValue.valClassName(idx[i]) != ES.nam_clsName): 
                idx[i] = _classval()[ESValue.valClassName(idx[i])](idx[i])     
        return idx
            
    @staticmethod
    def couplinginfos(l1, l2, fast=True):
        '''return the coupling info between two list (dict)'''
        if not l1 or not l2:
            return {'lencoupling': 0, 'rate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': 0, 'distmax': 0, 'diff': 0, 'typecoupl': 'null'}
        ls = len(util.tocodec(l1, fast=fast))
        lo = len(util.tocodec(l2, fast=fast))
        x0 = max(ls, lo)
        x1 = ls * lo
        diff = abs(ls - lo)
        if min(ls, lo) == 1: 
            if ls == 1: typec = 'derived'
            else: typec = 'derive'
            return {'lencoupling': x0, 'rate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': x0, 'distmax': x1, 'diff': diff, 'typecoupl': typec}
        x = len(util.tocodec([tuple((v1,v2)) for v1, v2 in zip(l1, l2)], fast=fast))
        dic = {'lencoupling': x, 'rate': (x - x0) / (x1 - x0),
                'disttomin': x - x0,  'disttomax': x1 - x,
                'distmin': x0, 'distmax': x1, 'diff': diff}
        if   dic['rate'] == 0 and dic['diff'] == 0: dic['typecoupl'] = 'coupled'
        elif dic['rate'] == 0 and ls < lo:          dic['typecoupl'] = 'derived'
        elif dic['rate'] == 0 and ls > lo:          dic['typecoupl'] = 'derive'
        elif dic['rate'] == 1:                      dic['typecoupl'] = 'crossed'
        else:                                       dic['typecoupl'] = 'linked'
        return dic

    @staticmethod 
    def decodeobj(bs=None, fast=True):
        '''Generate an Iindex Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert

        *Returns* : Iindex '''
        # decode bs
        if not bs:                       return ([],  None, None, None, -1)
        if   isinstance(bs, bytes): lis = cbor2.loads(bs)
        elif isinstance(bs, str):   lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list):  lis = bs
        else: raise IindexError("the type of parameter is not available")
        if not isinstance(lis, list): raise IindexError("the parameter has to be a list")
        if not lis:                      return ([],  None, None, None, -1)
        if not isinstance(lis[0], list): return (lis, None, None, None, -1)
        if len(lis)==1:                  return (lis, None, None, None, -1)
        codec = lis[0]
        name = keys = typevalue = None
        parent = -1
        if lis[1] is None or isinstance(lis[1], str): name = lis[1]
        elif not isinstance(lis[1], list) or len(lis[1]) == 0: 
            raise IindexError("the parameter is unconsistent")
        else: 
            if isinstance(lis[1][0], int): keys = lis[1]
            elif not isinstance(lis[1][0], (type(None), str, int)):
                raise IindexError("the parameter is unconsistent")
            else:    
                name = lis[1][0]
                if   len(lis[1]) > 1 and isinstance(lis[1][1], int): parent    = lis[1][1]
                elif len(lis[1]) > 1 and isinstance(lis[1][1], str): typevalue = lis[1][1]
                else: raise IindexError("the parameter is unconsistent")
                if   len(lis[1]) ==3 and isinstance(lis[1][2], str): typevalue = lis[1][2]
                elif len(lis[1]) > 2: raise IindexError("the parameter is unconsistent")
        if   len(lis) > 2 and isinstance(lis[2], list): keys = lis[2]
        elif len(lis) > 2: raise IindexError("the parameter is unconsistent")
        '''if parent >= 0:   #!!!
            adjustedcodec = Iindex(codec, keys=keys, fast=fast)
            codec = adjustedcodec.values
            keys = None'''
        return (codec, name, keys, typevalue, parent)

    @staticmethod
    def encodeobj(codeclist, keyslist=None, name=None, typevalue=None, 
                  parent=-1, **kwargs):
        '''
        Return a formatted object with values, keys and codec.
        Format can be json, bson or cbor
        object can be string, bytes or dict

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default True). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **parent** : int (default -1) - Ilist index linked to (-1 if primary)
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'fast': True, 
                  'codif': {}} | kwargs
        js = codeclist
        if name or typevalue or parent >= 0 or keyslist or \
            (len(codeclist)==1 and name):    js = [js]
        if name or typevalue or parent >= 0:
            if not typevalue and parent < 0: js.append(name)
            elif not typevalue:              js.append([name, parent])
            elif parent < 0:                 js.append([name, typevalue])
            else:                            js.append([name, parent, typevalue])
        if keyslist:                         js.append(keyslist)
        if option['encoded'] and option['encode_format'] == 'json': 
            return json.dumps( js, cls=IlistEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(js, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return js

    @staticmethod
    def filter(func, lis, res, *args, **kwargs ):
        '''apply "func" to each value of "lis" and tests if equals "res".
        Return the list of index with True result.'''
        lisf = util.funclist(lis, func, *args, **kwargs)
        return [i for i in range(len(lis)) if lisf[i] == res]

    @staticmethod
    def funclist(value, func, *args, **kwargs):
        '''return the function func applied to the object value with parameters args and kwargs'''
        if func in (None, []) : return value
        lis = []
        if not isinstance(value, list): listval = [value]
        else : listval = value
        for val in listval :
            try : lis.append(val.func(*args, **kwargs))
            except :
                try : lis.append(func(val, *args, **kwargs))
                except :
                    try : lis.append(listval.func(val, *args, **kwargs))
                    except :
                        try : lis.append(func(listval, val, *args, **kwargs))
                        except : raise IindexError("unable to apply func")
        if len(lis) == 1 : return lis[0]
        return lis

    @staticmethod
    def idxfull(setidx):
        '''return additional keys for each index to have crossed setidx'''
        setcodec = [set(idx.keys) for idx in setidx]
        lenfull = util.mul([len(codec) for codec in setcodec])
        if lenfull == len(setidx[0]) : return []
        complet = Counter(list(product(*setcodec))) 
        complet.subtract(Counter(util.tuple(util.transpose([idx.keys for idx in setidx]))))
        keysadd = util.transpose(util.list(list(complet.elements())))
        if not keysadd : return []
        return keysadd

    @staticmethod
    def idxlink(ref, l2):
        ''' return dic ={ref i : l2 i} pour chaque tuple different'''
        lis = set(util.tuple(util.transpose([ref, l2])))
        if not len(lis) == len(set(ref)) : return {}
        return dict(lis)

    @staticmethod
    def index(idx, val):
        '''return the index of val in idx'''
        if not isinstance(val, list): return idx.index(val)
        return [idx.index(v) for v in val]

    @staticmethod
    def json(val, **option):
        '''return the dict format of val (if function json() or to_json() exists)'''
        if isinstance(val, (str, int, float, bool, tuple, list, type(None), bytes)): 
            return val
        if isinstance(val, datetime.datetime): 
            return {ES.datetime: val}
        if isinstance(val, tuple(util.invcastfunc.keys())[0:5]):      #ESValue
            if not option['typevalue']: return val.json(**option)
            else: return {util.invcastfunc[val.__class__]: val.json(**option)} 
        if isinstance(val, Ilist): return {ES.ili_valName: val.json(**option)}
        if val.__class__.__name__ == 'Observation': return {ES.obs_valName: val.to_json(**option)}


    @staticmethod
    def keyscrossed(lenidx): 
        '''return a list of crossed keys from a list of length'''
        listrange = [range(lidx) for lidx in lenidx] 
        return util.transpose(util.list(list(product(*listrange))))

    @staticmethod
    def list(values): 
        '''transform a list of tuples in a list of lists'''
        return list(map(list, values))

    @staticmethod
    def mul(values):
        mul = 1
        for val in values : mul *= val
        return mul

    @staticmethod
    def reindex(oldkeys, oldcodec, newcodec, fast) :
        '''new keys with new order of codec'''
        if fast :
            dic= {newcodec[i]:i for i in range(len(newcodec))}
            return [dic[oldcodec[key]] for key in oldkeys]
        return [newcodec.index(oldcodec[key]) for key in oldkeys]

    @staticmethod
    def reorder(values, sort=None):
        '''change the order of values following the order of sort'''
        if not sort: return values
        return [values[ind] for ind in sort]
    
    @staticmethod
    def resetidx(values, fast=True):
        '''return codec and keys from values'''
        codec = util.tocodec(values, fast=fast)
        return (codec, util.tokeys(values, codec, fast))

    @staticmethod
    def str(idx): 
        '''return a list with values in the str format'''
        return [str(val) for val in idx]

    @staticmethod
    def tokeys(values, codec=None, fast=True):
        ''' return index of extv in extset'''
        if not codec: codec = util.tocodec(values, fast=fast)
        if fast :
            dic = {codec[i]:i for i in range(len(codec))}
            return [dic[val] for val in values]
        return [codec.index(val) for val in values]
 
    @staticmethod
    def tovalues(keys, codec, fast=True):
        '''return values for keys'''
        return [codec[key] for key in keys]

    @staticmethod
    def tonumpy(lis, func=identity, **kwargs):
        if func is None : func = identity
        if func == 'index' : return np.array(list(range(len(lis))))
        valList = util.funclist(lis, func, **kwargs)
        if type(valList[0]) == str :
            try : datetime.datetime.fromisoformat(valList[0])
            except : return np.array(valList)
            return np.array(valList, dtype=np.datetime64)
        if type(valList[0]) == datetime.datetime : return np.array(valList, dtype=np.datetime64)
        return np.array(valList)

    @staticmethod
    def tocodec(values, keys=None, fast=True):
        '''extract a list of unique values'''
        if fast and not keys: return list(set(values))
        if fast and keys:
            ind, codec = zip(*sorted(set(zip(keys,values))))
            #if ind != tuple(range(len(codec))): 
            #    raise IindexError('keys is not compatible with values')
            return list(codec)
        codec = []
        if not keys:
            #return [val for val in values if not val in codec]
            for val in values :
                if not val in codec : codec.append(val)
            return codec
        i = -1
        for ind, val in sorted(zip(keys,values)):
            if ind == i + 1 : 
                codec.append(val)
                i += 1
        return codec
    
    @staticmethod
    def transpose(idxset):
        '''exchange row/column in a list of list'''
        if not isinstance(idxset, list): raise IindexError('index not transposable')
        if not idxset: return []
        size = min([len(ix) for ix in idxset]) 
        #return [[ix[ind] for ix in idxset] for ind in range(len(idxset[0]))]
        return [[ix[ind] for ix in idxset] for ind in range(size)]

    @staticmethod
    def tuple(idx):
        '''transform a list of list in a list of tuple'''
        return [val if not isinstance(val, list) else tuple(val) for val in idx]

class IindexError(Exception):
    ''' Ilist Exception'''
    #pass

"""
    def updateset(self, extind):
        # ajouter à la fin un recalcul de iidx en fonction de sorted(extset)
        iind = []
        for i in range(len(extind)):
            if len(self.setidx) == i : self.setidx.append([])
            if extind[i] not in self.setidx[i] : self.setidx[i].append(extind[i])
            iind.append(self.setidx[i].index(extind[i]))
        return iind

    def xderived(self, idxder, idxori) :
        dic = self._idxlink(self.extidx[idxori], self.extidx[idxder], coupled=False)
        return [dic[i] for i in self.setidx[idxori]]
    
    def to_obj(self, **kwargs):
        '''
        Return a formatted object with values, keys and codec.
        Format can be json, bson or cbor
        object can be string, bytes or dict

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (bson, json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **link** : int (default -1) - index linked to (-1 if primary)
        - **complete** : boolean (default True) - True if Ilist is complete
        - **values** : boolean (default False) - True if values are included

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'fast': False, 
                  'link': -1, 'complete': True, 'values': False, 'codif': {}} | kwargs
        option2 = option | {'encoded': False, 'typevalue': False}
        js = {}
        js['name'] = self.name
        if option['values']: js['values'] = self.values
        else:
            js['codec'] = self.codec
            if option['link'] >= 0:      js['link']  = option['link']
            elif not option['complete']: js['keys'] = self.keys
        if option['codif'] and option['encode_format'] != 'bson':
            js2 = {}
            for k,v in js.items():
                if k in option['codif']: js2[option['codif'][k]] = v
                else: js2[k] = v
        else: js2 = js
        if option['encoded'] and option['encode_format'] == 'json': 
            return json.dumps( js2, cls=IlistEncoder)
        if option['encoded'] and option['encode_format'] == 'bson': 
            return bson.encode(js2)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(js2, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return js2
        '''        
        if option['fast'] :
        else:
            for i in range(len(ils.setidx)):
                if ils.idxname[i] != 'default index': 
                    option2 |= {'typevalue': not ils.idxname[i] in ES.esObsClass}
                    js[ils.idxname[i]] = [self._json(idx, **option2) for idx in ils.setidx[i]]
                    #js[ils.idxname[i]] = [self._json(idx, **option2) for idx in ils.setidx[i]]
            option2 |= {'typevalue': False}
            if not nulres: 
                js[ils.valname] = [self._json(ils.extval[i], **option2) for i in range(len(ils))]'''

    @classmethod
    def from_obj(cls, bs=None, indexset=None):
        '''Generate an Iindex Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert

        *Returns* : Iindex '''
        if not bs: bs = {} 
        if isinstance(bs, bytes):
            if bs[len(bs)-1] != 0x00 and (bs[0] & 0b11100000)== 0b10100000:
                dic2 = cbor2.loads(bs)
            else: dic2 = bson.decode(bs)
        elif isinstance(bs, str) : dic2 = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, dict): dic2 = bs
        else: raise IindexError("the type of parameter is not available")
        dic = {}
        for k,v in dic2.items():
            if k in ES.invcodeb: dic[ES.invcodeb[k]] = v
            else: dic[k] = v
        name = dic['name']
        if 'values' in dic: return Iindex.Iext(dic['values'], name)
        codec = dic['codec']
        if 'link' in dic: return Iindex(codec, name, indexset[dic['link']].keys)
        if 'keys' in dic: return Iindex(codec, name, dic['keys'])
        return Iindex(codec, name, [])

    def extendvalues(self, other, coupling=True):
        '''add new values to have the same length as other'''
        if not self.isderived(other) and not self.iscoupled(other):
            raise IindexError('The Iindex is not derived or coupled with other')
        self.tocoupled(other)
        if not coupling: self.reindex()   

    def resetkeys(self, fast=False):
        '''reset codec and keys from values (return None)

        *Parameters*

        - **fast** : boolean (default False). If True, fast operation (reduction controls)'''
        self.codec, self.keys = util.resetidx(self.values, fast)

    @classmethod
    def from_obj(cls, bs=None, fast=False):
        '''Generate an Iindex Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert

        *Returns* : Iindex '''
        
        if isinstance(bs, Iindex): return bs
        #codec, name, keys, typevalue, size, parent = util.decodeobj(bs)
        codec, name, keys, typevalue, code = util.decodeobj(bs)
        if keys: return Iindex(codec=codec, name=name, keys=keys, typevalue=typevalue, fast=fast)
        else: return Iindex.Iext(values=codec, name=name, typevalue=typevalue, fast=fast)

    @classmethod
    def from_extobj(cls, bs, size=None, extkeys=None, fast=False):
        '''Generate an Iindex Object from a bytes, json or dict value and from 
        a keys list (derived Iindex)

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **size** : length of Iindex
        - **extkeys** : list of int, string or dict data to convert

        *Returns* : Iindex '''
        if isinstance(bs, Iindex): return (-1, bs)
        #codec, name, keys, typevalue, size, parent = util.decodeobj(bs, size)
        codec, name, keys, typevalue, code = util.decodeobj(bs, standalone=False, size=size)
        if not keys: keys = extkeys
        if not keys: keys = list(range(len(codec)))
        return (code, Iindex(codec=codec, name=name, keys=keys, typevalue=typevalue, fast=fast))
        '''if keys: 
            return Iindex(codec=codec, name=name, keys=keys, typevalue=typevalue)
        if parent >= 0 and not extkeys: 
            raise IindexError('extkeys have to be present to decode a derived or coupled index')
        if extkeys: 
            return Iindex(codec=codec, name=name, keys=extkeys, typevalue=typevalue)'''
        
    def to_obj(self, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values

        *Returns* : string, bytes or dict'''
        option = {'keys': False, 'typevalue': None} | kwargs
        if option['keys']  and len(self.codec) > 1: 
            code = len(self)
            codeclist = self.codec
            keyslist = self.keys
        else: 
            code = -1 
            codeclist = self.values
            keyslist = None
        return util.encodeobj(codeclist, self.name, keyslist, option['typevalue'],
                              code, **kwargs)

    def to_extobj(self, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **parent** : int (default -1) - Ilist index linked to (-1 if primary)
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values
        - **fullcodec** : boolean (default False). If True, fullcodec is used

        *Returns* : string, bytes or dict'''
        option = {'parent': -1, 'keys': False, 'typevalue': None, 
                  'fullcodec': False} | kwargs
        keyslist = None
        if option['fullcodec']: 
            return util.encodeobj(self.values, self.name, None, code=-1, **option)            
        if option['parent'] >= 0 and len(self.codec) > 1: 
            code = option['parent']
        else: 
            code = -1
            if option['keys'] and len(self.codec) > 1: keyslist = self.keys
        return util.encodeobj(self.codec, self.name, keyslist, code=code, **option)

    @staticmethod
    def encodeobj(codeclist=None, name=None, keyslist=None, typevalue=None, 
                  code=-1, **kwargs):
        '''
        Return a formatted object with values, keys and codec.
        Format can be json, bson or cbor
        object can be string, bytes or dict

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **parent** : int (default -1) - Ilist index linked to (-1 if primary)
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'fast': False, 
                  'codif': {}} | kwargs
        option2 = option | {'encoded': False, 'typevalue': None}
        js = []
        if typevalue:   js.append({name: code, 'type': typevalue})
        elif code >= 0: js.append({name: code})
        else:           js.append(name)
        js += codeclist
        if keyslist:    js += keyslist
        if option['encoded'] and option['encode_format'] == 'json': 
            return json.dumps( js, cls=IlistEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(js, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return js

    @staticmethod 
    def decodeobj(bs=None, standalone=True, size=None):
    #def decodeobj(bs=None, size=None):
        '''Generate an Iindex Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert

        *Returns* : Iindex '''
        # decode bs
        if not bs: bs = {} 
        if not size: size = -1
        if   isinstance(bs, bytes): lis = cbor2.loads(bs)
        elif isinstance(bs, str):   lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list):  lis = bs
        else: raise IindexError("the type of parameter is not available")
        #code = parent = -1
        code = -1
        keys = codec = typevalue = name = None
        # decode lis
        if len(lis) == 0 : return (codec, name, keys, typevalue, code)
        #if len(lis) == 0 : return (codec, name, keys, typevalue, size, parent)
        if   isinstance(lis[0], str): name = lis[0]
        elif isinstance(lis[0], dict) and len(lis[0]) > 0:
            name = list(lis[0].keys())[0]
            code = lis[0][name]
            if len(lis[0]) > 1: typevalue = lis[0]['type']
        '''if size == None and code >= 0: size = code
        elif size == None and code < 0: size = len(lis) - 1
        else: parent = code'''
        if standalone and code >= 0: size = code
        #elif standalone and code < 0: size = 0
        elif code < 0 and size < 0: size = len(lis) - 1
        '''if len(lis) - 1 > size: #and size >= 0: 
            keys = lis[1:size+1]
            codec = lis[size+1 :]'''
        if len(lis) - 1 > size: #and size >= 0: 
            codec = lis[1:len(lis)-size]
            keys = lis[len(lis)-size :]
        else: codec = lis[1 :]
        return (codec, name, keys, typevalue, code)
        #return (codec, name, keys, typevalue, size, parent)

"""
