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


class Iindexset:
#%% intro
    '''
    An `Iindexset` is a list of interconnected Iindex with the same length.

    *Attributes (for @property see methods)* :

    - **leng** : length of each Iindex
    - **lidx** : list of the Iindex

    *Property (dynamic attributes)
    - **dimension** : number of primary Iindex
    - **complete** : boolean - True if all primary Iindex are crossed
    - **primary** : list of primary Iindex
    - **size** : number of Iindexes

    The methods defined in this class are :

    *constructor (classmethod))*

    - `Iindex.Idic`
    - `Iindex.Iext`
    - `Iindex.from_parent`
    - `Iindex.from_obj`
    - `Iindex.from_extobj`

    *dynamic value property (getters)*

    - `Iindex.values`
    - `Iindex.infos`

    *add - update methods*

    - `Iindex.append`    
    - `Iindex.setcodecvalue`   
    - `Iindex.setname`
    - `Iindex.setvalue`

    *transform methods*

    - `Iindex.coupling`
    - `Iindex.extendcodec`
    - `Iindex.extendkeys`
    - `Iindex.reindex`
    - `Iindex.reorder`
    - `Iindex.sort`
    - `Iindex.tocrossed`
    - `Iindex.tocoupled`
    - `Iindex.tofull`
    
    *idx property (getters)*

    - `Iindex.couplinginfos`
    - `Iindex.iscrossed`
    - `Iindex.iscoupled`
    - `Iindex.isderived`
    - `Iindex.islinked`
    - `Iindex.isvalue`
    - `Iindex.keytoval`
    - `Iindex.valtokey`   

    *export function*
    
    - `Iindex.to_obj`
    - `Iindex.to_extobj`
    - `Iindex.to_numpy`   
    - `Iindex.vlist`
    '''
    @classmethod
    def Iext(cls, extidx=None, idxname=None, fast=True):
        '''
        Iindexset constructor (external index).

        *Parameters*

        - **extidx** : index list (see data model)
        - **idxname** : list of string (default None) - name of index list (see data model)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)

        *Returns* : Iindexset'''
        if not idxname: idxname=[]
        if not extidx:  extidx =[]
        if not isinstance(extidx, list): return None
        if not isinstance(extidx[0], list): ext = [extidx]
        else:                               ext = extidx
        name = ['i' + str(i) for i in range(len(ext))]
        for i in range(len(idxname)): 
            if isinstance(idxname[i], str): name[i] = idxname[i]
        return cls([Iindex.Iext(extidx, nameidx) for extidx, nameidx in zip(ext, name)], 
                   fast=fast)

    @classmethod
    def from_obj(cls, bs=None, fast=True):
        '''
        Generate an Iindexset Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes or string data to convert

        *Returns* : Iindexset '''
        if not bs: bs = []
        if   isinstance(bs, bytes): lis = cbor2.loads(bs)
        elif isinstance(bs, str)  : lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list) : lis = bs
        else: raise IindexsetError("the type of parameter is not available")
        return cls(lis, fast=fast)

    def __init__(self, listidx=None, length=None, fast=True):
        '''
        Iindexset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of compatible Iindex
        - **length** :  int (default None)  - len of each Iindex'''
        #init self.lidx
        if isinstance(listidx, Iindexset): 
            self = copy(listidx)
            return
        if not listidx: listidx = []
        elif not isinstance(listidx, list) or not isinstance(listidx[0], (list, Iindex)): 
            listidx = [listidx]
        codind = [Iindex.from_obj(idx, fast=fast) for idx in listidx]
        self.lidx = list(range(len(codind)))        
        #init self.leng       
        if not length:  length  = -1
        leng = [len(iidx) for code, iidx in codind if code < 0 and len(iidx) != 1]
        if max(leng) == min(leng) and length < 0: length = max(leng)
        flat = length == max(leng) == min(leng)
        if flat:
            self.leng = length
        else:
            keysset = util.keyscrossed([len(iidx) for code, iidx in codind 
                         if code < 0 and len(iidx) != 1])
            if length >= 0 and length != len(keysset[0]): 
                raise IindexsetError('length of Iindex and Iindexset inconsistent')
            self.leng = len(keysset[0]) 
        #init primary               
        primary = [(rang, iidx) for rang, (code, iidx) in zip(range(len(codind)), codind)
                   if code < 0 and len(iidx) != 1]
        for ip, (rang, iidx) in zip(range(len(primary)), primary):
            if not flat: iidx.keys = keysset[ip]
            self.lidx[rang] = iidx
        #init secondary               
        for ii, (code, iidx) in zip(range(len(codind)), codind):
            if iidx.name is None or iidx.name == 'default index': iidx.name = 'i'+str(rang)
            if len(iidx.codec) == 1: 
                iidx.keys = [0] * self.leng
                self.lidx[ii] = iidx
            elif code >=0 and isinstance(self.lidx[ii], int): 
                self._addiidx(ii, code, iidx, codind, fast)
            elif code < 0 and isinstance(self.lidx[ii], int): 
                raise IindexsetError('Iindexset not canonical')
        return None
                
    def _addiidx(self, rang, code, iidx, codind, fast):
        if isinstance(self.lidx[code], int): 
            self._addiidx(code, codind[code][0], codind[code][1], codind, fast)
        if iidx.keys == list(range(len(iidx.codec))): #coupled format
            self.lidx[rang] = Iindex(iidx.codec, iidx.name, self.lidx[code].keys, fast=fast)
        else:
            self.lidx[rang] = Iindex(iidx.codec, iidx.name, 
                                     Iindex.keysfromderkeys(self.lidx[code].keys, 
                                                            codind[rang][1].keys), fast=fast)

