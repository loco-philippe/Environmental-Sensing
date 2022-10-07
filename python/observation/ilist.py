# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: philippe@loco-labs.io

The `observation.ilist` module contains the `Ilist` class.

Documentation is available in other pages :

- The Json Standard for Ilist is define
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/
documentation/IlistJSON-Standard.pdf)
- The concept of 'indexed list' is describe in
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki/Indexed-list).
- The non-regression test are at
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/
Tests/test_ilist.py)
- The [examples](https://github.com/loco-philippe/Environmental-Sensing/tree/main/
python/Examples/Ilist)
 are :
    - [creation](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
      python/Examples/Ilist/Ilist_creation.ipynb)
    - [variable](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
      python/Examples/Ilist/Ilist_variable.ipynb)
    - [update](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
      python/Examples/Ilist/Ilist_update.ipynb)
    - [structure](https://github.com/loco-philippe/Environmental-Sensing/blob/main/
      python/Examples/Ilist/Ilist_structure.ipynb)
    - [structure-analysis](https://github.com/loco-philippe/Environmental-Sensing/
      blob/main/python/Examples/Ilist/Ilist_structure-analysis.ipynb)

---
"""
# %% declarations
from collections import Counter
from copy import copy
import json
import csv
import cbor2

from esconstante import ES
from iindex import Iindex
from util import util, CborDecoder
from ilist_interface import IlistInterface, IlistError
from ilist_structure import IlistStructure


class Ilist(IlistStructure, IlistInterface):
    # %% intro
    '''
    An `Ilist` is a representation of an indexed list.

    *Attributes (for @property see methods)* :

    - **lindex** : list of Iindex
    - **lvarname** : variable name (list of string)

    The methods defined in this class are :

    *constructor (@classmethod))*

    - `Ilist.Idic`
    - `Ilist.Iext`
    - `Ilist.Iobj`
    - `Ilist.from_csv`
    - `Ilist.from_obj`
    - `Ilist.from_file`

    *dynamic value (getters @property)*

    - `Ilist.extidx`
    - `Ilist.extidxext`
    - `Ilist.idxname`
    - `Ilist.idxref`
    - `Ilist.idxlen`
    - `Ilist.iidx`
    - `Ilist.keys`
    - `Ilist.lenindex`
    - `Ilist.lenidx`
    - `Ilist.lidx`
    - `Ilist.lidxrow`
    - `Ilist.lvar`
    - `Ilist.lvarrow`
    - `Ilist.lname`
    - `Ilist.lunicname`
    - `Ilist.lunicrow`
    - `Ilist.setidx`
    - `Ilist.tiidx`
    - `Ilist.textidx`
    - `Ilist.textidxext`

    *global value (getters @property)*

    - `Ilist.complete`
    - `Ilist.consistent`
    - `Ilist.dimension`
    - `Ilist.lencomplete`
    - `Ilist.primary`
    - `Ilist.zip`

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
    - `Ilist.valtokey`

    *add - update methods (`observation.ilist_structure.IlistStructure`)*

    - `Ilist.add`
    - `Ilist.addindex`
    - `Ilist.append`
    - `Ilist.delindex`
    - `Ilist.delrecord`
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
    - `Ilist.merge`
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
    - `Ilist.to_file`
    - `Ilist.to_xarray`
    - `Ilist.to_dataFrame`
    - `Ilist.view`
    - `Ilist.vlist`
    - `Ilist.voxel`
    '''
    @classmethod
    def Idic(cls, idxdic=None, typevalue=ES.def_clsName, var=None, reindex=True):
        '''
        Ilist constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **var** :  int (default None) - row of the variable'''
        if not idxdic:
            return cls.Iext(idxval=None, idxname=None, typevalue=typevalue, var=var, 
                            reindex=reindex)
        if isinstance(idxdic, Ilist):
            return idxdic
        if not isinstance(idxdic, dict):
            raise IlistError("idxdic not dict")
        return cls.Iext(idxval=list(idxdic.values()), idxname=list(idxdic.keys()), 
                        typevalue=typevalue, var=var, reindex=reindex)

    @classmethod
    def Iext(cls, idxval=None, idxname=None, typevalue=ES.def_clsName, var=None, 
             reindex=True):
        '''
        Ilist constructor (external index).

        *Parameters*

        - **idxval** : list of Iindex or list of values (see data model)
        - **idxname** : list of string (default None) - list of Iindex name (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **var** :  int (default None) - row of the variable'''
        #print('debut iext')
        #t0 = time()
        if idxname is None:
            idxname = []
        if idxval is None:
            idxval = []
        if not isinstance(idxval, list):
            return None
        # if len(idxval) == 0: return cls()
        val = []
        for idx in idxval:
            if not isinstance(idx, list):
                val.append([idx])
            else:
                val.append(idx)
        lenval=[len(idx) for idx in val]
        if lenval and max(lenval) != min(lenval):
            raise IlistError('the length of Iindex are different')
        '''length = len(val[0])
        for idx in val:
            if len(idx) != length:
                raise IlistError('the length of Iindex are different')'''
        return cls(listidx=val, name=idxname, var=var, typevalue=typevalue,
                   context=False, reindex=reindex)

    @classmethod
    def from_csv(cls, filename='ilist.csv', var=None, header=True, nrow=None,
                 optcsv={'quoting': csv.QUOTE_NONNUMERIC}, dtype=ES.def_dtype):
        '''
        Ilist constructor (from a csv file). Each column represents index values.

        *Parameters*

        - **filename** : string (default 'ilist.csv'), name of the file to read
        - **var** : integer (default None). column row for variable data
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
                # elif irow == 0:
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
        return cls.Iext(idxval, idxname, typevalue=None, var=var, reindex=True)

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
        if btype == bytes('[', 'UTF-8') or forcestring:
            with open(filename, 'r', newline='', encoding="utf-8") as file:
                bjson = file.read()
        else:
            with open(filename, 'rb') as file:
                bjson = file.read()
        return cls.from_obj(bjson, reindex=True)

    @classmethod
    def Iobj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate a new Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        return cls.from_obj(bsd, reindex=reindex, context=context)

    @classmethod
    def from_obj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate an Ilist Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        if not bsd:
            bsd = []
        if isinstance(bsd, bytes):
            lis = cbor2.loads(bsd)
        elif isinstance(bsd, str):
            lis = json.loads(bsd, object_hook=CborDecoder().codecbor)
        elif isinstance(bsd, list):
            lis = bsd
        else:
            raise IlistError("the type of parameter is not available")
        return cls(lis, reindex=reindex, context=context)

    def __init__(self, listidx=None, name=None, length=None, var=None, reindex=True,
                 typevalue=ES.def_clsName, context=True):
        '''
        Ilist constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of compatible Iindex data
        - **name** :  list (default None) - list of name for the Iindex data
        - **var** :  int (default None) - row of the variable
        - **length** :  int (default None)  - len of each Iindex
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **context** : boolean (default True) - if False, only codec and keys are included'''

        self.name = self.__class__.__name__
        if not isinstance(name, list):
            name = [name]
        if isinstance(var, list):
            idxvar = var
        elif not isinstance(var, int) or var < 0:
            idxvar = []
        else:
            idxvar = [var]

        if listidx.__class__.__name__ in ['Ilist', 'Observation']:
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.lvarname = copy(listidx.lvarname)
            return
        if not listidx:
            self.lindex = []
            self.lvarname = []
            return

        if not isinstance(listidx, list) or not isinstance(listidx[0], (list, Iindex)):
            listidx = [[idx] for idx in listidx]
        codind, lcodind, lidx, idxvar, length, leng2 = \
            Ilist._init_internal(listidx, typevalue, name,
                                 context, idxvar, length)
        self.lindex = list(range(len(codind)))

        if len(listidx) == 1:
            self.lindex = [codind[0][1]]
            self.lvarname = [codind[0][1].name]
            return
        if length == 0:
            self.lvarname = [codind[i][1].name for i in idxvar]
            self.lindex = [iidx for code, iidx in codind]
            return

        flat = True
        if leng2:
            flat = length == max(leng2) == min(leng2)
        self._init_index(lcodind, flat, lidx, length, codind)
        for i in idxvar:
            self.lindex[i] = codind[i][1]
        self.lvarname = [codind[i][1].name for i in idxvar]
        if reindex:
            self.reindex()
        return

    @staticmethod
    def _init_internal(listidx, typevalue, name, context, idxvar, length):
        '''creation of internal data'''
        typeval = [typevalue for i in range(len(listidx))]
        #for i in range(len(name)):
        #    typeval[i] = util.typename(name[i], typeval[i])
        for i, nam in enumerate(name):
            typeval[i] = util.typename(nam, typeval[i])
        codind = [Iindex.from_obj(idx, typevalue=typ, context=context)
                  for idx, typ in zip(listidx, typeval)]
        for i, (code, idx) in zip(range(len(codind)), codind):
            if len(name) > i and name[i]:
                idx.name = name[i]
            if idx.name is None or idx.name == ES.defaultindex:
                idx.name = 'i'+str(i)
            if code == ES.variable and not idxvar:
                idxvar = [i]
        lcodind = [codind[i] for i in range(len(codind)) if i not in idxvar]
        lidx = [i for i in range(len(codind)) if i not in idxvar]
        # init length
        if not length:
            length = -1
        leng = [len(iidx)
                for code, iidx in codind if code < 0 < len(iidx)]
        leng2 = [l for l in leng if l > 1]
        if not leng:
            length = 0
        elif not leng2:
            length = 1
        elif max(leng2) == min(leng2) and length < 0:
            length = max(leng2)
        if idxvar:
            length = len(codind[idxvar[0]][1])
        return (codind, lcodind, lidx, idxvar, length, leng2)

    def _init_index(self, lcodind, flat, lidx, length, codind):
        '''creation of primary and secondary Iindex'''
        if not flat:
            keysset = util.canonorder([len(iidx) for code, iidx in lcodind
                                       if code < 0 and len(iidx) != 1])
            if length >= 0 and length != len(keysset[0]):
                raise IlistError('length of Iindex and Ilist inconsistent')
            length = len(keysset[0])
        else:
            keysset = None
        # init primary
        primary = [(rang, iidx) for rang, (code, iidx) in zip(range(len(lcodind)), lcodind)
                   if code < 0 and len(iidx) != 1]
        for i, (rang, iidx) in zip(range(len(primary)), primary):
            if not flat:
                iidx.keys = keysset[i]
            self.lindex[lidx[rang]] = iidx
        # init secondary
        for i, (code, iidx) in zip(range(len(lcodind)), lcodind):
            if iidx.name is None or iidx.name == ES.defaultindex:
                iidx.name = 'i'+str(i)
            if len(iidx.codec) == 1:
                iidx.keys = [0] * length
                self.lindex[lidx[i]] = iidx
            elif code >= 0 and isinstance(self.lindex[lidx[i]], int):
                self._addiidx(lidx[i], code, iidx, codind, length)
            elif code < 0 and isinstance(self.lindex[lidx[i]], int):
                raise IlistError('Ilist not canonical')

    def _addiidx(self, rang, code, iidx, codind, length):
        '''creation derived or coupled Iindex and update lindex'''
        if isinstance(self.lindex[code], int):
            self._addiidx(code, codind[code][0],
                          codind[code][1], codind, length)
        if iidx.keys == list(range(len(iidx.codec))):
            # if len(iidx.codec) == length: #coupled format
            # coupled format
            if len(iidx.codec) == len(self.lindex[code].codec):
                self.lindex[rang] = Iindex(
                    iidx.codec, iidx.name, self.lindex[code].keys)
            else:  # derived format without keys
                parent = copy(self.lindex[code])
                parent.reindex()
                leng = len(parent.codec)
                keys = [(i*len(iidx.codec))//leng for i in range(leng)]
                self.lindex[rang] = Iindex(iidx.codec, iidx.name,
                                           Iindex.keysfromderkeys(parent.keys, keys))
        else:
            self.lindex[rang] = Iindex(iidx.codec, iidx.name,
                                       Iindex.keysfromderkeys(self.lindex[code].keys,
                                                              codind[rang][1].keys))

# %% special
    def __str__(self):
        '''return string format for var and lidx'''
        if self.lvar:
            stri = str(self.lvar[0]) + '\n'
        else:
            stri = ''
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

    def __eq__(self, other):
        ''' equal if all Iindex and var are equal'''
        return self.__class__.__name__ == other.__class__.__name__ \
            and self.lvarname == other.lvarname \
            and {idx in self.lindex for idx in other.lindex} in ({True}, set())

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
        if len(self) != 0 and len(self) != len(other) and len(other) != 0:
            raise IlistError("the sizes are not equal")
        otherc = copy(other)
        for idx in otherc.lindex:
            self.addindex(idx)
        if not self.lvarname:
            self.lvarname = other.lvarname
        return self

    def __copy__(self):
        ''' Copy all the data '''
        # return Ilist([copy(idx) for idx in self.lindex], var=self.lvarrow)
        return Ilist(self)

# %% property
    @property
    def complete(self):
        '''return a boolean (True if Ilist is complete and consistent)'''
        return self.lencomplete == len(self) and self.consistent

    @property
    def consistent(self):
        ''' True if all the record are different'''
        return max(Counter(zip(*self.iidx)).values()) == 1

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
    def idxname(self):
        ''' list of idx name'''
        return [idx.name for idx in self.lidx]

    @property
    def idxref(self):
        ''' list of idx parent row (idx row if linked)'''
        return [inf['parent'] if inf['typecoupl'] != 'linked' else
                inf['num'] for inf in self.indexinfos()]

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
    def keys(self):
        ''' list of keys for each index'''
        return [idx.keys for idx in self.lindex]

    @property
    def lencomplete(self):
        '''number of values if complete (prod(idxlen primary))'''
        return util.mul([self.idxlen[i] for i in self.primary])

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
    def lvar(self):
        '''list of var'''
        return [self.lindex[i] for i in self.lvarrow]

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
        # return [self.lname.index(name) for name not in self.idxvar]

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
        idxinfos = self.indexinfos()
        return [idxinfos.index(idx) for idx in idxinfos if idx['cat'] == 'primary']

    @property
    def setidx(self):
        '''list of codec for each idx'''
        return [idx.codec for idx in self.lidx]

    @property
    def tiidx(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iidx)))

    @property
    def textidx(self):
        '''list of values for each rec'''
        return util.transpose(self.extidx)

    @property
    def textidxext(self):
        '''list of val for each rec'''
        return util.transpose(self.extidxext)

    @property
    def typevalue(self):
        '''return typevalue calculated from Iindex name'''
        return [util.typename(name)for name in self.lname]

    @property
    def zip(self):
        '''return a zip format for textidx : tuple(tuple(rec))'''
        textidx = self.textidx
        return tuple(tuple(idx) for idx in textidx)
