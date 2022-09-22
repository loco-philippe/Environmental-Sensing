# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: philippe@loco-labs.io

The `ES.ilist` module contains the `Ilist` class.

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
#%% declarations
from collections import Counter
from copy import copy
import datetime, cbor2
import json
import csv
import math
from tabulate import tabulate
from ESconstante import ES
from ESValue import ESValue
from iindex import Iindex
from util import util, IindexEncoder, CborDecoder
import xarray
import numpy as np
import matplotlib.pyplot as plt

class Ilist:
#%% intro
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

    *selecting - infos methods*

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

    *add - update methods*

    - `Ilist.add`
    - `Ilist.addindex`
    - `Ilist.append`
    - `Ilist.delindex`
    - `Ilist.delrecord`
    - `Ilist.renameindex`
    - `Ilist.setvar`
    - `Ilist.setname`
    - `Ilist.updateindex`    
    
    *structure management - methods*

    - `Ilist.applyfilter`
    - `Ilist.coupling`
    - `Ilist.full`
    - `Ilist.getduplicates`
    - `Ilist.merge`
    - `Ilist.reindex`
    - `Ilist.reorder`
    - `Ilist.setfilter`
    - `Ilist.sort`
    - `Ilist.swapindex`
    - `Ilist.setcanonorder`
    - `Ilist.tostdcodec`
    
    *exports methods*

    - `Ilist.json`
    - `Ilist.plot`
    - `Ilist.to_obj`
    - `Ilist.to_csv`
    - `Ilist.to_file`
    - `Ilist.to_numpy`
    - `Ilist.to_xarray`
    - `Ilist.view`
    - `Ilist.vlist`
    - `Ilist.voxel`
    '''
    @classmethod
    def Idic(cls, idxdic=None, typevalue=ES.def_clsName, fullcodec=False, var=None):
        '''
        Ilist constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **fullcodec** : boolean (default False) - full codec if True
        - **var** :  int (default None) - row of the variable'''
        if not idxdic: return cls.Iext(idxval=None, idxname=None, typevalue=typevalue, 
                                          fullcodec=fullcodec, var=var)
        if isinstance(idxdic, Ilist): return idxdic
        if not isinstance(idxdic, dict): raise IlistError("idxdic not dict")
        return cls.Iext(list(idxdic.values()), list(idxdic.keys()), typevalue, fullcodec, var)

    @classmethod
    def Iext(cls, idxval=None, idxname=None, typevalue=ES.def_clsName, 
             fullcodec=False, var=None):
        '''
        Ilist constructor (external index).

        *Parameters*

        - **idxval** : list of Iindex or list of values (see data model)
        - **idxname** : list of string (default None) - list of Iindex name (see data model)
        - **typevalue** : str (default ES.def_clsName) - default value class (None or NamedValue)
        - **fullcodec** : boolean (default False) - full codec if True
        - **var** :  int (default None) - row of the variable'''
        #print('debut iext')
        #t0 = time()
        if idxname is None: idxname = []
        if idxval  is None: idxval  = []
        if not isinstance(idxval, list): return None
        #if len(idxval) == 0: return cls()
        val = []
        for idx in idxval:
            if not isinstance(idx, list): val.append([idx])
            else: val.append(idx)
        return cls(listidx=val, name=idxname, var=var, typevalue=typevalue, 
                   context=False)
        '''#if not isinstance(idxval[0], list): val = [[idx] for idx in idxval]
        #else:                               val = idxval
        name = ['i' + str(i) for i in range(len(val))]
        for i in range(len(idxname)): 
            if isinstance(idxname[i], str): name[i] = idxname[i]
        #print('fin init iext', time()-t0)
        lidx = [Iindex.Iext(idx, name, typevalue, fullcodec) 
                    for idx, name in zip(val, name)]
        #print('fin lidx iext', time()-t0)
        return cls(lidx, var=var)'''

    @classmethod
    def from_csv(cls, filename='ilist.csv', var=None, header=True, nrow=None,
                 optcsv = {'quoting': csv.QUOTE_NONNUMERIC}, dtype=ES.def_dtype):
        '''
        Ilist constructor (from a csv file). Each column represents index values.

        *Parameters*

        - **filename** : string (default 'ilist.csv'), name of the file to read
        - **var** : integer (default None). column row for variable data
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **nrow** : integer (default None). Number of row. If None, all the row else nrow
        - **dtype** : list of string (default None) - data type for each column (default str)
        - **optcsv** : dict (default : quoting) - see csv.reader options'''
        if not optcsv: optcsv = {}
        if not nrow: nrow = -1
        with open(filename, newline='') as f:
            reader = csv.reader(f, **optcsv)
            irow = 0
            for row in reader:
                if   irow == nrow: break 
                elif irow == 0:
                    if dtype and not isinstance(dtype, list): dtype = [dtype] * len(row)
                    idxval  = [[] for i in range(len(row))]
                    idxname = None
                if irow == 0 and header:  idxname = row
                else:
                    if not dtype: 
                        for i in range(len(row)) : idxval[i].append(row[i])
                    else:
                        for i in range(len(row)) : idxval[i].append(util.cast(row[i], dtype[i]))
                irow += 1
                
        return cls.Iext(idxval, idxname, typevalue=None, var=var)
            
    @classmethod
    def from_file(cls, file, forcestring=False) :
        '''
        Generate `Ilist` object from file storage.

         *Parameters*

        - **file** : string - file name (with path)
        - **forcestring** : boolean (default False) - if True, forces the UTF-8 data format, else the format is calculated

        *Returns* : Ilist object'''
        with open(file, 'rb') as f: btype = f.read(1)
        if btype==bytes('[', 'UTF-8') or forcestring:
            with open(file, 'r', newline='') as f: bjson = f.read()
        else:
            with open(file, 'rb') as f: bjson = f.read()
        return cls.from_obj(bjson)

    @classmethod
    def Iobj(cls, bs=None, reindex=True, context=True):
        '''
        Generate a new Object from a bytes, string or list value

        *Parameters*

        - **bs** : bytes, string or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        return cls.from_obj(bs, reindex=reindex, context=context)

    @classmethod
    def from_obj(cls, bs=None, reindex=True, context=True):
        '''
        Generate an Ilist Object from a bytes, string or list value

        *Parameters*

        - **bs** : bytes, string or list data to convert
        - **reindex** : boolean (default True) - if True, default codec for each Iindex
        - **context** : boolean (default True) - if False, only codec and keys are included'''
        if not bs: bs = []
        if   isinstance(bs, bytes): lis = cbor2.loads(bs)
        elif isinstance(bs, str)  : lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list) : lis = bs
        else: raise IlistError("the type of parameter is not available")
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
        #print('debut')
        #t0 = time()

        #init self.lidx
        self.name = self.__class__.__name__
        if not isinstance(name, list): name = [name]
        if listidx.__class__.__name__ in ['Ilist','Obs']: 
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.lvarname = copy(listidx.lvarname)
            return
        if not listidx: 
            self.lindex = []
            self.lvarname = []
            return
        if not isinstance(listidx, list) or not isinstance(listidx[0], (list, Iindex)): 
            #listidx = [listidx]
            listidx = [[idx] for idx in listidx]
        typeval = [typevalue for i in range(len(listidx))]
        for i in range(len(name)): 
            typeval[i] = util.typename(name[i], typeval[i])          
        if len(listidx) == 1:
            code, idx = Iindex.from_obj(listidx[0], typevalue=typeval[0], context=context)
            if len(name) > 0 and name[0]: idx.name = name[0]
            if idx.name is None or idx.name == ES.defaultindex: idx.name = 'i0'
            self.lindex = [idx]
            self.lvarname = [idx.name]
            return            
        #print('init', time()-t0)
        
        #init
        if       isinstance(var, list): idxvar = var
        elif not isinstance(var, int) or var < 0: idxvar = []
        else: idxvar = [var]
        codind = [Iindex.from_obj(idx, typevalue=typ, context=context) 
                  for idx, typ in zip(listidx, typeval)]
        for ii, (code, idx) in zip(range(len(codind)), codind):
            if len(name) > ii and name[ii]: idx.name = name[ii]
            if idx.name is None or idx.name == ES.defaultindex: idx.name = 'i'+str(ii)
            if code == ES.variable and not idxvar: idxvar = [ii]
        self.lindex = list(range(len(codind)))    
        lcodind = [codind[i] for i in range(len(codind)) if i not in idxvar]
        lidx    = [i         for i in range(len(codind)) if i not in idxvar]
        #print('fin init', time()-t0)
        
        #init length
        if not length:  length  = -1
        #leng = [len(iidx) for code, iidx in codind if code < 0 and len(iidx) != 1]
        leng = [len(iidx) for code, iidx in codind if code < 0 and len(iidx) > 0]
        leng2 = [l for l in leng if l > 1]

        if not leng: length = 0
        elif not leng2: length = 1 
        #if max(leng) == min(leng) and length < 0: length = max(leng)
        elif max(leng2) == min(leng2) and length < 0: length = max(leng2)
        
        '''#leng = [len(iidx) for code, iidx in codind if code < 0 and len(iidx) > 1] #!!!!
        
        #leng = [len(iidx) for code, iidx in codind if code < 0]
        #if not leng: leng = [1] #!!!!!
        if not leng: leng = [0]
        #if max(leng) == min(leng) and length < 0: length = max(leng)
        if max(leng2) == min(leng2) and length < 0: length = max(leng2)
        '''
        if idxvar: length = len(codind[idxvar[0]][1])
        if length == 0 :
            self.lvarname = [codind[i][1].name for i in idxvar]
            #self.lindex = [[] for i in range(len(listidx))]
            self.lindex = [iidx for code, iidx in codind]
            return
        #flat = length == max(leng) == min(leng)
        flat = True
        if leng2: flat = length == max(leng2) == min(leng2)
        if not flat:
            keysset = util.canonorder([len(iidx) for code, iidx in lcodind 
                         if code < 0 and len(iidx) != 1])
            if length >= 0 and length != len(keysset[0]): 
                raise IlistError('length of Iindex and Ilist inconsistent')
            else: length = len(keysset[0])
        #print('fin leng', time()-t0)
        
        #init primary               
        primary = [(rang, iidx) for rang, (code, iidx) in zip(range(len(lcodind)), lcodind)
                   if code < 0 and len(iidx) != 1]
        for ip, (rang, iidx) in zip(range(len(primary)), primary):
            if not flat: iidx.keys = keysset[ip]
            self.lindex[lidx[rang]] = iidx
        #print('fin primary', time()-t0)
        
        #init secondary               
        for ii, (code, iidx) in zip(range(len(lcodind)), lcodind):
            if iidx.name is None or iidx.name == ES.defaultindex: iidx.name = 'i'+str(ii)
            if len(iidx.codec) == 1: 
                iidx.keys = [0] * length
                self.lindex[lidx[ii]] = iidx
            elif code >=0 and isinstance(self.lindex[lidx[ii]], int): 
                self._addiidx(lidx[ii], code, iidx, codind, length)
            elif code < 0 and isinstance(self.lindex[lidx[ii]], int): 
                raise IlistError('Ilist not canonical')
        #print('fin secondary', time()-t0)
        
        #init variable
        for i in idxvar: self.lindex[i] = codind[i][1]
        self.lvarname = [codind[i][1].name for i in idxvar]
        if reindex: self.reindex()
        return None
                
    def _addiidx(self, rang, code, iidx, codind, length):
        '''creation derived or coupled Iindex and update lindex'''
        if isinstance(self.lindex[code], int): 
            self._addiidx(code, codind[code][0], codind[code][1], codind, length)
        if iidx.keys == list(range(len(iidx.codec))):
            #if len(iidx.codec) == length: #coupled format
            if len(iidx.codec) == len(self.lindex[code].codec): #coupled format
                self.lindex[rang] = Iindex(iidx.codec, iidx.name, self.lindex[code].keys)
            else:  #derived format without keys
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

