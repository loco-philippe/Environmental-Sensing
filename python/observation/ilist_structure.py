# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.ilist_structure` module contains the `IlistStructure` class
(`observation.ilist.Ilist` methods).
"""

# %% declarations
from copy import copy
import csv
import math

from esconstante import ES
from iindex import Iindex
from util import util
from ilist_interface import IlistError


class IlistStructure:
    '''this class includes Ilist methods :

    *selecting - infos methods*

    - `IlistStructure.couplingmatrix`
    - `IlistStructure.idxrecord`
    - `IlistStructure.indexinfos`
    - `IlistStructure.indicator`
    - `IlistStructure.iscanonorder`
    - `IlistStructure.isinrecord`
    - `IlistStructure.keytoval`
    - `IlistStructure.loc`
    - `IlistStructure.nindex`
    - `IlistStructure.record`
    - `IlistStructure.recidx`
    - `IlistStructure.recvar`
    - `IlistStructure.valtokey`

    *add - update methods*

    - `IlistStructure.add`
    - `IlistStructure.addindex`
    - `IlistStructure.append`
    - `IlistStructure.delindex`
    - `IlistStructure.delrecord`
    - `IlistStructure.orindex`
    - `IlistStructure.renameindex`
    - `IlistStructure.setvar`
    - `IlistStructure.setname`
    - `IlistStructure.updateindex`

    *structure management - methods*

    - `IlistStructure.applyfilter`
    - `IlistStructure.coupling`
    - `IlistStructure.full`
    - `IlistStructure.getduplicates`
    - `IlistStructure.mix`
    - `IlistStructure.merging`
    - `IlistStructure.reindex`
    - `IlistStructure.reorder`
    - `IlistStructure.setfilter`
    - `IlistStructure.sort`
    - `IlistStructure.swapindex`
    - `IlistStructure.setcanonorder`
    - `IlistStructure.tostdcodec`
    '''
    # %% methods

    def add(self, other, name=False, solve=True):
        ''' Add other's values to self's values for each index

        *Parameters*

        - **other** : Ilist object to add to self object
        - **name** : Boolean (default False) - Add values with same index name (True) or
        same index row (False)
        - **solve** : Boolean (default True) - If True, replace None other's codec value
        with self codec value.

        *Returns* : self '''
        if self.lenindex != other.lenindex:
            raise IlistError('length are not identical')
        if name and sorted(self.lname) != sorted(other.lname):
            raise IlistError('name are not identical')
        for i in range(self.lenindex):
            if name:
                self.lindex[i].add(other.lindex[other.lname.index(self.lname[i])],
                                   solve=solve)
            else:
                self.lindex[i].add(other.lindex[i], solve=solve)
        return self

    def addindex(self, index, first=False, merge=False, update=False):
        '''add a new index.

        *Parameters*

        - **index** : Iindex - index to add (can be index representation)
        - **first** : If True insert index at the first row, else at the end
        - **merge** : create a new index if merge is False
        - **update** : if True, update actual values if index name is present (and merge is True)

        *Returns* : none '''
        idx = Iindex.obj(index)
        idxname = self.lname
        if len(idx) != len(self) and len(self) > 0:
            raise IlistError('sizes are different')
        if not idx.name in idxname:
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif idx.name in idxname and not merge: # !!! not merge suffit
            while idx.name in idxname:
                idx.name += '(2)'
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif update: # si merge
            self.lindex[idxname.index(idx.name)].setlistvalue(idx.values)

    def append(self, record, unique=False, typevalue=ES.def_clsName):
        '''add a new record.

        *Parameters*

        - **record** :  list of new index values to add to Ilist
        - **unique** :  boolean (default False) - Append isn't done if unique
        is True and record present
        - **typevalue** : list of string (default ES.def_clsName) - typevalue
        to convert record or string if typevalue is not define in indexes

        *Returns* : list - key record'''
        if self.lenindex != len(record):
            raise IlistError('len(record) not consistent')
        if not isinstance(typevalue, list):
            typevalue = [typevalue] * len(record)
        typevalue = [util.typename(self.lname[i], typevalue[i])
                     for i in range(self.lenindex)]
        record = [util.castval(val, typ)
                  for val, typ in zip(record, typevalue)]
        if self.isinrecord(self.idxrecord(record), False) and unique:
            return None
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
        if not filtname in self.lname:
            return None
        if inplace:
            ilis = self
        else:
            ilis = copy(self)
        ifilt = ilis.lname.index(filtname)
        ilis.sort([ifilt], reverse=not reverse, func=None)
        lisind = ilis.lindex[ifilt].recordfromvalue(reverse)
        if lisind:
            minind = min(lisind)
            for idx in ilis.lindex:
                del idx.keys[minind:]
        if inplace:
            self.delindex(filtname)
        else:
            ilis.delindex(filtname)
            if delfilter:
                self.delindex(filtname)
        ilis.reindex()
        return ilis

    def couplingmatrix(self, default=False, filename=None, att='rate'):
        '''return a matrix with coupling infos between each idx.
        One info can be stored in a file (csv format).

        *Parameters*

        - **default** : comparison with default codec
        - **filename** : string (default None) - name of the file to write the matrix
        - **att** : string - name of the info to store in the file

        *Returns* : array of array of dict'''
        return self.analysis.getmatrix()

    def coupling(self, derived=True, rate=0.1):
        '''Transform idx with low rate in coupled or derived indexes (codec extension).

        *Parameters*

        - **rate** : integer (default 0.1) - threshold to apply coupling.
        - **derived** : boolean (default : True).If True, indexes are derived, else coupled.

        *Returns* : list - coupling infos for each idx'''
        infos = self.indexinfos()
        coupl = True
        while coupl:
            coupl = False
            #print('while')
            for i, inf in enumerate(infos):
                #if inf['typecoupl'] != 'coupled' and \
                #    (inf['typecoupl'] not in ('derived', 'unique') or not derived)\
                #    and inf['linkrate'] < rate:
                if (inf['linkrate'] == 0 and inf['diffdistparent'] > 0 and 
                    inf['cat'] != 'unique' and inf['distparent'] != -1 and 
                    not derived) or (0 < inf['linkrate'] < rate and derived):
                    self.lindex[inf['distparent']].coupling(
                        self.lindex[i], derived=derived)
                    coupl = True
                    #print(i, inf['distparent'])
                    break
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
        if None in reckeys:
            return None
        row = self.tiindex.index(reckeys)
        for idx in self:
            del idx[row]
        return row

    def delindex(self, indexname):
        '''remove an Iindex or a list of Iindex.

        *Parameters*

        - **indexname** : string or list of string - name of index to remove

        *Returns* : none '''
        if isinstance(indexname, str):
            indexname = [indexname]
        for idxname in indexname:
            if idxname in self.lname:
                self.lindex.pop(self.lname.index(idxname))
    
    def _fullindex(self, ind, keysadd, indexname, leng, fillvalue, fillextern):
        idx = self.lindex[ind]
        lenadd = len(keysadd[0])
        if len(idx) == leng:
            return
        inf = self.indexinfos()
        if inf[ind]['cat'] == 'unique':
            idx.set_keys(idx.keys + [0] * lenadd)  
        elif self.lname[ind] in indexname:
            idx.set_keys(idx.keys + keysadd[indexname.index(self.lname[ind])])
        elif inf[ind]['parent'] == -1:
            fillval = fillvalue
            if fillextern:
                fillval = util.castval(fillvalue, util.typename(self.lname[ind], ES.def_clsName))
            idx.set_keys(idx.keys + [len(idx.codec)] * len(keysadd[0]))
            idx.set_codec(idx.codec + [fillval])
        else:
            parent = inf[ind]['parent']
            if len(self.lindex[parent]) != leng:
                self._fullindex(parent, keysadd, indexname, leng, fillvalue, fillextern)
            if inf[ind]['cat'] == 'coupled' :
                idx.tocoupled(self.lindex[parent], coupling=True)
            else:
                idx.tocoupled(self.lindex[parent], coupling=False)
        
    def full(self, reindex=False, idxname=None, fillvalue='-', fillextern=True,
             inplace=True, complete=True):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **idxname** : list of string - name of indexes to transform
        - **reindex** : boolean (default False) - if True, set default codec before transformation
        - **fillvalue** : object value used for var extension
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **inplace** : boolean (default True) - if True, filter is apply to self,
        - **complete** : boolean (default True) - if True, Iindex are ordered in canonical order

        *Returns* : self or new Ilist'''
        if inplace:
            ilis = self
        else:
            ilis = copy(self)
        if not idxname:
            idxname = ilis.primaryname
        if reindex:
            ilis.reindex()
        keysadd = util.idxfull([ilis.nindex(name) for name in idxname])
        if not keysadd or len(keysadd) == 0:
            return ilis
        lenadd = len(keysadd[0])
        for ind in range(ilis.lenindex):
            ilis._fullindex(ind, keysadd, idxname, len(ilis) + lenadd, fillvalue, fillextern)
        if complete:
            ilis.setcanonorder()
        return ilis

    def getduplicates(self, indexname=None, resindex=None, indexview=None):
        '''check duplicate cod in a list of indexes. Result is add in a new index or returned.

        *Parameters*

        - **indexname** : list of string (default none) - name of indexes to check 
        (if None, all Iindex)
        - **resindex** : string (default None) - Add a new index with check result

        *Returns* : list of int - list of rows with duplicate cod '''
        if not indexname:
            indexname = self.lname
        duplicates = []
        for name in indexname:
            duplicates += self.nindex(name).getduplicates()
        if resindex and isinstance(resindex, str):
            newidx = Iindex([True] * len(self), name=resindex)
            for item in duplicates:
                newidx[item] = False
            self.addindex(newidx)
        dupl = tuple(set(duplicates))
        if not indexview:
            return dupl
        return [tuple(self.record(ind, indexview)) for ind in dupl]

    def iscanonorder(self):
        '''return True if primary indexes have canonical ordered keys'''
        primary = self.primary
        canonorder = util.canonorder(
            [len(self.lidx[idx].codec) for idx in primary])
        return canonorder == [self.lidx[idx].keys for idx in primary]

    def isinrecord(self, record, extern=True):
        '''Check if record is present in self.

        *Parameters*

        - **record** : list - value for each Iindex
        - **extern** : if True, compare record values to external representation of self.value,
        else, internal

        *Returns boolean* : True if found'''
        if extern:
            return record in util.transpose(self.extidxext)
        return record in util.transpose(self.extidx)

    def idxrecord(self, record):
        '''return rec array (without variable) from complete record (with variable)'''
        return [record[self.lidxrow[i]] for i in range(len(self.lidxrow))]

    def indexinfos(self, keys=None):
        '''return a dict with infos of each index :
            - num, name, cat, typecoupl, diffdistparent, child, parent, distparent, 
            crossed, pparent, linkrate (struct info)
            - lencodec, mincodec, maxcodec, typecodec, ratecodec (base info)

        *Parameters*

        - **keys** : string, list or tuple (default None) - list of attributes to returned.
        if 'all' or None, all attributes are returned.
        if 'struct', only structural attributes are returned.
        
        *Returns* : dict'''
        return self.analysis.getinfos(keys)

    def indicator(self, fullsize=None, size=None):
        '''generate size indicators: ol (object lightness), ul (unicity level), gain (sizegain)

        *Parameters*

        - **fullsize** : int (default none) - size with full codec
        - **size** : int (default none) - size with existing codec
        - **indexinfos** : list (default None) - indexinfos data

        *Returns* : dict'''
        if not fullsize:
            fullsize = len(self.to_obj(encoded=True, modecodec='full'))
        if not size:
            size = len(self.to_obj(encoded=True))
        #lenidx = self.lenidx
        #nval = len(self) * (lenidx + 1)
        nval = len(self) * (self.lenindex + 1)
        sval = fullsize / nval
        #ncod = sum(self.idxlen) + lenidx
        ncod = sum(self.indexlen) + self.lenindex
        if nval != ncod:
            scod = (size - ncod * sval) / (nval - ncod)
            olight = scod / sval
        else:
            olight = None
        return {'total values': nval, 'mean size': round(sval, 3),
                'unique values': ncod, 'mean coding size': round(scod, 3),
                'unicity level': round(ncod / nval, 3),
                'optimize level': round(size / fullsize, 3),
                'object lightness': round(olight, 3),
                'maxgain': round((nval - ncod) / nval, 3),
                'gain': round((fullsize - size) / fullsize, 3)}

    def keytoval(self, listkey, extern=True):
        '''
        convert a keys list (key for each index) to a values list (value for each index).

        *Parameters*

        - **listkey** : key for each index
        - **extern** : boolean (default True) - if True, compare rec to val else to values

        *Returns*

        - **list** : value for each index'''
        return [idx.keytoval(key, extern=extern) for idx, key in zip(self.lindex, listkey)]

    def loc(self, rec, extern=True, row=False):
        '''
        Return record or row corresponding to a list of idx values.

        *Parameters*

        - **rec** : list - value for each idx
        - **extern** : boolean (default True) - if True, compare rec to val,
        else to values
        - **row** : Boolean (default False) - if True, return list of row,
        else list of records

        *Returns*

        - **object** : variable value or None if not found'''
        locrow = None
        try:
            if len(rec) == self.lenindex:
                locrow = list(set.intersection(*[set(self.lindex[i].loc(rec[i], extern))
                                               for i in range(self.lenindex)]))
            elif len(rec) == self.lenidx:
                locrow = list(set.intersection(*[set(self.lidx[i].loc(rec[i], extern))
                                               for i in range(self.lenidx)]))
        except:
            pass
        if locrow is None:
            return None
        if row:
            return locrow
        #return self.lvar[0][tuple(locrow)]
        return [self.record(locr, extern=extern) for locr in locrow]
 
    def mix(self, other, fillvalue=None):
        '''add other Iindex not included in self and add other's values'''
        sname = set(self.lname)
        oname = set(other.lname)
        newself = copy(self)
        copother = copy(other)
        for nam in oname - sname:
            newself.addindex([nam, [fillvalue] * len(newself)])
        for nam in sname - oname:
            copother.addindex([nam, [fillvalue] * len(copother)])
        return newself.add(copother, name=True, solve=False)

    def merging(self, listname=None):
        ''' add a new Iindex build with Iindex define in listname.
        Values of the new Iindex are set of values in listname Iindex'''
        self.addindex(Iindex.merging([self.nindex(name) for name in listname]))

    def nindex(self, name):
        ''' index with name equal to attribute name'''
        if name in self.lname:
            return self.lindex[self.lname.index(name)]
        return None

    def orindex(self, other, first=False, merge=False, update=False):
        ''' Add other's index to self's index (with same length)

        *Parameters*

        - **other** : self class - object to add
        - **first** : Boolean (default False) - If True insert indexes
        at the first row, else at the end
        - **merge** : Boolean (default False) - create a new index 
        if merge is False
        - **update** : Boolean (default False) - if True, update actual 
        values if index name is present (and merge is True)

        *Returns* : none '''
        if len(self) != 0 and len(self) != len(other) and len(other) != 0:
            raise IlistError("the sizes are not equal")
        otherc = copy(other)
        for idx in otherc.lindex:
            self.addindex(idx, first=first, merge=merge, update=update)
        #if not self.lvarname:
        #    self.lvarname = other.lvarname
        return self


    def record(self, row, indexname=None, extern=True):
        '''return the record at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val record else value record
        - **indexname** : list of str (default None) - list of fields to return
        *Returns*

        - **list** : val record or value record'''
        if indexname is None:
            indexname = self.lname
        if extern:
            record = [idx.valrow(row) for idx in self.lindex]
        else:
            record = [idx.values[row] for idx in self.lindex]
        return [record[self.lname.index(name)] for name in indexname] 

    def recidx(self, row, extern=True):
        '''return the list of idx val or values at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for idx'''
        if extern:
            return [idx.valrow(row) for idx in self.lidx]
        return [idx.values[row] for idx in self.lidx]

    def recvar(self, row, extern=True):
        '''return the list of var val or values at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for var'''
        # if extern: return [idx.val[row] for idx in self.lidx]
        if extern:
            return [idx.valrow(row) for idx in self.lvar]
        return [idx.values[row] for idx in self.lvar]

    def reindex(self):
        '''Calculate a new default codec for each index (Return self)'''
        for idx in self.lindex:
            idx.reindex()
        return self

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

    def setcanonorder(self, reindex=False):
        '''Set the canonical index order : primary - secondary/unique - variable.
        Set the canonical keys order : ordered keys in the first columns.

        *Parameters*
        - **reindex** : boolean (default False) - if True, set default codec after transformation

        *Return* : self'''
        order   = self.primaryname
        order   += self.secondaryname
        order   += self.lvarname
        order   += self.lunicname
        '''order   = [self.lidxrow[idx] for idx in self.primary]
        order  += [idx for idx in self.lidxrow if not idx in order]
        order  += self.lvarrow'''
        self.swapindex(order)
        self.sort(reindex=reindex)
        self.analysis.actualize()
        return self

    def setfilter(self, filt=None, first=False, filtname=ES.filter, unique=False):
        '''Add a filter index with boolean values

        - **filt** : list of boolean - values of the filter idx to add
        - **first** : boolean (default False) - If True insert index at the first row,
        else at the end
        - **filtname** : string (default ES.filter) - Name of the filter Iindex added

        *Returns* : self'''
        if not filt:
            filt = [True] * len(self)
        idx = Iindex(filt, name=filtname)
        idx.reindex()
        if not idx.cod in ([True, False], [False, True], [True], [False]):
            raise IlistError('filt is not consistent')
        if unique:
            for name in self.lname:
                if name[:len(ES.filter)] == ES.filter:
                    self.delindex(ES.filter)
        self.addindex(idx, first=first)
        return self

    def setname(self, listname=None):
        '''Update Iindex name by the name in listname'''
        for i in range(min(self.lenindex, len(listname))):
            self.lindex[i].name = listname[i]
        self.analysis.actualize()
    """def setvar(self, var=None):
        '''Define a var index by the name or the index row'''
        if var is None:
            self.lvarname = []
        elif isinstance(var, int) and self.lenindex > var >= 0:
            self.lvarname = [self.lname[var]]
        elif isinstance(var, str) and var in self.lname:
            self.lvarname = [var]
        else:
            raise IlistError('var is not consistent with Ilist')"""

    def sort(self, order=None, reverse=False, func=str, reindex=True):
        '''Sort data following the index order and apply the ascending or descending
        sort function to values.

        *Parameters*

        - **order** : list (default None)- new order of index to apply. If None or [],
        the sort function is applied to the existing order of indexes.
        - **reverse** : boolean (default False)- ascending if True, descending if False
        - **func**    : function (default str) - parameter key used in the sorted function
        - **reindex** : boolean (default True) - if True, apply a new codec order (key = func)

        *Returns* : self'''
        if not order:
            order = list(range(self.lenindex))
        orderfull = order + list(set(range(self.lenindex)) - set(order))
        if reindex:
            for i in order:
                self.lindex[i].reindex(codec=sorted(self.lindex[i].codec, key=func))
        newidx = util.transpose(sorted(util.transpose(
            [self.lindex[orderfull[i]].keys for i in range(self.lenindex)]),
            reverse=reverse))
        for i in range(self.lenindex):
            self.lindex[orderfull[i]].set_keys(newidx[i])
        return self

    def swapindex(self, order):
        '''
        Change the order of the index .

        *Parameters*

        - **order** : list of int or list of name - new order of index to apply.

        *Returns* : self '''
        if self.lenindex != len(order):
            raise IlistError('length of order and Ilist different')
        #self.lindex = [self.lindex[order[i]] for i in range(len(order))]
        if not order or isinstance(order[0], int):
            self.lindex = [self.lindex[ind] for ind in order]
        elif isinstance(order[0], str):
            self.lindex = [self.nindex(name) for name in order]
        return self

    def tostdcodec(self, inplace=False, full=True):
        '''Transform all codec in full or default codec.

        *Parameters*

        - **inplace** : boolean  (default False) - if True apply transformation
        to self, else to a new Ilist
        - **full** : boolean (default True)- full codec if True, default if False


        *Return Ilist* : self or new Ilist'''
        lindex = [idx.tostdcodec(inplace=False, full=full)
                  for idx in self.lindex]
        if inplace:
            self.lindex = lindex
            return self
        return self.__class__(lindex, self.lvarname)

    def updateindex(self, listvalue, index, extern=True, typevalue=None):
        '''update values of an index.

        *Parameters*

        - **listvalue** : list - index values to replace
        - **index** : integer - index row to update
        - **typevalue** : str (default None) - class to apply to the new value
        - **extern** : if True, the listvalue has external representation, else internal

        *Returns* : none '''
        self.lindex[index].setlistvalue(
            listvalue, extern=extern, typevalue=typevalue)

    def valtokey(self, rec, extern=True):
        '''convert a record list (value or val for each idx) to a key list 
        (key for each index).

        *Parameters*

        - **rec** : list of value or val for each index
        - **extern** : if True, the rec value has external representation, else internal

        *Returns*

        - **list of int** : record key for each index'''
        return [idx.valtokey(val, extern=extern) for idx, val in zip(self.lindex, rec)]

