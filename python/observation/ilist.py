# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: philippe@loco-labs.io

The `python.observation.ilist` module contains the `Ilist` class.

Documentation is available in other pages :

- The Json Standard for Ilist is define
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/IlistJSON-Standard.pdf)
- The concept of 'indexed list' is describe in
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression test are at
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests/test_ilist.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples/Ilist)
 are :
    - [creation](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Ilist/Ilist_creation.ipynb)
    - [variable](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Ilist/Ilist_variable.ipynb)
    - [update](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Ilist/Ilist_update.ipynb)
    - [structure](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Ilist/Ilist_structure.ipynb)
    - [structure-analysis](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Examples/Ilist/Ilist_structure-analysis.ipynb)

---
"""
# %% declarations
from collections import Counter
from copy import copy
import math
import json
import csv
import datetime
import cbor2
import pandas

from observation.esconstante import ES
from observation.iindex import Iindex
from observation.iindex_interface import IindexInterface, CborDecoder
from observation.util import util
from observation.ilist_interface import IlistInterface, IlistError
from observation.ilist_structure import IlistStructure
from observation.ilist_analysis import Analysis
from json_ntv.ntv import Ntv

class Ilist(IlistStructure, IlistInterface):
    # %% intro
    '''
    An `Ilist` is a representation of an indexed list.

    *Attributes (for @property see methods)* :

    - **lindex** : list of Iindex
    - **analysis** : Analysis object (data structure)

    The methods defined in this class are :

    *constructor (@classmethod))*

    - `Ilist.dic`
    - `Ilist.ext`
    - `Ilist.obj`
    - `Ilist.from_csv`
    - `Ilist.from_ntv`
    - `Ilist.from_obj`
    - `Ilist.from_file`
    - `Ilist.merge`

    *dynamic value - module analysis (getters @property)*

    - `Ilist.extidx`
    - `Ilist.extidxext`
    - `Ilist.groups`
    - `Ilist.idxname`
    - `Ilist.idxlen`
    - `Ilist.iidx`
    - `Ilist.lenidx`
    - `Ilist.lidx`
    - `Ilist.lidxrow`
    - `Ilist.lisvar`
    - `Ilist.lvar`
    - `Ilist.lvarname`
    - `Ilist.lvarrow`
    - `Ilist.lunicname`
    - `Ilist.lunicrow`
    - `Ilist.primaryname`
    - `Ilist.setidx`
    - `Ilist.zip`

    *dynamic value (getters @property)*

    - `Ilist.keys`
    - `Ilist.iindex`
    - `Ilist.indexlen`
    - `Ilist.lenindex`
    - `Ilist.lname`
    - `Ilist.tiindex`
    - `Ilist.typevalue`

    *global value (getters @property)*

    - `Ilist.category`
    - `Ilist.complete`
    - `Ilist.consistent`
    - `Ilist.dimension`
    - `Ilist.lencomplete`
    - `Ilist.primary`
    - `Ilist.secondary`

    *selecting - infos methods (`observation.ilist_structure.IlistStructure`)*

    - `Ilist.couplingmatrix`
    - `Ilist.idxrecord`
    - `Ilist.indexinfos`
    - `Ilist.indicator`
    - `Ilist.iscanonorder`
    - `Ilist.isinrecord`
    - `Ilist.keytoval`
    - `Ilist.loc`
    - `Ilist.nindex`
    - `Ilist.record`
    - `Ilist.recidx`
    - `Ilist.recvar`
    - `Ilist.tree`
    - `Ilist.valtokey`

    *add - update methods (`observation.ilist_structure.IlistStructure`)*

    - `Ilist.add`
    - `Ilist.addindex`
    - `Ilist.append`
    - `Ilist.delindex`
    - `Ilist.delrecord`
    - `Ilist.orindex`
    - `Ilist.renameindex`
    - `Ilist.setvar`
    - `Ilist.setname`
    - `Ilist.updateindex`

    *structure management - methods (`observation.ilist_structure.IlistStructure`)*

    - `Ilist.applyfilter`
    - `Ilist.coupling`
    - `Ilist.full`
    - `Ilist.getduplicates`
    - `Ilist.mix`
    - `Ilist.merging`
    - `Ilist.reindex`
    - `Ilist.reorder`
    - `Ilist.setfilter`
    - `Ilist.sort`
    - `Ilist.swapindex`
    - `Ilist.setcanonorder`
    - `Ilist.tostdcodec`

    *exports methods (`observation.ilist_interface.IlistInterface`)*

    - `Ilist.json`
    - `Ilist.plot`
    - `Ilist.to_obj`
    - `Ilist.to_csv`
    - `Ilist.to_dataframe`
    - `Ilist.to_file`
    - `Ilist.to_ntv`
    - `Ilist.to_obj`
    - `Ilist.to_xarray`
    - `Ilist.view`
    - `Ilist.vlist`
    - `Ilist.voxel`
    '''

    def __init__(self, listidx=None, reindex=True):
        '''
        Ilist constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Iindex data
        - **reindex** : boolean (default True) - if True, default codec for each Iindex'''

        self.name = self.__class__.__name__
        self.analysis = Analysis(self)
        self.lindex = []
        if listidx.__class__.__name__ in ['Ilist', 'Observation']:
            self.lindex = [copy(idx) for idx in listidx.lindex]
            return
        if not listidx:
            return
        self.lindex = listidx
        if reindex:
            self.reindex()
        self.analysis.actualize()
        return

    @classmethod
    def dic(cls, idxdic=None, typevalue=ES.def_clsName, reindex=True):
        '''
        Ilist constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)'''
        if not idxdic:
            return cls.ext(idxval=None, idxname=None, typevalue=typevalue,
                           reindex=reindex)
        if isinstance(idxdic, Ilist):
            return idxdic
        if not isinstance(idxdic, dict):
            raise IlistError("idxdic not dict")
        return cls.ext(idxval=list(idxdic.values()), idxname=list(idxdic.keys()),
                       typevalue=typevalue, reindex=reindex)

    @classmethod
    def ext(cls, idxval=None, idxname=None, typevalue=ES.def_clsName, reindex=True):
        '''
        Ilist constructor (external index).

        *Parameters*

        - **idxval** : list of Iindex or list of values (see data model)
        - **idxname** : list of string (default None) - list of Iindex name (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)'''
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
            raise IlistError('the length of Iindex are different')
        length = 0
        if lenval:
            length = lenval[0]
        if idxname is None:
            idxname = [None] * len(val)
        for ind, name in enumerate(idxname):
            if name is None or name == ES.defaultindex:
                idxname[ind] = 'i'+str(ind)
        lidx = [list(IindexInterface.decodeobj(
            idx, typevalue, context=False)) for idx in val]
        lindex = [Iindex(idx[2], name, list(range(length)), idx[1],
                         lendefault=length, reindex=reindex)
                  for idx, name in zip(lidx, idxname)]
        return cls(lindex, reindex=False)

    @classmethod
    def from_csv(cls, filename='ilist.csv', header=True, nrow=None,
                 optcsv={'quoting': csv.QUOTE_NONNUMERIC}, dtype=ES.def_dtype):
        '''
        Ilist constructor (from a csv file). Each column represents index values.

        *Parameters*

        - **filename** : string (default 'ilist.csv'), name of the file to read
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **nrow** : integer (default None). Number of row. If None, all the row else nrow
        - **dtype** : list of string (default None) - data type for each column (default str)
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
                    if dtype and not isinstance(dtype, list):
                        dtype = [dtype] * len(row)
                    idxval = [[] for i in range(len(row))]
                    idxname = None
                if irow == 0 and header:
                    idxname = row
                else:
                    if not dtype:
                        for i in range(len(row)):
                            idxval[i].append(row[i])
                    else:
                        for i in range(len(row)):
                            idxval[i].append(util.cast(row[i], dtype[i]))
                irow += 1
        return cls.ext(idxval, idxname, typevalue=None, reindex=True)

    @classmethod
    def from_file(cls, filename, forcestring=False):
        '''
        Generate Object from file storage.

         *Parameters*

        - **filename** : string - file name (with path)
        - **forcestring** : boolean (default False) - if True,
        forces the UTF-8 data format, else the format is calculated

        *Returns* : new Object'''
        with open(filename, 'rb') as file:
            btype = file.read(1)
        if btype == bytes('[', 'UTF-8') or btype == bytes('{', 'UTF-8') or forcestring:
            with open(filename, 'r', newline='', encoding="utf-8") as file:
                bjson = file.read()
        else:
            with open(filename, 'rb') as file:
                bjson = file.read()
        return cls.from_obj(bjson, reindex=True)

    @classmethod
    def obj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate a new Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        return cls.from_obj(bsd, reindex=reindex, context=context)

    @classmethod
    def from_ntv(cls, ntv_value, reindex=False):
        '''Generate an Ilist Object from a ntv_value

        *Parameters*

        - **ntv_value** : bytes, string, Ntv object to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex'''
        ntv = Ntv.obj(ntv_value)
        leng = max([len(ntvi) for ntvi in ntv.ntv_value])
        # decode: name, type, codec, parent, keys
        lidx = [list(Iindex.decodentv(ntvf)) for ntvf in ntv]
        for ind in range(len(lidx)):
            if lidx[ind][0] == '':
                lidx[ind][0] = 'i'+str(ind)
            Ilist._init_ntv_keys(ind, lidx, leng)
        lindex = [Iindex(idx[2], idx[0], idx[4], None, # idx[1] pour le type,
                     reindex=reindex) for idx in lidx]
        return cls(lindex, reindex=False)

    @classmethod
    def from_obj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate an Ilist Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string, DataFrame or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
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
            raise IlistError("the type of parameter is not available")
        return cls._init_obj(lis, reindex=reindex, context=context)

    def merge(self, fillvalue=math.nan, reindex=False, simplename=False):
        '''
        Merge method replaces Ilist objects included into its constituents.

        *Parameters*

        - **fillvalue** : object (default nan) - value used for the additional data
        - **reindex** : boolean (default False) - if True, set default codec after transformation
        - **simplename** : boolean (default False) - if True, new Iindex name are
        the same as merged Iindex name else it is a composed name.

        *Returns*: merged Ilist '''
        ilc = copy(self)
        delname = []
        row = ilc[0]
        if not isinstance(row, list):
            row = [row]
        merged, oldname, newname = Ilist._mergerecord(Ilist.ext(row, ilc.lname),
                                                      simplename=simplename)
        if oldname and not oldname in merged.lname:
            delname.append(oldname)
        for ind in range(1, len(ilc)):
            oldidx = ilc.nindex(oldname)
            for name in newname:
                ilc.addindex(Iindex(oldidx.codec, name, oldidx.keys))
            row = ilc[ind]
            if not isinstance(row, list):
                row = [row]
            rec, oldname, newname = Ilist._mergerecord(Ilist.ext(row, ilc.lname),
                                                       simplename=simplename)
            if oldname and newname != [oldname]:
                delname.append(oldname)
            for name in newname:
                oldidx = merged.nindex(oldname)
                fillval = util.castval(
                    fillvalue, util.typename(name, ES.def_clsName))
                merged.addindex(
                    Iindex([fillval] * len(merged), name, oldidx.keys))
            merged += rec
        for name in set(delname):
            if name:
                merged.delindex(name)
        if reindex:
            merged.reindex()
        ilc.lindex = merged.lindex
        return ilc

# %% internal
    @classmethod
    def _init_obj(cls, listidx=None, reindex=True, typevalue=ES.def_clsName, context=True):
        '''
        Ilist constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of compatible Iindex data
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        '''
        lindex = []
        if listidx.__class__.__name__ == 'DataFrame':
            lindex = []
            for name, idx in listidx.astype('category').items():
                lis = list(idx.cat.categories)
                if lis and isinstance(lis[0], pandas._libs.tslibs.timestamps.Timestamp):
                    lis = [ts.to_pydatetime().astimezone(datetime.timezone.utc)
                           for ts in lis]
                lindex.append(Iindex(lis, name, list(idx.cat.codes),
                                     lendefault=len(listidx), castobj=False))
            return cls(lindex, reindex=reindex)

        if isinstance(listidx, dict):
            for idxname in listidx:
                var, idx = Iindex.from_dict_obj({idxname: listidx[idxname]},
                                                typevalue=typevalue, reindex=reindex)
                lindex.append(idx)
            return cls(lindex, reindex=reindex)

        if isinstance(listidx, list) and len(listidx) == 0:
            return cls()

        # decode: name, typevaluedec, codec, parent, keys, isfullkeys, isparent
        lidx = [list(IindexInterface.decodeobj(idx, typevalue, context))
                for idx in listidx]
        for ind in range(len(lidx)):
            if lidx[ind][0] is None or lidx[ind][0] == ES.defaultindex:
                lidx[ind][0] = 'i'+str(ind)
            if lidx[ind][1] is None:
                lidx[ind][1] = util.typename(lidx[ind][0], typevalue)
        name, typevaluedec, codec, parent, keys, isfullkeys, isparent =\
            tuple(zip(*lidx))

        leng = [len(cod) for cod in codec]
        # mode full : tous False et même longueur
        fullmode = not max(isfullkeys) and max(leng) == min(leng)
        # mode default : tous True (idem all(isfullkeys))
        defmode = min(isfullkeys)

        # not max(isparent) : tous isparent = False
        if not max(isparent) and (fullmode or defmode):  # mode full ou mode default
            lindex = [Iindex(idx[2], idx[0], idx[4], idx[1],
                             reindex=reindex) for idx in lidx]
            return cls(lindex, reindex=reindex)

        length, crossed = Ilist._init_len_cros(
            fullmode, leng, isfullkeys, keys, isparent)
        keyscross = util.canonorder([leng[i] for i in crossed])
        # name: 0, typevaluedec: 1, codec: 2, parent: 3, keys: 4
        for ind in range(len(crossed)):
            lidx[crossed[ind]][4] = keyscross[ind]  # keys
        for ind in range(len(lidx)):
            Ilist._init_keys(ind, lidx, length)
        lindex = [Iindex(idx[2], idx[0], idx[4], idx[1],
                         reindex=reindex) for idx in lidx]
        return cls(lindex, reindex=False)

    @staticmethod
    def _init_len_cros(fullmode, leng, isfullkeys, keys, isparent):
        ''' initialization of length and crossed data'''
        # crossed : pas d'index (isfullindex false), pas de parent(isparent false)
        crossed = []
        if fullmode:  # au moins un fullkeys ou une longueur différente
            length = max(leng)
            return length, crossed

        # au moins un fullkeys ou une longueur différente
        if max(isfullkeys):
            length = len(keys[isfullkeys.index(True)])
            crossed = [i for i, (isfullk, ispar, lengt) in
                       enumerate(zip(isfullkeys, isparent, leng))
                       if not ispar and not isfullk and 1 < lengt < length]
            return length, crossed

        # max(leng) != min(leng) pas de fullindex => matrice et dérivés
        crossed = [i for i, (isfullk, ispar, lengt) in
                   enumerate(zip(isfullkeys, isparent, leng))
                   if not ispar and not isfullk and 1 < lengt]
        lencrossed = [leng[ind] for ind in crossed]

        if max(lencrossed) == min(lencrossed):
            length = lencrossed[0]
            crossed = []
            return length, crossed

        length = math.prod([leng[i] for i in crossed])
        if length / max(lencrossed) == max(lencrossed):
            length = max(lencrossed)
            crossed = [i for i, (isfullk, ispar, lengt) in
                       enumerate(zip(isfullkeys, isparent, leng))
                       if not ispar and not isfullk and 1 < lengt < length]
        return length, crossed

    @staticmethod
    def _init_ntv_keys(ind, lidx, leng):
        ''' initialization of explicit keys data in lidx object'''
        # name: 0, type: 1, codec: 2, parent: 3, keys: 4
        keys = lidx[ind][4]
        if keys is None and lidx[ind][3] is None:  # full or unique
            if len(lidx[ind][2]) == 1: # unique
                lidx[ind][4] = [0] * leng
            else:    # full
                lidx[ind][4] = list(range(leng))
            return
        if keys and len(keys) > 1 and lidx[ind][3] is None:  #complete
            return
        if keys and len(keys) == 1:  #primary
            coef = keys[0]
            lidx[ind][4] = [ (ikey % (coef * len(lidx[ind][2]))) // coef for ikey in range(leng)]
            return  
        parent = lidx[ind][3]
        if parent is None:
            raise IlistError('keys not referenced')          
        if not lidx[parent][4] or len(lidx[parent][4]) != leng:
            Ilist._init_ntv_keys(parent, lidx, leng)
        if not keys and len(lidx[ind][2]) == len(lidx[parent][2]):    # implicit
            lidx[ind][4] = lidx[parent][4]
            return
        lidx[ind][4] = Iindex.keysfromderkeys(lidx[parent][4], keys)  # relative
        return

    @staticmethod
    def _init_keys(ind, lidx, leng):
        ''' initialization of keys data'''
        # name: 0, typevaluedec: 1, codec: 2, parent: 3, keys: 4
        if lidx[ind][4] and (lidx[ind][3] is None or lidx[ind][3] < 0):
            return
        if lidx[ind][4] and len(lidx[ind][4]) == leng:
            return
        if len(lidx[ind][2]) == 1:
            lidx[ind][4] = [0] * leng
            return
        if lidx[ind][3] is None:
            raise IlistError('keys not referenced')
        if lidx[ind][3] < 0:
            lidx[ind][4] = list(range(leng))
            return
        if not lidx[lidx[ind][3]][4] or len(lidx[lidx[ind][3]][4]) != leng:
            Ilist._init_keys(lidx[ind][3], lidx, leng)
        if not lidx[ind][4] and len(lidx[ind][2]) == len(lidx[lidx[ind][3]][2]):
            # coupled format
            lidx[ind][4] = lidx[lidx[ind][3]][4]
            return
        # derived keys
        if not lidx[ind][4]:  # derived format without keys
            lenp = len(lidx[lidx[ind][3]][2])  # len codec parent
            lidx[ind][4] = [(i*len(lidx[ind][2])) // lenp for i in range(lenp)]
        lidx[ind][4] = Iindex.keysfromderkeys(
            lidx[lidx[ind][3]][4], lidx[ind][4])
        return

    @staticmethod
    def _mergerecord(rec, mergeidx=True, updateidx=True, simplename=False):
        row = rec[0]
        if not isinstance(row, list):
            row = [row]
        var = -1
        for ind, val in enumerate(row):
            if val.__class__.__name__ in ['Ilist', 'Observation']:
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
                ilis.addindex([name, [rec.nindex(name)[0]] * len(ilis)],
                              merge=mergeidx, update=updidx)
        return (ilis, oldname, newname)

# %% special
    def __str__(self):
        '''return string format for var and lidx'''
        stri = ''
        if self.lvar:
            for idx in self.lvar:
                stri += str(idx)
        stri += '\n'
        for idx in self.lidx:
            stri += str(idx)
        return stri

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
        ''' modify the Iindex values for each Iindex at the row ind'''
        if not isinstance(item, list):
            item = [item]
        for val, idx in zip(item, self.lindex):
            idx[ind] = val

    def __delitem__(self, ind):
        ''' remove all Iindex item at the row ind'''
        for idx in self.lindex:
            del idx[ind]

    def __hash__(self):
        '''return sum of all hash(Iindex)'''
        return sum([hash(idx) for idx in self.lindex])

    def _hashi(self):
        '''return sum of all hashi(Iindex)'''
        return sum([idx._hashi() for idx in self.lindex])

    def __eq__(self, other):
        ''' equal if hash values are equal'''
        return hash(self) == hash(other)

    def __add__(self, other):
        ''' Add other's values to self's values in a new Ilist'''
        newil = copy(self)
        newil.__iadd__(other)
        return newil

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        return self.add(other, name=True, solve=False)

    def __or__(self, other):
        ''' Add other's index to self's index in a new Ilist'''
        newil = copy(self)
        newil.__ior__(other)
        return newil

    def __ior__(self, other):
        ''' Add other's index to self's index'''
        return self.orindex(other, first=False, merge=True, update=False)

    def __copy__(self):
        ''' Copy all the data '''
        return Ilist(self)

# %% property
    @property
    def complete(self):
        '''return a boolean (True if Ilist is complete and consistent)'''
        return self.lencomplete == len(self) and self.consistent

    @property
    def consistent(self):
        ''' True if all the record are different'''
        if not self.iidx:
            return True
        return max(Counter(zip(*self.iidx)).values()) == 1

    @property
    def category(self):
        ''' dict with category for each Iindex'''
        return {field['name']: field['cat'] for field in self.indexinfos()}

    @property
    def dimension(self):
        ''' integer : number of primary Iindex'''
        return len(self.primary)

    @property
    def extidx(self):
        '''idx values (see data model)'''
        return [idx.values for idx in self.lidx]

    @property
    def extidxext(self):
        '''idx val (see data model)'''
        return [idx.val for idx in self.lidx]

    @property
    def groups(self):
        ''' list with crossed Iindex groups'''
        return self.analysis.getgroups()

    @property
    def idxname(self):
        ''' list of idx name'''
        return [idx.name for idx in self.lidx]

    @property
    def idxlen(self):
        ''' list of idx codec length'''
        return [len(idx.codec) for idx in self.lidx]

    @property
    def indexlen(self):
        ''' list of index codec length'''
        return [len(idx.codec) for idx in self.lindex]

    @property
    def iidx(self):
        ''' list of keys for each idx'''
        return [idx.keys for idx in self.lidx]

    @property
    def iindex(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def keys(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def lencomplete(self):
        '''number of values if complete (prod(idxlen primary))'''
        primary = self.primary
        return util.mul([self.idxlen[i] for i in primary])

    @property
    def lenindex(self):
        ''' number of indexes'''
        return len(self.lindex)

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
        '''list of boolean : True if Iindex is var'''
        return [name in self.lvarname for name in self.lname]

    @property
    def lvar(self):
        '''list of var'''
        return [self.lindex[i] for i in self.lvarrow]

    @property
    def lvarname(self):
        ''' list of variable Iindex name'''
        return self.analysis.getvarname()

    @property
    def lunicrow(self):
        '''list of unic idx row'''
        return [self.lname.index(name) for name in self.lunicname]

    @property
    def lvarrow(self):
        '''list of var row'''
        return [self.lname.index(name) for name in self.lvarname]

    @property
    def lidxrow(self):
        '''list of idx row'''
        return [i for i in range(self.lenindex) if i not in self.lvarrow]

    @property
    def lunicname(self):
        ''' list of unique index name'''
        return [idx.name for idx in self.lindex if len(idx.codec) == 1]

    @property
    def lname(self):
        ''' list of index name'''
        return [idx.name for idx in self.lindex]

    @property
    def primary(self):
        ''' list of primary idx'''
        return self.analysis.getprimary()

    @property
    def primaryname(self):
        ''' list of primary name'''
        return [self.lidx[idx].name for idx in self.primary]

    @property
    def secondary(self):
        ''' list of secondary idx'''
        return self.analysis.getsecondary()

    @property
    def secondaryname(self):
        ''' list of secondary name'''
        return [self.lindex[idx].name for idx in self.secondary]

    @property
    def setidx(self):
        '''list of codec for each idx'''
        return [idx.codec for idx in self.lidx]

    @property
    def tiindex(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iindex)))

    @property
    def typevalue(self):
        '''return typevalue calculated from Iindex name'''
        return [util.typename(name)for name in self.lname]

    @property
    def zip(self):
        '''return a zip format for transpose(extidx) : tuple(tuple(rec))'''
        textidx = util.transpose(self.extidx)
        if not textidx:
            return None
        return tuple(tuple(idx) for idx in textidx)
