# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `python.observation.dataset_structure` module contains the `DatasetStructure` class
(`python.observation.dataset.Dataset` methods).
"""

# %% declarations
from copy import copy

from observation.esconstante import ES
from observation.field import Field
from observation.util import util
from observation.dataset_interface import DatasetError
#from observation.fields import Sfield


class DatasetStructure:
    '''this class includes Dataset methods :

    *selecting - infos methods*

    - `DatasetStructure.couplingmatrix`
    - `DatasetStructure.idxrecord`
    - `DatasetStructure.indexinfos`
    - `DatasetStructure.indicator`
    - `DatasetStructure.iscanonorder`
    - `DatasetStructure.isinrecord`
    - `DatasetStructure.keytoval`
    - `DatasetStructure.loc`
    - `DatasetStructure.nindex`
    - `DatasetStructure.record`
    - `DatasetStructure.recidx`
    - `DatasetStructure.recvar`
    - `DatasetStructure.tree`
    - `DatasetStructure.valtokey`

    *add - update methods*

    - `DatasetStructure.add`
    - `DatasetStructure.addindex`
    - `DatasetStructure.append`
    - `DatasetStructure.delindex`
    - `DatasetStructure.delrecord`
    - `DatasetStructure.orindex`
    - `DatasetStructure.renameindex`
    - `DatasetStructure.setvar`
    - `DatasetStructure.setname`
    - `DatasetStructure.updateindex`

    *structure management - methods*

    - `DatasetStructure.applyfilter`
    - `DatasetStructure.coupling`
    - `DatasetStructure.full`
    - `DatasetStructure.getduplicates`
    - `DatasetStructure.mix`
    - `DatasetStructure.merging`
    - `DatasetStructure.reindex`
    - `DatasetStructure.reorder`
    - `DatasetStructure.setfilter`
    - `DatasetStructure.sort`
    - `DatasetStructure.swapindex`
    - `DatasetStructure.setcanonorder`
    - `DatasetStructure.tostdcodec`
    '''
    # %% methods

    """
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
    """
    def addindex(self, index, first=False, merge=False, update=False):
        '''add a new index.

        *Parameters*

        - **index** : Field - index to add (can be index Ntv representation)
        - **first** : If True insert index at the first row, else at the end
        - **merge** : create a new index if merge is False
        - **update** : if True, update actual values if index name is present (and merge is True)

        *Returns* : none '''
        idx = self.field.ntv(index)
        idxname = self.lname
        if len(idx) != len(self) and len(self) > 0:
            raise DatasetError('sizes are different')
        if not idx.name in idxname:
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif not merge:  # si idx.name in idxname
            while idx.name in idxname:
                idx.name += '(2)'
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif update:  # si merge et si idx.name in idxname
            self.lindex[idxname.index(idx.name)].setlistvalue(idx.values)

    def append(self, record, unique=False):
        '''add a new record.

        *Parameters*

        - **record** :  list of new index values to add to Dataset
        - **unique** :  boolean (default False) - Append isn't done if unique
        is True and record present
        
        *Returns* : list - key record'''
        if self.lenindex != len(record):
            raise DatasetError('len(record) not consistent')
        record = self.field.l_to_i(record)
        if self.isinrecord(self.idxrecord(record), False) and unique:
            return None
        return [self.lindex[i].append(record[i]) for i in range(self.lenindex)]

    def applyfilter(self, reverse=False, filtname=ES.filter, delfilter=True, inplace=True):
        '''delete records with defined filter value.
        Filter is deleted after record filtering.

        *Parameters*

        - **reverse** :  boolean (default False) - delete record with filter's 
        value is reverse
        - **filtname** : string (default ES.filter) - Name of the filter Field added
        - **delfilter** :  boolean (default True) - If True, delete filter's Field
        - **inplace** : boolean (default True) - if True, filter is apply to self,

        *Returns* : self or new Dataset'''
        if not filtname in self.lname:
            return None
        if inplace:
            ilis = self
        else:
            ilis = copy(self)
        ifilt = ilis.lname.index(filtname)
        #print(self.field.__name__, 'firledname')
        if self.field.__name__ == 'Sfield':
            ilis.sort([ifilt], reverse= not reverse, func=None)
        else:
            ilis.sort([ifilt], reverse=reverse, func=None)
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

    def couplingmatrix(self, default=False, filename=None, att='ratecpl'):
        '''return a matrix with coupling infos between each idx.
        One info can be stored in a file (csv format).

        *Parameters*

        - **default** : comparison with default codec
        - **filename** : string (default None) - name of the file to write the matrix
        - **att** : string - name of the info to store in the file

        *Returns* : array of array of dict'''
        return self.analysis.getmatrix()

    def coupling(self, derived=True, param='rateder', level=0.1):
        '''Transform idx with low rate in coupled or derived indexes (codec extension).

        *Parameters*

        - **param** : string (default 'rateder') - coupling measurement 
        ('rateder', 'diffdistparent', 'ratecpl', 'distance')
        - **level** : float (default 0.1) - param threshold to apply coupling.
        - **derived** : boolean (default : True). If True, indexes are derived, 
        else coupled.

        *Returns* : None'''
        infos = self.indexinfos()
        parent = {'rateder': 'distparent', 'diffdistparent': 'distparent',
                  'ratecpl': 'minparent', 'distance': 'minparent'}
        child = [None] * len(infos)
        for idx in range(len(infos)):
            iparent = infos[idx][parent[param]]
            if iparent != -1:
                if child[iparent] is None:
                    child[iparent] = []
                child[iparent].append(idx)
        for idx in range(len(infos)):
            self._couplingidx(idx, child, derived, param,
                              parent[param], level, infos)

    def _couplingidx(self, idx, child, derived, param, parentparam, level, infos):
        ''' Field coupling (included childrens of the Field)'''
        inf = infos[idx]
        if inf['cat'] in ('coupled', 'unique') or inf[parentparam] == -1\
                or inf[param] >= level or (derived and inf['cat'] == 'derived'):
            return
        if child[idx]:
            for childidx in child[idx]:
                self._couplingidx(childidx, child, derived,
                                  param, parentparam, level, infos)
        self.lindex[inf[parentparam]].coupling(self.lindex[idx], derived=derived,
                                               duplicate=False)
        return

    def delrecord(self, record, extern=True):
        '''remove a record.

        *Parameters*

        - **record** :  list - index values to remove to Dataset
        - **extern** : if True, compare record values to external representation 
        of self.value, else, internal

        *Returns* : row deleted'''
        self.reindex()
        reckeys = self.valtokey(record, extern=extern)
        if None in reckeys:
            return None
        row = self.tiindex.index(reckeys)
        for idx in self:
            del idx[row]
        return row

    """
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
    """
    
    def _fullindex(self, ind, keysadd, indexname, varname, leng, fillvalue, fillextern):
        if not varname:
            varname = []
        idx = self.lindex[ind]
        lenadd = len(keysadd[0])
        if len(idx) == leng:
            return
        inf = self.indexinfos()
        if inf[ind]['cat'] == 'unique':
            idx.set_keys(idx.keys + [0] * lenadd)
        elif self.lname[ind] in indexname:
            idx.set_keys(idx.keys + keysadd[indexname.index(self.lname[ind])])
        elif inf[ind]['parent'] == -1 or self.lname[ind] in varname:
            fillval = fillvalue
            if fillextern:
                fillval = self.field.s_to_i(fillvalue)
            idx.set_keys(idx.keys + [len(idx.codec)] * len(keysadd[0]))
            idx.set_codec(idx.codec + [fillval])
        else:
            parent = inf[ind]['parent']
            if len(self.lindex[parent]) != leng:
                self._fullindex(parent, keysadd, indexname, varname, leng,
                                fillvalue, fillextern)
            if inf[ind]['cat'] == 'coupled':
                idx.tocoupled(self.lindex[parent], coupling=True)
            else:
                idx.tocoupled(self.lindex[parent], coupling=False)

    def full(self, reindex=False, idxname=None, varname=None, fillvalue='-',
             fillextern=True, inplace=True, complete=True):
        '''tranform a list of indexes in crossed indexes (value extension).

        *Parameters*

        - **idxname** : list of string - name of indexes to transform
        - **varname** : string - name of indexes to use
        - **reindex** : boolean (default False) - if True, set default codec 
        before transformation
        - **fillvalue** : object value used for var extension
        - **fillextern** : boolean(default True) - if True, fillvalue is converted 
        to internal value
        - **inplace** : boolean (default True) - if True, filter is apply to self,
        - **complete** : boolean (default True) - if True, Field are ordered 
        in canonical order

        *Returns* : self or new Dataset'''
        ilis = self if inplace else copy(self)
        if not idxname:
            idxname = ilis.primaryname
        if reindex:
            ilis.reindex()
        keysadd = util.idxfull([ilis.nindex(name) for name in idxname])
        if keysadd and len(keysadd) != 0:
            lenadd = len(keysadd[0])
            for ind in range(ilis.lenindex):
                ilis._fullindex(ind, keysadd, idxname, varname, len(ilis) + lenadd,
                                fillvalue, fillextern)
        '''if not keysadd or len(keysadd) == 0:
            return ilis
        lenadd = len(keysadd[0])
        for ind in range(ilis.lenindex):
            ilis._fullindex(ind, keysadd, idxname, varname, len(ilis) + lenadd,
                            fillvalue, fillextern)   '''     
        if complete:
            ilis.setcanonorder()
        return ilis

    def getduplicates(self, indexname=None, resindex=None, indexview=None):
        '''check duplicate cod in a list of indexes. Result is add in a new 
        index or returned.

        *Parameters*

        - **indexname** : list of string (default none) - name of indexes to check 
        (if None, all Field)
        - **resindex** : string (default None) - Add a new index named resindex 
        with check result (False if duplicate)
        - **indexview** : list of str (default None) - list of fields to return

        *Returns* : list of int - list of rows with duplicate cod '''
        if not indexname:
            indexname = self.lname
        duplicates = []
        for name in indexname:
            duplicates += self.nindex(name).getduplicates()
        if resindex and isinstance(resindex, str):
            newidx = self.field([True] * len(self), name=resindex)
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

        - **record** : list - value for each Field
        - **extern** : if True, compare record values to external representation
        of self.value, else, internal

        *Returns boolean* : True if found'''
        if extern:
            return record in util.transpose(self.extidxext)
        return record in util.transpose(self.extidx)

    def idxrecord(self, record):
        '''return rec array (without variable) from complete record (with variable)'''
        return [record[self.lidxrow[i]] for i in range(len(self.lidxrow))]

    def indexinfos(self, keys=None):
        '''return a dict with infos of each index :
            - num, name, cat, diffdistparent, child, parent, distparent, 
            crossed, pparent, rateder (struct info)
            - lencodec, mincodec, maxcodec, typecodec, ratecodec (base info)

        *Parameters*

        - **keys** : string, list or tuple (default None) - list of attributes 
        to returned.
        if 'all' or None, all attributes are returned.
        if 'struct', only structural attributes are returned.

        *Returns* : dict'''
        return self.analysis.getinfos(keys)

    def indicator(self, fullsize=None, size=None):
        '''generate size indicators: ol (object lightness), ul (unicity level), 
        gain (sizegain)

        *Parameters*

        - **fullsize** : int (default none) - size with full codec
        - **size** : int (default none) - size with existing codec
        - **indexinfos** : list (default None) - indexinfos data

        *Returns* : dict'''
        if not fullsize:
            fullsize = len(self.to_obj(encoded=True, modecodec='full'))
        if not size:
            size = len(self.to_obj(encoded=True))
        nval = len(self) * (self.lenindex + 1)
        sval = fullsize / nval
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
        return [self.record(locr, extern=extern) for locr in locrow]

    def mix(self, other, fillvalue=None):
        '''add other Field not included in self and add other's values'''
        sname = set(self.lname)
        oname = set(other.lname)
        newself = copy(self)
        copother = copy(other)
        for nam in oname - sname:
            newself.addindex({nam: [fillvalue] * len(newself)})
        for nam in sname - oname:
            copother.addindex({nam: [fillvalue] * len(copother)})
        return newself.add(copother, name=True, solve=False)

    def merging(self, listname=None):
        ''' add a new Field build with Field define in listname.
        Values of the new Field are set of values in listname Field'''
        self.addindex(Field.merging([self.nindex(name) for name in listname]))

    """
    def nindex(self, name):
        ''' index with name equal to attribute name'''
        if name in self.lname:
            return self.lindex[self.lname.index(name)]
        return None
    """
    
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
            raise DatasetError("the sizes are not equal")
        otherc = copy(other)
        for idx in otherc.lindex:
            self.addindex(idx, first=first, merge=merge, update=update)
        return self

    def record(self, row, indexname=None, extern=True):
        '''return the record at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val record else
        value record
        - **indexname** : list of str (default None) - list of fields to return
        *Returns*

        - **list** : val record or value record'''
        if indexname is None:
            indexname = self.lname
        if extern:
            record = [idx.val[row] for idx in self.lindex]
            #record = [idx.values[row].to_obj() for idx in self.lindex]
            #record = [idx.valrow(row) for idx in self.lindex]
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
            return [idx.values[row].to_obj() for idx in self.lidx]
            #return [idx.valrow(row) for idx in self.lidx]
        return [idx.values[row] for idx in self.lidx]

    def recvar(self, row, extern=True):
        '''return the list of var val or values at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for var'''
        if extern:
            return [idx.values[row].to_obj() for idx in self.lvar]
            #return [idx.valrow(row) for idx in self.lvar]
        return [idx.values[row] for idx in self.lvar]

    """
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
    """

    def setcanonorder(self, reindex=False):
        '''Set the canonical index order : primary - secondary/unique - variable.
        Set the canonical keys order : ordered keys in the first columns.

        *Parameters*
        - **reindex** : boolean (default False) - if True, set default codec after
        transformation

        *Return* : self'''
        order = self.primaryname
        order += self.secondaryname
        order += self.lvarname
        order += self.lunicname
        self.swapindex(order)
        self.sort(reindex=reindex)
        self.analysis.actualize()
        return self

    def setfilter(self, filt=None, first=False, filtname=ES.filter, unique=False):
        '''Add a filter index with boolean values

        - **filt** : list of boolean - values of the filter idx to add
        - **first** : boolean (default False) - If True insert index at the first row,
        else at the end
        - **filtname** : string (default ES.filter) - Name of the filter Field added

        *Returns* : self'''
        if not filt:
            filt = [True] * len(self)
        idx = self.field(filt, name=filtname)
        idx.reindex()
        if not idx.cod in ([True, False], [False, True], [True], [False]):
            raise DatasetError('filt is not consistent')
        if unique:
            for name in self.lname:
                if name[:len(ES.filter)] == ES.filter:
                    self.delindex(ES.filter)
        self.addindex(idx, first=first)
        return self

    def setname(self, listname=None):
        '''Update Field name by the name in listname'''
        super().setname(listname)
        #for i in range(min(self.lenindex, len(listname))):
        #    self.lindex[i].name = listname[i]
        self.analysis.actualize()

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
                self.lindex[i].reindex(codec=sorted(
                    self.lindex[i].codec, key=func))
        newidx = util.transpose(sorted(util.transpose(
            [self.lindex[orderfull[i]].keys for i in range(self.lenindex)]),
            reverse=reverse))
        for i in range(self.lenindex):
            self.lindex[orderfull[i]].set_keys(newidx[i])
        return self

    """
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
    """
    
    def tostdcodec(self, inplace=False, full=True):
        '''Transform all codec in full or default codec.

        *Parameters*

        - **inplace** : boolean  (default False) - if True apply transformation
        to self, else to a new Dataset
        - **full** : boolean (default True)- full codec if True, default if False


        *Return Dataset* : self or new Dataset'''
        lindex = [idx.tostdcodec(inplace=False, full=full)
                  for idx in self.lindex]
        if inplace:
            self.lindex = lindex
            return self
        return self.__class__(lindex, self.lvarname)

    def tree(self, mode='derived', width=5, lname=20, string=True):
        '''return a string with a tree of derived Field.

         *Parameters*

        - **lname** : integer (default 20) - length of the names        
        - **width** : integer (default 5) - length of the lines        
        - **mode** : string (default 'derived') - kind of tree :
            'derived' : derived tree
            'distance': min distance tree
            'diff': min dist rate tree
        '''
        return self.analysis.tree(width=width, lname=lname, mode=mode, string=string)

    def updateindex(self, listvalue, index, extern=True):
        '''update values of an index.

        *Parameters*

        - **listvalue** : list - index values to replace
        - **index** : integer - index row to update
        - **extern** : if True, the listvalue has external representation, else internal

        *Returns* : none '''
        self.lindex[index].setlistvalue(listvalue, extern=extern)

    def valtokey(self, rec, extern=True):
        '''convert a record list (value or val for each idx) to a key list 
        (key for each index).

        *Parameters*

        - **rec** : list of value or val for each index
        - **extern** : if True, the rec value has external representation, else internal

        *Returns*

        - **list of int** : record key for each index'''
        return [idx.valtokey(val, extern=extern) for idx, val in zip(self.lindex, rec)]
