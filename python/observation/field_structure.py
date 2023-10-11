# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `python.observation.field_structure` module contains the `FieldStructure` class
(`python.observation.field.Field` methods).
"""
from observation.cfield import Cfield

class FieldStructure(Cfield):
    '''this class includes Field methods :

    *add - update methods*

    - `FieldStructure.append`
    - `FieldStructure.setcodecvalue`
    - `FieldStructure.setcodeclist`
    - `FieldStructure.setname`
    - `FieldStructure.setkeys`
    - `FieldStructure.setlistvalue`
    - `FieldStructure.setvalue`

    *transform methods*

    - `FieldStructure.coupling`
    - `FieldStructure.extendkeys`
    - `FieldStructure.full`
    - `FieldStructure.reindex`
    - `FieldStructure.reorder`
    - `FieldStructure.sort`
    - `FieldStructure.tocoupled`
    - `FieldStructure.tostdcodec`

    *getters methods*

    - `FieldStructure.couplinginfos`
    - `FieldStructure.derkeys`
    - `FieldStructure.getduplicates`
    - `FieldStructure.iscrossed`
    - `FieldStructure.iscoupled`
    - `FieldStructure.isderived`
    - `FieldStructure.islinked`
    - `FieldStructure.isvalue`
    - `FieldStructure.iskeysfromderkeys`
    - `FieldStructure.keysfromderkeys`
    - `FieldStructure.keytoval`
    - `FieldStructure.loc`
    - `FieldStructure.recordfromkeys`
    - `FieldStructure.recordfromvalue`
    - `FieldStructure.valtokey`  '''

    def append(self, value, unique=True):
        '''add a new value

        *Parameters*

        - **value** : new object value
        - **unique** :  boolean (default True) - If False, duplication codec if value is present

        *Returns* : key of value '''
        return super().append(self.s_to_i(value), unique)

    def isvalue(self, value, extern=True):
        ''' return True if value is in index values

        *Parameters*

        - **value** : value to check
        - **extern** : if True, compare value to external representation of self.value,
        else, internal'''
        if extern:
            return value in self.val
        return super().isvalue(value)

    def keytoval(self, key, extern=True):
        ''' return the value of a key

        *Parameters*

        - **key** : key to convert into values
        - **extern** : if True, return string representation else, internal value

        *Returns*

        - **int** : first key finded (None else)'''
        if extern:
            return self.s_to_e(super().keytoval(key))
        return super().keytoval(key)

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
            return super().recordfromvalue(self.s_to_i(value))
        return super().recordfromvalue(value)

    def setcodecvalue(self, oldvalue, newvalue, extern=True,
                      nameonly=False, valueonly=False):
        '''update all the oldvalue by newvalue

        *Parameters*

        - **oldvalue** : list of values to replace
        - **newvalue** : list of new value to apply
        - **extern** : if True, the newvalue has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : int - last codec rank updated (-1 if None)'''
        if extern:
            return super().setcodecvalue(self.s_to_i(oldvalue), self.s_to_i(newvalue),
                                         nameonly, valueonly)
        return super().setcodecvalue(oldvalue, newvalue, nameonly, valueonly)

    def setcodeclist(self, listcodec, extern=True, nameonly=False, valueonly=False):
        '''update codec with listcodec values

        *Parameters*

        - **listcodec** : list of new codec values to apply
        - **extern** : if True, the newvalue has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : int - last codec rank updated (-1 if None)'''
        if extern:
            super().setcodeclist(self.l_to_i(listcodec), nameonly, valueonly)
        super().setcodeclist(listcodec, nameonly, valueonly)

    def setvalue(self, ind, value, extern=True, nameonly=False, valueonly=False):
        '''update a value at the rank ind (and update codec and keys)

        *Parameters*

        - **ind** : rank of the value
        - **value** : new value
        - **extern** : if True, the value has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : None'''
        if extern:
            super().setvalue(ind, self.s_to_i(value), nameonly, valueonly)
        else:
            super().setvalue(ind, value, nameonly, valueonly)

    def setlistvalue(self, listvalue, extern=True, nameonly=False, valueonly=False):
        '''update the values (and update codec and keys)

        *Parameters*

        - **listvalue** : list - list of new values
        - **extern** : if True, the value has external representation, else internal
        - **nameonly** : if True, only the name of ESValue is changed
        - **valueonly** : if True, only the value of ESValue is changed

        *Returns* : None'''
        if extern:
            super().setlistvalue(self.l_to_i(listvalue), nameonly, valueonly)
        else:
            super().setlistvalue(listvalue, nameonly, valueonly)

    def valtokey(self, value, extern=True):
        '''convert a value to a key

        *Parameters*

        - **value** : value to convert
        - **extern** : if True, the value has external representation, else internal

        *Returns*

        - **int** : first key finded (None else)'''
        if extern:
            return super().valtokey(self.s_to_i(value))
        return super().valtokey(value)
