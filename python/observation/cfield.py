# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 22:26:38 2023

@author: a lab in the Air
"""

from copy import copy, deepcopy
from collections import defaultdict, Counter

from observation.util import util
from observation.esconstante import ES
from observation.field_interface import FieldError

@staticmethod 
def root(leng):
    return Cfield(Cutil.identity(leng), 'root')
    
class Cutil:
    
    @staticmethod
    def identity(leng):
        return list(range(leng))

    @staticmethod 
    def default(values):
        codec = list(dict.fromkeys(values))
        dic = {codec[i]: i for i in range(len(codec))}
        keys = [dic[val] for val in values]
        return (codec, keys)

    @staticmethod
    def dist(key1, key2):
        return len(util.tocodec([tuple((v1, v2)) for v1, v2 in zip(key1, key2)]))

class Cfield:
    # %% intro
    '''
    '''
    def __init__(self, codec, name=None, keys=None, default=False):
        '''Two modes:
            - a single attributes : Cfield object to copy
            - multiple attributes : set codec, name and keys attributes'''
        if isinstance(codec, Cfield):
            self._keys = codec._keys
            self._codec = codec._codec
            self.name = codec.name
        if not default: 
            self._keys = keys if keys else Cutil.identity(len(codec))
            #self._keys = keys if keys else list(range(len(codec)))
            self._codec = codec if codec else Cutil.identity(len(keys))
            #self._codec = codec if codec else list(range(len(keys)))
        else:
            self._codec, self._keys = Cutil.default(codec)
        self.name = name if name else 'field'
        
    def __repr__(self):
        '''return classname and number of value'''
        return self.__class__.__name__ + '[' + str(len(self)) + ']'
    
    def __eq__(self, other):
        ''' equal if class and values are equal'''
        return self.__class__ .__name__ == other.__class__.__name__ and \
               self.values == other.values

    def __len__(self):
        ''' len of values'''
        return len(self._keys)
    
    def __contains__(self, item):
        ''' item of values'''
        return item in self.values

    def __getitem__(self, ind):
        ''' return value item (value conversion)'''
        if isinstance(ind, tuple):
            return [copy(self.values[i]) for i in ind]
        #return self.values[ind]
        return copy(self.values[ind])
    
    def __setitem__(self, ind, value):
        ''' modify values item'''
        if ind < 0 or ind >= len(self):
            raise FieldError("out of bounds")
        self.setvalue(ind, value, extern=True)

    def __delitem__(self, ind):
        '''remove a record (value and key).'''
        self._keys.pop(ind)
        self.reindex()

    def __hash__(self):
        '''return hash(values)'''
        return hash(tuple(self.values))

    def _hashe(self):
        '''return hash(values)'''
        return hash(tuple(self.values))

    def _hashi(self):
        '''return hash(codec) + hash(keys)'''
        return hash(tuple(self._codec)) + hash(tuple(self._keys))

    def __add__(self, other):
        ''' Add other's values to self's values in a new Field'''
        newiindex = self.__copy__()
        newiindex.__iadd__(other)
        return newiindex

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        return self.add(other, solve=False)
    
    def __copy__(self):
        ''' Copy all the data '''
        return self.__class__(self)
    
    # %% property
    @property 
    def analysis(self):
        return { 'id': self.name, 'lencodec': len(self.codec), 
                 'mincodec': len(set(self.codec)), 'maxcodec': len(self),
                 'hashf': hash(self)}
    
    @property
    def codec(self):
        '''return codec  '''
        return self._codec

    @property
    def infos(self):
        '''return dict with lencodec, typecodec, ratecodec, mincodec, maxcodec'''
        maxi = len(self)
        mini = len(set(self._codec))
        xlen = len(self._codec)
        rate = 0.0
        if maxi == 0:
            typecodec = 'null'
        elif xlen == 1:
            typecodec = 'unique'
        elif mini == maxi:
            typecodec = 'complete'
        elif xlen == maxi:
            typecodec = 'full'
        else:
            rate = (maxi - xlen) / (maxi - mini)
            if xlen == mini:
                typecodec = 'default'
            else:
                typecodec = 'mixed'
        return {'lencodec': xlen, 'mincodec': mini, 'maxcodec': maxi,
                'typecodec': typecodec, 'ratecodec': rate}

    @property
    def keys(self):
        '''return keys  '''
        return self._keys

    @property
    def values(self):
        '''return values (see data model)'''
        return [self._codec[key] for key in self._keys]
    
    # %% methods
    def add(self, other, solve=True):
        ''' Add other's values to self's values

        *Parameters*

        - **other** : Field object to add to self object
        - **solve** : Boolean (default True) - If True, replace None other's codec value
        with self codec value.

        *Returns* : self '''
        if solve:
            solved = copy(other)
            for i in range(len(solved._codec)):
                if not util.isNotNull(solved._codec[i]) and i in range(len(self._codec)):
                    solved._codec[i] = self._codec[i]
            values = self.values + solved.values
        else:
            values = self.values + other.values
        codec = util.tocodec(values)
        if set(codec) != set(self._codec):
            self._codec = codec
        self._keys = util.tokeys(values, self._codec)
        return self

    def append(self, value, unique=True):
        '''add a new value

        *Parameters*

        - **value** : new object value
        - **unique** :  boolean (default True) - If False, duplication codec if value is present

        *Returns* : key of value '''
        #value = Ntv.obj(value)
        #value = self.s_to_i(value)
        if value in self._codec and unique:
            key = self._codec.index(value)
        else:
            key = len(self._codec)
            self._codec.append(value)
        self._keys.append(key)
        return key

    def coupling(self, idx, derived=True, duplicate=True, reindex=False):
        '''
        Transform indexes in coupled or derived indexes (codec extension).
        If derived option is True, self._codec is extended and idx codec not,
        else, both are coupled and both codec are extended.

        *Parameters*

        - **idx** : single Field or list of Field to be coupled or derived.
        - **derived** : boolean (default : True) - if True result is derived,
        if False coupled
        - **duplicate** : boolean (default: True) - if True, return duplicate records 
        (only for self index)
        - **reindex** : boolean (default : False). If True self.index is reindexed 
        with default codec. But if not derived, idx indexes MUST to be reindexed.

        *Returns* : tuple with duplicate records (errors) if 'duplicate', None else'''
        if not isinstance(idx, list):
            index = [idx]
        else:
            index = idx
        idxzip = self.__class__(list(zip(*([self._keys] + [ix._keys for ix in index]))),
                                reindex=True)
        self.tocoupled(idxzip)
        if not derived:
            for ind in index:
                ind.tocoupled(idxzip)
        if duplicate:
            return self.getduplicates(reindex)
        if reindex:
            self.reindex()
        return    

    def couplinginfos(self, other, default=False):
        '''return a dict with the coupling info between other (distance, ratecpl,
        rateder, dist, disttomin, disttomax, distmin, distmax, diff, typecoupl)

        *Parameters*

        - **other** : other index to compare
        - **default** : comparison with default codec

        *Returns* : dict'''
        if default:
            return util.couplinginfos(self.values, other.values)
        if min(len(self), len(other)) == 0:
            return {'dist': 0, 'rateder': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': 0, 'distmax': 0, 'diff': 0, 'typecoupl': 'null',
                    'distance': 0, 'ratecpl': 0}
        xs = len(self._codec)         # xs
        xo = len(other._codec)        # xo
        dmin = max(xs, xo)          # dmin
        dmax = xs * xo              # dmax
        diff = abs(xs - xo)         # diff
        if min(xs, xo) == 1:
            ratecpl = 0
            if dmax - dmin + diff != 0:
                ratecpl = diff / (dmax - dmin + diff)  # 
            if xs == 1:
                typec = 'derived'
            else:
                typec = 'derive'
            return {'dist': dmin, 'rateder': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': dmin, 'distmax': dmax, 'diff': diff,
                    'typecoupl': typec, 'distance': diff, 'ratecpl': ratecpl}
        xso = len(util.tocodec([tuple((v1, v2))     # xab
                  for v1, v2 in zip(self._keys, other._keys)]))
        dic = {'dist': xso, 'distmin': dmin, 'distmax': dmax, 'diff': diff,
               'rateder': (xso - dmin) / (dmax - dmin),            # rateDer
               'disttomin': xso - dmin,  
               'disttomax': dmax - xso,        
               'distance': xso - dmin + diff,
               'ratecpl': (xso - dmin + diff) / (dmax - dmin + diff)}  #rateCpl
        if dic['rateder'] == 0 and dic['diff'] == 0:
            dic['typecoupl'] = 'coupled'
        elif dic['rateder'] == 0 and xs < xo:
            dic['typecoupl'] = 'derived'
        elif dic['rateder'] == 0 and xs > xo:
            dic['typecoupl'] = 'derive'
        elif dic['rateder'] == 1:
            dic['typecoupl'] = 'crossed'
        elif xs < xo:
            dic['typecoupl'] = 'linked'
        else:
            dic['typecoupl'] = 'link'
        return dic
    
    def dist(self, other):
        '''return default coupling codec between two Cfield'''
        return util.dist(self._keys, other._keys)

    def derkeys(self, parent):
        '''return keys derived from parent keys

        *Parameters*

        - **parent** : Field - parent

        *Returns* : list of keys'''
        derkey = [ES.nullparent] * len(parent._codec)
        for i in range(len(self)):
            derkey[parent._keys[i]] = self._keys[i]
        if min(derkey) < 0:
            raise FieldError("parent is not a derive Field")
        return derkey    
    
    def extendkeys(self, keys):
        '''add keys to the Field

        *Parameters*

        - **keys** : list of int (value lower or equal than actual keys)

        *Returns* : None '''
        if min(keys) < 0 or max(keys) > len(self._codec) - 1:
            raise FieldError('keys not consistent with codec')
        self._keys += keys

    @staticmethod
    def full(listidx):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **listidx** : list of Field to transform

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

    def getduplicates(self, reindex=False):
        ''' calculate items with duplicate codec

        *Parameters*

        - **reindex** : boolean (default : False). If True index is reindexed with default codec
        
        *Returns* : tuple of items with duplicate codec'''
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
        if reindex:
            self.reindex()
        return tuple(duplicates)    
    
    def iscrossed(self, other):
        '''return True if self is crossed to other'''
        return self.couplinginfos(other)['rateder'] == 1.0

    def iscoupled(self, other):
        '''return True if self is coupled to other'''
        info = self.couplinginfos(other)
        return info['diff'] == 0 and info['rateder'] == 0

    def isderived(self, other):
        '''return True if self is derived from other'''
        info = self.couplinginfos(other)
        return info['diff'] != 0 and info['rateder'] == 0.0

    def iskeysfromderkeys(self, other):
        '''return True if self._keys is relative from other._keys'''
        leng = len(other._codec)
        if leng % len(self._codec) != 0:
            return False
        keys = [(i*len(self._codec))//leng for i in range(leng)]
        return self.__class__.keysfromderkeys(other._keys, keys) == self._keys

    def islinked(self, other):
        '''return True if self is linked to other'''
        rate = self.couplinginfos(other)['rateder']
        return 0.0 < rate < 1.0    

    def isvalue(self, value):
        ''' return True if value is in index values

        *Parameters*

        - **value** : value to check'''
        return value in self.values

    def keytoval(self, key):
        ''' return the value of a key

        *Parameters*

        - **key** : key to convert into values
        - **extern** : if True, return string representation else, internal value

        *Returns*

        - **int** : first key finded (None else)'''
        if key < 0 or key >= len(self._codec):
            return None
        return self._codec[key]    
    
    @staticmethod
    def keysfromderkeys(parentkeys, derkeys):
        '''return keys from parent keys and derkeys

        *Parameters*

        - **parentkeys** : list of keys from parent
        - **derkeys** : list of derived keys

        *Returns* : list of keys'''
        #return [derkeys[parentkeys[i]] for i in range(len(parentkeys))]
        return [derkeys[pkey] for pkey in parentkeys]
    
    def loc(self, value):
        '''return a list of record number with value

        *Parameters*

        - **value** : value to check

        *Returns*

        - **list of int** : list of record number finded (None else)'''
        return self.recordfromvalue(value)    
    
    def recordfromvalue(self, value):
        '''return a list of record number with value

        *Parameters*

        - **value** : value to check
        - **extern** : if True, compare value to external representation of self.value,
        else, internal

        *Returns*

        - **list of int** : list of record number finded (None else)'''

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
        '''Change the Field order with a new order define by sort and reset the codec.

        *Parameters*

        - **sort** : int list (default None)- new record order to apply. If None, no change.
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Field is created.

        *Returns*

        - **Field** : self if inplace, new Field if not inplace'''
        values = util.reorder(self.values, sort)
        codec, keys = util.resetidx(values)
        if inplace:
            self._keys = keys
            self._codec = codec
            return None
        return self.__class__(name=self.name, codec=codec, keys=keys)
    
    def setcodecvalue(self, oldvalue, newvalue, nameonly=False, valueonly=False):
        '''update all the oldvalue by newvalue

        *Parameters*

        - **oldvalue** : list of values to replace
        - **newvalue** : list of new value to apply
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : int - last codec rank updated (-1 if None)'''

        rank = -1
        for i in range(len(self._codec)):
            if self._codec[i] == oldvalue:
                if nameonly:
                    self._codec[i].setName(newvalue.ntv_name)
                elif valueonly:
                    self._codec[i].setValue(newvalue.ntv_value)
                else:
                    self._codec[i] = newvalue
                rank = i
        return rank
    
    def setcodeclist(self, listcodec, nameonly=False, valueonly=False):
        '''update codec with listcodec values

        *Parameters*

        - **listcodec** : list of new codec values to apply
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : int - last codec rank updated (-1 if None)'''
        self._codec = listcodec

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
        - **inplace** : if True, update self data, else create a new Field

        *Returns* : self or new Field'''
        codec = util.tocodec(self.values, keys)
        if inplace:
            self._codec = codec
            self._keys = keys
            return self
        return self.__class__(codec=codec, name=self.name, keys=keys)

    def setname(self, name):
        '''update the Field name

        *Parameters*

        - **name** : str to set into name

        *Returns* : boolean - True if update'''
        if isinstance(name, str):
            self.name = name
            return True
        return False    
    
    def setvalue(self, ind, value, nameonly=False, valueonly=False):
        '''update a value at the rank ind (and update codec and keys)

        *Parameters*

        - **ind** : rank of the value
        - **value** : new value
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : None'''
        values = self.values
        if nameonly:
            values[ind].setName(values.ntv_name)
        elif valueonly:
            values[ind].setValue(values.ntv_value)
        else:
            values[ind] = value
        self._codec, self._keys = util.resetidx(values)

    def setlistvalue(self, listvalue, nameonly=False, valueonly=False):
        '''update the values (and update codec and keys)

        *Parameters*

        - **listvalue** : list - list of new values
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : None'''
        values = self.values
        for i, value_i in enumerate(listvalue):
            if nameonly:
                values[i].setName(value_i.ntv_name)
            elif valueonly:
                values[i].setValue(value_i.ntv_value)
            else:
                values[i] = value_i
        self._codec, self._keys = util.resetidx(values)
    
    def sort(self, reverse=False, inplace=True, func=str):
        '''Define sorted index with ordered codec.

        *Parameters*

        - **reverse** : boolean (defaut False) - codec is sorted with reverse order
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Field is created.
        - **func**    : function (default str) - key used in the sorted function

        *Return*

        - **Field** : self if inplace, new Field if not inplace'''
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
            raise FieldError("Field is not coupled or derived from other")
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

        - **Field** : self if inplace, new Field if not inplace'''
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
        return self.__class__(codec=codec, name=self.name, keys=keys)
    
    def valtokey(self, value):
        '''convert a value to a key

        *Parameters*

        - **value** : value to convert

        *Returns*

        - **int** : first key finded (None else)'''
        if value in self._codec:
            return self._codec.index(value)
        return None    
    
    
    