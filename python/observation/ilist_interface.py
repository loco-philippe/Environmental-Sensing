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
    '''this class includes Ilist methods :

    - `IlistInterface.json`
    - `IlistInterface.plot`
    - `IlistInterface.to_obj`
    - `IlistInterface.to_csv`
    - `IlistInterface.to_file`
    - `IlistInterface.to_xarray`
    - `IlistInterface.to_dataframe`
    - `IlistInterface.view`
    - `IlistInterface.vlist`
    - `IlistInterface.voxel`
    '''

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

    def plot(self, varname=None, idxname=None, order=None, line=True, size=5, marker='o', maxlen=20):
        '''
        This function visualize data with line or colormesh.

        *Parameters*

        - **varname** : string (default none) - Name of the variable to use. If None,
        first lvarname is used.
        - **line** : Boolean (default True) - Choice line or colormesh.
        - **order** : list (defaut None) - order of the axes (x, y, hue or col)
        - **size** : int (defaut 5) - plot size
        - **marker** : Char (default 'o') - Symbol for each point.
        - **maxlen** : Integer (default 20) - maximum length for string

        *Returns*

        - **None**  '''
        if not self.consistent:
            return None
        if idxname:
            idxname = [name for name in idxname if len(
                self.nindex(name).codec) > 1]
        xar = self.to_xarray(numeric=True, varname=varname, idxname=idxname, lisfunc=[util.cast],
                             dtype='str', npdtype='str', maxlen=maxlen, coord=True)
        if not order:
            order = [0, 1, 2]

        if len(xar.dims) == 1:
            xar.plot.line(x=xar.dims[0]+'_row', size=size, marker=marker)
        elif len(xar.dims) == 2 and line:
            xar.plot.line(x=xar.dims[order[0]] + '_row',
                          xticks=list(xar.coords[xar.dims[0]+'_row'].values),
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

    def to_obj(self, **kwargs):
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
        - **fullvar** : boolean (default True) - if True and modecodec='optimize, 
        variable index is with a full codec
        - **geojson** : boolean (default False) - geojson for LocationValue if True

        *Returns* : string, bytes or dict'''
        option = {'modecodec': 'optimize', 'encoded': False,
                  'encode_format': 'json', 'codif': ES.codeb, 'name': False,
                  'geojson': False, 'fullvar': True} | kwargs
        option2 = {'encoded': False, 'encode_format': 'json',
                   'codif': option['codif'], 'geojson': option['geojson'],
                   'modecodec': option['modecodec'], 'fullvar': option['fullvar']}
        if option['modecodec'] == 'dict':
            lis = {}
            for idx in self.lindex:
                name, dicval = list(idx.to_dict_obj(**option2).items())[0]
                if name in self.lvarname:
                    dicval['var'] = True
                lis[name] = dicval
        else:
            indexname = [option['name'] or name != 'i' + str(i)
                         for i, name in enumerate(self.lname)]
            if option['modecodec'] != 'optimize':
                lis = [idx.to_obj(name=iname, **option2)
                       for idx, iname in zip(self.lindex, indexname)]
            else:
                lis = self._optimize_obj(indexname, **option2)

        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(lis, cls=IindexEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor':
            return cbor2.dumps(lis, datetime_as_timestamp=True,
                               timezone=datetime.timezone.utc, canonical=True)
        return lis

    def to_xarray(self, info=False, idxname=None, varname=None, fillvalue='?',
                  fillextern=True, lisfunc=None, name=None, numeric=False,
                  npdtype=None, attrs=None, coord=False, **kwargs):
        '''
        Complete the Object and generate a Xarray DataArray with the dimension define by idx.
        Only the first variable is incuded.

        *Parameters*

        - **info** : boolean (default False) - if True, add _dict attributes to attrs Xarray
        - **idxname** : list (default none) - list of idx to be completed. If None,
        self.primary is used.
        - **varname** : string (default none) - Name of the variable to use. If None,
        first lvarname is used.
        - **fillvalue** : object (default '?') - value used for the new extval
        - **fillextern** : boolean(default True) - if True, fillvalue is converted to typevalue
        - **lisfunc** : function (default none) - list of function to apply to indexes before export
        - **name** : string (default None) - DataArray name. If None, variable name
        - **numeric** : Boolean (default False) - Generate a numeric DataArray.Values.
        - **npdtype** : string (default None) - numpy dtype for the DataArray ('object' if None)
        - **attrs** : dict (default None) - attributes for the DataArray
        - **coord** : boolean (default False) - if True, add derivated coords
        - **kwargs** : parameter for lisfunc

        *Returns* : DataArray '''
        option = {'dtype': None} | kwargs
        if not self.consistent:
            raise IlistError("Ilist not consistent")
        if idxname is None or idxname == []:
            idxname = self.primaryname
        ilf = self.full(idxname=idxname, varname=varname, fillvalue=fillvalue,
                        fillextern=fillextern, inplace=False)
        ilf.setcanonorder()
        if not varname and len(ilf.lvarname) != 0:
            varname = ilf.lvarname[0]
        if not varname in ilf.lname:
            ivar = -1
        else:
            ivar = ilf.lname.index(varname)
        if isinstance(lisfunc, list) and len(lisfunc) == 1:
            lisfunc = lisfunc * ilf.lenindex
        elif isinstance(lisfunc, list) and len(lisfunc) != ilf.lenindex:
            lisfunc = [None] * ilf.lenindex
        elif not isinstance(lisfunc, list):
            funcvar = lisfunc
            lisfunc = [None] * ilf.lenindex
            if ivar != -1:
                lisfunc[ivar] = funcvar
        lisfuncname = dict(zip(ilf.lname, lisfunc))
        coords = ilf._xcoord(idxname, ivar, lisfuncname, coord, **option)
        dims = idxname
        if numeric:
            lisfunc[ivar] = util.cast
            fillvalue = math.nan
            npdtype = 'float'
            option['dtype'] = 'float'
        if ivar == -1:
            data = Iindex(list(range(len(ilf)))).to_numpy(npdtype='int')\
                .reshape([len(ilf.nindex(name).codec) for name in idxname])
        else:
            data = ilf.lindex[ivar]\
                .to_numpy(func=lisfunc[ivar], npdtype=npdtype, **option)\
                .reshape([len(ilf.nindex(name).codec) for name in idxname])
        if not name and ivar == -1:
            name = ilf.name
        elif not name:
            name = ilf.lname[ivar]
        if not isinstance(attrs, dict):
            attrs = {}
        for nam in ilf.lunicname:
            attrs[nam] = ilf.nindex(nam).codec[0]
        if info:
            attrs |= ilf.indexinfos()
        return xarray.DataArray(data, coords, dims, attrs=attrs, name=name)

    def voxel(self, idxname=None, varname=None):
        '''
        Plot not null values in a cube with voxels and return indexes values.

        *Parameters*

        - **idxname** : list (default none) - list of idx to be completed. If None,
        self.primary is used.
        - **varname** : string (default none) - Name of the variable to use. If None,
        first lvarname is used.

        *Returns* : **dict of indexes values**
        '''
        if not self.consistent:
            return None
        if idxname is None or idxname == []:
            idxname = self.primaryname
        if varname is None and self.lvarname:
            varname = self.lvarname[0]
        if len(idxname) > 3:
            raise IlistError('number of idx > 3')
        if len(idxname) == 2:
            self.addindex(Iindex('null', ' ', keys=[0]*len(self)))
            idxname += [' ']
        elif len(idxname) == 1:
            self.addindex(Iindex('null', ' ', keys=[0]*len(self)))
            self.addindex(Iindex('null', '  ', keys=[0]*len(self)))
            idxname += [' ', '  ']
        xar = self.to_xarray(idxname=idxname, varname=varname, fillvalue='?',
                             fillextern=False, lisfunc=util.isNotEqual, tovalue='?')
        axe = plt.figure().add_subplot(projection='3d')
        axe.voxels(xar, edgecolor='k')
        axe.set_xticks(np.arange(self.idxlen[self.idxname.index(xar.dims[0])]))
        axe.set_yticks(np.arange(self.idxlen[self.idxname.index(xar.dims[1])]))
        axe.set_zticks(np.arange(self.idxlen[self.idxname.index(xar.dims[2])]))
        axe.set(xlabel=xar.dims[0][:8],
                ylabel=xar.dims[1][:8],
                zlabel=xar.dims[2][:8])
        plt.show()
        self.delindex([' ', '  '])
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
        - **index** : integer - index to update (index=-1 for first variable)

        *Returns* : list of func result'''
        if index == -1 and self.lvar:
            return self.lvar[0].vlist(func, *args, **kwargs)
        if index == -1 and self.lenindex == 1:
            index = 0
        return self.lindex[index].vlist(func, *args, **kwargs)

    # %%internal
    def _optimize_obj(self, idxname, **option2):
        '''return list object with optimize modecodec'''
        indexinfos = self.indexinfos()
        notkeys = True
        lis = []
        if self.iscanonorder():
            notkeys = None
        for idx, iname, inf in zip(self.lindex, idxname, indexinfos):
            if inf['cat'] == 'unique':
                lis.append(idx.tostdcodec(full=False).to_obj(
                    name=iname, **option2))
            elif inf['cat'] == 'primary':
                lis.append(idx.to_obj(keys=notkeys, name=iname, **option2))
            elif inf['cat'] == 'coupled':
                lis.append(idx.setkeys(self.lindex[inf['parent']].keys, inplace=False).
                           to_obj(parent=inf['parent'], name=iname, **option2))
            elif inf['parent'] == -1:  # cat='variable' or 'secondary'
                if option2['fullvar'] and inf['cat'] == 'variable' and not(inf['child']):
                    opt = option2 | {'modecodec': 'full'}
                    lis.append(idx.to_obj(name=iname, **opt))
                elif idx.keys == list(range(len(self))):
                    lis.append(idx.to_obj(name=iname, **option2))
                else:
                    lis.append(idx.to_obj(keys=True, name=iname, **option2))
            else:  # derived
                if len(self.lindex[inf['parent']].codec) == len(self):
                    lis.append(idx.to_obj(keys=True, name=iname, **option2))
                elif idx.iskeysfromderkeys(self.lindex[inf['parent']]):
                    lis.append(idx.to_obj(parent=inf['parent'],
                                          name=iname, **option2))
                else:
                    keys = idx.derkeys(self.lindex[inf['parent']])
                    lis.append(idx.to_obj(keys=keys, parent=inf['parent'],
                                          name=iname, **option2))
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

    def _xcoord(self, axename, ivar, lisfuncname=None, coord=False, **kwargs):
        ''' Coords generation for Xarray'''
        maxlen = kwargs.get('maxlen', 20)
        info = self.indexinfos()
        coords = {}
        for i in range(self.lenindex):
            fieldi = info[i]
            iname = self.lname[i]
            if fieldi['pparent'] == -1 or i == ivar:
                continue
            if isinstance(lisfuncname, dict) and len(lisfuncname) == self.lenindex:
                funci = lisfuncname[iname]
            else:
                funci = None
            if iname in axename:
                coords[iname] = self.lindex[i].to_numpy(
                    func=funci, codec=True, **kwargs)
                if coord:
                    coords[iname+'_row'] = (iname,
                                            np.arange(len(coords[iname])))
                    coords[iname+'_str'] = (iname, self.lindex[i].to_numpy(func=util.cast,
                                                                           codec=True, dtype='str', maxlen=maxlen))
            else:
                self.lindex[i].setkeys(
                    self.lindex[fieldi['pparent']].keys)  # !!!
                coords[iname] = (self.lname[fieldi['pparent']],
                                 self.lindex[i].to_numpy(func=funci, codec=True, **kwargs))
        return coords
