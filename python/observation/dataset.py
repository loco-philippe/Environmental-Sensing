# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: philippe@loco-labs.io

The `python.observation.dataset` module contains the `Dataset` class.

Documentation is available in other pages :

- The Json Standard for Dataset is define
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/DatasetJSON-Standard.pdf)
- The concept of 'indexed list' is describe in
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression test are at
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_dataset.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples/Dataset)
 are :
    - [creation](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Dataset/Dataset_creation.ipynb)
    - [variable](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Dataset/Dataset_variable.ipynb)
    - [update](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Dataset/Dataset_update.ipynb)
    - [structure](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Dataset/Dataset_structure.ipynb)
    - [structure-analysis](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Dataset/Dataset_structure-analysis.ipynb)

---
"""
# %% declarations
from collections import Counter
from copy import copy
from abc import ABC
import math
import json
import csv


from observation.util import util
from observation.dataset_interface import DatasetInterface
from observation.dataset_structure import DatasetStructure
from observation.dataset_analysis import Analysis

from json_ntv.ntv import Ntv, NtvConnector
from json_ntv.ntv_util import NtvUtil
from tab_analysis import Util

from observation.cdataset import Cdataset, DatasetError

class Dataset(DatasetStructure, DatasetInterface, ABC, Cdataset):
    # %% intro
    '''
    An `Dataset` is a representation of an indexed list.

    *Attributes (for @property see methods)* :

    - **lindex** : list of Field
    - **analysis** : Analysis object (data structure)

    The methods defined in this class are :

    *constructor (@classmethod))*

    - `Dataset.ntv`
    - `Dataset.from_csv`
    - `Dataset.from_ntv`
    - `Dataset.from_file`
    - `Dataset.merge`

    *abstract static methods (@abstractmethod, @staticmethod)*

    - `Dataset.field_class`
    
    *dynamic value - module analysis (getters @property)*

    - `Dataset.extidx`
    - `Dataset.extidxext`
    - `Dataset.groups`
    - `Dataset.idxname`
    - `Dataset.idxlen`
    - `Dataset.iidx`
    - `Dataset.lenidx`
    - `Dataset.lidx`
    - `Dataset.lidxrow`
    - `Dataset.lisvar`
    - `Dataset.lvar`
    - `Dataset.lvarname`
    - `Dataset.lvarrow`
    - `Dataset.lunicname`
    - `Dataset.lunicrow`
    - `Dataset.primaryname`
    - `Dataset.setidx`
    - `Dataset.zip`

    *dynamic value (getters @property)*

    - `Dataset.keys`
    - `Dataset.iindex`
    - `Dataset.indexlen`
    - `Dataset.lenindex`
    - `Dataset.lname`
    - `Dataset.tiindex`

    *global value (getters @property)*

    - `Dataset.complete`
    - `Dataset.consistent`
    - `Dataset.dimension`
    - `Dataset.lencomplete`
    - `Dataset.primary`
    - `Dataset.secondary`

    *selecting - infos methods (`observation.dataset_structure.DatasetStructure`)*

    - `Dataset.idxrecord`
    - `Dataset.indexinfos`
    - `Dataset.indicator`
    - `Dataset.iscanonorder`
    - `Dataset.isinrecord`
    - `Dataset.keytoval`
    - `Dataset.loc`
    - `Dataset.nindex`
    - `Dataset.record`
    - `Dataset.recidx`
    - `Dataset.recvar`
    - `Dataset.tree`
    - `Dataset.valtokey`

    *add - update methods (`observation.dataset_structure.DatasetStructure`)*

    - `Dataset.add`
    - `Dataset.addindex`
    - `Dataset.append`
    - `Dataset.delindex`
    - `Dataset.delrecord`
    - `Dataset.orindex`
    - `Dataset.renameindex`
    - `Dataset.setvar`
    - `Dataset.setname`
    - `Dataset.updateindex`

    *structure management - methods (`observation.dataset_structure.DatasetStructure`)*

    - `Dataset.applyfilter`
    - `Dataset.coupling`
    - `Dataset.full`
    - `Dataset.getduplicates`
    - `Dataset.mix`
    - `Dataset.merging`
    - `Dataset.reindex`
    - `Dataset.reorder`
    - `Dataset.setfilter`
    - `Dataset.sort`
    - `Dataset.swapindex`
    - `Dataset.setcanonorder`
    - `Dataset.tostdcodec`

    *exports methods (`observation.dataset_interface.DatasetInterface`)*

    - `Dataset.json`
    - `Dataset.plot`
    - `Dataset.to_obj`
    - `Dataset.to_csv`
    - `Dataset.to_dataframe`
    - `Dataset.to_file`
    - `Dataset.to_ntv`
    - `Dataset.to_obj`
    - `Dataset.to_xarray`
    - `Dataset.view`
    - `Dataset.vlist`
    - `Dataset.voxel`
    '''

    field_class = None
    
    def __init__(self, listidx=None, reindex=True):
        '''
        Dataset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Field data
        - **reindex** : boolean (default True) - if True, default codec for each Field'''

        self.field    = self.field_class
        #self.analysis = Analysis(self)
        name = self.__class__.__name__
        Cdataset.__init__(self, listidx, name, reindex=reindex)
        #self.analysis.actualize()
        return

    """@classmethod
    def dic(cls, idxdic=None, reindex=True):
        '''
        Dataset constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        if not idxdic:
            return cls.ext(idxval=None, idxname=None, reindex=reindex)
        if isinstance(idxdic, Dataset):
            return idxdic
        if not isinstance(idxdic, dict):
            raise DatasetError("idxdic not dict")
        return cls.ext(idxval=list(idxdic.values()), idxname=list(idxdic.keys()),
                       reindex=reindex)"""

    """@classmethod
    def ext(cls, idxval=None, idxname=None, reindex=True):
        '''
        Dataset constructor (external index).

        *Parameters*

        - **idxval** : list of Field or list of values (see data model)
        - **idxname** : list of string (default None) - list of Field name (see data model)
        if idxval is None:
            idxval = []
        if not isinstance(idxval, list):
            return None
        val = [ [idx] if not isinstance(idx, list) else idx for idx in idxval]
        lenval = [len(idx) for idx in val]
        if lenval and max(lenval) != min(lenval):
            raise DatasetError('the length of Field are different')
        length = lenval[0] if lenval else 0
        if idxname is None:
            idxname = [None] * len(val)
        for ind, name in enumerate(idxname):
            if name is None or name == ES.defaultindex:
                idxname[ind] = 'i'+str(ind)
        lidx = [list(FieldInterface.decodeobj(
            idx, typevalue, context=False)) for idx in val]
        lindex = [Field(idx[2], name, list(range(length)), idx[1],
                         lendefault=length, reindex=reindex)
                  for idx, name in zip(lidx, idxname)]
        return cls(lindex, reindex=False)"""

    @classmethod
    def from_csv(cls, filename='dataset.csv', header=True, nrow=None, decode_str=True,
                 decode_json=True, optcsv={'quoting': csv.QUOTE_NONNUMERIC}):
        '''
        Dataset constructor (from a csv file). Each column represents index values.

        *Parameters*

        - **filename** : string (default 'dataset.csv'), name of the file to read
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **nrow** : integer (default None). Number of row. If None, all the row else nrow
        - **optcsv** : dict (default : quoting) - see csv.reader options'''
        if not optcsv:
            optcsv = {}
        if not nrow:
            nrow = -1
        with open(filename, newline='', encoding="utf-8") as file:
            reader = csv.reader(file, **optcsv)
            irow = 0
            for row in reader:
                if irow == nrow:
                    break
                if irow == 0:
                    idxval = [[] for i in range(len(row))]
                    idxname = [''] * len(row)
                if irow == 0 and header:
                    idxname = row
                else:
                    for i in range(len(row)):
                        if decode_json:
                            try:
                                idxval[i].append(json.loads(row[i]))
                            except:
                                idxval[i].append(row[i])
                        else:
                            idxval[i].append(row[i])
                irow += 1
        lindex = [cls.field_class.from_ntv({name:idx}, decode_str=decode_str) for idx, name in zip(idxval, idxname)]
        return cls(listidx=lindex, reindex=True)

    @classmethod
    def from_file(cls, filename, forcestring=False, reindex=True, decode_str=False):
        '''
        Generate Object from file storage.

         *Parameters*

        - **filename** : string - file name (with path)
        - **forcestring** : boolean (default False) - if True,
        forces the UTF-8 data format, else the format is calculated
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **decode_str**: boolean (default False) - if True, string are loaded in json data

        *Returns* : new Object'''
        with open(filename, 'rb') as file:
            btype = file.read(1)
        if btype == bytes('[', 'UTF-8') or btype == bytes('{', 'UTF-8') or forcestring:
            with open(filename, 'r', newline='', encoding="utf-8") as file:
                bjson = file.read()
        else:
            with open(filename, 'rb') as file:
                bjson = file.read()
        return cls.from_ntv(bjson, reindex=reindex, decode_str=decode_str)

    """@classmethod
    def obj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate a new Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        return cls.from_obj(bsd, reindex=reindex, context=context)"""

    @classmethod
    def ntv(cls, ntv_value, reindex=True, fast=False):
        '''Generate an Dataset Object from a ntv_value

        *Parameters*

        - **ntv_value** : bytes, string, Ntv object to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **fast** : boolean (default False) - if True, ntv_value are not converted in json-value'''
        return cls.from_ntv(ntv_value, reindex=reindex, fast=fast)
    
    @classmethod
    def from_ntv(cls, ntv_value, reindex=True, decode_str=False, fast=False):
        '''Generate an Dataset Object from a ntv_value

        *Parameters*

        - **ntv_value** : bytes, string, Ntv object to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **decode_str**: boolean (default False) - if True, string are loaded in json data
        - **fast** : boolean (default False) - if True, ntv_value are not converted in json-value'''
        ntv = Ntv.obj(ntv_value, decode_str=decode_str, fast=fast)
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
        return cls(lindex, reindex=reindex)

    """@classmethod
    def from_obj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate an Dataset Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string, DataFrame or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Field
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        if isinstance(bsd, cls):
            return bsd
        if bsd is None:
            bsd = []
        if isinstance(bsd, bytes):
            lis = cbor2.loads(bsd)
        elif isinstance(bsd, str):
            lis = json.loads(bsd, object_hook=CborDecoder().codecbor)
        elif isinstance(bsd, (list, dict)) or bsd.__class__.__name__ == 'DataFrame':
            lis = bsd
        else:
            raise DatasetError("the type of parameter is not available")
        return cls._init_obj(lis, reindex=reindex, context=context)"""

    def merge(self, fillvalue=math.nan, reindex=False, simplename=False):
        '''
        Merge method replaces Dataset objects included into its constituents.

        *Parameters*

        - **fillvalue** : object (default nan) - value used for the additional data
        - **reindex** : boolean (default False) - if True, set default codec after transformation
        - **simplename** : boolean (default False) - if True, new Field name are
        the same as merged Field name else it is a composed name.

        *Returns*: merged Dataset '''
        ilc = copy(self)
        delname = []
        row = ilc[0]
        if not isinstance(row, list):
            row = [row]
        merged, oldname, newname = Dataset._mergerecord(self.ext(row, ilc.lname),
                                                      simplename=simplename)
        if oldname and not oldname in merged.lname:
            delname.append(oldname)
        for ind in range(1, len(ilc)):
            oldidx = ilc.nindex(oldname)
            for name in newname:
                ilc.addindex(self.field(oldidx.codec, name, oldidx.keys))
            row = ilc[ind]
            if not isinstance(row, list):
                row = [row]
            rec, oldname, newname = Dataset._mergerecord(self.ext(row, ilc.lname),
                                                       simplename=simplename)
            if oldname and newname != [oldname]:
                delname.append(oldname)
            for name in newname:
                oldidx = merged.nindex(oldname)
                fillval = self.field.s_to_i(fillvalue)
                merged.addindex(
                    self.field([fillval] * len(merged), name, oldidx.keys))
            merged += rec
        for name in set(delname):
            if name:
                merged.delindex(name)
        if reindex:
            merged.reindex()
        ilc.lindex = merged.lindex
        return ilc

    @classmethod
    def ext(cls, idxval=None, idxname=None, reindex=True, fast=False):
        '''
        Dataset constructor (external index).

        *Parameters*

        - **idxval** : list of Field or list of values (see data model)
        - **idxname** : list of string (default None) - list of Field name (see data model)'''
        if idxval is None:
            idxval = []
        if not isinstance(idxval, list):
            return None
        val = []
        for idx in idxval:
            if not isinstance(idx, list):
                val.append([idx])
            else:
                val.append(idx)
        lenval = [len(idx) for idx in val]
        if lenval and max(lenval) != min(lenval):
            raise DatasetError('the length of Iindex are different')
        length = lenval[0] if lenval else 0
        idxname = [None] * len(val) if idxname is None else idxname
        for ind, name in enumerate(idxname):
            if name is None or name == '$default':
                idxname[ind] = 'i'+str(ind)
        lindex = [cls.field_class(codec, name, lendefault=length, reindex=reindex,
                                  fast=fast) for codec, name in zip(val, idxname)]
        return cls(lindex, reindex=False)
    
# %% internal
    @staticmethod
    def _mergerecord(rec, mergeidx=True, updateidx=True, simplename=False):
        #row = rec[0] if isinstance(rec, list) else rec
        row = rec[0]
        if not isinstance(row, list):
            row = [row]
        var = -1
        for ind, val in enumerate(row):
            if val.__class__.__name__ in ['Sdataset', 'Ndataset', 'Observation']:
                var = ind
                break
        if var < 0:
            return (rec, None, [])
        ilis = row[var]
        oldname = rec.lname[var]
        if ilis.lname == ['i0']:
            newname = [oldname]
            ilis.setname(newname)
        elif not simplename:
            newname = [oldname + '_' + name for name in ilis.lname]
            ilis.setname(newname)
        else:
            newname = copy(ilis.lname)
        for name in rec.lname:
            if name in newname:
                newname.remove(name)
            else:
                updidx = name in ilis.lname and not updateidx
                ilis.addindex({name: [rec.nindex(name)[0]] * len(ilis)},
                              merge=mergeidx, update=updidx)
                #ilis.addindex([name, [rec.nindex(name)[0]] * len(ilis)],
                #              merge=mergeidx, update=updidx)
        return (ilis, oldname, newname)

# %% special
    def __str__(self):
        '''return string format for var and lidx'''
        stri = ''
        if self.lvar:
            stri += 'variables :\n'
            for idx in self.lvar:
                stri += '    ' + str(idx) + '\n'
        if self.lidx:
            stri += 'index :\n'
            for idx in self.lidx:
                stri += '    ' + str(idx) + '\n'
        return stri

    def __add__(self, other):
        ''' Add other's values to self's values in a new Dataset'''
        newil = copy(self)
        newil.__iadd__(other)
        return newil

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        return self.add(other, name=True, solve=False)
    
    def __or__(self, other):
        ''' Add other's index to self's index in a new Dataset'''
        newil = copy(self)
        newil.__ior__(other)
        return newil

    def __ior__(self, other):
        ''' Add other's index to self's index'''
        return self.orindex(other, first=False, merge=True, update=False)

# %% property
    @property
    def complete(self):
        '''return a boolean (True if Dataset is complete and consistent)'''
        return self.lencomplete == len(self) and self.consistent

    @property
    def consistent(self):
        ''' True if all the record are different'''
        selfiidx = self.iidx
        if not selfiidx:
            return True
        return max(Counter(zip(*selfiidx)).values()) == 1

    @property
    def extidx(self):
        '''idx values (see data model)'''
        return [idx.values for idx in self.lidx]

    @property
    def extidxext(self):
        '''idx val (see data model)'''
        return [idx.val for idx in self.lidx]

    @property
    def idxname(self):
        ''' list of idx name'''
        return [idx.name for idx in self.lidx]

    @property
    def idxlen(self):
        ''' list of idx codec length'''
        return [len(idx.codec) for idx in self.lidx]

    @property
    def iidx(self):
        ''' list of keys for each idx'''
        return [idx.keys for idx in self.lidx]

    @property
    def lencomplete(self):
        '''number of values if complete (prod(idxlen primary))'''
        primary = self.primary
        return util.mul([self.idxlen[i] for i in primary])
    
    @property
    def lenidx(self):
        ''' number of idx'''
        return len(self.lidx)

    @property
    def lidx(self):
        '''list of idx'''
        return [self.lindex[i] for i in self.lidxrow]

    @property
    def lisvar(self):
        '''list of boolean : True if Field is var'''
        return [name in self.lvarname for name in self.lname]

    @property
    def lvar(self):
        '''list of var'''
        return [self.lindex[i] for i in self.lvarrow]

    @property
    def lvarrow(self):
        '''list of var row'''
        return [self.lname.index(name) for name in self.lvarname]

    @property
    def lidxrow(self):
        '''list of idx row'''
        return [i for i in range(self.lenindex) if i not in self.lvarrow]

    @property
    def primary(self):
        ''' list of primary idx'''
        return [self.lidxrow.index(self.lname.index(name)) for name in self.primaryname]

    @property
    def primaryname(self):
        ''' list of primary name'''
        return Util.view(self._analysis.primary, mode='id')

    @property
    def secondary(self):
        ''' list of secondary idx'''
        return [self.lidxrow.index(self.lname.index(name)) for name in self.secondaryname]

    @property
    def secondaryname(self):
        ''' list of secondary name'''
        return Util.view(self._analysis.secondary, mode='id')

    @property
    def setidx(self):
        '''list of codec for each idx'''
        return [idx.codec for idx in self.lidx]

    @property
    def zip(self):
        '''return a zip format for transpose(extidx) : tuple(tuple(rec))'''
        textidx = util.transpose(self.extidx)
        if not textidx:
            return None
        return tuple(tuple(idx) for idx in textidx)
