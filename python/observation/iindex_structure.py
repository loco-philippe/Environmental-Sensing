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
    '''this class includes Iindex methods :

    *add - update methods*

    - `IindexStructure.append`
    - `IindexStructure.setcodecvalue`
    - `IindexStructure.setcodeclist`
    - `IindexStructure.setname`
    - `IindexStructure.setkeys`
    - `IindexStructure.setlistvalue`
    - `IindexStructure.setvalue`

    *transform methods*

    - `IindexStructure.coupling`
    - `IindexStructure.extendkeys`
    - `IindexStructure.full`
    - `IindexStructure.reindex`
    - `IindexStructure.reorder`
    - `IindexStructure.sort`
    - `IindexStructure.tocoupled`
    - `IindexStructure.tostdcodec`

    *getters methods*

    - `IindexStructure.couplinginfos`
    - `IindexStructure.derkeys`
    - `IindexStructure.getduplicates`
    - `IindexStructure.iscrossed`
    - `IindexStructure.iscoupled`
    - `IindexStructure.isderived`
    - `IindexStructure.islinked`
    - `IindexStructure.isvalue`
    - `IindexStructure.iskeysfromderkeys`
    - `IindexStructure.keysfromderkeys`
    - `IindexStructure.keytoval`
    - `IindexStructure.loc`
    - `IindexStructure.recordfromkeys`
    - `IindexStructure.recordfromvalue`
    - `IindexStructure.valtokey`  '''

    def append(self, value,  typevalue=ES.def_clsName, unique=True):
        '''add a new value

        *Parameters*

        - **value** : new object value
        - **typevalue** : string (default ES.def_clsName) - typevalue to apply to value
        - **unique** :  boolean (default True) - If False, duplication codec if value is present

        *Returns* : key of value '''
        value = util.castval(value, util.typename(self.name, typevalue))
        if value in self._codec and unique:
            key = self._codec.index(value)
        else:
            key = len(self._codec)
            self._codec.append(value)
        self._keys.append(key)
        return key

    def coupling(self, idx, derived=True, duplicate=True):
        '''
        Transform indexes in coupled or derived indexes (codec extension).
        If derived option is True, self._codec is extended and idx codec not,
        else, both are coupled and both codec are extended.

        *Parameters*

        - **idx** : single Iindex or list of Iindex to be coupled or derived.
        - **derived** : boolean (default : True) - if True result is derived,
        if False coupled
        - **duplicate** : boolean (default: True) - if True, return duplicate records

        *Returns* : tuple with duplicate records (errors) if 'duplicate', None else'''
        if not isinstance(idx, list):
            index = [idx]
        else:
            index = idx
        idxzip = self.__class__.ext(list(zip(*([self._keys] + [ix._keys for ix in index]))),
                                    typevalue=None)
        self.tocoupled(idxzip)
        if not derived:
            for ind in index:
                ind.tocoupled(idxzip)
        if duplicate:
            return self.getduplicates()
        return

    def couplinginfos(self, other, default=False):
        '''return a dict with the coupling info between other (distance, rate,
        dist, disttomin, disttomax, distmin, distmax, diff, typecoupl)

        *Parameters*

        - **other** : other index to compare
        - **default** : comparison with default codec

        *Returns* : dict'''
        if default:
            return util.couplinginfos(self.values, other.values)
        if min(len(self), len(other)) == 0:
            return {'dist': 0, 'distrate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': 0, 'distmax': 0, 'diff': 0, 'typecoupl': 'null',
                    'distance': 0, 'rate': 0}
        lens = len(self._codec)
        leno = len(other._codec)
        xmin = max(lens, leno)
        xmax = lens * leno
        diff = abs(lens - leno)
        if min(lens, leno) == 1:
            rate = 0
            if xmax - xmin + diff != 0:
                rate = diff / (xmax - xmin + diff)
            if lens == 1:
                typec = 'derived'
            else:
                typec = 'derive'
            return {'dist': xmin, 'distrate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': xmin, 'distmax': xmax, 'diff': diff,
                    'typecoupl': typec, 'distance': diff, 'rate': rate}
        xso = len(util.tocodec([tuple((v1, v2))
                  for v1, v2 in zip(self._keys, other._keys)]))
        dic = {'dist': xso, 'distrate': (xso - xmin) / (xmax - xmin),
               'disttomin': xso - xmin,  'disttomax': xmax - xso,
               'distmin': xmin, 'distmax': xmax, 'diff': diff,
               'distance': xso - xmin + diff,
               'rate': (xso - xmin + diff) / (xmax - xmin + diff)}
        if dic['distrate'] == 0 and dic['diff'] == 0:
            dic['typecoupl'] = 'coupled'
        elif dic['distrate'] == 0 and lens < leno:
            dic['typecoupl'] = 'derived'
        elif dic['distrate'] == 0 and lens > leno:
            dic['typecoupl'] = 'derive'
        elif dic['distrate'] == 1:
            dic['typecoupl'] = 'crossed'
        elif lens < leno:
            dic['typecoupl'] = 'linked'
        else:
            dic['typecoupl'] = 'link'
        return dic

    def derkeys(self, parent):
        '''return keys derived from parent keys

        *Parameters*

        - **parent** : Iindex - parent

        *Returns* : list of keys'''
        derkey = [ES.nullparent] * len(parent._codec)
        for i in range(len(self)):
            derkey[parent._keys[i]] = self._keys[i]
        if min(derkey) < 0:
            raise IindexError("parent is not a derive Iindex")
        return derkey

    def extendkeys(self, keys):
        '''add keys to the Iindex

        *Parameters*

        - **keys** : list of int (value lower or equal than actual keys)

        *Returns* : None '''
        if min(keys) < 0 or max(keys) > len(self._codec) - 1:
            raise IindexError('keys not consistent with codec')
        self._keys += keys

    @staticmethod
    def full(listidx):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **listidx** : list of Iindex to transform

        *Returns* : tuple of records added '''
        idx1 = listidx[0]
        for idx in listidx:
            if len(idx) != len(idx):
                return None
        leninit = len(idx1)
        keysadd = util.idxfull(listidx)
        for idx, keys in zip(listidx, keysadd):
            idx._keys += keys
        return tuple(range(leninit, len(idx1)))

    def getduplicates(self):
        ''' return tuple of items with duplicate codec'''
        count = Counter(self._codec)
        defcodec = list(count - Counter(list(count)))
        dkeys = defaultdict(list)
        for key, ind in zip(self._keys, range(len(self))):
            dkeys[key].append(ind)
        dcodec = defaultdict(list)
        for key, ind in zip(self._codec, range(len(self._codec))):
            dcodec[key].append(ind)
        duplicates = []
        for item in defcodec:
            for codecitem in dcodec[item]:
                duplicates += dkeys[codecitem]
        return tuple(duplicates)

    def iscrossed(self, other):
        '''return True if self is crossed to other'''
        return self.couplinginfos(other)['distrate'] == 1.0

    def iscoupled(self, other):
        '''return True if self is coupled to other'''
        info = self.couplinginfos(other)
        return info['diff'] == 0 and info['distrate'] == 0

    def isderived(self, other):
        '''return True if self is derived from other'''
        info = self.couplinginfos(other)
        return info['diff'] != 0 and info['distrate'] == 0.0

    def iskeysfromderkeys(self, other):
        '''return True if self._keys is relative from other._keys'''
        leng = len(other._codec)
        if leng % len(self._codec) != 0:
            return False
        keys = [(i*len(self._codec))//leng for i in range(leng)]
        return self.__class__.keysfromderkeys(other._keys, keys) == self._keys

    def islinked(self, other):
        '''return True if self is linked to other'''
        rate = self.couplinginfos(other)['distrate']
        return 0.0 < rate < 1.0

    def isvalue(self, value, extern=True):
        ''' return True if value is in index values

        *Parameters*

        - **value** : value to check
        - **extern** : if True, compare value to external representation of self.value,
        else, internal'''
        if extern:
            return value in self.val
        return value in self.values

    def keytoval(self, key, extern=True):
        ''' return the value of a key

        *Parameters*

        - **key** : key to convert into values
        - **extern** : if True, return string representation else, internal value

        *Returns*

        - **int** : first key finded (None else)'''
        if key < 0 or key >= len(self._codec):
            return None
        if extern:
            return self.cod[key]
        return self._codec[key]

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

        if extern:
            value = util.castval(
                value, util.typename(self.name, ES.def_clsName))
        if not value in self._codec:
            return None
        listkeys = [cod for cod, val in zip(
            range(len(self._codec)), self._codec) if val == value]
        return self.recordfromkeys(listkeys)

    def recordfromkeys(self, listkeys):
        '''return a list of record number with key in listkeys

        *Parameters*

        - **listkeys** : list of keys to check

        *Returns*

        - **list of int** : list of record number finded (None else)'''

        return [rec for rec, key in zip(range(len(self)), self._keys) if key in listkeys]

    def reindex(self, codec=None):
        '''apply a reordered codec. If None, a new default codec is apply.

        *Parameters*

        - **codec** : list (default None) - reordered codec to apply.

        *Returns* : self'''

        if not codec:
            codec = util.tocodec(self.values)
        self._keys = util.reindex(self._keys, self._codec, codec)
        self._codec = codec
        return self

    def reorder(self, sort=None, inplace=True):
        '''Change the Iindex order with a new order define by sort and reset the codec.

        *Parameters*

        - **sort** : int list (default None)- new record order to apply. If None, no change.
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Iindex is created.

        *Returns*

        - **Iindex** : self if inplace, new Iindex if not inplace'''
        values = util.reorder(self.values, sort)
        codec, keys = util.resetidx(values)
        if inplace:
            self._keys = keys
            self._codec = codec
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
        for i in range(len(self._codec)):
            if self._codec[i] == oldvalue:
                if typevalue in ES.ESclassName and nameonly:
                    self._codec[i].setName(newvalue.name)
                elif typevalue in ES.ESclassName and valueonly:
                    self._codec[i].setValue(newvalue.value)
                self._codec[i] = newvalue
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
        if extern:
            listcodec = util.castobj(listcodec, typevalue)
        for i in range(len(self._codec)):
            if typevalue in ES.ESclassName and nameonly:
                self._codec[i].setName(listcodec[i].name)
            elif typevalue in ES.ESclassName and valueonly:
                self._codec[i].setValue(listcodec[i].value)
            else:
                self._codec[i] = listcodec[i]

    def set_keys(self, keys):
        ''' _keys setters '''
        self._keys = keys

    def set_codec(self, codec):
        ''' _codec setters '''
        self._codec = codec

    def setkeys(self, keys, inplace=True):
        '''apply new keys (replace codec with extended codec from parent keys)

        *Parameters*

        - **keys** : list of keys to apply
        - **inplace** : if True, update self data, else create a new Iindex

        *Returns* : self or new Iindex'''
        codec = util.tocodec(self.values, keys)
        if inplace:
            self._codec = codec
            self._keys = keys
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
        if extern:
            value = util.castval(value, typevalue)
        values = self.values
        if typevalue in ES.ESclassName and nameonly:
            values[ind].setName(values.name)
        elif typevalue in ES.ESclassName and valueonly:
            values[ind].setValue(values.value)
        else:
            values[ind] = value
        self._codec, self._keys = util.resetidx(values)

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
        if extern:
            listvalue = util.castobj(listvalue, typevalue)
        values = self.values
        for i, value_i in enumerate(listvalue):
            if typevalue in ES.ESclassName and nameonly:
                values[i].setName(value_i.name)
            elif typevalue in ES.ESclassName and valueonly:
                values[i].setValue(value_i.value)
            else:
                values[i] = value_i
        self._codec, self._keys = util.resetidx(values)

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
            self.reindex(codec=sorted(self._codec, reverse=reverse, key=func))
            self._keys.sort()
            return self
        oldcodec = self._codec
        codec = sorted(oldcodec, reverse=reverse, key=str)
        return self.__class__(name=self.name, codec=codec,
                              keys=sorted(util.reindex(self._keys, oldcodec, codec)))

    def tocoupled(self, other, coupling=True):
        '''
        Transform a derived index in a coupled index (keys extension) and add
        new values to have the same length as other.

        *Parameters*

        - **other** : index to be coupled.
        - **coupling** : boolean (default True) - reindex if False

        *Returns* : None'''
        dic = util.idxlink(other._keys, self._keys)
        if not dic:
            raise IindexError("Iindex is not coupled or derived from other")
        self._codec = [self._codec[dic[i]] for i in range(len(dic))]
        self._keys = other._keys
        if not coupling:
            self.reindex()

    def tostdcodec(self, inplace=False, full=True):
        '''
        Transform codec in full or in default codec.

        *Parameters*

        - **inplace** : boolean (default True) - if True, new order is apply to self,
        - **full** : boolean (default True) - if True reindex with full codec

        *Return*

        - **Iindex** : self if inplace, new Iindex if not inplace'''
        if full:
            codec = self.values
            keys = list(range(len(codec)))
        else:
            codec = util.tocodec(self.values)
            keys = util.reindex(self._keys, self._codec, codec)
        if inplace:
            self._codec = codec
            self._keys = keys
            return self
        return self.__class__(codec=codec, name=self.name, keys=keys, castobj=False)

    def valrow(self, row):
        ''' return json val for a record

        *Parameters*

        - **row** : record to obtain val

        *Returns* : val[row]'''
        val = ESValue.uncastsimple(self._codec[self._keys[row]])
        if isinstance(val, (str, int, float, bool, list, dict, type(None), bytes)):
            return val
        return val.json(encoded=False)

    def valtokey(self, value, extern=True):
        '''convert a value to a key

        *Parameters*

        - **value** : value to convert
        - **extern** : if True, the value has external representation, else internal

        *Returns*

        - **int** : first key finded (None else)'''
        if extern:
            value = util.castval(
                value, util.typename(self.name, ES.def_clsName))
        if value in self._codec:
            return self._codec.index(value)
        return None