#%% special
    def __str__(self):
        '''return string format for var and lidx'''
        if self.lvar: stri = str(self.lvar[0]) + '\n'
        else: stri = ''
        for idx in self.lidx: stri += str(idx)
        return stri

    def __repr__(self):
        '''return classname, number of value and number of indexes'''
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(self.lenindex) + ']'

    def __len__(self):
        ''' len of values'''
        if not self.lindex: return 0
        return len(self.lindex[0])

    def __contains__(self, item):
        ''' list of lindex values'''
        return item in self.lindex

    def __getitem__(self, ind):
        ''' return value record (value conversion)'''
        res = [idx[ind] for idx in self.lindex]
        if len(res) == 1: return res[0]
        return res

    def __setitem__(self, ind, item):
        ''' modify the Iindex values for each Iindex at the row ind'''
        if not isinstance(item, list): item = [item]
        for val, idx in zip(item, self.lindex): idx[ind] = val
            
    def __delitem__(self, ind):
        ''' remove all Iindex item at the row ind'''
        for idx in self.lindex: del(idx[ind])
        
    def __hash__(self): 
        '''return sum of all hash(Iindex)'''
        return sum([hash(idx) for idx in self.lindex])

    def __eq__(self, other):
        ''' equal if all Iindex and var are equal'''
        return self.__class__.__name__ == other.__class__.__name__ \
            and self.lvarname == other.lvarname \
            and set([idx in self.lindex for idx in other.lindex]) in ({True}, set())
    
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
        for idx in otherc.lindex: self.addindex(idx)
        if not self.lvarname: self.lvarname = other.lvarname
        return self

    def __copy__(self):
        ''' Copy all the data '''
        #return Ilist([copy(idx) for idx in self.lindex], var=self.lvarrow)
        return Ilist(self)

