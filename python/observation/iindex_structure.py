# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.iindex_structure` module contains the `IindexStructure` class 
(`observation.iindex.Iindex` methods).
"""
from collections import defaultdict, Counter

from esvalue_base import ESValue
from util import util
from esconstante import ES
from iindex_interface import IindexError

class IindexStructure:
    def append(self, value,  typevalue=ES.def_clsName, unique=True):
        '''add a new value

        *Parameters*

        - **value** : new object value
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to value
        - **unique** :  boolean (default True) - If False, duplication codec if value is present

        *Returns* : key of value '''        
        value = util.castval(value, util.typename(self.name, ES.def_clsName))
        if value in self.codec and unique: key = self.codec.index(value)
        else: 
            key = len(self.codec)
            self.codec.append(value)
        self.keys.append(key)
        return key
        
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
        idxzip = self.__class__.Iext(list(zip(*([self.keys] + [ix.keys for ix in index]))), 
                             typevalue=None)
        self.tocoupled(idxzip)
        if not derived: 
            for ix in index: ix.tocoupled(idxzip)
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
        return self.__class__.keysfromderkeys(other.keys, keys) == self.keys
        
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
        if not value in self.codec: raise IndexError('value not present')
        listkeys = [cod for cod, val in zip(range(len(self.codec)), self.codec) if val == value]
        return self.recordfromkeys(listkeys)
    
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
        return self.__class__(name=self.name, codec=codec, keys=keys)
    
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
        return self.__class__(codec=codec, name=self.name, keys=keys)

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
        return self.__class__(name=self.name, codec=codec,
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
        return self.__class__(codec=codec, name=self.name, keys=keys)
        
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
