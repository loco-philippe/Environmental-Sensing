# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `observation.ilist_interface` module contains the `IlistInterface` class
(`observation.ilist.Ilist` methods).
"""

# %% declarations
import datetime
import json
import csv
import math
import xarray
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import cbor2

from esconstante import ES
from iindex import Iindex
from iindex_interface import IindexEncoder
from util import util

#import sys
#print("In module ilist_interface sys.path[0], __package__ ==", sys.path[0], __package__)
#print("In module ilist_interface __package__, __name__ ==", __package__, __name__)


class IlistError(Exception):
    ''' Ilist Exception'''
    # pass


class IlistInterface:
    '''this class includes Iindex methods'''

    def json(self, **kwargs):
        '''
        Return json dict, json string or Cbor binary.

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **modecodec** : string (default 'optimize') - if 'full', each index is with a full codec
        if 'default' each index has keys, if 'optimize' keys are optimized, 
        if 'dict' dict format is used, if 'nokeys' keys are absent
        - **name** : boolean (default False) - if False, default index name are not included
        - **geojson** : boolean (default False) - geojson for LocationValue if True

        *Returns* : string or dict'''
        return self.to_obj(**kwargs)

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
        if not self.consistent:
            return None
        xar = self.to_xarray(numeric=True, lisfunc=[util.cast], dtype='str',
                             npdtype='str', maxlen=maxlen)
        if not order:
            order = [0, 1, 2]

        if len(xar.dims) == 1:
            xar.plot.line(x=xar.dims[0]+'_row', size=size, marker=marker)
        elif len(xar.dims) == 2 and line:
            xar.plot.line(x=xar.dims[order[0]] + '_row',
                          xticks=list(xar.coords[xar.dims[0]+'_row'].values),
                          # hue=xar.dims[order[1]]+'_row', size=size, marker=marker)
                          hue=xar.dims[order[1]], size=size, marker=marker)
        elif len(xar.dims) == 2 and not line:
            xar.plot(x=xar.dims[order[0]]+'_row', y=xar.dims[order[1]]+'_row',
                     xticks=list(xar.coords[xar.dims[order[0]]+'_row'].values),
                     yticks=list(xar.coords[xar.dims[order[1]]+'_row'].values),
                     size=size)
        elif len(xar.dims) == 3 and line:
            xar.plot.line(x=xar.dims[order[0]] + '_row', col=xar.dims[order[1]],
                          xticks=list(
                xar.coords[xar.dims[order[0]]+'_row'].values),
                hue=xar.dims[order[2]], col_wrap=2, size=size, marker=marker)
        elif len(xar.dims) == 3 and not line:
            xar.plot(x=xar.dims[order[0]]+'_row', y=xar.dims[order[1]]+'_row',
                     xticks=list(xar.coords[xar.dims[order[0]]+'_row'].values),
                     yticks=list(xar.coords[xar.dims[order[1]]+'_row'].values),
                     col=xar.dims[order[2]], col_wrap=2, size=size)
        plt.show()
        return {xar.dims[i]: list(xar.coords[xar.dims[i]].values) for i in range(len(xar.dims))}

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
        if not optcsv:
            optcsv = {}
        tab = self._to_tab(**kwargs)
        with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, **optcsv)
            for lign in tab:
                size += writer.writerow(lign)
        return size

    def to_dataframe(self, info=False, idx=None, fillvalue='?', fillextern=True,
                     lisfunc=None, name=None, numeric=False, npdtype=None, **kwargs):
        '''
        Complete the Object and generate a Pandas DataFrame with the dimension define by idx.

        *Parameters*

        - **info** : boolean (default False) - if True, add _dict attributes to attrs Xarray
        - **idx** : list (default none) - list of idx to be completed. If [],
        self.primary is used.
        - **fillvalue** : object (default '?') - value used for the new extval
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **lisfunc** : function (default none) - list of function to apply to indexes before export
        - **name** : string (default None) - DataArray name. If None, variable name
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values.
        - **npdtype** : string (default None) - numpy dtype for the DataArray ('object' if None)
        - **kwargs** : parameter for lisfunc

        *Returns* : pandas.DataFrame '''
        if self.consistent:
            return self.to_xarray(info=info, idx=idx, fillvalue=fillvalue,
                                  fillextern=fillextern, lisfunc=lisfunc, name=name,
                                  numeric=numeric, npdtype=npdtype, **kwargs
                                  ).to_dataframe(name=name)
        return None

    def to_file(self, filename, **kwargs):
        '''Generate file to display data.

         *Parameters (kwargs)*

        - **filename** : string - file name (with path)
        - **kwargs** : see 'to_obj' parameters

        *Returns* : Integer - file lenght (bytes)  '''
        option = {'encode_format': 'cbor'} | kwargs | {'encoded': True}
        data = self.to_obj(**option)
        if option['encode_format'] == 'cbor':
            size = len(data)
            with open(filename, 'wb') as file:
                file.write(data)
        else:
            size = len(bytes(data, 'UTF-8'))
            with open(filename, 'w', newline='', encoding="utf-8") as file:
                file.write(data)
        return size

    def to_obj(self, indexinfos=None, **kwargs):
        '''Return a formatted object (json string, cbor bytes or json dict).

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **modecodec** : string (default 'optimize') - if 'full', each index is with a full codec
        if 'default' each index has keys, if 'optimize' keys are optimized, 
        if 'dict' dict format is used, if 'nokeys' keys are absent
        - **name** : boolean (default False) - if False, default index name are not included
        - **geojson** : boolean (default False) - geojson for LocationValue if True

        *Returns* : string, bytes or dict'''
        option = {'modecodec':'optimize', 'encoded': False,
                  'encode_format': 'json', 'codif': ES.codeb, 'name': False,
                  'geojson': False} | kwargs
        option2 = {'encoded': False, 'encode_format': 'json',
                   'codif': option['codif'], 'geojson': option['geojson'],
                   'modecodec': option['modecodec']}
        if option['modecodec'] == 'dict':
            lis = {}
            for idx in self.lindex:
                keyval = list(idx.to_dict_obj(**option2).items())[0]
                name, dicval = keyval
                if name in self.lvarname:
                    dicval['var'] = True
                lis[name] = dicval
        else:
            lis = []
            idxname = False
            # add not variable Iindex
            for idx in self.lidx:
                idxname = option['name'] or idx.name != 'i' + str(self.lname.index(idx.name))
            if   option['modecodec'] == 'full':
                for idx in self.lidx:
                    lis.append(idx.tostdcodec(full=True).to_obj(name=idxname, **option2))
            elif option['modecodec'] == 'default':
                for idx in self.lidx:
                    lis.append(idx.to_obj(keys=True, name=idxname, **option2))
            elif option['modecodec'] == 'nokeys':
                for idx in self.lidx:
                    lis.append(idx.to_obj(name=idxname, **option2))        
            elif option['modecodec'] == 'optimize':
                lis = self._optimize_obj(indexinfos, idxname, lis, **option2)
            # add variable Iindex
            if self.lenindex > 1:
                parent = ES.variable
            else:
                parent = ES.nullparent
            for i in self.lvarrow:
                idx = self.lindex[i]
                idxname = option['name'] or idx.name != 'i' + \
                    str(self.lname.index(idx.name))
                if i != self.lenindex - 1:
                    lis.insert(i, idx.tostdcodec(full=True).to_obj(keys=False, 
                        parent=parent, name=idxname, **option2))
                else:
                    lis.append(idx.tostdcodec(full=True).to_obj(keys=False, 
                        parent=parent, name=idxname, **option2))
            
        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(lis, cls=IindexEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor':
            return cbor2.dumps(lis, datetime_as_timestamp=True,
                               timezone=datetime.timezone.utc, canonical=True)
        return lis

    def to_xarray(self, info=False, idx=None, fillvalue='?', fillextern=True,
                  lisfunc=None, name=None, numeric=False, npdtype=None, attrs=None, **kwargs):
        '''
        Complete the Object and generate a Xarray DataArray with the dimension define by idx.

        *Parameters*

        - **info** : boolean (default False) - if True, add _dict attributes to attrs Xarray
        - **idx** : list (default none) - list of idx to be completed. If [],
        self.primary is used.
        - **fillvalue** : object (default '?') - value used for the new extval
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **lisfunc** : function (default none) - list of function to apply to indexes before export
        - **name** : string (default None) - DataArray name. If None, variable name
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values.
        - **npdtype** : string (default None) - numpy dtype for the DataArray ('object' if None)
        - **attrs** : dict (default None) - attributes for the DataArray
        - **kwargs** : parameter for lisfunc

        *Returns* : DataArray '''
        option = {'dtype': None} | kwargs
        if not self.consistent:
            raise IlistError("Ilist not consistent")
        if len(self.lvarname) == 0:
            raise IlistError("Variable is not defined")
        if isinstance(lisfunc, list) and len(lisfunc) == 1:
            lisfunc = lisfunc * self.lenindex
        elif isinstance(lisfunc, list) and len(lisfunc) != self.lenindex:
            lisfunc = [None] * self.lenindex
        elif not isinstance(lisfunc, list):
            funcvar = lisfunc
            lisfunc = [None] * self.lenindex
            lisfunc[self.lvarrow[0]] = funcvar
        lisfuncname = dict(zip(self.lname, lisfunc))
        if idx is None or idx == []:
            idx = self.primary
        axesname = [self.idxname[i] for i in idx[:len(self.idxname)]]
        ilf = self.full(indexname=axesname, fillvalue=fillvalue,
                        fillextern=fillextern, inplace=False)
        ilf.setcanonorder()
        idxilf = list(range(len(idx[:len(self.idxname)])))
        coord = ilf._xcoord(idxilf, lisfuncname, **option)
        dims = [ilf.idxname[i] for i in idxilf]
        if numeric:
            lisfunc[self.lvarrow[0]] = util.cast
            fillvalue = math.nan
            npdtype = 'float'
            option['dtype'] = 'float'
        data = ilf.lvar[0].to_numpy(func=lisfunc[self.lvarrow[0]],
                                    npdtype=npdtype, **option
                                    ).reshape([ilf.idxlen[idx] for idx in idxilf])
        if not name:
            name = self.name
        if not isinstance(attrs, dict):
            attrs = {}
        for nam in self.lunicname:
            attrs[nam] = self.nindex(nam).codec[0]
        if info:
            attrs |= ilf.indexinfos()
        return xarray.DataArray(data, coord, dims, attrs=attrs, name=name)

    def voxel(self):
        '''
        Plot not null values in a cube with voxels and return indexes values.

        *Returns* : **dict of indexes values**
        '''
        if not self.consistent:
            return None
        if self.lenidx > 3:
            raise IlistError('number of idx > 3')
        if self.lenidx == 2:
            self.addindex(Iindex('null', ' ', keys=[0]*len(self)))
        elif self.lenidx == 1:
            self.addindex(Iindex('null', ' ', keys=[0]*len(self)))
            self.addindex(Iindex('null', '  ', keys=[0]*len(self)))
        xar = self.to_xarray(idx=[0, 1, 2], fillvalue='?', fillextern=False,
                            lisfunc=util.isNotEqual, tovalue='?')
        axe = plt.figure().add_subplot(projection='3d')
        axe.voxels(xar, edgecolor='k')
        axe.set_xticks(np.arange(self.idxlen[self.idxname.index(xar.dims[0])]))
        axe.set_yticks(np.arange(self.idxlen[self.idxname.index(xar.dims[1])]))
        axe.set_zticks(np.arange(self.idxlen[self.idxname.index(xar.dims[2])]))
        axe.set(xlabel=xar.dims[0][:8],
                ylabel=xar.dims[1][:8],
                zlabel=xar.dims[2][:8])
        plt.show()
        return {xar.dims[i]: list(xar.coords[xar.dims[i]].values)
                for i in range(len(xar.dims))}

    def view(self, **kwargs):
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
        - **width** : Integer (default None) - Number of characters displayed for each
        attribute (all if None)
        - **ifunc** : function (default None) - function to apply to indexes
        - **tabulate params** : default 'tablefmt': 'simple', 'numalign': 'left',
        'stralign': 'left', 'floatfmt': '.3f' - See tabulate module
        - **other kwargs** : parameter for ifunc

        *Returns* : list or html table (tabulate format) '''
        # print(kwargs)
        opttab = {'defcode': 'j', 'all': True, 'lenres': 0, 'header': True}
        optview = {'tablefmt': 'simple', 'numalign': 'decimal',
                   'stralign': 'left', 'floatfmt': '.2f'}
        option = opttab | optview | kwargs
        tab = self._to_tab(**option)
        width = ({'width': None} | kwargs)['width']
        if width:
            tab = [[(lambda x: x[:width] if isinstance(x, str) else x)(val)
                    for val in lig] for lig in tab]
        return tabulate(tab, headers='firstrow', **{k: option[k] for k in optview})

    def vlist(self, *args, func=None, index=-1, **kwargs):
        '''
        Apply a function to an index and return the result.

        *Parameters*

        - **func** : function (default none) - function to apply to extval or extidx
        - **args, kwargs** : parameters for the function
        - **index** : integer - index to update (index=-1 for variable)

        *Returns* : list of func result'''
        if index == -1 and self.lvar:
            return self.lvar[0].vlist(func, *args, **kwargs)
        if index == -1 and self.lenindex == 1:
            index = 0
        return self.lindex[index].vlist(func, *args, **kwargs)

    # %%internal
    def _optimize_obj(self, indexinfos, idxname, lis, **option2):
        '''return list object with primary and secondary Iindex'''
        if not indexinfos:
            indexinfos = self.indexinfos(default=False)
        notkeyscrd = True
        if self.iscanonorder():
            notkeyscrd = None
        for idx, inf in zip(self.lidx, indexinfos):
            if inf['typecoupl'] == 'unique':
                lis.append(idx.tostdcodec(full=False).to_obj(
                    name=idxname, **option2))
            elif inf['typecoupl'] == 'crossed':
                lis.append(idx.to_obj(keys=notkeyscrd,
                           name=idxname, **option2))
            elif inf['typecoupl'] == 'coupled':
                if self.lidx[inf['parent']].keys == list(range(len(self))):
                    lis.append(idx.setkeys(self.lidx[inf['parent']].keys, inplace=False).
                           to_obj(name=idxname, **option2))
                else:
                    lis.append(idx.setkeys(self.lidx[inf['parent']].keys, inplace=False).
                           to_obj(parent=self.lidxrow[inf['parent']],
                                  name=idxname, **option2))
            elif inf['typecoupl'] == 'linked':
                lis.append(idx.to_obj(keys=True, name=idxname, **option2))
            elif inf['typecoupl'] == 'derived':
                if idx.iskeysfromderkeys(self.lidx[inf['parent']]):
                    lis.append(idx.to_obj(parent=self.lidxrow[inf['parent']],
                                          name=idxname, **option2))
                else:
                    keys = idx.derkeys(self.lidx[inf['parent']])
                    lis.append(idx.to_obj(keys=keys, parent=self.lidxrow[inf['parent']],
                                          name=idxname, **option2))
            else:
                raise IlistError('Iindex type undefined')
        return lis
    
    def _to_tab(self, **kwargs):
        ''' data preparation (dict of dict) for view or csv export.
        Representation is included if :
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
                  'header': True} | kwargs
        tab = []
        reslist = []
        diccode = {'j': '', 'n': 'name-', 's': 'smpl-', 'f': 'func-'}
        if option['header']:
            for name in self.lname:
                if name in option:
                    for char, code in diccode.items():
                        if char in option[name]:
                            reslist.append(code + name)
                elif option['all']:
                    for char, code in diccode.items():
                        if char in option['defcode']:
                            reslist.append(code + name)
            tab.append(reslist)
        lenres = option['lenres']
        if lenres == 0:
            lenres = len(self)
        for i in range(min(lenres, len(self))):
            reslist = []
            for name in self.lname:
                if name in option:
                    for char, code in diccode.items():
                        if char in option[name]:
                            val = self.nindex(name).values[i]
                            if char == 'j':
                                reslist.append(util.cast(val, dtype='json'))
                            elif char == 'n':
                                reslist.append(util.cast(val, dtype='name'))
                            elif char == 's':
                                reslist.append(
                                    util.cast(val, dtype='json', string=True))
                            elif char == 'f':
                                reslist.append(util.funclist(
                                    val, option['ifunc'], **kwargs))
                elif option['all']:
                    for char, code in diccode.items():
                        if char in option['defcode']:
                            val = self.nindex(name).values[i]
                            if char == 'j':
                                reslist.append(util.cast(val, dtype='json'))
                            elif char == 'n':
                                reslist.append(util.cast(val, dtype='name'))
                            elif char == 's':
                                reslist.append(
                                    util.cast(val, dtype='json', string=True))
                            elif char == 'f':
                                reslist.append(util.funclist(
                                    val, option['ifunc'], **kwargs))
            tab.append(reslist)
        return tab

    def _xcoord(self, axe, lisfuncname=None, **kwargs):
        ''' Coords generation for Xarray'''
        maxlen = kwargs.get('maxlen', 20)
        info = self.indexinfos()
        coord = {}
        for i in self.lidxrow:
            fieldi = info[i]
            if fieldi['cat'] == 'unique':
                continue
            if isinstance(lisfuncname, dict) and len(lisfuncname) == self.lenindex:
                funci = lisfuncname[self.lname[i]]
            else:
                funci = None
            iname = self.idxname[i]
            if i in axe:
                coord[iname] = self.lidx[i].to_numpy(
                    func=funci, codec=True, **kwargs)
                coord[iname+'_row'] = (iname, np.arange(len(coord[iname])))
                coord[iname+'_str'] = (iname, self.lidx[i].to_numpy(func=util.cast,
                                       codec=True, dtype='str', maxlen=maxlen))
            else:
                self.lidx[i].setkeys(self.lidx[fieldi['pparent']].keys)
                coord[iname] = (self.idxname[fieldi['pparent']],
                                self.lidx[i].to_numpy(func=funci, codec=True, **kwargs))
        return coord
