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
import math 
import json
import csv
import cbor2

from esconstante import ES
from iindex import Iindex
from iindex_interface import IindexInterface, CborDecoder
from util import util
from ilist_interface import IlistInterface, IlistError
from ilist_structure import IlistStructure
from ilist_analysis import Analysis


class Ilist(IlistStructure, IlistInterface):
    # %% intro
    '''
    An `Ilist` is a representation of an indexed list.

    *Attributes (for @property see methods)* :

    - **lindex** : list of Iindex
    - **lvarname** : variable name (list of string)
    - **analysis** : Analysis object (data structure)

    The methods defined in this class are :

    *constructor (@classmethod))*

    - `Ilist.dic`
    - `Ilist.ext`
    - `Ilist.obj`
    - `Ilist.from_csv`
    - `Ilist.from_obj`
    - `Ilist.from_file`

    *dynamic value (getters @property)*

    - `Ilist.extidx`
    - `Ilist.extidxext`
    - `Ilist.idxname`
    - `Ilist.idxlen`
    - `Ilist.iidx`
    - `Ilist.keys`
    - `Ilist.lenindex`
    - `Ilist.lenidx`
    - `Ilist.lidx`
    - `Ilist.lidxrow`
    - `Ilist.lisvar`
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
    - `Ilist.to_dataframe`
    - `Ilist.view`
    - `Ilist.vlist`
    - `Ilist.voxel`
    '''
    def __init__(self, listidx=None, lvarname=None, reindex=True):
        '''
        Ilist constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of Iindex data
        - **lvarname** :  list (default None) - list of name of variable
        - **reindex** : boolean (default True) - if True, default codec for each Iindex'''

        self.name = self.__class__.__name__
        self.analysis = Analysis(self)
        self.lindex = []
        '''if not lvarname:
            self.lvarname = []
        elif not isinstance(lvarname, list):
            self.lvarname = [lvarname]
        else: 
            self.lvarname = lvarname'''
        if listidx.__class__.__name__ in ['Ilist', 'Observation']:
            self.lindex = [copy(idx) for idx in listidx.lindex]
            #self.lvarname = copy(listidx.lvarname)
            return
        if not listidx:
            return
        self.lindex = listidx
        if reindex:
            self.reindex()
        # %%% modif
        self.analysis._actualize()              
        #self.lvarname = self.analysis.lvarname
        return

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
        lvarname = []
        if listidx.__class__.__name__ == 'DataFrame':
            lindex = [Iindex(list(idx.cat.categories), name, list(idx.cat.codes),
                             lendefault=len(listidx), castobj=False)
                     for name, idx in listidx.astype('category').items()]
            return cls(lindex, lvarname=lvarname, reindex=reindex)
        
        if isinstance(listidx, dict):
            for idxname in listidx:
                var, idx = Iindex.from_dict_obj({idxname: listidx[idxname]}, 
                                                typevalue=typevalue, reindex=reindex)
                lindex.append(idx)
                if var: 
                    lvarname.append(idxname)
            return cls(lindex, lvarname=lvarname, reindex=reindex)

        if isinstance(listidx, list) and len(listidx) == 0:
            return cls()
        
        #decode: name, typevaluedec, codec, parent, keys, isfullindex, isparent, isvar
        lidx = [list(IindexInterface.decodeobj(idx, typevalue, context)) for idx in listidx]
        for ind in range(len(lidx)):
            if lidx[ind][0] is None or lidx[ind][0] == ES.defaultindex:
                lidx[ind][0] = 'i'+str(ind)
            if lidx[ind][1] is None:
                lidx[ind][1] = util.typename(lidx[ind][0], typevalue)
        name, typevaluedec, codec, parent, keys, isfullkeys, isparent, isvar =\
            tuple(zip(*lidx))

        leng = [len(cod) for cod in codec]
        fullmode = not max(isfullkeys) and max(leng) == min(leng)  # mode full : tous False
        defmode = min(isfullkeys)       # mode default : tous True (idem all(isfullkeys))
        #lvarname = [name[i] for i,val in enumerate(isvar) if val]

        # not max(isparent) : tous isparent = False
        #if not max(isparent) and ((fullmode and max(leng) == min(leng)) or defmode): # mode full ou mode default
        if not max(isparent) and (fullmode or defmode): # mode full ou mode default
            lindex = [Iindex(idx[2], idx[0], idx[4], idx[1], reindex=reindex) for idx in lidx]
            return cls(lindex, lvarname=lvarname, reindex=reindex)

        crossed = []
        #crossed : pas d'index (isfullindex false), pas de parent(isparent false)
        if not fullmode: #au moins un fullkeys ou une longueur différente
            if max(isfullkeys): 
                length = len(keys[isfullkeys.index(True)])
                crossed = [i for i, (isfullk, ispar, lengt) in 
                           enumerate(zip(isfullkeys, isparent, leng))
                           if not ispar and not isfullk and 1 < lengt < length]
            else: # max(leng) != min(leng)
                #sinon pas de fullindex => matrice et dérivés
                crossed = [i for i,(isfullk, ispar, lengt) in 
                           enumerate(zip(isfullkeys, isparent, leng))
                           if not ispar and not isfullk and 1 < lengt]
                lencrossed = [leng[ind] for ind in crossed]
                if max(lencrossed) == min(lencrossed):
                    length = lencrossed[0]
                    crossed = []
                else:
                    length = math.prod([leng[i] for i in crossed])
                    if length / max(lencrossed) == max(lencrossed):
                        length = max(lencrossed)
                        crossed = [i for i, (isfullk, ispar, lengt) in 
                                   enumerate(zip(isfullkeys, isparent, leng))
                                   if not ispar and not isfullk and 1 < lengt < length]                        
        '''if not fullmode or max(isvar): #au moins un fullkeys ou un var
            if not fullmode: 
                length = len(keys[isfullkeys.index(True)])
            else:
                length = leng[isvar.index(True)]
            crossed = [i for i, (isfullk, ispar, isvr, lengt) in 
                       enumerate(zip(isfullkeys, isparent, isvar, leng))
                       if not ispar and not isfullk and not isvr and 1 < lengt < length]
        #crossed : pas d'index (isfullindex false), pas de parent(isparent false)
        else: 
            #sinon pas de fullindex (mais un sans index) => matrice et dérivés
            crossed = [i for i,(isfullk, ispar, isvr, lengt) in 
                       enumerate(zip(isfullkeys, isparent, isvar, leng))
                       if not ispar and not isfullk and not isvr and lengt > 1]
                       #if not ispar and not isfullk and not isvr]
            lencrossed = [leng[ind] for ind in crossed]
            if max(lencrossed) == min(lencrossed):
                length = lencrossed[0]
                crossed = []
            else:
                length = math.prod([leng[i] for i in crossed])'''
        keyscross = util.canonorder([leng[i] for i in crossed])
        for ind in range(len(crossed)):
            lidx[crossed[ind]][4] = keyscross[ind] # keys

        for ind in range(len(lidx)):
            Ilist._init_keys(ind, lidx, length)
        lindex = [Iindex(idx[2], idx[0], idx[4], idx[1], reindex=reindex) for idx in lidx]
        return cls(lindex, lvarname=lvarname, reindex=False)
        
    @staticmethod
    def _init_keys(ind, lidx, leng):
        # codec: 2, parent: 3, keys: 4
        if lidx[ind][4] and (lidx[ind][3] is None or lidx[ind][3] < 0): 
            return
        if len(lidx[ind][2]) == 1:
            lidx[ind][4] = [0] * leng
            return 
        if lidx[ind][3] is None:
            raise IlistError('keys not referenced')
        if lidx[ind][3] < 0:
            lidx[ind][4] = list(range(leng))
            return
        if not lidx[lidx[ind][3]][4]:
            Ilist._init_keys(lidx[ind][3], lidx, leng)
        if not lidx[ind][4]:
            if len(lidx[ind][2]) == len(lidx[lidx[ind][3]][2]):    # coupled format
                lidx[ind][4] = lidx[lidx[ind][3]][4]
                return
            # derived format without keys
            lencodp = len(lidx[lidx[ind][3]][2])  # codec
            lidx[ind][4] = [(i*len(lidx[ind][2]))//lencodp for i in range(lencodp)]
            return
        # derived keys
        lidx[ind][4] = Iindex.keysfromderkeys(lidx[lidx[ind][3]][4], lidx[ind][4])
        return    
        
    @classmethod
    def dic(cls, idxdic=None, typevalue=ES.def_clsName, var=None, reindex=True):
        '''
        Ilist constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **var** :  int (default None) - row of the variable'''
        if not idxdic:
            return cls.ext(idxval=None, idxname=None, typevalue=typevalue, var=var,
                            reindex=reindex)
        if isinstance(idxdic, Ilist):
            return idxdic
        if not isinstance(idxdic, dict):
            raise IlistError("idxdic not dict")
        return cls.ext(idxval=list(idxdic.values()), idxname=list(idxdic.keys()),
                        typevalue=typevalue, var=var, reindex=reindex)

    @classmethod
    def ext(cls, idxval=None, idxname=None, typevalue=ES.def_clsName, var=None,
             reindex=True):
        '''
        Ilist constructor (external index).

        *Parameters*

        - **idxval** : list of Iindex or list of values (see data model)
        - **idxname** : list of string (default None) - list of Iindex name (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **var** :  int (default None) - row of the variable'''
        #print('debut ext')
        #t0 = time()

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
        lvarname = None 
        if not var is None:
            lvarname = idxname[var]
        lidx = [list(IindexInterface.decodeobj(idx, typevalue, context=False)) for idx in val]
        lindex = [Iindex(idx[2], name, list(range(length)), idx[1], lendefault=length, reindex=reindex) 
                  for idx, name in zip(lidx, idxname)]
        return cls(lindex, lvarname=lvarname, reindex=False)      

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
        return cls.ext(idxval, idxname, typevalue=None, var=var, reindex=True)

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
    def from_obj(cls, bsd=None, reindex=True, context=True):
        '''
        Generate an Ilist Object from a bytes, string or list value

        *Parameters*

        - **bsd** : bytes, string, DataFrame or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
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
        #return sum([hash(idx) for idx in self.lindex]) + hash(tuple(self.lvarname))

    def _hashi(self):
        '''return sum of all hashi(Iindex)'''
        '''return hash(tuple(tuple([idx._hashi() for idx in self.lindex]),
                          tuple([idx._hashi() for idx in self.lindex]),
                          tuple(self.lvarname)))'''
        return sum([idx._hashi() for idx in self.lindex])
        #return sum([idx._hashi() for idx in self.lindex]) + hash(tuple(self.lvarname))
        #return hash(tuple(self.values))
    

    def __eq__(self, other):
        ''' equal if hash values are equal'''
        return hash(self) == hash(other)
        '''return self.__class__.__name__ == other.__class__.__name__ \
            and self.lvarname == other.lvarname \
            and {idx in self.lindex for idx in other.lindex} in ({True}, set())'''

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

    """@property
    def crossed(self):
        ''' list of crossed idx'''
        return self.analysis.getcrossed()"""

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
    def primaryname(self):
        ''' list of primary name'''
        return [self.lidx[idx].name for idx in self.primary]

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
        # %%% modif
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
        # %%% modif
        return self.analysis.getprimary3()
        #return self.analysis.getprimary()

    @property
    def setidx(self):
        '''list of codec for each idx'''
        return [idx.codec for idx in self.lidx]

    @property
    def tiidx(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iidx)))

    @property
    def tiindex(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iindex)))

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
        if not textidx:
            return None
        return tuple(tuple(idx) for idx in textidx)
