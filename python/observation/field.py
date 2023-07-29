# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: philippe@loco-labs.io

The `python.observation.field` module contains the `Field` class.

Documentation is available in other pages :

- The Json Standard for Field is defined [here](https://github.com/loco-philippe/
Environmental-Sensing/tree/main/documentation/IlistJSON-Standard.pdf)
- The concept of 'indexed list' is described in
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression tests are at [this page](https://github.com/loco-philippe/
Environmental-Sensing/blob/main/python/Tests/test_iindex.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/
python/Examples/Field) are :
    - [creation](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
    python/Examples/Field/Field_creation.ipynb)
    - [value](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
    python/Examples/Field/Field_value.ipynb)
    - [update](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
    python/Examples/Field/Field_update.ipynb)
    - [structure](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
    python/Examples/Field/Field_structure.ipynb)
    - [structure-analysis](https://github.com/loco-philippe/Environmental-Sensing/
    blob/main/python/Examples/Field/Field_structure-analysis.ipynb)

---
"""
# %% declarations
from copy import copy, deepcopy
from abc import ABC, abstractmethod

from observation.esconstante import ES
from observation.field_interface import FieldInterface, FieldError
from observation.field_structure import FieldStructure
from observation.util import util
from json_ntv import Ntv, NtvList



class Field(FieldStructure, FieldInterface, ABC):
    # %% intro
    '''
    An `Field` is a representation of an index list .

    *Attributes (for dynamic attributes see @property methods)* :

    - **name** : name of the Field
    - **codec** : list of values for each key
    - **keys** : list of code values

    The methods defined in this class are :

    *constructor (@classmethod)*

    - `Field.bol`
    - `Field.ntv`
    - `Field.from_parent`
    - `Field.from_ntv`
    - `Field.merging`

    *conversion abstract static methods (@abstractmethod, @staticmethod)*

    - `Field.l_to_i`
    - `Field.s_to_i`
    - `Field.l_to_e`
    - `Field.s_to_e`
    - `Field.i_to_n`
    - `Field.n_to_i`
    - `Field.i_to_name`

    *dynamic value (getters @property)*

    - `Field.values`
    - `Field.val`
    - `Field.cod`
    - `Field.codec`
    - `Field.infos`
    - `Field.keys`

    *add - update methods (`observation.field_structure.FieldStructure`)*

    - `Field.append`
    - `Field.setcodecvalue`
    - `Field.setcodeclist`
    - `Field.setname`
    - `Field.setkeys`
    - `Field.setlistvalue`
    - `Field.setvalue`

    *transform methods (`observation.field_structure.FieldStructure`)*

    - `Field.coupling`
    - `Field.extendkeys`
    - `Field.full`
    - `Field.reindex`
    - `Field.reorder`
    - `Field.sort`
    - `Field.tocoupled`
    - `Field.tostdcodec`

    *getters methods (`observation.field_structure.FieldStructure`)*

    - `Field.couplinginfos`
    - `Field.derkeys`
    - `Field.getduplicates`
    - `Field.iscrossed`
    - `Field.iscoupled`
    - `Field.isderived`
    - `Field.islinked`
    - `Field.isvalue`
    - `Field.iskeysfromderkeys`
    - `Field.keysfromderkeys`
    - `Field.keytoval`
    - `Field.loc`
    - `Field.recordfromkeys`
    - `Field.recordfromvalue`
    - `Field.valtokey`

    *export methods (`observation.field_interface.FieldInterface`)*

    - `Field.json`
    - `Field.to_obj`
    - `Field.to_dict_obj`
    - `Field.to_numpy`
    - `Field.to_pandas`
    - `Field.vlist`
    - `Field.vName`
    - `Field.vSimple`
    '''

    def __init__(self, codec=None, name=None, keys=None,
                 lendefault=0, reindex=False, fast=False):
        '''
        Field constructor.

        *Parameters*

        - **codec** :  list (default None) - external different values of index (see data model)
        - **keys** :  list (default None)  - key value of index (see data model)
        - **name** : string (default None) - name of index (see data model)
        - **lendefault** : integer (default 0) - default len if no keys is defined
        - **reindex** : boolean (default True) - if True, default codec is apply
        - **fast**: boolean (default False) - if True, codec is created without conversion'''
        if isinstance(codec, Field):
            self._keys = copy(codec._keys)
            self._codec = deepcopy(codec._codec)
            self.name = copy(codec.name)
            return
        if codec is None:
            codec = []
        if not isinstance(codec, list):
            codec = [codec]
        codec = list(codec)
        leng = lendefault
        if codec and len(codec) > 0 and not leng:
            leng = len(codec)
        if not keys is None:
            leng = len(keys)
        if not name:
            name = ES.defaultindex
        if not (keys is None or isinstance(keys, list)):
            raise FieldError("keys not list")
        if keys is None and leng == 0:
            keys = []
        elif keys is None:
            keys = [(i*len(codec))//leng for i in range(leng)]
        if not isinstance(codec, list):
            raise FieldError("codec not list")
        if codec == []:
            keysset = util.tocodec(keys)
            #codec = [Ntv.obj(key) for key in keysset]
            codec = self.l_to_i(keysset, fast=True)
        codec = self.l_to_i(codec, fast=fast)
        self._keys = keys
        self._codec = codec
        self.name = name
        if reindex:
            self.reindex()

    @classmethod
    def bol(cls, leng, notdef=None, name=None, default=True):
        '''
        Field constructor (boolean value).

        *Parameters*

        - **leng** : integer - length of the Field
        - **notdef** : list (default None) - list of records without default value
        - **default** : boolean (default True) - default value
        - **name** : string (default None) - name of Field'''
        values = [default] * leng
        if notdef:
            for item in notdef:
                values[item] = not default        
        return cls.ntv({name: values})
        
    @classmethod
    def from_parent(cls, codec, parent, name=None, reindex=False):
        '''Generate an Field Object from specific codec and parent keys.

        *Parameters*

        - **codec** : list of objects
        - **name** : string (default None) - name of index (see data model)
        - **parent** : Field, parent of the new Field
        - **reindex** : boolean (default True) - if True, default codec is apply

        *Returns* : Field '''
        if isinstance(codec, Field):
            return copy(codec)
        return cls(codec=codec, name=name, keys=parent._keys, reindex=reindex)

    @classmethod 
    def ntv(cls, ntv_value=None, extkeys=None, reindex=True, decode_str=False):
        '''Generate an Field Object from a Ntv field object'''
        return cls.from_ntv(ntv_value, extkeys=extkeys, reindex=reindex, decode_str=decode_str)
    
    @classmethod 
    def from_ntv(cls, ntv_value=None, extkeys=None, reindex=True, decode_str=False,
                 add_type=True, lengkeys=None):
        '''Generate an Field Object from a Ntv field object'''
        if isinstance(ntv_value, cls):
            return copy(ntv_value)
        ntv = Ntv.obj(ntv_value, decode_str=decode_str)
        #ntv = NtvList(ntv_value)
        if ntv_value is None:
            return cls()
        name, typ, codec, parent, keys, coef, leng = cls.decode_ntv(ntv)
        if parent and not extkeys:
            return None
        if coef:
            keys = FieldInterface.keysfromcoef(coef, leng//coef, lengkeys)
        elif extkeys and parent:
            keys = cls.keysfromderkeys(extkeys, keys)
        elif extkeys and not parent:
            keys = extkeys
        keys = list(range(len(codec))) if keys is None else keys
        name = ntv.json_name(string=True) if add_type else name
        return cls(codec=codec, name=name, keys=keys, reindex=reindex)

    """@classmethod
    def from_dict_obj(cls, bsd, typevalue=ES.def_clsName, reindex=False):
        '''Generate an Field Object from a dict value'''
        var = False
        if not isinstance(bsd, dict):
            raise FieldError('data is not a dict')
        name = list(bsd.keys())[0]
        bsdv = list(bsd.values())[0]
        if not 'value' in bsdv:
            raise FieldError('value is not present')
        value = bsdv['value']
        if not isinstance(value, list):
            value = [value]
        if 'type' in bsdv and isinstance(bsdv['type'], str):
            typevalue = bsdv['type']
        if 'var' in bsdv and isinstance(bsdv['var'], bool):
            var = bsdv['var']
        codec = [util.castval(val['codec'], typevalue) for val in value]
        pairs = []
        for i, rec in enumerate(value):
            record = rec['record']
            if not isinstance(record, list):
                record = [record]
            for j in record:
                pairs.append((j, i))
        if not pairs:
            return (var, cls())
        keys = list(list(zip(*sorted(pairs)))[1])

        idx = cls(name=name, codec=codec, keys=keys, typevalue=None)
        return (var, idx)"""

    @classmethod
    def merging(cls, listidx, name=None):
        '''Create a new Field with values are tuples of listidx Field values

        *Parameters*

        - **listidx** : list of Field to be merged.
        - **name** : string (default : None) - Name of the new Field

        *Returns* : new Field'''
        if not name:
            name = str(list({idx.name for idx in listidx}))
        values = util.transpose([idx.values for idx in listidx])
        return cls.ntv({name: values})


# %% abstract
    @staticmethod    
    @abstractmethod
    def l_to_i(lis):
        ''' converting a list of external values to a list of internal values'''
        pass

    @staticmethod
    @abstractmethod
    def s_to_i(val):
        '''converting an external value to an internal value'''
        pass 

    @staticmethod
    @abstractmethod
    def n_to_i(ntv):
        ''' converting a NTV value to an internal value'''
        pass 

    @staticmethod
    @abstractmethod
    def l_to_e(lis):
        ''' converting a list of internal values to a list of external values'''
        pass 

    @staticmethod
    @abstractmethod
    def s_to_e(val):
        '''converting an internal value to an external value'''
        pass 

    @staticmethod
    @abstractmethod
    def i_to_n(val):
        ''' converting an internal value to a NTV value'''
        pass 

    @staticmethod
    @abstractmethod
    def i_to_name(val):
        ''' return the name of the internal value'''
        pass 
# %% special

    def __repr__(self):
        '''return classname and number of value'''
        return self.__class__.__name__ + '[' + str(len(self)) + ']'

    def __eq__(self, other):
        ''' equal if class and values are equal'''
        return self.__class__ .__name__ == other.__class__.__name__ and self.values == other.values

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

    def __copy__(self):
        ''' Copy all the data '''
        return self.__class__(self)

# %% property
    @property
    def cod(self):
        '''return codec conversion to json value '''
        return self.l_to_e(self._codec)
        #return [codec.to_obj() for codec in self._codec]
        #return [codec.ntv_value for codec in self._codec]
        #return self.to_ntv(codecval=True).ntv_value
        #return self.to_obj(modecodec='optimize', codecval=True, encoded=False, listunic=True)

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

    @property
    def val(self):
        '''return values conversion to string '''
        return [self.s_to_e(self._codec[key]) for key in self._keys]
        #return [self._codec[key].to_obj() for key in self._keys]
        #return self.to_obj(modecodec='full', codecval=True, encoded=False)