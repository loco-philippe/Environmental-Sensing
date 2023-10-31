# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 11:54:18 2023

@author: phili
"""
from copy import copy

from observation.dataset__analysis import DatasetAnalysis
from observation.util import util
from observation.cfield import Cfield

from json_ntv import Ntv
from json_ntv.ntv_util import NtvUtil, NtvConnector

class Cdataset(DatasetAnalysis):

    field_class = Cfield

    def __init__(self, listidx=None, name=None, reindex=True):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        '''
        if isinstance(listidx, Cdataset):
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.name = listidx.name
            return
        self.name     = name
        self.lindex   = [] if listidx is None else listidx
        if reindex:
            self.reindex()
        return

    def __repr__(self):
        '''return classname, number of value and number of indexes'''
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(self.lenindex) + ']'

    def __str__(self):
        '''return string format for var and lidx'''
        stri = ''
        stri += 'fields :\n'
        for idx in self.lindex:
            stri += '    ' + str(idx) + '\n'
        return stri
    
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

    @classmethod
    def from_ntv(cls, ntv_value, reindex=True, decode_str=False):
        '''Generate an Dataset Object from a ntv_value

        *Parameters*

        - **ntv_value** : bytes, string, Ntv object to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **decode_str**: boolean (default False) - if True, string are loaded in json data'''
        ntv = Ntv.obj(ntv_value, decode_str=decode_str)
        if len(ntv) == 0:
            return cls()
        lidx = [list(NtvUtil.decode_ntv_tab(ntvf, cls.field_class.ntv_to_val)) for ntvf in ntv]
        leng = max([idx[6] for idx in lidx])
        for ind in range(len(lidx)):
            if lidx[ind][0] == '':
                lidx[ind][0] = 'i'+str(ind)
            NtvConnector.init_ntv_keys(ind, lidx, leng)
        lindex = [cls.field_class(idx[2], idx[0], idx[4], None, # idx[1] pour le type,
                     reindex=reindex) for idx in lidx]
        return cls(lindex, reindex=reindex, name=ntv.name)
    
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

    def analys(self, distr=False):
        return {'name': self.name, 'fields': [fld.analysis for fld in self.lindex],
                'length': len(self), 'relations': {
                   self.lindex[i].name: 
                       {self.lindex[j].name: 
                          util.dist(self.lindex[i].keys, self.lindex[j].keys, distr) 
                        for j in range(i+1, len(self.lindex))} 
                   for i in range(len(self.lindex)-1)}}  
    
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

    def check_relationship(self, relations):
        '''get the list of inconsistent records for each relationship defined in relations

         *Parameters*

        - **relations** : list of dict - list of fields with relationship property
        
        *Returns* : dict with for each relationship: key = pair of name, 
        and value = list of inconsistent records'''
        if not isinstance(relations, (list, dict)):
            raise DatasetError("relations is not correct")
        if isinstance(relations, dict):
            relations = [relations]
        dic_res = {}
        for field in relations:
            if not 'relationship' in field or not 'name' in field:
                continue
            if not 'parent' in field['relationship'] or not 'link' in field['relationship']:
                raise DatasetError("relationship is not correct")
            rel = field['relationship']['link']
            f_parent = self.nindex(field['relationship']['parent'])
            f_field = self.nindex(field['name'])
            name_rel = field['name'] + ' - ' + field['relationship']['parent']
            if f_parent is None or f_field is None:
                raise DatasetError("field's name is not present in data")
            match rel:
                case 'derived':
                    dic_res[name_rel] = f_parent.coupling(f_field, reindex=True)                
                case 'coupled':
                    dic_res[name_rel] = f_parent.coupling(f_field, derived=False, reindex=True)    
                case _:
                    raise DatasetError(rel + "is not a valid relationship")
        return dic_res          
    
class DatasetError(Exception):
    ''' Dataset Exception'''
    # pass
