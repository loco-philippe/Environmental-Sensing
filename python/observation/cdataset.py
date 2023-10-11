# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:54:18 2023

@author: phili
"""
from observation.dataset_interface import DatasetError
from observation.util import util

class Cdataset:

    def __init__(self, listidx=None, name=None):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        '''

        self.name     = name
        self.lindex   = [] if listidx is None else listidx

    def __repr__(self):
        '''return classname, number of value and number of indexes'''
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(self.lenindex) + ']'

    def __len__(self):
        ''' len of values'''
        if not self.lindex:
            return 0
        return len(self.lindex[0])

    def __contains__(self, item):
        ''' list of lindex values'''
        return item in self.lindex

    def __getitem__(self, ind):
        ''' return value record (value conversion)'''
        res = [idx[ind] for idx in self.lindex]
        if len(res) == 1:
            return res[0]
        return res

    def __setitem__(self, ind, item):
        ''' modify the Field values for each Field at the row ind'''
        if not isinstance(item, list):
            item = [item]
        for val, idx in zip(item, self.lindex):
            idx[ind] = val

    def __delitem__(self, ind):
        ''' remove all Field item at the row ind'''
        for idx in self.lindex:
            del idx[ind]

    def __hash__(self):
        '''return sum of all hash(Field)'''
        return sum([hash(idx) for idx in self.lindex])

    def _hashi(self):
        '''return sum of all hashi(Field)'''
        return sum([idx._hashi() for idx in self.lindex])

    def __eq__(self, other):
        ''' equal if hash values are equal'''
        return hash(self) == hash(other)

    def __copy__(self):
        ''' Copy all the data '''
        return self.__class__(self)

# %% property
    @property
    def indexlen(self):
        ''' list of index codec length'''
        return [len(idx.codec) for idx in self.lindex]

    @property
    def iindex(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def keys(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def lenindex(self):
        ''' number of indexes'''
        return len(self.lindex)

    @property
    def lunicname(self):
        ''' list of unique index name'''
        return [idx.name for idx in self.lindex if len(idx.codec) == 1]

    @property
    def lunicrow(self):
        '''list of unic idx row'''
        return [self.lname.index(name) for name in self.lunicname]

    @property
    def lname(self):
        ''' list of index name'''
        return [idx.name for idx in self.lindex]

    @property
    def tiindex(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iindex)))

# %%methods

    def add(self, other, name=False, solve=True):
        ''' Add other's values to self's values for each index

        *Parameters*

        - **other** : Dataset object to add to self object
        - **name** : Boolean (default False) - Add values with same index name (True) or
        same index row (False)
        - **solve** : Boolean (default True) - If True, replace None other's codec value
        with self codec value.

        *Returns* : self '''
        if self.lenindex != other.lenindex:
            raise DatasetError('length are not identical')
        if name and sorted(self.lname) != sorted(other.lname):
            raise DatasetError('name are not identical')
        for i in range(self.lenindex):
            if name:
                self.lindex[i].add(other.lindex[other.lname.index(self.lname[i])],
                                   solve=solve)
            else:
                self.lindex[i].add(other.lindex[i], solve=solve)
        return self

    def reindex(self):
        '''Calculate a new default codec for each index (Return self)'''
        for idx in self.lindex:
            idx.reindex()
        return self

    def delindex(self, delname=None, savename=None):
        '''remove an Field or a list of Field.

        *Parameters*

        - **delname** : string or list of string - name of index to remove
        - **savename** : string or list of string - name of index to keep

        *Returns* : none '''
        if not delname and not savename :
            return
        if isinstance(delname, str):
            delname = [delname]
        if isinstance(savename, str):
            savename = [savename]
        if delname and savename:
            delname = [name for name in delname if not name in savename]
        if not delname:
            delname = [name for name in self.lname if not name in savename]
        for idxname in delname:
            if idxname in self.lname:
                self.lindex.pop(self.lname.index(idxname))

    def nindex(self, name):
        ''' index with name equal to attribute name'''
        if name in self.lname:
            return self.lindex[self.lname.index(name)]
        return None

    def renameindex(self, oldname, newname):
        '''replace an index name 'oldname' by a new one 'newname'. '''
        for i in range(self.lenindex):
            if self.lname[i] == oldname:
                self.lindex[i].setname(newname)
        for i in range(len(self.lvarname)):
            if self.lvarname[i] == oldname:
                self.lvarname[i] = newname

    def reorder(self, recorder=None):
        '''Reorder records in the order define by 'recorder' '''
        if recorder is None or set(recorder) != set(range(len(self))):
            return None
        for idx in self.lindex:
            idx.set_keys([idx.keys[i] for i in recorder])
        return None

    def setname(self, listname=None):
        '''Update Field name by the name in listname'''
        for i in range(min(self.lenindex, len(listname))):
            self.lindex[i].name = listname[i]

    def swapindex(self, order):
        '''
        Change the order of the index .

        *Parameters*

        - **order** : list of int or list of name - new order of index to apply.

        *Returns* : self '''
        if self.lenindex != len(order):
            raise DatasetError('length of order and Dataset different')
        if not order or isinstance(order[0], int):
            self.lindex = [self.lindex[ind] for ind in order]
        elif isinstance(order[0], str):
            self.lindex = [self.nindex(name) for name in order]
        return self
