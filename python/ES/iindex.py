# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: philippe@loco-labs.io

The `ES.iindex` module contains the `Iindex` class.

Documentation is available in other pages :

- The Json Standard for Iindex is defined 
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/IlistJSON-Standard.pdf)
- The concept of 'indexed list' is described in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression tests are at 
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_iindex.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples/Iindex)
 are :
    - [creation](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Iindex/Iindex_creation.ipynb)
    - [value](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Iindex/Iindex_value.ipynb)
    - [update](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Iindex/Iindex_update.ipynb)
    - [structure](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Iindex/Iindex_structure.ipynb)
    - [structure-analysis](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Iindex/Iindex_structure-analysis.ipynb)

---

"""
#%% declarations
from util import util
import json
from copy import copy, deepcopy
import datetime
import numpy as np
from ESconstante import ES
from util import identity
from collections import defaultdict, Counter
from ESValue import ESValueEncoder, ESValue

class Iindex:
#%% intro
    '''
    An `Iindex` is a representation of an index list .

    *Attributes (for dynamic attributes see @property methods)* :

    - **name** : name of the Iindex
    - **codec** : list of values for each key
    - **keys** : list of code values

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Iindex.Idic`
    - `Iindex.Iext`
    - `Iindex.Iobj`
    - `Iindex.from_parent`
    - `Iindex.from_obj`

    *dynamic value (getters @property)*

    - `Iindex.values`
    - `Iindex.val`
    - `Iindex.cod`
    - `Iindex.infos`

    *add - update methods*

    - `Iindex.append`    
    - `Iindex.setcodecvalue`   
    - `Iindex.setcodeclist`   
    - `Iindex.setname`
    - `Iindex.setkeys`
    - `Iindex.setlistvalue`
    - `Iindex.setvalue`

    *transform methods*

    - `Iindex.coupling`
    - `Iindex.extendkeys`
    - `Iindex.full`
    - `Iindex.reindex`
    - `Iindex.reorder`
    - `Iindex.sort`
    - `Iindex.tocoupled`
    - `Iindex.tostdcodec`
    
    *getters methods*

    - `Iindex.couplinginfos`
    - `Iindex.derkeys`
    - `Iindex.getduplicates`
    - `Iindex.iscrossed`
    - `Iindex.iscoupled`
    - `Iindex.isderived`
    - `Iindex.islinked`
    - `Iindex.isvalue`
    - `Iindex.iskeysfromderkeys`
    - `Iindex.keysfromderkeys`
    - `Iindex.keytoval`
    - `Iindex.loc`   
    - `Iindex.recordfromkeys`   
    - `Iindex.recordfromvalue`   
    - `Iindex.valtokey`   

    *export methods*
    
    - `Iindex.to_obj`
    - `Iindex.to_numpy`   
    - `Iindex.vlist`
    - `Iindex.vName`
    - `Iindex.vSimple`
    '''
    def __init__(self, codec=None, name=None, keys=None, typevalue=ES.def_clsName, 
                 lendefault=0, reindex=False):
        '''
        Iindex constructor.

        *Parameters*

        - **codec** :  list (default None) - external different values of index (see data model)
        - **keys** :  list (default None)  - key value of index (see data model)
        - **name** : string (default None) - name of index (see data model)
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to codec
        - **lendefault** : integer (default 0) - default len if no keys is defined
        - **reindex** : boolean (default True) - if True, default codec is apply'''
        #print(name)
        #t0=time()
        if isinstance(codec, Iindex):
            self.keys  = copy(codec.keys)
            self.codec = deepcopy(codec.codec)
            self.name  = copy(codec.name)
            return
        #if keys is None : keys  = []
        if codec is None: codec = []
        if not isinstance(codec, list): codec = [codec]
        leng = lendefault
        if codec and len(codec) > 0 and not leng: leng = len(codec)
        #if keys : leng = len(keys)
        if not keys is None: leng = len(keys)
        if not name: name = ES.defaultindex 
        else:
            typevalue = util.typename(name, typevalue)
            #if typename: typevalue = typename
            #if name in ES.typeName: typevalue = ES.typeName[name]
            #if name[0:2] == 'ES':   typevalue = ES.ES_clsName
        #if not isinstance(keys, list): raise IindexError("keys not list")
        if not (keys is None or isinstance(keys, list)): raise IindexError("keys not list")
        #if not keys: keys = [(i*len(codec))//leng for i in range(leng)]
        if keys is None and leng == 0: keys = [] 
        elif keys is None: keys = [(i*len(codec))//leng for i in range(leng)]
        #if not keys: 
        #    if len(codec) == 1: keys = [0] * leng
        #    else:  keys = list(range(leng))
        if not isinstance(codec, list): raise IindexError("codec not list")
        if codec == [] : codec = util.tocodec(keys)
        #codec = util.castobj(codec, typevalue)
        codec = [ESValue.from_obj(val, typevalue) for val in codec]
        self.keys  = keys
        self.codec = codec
        self.name  = name
        if reindex: self.reindex()
        #print('time', time()-t0)

    @classmethod
    def Iext(cls, values=None, name=None, typevalue=ES.def_clsName, fullcodec=False):
        '''
        Iindex constructor (external list).

        *Parameters*

        - **values** :  list (default None) - external values of index (see data model)
        - **name** : string (default None) - name of index (see data model)
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to codec
        - **fullcodec** : boolean (default False) - full codec if True'''
        #print('debut iindex iext')
        #t0=time()
        if not values: return cls(name=name, typevalue=typevalue)
        if isinstance(values, Iindex): return copy(values)
        if not isinstance(values, list): values = [values]
        typevalue = util.typename(name, typevalue)
        #if name in ES.typeName: typevalue = ES.typeName[name]
        #if name and name[0:2] == 'ES':   typevalue = ES.ES_clsName
        values = util.castobj(values, typevalue)
        if fullcodec: codec, keys = (values, [i for i in range(len(values))])
        else:  codec, keys = util.resetidx(values)
        #print('fin iext', time()-t0)
        return cls(name=name, codec=codec, keys=keys, typevalue=None)

    @classmethod
    def Idic(cls, dicvalues=None, typevalue=ES.def_clsName, fullcodec=False):
        '''
        Iindex constructor (external dictionnary).

        *Parameters*

        - **dicvalues** : {name : values}  (see data model)
        - **fullcodec** : boolean (default False) - full codec if True
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to codec'''
        if not dicvalues: return cls.Iext(name=None, values=None, typevalue=typevalue, 
                                          fullcodec=fullcodec)
        if isinstance(dicvalues, Iindex): return copy(dicvalues)
        if not isinstance(dicvalues, dict): raise IindexError("dicvalues not dict")
        if len(dicvalues) != 1: raise IindexError("one key:values is required")
        name = list(dicvalues.keys())[0]
        values = dicvalues[name]
        return cls.Iext(name=name, values=values, typevalue=typevalue, 
                        fullcodec=fullcodec)

    @classmethod
    def from_parent(cls, codec, parent, name=None, typevalue=ES.def_clsName, reindex=False):
        '''Generate an Iindex Object from specific codec and parent keys.

        *Parameters*

        - **codec** : list of objects 
        - **name** : string (default None) - name of index (see data model)
        - **parent** : Iindex, parent of the new Iindex
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to codec
        - **reindex** : boolean (default True) - if True, default codec is apply
        
        *Returns* : Iindex '''
        if isinstance(codec, Iindex): return copy(codec)
        return Iindex(codec=codec, name=name, keys=parent.keys, typevalue=typevalue, reindex=reindex)
    
    @classmethod
    def Iobj(cls, bs, extkeys=None, typevalue=ES.def_clsName, context=True, reindex=False):
        '''Generate an Iindex Object from a bytes, json or dict value and from 
        a keys list (derived Iindex)

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to codec
        - **extkeys** : list (default None) of int, string or dict data to convert in keys
        - **context** : boolean (default True) - if False, only codec and keys are included
        - **reindex** : boolean (default True) - if True, default codec is apply

        *Returns* : tuple(code, Iindex) '''
        return Iindex.from_obj(bs, extkeys=extkeys, typevalue=typevalue, context=context, reindex=reindex)[1]
    
    @classmethod
    def from_obj(cls, bs, extkeys=None, typevalue=ES.def_clsName, context=True, reindex=False):
        '''Generate an Iindex Object from a bytes, json or dict value and from 
        a keys list (derived Iindex)

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to codec
        - **extkeys** : list (default None) of int, string or dict data to convert in keys
        - **context** : boolean (default True) - if False, only codec and keys are included
        - **reindex** : boolean (default True) - if True, default codec is apply

        *Returns* : tuple(code, Iindex) '''
        #print('debut fromobj')
        #t0 = time()
        if isinstance(bs, Iindex): return (ES.nullparent, copy(bs))
        name, typevaluedec, codec, parent, keys = util.decodeobj(bs, typevalue, context)
        if extkeys and parent >= 0 :  keys = Iindex.keysfromderkeys(extkeys, keys)
        elif extkeys and parent < 0 :  keys = extkeys
        #if not keys: keys = list(range(len(codec)))
        if keys is None: keys = list(range(len(codec)))
        if typevaluedec: typevalue=typevaluedec
        return (parent, Iindex(codec=codec, name=name, keys=keys, typevalue=typevalue, reindex=reindex))
        
#%% special
    def __repr__(self):
        '''return classname and number of value'''
        return self.__class__.__name__ + '[' + str(len(self)) + ']'
   
    def __str__(self):
        '''return json string format'''
        return '    ' + self.to_obj(encoded=True, fullcodec=True, untyped=False) + '\n'

    def __eq__(self, other):
        ''' equal if class and values are equal'''
        return self.__class__ == other.__class__ and self.values == other.values

    def __len__(self):
        ''' len of values'''
        return len(self.keys)

    def __contains__(self, item):
        ''' item of values'''
        return item in self.values

    def __getitem__(self, ind):
        ''' return value item (value conversion)'''
        if isinstance(ind, tuple): return [copy(self.values[i]) for i in ind]
        return copy(self.values[ind])

    def __setitem__(self, ind, value):
        ''' modify values item'''
        if ind < 0 or ind >= len(self) : raise IindexError("out of bounds")
        self.setvalue(ind, value, extern=True)

    def __delitem__(self, ind):
        '''remove a record (value and key).'''
        self.keys.pop(ind)
        self.reindex()
    
    def __hash__(self): 
        '''return hash(codec) + hash(keys)'''
        return util.hash(self.codec) + util.hash(self.keys)
    
    def __add__(self, other):
        ''' Add other's values to self's values in a new Iindex'''
        newiindex = self.__copy__()
        newiindex.__iadd__(other)
        return newiindex

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        return self.add(other, solve=False)     

    def add(self, other, solve=True):
        ''' Add other's values to self's values

        *Parameters*

        - **other** : Iindex object to add to self object
        - **solve** : Boolean (default True) - If True, replace None other's codec value
        with self codec value. 
        
        *Returns* : self '''      
        if solve: 
            solved = copy(other)
            for i in range(len(solved.codec)):
                #if solved.codec[i] is None and i in range(len(self.codec)): 
                if not util.isNotNull(solved.codec[i]) and i in range(len(self.codec)): 
                    solved.codec[i] = self.codec[i]
            values = self.values + solved.values
        else: values = self.values + other.values
        codec = util.tocodec(values)
        if set(codec) != set(self.codec): self.codec = codec
        self.keys  = util.tokeys(values, self.codec)
        return self

    def __copy__(self):
        ''' Copy all the data '''
        #return Iindex([copy(cod) for cod in self.codec], copy(self.name), copy(self.keys))
        return Iindex(self)
    
#%% property
    @property
    def cod(self):
        '''return codec conversion to string '''
        return self.to_obj(fullcodec=False, codecval=True, encoded=False, listunic=True)
        #return self.to_obj(fullcodec=False, simpleval=True, encoded=False, listunic=True)
        #if ES.def_clsName: return [cod.json(encoded=False) for cod in self.codec]
        #return self.codec
        
    @property
    def infos(self):
        '''return dict with lencodec, typecodec, rate, disttomin, disttomax'''
        M = len(self)
        m = len(set(self.codec))
        x = len(self.codec)
        rate = 0.0
        if   M == 0: typecodec = 'null'
        elif x == 1: typecodec = 'unique'
        #elif m == 1: typecodec = 'unique'
        elif m == M: typecodec = 'complete'
        elif x == M: typecodec = 'full'
        else: 
            rate = (M - x) / (M - m)
            if x == m:  typecodec = 'default'
            else:       typecodec = 'mixed'
        disttomin = x - m
        disttomax = M - x
        return {'lencodec': x, 'min': m, 'max': M, 'typecodec': typecodec, 
                'rate': rate, 'disttomin': disttomin, 'disttomax': disttomax}

    @property
    def typevalue(self):
        '''return typevalue calculated from name'''
        return util.typename(self.name)   

    @property
    def values(self):
        '''return values (see data model)'''
        return [self.codec[key] for key in self.keys]    

    @property
    def val(self):
        '''return values conversion to string '''
        return self.to_obj(fullcodec=True, codecval=True, encoded=False)
        #return self.to_obj(fullcodec=True, simpleval=True, encoded=False)
        #if ES.def_clsName: return [self.codec[key].json(encoded=False) for key in self.keys]
        #return self.values

#%% methods
    def append(self, value,  typevalue=ES.def_clsName, unique=True):
        '''add a new value

        *Parameters*

        - **value** : new object value
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to value
        - **unique** :  boolean (default True) - If False, duplication codec if value is present

        *Returns* : key of value '''        
        #if typevalue is None: typevalue = self.typevalue
        #if typevalue is None: dtype = None
        #else: dtype = ES.valname[typevalue]
        #value = util.cast(value, dtype)
        value = util.castval(value, util.typename(self.name, ES.def_clsName))
        if value in self.codec and unique: key = self.codec.index(value)
        else: 
            key = len(self.codec)
            self.codec.append(value)
        self.keys.append(key)
        return key
        
    @staticmethod
    def merging(listidx, name=None):
        '''Create a new Iindex with values are tuples of listidx Iindex values
        
        *Parameters*

        - **listidx** : list of Iindex to be merged.
        - **name** : string (default : None) - Name of the new Iindex

        *Returns* : new Iindex'''        
        if not name: name = str(list(set([idx.name for idx in listidx])))
        values = util.tuple(util.transpose([idx.values for idx in listidx]))
        return Iindex.Iext(values, name)
    
    def coupling(self, idx, derived=True):
        '''
        Transform indexes in coupled or derived indexes (codec extension).
        If derived option is True, self.codec is extended and idx codec not,
        else, both are coupled and both codec are extended.

        *Parameters*

        - **idx** : single Iindex or list of Iindex to be coupled or derived.
        - **derived** : boolean (default : True)

        *Returns* : tuple with duplicate records (errors)'''
        if not isinstance(idx, list): index = [idx]
        else: index = idx
        idxzip = Iindex.Iext(list(zip(*([self.keys] + [ix.keys for ix in index]))), 
                             typevalue=None)
        self.tocoupled(idxzip)
        if not derived: 
            for ix in index: ix.tocoupled(idxzip)
        #return len(self.codec)
        return self.getduplicates()
    
    def couplinginfos(self, other, default=False):
        '''return a dict with the coupling info between other (lencoupling, rate, 
        disttomin, disttomax, distmin, distmax, diff, typecoupl)

        *Parameters*

        - **other** : other index to compare
        - **default** : comparison with default codec 

        *Returns* : dict'''
        if default: return util.couplinginfos(self.values, other.values)
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
        x  = len(util.tocodec([tuple((v1,v2)) for v1, v2 in zip(self.keys, other.keys)]))
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
        '''return keys derived from parent keys
 
        *Parameters*

        - **parent** : Iindex - parent

        *Returns* : list of keys'''
        derkey  = [ES.nullparent] * len(parent.codec)
        for i in range(len(self)):
            derkey[parent.keys[i]] = self.keys[i]
        if min(derkey) < 0:
            raise IindexError("parent is not a derive Iindex")
        return derkey

    def extendkeys(self, keys):
        '''add keys to the Iindex
        
        *Parameters*

        - **keys** : list of int (value lower or equal than actual keys)
        
        *Returns* : None '''
        if min(keys) < 0 or max(keys) > len(self.codec) - 1: 
            raise IindexError('keys not consistent with codec')
        self.keys += keys
    
    @staticmethod
    def full(listidx):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **listidx** : list of Iindex to transform

        *Returns* : tuple of records added '''     
        idx1 = listidx[0]
        for idx in listidx: 
            if len(idx) != len(idx): return
        leninit = len(idx1)
        keysadd = util.idxfull(listidx)
        for idx, keys in zip(listidx, keysadd): idx.keys += keys
        return tuple(range(leninit, len(idx1)))
        
    def getduplicates(self):
        ''' return tuple of items with duplicate codec'''
        co = Counter(self.codec)
        defcodec = list(co - Counter(list(co)))       
        dkeys  = defaultdict(list)
        for l,i in zip(self.keys, range(len(self))): dkeys[l].append(i)
        dcodec = defaultdict(list)
        for l,i in zip(self.codec, range(len(self.codec))): dcodec[l].append(i)       
        duplicates = []
        for item in defcodec: 
            for codecitem in dcodec[item]: duplicates += dkeys[codecitem]    
        return tuple(duplicates)
    
    def iscrossed(self, other):
        '''return True if self is crossed to other'''
        return self.couplinginfos(other)['rate'] == 1.0

    def iscoupled(self, other):
        '''return True if self is coupled to other'''
        info = self.couplinginfos(other)
        return info['diff'] == 0 and info['rate'] == 0

    def isderived(self, other):
        '''return True if self is derived from other'''
        info = self.couplinginfos(other)
        return info['diff'] != 0 and info['rate'] == 0.0 

    def iskeysfromderkeys(self, other):
        leng = len(other.codec)    
        keys = [(i*len(self.codec))//leng for i in range(leng)]
        return Iindex.keysfromderkeys(other.keys, keys) == self.keys
        
    def islinked(self, other):
        '''return True if self is linked to other'''
        rate = self.couplinginfos(other)['rate']
        return rate < 1.0 and rate > 0.0

    def isvalue(self, value, extern=True):
        ''' return True if value is in index values

        *Parameters*

        - **value** : value to check
        - **extern** : if True, compare value to external representation of self.value, 
        else, internal'''
        if extern: return value in self.val
        return value in self.values

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

    def keytoval(self, key, extern=True):
        ''' return the value of a key
        
        *Parameters*

        - **key** : key to convert into values
        - **extern** : if True, return string representation else, internal value
        
        *Returns*

        - **int** : first key finded (None else)'''
        if key < 0 or key >= len(self.codec): return None
        if extern: return self.cod[key]
        return self.codec[key]

    @staticmethod
    def keysfromderkeys(parentkeys, derkeys):
        '''return keys from parent keys and derkeys
        
        *Parameters*

        - **parentkeys** : list of keys from parent
        - **derkeys** : list of derived keys

        *Returns* : list of keys'''
        return [derkeys[parentkeys[i]] for i in range(len(parentkeys))]
    
    def loc(self, value, extern=True):
        '''return a list of record number with value
        
        *Parameters*

        - **value** : value to check
        - **extern** : if True, compare value to external representation of self.value, 
        else, internal
        
        *Returns*

        - **list of int** : list of record number finded (None else)'''
        return self.recordfromvalue(value, extern=extern)
    
    def recordfromvalue(self, value, extern=True):
        '''return a list of record number with value
        
        *Parameters*

        - **value** : value to check
        - **extern** : if True, compare value to external representation of self.value, 
        else, internal
        
        *Returns*

        - **list of int** : list of record number finded (None else)'''
        
        if extern: value = util.castval(value, util.typename(self.name, ES.def_clsName))
        #if extern: value = util.cast(value, ES.def_dtype)
        if not value in self.codec: raise IndexError('value not present')
        listkeys = [cod for cod, val in zip(range(len(self.codec)), self.codec) if val == value]
        return self.recordfromkeys(listkeys)
        #return [rec for rec, key in zip(range(len(self)), self.keys ) if key in keys ]
    
    def recordfromkeys(self, listkeys):
        '''return a list of record number with key in listkeys
        
        *Parameters*

        - **listkeys** : list of keys to check
        
        *Returns*

        - **list of int** : list of record number finded (None else)'''
        
        return [rec for rec, key in zip(range(len(self)), self.keys ) if key in listkeys ]
    
    def reindex(self, codec=None):
        '''apply a reordered codec. If None, a new default codec is apply. 
        
        *Parameters*

        - **codec** : list (default None) - reordered codec to apply. 

        *Returns* : self'''

        if not codec: codec = util.tocodec(self.values)
        self.keys = util.reindex(self.keys, self.codec, codec)
        self.codec = codec
        return self
        
    def reorder(self, sort=None, inplace=True):
        '''Change the Iindex order with a new order define by sort and reset the codec.

        *Parameters*

        - **sort** : int list (default None)- new record order to apply. If None, no change.
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Iindex is created.

        *Returns*

        - **Iindex** : self if inplace, new Iindex if not inplace'''
        values      = util.reorder(self.values, sort)
        codec, keys = util.resetidx(values)
        if inplace :
            self.keys  = keys
            self.codec = codec
            return None
        return Iindex(name=self.name, codec=codec, keys=keys)
    
    def setcodecvalue(self, oldvalue, newvalue, extern=True, typevalue=None, 
                      nameonly=False, valueonly=False):
        '''update all the oldvalue by newvalue

        *Parameters*

        - **oldvalue** : list of values to replace 
        - **newvalue** : list of new value to apply
        - **typevalue** : str (default None) - cast to apply to the new value 
        - **extern** : if True, the newvalue has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : int - last codec rank updated (-1 if None)'''
        typevalue = util.typename(self.name, typevalue)
        if extern: 
            newvalue = util.castval(newvalue, typevalue)
            oldvalue = util.castval(oldvalue, typevalue)
        rank = -1
        for i in range(len(self.codec)):
            if self.codec[i] == oldvalue: 
                if   typevalue in ES.ESclassName and nameonly:  self.codec[i].setName (newvalue.name)
                elif typevalue in ES.ESclassName and valueonly: self.codec[i].setValue(newvalue.value)
                self.codec[i] = newvalue
                rank = i
        return rank
    
    def setcodeclist(self, listcodec, extern=True, typevalue=None, nameonly=False, valueonly=False):
        '''update codec with listcodec values

        *Parameters*

        - **listcodec** : list of new codec values to apply
        - **typevalue** : str (default None) - cast to apply to the new value 
        - **extern** : if True, the newvalue has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : int - last codec rank updated (-1 if None)'''
        typevalue = util.typename(self.name, typevalue)
        if extern: listcodec = util.castobj(listcodec, typevalue)
        for i in range(len(self.codec)):
            if   typevalue in ES.ESclassName and nameonly:  self.codec[i].setName (listcodec[i].name)
            elif typevalue in ES.ESclassName and valueonly: self.codec[i].setValue(listcodec[i].value)
            else: self.codec[i] = listcodec[i]

    def setkeys(self, keys, inplace=True):
        '''apply new keys (replace codec with extended codec from parent keys)

        *Parameters*

        - **keys** : list of keys to apply
        - **inplace** : if True, update self data, else create a new Iindex

        *Returns* : self or new Iindex'''
        codec = util.tocodec(self.values, keys)
        if inplace:
            self.codec = codec
            self.keys  = keys
            return self
        return Iindex(codec=codec, name=self.name, keys=keys)

    def setname(self, name):
        '''update the Iindex name 
        
        *Parameters*

        - **name** : str to set into name

        *Returns* : boolean - True if update'''
        if isinstance(name, str): 
            self.name = name 
            return True
        return False
        
    def setvalue(self, ind, value, extern=True, typevalue=None, nameonly=False, valueonly=False):
        '''update a value at the rank ind (and update codec and keys) 
        
        *Parameters*

        - **ind** : rank of the value 
        - **value** : new value 
        - **extern** : if True, the value has external representation, else internal
        - **typevalue** : str (default None) - cast to apply to the new value 
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : None'''
        typevalue = util.typename(self.name, typevalue)
        if extern: value = util.castval(value, typevalue)
        values = self.values
        if   typevalue in ES.ESclassName and nameonly:  values[ind].setName (values.name)
        elif typevalue in ES.ESclassName and valueonly: values[ind].setValue(values.value)
        else: values[ind] = value
        self.codec, self.keys = util.resetidx(values)

    def setlistvalue(self, listvalue, extern=True, typevalue=None, nameonly=False, valueonly=False):
        '''update the values (and update codec and keys) 
        
        *Parameters*

        - **listvalue** : list - list of new values
        - **typevalue** : str (default None) - class to apply to the new value 
        - **extern** : if True, the value has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : None'''
        typevalue = util.typename(self.name, typevalue)
        if extern: listvalue = util.castobj(listvalue, typevalue)
        values = self.values
        for i in range(len(listvalue)):
            if   typevalue in ES.ESclassName and nameonly:  values[i].setName (listvalue[i].name)
            elif typevalue in ES.ESclassName and valueonly: values[i].setValue(listvalue[i].value)
            else: values[i] = listvalue[i]
        self.codec, self.keys = util.resetidx(values)
        #if extern and not typevalue: typevalue = ES.def_clsName
        #values = util.castobj(listvalue, typevalue)
        #self.codec, self.keys = util.resetidx(values)
        
    def sort(self, reverse=False, inplace=True, func=str):
        '''Define sorted index with ordered codec.

        *Parameters*

        - **reverse** : boolean (defaut False) - codec is sorted with reverse order
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Iindex is created.
        - **func**    : function (default str) - key used in the sorted function

        *Return*
        
        - **Iindex** : self if inplace, new Iindex if not inplace'''
        if inplace:
            self.reindex(codec=sorted(self.codec, reverse=reverse, key=func))
            self.keys.sort()
            return self
        oldcodec    = self.codec
        codec       = sorted(oldcodec, reverse=reverse, key=str)
        return Iindex(name=self.name, codec=codec,
                      keys=sorted(util.reindex(self.keys, oldcodec, codec)))

    def tocoupled(self, other, coupling=True):
        '''
        Transform a derived index in a coupled index (keys extension) and add 
        new values to have the same length as other.

        *Parameters*

        - **other** : index to be coupled.
        - **coupling** : boolean (default True) - reindex if False

        *Returns* : None'''
        dic = util.idxlink(other.keys, self.keys)
        if not dic: raise IindexError("Iindex is not coupled or derived from other")
        self.codec = [self.codec[dic[i]] for i in range(len(dic))]
        self.keys  = other.keys
        if not coupling: self.reindex()

    def tostdcodec(self, inplace=False, full=True):
        '''
        Transform codec in full or in default codec.

        *Parameters*

        - **inplace** : boolean (default True) - if True, new order is apply to self,
        - **full** : boolean (default True) - if True reindex with fullcodec

        *Return*
        
        - **Iindex** : self if inplace, new Iindex if not inplace'''
        if full:
            codec = self.values
            keys  = list(range(len(codec)))
        else:
            codec = util.tocodec(self.values)
            keys  = util.reindex(self.keys, self.codec, codec)
        if inplace:
            self.codec = codec
            self.keys  = keys
            return self
        return Iindex(codec=codec, name=self.name, keys=keys)
    
    def to_numpy(self, func=None, codec=False, npdtype=None, **kwargs):
        '''
        Transform Iindex in a Numpy array.

        *Parameters*

        - **func** : function (default None) - function to apply for each value of the Iindex. 
        If func is the 'index' string, values are replaced by raw values.
        - **npdtype** : string (default None) - numpy dtype for the Array ('object' if None)
        - **kwargs** : parameters to apply to the func function

        *Returns* : Numpy Array'''
        #option = {'dtype': None} | kwargs
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
        #return np.array(values, dtype=object)
        '''    try : datetime.datetime.fromisoformat(values[0])
            except : return np.array(values)
            return np.array(values, dtype=np.datetime64)
        if isinstance(values[0], datetime.datetime): 
            return np.array(values, dtype=np.datetime64)
        return np.array(values)'''

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
    
    def valrow(self, row):
        ''' return val for a record
        
        *Parameters*

        - **row** : record to obtain val
        
        *Returns* : val[row]'''
        cc = ESValue._uncastsimple(self.codec[self.keys[row]])
        if isinstance(cc, (str, int, float, bool, list, dict, type(None), bytes)): 
            return cc        
        return cc.json(encoded=False) 
    
    def valtokey(self, value, extern=True):
        '''convert a value to a key 
        
        *Parameters*

        - **value** : value to convert
        - **extern** : if True, the value has external representation, else internal

        *Returns*

        - **int** : first key finded (None else)'''
        if extern: value = util.castval(value, util.typename(self.name, ES.def_dtype))
        if value in self.codec:  return self.codec.index(value)
        return None

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

class IindexError(Exception):
    ''' Iindex Exception'''
    #pass
