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
    # %% methods
    def add(self, other, name=False, solve=True):
        ''' Add other's values to self's values for each index

        *Parameters*

        - **other** : Ilist object to add to self object
        - **name** : Boolean (default False) - Add values with same index name (True) or
        same index row (False)

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
        if not self.lvarname:
            self.lvarname = other.lvarname
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
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
        elif idx.name in idxname and not merge:
            while idx.name in idxname:
                idx.name += '(2)'
            if first:
                self.lindex.insert(0, idx)
            else:
                self.lindex.append(idx)
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
        if self.lenindex != len(record):
            raise('len(record) not consistent')
        if not isinstance(typevalue, list):
            typevalue = [typevalue] * len(record)
        typevalue = [util.typename(self.lname[i], typevalue[i])
                     for i in range(self.lenindex)]
        record = [util.castval(val, typ)
                  for val, typ in zip(record, typevalue)]
        '''for i in range(self.lenindex):
            if not typevalue[i] and self.typevalue[i]: typevalue[i] = ES.valname[self.typevalue[i]]
        #if dtype and not isinstance(dtype, list): dtype = [dtype] * len(record)
        #if dtype: record = [util.cast(value, typ) for value, typ in zip(record, dtype)]
        record = [util.cast(value, typ) for value, typ in zip(record, typevalue)]'''
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
        if inplace:
            il = self
        else:
            il = copy(self)
        if not filtname in il.lname:
            return False
        ifilt = il.lname.index(filtname)
        il.sort([ifilt], reverse=not reverse, func=None)
        minind = min(il.lindex[ifilt].recordfromvalue(reverse))
        for idx in il.lindex:
            del(idx.keys[minind:])
        if delfilter:
            self.delindex(filtname)
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
            for j in range(i, lenidx):
                mat[i][j] = self.lidx[i].couplinginfos(
                    self.lidx[j], default=default)
            for j in range(i):
                mat[i][j] = copy(mat[j][i])
                if mat[i][j]['typecoupl'] == 'derived':
                    mat[i][j]['typecoupl'] = 'derive'
                elif mat[i][j]['typecoupl'] == 'derive':
                    mat[i][j]['typecoupl'] = 'derived'
                elif mat[i][j]['typecoupl'] == 'linked':
                    mat[i][j]['typecoupl'] = 'link'
                elif mat[i][j]['typecoupl'] == 'link':
                    mat[i][j]['typecoupl'] = 'linked'
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
                    self.lidx[infos[i]['parent']].coupling(
                        self.lidx[i], derived=derived)
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
        if None in reckeys:
            return None
        row = self.tiidx.index(reckeys)
        for idx in self:
            del(idx[row])
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
        if inplace:
            il = self
        else:
            il = copy(self)
        if not indexname:
            primary = il.primary
        else:
            primary = [il.idxname.index(name) for name in indexname]
        secondary = [idx for idx in range(il.lenidx) if idx not in primary]
        if reindex:
            il.reindex()
        keysadd = util.idxfull([il.lidx[i] for i in primary])
        if not keysadd or len(keysadd) == 0:
            return il
        leninit = len(il)
        lenadd = len(keysadd[0])
        inf = il.indexinfos()
        for i, j in zip(primary, range(len(primary))):
            if inf[i]['cat'] == 'unique':
                il.lidx[i].keys += [0] * lenadd
            else:
                il.lidx[i].keys += keysadd[j]
        for i in secondary:
            if inf[i]['cat'] == 'unique':
                il.lidx[i].keys += [0] * lenadd
            else:
                il.lidx[i].tocoupled(il.lidx[inf[i]['parent']], coupling=False)
        for i in range(il.lenidx):
            if len(il.lidx[i].keys) != leninit + lenadd:
                raise IlistError('primary indexes have to be present')
        if il.lvarname:
            il.lvar[0].keys += [len(il.lvar[0].codec)] * len(keysadd[0])
            if fillextern:
                il.lvar[0].codec.append(util.castval(fillvalue,
                                                     util.typename(il.lvarname[0], ES.def_clsName)))
            else:
                il.lvar[0].codec.append(fillvalue)
        if complete:
            il.setcanonorder()
        return il

    def getduplicates(self, indexname=None, resindex=None):
        '''check duplicate cod in a list of indexes. Result is add in a new index or returned.

        *Parameters*

        - **indexname** : list of string - name of indexes to check
        - **resindex** : string (default None) - Add a new index with check result

        *Returns* : list of int - list of rows with duplicate cod '''
        if not indexname:
            primary = self.primary
        else:
            primary = [self.idxname.index(name) for name in indexname]
        duplicates = []
        for idx in primary:
            duplicates += self.lidx[idx].getduplicates()
        if resindex and isinstance(resindex, str):
            newidx = Iindex([True] * len(self), name=resindex)
            for item in duplicates:
                newidx[item] = False
            self.addindex(newidx)
        return tuple(set(duplicates))

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
            return record in self.textidxext
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
        if not mat:
            mat = self.couplingmatrix(default=default)
        for i in range(self.lenidx):
            infos[i]['num'] = i
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
                infos[i]['cat'] = 'unique'
                infos[i]['typecoupl'] = 'unique'
                infos[i]['parent'] = i
            elif minrate == 0.0:
                infos[i]['cat'] = 'secondary'
                infos[i]['parent'] = minparent
            else:
                infos[i]['cat'] = 'primary'
                infos[i]['parent'] = minparent
                if minparent == i:
                    infos[i]['typecoupl'] = 'crossed'
            if minparent != i:
                infos[i]['typecoupl'] = mat[i][minparent]['typecoupl']
            infos[i]['linkrate'] = round(minrate, 2)
            infos[i]['pname'] = self.idxname[infos[i]['parent']]
            infos[i]['pparent'] = 0
            if base:
                infos[i] |= self.lidx[i].infos
        for i in range(self.lenidx):
            util.pparent(i, infos)
        if not keys:
            return infos
        return [{k: v for k, v in inf.items() if k in keys} for inf in infos]

    def indicator(self, fullsize=None, size=None, indexinfos=None):
        '''generate size indicators: ol (object lightness), ul (unicity level), gain (sizegain)

        *Parameters*

        - **fullsize** : int (default none) - size with fullcodec
        - **size** : int (default none) - size with existing codec
        - **indexinfos** : list (default None) - indexinfos data

        *Returns* : dict'''
        if not indexinfos:
            indexinfos = self.indexinfos()
        if not fullsize:
            fullsize = len(self.to_obj(indexinfos=indexinfos,
                           encoded=True, fullcodec=True))
        if not size:
            size = len(self.to_obj(indexinfos=indexinfos, encoded=True))
        lenidx = self.lenidx
        nv = len(self) * (lenidx + 1)
        sv = fullsize / nv
        nc = sum(self.idxlen) + lenidx
        if nv != nc:
            sc = (size - nc * sv) / (nv - nc)
            ol = sc / sv
        else:
            ol = None
        return {'init values': nv, 'mean size': round(sv, 3),
                'unique values': nc, 'mean coding size': round(sc, 3),
                'unicity level': round(nc / nv, 3), 'object lightness': round(ol, 3),
                'gain': round((fullsize - size) / fullsize, 3)}

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
        if row:
            return locrow
        else:
            return self.lvar[0][tuple(locrow)]

    def merge(self, name='merge', fillvalue=math.nan, mergeidx=False, updateidx=False):
        '''
        Merge method replaces Ilist objects included in variable data into its constituents.

        *Parameters*

        - **name** : str (default 'merge') - name of the new Ilist object
        - **fillvalue** : object (default nan) - value used for the additional data
        - **mergeidx** : create a new index if mergeidx is False
        - **updateidx** : if True (and mergeidx is True), update actual values if index name is present

        *Returns*: merged Ilist '''
        find = True
        ilm = copy(self)
        nameinit = ilm.idxname
        while find:
            find = False
            for i in range(len(ilm)):
                if not ilm.lvar[0].values[i].__class__.__name__ in ['Ilist', 'Observation']:
                    continue
                find = True
                il = ilm.lvar[0].values[i].merge()
                ilname = il.idxname
                record = ilm.recidx(i, extern=False)
                for val, j in zip(reversed(record), reversed(range(len(record)))):  # Ilist pere
                    nameidx = ilm.lidx[j].name
                    updidx = nameidx in nameinit and not updateidx
                    il.addindex([nameidx, [val] * len(il)], first=True,
                                merge=mergeidx, update=updidx)  # ajout des index au fils
                for name in ilname:
                    fillval = util.castval(
                        fillvalue, util.typename(name, ES.def_clsName))
                    ilm.addindex([name, [fillval] * len(ilm)],
                                 merge=mergeidx, update=False)  # ajout des index au père
                del(ilm[i])
                il.renameindex(il.lvarname[0], ilm.lvarname[0])
                ilm += il
                break
        return ilm

    def mix(self, other, name=False, fillvalue=None):
        '''add other Iindex not included in self and add other's values'''
        sname = set(self.lname)
        oname = set(other.lname)
        newself = copy(self)
        copother = copy(other)
        for name in oname - sname:
            newself.addindex([name, [fillvalue] * len(newself)])
        for name in sname - oname:
            copother.addindex([name, [fillvalue] * len(copother)])
        return newself.add(copother, name=True, solve=False)

    def merging(self, listname=None):
        ''' add a new Iindex build with Iindex define in listname.
        Values of the new Iindex are set of values in listname Iindex'''
        self.addindex(Iindex.merging([self.nindex(name) for name in listname]))
        return None

    def nindex(self, name):
        ''' index with name equal to attribute name'''
        if name in self.lname:
            return self.lindex[self.lname.index(name)]
        return None

    def record(self, row, extern=True):
        '''return the record at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val record else value record

        *Returns*

        - **list** : val record or value record'''
        if extern:
            return [idx.valrow(row) for idx in self.lindex]
        # if extern: return [idx.val[row] for idx in self.lindex]
        return [idx.values[row] for idx in self.lindex]

    def recidx(self, row, extern=True):
        '''return the list of idx val or values at the row

        *Parameters*

        - **row** : int - row of the record
        - **extern** : boolean (default True) - if True, return val rec else value rec

        *Returns*

        - **list** : val or value for idx'''
        # if extern: return [idx.val[row] for idx in self.lidx]
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
            return
        for idx in self.lindex:
            idx.keys = [idx.keys[i] for i in recorder]
        return None

    def setcanonorder(self):
        '''Set the canonical index order : primary - secondary/unique - variable.
        Set the canonical keys order : ordered keys in the first columns.
        Return self'''
        order = [self.lidxrow[idx] for idx in self.primary]
        order += [idx for idx in self.lidxrow if not idx in order]
        order += self.lvarrow
        self.swapindex(order)
        self.sort()
        return self

    def setfilter(self, filt=None, first=False, filtname=ES.filter, unique=False):
        '''Add a filter index with boolean values

        - **filt** : list of boolean - values of the filter idx to add
        - **first** : boolean (default False) - If True insert index at the first row, else at the end
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

    def setvar(self, var=None):
        '''Define a var index by the name or the index row'''
        if var is None:
            self.lvarname = []
        elif isinstance(var, int) and var >= 0 and var < self.lenindex:
            self.lvarname = [self.lname[var]]
        elif isinstance(var, str) and var in self.lname:
            self.lvarname = [var]
        else:
            raise IlistError('var is not consistent with Ilist')

    def sort(self, order=None, reverse=False, func=str):
        '''Sort data following the index order and apply the ascending or descending
        sort function to values.

        *Parameters*

        - **order** : list (default None)- new order of index to apply. If None or [],
        the sort function is applied to the existing order of indexes.
        - **reverse** : boolean (default False)- ascending if True, descending if False
        - **func**    : function (default str) - parameter key used in the sorted function

        *Returns* : self'''
        if not order:
            order = []
        orderfull = order + list(set(range(self.lenindex)) - set(order))
        for idx in [self.lindex[i] for i in order]:
            idx.reindex(codec=sorted(idx.codec, key=func))
        newidx = util.transpose(sorted(util.transpose(
            [self.lindex[orderfull[i]].keys for i in range(self.lenindex)]),
            reverse=reverse))
        for i in range(self.lenindex):
            self.lindex[orderfull[i]].keys = newidx[i]
        return self

    def swapindex(self, order):
        '''
        Change the order of the index .

        *Parameters*

        - **order** : list of int - new order of index to apply.

        *Returns* : self '''
        if self.lenindex != len(order):
            raise IlistError('length of order and Ilist different')
        self.lindex = [self.lindex[order[i]] for i in range(len(order))]
        return self

    def tostdcodec(self, inplace=False, full=True):
        '''Transform all codec in full or default codec.

        *Parameters*

        - **inplace** : boolean  (default False) - if True apply transformation to self, else to a new Ilist
        - **full** : boolean (default True)- full codec if True, default if False


        *Return Ilist* : self or new Ilist'''
        lindex = [idx.tostdcodec(inplace=False, full=full)
                  for idx in self.lindex]
        if inplace:
            self.lindex = lindex
            return self
        return self.__class__(lindex, var=self.lvarrow[0])
        # return Ilist(lindex, var=self.lvarrow[0])

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
        '''convert a rec list (value or val for each idx) to a key list (key for each idx).

        *Parameters*

        - **rec** : list of value or val for each idx
        - **extern** : if True, the rec value has external representation, else internal

        *Returns*

        - **list of int** : rec key for each idx'''
        return [idx.valtokey(val, extern=extern) for idx, val in zip(self.lidx, rec)]