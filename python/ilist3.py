# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:30:00 2022

@author: a179227
"""
#%% declarations
from collections import Counter
from itertools import product
from copy import copy, deepcopy
from timeslot import TimeSlot
import datetime, cbor2
import json
import re
import csv
import numpy as np
from ESValue import LocationValue, DatationValue, PropertyValue, NamedValue
from ESValue import ESValue, ExternValue
from ilist import Ilist, IlistEncoder, CborDecoder
import math
from ESconstante import ES, _classval
from iindex import Iindex, util
from time import time


class Ilist3:
#%% intro
    @classmethod
    def Idic(cls, idxdic=None, typevalue=ES.def_clsName, fast=True, fullcodec=False, var=None):
        '''
        Ilist3 constructor (external dictionnary).

        *Parameters*

        - **idxdic** : {name : values}  (see data model)
        - **fullcodec** : boolean (default False) - full codec if True
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        is generated if no index is defined'''
        if not idxdic: return cls.Iext(idxval=None, idxname=None, typevalue=typevalue, 
                                          fast=fast, fullcodec=fullcodec, var=var)
        if isinstance(idxdic, Ilist3): return idxdic
        if not isinstance(idxdic, dict): raise Ilist3Error("idxdic not dict")
        return cls.Iext(list(idxdic.values()), list(idxdic.keys()), typevalue, fast, fullcodec, var)

    @classmethod
    def Iext(cls, idxval=None, idxname=None, typevalue=ES.def_clsName, fast=True, fullcodec=False, var=None):
        '''
        Ilist3 constructor (external index).

        *Parameters*

        - **extidx** : index list (see data model)
        - **idxname** : list of string (default None) - name of index list (see data model)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)

        *Returns* : Ilist3'''
        #print('debut iext')
        #t0 = time()
        if not idxname: idxname=[]
        if not idxval:  idxval =[]
        if not isinstance(idxval, list): return None
        if len(idxval) == 0: return cls()
        if not isinstance(idxval[0], list): val = [idxval]
        else:                               val = idxval
        name = ['i' + str(i) for i in range(len(val))]
        for i in range(len(idxname)): 
            if isinstance(idxname[i], str): name[i] = idxname[i]
        #print('fin init iext', time()-t0)
        lidx = [Iindex.Iext(idx, name, typevalue, fast, fullcodec) 
                    for idx, name in zip(val, name)]
        #print('fin lidx iext', time()-t0)
        return cls(lidx, fast=fast, var=var)
        #return cls([Iindex.Iext(idx, name, typevalue, fast, fullcodec) 
        #            for idx, name in zip(val, name)], fast=fast)

    @classmethod
    def from_csv(cls, filename='ilist.csv', var=None, header=True, optcsv=None, dtype=ES.def_dtype, **kwargs):
        '''
        Ilist constructor (from a csv file). Each column represents index values.

        *Parameters*

        - **filename** : string (default 'ilist.csv'), name of the file to read
        - **var** : integer (default None). column row for variable data
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **dtype** : list of string (default None) - data type for each column (default str)
        - **kwargs** : see csv.reader options

        *Returns* : Ilist'''
        if not optcsv: optcsv = {}
        optcsv = {'quoting': csv.QUOTE_NONNUMERIC} | optcsv
        with open(filename, newline='') as f:
            reader = csv.reader(f, **optcsv)
            first=True
            for row in reader:
                if first:
                    if dtype and not isinstance(dtype, list): dtype = [dtype] * len(row)
                    idxval  = [[] for i in range(len(row))]
                    idxname = None
                if first and header:
                    idxname = row
                else:
                    if not dtype: 
                        for i in range(len(row)) : idxval[i].append(row[i])
                    else:
                        for i in range(len(row)) : idxval[i].append(util.cast(row[i], dtype[i]))
                first = False
        return cls.Iext(idxval, idxname, typevalue=None, var=var)
            
    @classmethod
    def from_obj(cls, bs=None, fast=True, reindex=True):
        '''
        Generate an Ilist3 Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes or string data to convert

        *Returns* : Ilist3 '''
        if not bs: bs = []
        if   isinstance(bs, bytes): lis = cbor2.loads(bs)
        elif isinstance(bs, str)  : lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list) : lis = bs
        else: raise Ilist3Error("the type of parameter is not available")
        return cls(lis, fast=fast, reindex=reindex)

    def __init__(self, listidx=None, length=None, fast=True, var=None, 
                 reindex=True, typevalue=ES.def_clsName):
        '''
        Ilist3 constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of compatible Iindex
        - **var** :  int (default None) - row of the variable
        - **length** :  int (default None)  - len of each Iindex'''
        #init self.lidx
        #print('debut')
        #t0 = time()
        if isinstance(listidx, Ilist3): 
            self.lindex = [copy(idx) for idx in listidx.lindex]
            self.lvarname = copy(listidx.lvarname)
            return
        if not listidx: 
            self.lindex = []
            self.lvarname = []
            return
        if not isinstance(listidx, list) or not isinstance(listidx[0], (list, Iindex)): 
            listidx = [listidx]
        if len(listidx) == 1:
            code, idx = Iindex.from_obj(listidx[0], typevalue=typevalue, fast=fast)
            if idx.name is None or idx.name == 'default index': idx.name = 'i0'
            self.lindex = [idx]
            self.lvarname = [idx.name]
            return            
        #print('init', time()-t0)
        #init
        if       isinstance(var, list): idxvar = var
        elif not isinstance(var, int) or var < 0: idxvar = []
        else: idxvar = [var]
        codind = [Iindex.from_obj(idx, typevalue=typevalue, fast=fast) for idx in listidx]
        for ii, (code, idx) in zip(range(len(codind)), codind):
            if idx.name is None or idx.name == 'default index': idx.name = 'i'+str(ii)
            if code == ES.variable and not idxvar: idxvar = [ii]
        self.lindex = list(range(len(codind)))    
        lcodind = [codind[i] for i in range(len(codind)) if i not in idxvar]
        lidx    = [i         for i in range(len(codind)) if i not in idxvar]
        #print('fin init', time()-t0)
        #init length
        if not length:  length  = -1
        leng = [len(iidx) for code, iidx in codind if code < 0 and len(iidx) != 1]
        if max(leng) == min(leng) and length < 0: length = max(leng)
        if idxvar: length = len(codind[idxvar[0]][1])
        flat = length == max(leng) == min(leng)
        if not flat:
            keysset = util.keyscrossed([len(iidx) for code, iidx in lcodind 
                         if code < 0 and len(iidx) != 1])
            if length >= 0 and length != len(keysset[0]): 
                raise Ilist3Error('length of Iindex and Ilist3 inconsistent')
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
            if iidx.name is None or iidx.name == 'default index': iidx.name = 'i'+str(ii)
            if len(iidx.codec) == 1: 
                iidx.keys = [0] * length
                self.lindex[lidx[ii]] = iidx
            elif code >=0 and isinstance(self.lindex[lidx[ii]], int): 
                self._addiidx(lidx[ii], code, iidx, codind, fast)
            elif code < 0 and isinstance(self.lindex[lidx[ii]], int): 
                raise Ilist3Error('Ilist3 not canonical')
        #print('fin secondary', time()-t0)
        #init variable
        for i in idxvar: self.lindex[i] = codind[i][1]
        self.lvarname = [codind[i][1].name for i in idxvar]
        if reindex: self.reindex(fast)
        return None
                
    def _addiidx(self, rang, code, iidx, codind, fast):
        if isinstance(self.lindex[code], int): 
            self._addiidx(code, codind[code][0], codind[code][1], codind, fast)
        if iidx.keys == list(range(len(iidx.codec))): #coupled format
            self.lindex[rang] = Iindex(iidx.codec, iidx.name, self.lindex[code].keys, fast=fast)
        else:
            self.lindex[rang] = Iindex(iidx.codec, iidx.name, 
                                      Iindex.keysfromderkeys(self.lindex[code].keys, 
                                                            codind[rang][1].keys), fast=fast)

#%% special
    def __str__(self):
        if self.lvar: stri = str(self.lvar[0]) + '\n'
        else: stri = ''
        for idx in self.lidx: stri += str(idx)
        return stri

    def __repr__(self):
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(len(self.lindex)) + ']'

    def __len__(self):
        ''' len of Iindex list'''
        if not self.lindex: return 0
        return len(self.lindex[0])
        #return len(self.lidx)

    def __contains__(self, item):
        ''' item of Iindex'''
        return item in self.lidx

    def __getitem__(self, ind):
        ''' return Iindex item value'''
        res = [idx[ind] for idx in self.lindex]
        if len(res) == 1: return res[0]
        return res

    def __setitem__(self, ind, item):
        ''' modify Iindex item'''
        if not isinstance(item, list): item = [item]
        for val, idx in zip(item, self.lindex): idx[ind] = val
            
    def __delitem__(self, ind):
        ''' delete all index item'''
        for idx in self.lindex: del(idx[ind])
        
    def __hash__(self): 
        return sum([hash(idx) for idx in self.lidx])

    def __eq__(self, other):
        ''' equal if values are equal'''
        #return self.__class__ == other.__class__ and set(self.lindex) == set(other.lindex)
        return self.__class__ == other.__class__ \
            and self.lvarname == other.lvarname \
            and set([idx in self.lindex for idx in other.lindex]) in ({True}, set())
    
    def __add__(self, other):
        ''' Add other's values to self's values in a new Ilistindex'''
        newlidx = copy(self)
        newlidx.__iadd__(other)
        return newlidx

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        if self.lenindex != other.lenindex: raise Ilist3Error('length are not identical')
        if sorted(self.lname) != sorted(other.lname): raise Ilist3Error('name are not identical')
        for i in range(self.lenindex): 
            self.lindex[i] += other.lindex[other.lname.index(self.lname[i])]
        if not self.lvarname: self.lvarname = other.lvarname
        return self        
    
    def __or__(self, other):
        ''' Add other's index to self's index in a new Ilist3'''
        newiidx = copy(self)
        newiidx.__ior__(other)
        return newiidx

    def __ior__(self, other):
        ''' Add other's index to self's index'''
        if len(self) != 0 and len(self) != len(other) and len(other) != 0:
            raise Ilist3Error("the sizes are not equal")
        otherc = copy(other)
        for idx in otherc.lindex: self.addindex(idx)
        if not self.lvarname: self.lvarname = other.lvarname
        return self

    def __copy__(self):
        ''' Copy all the data (deepcopy)'''
        return Ilist3([copy(idx) for idx in self.lindex], var=self.lvarrow)

#%% property
    @property
    def complete(self):
        '''return a boolean (True if Ilist3 is complete and consistent)'''
        return self.lencomplete == len(self) and self.consistent

    @property
    def consistent(self):
        ''' True if all the record are different'''
        return max(Counter(zip(*self.iidx)).values()) == 1

    @property
    def dimension(self):
        ''' return an integer : the number of primary indexes'''
        return len(self.primary)

    @property
    def extidx(self):
        '''return extidx (see data model)'''
        return [idx.values for idx in self.lidx]

    @property
    def extidxext(self):
        '''return extidx (see data model)'''
        return [idx.val for idx in self.lidx]

    @property    
    def idxname(self):
        ''' list of Iindex name'''
        return [idx.name for idx in self.lidx]

    @property    
    def iskeyscrossed(self):
        '''return True if crossed indexes have crossed keys'''
        primary = self.primary
        keyscrossed = util.keyscrossed([len(self.lidx[idx].codec) for idx in primary])
        return keyscrossed == [self.lidx[idx].keys for idx in primary]

    @property
    def idxref(self): return [inf['parent'] if inf['typecoupl'] != 'linked' else 
                              inf['num'] for inf in self.indexinfos()]  
    
    @property    
    def idxlen(self):
        ''' list of Iindex length'''
        return [len(idx.codec) for idx in self.lidx]

    @property 
    def iidx(self):
        ''' list of keys for each Iindex'''
        return [idx.keys for idx in self.lidx]
    
    @property
    def lencomplete(self):
        ''' return an integer : number of values if complete (prod(idxlen primary))'''
        return util.mul([self.idxlen[i] for i in self.primary])
    
    @property    
    def lenindex(self):
        ''' number of Iindex'''
        return len(self.lindex)

    @property    
    def lenidx(self):
        ''' number of Iindex'''
        return len(self.lidx)

    @property
    def lidx(self):
        '''return the list of indexes'''
        return [self.lindex[i] for i in self.lidxrow]

    @property
    def lvar(self):
        '''return the list of variables'''
        return [self.lindex[i] for i in self.lvarrow]

    @property
    def lvarrow(self):
        '''return the row of variables'''
        return [self.lname.index(name) for name in self.lvarname]

    @property
    def lidxrow(self):
        '''return the row of index'''
        return [i for i in range(len(self.lindex)) if i not in self.lvarrow]
        #return [self.lname.index(name) for name not in self.idxvar]
    
    @property    
    def lname(self):
        ''' list of Iindex name'''
        return [idx.name for idx in self.lindex]

    @property    
    def primary(self):
        ''' return list of primary indexes'''
        idxinfos = self.indexinfos()
        return [idxinfos.index(idx) for idx in idxinfos if idx['cat'] == 'primary']

    @property
    def setidx(self): 
        '''list of codec for each index'''
        return [idx.codec for idx in self.lidx]
    
    @property 
    def tiidx(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iidx)))

    @property
    def textidx(self):
        '''return the textidx (see data model)'''
        return util.transpose(self.extidx)

    @property
    def textidxext(self):
        '''return the textidx (see data model)'''
        return util.transpose(self.extidxext)
    
    @property
    def zip(self):
        '''return a zip format for textidx : tuple(tuple(idx)'''
        textidx = self.textidx
        return tuple(tuple(idx) for idx in textidx)
    #%% methods
    def addindex(self, index, first=False, merge=False, update=False):
        '''add a new index.

        *Parameters*

        - **index** : Iindex - index to add (can be index value)

        *Returns* : none '''      
        idx = Iindex.from_obj(index)[1]
        #idxname = self.idxname
        idxname = self.lname
        if len(idx) != len(self) and len(self) > 0: 
            raise Ilist3Error('size are different')
        if not idx.name in idxname: 
            if first: self.lindex.insert(0, idx)
            else: self.lindex.append(idx)
        elif idx.name in idxname and not merge:
            while idx.name in idxname: idx.name += '(2)'
            if first: self.lindex.insert(0, idx)
            else: self.lindex.append(idx)
        elif update:
            #self.lidx[self.idxname.index(idx.name)].values = idx.values
            self.lindex[idxname.index(idx.name)].setlistvalue(idx.values)
            
    def append(self, listval, unique=False, dtype=ES.def_dtype, extern=True):
        '''add a new record listval .

        *Parameters*

        - **listval** :  list - new index values to add to Ilist3
        - **unique** :  boolean (default False) - If True and value present
        - **fast** : boolean (default False) - Update whithout reindex

        *Returns* : list of keys '''
        if dtype and not isinstance(dtype, list): dtype = [dtype] * len(listval)
        if dtype: listval = [util.cast(value, typ) for value, typ in zip(listval, dtype)]
        if self.isvaluesindex(self.idxrecord(listval), False) and unique: return None
        return [self.lindex[i].append(listval[i]) for i in range(len(self.lindex))]

    def applyfilter(self, reverse=False):
        if not ES.filter in self.lname: return False
        ifilt = self.lname.index(ES.filter)
        order = [ifilt] + [i for i in range(len(self.lindex)) if i != ifilt]
        invers = self.lindex[ifilt].keys[0]==self.lindex[ifilt].val[0]
        self.sortkeys(order, reverse=invers is not reverse)
        #print(self)
        minind = min(self.lindex[ifilt].recordfromvalue(reverse))
        for idx in self.lindex: del(idx.keys[minind:])
        self.delindex(ES.filter)
        self.reindex()

    def couplingmatrix(self, default=False, file=None, att='rate', fast=True):
        '''return a matrix with coupling infos between each indexes.
        One info can be stored in a file (csv format).

        *Parameters*

        - **default** : comparison with default codec 
        - **file** : string (default None) - name of the file. If None, the array 
        is returned.
        - **att** : string - name of the info to store in the file

        *Returns* : array of array of dict'''
        lenidx = self.lenidx
        mat = [[None for i in range(lenidx)] for i in range(lenidx)]
        for i in range(lenidx):
            for j  in range(i, lenidx): 
                mat[i][j] = self.lidx[i].couplinginfos(self.lidx[j], default=default, fast=fast)
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

    def coupling(self, mat=None, fast=True, derived=True, rate=0.1):  
        '''Transform indexes with low rate in coupled or derived indexes (codec extension).

        *Parameters*

        - **mat** : array of array (default None) - coupling matrix 
        - **rate** : integer (default 0.1) - threshold to apply coupling function.
        - **derived** : boolean (default : True).If True, indexes are derived, else coupled.

        *Returns* : None'''
        infos = self.indexinfos(mat=mat, fast=fast)  
        coupl = True
        while coupl:
            coupl = False
            for i in range(len(infos)):
                if infos[i]['typecoupl'] != 'coupled' and (infos[i]['typecoupl'] 
                    not in ('derived', 'unique') or not derived) and infos[i]['linkrate'] < rate: 
                    #if (infos[i]['linkrate'] > 0.0 or not derived) and infos[i]['linkrate'] < rate: 
                    self.lidx[infos[i]['parent']].coupling(self.lidx[i], derived=derived, fast=fast)
                    coupl = True
            infos = self.indexinfos(fast=fast)  
        return infos
        
    def delrecord(self, record, extern=True):
        '''remove a record.

        *Parameters*

        - **record** :  list - index values to remove to Ilist3

        *Returns* : record row '''
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

    def full(self, fast=True, reindex=False, indexname=None, fillvalue='-'):
        if not indexname: primary = self.primary
        else: primary = [self.idxname.index(name) for name in indexname]
        secondary = [idx for idx in range(len(self.lidx)) if idx not in primary]
        if reindex: self.reindex(fast=fast)
        keysadd = util.idxfull([self.lidx[i] for i in primary])
        if not keysadd or len(keysadd) == 0: return
        leninit = len(self)
        lenadd  = len(keysadd[0])
        inf = self.indexinfos()
        for i,j in zip(primary, range(len(primary))):
            if      inf[i]['cat'] == 'unique': self.lidx[i].keys += [0] * lenadd
            else:   self.lidx[i].keys += keysadd[j]
        for i in secondary:
            if      inf[i]['cat'] == 'unique': self.lidx[i].keys += [0] * lenadd
            else:   self.lidx[i].tocoupled(self.lidx[inf[i]['parent']], coupling=False, 
                                         fast=fast)  
        for i in range(len(self.lidx)):
            if len(self.lidx[i].keys) != leninit + lenadd:
                raise Ilist3Error('primary indexes have to be present')
        if self.lvarname:
            self.lvar[0].keys += [len(self.lvar[0].codec)] * len(keysadd[0])
            self.lvar[0].codec.append(util.cast(fillvalue, ES.def_dtype))
        return None
        
    def isvaluesindex(self, listval, extern=True):
        '''
        Return True if listval is a valid record.

        *Parameters*

        - **listval** : list - value for each Iindex

        *Returns* : boolean - True if found'''
        if extern: return listval in self.textidxext
        return listval in self.textidx
    
    def idxrecord(self, record):
        '''return index array from record'''
        return [record[self.lidxrow[i]] for i in range(len(self.lidxrow))]
    
    def indexinfos(self, keys=None, mat=None, default=False, base=False, fast=True):
        '''return an array with infos of each index.

        *Parameters*

        - **keys** : list (default none) - list of information to return (reduct dict), all if None
        - **default** : comparison with default codec if new coupling matrix 
        - **mat** : array of array (default None) - coupling matrix 
        - **base** : boolean (default False) - if True, add Iindex infos

        *Returns* : array'''
        infos = [{} for i in range(self.lenidx)]
        if not mat: mat = self.couplingmatrix(default=default, fast=fast)
        for i in range(self.lenidx):
            infos[i]['num']  = i
            infos[i]['name'] = self.idxname[i]
            minrate = 1.0
            mindiff = len(self)
            disttomin = None 
            minparent = i
            infos[i]['typecoupl'] = 'null'
            for j in range(self.lenidx):
                if mat[i][j]['typecoupl'] == 'derived': 
                    minrate = 0.0
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
                        minrate = 0.0
                        minparent = j
                        break
                    elif mat[i][j]['typecoupl'] == 'crossed' and minrate > 0.0:
                        if not disttomin or mat[i][j]['disttomin'] < disttomin:
                            disttomin = mat[i][j]['disttomin']
                            minrate = mat[i][j]['rate']
                            minparent = j
            if self.lidx[i].infos['typeindex'] == 'unique':
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
            infos[i]['linkrate']          = minrate
            infos[i]['parentname']        = self.idxname[infos[i]['parent']]
            if base: infos[i]            |= self.lidx[i].infos
        if not keys: return infos
        return [{k:v for k,v in inf.items() if k in keys} for inf in infos]

    def indicator(self, fullsize=None, size=None, indexinfos=None):
        '''return ol (object lightness), ul (unicity level), gain (sizegain)'''
        if not indexinfos: indexinfos = self.indexinfos()
        if not fullsize: fullsize = len(self.to_obj(indexinfos=indexinfos, encoded=True, fullcodec=True))
        if not size:     size     = len(self.to_obj(indexinfos=indexinfos, encoded=True))
        lenidx = len(self.lidx)
        nv = len(self) * (lenidx + 1)
        sv = fullsize / nv
        nc = sum(self.idxlen) + lenidx
        if nv != nc: 
            sc = (size - nc * sv) / (nv - nc)
            ol = sc / sv
        else: ol = None
        return {'unique values': nc, 'unicity level': round(nc / nv, 3), 
                'mean size': round(sc, 3), 'object lightness': round(ol, 3),
                'gain':round((fullsize - size) / fullsize, 3)}
        
    def json(self, **kwargs):
        '''
        Return json dict, string or binary.

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (bynary if True, dict else)
        - **encode_format** : string (default 'json') - choice for return format (json, bson or cbor)
        - **json_res_index** : default False - if True add the index to the value
        - **order** : default [] - list of ordered index
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default {}). Numerical value for string in CBOR encoder

        *Returns* : string or dict'''

        #option = {'encode_format': 'json', 'encoded' : False, 'codif' : {}} | kwargs
        #return self.to_obj(**option)
        return self.to_obj(**kwargs)

    def keytoval(self, listkey, extern=True):
        '''
        convert a keys list (key for each index) to a values list (value for each index).

        *Parameters*

        - **listkey** : key for each index

        *Returns*

        - **list** : value for each index'''
        return [idx.keytoval(key, extern=extern) for idx, key in zip(self.lidx, listkey)] 
    
    def loc(self, listval, extern=True):
        '''
        Return variable value corresponding to a list of index values.

        *Parameters*

        - **listval** : list - value for each index

        *Returns*

        - **object** : variable value '''
        try:
            if extern: 
                row = self.textidxext.index(listval)
            else: 
                row = self.textidx.index(listval)
        except: return None
        return self.lvar[0][row]

        
        keys = self.indexset.valtokey(listval, extern=extern)
        try :
            ival = self.tiidx.index(keys)
        except :
            return None
        return self.variable[ival]     

    def lrecord(self, row, extern=True):
        '''return the list of all index values at the row'''
        if extern: return [idx.val[row] for idx in self.lindex]
        return [idx.values[row] for idx in self.lindex]
    
    def merge(self, name='merge', fillvalue=math.nan, merge=False, update=False):
        '''
        Merge method replaces Ilist objects included in variable data into its constituents.

        *Parameters*

        - **name** : str (default 'merge') - name of the new Ilist object
        - **fillvalue** : object (default None) - value used for the new data 

        *Returns*

        - **Ilist** : merged Ilist '''     
        fillvalue = util.cast(fillvalue, ES.def_dtype)
        find = True
        ilm = copy(self)
        nameinit = ilm.idxname
        while find:
            find = False
            for i in range(len(ilm)):
                if not isinstance(ilm.lvar[0].values[i], Ilist3): continue
                find = True
                il = ilm.lvar[0].values[i].merge()
                ilname = il.idxname
                record = ilm.record(i, extern=False)
                for val, j in zip(reversed(record), reversed(range(len(record)))): # Ilist pere
                    nameidx = ilm.lidx[j].name
                    updateidx = nameidx in nameinit and not update
                    il.addindex ([nameidx, [val] * len(il)], first=True,
                                          merge=merge, update=updateidx) # ajout des index au fils
                for name in ilname:
                    ilm.addindex([name, [fillvalue] * len(ilm)], 
                                          merge=merge, update=False) # ajout des index au père
                del(ilm[i])
                il.renameindex(il.lvarname[0], ilm.lvarname[0]) 
                ilm += il
                break
        return ilm

    def renameindex(self, oldname, newname):
        for i in range(len(self.lindex)):
            if self.lname[i] == oldname: self.lindex[i].setname(newname)
        for i in range(len(self.lvarname)):
            if self.lvarname[i] == oldname: self.lvarname[i] = newname

    def record(self, row, extern=True):
        '''return the list of index values at the row'''
        if extern: return [idx.val[row] for idx in self.lidx]
        return [idx.values[row] for idx in self.lidx]

    def reindex(self, fast=True):
        '''Calculate a new default codec for each index (Return self)'''
        for idx in self.lindex: idx.reindex(fast=fast)
        return self       

    def setfilter(self, filt=None, first=False, merge=False, update=False):
        if not filt: filt = [True] * len(self)
        idx = Iindex(filt, name=ES.filter)
        idx.reindex()
        if not idx.cod in ([True, False], [False, True], [True], [False]):
            raise Ilist3Error('filt is not consistent')
        if ES.filter in self.lname: self.delindex(ES.filter)
        self.addindex(idx, first=first, merge=merge, update=update)
                
    def setvar(self, var=None):
        '''Calculate a new default codec for each index (Return self)'''
        if var is None: self.lvarname = []
        elif isinstance(var, int) and var >= 0 and var < len(self.lindex): 
            self.lvarname = [self.lname[var]]
        elif isinstance(var, str) and var in self.lname:
            self.lvarname = [var]
        else: raise Ilist3Error('var is not consistent with Ilist')

    def sortkeys(self, order=None, reverse=False):
        '''Sort data following the index order and apply the ascending or descending sort function to keys.
        
        *Parameters*

        - **order** : list (default [])- new order of index to apply. If [], the sort 
        function is applied to the existing order of indexes.
        - **reverse** : boolean (default False)- ascending if True, descending if False

        *Returns* : None'''
        if not order: order = list(range(len(self.lindex)))
        newidx = util.transpose(sorted(util.transpose(
            [self.lindex[order[i]].keys for i in range(len(self.lindex))]), 
            reverse=reverse))
        #newidx = util.transpose(sorted(util.transpose([idx.keys for idx in self.lindex])))
        for i in range(len(self.lindex)): self.lindex[order[i]].keys = newidx[i]

    def swapindex(self, order):
        '''
        Change the order of the index .

        *Parameters*

        - **order** : list - new order of index to apply.

        *Returns* : none '''
        if len(self.lindex) != len(order): raise Ilist3Error('length of order and Ilist3 different')
        self.lindex=[self.lindex[order[i]] for i in range(len(order))]


    def tostdcodec(self, inplace=False, fast=True, full=True):
        '''
        Transform all codec in full or default codec.

        *Return* : self or Ilist3'''
        '''lidx = [idx.tostdcodec(inplace=False, fast=fast, full=full) for idx in self.lidx]
        if inplace:
            self.lidx = lidx
            return self
        else: 
            return Ilist3(lidx, fast=fast)'''

        lindex = [idx.tostdcodec(inplace=False, fast=fast, full=full) for idx in self.lindex]
        if inplace:
            self.lindex = lindex
            return self
        else: 
            return Ilist3(lindex, fast=fast, var=self.lvarrow[0])
        
    def to_csv(self, filename='ilist.csv', ifunc=None, header=True, optcsv=None, **kwargs):
        '''
        Generate a csv file with Ilist data (a column for each index)

        *Parameters*

        - **filename** : string (default 'ilist.csv') - name of the file to create
        - **ifunc** : list of function (default None) - function to apply to indexes
        before writting csv file
        - **order** : list of integer (default None) - ordered list of index in columns
        - **header** : boolean (default True). If True, the first raw is dedicated to names
        - **kwargs** : parameter for csv.writer or func

        *Returns* : none '''
        size = 0
        if not optcsv: optcsv = {}
        optcsv = {'quoting': csv.QUOTE_NONNUMERIC} | optcsv
        if ifunc and not isinstance(ifunc, list): ifunc = [ifunc] * len(self.lindex)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, **optcsv)
            if header: size += writer.writerow(self.lname)
            for i in range(len(self)):
                if not ifunc: row = self.lrecord(i) 
                else: row = [util.funclist(self.lindex[j].values[i], ifunc[j], **kwargs) 
                       for j in range(len(self.lindex))]
                size += writer.writerow(row)
        return size
    
    def to_keyscrossed(self):
        ''' change the index order : primary - secondary - variable
        change the keys order to have ordered keys in the first columns'''
        order = [self.lidxrow[idx] for idx in self.primary]
        for i in self.lidxrow: 
            if not i in order: order.append(i)
        for i in self.lvarrow: order.append(i)
        self.swapindex(order)
        self.sortkeys()
        #newidx = util.transpose(sorted(util.transpose([idx.keys for idx in self.lindex])))
        #for i in range(len(self.lindex)): self.lindex[i].keys = newidx[i]
        
    def to_obj(self, indexinfos=None, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **keys** : boolean (default False) - if True, primary keys is included
        - **fullcodec** : boolean (default False) - if True, each index is with a full codec
        - **defaultcodec** : boolean (default False) - if True, each index is whith a default codec
        - **typevalue** : string (default None) - type to convert values

        *Returns* : string, bytes or dict'''
        option = {'fullcodec': False, 'defaultcodec': False, 'keys': False, 
                  'typevalue': None, 'encoded': False, 'encode_format': 'json',
                  'fast': True, 'codif': ES.codeb} | kwargs
        option2 = {'encoded': False, 'encode_format': 'json', 'fast': option['fast'], 'codif': option['codif']}
        lis = []
        if option['fullcodec'] or option['defaultcodec']: 
            for idx in self.lidx: lis.append(idx.tostdcodec(full=not option['defaultcodec'])
                                             .to_obj(keys=not option['fullcodec'], **option2))
        else:
            if not indexinfos: indexinfos=self.indexinfos(default=False, fast=option['fast'])
            notkeyscrd = True 
            if self.iskeyscrossed: notkeyscrd = None
            for idx, inf in zip(self.lidx, indexinfos):
                if   inf['typecoupl'] == 'unique' : 
                    lis.append(idx.tostdcodec(full=False).to_obj(**option2))
                elif inf['typecoupl'] == 'crossed': 
                    lis.append(idx.to_obj(keys=notkeyscrd, **option2)) #!!! multiple primary !!!
                elif inf['typecoupl'] == 'coupled': 
                    lis.append(idx.setkeys(self.lidx[inf['parent']].keys, inplace=False).
                               to_obj(parent=self.lidxrow[inf['parent']], **option2))
                    #lis.append(idx.to_obj(parent=self.lidxrow[inf['parent']], **option2))
                elif inf['typecoupl'] == 'linked' : 
                    lis.append(idx.to_obj(keys=True, **option2))
                elif inf['typecoupl'] == 'derived': 
                    keys=idx.derkeys(self.lidx[inf['parent']])
                    lis.append(idx.to_obj(keys=keys, parent=self.lidxrow[inf['parent']], **option2))
                else: raise Ilist3Error('Iindex type undefined')
        for i in self.lvarrow: 
            if i != len(self.lindex)-1:
                lis.insert(i, self.lindex[i].tostdcodec(full=True).
                           to_obj(keys=False, parent=ES.variable, **option2))        
            else:
                lis.append(self.lindex[i].tostdcodec(full=True).
                           to_obj(keys=False, parent=ES.variable, **option2))        
        if option['encoded'] and option['encode_format'] == 'json': 
            return  json.dumps(lis, cls=IlistEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(lis, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return lis

    def updateindex(self, listvalue, index, extern=True, typevalue=None):
        '''update values of an index.

        *Parameters*

        - **listvalue** : list - index values to replace
        - **index** : integer - index row (in self.lindex) to update

        *Returns* : none '''      
        self.lindex[index].setlistvalue(listvalue, extern=extern, typevalue=typevalue)

    def valtokey(self, listval, extern=True):
        '''
        convert a values list (value for each index) to a key list (key for each index).

        *Parameters*

        - **listval** : list of value for each extidx

        *Returns*

        - **list** : list of int - key for each index'''
        return [idx.valtokey(val, extern=extern) for idx, val in zip(self.lidx, listval)]

    def vlist(self, *args, func=None, idx=-1, **kwargs):
        '''
        Apply a function to an index and return the result.

        *Parameters*

        - **func** : function (default none) - function to apply to extval or extidx
        - **args, kwargs** : parameters for the function
        - **idx** : integer - index to update (idx=-1 for variable)

        *Returns* : list of func result'''
        if idx == -1 and self.lvar: return self.lvar[0].vlist(func, *args, **kwargs)
        if idx == -1 and len(self.lindex) == 1: idx=0        
        return self.lindex[idx].vlist(func, *args, **kwargs) 

class Ilist3Error(Exception):
    ''' Ilist3 Exception'''
    #pass
