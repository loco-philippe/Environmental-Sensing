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
#from json_ntv import Ntv, NtvList

from observation.cfield import Cfield



class Field(FieldStructure, FieldInterface, ABC, Cfield):
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
    - `Field.ntv_to_val`
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
            Cfield.__init__(self, deepcopy(codec._codec), copy(codec.name), copy(codec._keys))
            return
        if codec is None:
            codec = []
        if not isinstance(codec, list):
            codec = [codec]
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
        if codec == []:
            keysset = util.tocodec(keys)
            codec = self.l_to_i(keysset, fast=True)
        codec = self.l_to_i(codec, fast=fast)
        Cfield.__init__(self, codec, name, keys, reindex=reindex)

    def __setitem__(self, ind, value):
        ''' modify values item'''
        if ind < 0 or ind >= len(self):
            raise FieldError("out of bounds")
        self.setvalue(ind, value, extern=True)
        
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
    def ntv_to_val(cls, ntv):
        '''conversion in decode_ntv_tab'''
        return cls.n_to_i(ntv.val)    

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

# %% property
    @property
    def cod(self):
        '''return codec conversion to json value '''
        return self.l_to_e(self._codec)


    @property
    def val(self):
        '''return values conversion to string '''
        return [self.s_to_e(self._codec[key]) for key in self._keys]