#%% special
    def __repr__(self):
        return self.__class__.__name__ + '[' + str(len(self)) + ', ' + str(self.lenidx) + ']'

    def __len__(self):
        ''' len of Iindex list'''
        return self.leng

    def __contains__(self, item):
        ''' item of Iindex'''
        return item in self.lidx

    def __getitem__(self, ind):
        ''' return Iindex item'''
        return self.lidx[ind]

    def __setitem__(self, ind, index):
        ''' modify Iindex item'''
        if ind < 0 or ind >= len(self): raise IindexsetError("out of bounds")
        if not isinstance(index, Iindex): raise IindexsetError("index is not Iindex")
        if len(index) != len(self): raise IindexsetError("index length not consistent")
        self.lidx[ind] = index

    def __eq__(self, other):
        ''' equal if values are equal'''
        return self.leng == other.leng and self.lidx == other.lidx

    def __add__(self, other):
        ''' Add other's values to self's values in a new Ilistindex'''
        if self.lenidx != other.lenidx: return None
        newlidx = copy(self)
        newlidx.__iadd__(other)
        return newlidx

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        if self.lenidx != other.lenidx: raise IindexsetError('length are not identical')
        for idx, idx2 in zip(self.lidx, other.lidx): idx += idx2
        self.leng += other.leng
        return self        
    
    def __or__(self, other):
        ''' Add other's index to self's index in a new Iindexset'''
        newiidx = self.__copy__()
        newiidx.__ior__(other)
        return newiidx

    def __ior__(self, other):
        ''' Add other's index to self's index'''
        if len(self) != len(other): raise IindexsetError("the sizes are not equal")
        otherc = copy(other)
        for idx in otherc.lidx:
            if idx.name in self.idxname: idx.name += '(2)'
            self.lidx.append(idx)
        return self

    def __copy__(self):
        ''' Copy all the data (deepcopy)'''
        return Iindexset([copy(idx) for idx in self.lidx], self.leng)