#%% property
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
        #return [self.lname.index(name) for name not in self.idxvar]
    
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
    
    #%% methods
    def add(self, other, name=False, solve=True):
        ''' Add other's values to self's values for each index 

        *Parameters*

        - **other** : Ilist object to add to self object
        - **name** : Boolean (default False) - Add values with same index name (True) or 
        same index row (False)

        *Returns* : self '''      
        if self.lenindex != other.lenindex: raise IlistError('length are not identical')
        if name and sorted(self.lname) != sorted(other.lname): raise IlistError('name are not identical')
        for i in range(self.lenindex): 
            if name: self.lindex[i].add(other.lindex[other.lname.index(self.lname[i])], 
                                        solve=solve)
            else: self.lindex[i].add(other.lindex[i], solve=solve)
        if not self.lvarname: self.lvarname = other.lvarname
        return self        

    def addindex(self, index, first=False, merge=False, update=False):
        '''add a new index.

        *Parameters*

        - **index** : Iindex - index to add (can be index representation)
        - **first** : If True insert index at the first row, else at the end
        - **merge** : create a new index if merge is False
        - **update** : if True, update actual values if index name is present (and merge is True)

        *Returns* : none '''      
        idx = Iindex.Iobj(index)
        idxname = self.lname
        if len(idx) != len(self) and len(self) > 0: 
            raise IlistError('sizes are different')
        if not idx.name in idxname: 
            if first: self.lindex.insert(0, idx)
            else: self.lindex.append(idx)
        elif idx.name in idxname and not merge:
            while idx.name in idxname: idx.name += '(2)'
            if first: self.lindex.insert(0, idx)
            else: self.lindex.append(idx)
        elif update:
            self.lindex[idxname.index(idx.name)].setlistvalue(idx.values)
            
    def append(self, record, unique=False, typevalue=ES.def_clsName):
        '''add a new record.

        *Parameters*

        - **record** :  list of new index values to add to Ilist
        - **unique** :  boolean (default False) - Append isn't done if unique is True and record present
        - **typevalue** : list of string (default ES.def_clsName) - typevalue to convert record or
         string if typevalue is not define in indexes

        *Returns* : list - key record'''
        if self.lenindex != len(record): raise('len(record) not consistent')
        if not isinstance(typevalue, list): typevalue = [typevalue] * len(record)
        typevalue = [util.typename(self.lname[i], typevalue[i]) for i in range(self.lenindex)]
        record = [util.castval(val, typ) for val, typ in zip(record, typevalue)]
        '''for i in range(self.lenindex):
            if not typevalue[i] and self.typevalue[i]: typevalue[i] = ES.valname[self.typevalue[i]]
        #if dtype and not isinstance(dtype, list): dtype = [dtype] * len(record)
        #if dtype: record = [util.cast(value, typ) for value, typ in zip(record, dtype)]
        record = [util.cast(value, typ) for value, typ in zip(record, typevalue)]'''
        if self.isinrecord(self.idxrecord(record), False) and unique: return None
        return [self.lindex[i].append(record[i]) for i in range(self.lenindex)]

    def applyfilter(self, reverse=False, filtname=ES.filter, delfilter=True, inplace=True):
        '''delete records with defined filter value.
        Filter is deleted after record filtering.

        *Parameters*

        - **reverse** :  boolean (default False) - delete record with filter's value is reverse
        - **filtname** : string (default ES.filter) - Name of the filter Iindex added 
        - **delfilter** :  boolean (default True) - If True, delete filter's Iindex
        - **inplace** : boolean (default True) - if True, filter is apply to self,

        *Returns* : self or new Ilist'''
        if inplace: il = self
        else: il = copy(self)
        if not filtname in il.lname: return False
        ifilt = il.lname.index(filtname)        
        il.sort([ifilt], reverse=not reverse, func=None)
        minind = min(il.lindex[ifilt].recordfromvalue(reverse))
        for idx in il.lindex: del(idx.keys[minind:])
        if delfilter: self.delindex(filtname)
        il.reindex()
        return il
    
    def couplingmatrix(self, default=False, file=None, att='rate'):
        '''return a matrix with coupling infos between each idx.
        One info can be stored in a file (csv format).

        *Parameters*

        - **default** : comparison with default codec 
        - **file** : string (default None) - name of the file to write the matrix
        - **att** : string - name of the info to store in the file

        *Returns* : array of array of dict'''
        lenidx = self.lenidx
        mat = [[None for i in range(lenidx)] for i in range(lenidx)]
        for i in range(lenidx):
            for j  in range(i, lenidx): 
                mat[i][j] = self.lidx[i].couplinginfos(self.lidx[j], default=default)
            for j  in range(i): 
                mat[i][j] = copy(mat[j][i])
                if   mat[i][j]['typecoupl'] == 'derived': mat[i][j]['typecoupl'] = 'derive'
                elif mat[i][j]['typecoupl'] == 'derive' : mat[i][j]['typecoupl'] = 'derived'                
                elif mat[i][j]['typecoupl'] == 'linked' : mat[i][j]['typecoupl'] = 'link'
                elif mat[i][j]['typecoupl'] == 'link'   : mat[i][j]['typecoupl'] = 'linked'
        if file:
            with open(file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.idxname)
                for i in range(lenidx): 
                    writer.writerow([mat[i, j][att] for j in range(lenidx)])
                writer.writerow(self.idxlen)
        return mat

    def coupling(self, mat=None, derived=True, rate=0.1):  
        '''Transform idx with low rate in coupled or derived indexes (codec extension).

        *Parameters*

        - **mat** : array of array (default None) - coupling matrix 
        - **rate** : integer (default 0.1) - threshold to apply coupling.
        - **derived** : boolean (default : True).If True, indexes are derived, else coupled.

        *Returns* : list - coupling infos for each idx'''
        infos = self.indexinfos(mat=mat)  
        coupl = True
        while coupl:
            coupl = False
            for i in range(len(infos)):
                if infos[i]['typecoupl'] != 'coupled' and (infos[i]['typecoupl'] 
                    not in ('derived', 'unique') or not derived) and infos[i]['linkrate'] < rate: 
                    self.lidx[infos[i]['parent']].coupling(self.lidx[i], derived=derived)
                    coupl = True
            infos = self.indexinfos()  
        return infos
        
    def delrecord(self, record, extern=True):
        '''remove a record.

        *Parameters*

        - **record** :  list - index values to remove to Ilist
        - **extern** : if True, compare record values to external representation of self.value, 
        else, internal
        
        *Returns* : row deleted'''
        self.reindex()
        reckeys = self.valtokey(record, extern=extern)
        if None in reckeys: return None
        row = self.tiidx.index(reckeys)
        for idx in self: del(idx[row])
        return row
        
    def delindex(self, indexname):
        '''remove an index.

        *Parameters*

        - **indexname** : string - name of index to remove

        *Returns* : none '''      
        self.lindex.pop(self.lname.index(indexname))

    def full(self, reindex=False, indexname=None, fillvalue='-', fillextern=True, 
             inplace=True, complete=True):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **indexname** : list of string - name of indexes to transform
        - **reindex** : boolean (default False) - if True, set default codec before transformation
        - **fillvalue** : object value used for var extension
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **inplace** : boolean (default True) - if True, filter is apply to self,
        - **complete** : boolean (default True) - if True, Iindex are ordered in canonical order

        *Returns* : self or new Ilist'''
        if inplace: il = self
        else: il = copy(self)
        if not indexname: primary = il.primary
        else: primary = [il.idxname.index(name) for name in indexname]
        secondary = [idx for idx in range(il.lenidx) if idx not in primary]
        if reindex: il.reindex()
        keysadd = util.idxfull([il.lidx[i] for i in primary])
        if not keysadd or len(keysadd) == 0: return il
        leninit = len(il)
        lenadd  = len(keysadd[0])
        inf = il.indexinfos()
        for i,j in zip(primary, range(len(primary))):
            if      inf[i]['cat'] == 'unique': il.lidx[i].keys += [0] * lenadd
            else:   il.lidx[i].keys += keysadd[j]
        for i in secondary:
            if      inf[i]['cat'] == 'unique': il.lidx[i].keys += [0] * lenadd
            else:   il.lidx[i].tocoupled(il.lidx[inf[i]['parent']], coupling=False)  
        for i in range(il.lenidx):
            if len(il.lidx[i].keys) != leninit + lenadd:
                raise IlistError('primary indexes have to be present')
        if il.lvarname:
            il.lvar[0].keys += [len(il.lvar[0].codec)] * len(keysadd[0])
            if fillextern: il.lvar[0].codec.append(util.castval(fillvalue, 
                             util.typename(il.lvarname[0], ES.def_clsName)))
            else: il.lvar[0].codec.append(fillvalue)
            #il.lvar[0].codec.append(util.cast(fillvalue, ES.def_dtype))
        if complete : il.setcanonorder()
        return il

    def getduplicates(self, indexname=None, resindex=None):
        '''check duplicate cod in a list of indexes. Result is add in a new index or returned.

        *Parameters*

        - **indexname** : list of string - name of indexes to check
        - **resindex** : string (default None) - Add a new index with check result

        *Returns* : list of int - list of rows with duplicate cod '''   
        if not indexname: primary = self.primary
        else: primary = [self.idxname.index(name) for name in indexname]
        duplicates = []
        for idx in primary: duplicates += self.lidx[idx].getduplicates()
        if resindex and isinstance(resindex, str):
            newidx = Iindex([True] * len(self), name=resindex)
            for item in duplicates: newidx[item] = False
            self.addindex(newidx)
        return tuple(set(duplicates))
            
    def iscanonorder(self):
        '''return True if primary indexes have canonical ordered keys'''
        primary = self.primary
        canonorder = util.canonorder([len(self.lidx[idx].codec) for idx in primary])
        return canonorder == [self.lidx[idx].keys for idx in primary]

    def isinrecord(self, record, extern=True):
        '''Check if record is present in self.

        *Parameters*

        - **record** : list - value for each Iindex
        - **extern** : if True, compare record values to external representation of self.value, 
        else, internal

        *Returns boolean* : True if found'''
        if extern: return record in self.textidxext
        return record in self.textidx
    
    def idxrecord(self, record):
        '''return rec array (without variable) from complete record (with variable)'''
        return [record[self.lidxrow[i]] for i in range(len(self.lidxrow))]
    
    def indexinfos(self, keys=None, mat=None, default=False, base=False):
        '''return an array with infos of each index :
            - num, name, cat, typecoupl, diff, parent, pname, pparent, linkrate
            - lencodec, min, max, typecodec, rate, disttomin, disttomax (base info)

        *Parameters*

        - **keys** : list (default none) - list of information to return (reduct dict), all if None
        - **default** : build infos with default codec if new coupling matrix is calculated
        - **mat** : array of array (default None) - coupling matrix 
        - **base** : boolean (default False) - if True, add Iindex infos

        *Returns* : array'''
        infos = [{} for i in range(self.lenidx)]
        if not mat: mat = self.couplingmatrix(default=default)
        for i in range(self.lenidx):
            infos[i]['num']  = i
            infos[i]['name'] = self.idxname[i]
            minrate = 1.00
            mindiff = len(self)
            disttomin = None 
            minparent = i
            infos[i]['typecoupl'] = 'null'
            for j in range(self.lenidx):
                if mat[i][j]['typecoupl'] == 'derived': 
                    minrate = 0.00
                    if mat[i][j]['diff'] < mindiff:
                        mindiff = mat[i][j]['diff'] 
                        minparent = j 
                elif mat[i][j]['typecoupl'] == 'linked' and minrate > 0.0:
                    if not disttomin or mat[i][j]['disttomin'] < disttomin:
                        disttomin = mat[i][j]['disttomin']
                        minrate = mat[i][j]['rate']
                        minparent = j
                if j < i:
                    if mat[i][j]['typecoupl'] == 'coupled':
                        minrate = 0.00
                        minparent = j
                        break
                    elif mat[i][j]['typecoupl'] == 'crossed' and minrate > 0.0:
                        if not disttomin or mat[i][j]['disttomin'] < disttomin:
                            disttomin = mat[i][j]['disttomin']
                            minrate = mat[i][j]['rate']
                            minparent = j
            if self.lidx[i].infos['typecodec'] == 'unique':
                infos[i]['cat']           = 'unique'
                infos[i]['typecoupl']     = 'unique'
                infos[i]['parent']        = i    
            elif minrate == 0.0: 
                infos[i]['cat']           = 'secondary'
                infos[i]['parent']        = minparent
            else: 
                infos[i]['cat']           = 'primary'
                infos[i]['parent']        = minparent                         
                if minparent == i: 
                    infos[i]['typecoupl'] = 'crossed'
            if minparent != i: 
                infos[i]['typecoupl']     = mat[i][minparent]['typecoupl']
            infos[i]['linkrate']          = round(minrate, 2)
            infos[i]['pname']             = self.idxname[infos[i]['parent']]
            infos[i]['pparent']           = 0
            if base: infos[i]            |= self.lidx[i].infos
        for i in range(self.lenidx): util.pparent(i, infos)
        if not keys: return infos
        return [{k:v for k,v in inf.items() if k in keys} for inf in infos]

    def indicator(self, fullsize=None, size=None, indexinfos=None):
        '''generate Ilist indicators: ol (object lightness), ul (unicity level), gain (sizegain)
        
        *Parameters*

        - **fullsize** : int (default none) - size with fullcodec
        - **size** : int (default none) - size with existing codec
        - **indexinfos** : list (default None) - indexinfos data

        *Returns* : dict'''        
        if not indexinfos: indexinfos = self.indexinfos()
        if not fullsize: fullsize = len(self.to_obj(indexinfos=indexinfos, encoded=True, fullcodec=True))
        if not size:     size     = len(self.to_obj(indexinfos=indexinfos, encoded=True))
        lenidx = self.lenidx
        nv = len(self) * (lenidx + 1)
        sv = fullsize / nv
        nc = sum(self.idxlen) + lenidx
        if nv != nc: 
            sc = (size - nc * sv) / (nv - nc)
            ol = sc / sv
        else: ol = None
        return {'init values': nv, 'mean size': round(sv, 3),
                'unique values': nc, 'mean coding size': round(sc, 3), 
                'unicity level': round(nc / nv, 3), 'object lightness': round(ol, 3),
                'gain':round((fullsize - size) / fullsize, 3)}
        
    def json(self, **kwargs):
        '''
        Return json dict, json string or Cbor binary.

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (bynary if True, dict else)
        - **encode_format** : string (default 'json') - choice for return format (json, bson or cbor)
        - **json_res_index** : default False - if True add the index to the value
        - **order** : default [] - list of ordered index
        - **codif** : dict (default {}). Numerical value for string in CBOR encoder

        *Returns* : string or dict'''
        return self.to_obj(**kwargs)

    def keytoval(self, listkey, extern=True):
        '''
        convert a keys list (key for each idx) to a values list (value for each idx).

        *Parameters*

        - **listkey** : key for each idx
        - **extern** : boolean (default True) - if True, compare rec to val else to values 
        
        *Returns*

        - **list** : value for each index'''
        return [idx.keytoval(key, extern=extern) for idx, key in zip(self.lidx, listkey)] 
    
    def loc(self, rec, extern=True, row=False):
        '''
        Return variable value or row corresponding to a list of idx values.

        *Parameters*

        - **rec** : list - value for each idx
        - **extern** : boolean (default True) - if True, compare rec to val else to values 
        - **row** : Boolean (default False) - if True, return list of row, else list of variable values
        
        *Returns*

        - **object** : variable value or None if not found'''
        locrow = list(set.intersection(*[set(self.lidx[i].loc(rec[i], extern)) 
                                       for i in range(self.lenidx)]))
        if row: return locrow
        else: return self.lvar[0][tuple(locrow)]
        '''try:
            if extern: 
                row = self.textidxext.index(rec)
            else: 
                row = self.textidx.index(rec)
        except: return None
        return self.lvar[0][row]'''

    def merge(self, name='merge', fillvalue=math.nan, mergeidx=False, updateidx=False):
        '''
        Merge method replaces Ilist objects included in variable data into its constituents.

        *Parameters*

        - **name** : str (default 'merge') - name of the new Ilist object
        - **fillvalue** : object (default nan) - value used for the additional data 
        - **mergeidx** : create a new index if mergeidx is False
        - **updateidx** : if True (and mergeidx is True), update actual values if index name is present 
        
        *Returns*

        - **Ilist** : merged Ilist '''     
        #if len(self.lvarname) == 0: fillvalue = util.castval(fillvalue, ES.def_clsName)
        #else: fillvalue = util.castval(fillvalue, util.typename(self.lvarname[0], 
        #                                                        ES.def_clsName))
        #fillvalue = util.cast(fillvalue, ES.def_dtype)
        find = True
        ilm = copy(self)
        nameinit = ilm.idxname
        while find:
            find = False
            for i in range(len(ilm)):
                if not ilm.lvar[0].values[i].__class__.__name__ in ['Ilist', 'Obs']: continue
                find = True
                il = ilm.lvar[0].values[i].merge()
                ilname = il.idxname
                record = ilm.recidx(i, extern=False)
                for val, j in zip(reversed(record), reversed(range(len(record)))): # Ilist pere
                    nameidx = ilm.lidx[j].name
                    updidx = nameidx in nameinit and not updateidx
                    il.addindex ([nameidx, [val] * len(il)], first=True,
                                          merge=mergeidx, update=updidx) # ajout des index au fils
                for name in ilname:
                    fillval = util.castval(fillvalue, util.typename(name, ES.def_clsName))
                    ilm.addindex([name, [fillval] * len(ilm)], 
                                          merge=mergeidx, update=False) # ajout des index au père
                del(ilm[i])
                il.renameindex(il.lvarname[0], ilm.lvarname[0]) 
                ilm += il
                break
        return ilm

    def merging(self, listname=None):
        ''' add a new index in Ilist object build with indexes define in listname'''
        self.addindex(Iindex.merging([self.nindex(name) for name in listname]))
        return None
    
    def nindex(self, name):
        ''' index with name equal to attribute name'''
        if name in self.lname: return self.lindex[self.lname.index(name)]
        return None
    
    def plot(self, order=None, line=True, size=5, marker='o', maxlen=20):
        '''
        This function visualize data with line or colormesh.

        *Parameters*

        - **line** : Boolean (default True) - Choice line or colormesh.
        - **order** : list (defaut None) - order of the axes (x, y, hue or col)
        - **size** : int (defaut 5) - plot size
        - **marker** : Char (default 'o') - Symbol for each point.
        - **maxlen** : Integer (default 20) - maximum length for string

        *Returns*

        - **None**  '''
        if not self.consistent : return
        xa = self.to_xarray(numeric = True, lisfunc=[util.cast], 
                             dtype='str', maxlen=maxlen)
        if not order: order = [0,1,2]
        
        if   len(xa.dims) == 1:
            xa.plot.line(x=xa.dims[0]+'_row', size=size, marker=marker)
        elif len(xa.dims) == 2 and line:
            xa.plot.line(x=xa.dims[order[0]]+ '_row',
                xticks=list(xa.coords[xa.dims[0]+'_row'].values),
                #hue=xa.dims[order[1]]+'_row', size=size, marker=marker)
                hue=xa.dims[order[1]], size=size, marker=marker)
        elif len(xa.dims) == 2 and not line:
            xa.plot(x=xa.dims[order[0]]+'_row', y=xa.dims[order[1]]+'_row',
                xticks=list(xa.coords[xa.dims[order[0]]+'_row'].values),
                yticks=list(xa.coords[xa.dims[order[1]]+'_row'].values),
                size = size)
        elif len(xa.dims) == 3 and line:
            xa.plot.line(x=xa.dims[order[0]]+ '_row', col=xa.dims[order[1]],
                xticks=list(xa.coords[xa.dims[order[0]]+'_row'].values),
                hue=xa.dims[order[2]], col_wrap=2, size=size, marker=marker)
        elif len(xa.dims) == 3 and not line:
            xa.plot(x=xa.dims[order[0]]+'_row', y=xa.dims[order[1]]+'_row', 
                xticks=list(xa.coords[xa.dims[order[0]]+'_row'].values),
                yticks=list(xa.coords[xa.dims[order[1]]+'_row'].values),
                col=xa.dims[order[2]], col_wrap=2, size=size)
        plt.show()
        return {xa.dims[i]: list(xa.coords[xa.dims[i]].values) for i in range(len(xa.dims))}

    def record(self, row, extern=True):
        '''return the record at the row
           
        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val record else value record

        *Returns*

        - **list** : val record or value record'''
        if extern: return [idx.valrow(row) for idx in self.lindex]
        #if extern: return [idx.val[row] for idx in self.lindex]
        return [idx.values[row] for idx in self.lindex]
    
    def recidx(self, row, extern=True):
        '''return the list of idx val or values at the row
           
        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for idx'''
        #if extern: return [idx.val[row] for idx in self.lidx]
        if extern: return [idx.valrow(row) for idx in self.lidx]
        return [idx.values[row] for idx in self.lidx]

    def recvar(self, row, extern=True):
        '''return the list of var val or values at the row
           
        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for var'''
        #if extern: return [idx.val[row] for idx in self.lidx]
        if extern: return [idx.valrow(row) for idx in self.lvar]
        return [idx.values[row] for idx in self.lvar]

    def reindex(self):
        '''Calculate a new default codec for each index (Return self)'''
        for idx in self.lindex: idx.reindex()
        return self       

    def renameindex(self, oldname, newname):
        '''replace an index name 'oldname' by a new one 'newname'. '''
        for i in range(self.lenindex):
            if self.lname[i] == oldname: self.lindex[i].setname(newname)
        for i in range(len(self.lvarname)):
            if self.lvarname[i] == oldname: self.lvarname[i] = newname

    def reorder(self, recorder=None):
        '''Reorder records in the order define by 'recorder' '''
        if recorder is None or set(recorder) != set(range(len(self))): return
        for idx in self.lindex: idx.keys = [idx.keys[i] for i in recorder]
        return None
        
    def setcanonorder(self):
        '''Set the canonical index order : primary - secondary/unique - variable.
        Set the canonical keys order : ordered keys in the first columns'''
        order = [self.lidxrow[idx] for idx in self.primary]
        order += [idx for idx in self.lidxrow if not idx in order]
        order += self.lvarrow
        '''for i in self.lidxrow: 
            if not i in order: order.append(i)
        for i in self.lvarrow: order.append(i)'''
        self.swapindex(order)
        self.sort()
        return self
        
    def setfilter(self, filt=None, first=False, filtname=ES.filter):
        '''Add a filter index with boolean values
           
        - **filt** : list of boolean - values of the filter idx to add
        - **first** : boolean (default False) - If True insert index at the first row, else at the end
        - **filtname** : string (default ES.filter) - Name of the filter Iindex added 

        *Returns* : none'''
        if not filt: filt = [True] * len(self)
        idx = Iindex(filt, name=filtname)
        idx.reindex()
        if not idx.cod in ([True, False], [False, True], [True], [False]):
            raise IlistError('filt is not consistent')
        if ES.filter in self.lname: self.delindex(ES.filter)
        self.addindex(idx, first=first)
                
    def setname(self, listname=None):
        '''Update Iindex name by the name in listname'''
        for i in range(min(self.lenindex, len(listname))):
            self.lindex[i].name = listname[i]

    def setvar(self, var=None):
        '''Define a var index by the name or the index row'''
        if var is None: self.lvarname = []
        elif isinstance(var, int) and var >= 0 and var < self.lenindex: 
            self.lvarname = [self.lname[var]]
        elif isinstance(var, str) and var in self.lname:
            self.lvarname = [var]
        else: raise IlistError('var is not consistent with Ilist')

    def sort(self, order=None, reverse=False, func=str):
        '''Sort data following the index order and apply the ascending or descending 
        sort function to values.
        
        *Parameters*

        - **order** : list (default None)- new order of index to apply. If None or [], 
        the sort function is applied to the existing order of indexes.
        - **reverse** : boolean (default False)- ascending if True, descending if False
        - **func**    : function (default str) - parameter key used in the sorted function

        *Returns* : None'''
        if not order: order = []
        orderfull = order + list(set(range(self.lenindex)) - set(order))
        for idx in [self.lindex[i] for i in order]:
            idx.reindex(codec=sorted(idx.codec, key=func))
        newidx = util.transpose(sorted(util.transpose(
            [self.lindex[orderfull[i]].keys for i in range(self.lenindex)]), 
            reverse=reverse))
        for i in range(self.lenindex): self.lindex[orderfull[i]].keys = newidx[i]

    def swapindex(self, order):
        '''
        Change the order of the index .

        *Parameters*

        - **order** : list of int - new order of index to apply.

        *Returns* : none '''
        if self.lenindex != len(order): raise IlistError('length of order and Ilist different')
        self.lindex=[self.lindex[order[i]] for i in range(len(order))]


    def tostdcodec(self, inplace=False, full=True):
        '''Transform all codec in full or default codec.
        
        *Parameters*

        - **inplace** : boolean  (default False) - if True apply transformation to self, else to a new Ilist
        - **full** : boolean (default True)- full codec if True, default if False


        *Return Ilist* : self or new Ilist'''
        lindex = [idx.tostdcodec(inplace=False, full=full) for idx in self.lindex]
        if inplace:
            self.lindex = lindex
            return self
        return Ilist(lindex, var=self.lvarrow[0])

    def to_csv(self, filename, optcsv={'quoting': csv.QUOTE_NONNUMERIC}, **kwargs):
        '''
        Generate csv file to display data.

        *Parameters*

        - **filename** : string - file name (with path)
        - **optcsv** : parameter for csv.writer

        *Parameters (kwargs)*

        - **name=listcode** : element (default None) - eg location='ns'
            - listcode : string with Code for each index (j: json, n: name, s: simple).
            - name : name of the index 
        - **lenres** : Integer (default : 0) - Number of raws (all if 0)
        - **header** : Boolean (default : True) - If True, first line with names
        - **optcsv** : parameter for csv.writer
        - **ifunc** : function (default None) - function to apply to indexes
        - **other kwargs** : parameter for ifunc
        
        *Returns* : size of csv file '''
        size = 0
        if not optcsv: optcsv = {}
        tab = self._to_tab(**kwargs)
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, **optcsv)
            for lign in tab : 
                size += writer.writerow(lign)
        return size
       
    """def to_csv(self, filename='ilist.csv', ifunc=None, header=True, 
               optcsv={'quoting': csv.QUOTE_NONNUMERIC}, **kwargs):
        '''
        Generate a csv file with Ilist data (a column for each index)

        *Parameters*

        - **filename** : string (default 'ilist.csv') - name of the file to create
        - **ifunc** : list of function (default None) - function to apply to indexes
        before writting csv file
        - **order** : list of integer (default None) - ordered list of index in columns
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **optcsv** : parameter for csv.writer
        - **kwargs** : parameter for ifunc

        *Returns* : size of csv file '''
        size = 0
        if not optcsv: optcsv = {}
        #optcsv = {'quoting': csv.QUOTE_NONNUMERIC} | optcsv
        if ifunc and not isinstance(ifunc, list): ifunc = [ifunc] * self.lenindex
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, **optcsv)
            if header: size += writer.writerow(self.lname)
            for i in range(len(self)):
                if not ifunc: row = self.record(i) 
                else: row = [util.funclist(self.lindex[j].values[i], ifunc[j], **kwargs) 
                       for j in range(self.lenindex)]
                size += writer.writerow(row)
        return size"""
    
    def to_xarray(self, info=False, idx=None, fillvalue='?', fillextern=True,
                  lisfunc=None, name=None, numeric=False, npdtype=None, **kwargs):
        '''
        Complete the Ilist and generate a Xarray DataArray with the dimension define by ind.

        *Parameters*

        - **info** : boolean (default False) - if True, add _dict attributes to attrs Xarray
        - **idx** : list (default none) - list of idx to be completed. If [],
        self.axes is used.
        - **fillvalue** : object (default '?') - value used for the new extval
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **lisfunc** : function (default none) - list of function to apply to indexes before export
        - **name** : string (default None) - DataArray name. If None, variable name
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values.
        - **npdtype** : string (default None) - numpy dtype for the DataArray ('object' if None)
        - **kwargs** : parameter for lisfunc

        *Returns* : none '''
        if not self.consistent : raise IlistError("Ilist not consistent")
        if len(self.lvarname) == 0 : raise IlistError("Variable is not defined")
        if isinstance(lisfunc, list) and len(lisfunc) == 1: 
            lisfunc = lisfunc * self.lenindex
        elif isinstance(lisfunc, list) and len(lisfunc) != self.lenindex : 
            lisfunc = [None] * self.lenindex
        elif not isinstance(lisfunc, list):
            funcvar = lisfunc            
            lisfunc = [None] * self.lenindex
            lisfunc[self.lvarrow[0]] = funcvar
        if numeric: 
            lisfunc[self.lvarrow[0]] = ESValue.to_float
            fillvalue= math.nan
            npdtype='float'
        lisfuncname = dict(zip(self.lname, lisfunc))
        if idx is None or idx==[] : idx = self.primary
        axesname = [self.idxname[i] for i in idx[:len(self.idxname)]]
        ilf = self.full(indexname=axesname, fillvalue=fillvalue, 
                        fillextern=fillextern, inplace=False)
        ilf.setcanonorder()
        idxilf = list(range(len(idx[:len(self.idxname)])))
        coord = ilf._xcoord(idxilf, lisfuncname, **kwargs)
        dims = [ilf.idxname[i] for i in idxilf]
        data = ilf.lvar[0].to_numpy(func=lisfuncname[self.lvarname[0]], 
                                    npdtype=npdtype, **kwargs
                                     ).reshape([ilf.idxlen[idx] for idx in idxilf])
        if not name: name = self.name
        attrs={}
        for nam in self.lunicname: attrs[nam] = self.nindex(nam).codec[0]
        if info: attrs |= ilf.indexinfos()
        return xarray.DataArray(data, coord, dims, attrs=attrs, name=name)

    def to_file(self, file, **kwargs) :
        '''Generate file to display `Ilist` data.

         *Parameters (kwargs)*

        - **file** : string - file name (with path)
        - **kwargs** : see 'to_obj' parameters

        *Returns* : Integer - file lenght (bytes)  '''
        option = {'encode_format': 'cbor'} | kwargs | {'encoded': True}
        data = self.to_obj(**option)
        if option['encode_format'] == 'cbor':
            size = len(data)
            with open(file, 'wb') as f: f.write(data)
        else:
            size = len(bytes(data, 'UTF-8'))
            with open(file, 'w', newline='') as f: f.write(data)
        return size
    
    def to_obj(self, indexinfos=None, **kwargs):
        '''Return a formatted object (json string, cbor bytes or json dict). 

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **fullcodec** : boolean (default False) - if True, each index is with a full codec
        - **defaultcodec** : boolean (default False) - if True, each index is whith a default codec
        - **name** : boolean (default False) - if False, default index name are not included

        *Returns* : string, bytes or dict'''
        option = {'fullcodec': False, 'defaultcodec': False, 'encoded': False, 
                  'encode_format': 'json', 'codif': ES.codeb, 'name': False} | kwargs
        option2 = {'encoded': False, 'encode_format': 'json', 'codif': option['codif']}
        lis = []
        if option['fullcodec'] or option['defaultcodec']: 
            for idx in self.lidx: 
                idxname = option['name'] or idx.name != 'i' + str(self.lname.index(idx.name))
                lis.append(idx.tostdcodec(full=not option['defaultcodec'])
                           .to_obj(keys=not option['fullcodec'], name=idxname, **option2))
        else:
            if not indexinfos: indexinfos=self.indexinfos(default=False)
            notkeyscrd = True 
            if self.iscanonorder(): notkeyscrd = None
            for idx, inf in zip(self.lidx, indexinfos):
                idxname = option['name'] or idx.name != 'i' + str(self.lname.index(idx.name))
                if   inf['typecoupl'] == 'unique' : 
                    lis.append(idx.tostdcodec(full=False).to_obj(name=idxname, **option2))
                elif inf['typecoupl'] == 'crossed': 
                    lis.append(idx.to_obj(keys=notkeyscrd, name=idxname, **option2))
                elif inf['typecoupl'] == 'coupled': 
                    lis.append(idx.setkeys(self.lidx[inf['parent']].keys, inplace=False).
                               to_obj(parent=self.lidxrow[inf['parent']], 
                                      name=idxname, **option2))
                elif inf['typecoupl'] == 'linked' : 
                    lis.append(idx.to_obj(keys=True, name=idxname, **option2))
                elif inf['typecoupl'] == 'derived': 
                    if idx.iskeysfromderkeys(self.lidx[inf['parent']]):
                        lis.append(idx.to_obj(parent=self.lidxrow[inf['parent']], 
                                          name=idxname, **option2))                        
                    else:
                        keys=idx.derkeys(self.lidx[inf['parent']])
                        lis.append(idx.to_obj(keys=keys, parent=self.lidxrow[inf['parent']], 
                                          name=idxname, **option2))
                else: raise IlistError('Iindex type undefined')
        for i in self.lvarrow: 
            idx = self.lindex[i]
            idxname = option['name'] or idx.name != 'i' + str(self.lname.index(idx.name))
            if i != self.lenindex - 1:
                lis.insert(i, idx.tostdcodec(full=True).
                           to_obj(keys=False, parent=ES.variable, name=idxname, **option2))        
            else:
                lis.append(idx.tostdcodec(full=True).
                           to_obj(keys=False, parent=ES.variable, name=idxname, **option2))        
        if option['encoded'] and option['encode_format'] == 'json': 
            return  json.dumps(lis, cls=IindexEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(lis, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return lis

    def updateindex(self, listvalue, index, extern=True, typevalue=None):
        '''update values of an index.

        *Parameters*

        - **listvalue** : list - index values to replace
        - **index** : integer - index row to update
        - **typevalue** : str (default None) - class to apply to the new value 
        - **extern** : if True, the listvalue has external representation, else internal

        *Returns* : none '''      
        self.lindex[index].setlistvalue(listvalue, extern=extern, typevalue=typevalue)

    def valtokey(self, rec, extern=True):
        '''convert a rec list (value or val for each idx) to a key list (key for each idx).

        *Parameters*

        - **rec** : list of value or val for each idx
        - **extern** : if True, the rec value has external representation, else internal

        *Returns*

        - **list of int** : rec key for each idx'''
        return [idx.valtokey(val, extern=extern) for idx, val in zip(self.lidx, rec)]

    def view(self, **kwargs) :
        '''
        Generate tabular list to display data.

        *Parameters (kwargs)*

        - **name=listcode** : element (default None) - eg location='ns'
            - listcode : string with Code for each index (j: json, n: name, s: simple).
            - name : name of the index 
        - **defcode** : String (default : 'j') - default list code (if 'all' is True)
        - **all** : Boolean (default : True) - 'defcode apply to all indexes or none
        - **lenres** : Integer (default : 0) - Number of raws (all if 0)
        - **header** : Boolean (default : True) - First line with names
        - **width** : Integer (default None) - Number of characters displayed for each attribute (all if None)
        - **ifunc** : function (default None) - function to apply to indexes
        - **tabulate params** : default 'tablefmt': 'simple', 'numalign': 'left', 'stralign': 'left',
                   'floatfmt': '.3f' - See tabulate module
        - **other kwargs** : parameter for ifunc

        *Returns* : None '''
        #print(kwargs)
        opttab = {'defcode': 'j', 'all': True, 'lenres': 0, 'header':True}
        optview = {'tablefmt': 'simple', 'numalign': 'decimal', 'stralign': 'left', 'floatfmt': '.2f'}
        option = opttab | optview | kwargs
        tab = self._to_tab(**option)
        width = ({'width': None} | kwargs)['width']
        if width: tab = [[(lambda x : x[:width] if type(x)==str else x)(val) 
                           for val in lig] for lig in tab]
        print(tabulate(tab, headers='firstrow', **{k: option[k] for k in optview})) 
    
    def vlist(self, *args, func=None, index=-1, **kwargs):
        '''
        Apply a function to an index and return the result.

        *Parameters*

        - **func** : function (default none) - function to apply to extval or extidx
        - **args, kwargs** : parameters for the function
        - **index** : integer - index to update (index=-1 for variable)

        *Returns* : list of func result'''
        if index == -1 and self.lvar: return self.lvar[0].vlist(func, *args, **kwargs)
        if index == -1 and self.lenindex == 1: index = 0        
        return self.lindex[index].vlist(func, *args, **kwargs) 

    def voxel(self):
        '''
        Plot not null values in a cube with voxels and return indexes values.
        
        *Returns* : **dict of indexes values**
        '''
        if not self.consistent : return
        if   self.lenidx  > 3: raise IlistError('number of idx > 3')
        elif self.lenidx == 2: self.addindex(Iindex('null', ' ', keys=[0]*len(self)))
        elif self.lenidx == 1: 
            self.addindex(Iindex('null', ' ', keys=[0]*len(self)))
            self.addindex(Iindex('null', '  ', keys=[0]*len(self)))
        xa = self.to_xarray(idx=[0,1,2], fillvalue='?', fillextern=False,
                             lisfunc=util.isNotEqual, tovalue='?')
        ax = plt.figure().add_subplot(projection='3d')
        ax.voxels(xa, edgecolor='k')
        ax.set_xticks(np.arange(self.idxlen[self.idxname.index(xa.dims[0])]))
        ax.set_yticks(np.arange(self.idxlen[self.idxname.index(xa.dims[1])]))
        ax.set_zticks(np.arange(self.idxlen[self.idxname.index(xa.dims[2])]))
        ax.set(xlabel=xa.dims[0][:8], 
               ylabel=xa.dims[1][:8],
               zlabel=xa.dims[2][:8])
        plt.show()
        return {xa.dims[i]: list(xa.coords[xa.dims[i]].values) 
                for i in range(len(xa.dims))}

    def _to_tab(self, **kwargs):
        ''' data preparation (dict of dict) for view or csv export. Representation is included if :
            - code is definie in the name element of the field
            - or code is defined in 'defcode' element and 'all' element is True

        *Parameters (kwargs)*

        - **name=listcode** : element (default None) - eg location='ns'
            - listcode : string with Code for each index (j: json, n: name, s: simple, f: ifunc).
            - name : name of the index 
        - **defcode** : String (default : 'j') - default list code (if 'all' is True)
        - **all** : Boolean (default : True) - 'defcode apply to all indexes or none
        - **lenres** : Integer (default : 0) - Number of raws (all if 0)
        - **ifunc** : function (default None) - function to apply to indexes
        - **other kwargs** : parameter for ifunc'''

        option = {'defcode': 'j', 'all': True, 'lenres': 0, 'ifunc': None,
                  'header': True}  | kwargs
        tab = list()
        resList = []
        diccode = {'j': '', 'n': 'name-', 's': 'smpl-', 'f': 'func-'}
        if option['header']:
            for name in self.lname:
                if name in option:
                    for n, code in diccode.items():
                        if n in option[name]: resList.append(code + name)
                elif option['all']:
                    for n, code in diccode.items():
                        if n in option['defcode']: resList.append(code + name)                
                '''for n, code in diccode.items():
                    if (name in option and n in option[name]) or (
                                option['all'] and n in option['defcode']):
                        resList.append(code + name)'''
            tab.append(resList)
        lenres = option['lenres']
        if lenres == 0 : lenres = len(self)
        for i in range(min(lenres, len(self))) :
            resList = []
            for name in self.lname:
                if name in option:
                    for n, code in diccode.items():
                        if n in option[name]: 
                            val = self.nindex(name).values[i]
                            if n == 'j': resList.append(util.cast(val, dtype='json'))
                            if n == 'n': resList.append(util.cast(val, dtype='name'))
                            if n == 's': resList.append(util.cast(val, dtype='json', string=True))
                            if n == 'f': resList.append(util.funclist(val, option['ifunc'], **kwargs))
                elif option['all']:
                    for n, code in diccode.items():
                        if n in option['defcode']: 
                            val = self.nindex(name).values[i]
                            if n == 'j': resList.append(util.cast(val, dtype='json'))
                            if n == 'n': resList.append(util.cast(val, dtype='name'))
                            if n == 's': resList.append(util.cast(val, dtype='json', string=True))
                            if n == 'f': resList.append(util.funclist(val, option['ifunc'], **kwargs))
                '''for n, code in diccode.items():
                    if (name in option and n in option[name]) or (
                                option['all'] and n in option['defcode']):
                        val = self.nindex(name).values[i]
                        if n == 'j': resList.append(util.cast(val, dtype='json'))
                        if n == 'n': resList.append(util.cast(val, dtype='name'))
                        if n == 's': resList.append(util.cast(val, dtype='json', string=True))
                        if n == 'f': resList.append(util.funclist(val, option['ifunc'], **kwargs))'''
            tab.append(resList)
        #print(tab)
        return tab
    
    def _xcoord(self, axe, lisfuncname=None, **kwargs) :
        ''' Coords generation for Xarray'''
        if 'maxlen' in kwargs : maxlen=kwargs['maxlen']
        else: maxlen = 20
        info = self.indexinfos()
        coord = {}
        for i in self.lidxrow:
            fieldi = info[i]
            if fieldi['cat'] == 'unique': continue
            if isinstance(lisfuncname, dict) and len(lisfuncname) == self.lenindex: 
                funci= lisfuncname[self.lname[i]]
            else : funci = None
            iname = self.idxname[i]
            if i in axe :  
                coord[iname] = self.lidx[i].to_numpy(func=funci, codec=True, **kwargs)
                coord[iname+'_row'] = (iname, np.arange(len(coord[iname])))
                coord[iname+'_str'] = (iname, self.lidx[i].to_numpy(func=util.cast, 
                                       codec=True, dtype='str', maxlen=maxlen))
            else:
                self.lidx[i].setkeys(self.lidx[fieldi['pparent']].keys)
                coord[iname] = (self.idxname[fieldi['pparent']], 
                                self.lidx[i].to_numpy(func=funci, codec=True, **kwargs))
        return coord

class IlistError(Exception):
    ''' Ilist Exception'''
    #pass