#%% property
    @property
    def complete(self):
        '''return a boolean (True if Iindexset is complete and consistent)'''
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
    def idxname(self):
        ''' list of Iindex name'''
        return [idx.name for idx in self.lidx]

    @property    
    def idxlen(self):
        ''' list of Iindex length'''
        return [len(idx.codec) for idx in self.lidx]

    @property 
    def iidx(self):
        ''' list of keys for each Iindex'''
        return [idx.keys for idx in self.lidx]
    
    @property 
    def tiidx(self):
        ''' list of keys for each record'''
        return util.list(list(zip(*self.iidx)))
    
    @property
    def lencomplete(self):
        ''' return an integer : number of values if complete (prod(idxlen primary))'''
        return util.mul([self.idxlen[i] for i in self.primary])
    
    @property    
    def lenidx(self):
        ''' number of Iindex'''
        return len(self.lidx)
    
    @property    
    def primary(self):
        ''' return list of primary indexes'''
        idxinfos = self.indexinfos()
        return [idxinfos.index(idx) for idx in idxinfos if idx['cat'] == 'primary']

    @property    
    def iskeyscrossed(self):
        '''return True if crossed indexes have crossed keys'''
        primary = self.primary
        keyscrossed = util.keyscrossed([len(self[idx].codec) for idx in primary])
        return keyscrossed == [self[idx].keys for idx in primary]
    
    #%% methods
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

    def coupling(self, mat=None, fast=True, rate=0.1):  
        infos = self.indexinfos(mat=mat, fast=fast)  
        coupl = True
        while coupl:
            coupl = False
            for i in range(len(infos)):
                if infos[i]['linkrate'] > 0.0 and infos[i]['linkrate'] < rate: 
                    self.lidx[infos[i]['parent']].coupling(self.lidx[i], fast=fast)
                    coupl = True
            infos = self.indexinfos(fast=fast)  
        return infos
        
    def full(self, fast=True, reindex=False):
        if reindex: self.reindex(fast=fast)
        keysadd = util.idxfull([self.lidx[i] for i in self.primary])
        lenadd = len(keysadd[0])
        iprim = 0
        inf = self.indexinfos()
        #for idx, inf in zip(self.lidx, self.indexinfos()):
        for i in range(self.lenidx):
            if      inf[i]['cat'] == 'unique': self.lidx[i].keys += [0] * lenadd
            elif    inf[i]['cat'] == 'primary':
                self.lidx[i].keys += keysadd[iprim]
                iprim += 1
            else: self.lidx[i].tocoupled(self.lidx[inf[i]['parent']], coupling=False, 
                                         fast=fast)  
        self.leng += lenadd
        return None
        
    def indexinfos(self, keys=None, mat=None, default=False, base=False, fast=True):
        '''return an array with infos of each index.

        *Parameters*

        - **default** : comparison with default codec if new coupling matrix 
        - **mat** : array of array (default None) - coupling matrix 

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
        
        
    def reindex(self, fast=True):
        for idx in self.lidx: idx.reindex(fast=fast)
        return self       

    def tostdcodec(self, inplace=False, fast=True, full=True):
        '''
        Transform all codec in full or default codec.

        *Return* : self or Iindexset'''
        lidx = [idx.tostdcodec(inplace=inplace, fast=fast, full=full) for idx in self.lidx]
        if inplace:
            self.lidx = lidx
            return self
        else: 
            return Iindexset(lidx, fast=fast)
         
    def to_obj(self, indexinfos=None, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **keys** : boolean (default False) - if True, primary keys is included
        - **fullcodec** : boolean (default False) - if True, each index is with a full codec
        - **defaultcodec** : boolean (default False) - if True, each index is whit a default codec
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
                    lis.append(idx.to_obj(parent=inf['parent'], **option2))
                elif inf['typecoupl'] == 'linked' : 
                    lis.append(idx.to_obj(keys=True, **option2))
                elif inf['typecoupl'] == 'derived': 
                    keys=idx.derkeys(self.lidx[inf['parent']])
                    lis.append(idx.to_obj(keys=keys, parent=inf['parent'], **option2))
                else: raise IindexsetError('Iindex type undefined')
        if option['encoded'] and option['encode_format'] == 'json': 
            return  json.dumps(lis, cls=IlistEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(lis, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return lis
            
"""def initold__(self, listidx=None, length=None, fast=True):
        '''
        Iindexset constructor.

        *Parameters*

        - **listidx** :  list (default None) - list of compatible Iindex
        - **length** :  int (default None)  - len of each Iindex'''
        if not length:  length  = -1
        if not listidx: listidx = []
        elif not isinstance(listidx, list) or not isinstance(listidx[0], (list, Iindex)): 
            listidx = [listidx]
        self.lidx = []
        codind = [Iindex.from_obj(idx, fast=fast) for idx in listidx]
        #codind = [Iindex.from_extobj(idx, size=length, fast=fast) for idx in listidx]
        #leng = [len(iidx) for code, iidx in codind if not code]
        leng = [len(iidx) for code, iidx in codind if code < 0]
        if max(leng) == min(leng) and length < 0: length = max(leng)
        self.lidx = list(range(len(codind)))        
        scodind = sorted(zip(range(len(codind)), codind), key=lambda x: x[1][0])
        flat = length == max(leng) == min(leng)
        if flat:
            self.leng = length
        else:
            rang = [range(len(iidx)) for code, iidx in codind if code < 0] 
            #rang = [range(len(iidx)) for code, iidx in codind if not code] 
            keysset = util.transpose(util.list(list(product(*rang))))
            if length >= 0 and length != len(keysset[0]): 
                raise IindexsetError('length of Iindex and Iindexset inconsistent')
            self.leng = len(keysset[0]) 
        ik = 0
        for i in [sc[0] for sc in scodind]:
            print(i)
            if codind[i][1].name is None or codind[i][1].name == 'default index': 
                codind[i][1].name = 'i'+str(i)
            if len(codind[i][1].codec) == 1: 
                codind[i][1].keys = [0] * self.leng
                self.lidx[i] = codind[i][1]
            elif codind[i][0] < 0:
            #elif not codind[i][0]:
                if not flat: 
                    codind[i][1].keys = keysset[ik]
                    ik += 1
                self.lidx[i] = codind[i][1]
            else:
                self.lidx[i] = Iindex.from_parent(codind[i][1].codec, self.lidx[codind[i][0]],
                                                  codind[i][1].name, fast=fast)
                '''self.lidx[i] = Iindex.from_parent(codind[i][1].codec, self.lidx[codind[i][0]],
                                                  codind[i][1].name, fast=fast).reindex(fast=fast)'''
    
    @classmethod
    def from_extobj(cls, bs=None, fast=False):
        '''
        Generate an Iindexset Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes or string data to convert

        *Returns* : Iindexset '''
        if not bs: bs = []
        if isinstance(bs, bytes):  lis = cbor2.loads(bs)
        elif isinstance(bs, str) : lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list): lis = bs
        else: raise IindexsetError("the type of parameter is not available")
        return cls(lis, fast=fast)
             
    @classmethod
    def Iext(cls, values=None, name=None, typevalue=None, fast=False, fullcodec=False):
        '''
        Iindex constructor (external list).

        *Parameters*

        - **values** :  list (default None) - external values of index (see data model)
        - **name** : string (default None) - name of index (see data model)
        - **fullcodec** : boolean (default False) - full codec if True
        - **fast** : boolean (default False) - fast methods for simple values'''
        if not values: return cls(name=name, typevalue=typevalue)
        if isinstance(values, Iindex): return values
        if not isinstance(values, list): values = [values]
        if fullcodec: codec, keys = (values, [i for i in range(len(values))])
        else:  codec, keys = util.resetidx(values, fast)
        return cls(name=name, codec=codec, keys=keys, typevalue=typevalue)

    @classmethod
    def Idic(cls, dicvalues=None, typevalue=None, fast=False, fullcodec=False):
        '''
        Iindex constructor (external dictionnary).

        *Parameters*

        - **dicvalues** : {name : values}  (see data model)
        - **fullcodec** : boolean (default False) - full codec if True
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        is generated if no index is defined'''
        if not dicvalues: return cls.Iext(name=None, values=None, typevalue=typevalue, 
                                          fast=fast, fullcodec=fullcodec)
        if isinstance(dicvalues, Iindex): return dicvalues
        if not isinstance(dicvalues, dict): raise IindexError("dicvalues not dict")
        if len(dicvalues) != 1: raise IindexError("one key:values is required")
        name = list(dicvalues.keys())[0]
        values = dicvalues[name]
        return cls.Iext(name=name, values=values, typevalue=typevalue, 
                        fast=fast, fullcodec=fullcodec)

    @classmethod
    def from_parent(cls, codec, parent, name=None):
        '''Generate an Iindex Object from specific codec and parent keys.

        *Parameters*

        - **codec** : list of objects 
        - **parent** : Iindex, parent of the new Iindex

        *Returns* : Iindex '''
        if isinstance(codec, Iindex): return codec
        return Iindex(codec, name, util.tokeys(parent.values))
    
    @classmethod
    def from_obj(cls, bs=None, fast=False):
        '''Generate an Iindex Object from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert

        *Returns* : Iindex '''
        
        if isinstance(bs, Iindex): return bs
        codec, name, keys, typevalue, size, parent = util.decodeobj(bs)
        if keys: return Iindex(codec=codec, name=name, keys=keys, typevalue=typevalue)
        else: return Iindex.Iext(values=codec, name=name, typevalue=typevalue, fast=fast)

    @classmethod
    def from_extobj(cls, bs, size, extkeys=None, fast=False):
        '''Generate an Iindex Object from a bytes, json or dict value and from 
        a keys list (derived Iindex)

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **size** : length of Iindex
        - **extkeys** : list of int, string or dict data to convert

        *Returns* : Iindex '''
        if isinstance(bs, Iindex): return bs
        codec, name, keys, typevalue, size, parent = util.decodeobj(bs, size)
        if keys: 
            return Iindex(codec=codec, name=name, keys=keys, typevalue=typevalue)
        if parent >= 0 and not extkeys: 
            raise IindexError('extkeys have to be present to decode a derived or coupled index')
        if extkeys: 
            return Iindex(codec=codec, name=name, keys=extkeys, typevalue=typevalue)
        
#%% special
    def stri(self):
        ''' return ival and iidx'''
        texLis = json.dumps(self.ival) + '\n'
        for idx in self.iidx : texLis += '\n' + json.dumps(idx)
        print(texLis)

    def stre(self):
        ''' return valname, extval, idxname and extidx'''
        option = {'encoded': False, 'encode_format': 'json', 'typevalue': True}
        texLis = json.dumps({self.valname: [self._json(val, **option) for val in self.extval]},
                            cls=IlistEncoder)+ '\n'
        for (idx, nam) in zip(self.extidx, self.idxname) :
            option |= {'typevalue': not nam in ES.esObsClass}
            texLis += '\n' + json.dumps({nam: [self._json(i, **option) for i in idx]}, 
                                        cls=IlistEncoder)
        return texLis
   
    def __str__(self):
        return self.name + ' : ' + self.values.__repr__() + '\n'

#%% property
    @property
    def values(self):
        '''return values (see data model)'''
        return [self.codec[key] for key in self.keys]

    @property

#%% methods

    @staticmethod
    def coupling(idx1, idx2):
        '''
        Transform two indexes in coupled indexes (codec extension).

        *Parameters*

        - **idx1, idx2** : index to be coupled.

        *Returns* : None'''
        idxzip = Iindex.Iext(list(zip(idx1.keys, idx2.keys)))
        idx1.tocoupled(idxzip)
        idx2.tocoupled(idxzip)
        
    def extendcodec(self, parent):
        '''replace codec with extended codec from parent'''
        keys = util.tokeys(parent.values)
        self.codec = util.tocodec(self.values, keys)
        self.keys  = keys
        
    def extendkeys(self, keys):
        '''add keys to the Iindex
        
        *Parameters*

        - **keys** : list of int (value present in Iindex keys)
        
        *Returns* : None '''
        if min(keys) < 0 or max(keys) > len(self.codec)-1: 
            raise IindexError('keys not consistent with codec')
        self.keys += keys
    
    def iscrossed(self, other):
        '''return True if is crossed to other'''
        return self.couplinginfos(other)['rate'] == 1.0

    def iscoupled(self, other):
        '''return True if is coupled to other'''
        info = self.couplinginfos(other)
        return info['diff'] == 0 and info['rate'] == 0
        #if min(len(self), len(other)) == 0: return False
        #return len(util.idxlink(other.keys, self.keys)) == len(set(other.keys))

    def isderived(self, other):
        '''return True if is derived from other'''
        info = self.couplinginfos(other)
        return info['diff'] != 0 and info['rate'] == 0.0 
        #if min(len(self), len(other)) == 0: return False
        #lis = set(util.tuple(util.transpose([self.keys, other.keys])))
        #return len(lis) == len(set(other.keys)) and len(set(self.keys)) < len(set(other.keys))

    def islinked(self, other):
        '''return True if is linked to other'''
        rate = self.couplinginfos(other)['rate']
        return rate < 1.0 and rate > 0.0

    def isvalue(self, value):
        ''' return True if value is in index
        
        *Parameters*

        - **value** : value to check'''
        return value in self.values

    def keytoval(self, key):
        ''' return first value of a key
        
        *Parameters*

        - **key** : key to convert into values

        *Returns*

        - **int** : first key finded (None else)'''
        if key > 0 and key < len(self.codec): return self.codec[key]
        return None

    def reindex(self, codec=None, fast=False):
        '''apply a reordered codec (return None)
        
        *Parameters*

        - **codec** : list (default None) - reordered codec to apply. If None, a new codec is calculated.
        - **fast** : boolean (default False) - If True, fast operation (reduction controls)'''
        if not codec: codec = util.tocodec(self.values)
        self.keys = util.reindex(self.keys, self.codec, codec, fast)
        self.codec = codec
        
    def reorder(self, sort=None, inplace=True, fast=False):
        '''Change the Iindex order with a new order define by sort and reset the codec.

        *Parameters*

        - **sort** : int list (default None)- new record order to apply. If None, no change.
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        if False a new Iindex is created.

        *Returns*

        - **None**, if inplace. **Iindex** if not inplace'''
        values      = util.reorder(self.values, sort)
        codec, keys = util.resetidx(values, fast=fast)
        if inplace :
            self.keys  = keys
            self.codec = codec
            return None
        return Iindex(name=self.name, codec=codec, keys=keys)
    
    def setcodecvalue(self, oldvalue, newvalue, dtype=None):
        '''update all the oldvalue values by newvalue

        *Parameters*

        - **oldvalue** : value to replace 
        - **newvalue** : new value to apply
        - **dtype** : str (default None) - cast to apply to the new value 

        *Returns* : int - last codec rank updated (-1 if None)'''
        rank = -1
        for i in range(len(self.codec)):
            if self.codec[i] == oldvalue: 
                self.codec[i] = util.cast(newvalue, dtype)
                rank = i
        return rank
    
    def setname(self, name):
        '''update the Iindex name (return None)
        
        *Parameters*

        - **name** : str to set into name '''
        if isinstance(name, str): self.name = name 
        
    def setvalue(self, ind, value, dtype=None, fast=False):
        '''update a value at the rank ind (and update codec and keys) 
        
        *Parameters*

        - **ind** : rank of the value 
        - **value** : new value 
        - **dtype** : str (default None) - cast to apply to the new value 
        - **fast** : boolean (default False) - Update whithout reindex

        *Returns* : None'''
        values = self.values
        values[ind] = util.cast(value, dtype)
        self.codec, self.keys = util.resetidx(values, fast)

    def sort(self, reverse=False, inplace=True, fast=False):
        '''Define new sorted index with ordered codec.

        *Parameters*

        - **reverse** : boolean (defaut False) - codec is sorted with reverse order
        - **inplace** : boolean (default True) - if True, new order is apply to self,
        - **fast** : boolean (default False) - Update whithout reindex
        
        *Returns* : None'''
        if inplace:
            self.reindex(codec=sorted(self.codec, reverse=reverse, key=str), fast=fast)
            self.keys.sort()
            return None
        oldcodec    = self.codec
        codec       = sorted(oldcodec, reverse=reverse, key=str)
        return Iindex(name=self.name, codec=codec,
                      keys=sorted(util.reindex(self.keys, oldcodec, codec, fast)))

    @staticmethod
    def tocrossed(indexset):
        '''Add new values to obtain an indexset with only crossed Indexes

        *Parameters*

        - **indexset** : list of Iindex - list of indexes to be crossed.

        *Returns* : None'''
        if not indexset or not isinstance(indexset, list) or not isinstance(indexset[0], Iindex):
            raise IindexError('indexset is not a list of Iindex')
        keysset = util.idxfull(indexset)
        if not keysset: return
        for i in range(len(indexset)): indexset[i].extendkeys(keysset[i])

    def tocoupled(self, other, coupling=True):
        '''
        Transform a derived index in a coupled index (keys extension) and add 
        new values to have the same length as other.

        *Parameters*

        - **other** : index to be coupled.
        - **coupling** : boolean (default True) - reindex if False

        *Returns* : None'''
        dic = util.idxlink(other.keys, self.keys)
        if not dic: raise IindexError("Iindex is not coupled or derived from other")
        #self.codec = [self.codec[dic[i]] for i in range(len(idx))]
        self.codec = [self.codec[dic[i]] for i in range(len(dic))]
        self.keys  = other.keys
        if not coupling: self.reindex()

    def tofull(self):
        '''
        Transform codec in full codec.

        *Returns* : None'''
        self.codec = self.values
        self.keys  = list(range(len(self.codec)))

    def to_numpy(self, func=identity, **kwargs):
        if len(self) == 0: raise IindexError("Ilist is empty")
        if func is None : func = identity
        if func == 'index' : return np.array(list(range(len(self.values))))
        values = util.funclist(self.values, func, **kwargs)
        if isinstance(values[0], str):
            try : datetime.datetime.fromisoformat(values[0])
            except : return np.array(values)
            return np.array(values, dtype=np.datetime64)
        if isinstance(values[0], datetime.datetime): 
            return np.array(values, dtype=np.datetime64)
        return np.array(values)


    def to_obj(self, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values

        *Returns* : string, bytes or dict'''
        option = {'keys': False, 'typevalue': None} | kwargs
        if option['keys']: 
            code = len(self)
            codeclist = self.codec
            keyslist = self.keys
        else: 
            code = -1 
            codeclist = self.values
            keyslist = None
        return util.encodeobj(codeclist, self.name, keyslist, option['typevalue'],
                              code, **kwargs)

    def to_extobj(self, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **parent** : int (default -1) - Ilist index linked to (-1 if primary)
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values

        *Returns* : string, bytes or dict'''
        option = {'parent': -1, 'keys': False, 'typevalue': None} | kwargs
        keyslist = None
        if option['parent'] >= 0 : 
            code = option['parent']
        else: 
            code = -1
            if option['keys'] : keyslist = self.keys
        return util.encodeobj(self.codec, self.name, keyslist, option['typevalue'], 
                              code, **kwargs)

    def valtokey(self, value):
        '''convert a value to a key 
        
        *Parameters*

        - **value** : value to convert

        *Returns*

        - **int** : first key finded (None else)'''
        if value in self.codec:  return self.codec.index(value)
        else: return None

    def vlist(self, func, *args, **kwargs):
        '''
        Apply a function to values and return the result.

        *Parameters*

        - **func** : function - function to apply to values
        - **args, kwargs** : parameters for the function
        - **idx** : integer - index to update (idx=-1 for extval)

        *Returns* : list of func result'''
        return util.funclist(self.values, func, *args, **kwargs)

"""
class IindexsetError(Exception):
    ''' Iindexset Exception'''
    #pass

"""
    def to_extobj(self, **kwargs):
        '''Return a formatted object (string, bytes or dict). Format can be json or cbor

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **fast** : boolean (default False). If True, fast operation (reduction controls)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **parent** : int (default -1) - Ilist index linked to (-1 if primary)
        - **keys** : boolean (default False) - True if keys is included
        - **typevalue** : string (default None) - type to convert values
        - **fullcodec** : boolean (default False). If True, fullcodec is used

        *Returns* : string, bytes or dict'''
        #option = {'parent': -1, 'keys': False, 'typevalue': None,
        option = {'keys': False, 'typevalue': None,
                  'fullcodec': False, 'encoded': False, 'encode_format': 'json'} | kwargs
        option2 = option | {'encoded': False, 'encode_format': 'json'}
        lis = []
        for idx, inf in zip(self.lidx, self.indexinfos(default=False)):
            if inf['cat'] in ['primary', 'unique']: lis.append(idx.to_extobj(**option2))
            else: 
                idx2=idx.extendcodec(self.lidx[inf['parent']], inplace=False)
                #option2['parent'] = inf['parent']
                #lis.append(idx2.to_extobj(**option2))
                lis.append(idx2.to_extobj(parent=inf['parent'], **option2))
        if option['encoded'] and option['encode_format'] == 'json': 
            return  json.dumps(lis, cls=IlistEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(lis, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return lis
"""
