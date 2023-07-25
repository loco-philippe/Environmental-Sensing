# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 12:48:16 2022

@author: philippe@loco-labs.io
"""

from collections import Counter
from itertools import product
import datetime
import re
import numpy as np
import math

from observation.timeslot import TimeInterval
from observation.esconstante import ES, _classval
from observation.esvalue_base import ESValue


def identity(*args, **kwargs):
    '''return the same value as args or kwargs'''
    if len(args) > 0:
        return args[0]
    if len(kwargs) > 0:
        return kwargs[list(kwargs.keys())[0]]
    return None


class util:
    ''' common functions for Field and Dataset class'''
# %% util
    c1 = re.compile('\d+\.?\d*[,\-_ ;:]')
    c2 = re.compile('[,\-_ ;:]\d+\.?\d*')

    @staticmethod
    def canonorder(lenidx):
        '''return a list of crossed keys from a list of number of values'''
        listrange = [range(lidx) for lidx in lenidx]
        return util.transpose(util.list(list(product(*listrange))))

    """@staticmethod
    def cast(val, dtype=None, string=True, default=None, maxlen=None):
        ''' convert val in the type defined by the string dtype'''
        typeval = val.__class__.__name__
        if dtype == 'name':
            if typeval in ES.className and val.name:
                name = val.name
            else:
                name = default
            if maxlen:
                return name[:maxlen]
            return name
        if dtype == 'simple':
            if typeval in ES.className:
                return val.vSimple(string=string)
            else:
                return val
        if dtype == 'json':
            if typeval in ES.className:
                return val.json()
            else:
                return val
        if dtype == 'obj':
            if typeval in ES.className:
                return val.to_obj(encoded=False)
            else:
                return val
        if dtype == 'str':
            if maxlen:
                return str(val)[:maxlen]
            else:
                return str(val)
        if not dtype:
            return ESValue._castsimple(val)
        if dtype == 'int':
            try:
                return int(val.lstrip())
            except:
                return math.nan
        if dtype == 'float':
            if typeval in ['float', 'int']:
                return float(val)
            if typeval in ES.className:
                return val.to_float()
            try:
                return float(val.lstrip())
            except:
                return math.nan
        if dtype == 'datetime':
            try:
                return TimeInterval._dattz(datetime.datetime.fromisoformat(val))
            except ValueError:
                return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        if dtype == 'coord':
            if util.c1.search(val) and util.c2.search(val):
                return [float(util.c1.search(val)[0][:-1]), float(util.c2.search(val)[0][1:])]
            else:
                return [-1, -1]
        if typeval in ES.ESclassName:
            return val
        if dtype in ES.typeName:  # tous les types environmental sensing
            return ESValue.from_obj(val, ES.typeName[dtype])
        raise utilError("dtype : " + dtype + " inconsistent with data")

    @staticmethod
    def castobj(lis, classvalue=None):
        ''' convert a list of values in the ESValue defined by the string classvalue'''
        if not lis:
            return lis
        return [util.castval(val, classvalue) for val in lis]

    @staticmethod
    def castval(val, classvalue=None):
        ''' convert a value in the ESValue defined by the string classvalue'''
        classn, name, value = ESValue._decodevalue(val)
        if classn:
            classvalue = classn
        if classvalue is None:
            dtype = None
        else:
            dtype = ES.valname[classvalue]

        if dtype is None:
            return util.cast(val)
        if classvalue in ES.ESclassName:  # ESValue.cast()
            return util.cast(ESValue.from_obj(val, classvalue), dtype)
        if classvalue == ES.ES_clsName:   # cast auto ESValue
            return _classval()[ESValue.valClassName(val)].from_obj(val)
            # return _classval()[ESValue.valClassName(val)](val)
        if classvalue in ES.className:
            return _classval()[classvalue].obj(value)
            # return _classval()[classvalue](value)
        return val"""

    @staticmethod
    def couplinginfos(l1, l2):
        '''return a dict with the coupling info between two list'''
        if not l1 or not l2:
            return {'dist': 0, 'rateder': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': 0, 'distmax': 0, 'diff': 0, 'typecoupl': 'null'}
        ls = len(util.tocodec(l1))
        lo = len(util.tocodec(l2))
        x0 = max(ls, lo)
        x1 = ls * lo
        diff = abs(ls - lo)
        if min(ls, lo) == 1:
            if ls == 1:
                typec = 'derived'
            else:
                typec = 'derive'
            return {'dist': x0, 'rateder': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': x0, 'distmax': x1, 'diff': diff, 'typecoupl': typec}
        x = len(util.tocodec([tuple((v1, v2)) for v1, v2 in zip(l1, l2)]))
        dic = {'dist': x, 'rateder': (x - x0) / (x1 - x0),
               'disttomin': x - x0,  'disttomax': x1 - x,
               'distmin': x0, 'distmax': x1, 'diff': diff}
        if dic['rateder'] == 0 and dic['diff'] == 0:
            dic['typecoupl'] = 'coupled'
        elif dic['rateder'] == 0 and ls < lo:
            dic['typecoupl'] = 'derived'
        elif dic['rateder'] == 0 and ls > lo:
            dic['typecoupl'] = 'derive'
        elif dic['rateder'] == 1:
            dic['typecoupl'] = 'crossed'
        elif ls < lo:
            dic['typecoupl'] = 'linked'
        else:
            dic['typecoupl'] = 'link'
        return dic

    @staticmethod
    def filter(func, lis, res, *args, **kwargs):
        '''apply "func" to each value of "lis" and tests if equals "res".
        Return the list of index with True result.'''
        lisf = util.funclist(lis, func, *args, **kwargs)
        return [i for i in range(len(lis)) if lisf[i] == res]

    @staticmethod
    def funclist(value, func, *args, **kwargs):
        '''return the function func applied to the object value with parameters args and kwargs'''
        if func in (None, []):
            return value
        lis = []
        if not (isinstance(value, list) or value.__class__.__name__ in ['Field', 'Dataset', 'Observation']):
            listval = [value]
        else:
            listval = value
        for val in listval:
            try:
                lis.append(val.func(*args, **kwargs))
            except:
                try:
                    lis.append(func(val, *args, **kwargs))
                except:
                    try:
                        lis.append(listval.func(val, *args, **kwargs))
                    except:
                        try:
                            lis.append(func(listval, val, *args, **kwargs))
                        except:
                            raise utilError("unable to apply func")
        if len(lis) == 1:
            return lis[0]
        return lis

    @staticmethod
    def hash(listval):
        ''' return sum of hash values in the list'''
        # return sum([hash(i) for i in listval])
        return hash(tuple(listval))

    @staticmethod
    def idxfull(setidx):
        '''return additional keys for each index in the setidx list to have crossed setidx'''
        setcodec = [set(idx.keys) for idx in setidx]
        lenfull = util.mul([len(codec) for codec in setcodec])
        if lenfull <= len(setidx[0]):
            return []
        complet = Counter(list(product(*setcodec)))
        complet.subtract(
            Counter(util.tuple(util.transpose([idx.keys for idx in setidx]))))
        keysadd = util.transpose(util.list(list(complet.elements())))
        if not keysadd:
            return []
        return keysadd

    @staticmethod
    def isEqual(value, tovalue=None, **kwargs):
        ''' return True if value and tovalue are equal'''
        return value.__class__.__name__ == tovalue.__class__.__name__ and \
            value == tovalue

    @staticmethod
    def isNotEqual(value, tovalue=None, **kwargs):
        ''' return True if value and tovalue are not equal'''
        return value.__class__.__name__ != tovalue.__class__.__name__ or \
            value != tovalue

    @staticmethod
    def isNotNull(value, nullvalue=None, **kwargs):
        '''return boolean. True if value' is not a NullValue'''
        if value.__class__.__name__ in ES.valname:
            return value != value.__class__(nullvalue)
        return not value is None

    @staticmethod
    def idxlink(ref, l2):
        ''' return a dict for each different tuple (ref value, l2 value)'''
        return dict(set(zip(ref, l2)))
        #lis = set(util.tuple(util.transpose([ref, l2])))
        # if not len(lis) == len(set(ref)):
        #    return {}
        # return dict(lis)

    @staticmethod
    def json(val, **option):
        datecast = True
        if 'datetime' in option:
            datecast = option['datetime']
        val = ESValue.uncastsimple(val, datecast)
        if isinstance(val, (str, int, float, bool, list, dict, type(None), bytes, datetime.datetime)):
            return val
        if option['simpleval']:
            return val.json(**option)
        if val.__class__.__name__ in ES.ESclassName:  # ESValue
            if not option['typevalue']:
                return val.json(**option)
            else:
                return {ES.valname[val.__class__.__name__]: val.json(**option)}
        if val.__class__.__name__ == 'Dataset':
            return {ES.ili_valName: val.json(**option)}
        if val.__class__.__name__ == 'Field':
            return {ES.iin_valName: val.json(**option)}
        if val.__class__.__name__ == 'Observation':
            return {ES.obs_valName: val.to_obj(**option)}

    @staticmethod
    def list(tuplelists):
        '''transform a list of tuples in a list of lists'''
        return list(map(list, tuplelists))

    @staticmethod
    def listed(idx):
        '''transform a tuple of tuple in a list of list'''
        return [val if not isinstance(val, tuple) else util.listed(val) for val in idx]

    @staticmethod
    def mul(values):
        '''return the product of values in a list or tuple (math.prod)'''
        mul = 1
        for val in values:
            mul *= val
        return mul

    @staticmethod
    def pparent(row, infos):
        '''return field 'pparent' '''
        if row < 0:
            return row
        field = infos[row]
        # if field['pparent'] != 0:
        if field['pparent'] != -2:
            return field['pparent']
        if field['cat'] == 'primary':
            field['pparent'] = field['num']
        elif field['cat'] == 'unique':
            field['pparent'] = -1
        else:
            field['pparent'] = util.pparent(field['parent'], infos)
        return field['pparent']

    @staticmethod
    def pparent2(row, infos):
        '''return field 'pparent' '''
        if row < 0:
            return row
        field = infos[row]
        # if field['pparent'] != 0:
        if field['pparent'] != -2:
            return field['pparent']
        if field['cat'] == 'primary':
            field['pparent'] = field['num']
        elif field['cat'] == 'unique':
            field['pparent'] = -1
        else:
            field['pparent'] = util.pparent2(field['parent'], infos)
        return field['pparent']

    @staticmethod
    def reindex(oldkeys, oldcodec, newcodec):
        '''new keys with new order of codec'''
        dic = {newcodec[i]: i for i in range(len(newcodec))}
        return [dic[oldcodec[key]] for key in oldkeys]

    @staticmethod
    def reorder(values, sort=None):
        '''return a new values list following the order define by sort'''
        if not sort:
            return values
        return [values[ind] for ind in sort]

    @staticmethod
    def resetidx(values):
        '''return codec and keys from a list of values'''
        codec = util.tocodec(values)
        return (codec, util.tokeys(values, codec))

    @staticmethod
    def str(listvalues):
        '''return a list with values in the str format'''
        return [str(val) for val in listvalues]

    @staticmethod
    def tokeys(values, codec=None):
        ''' return a list of keys from a list of values'''
        if not codec:
            codec = util.tocodec(values)
        dic = {codec[i]: i for i in range(len(codec))}  # !!!!long
        keys = [dic[val] for val in values]    # hyper long
        return keys

    @staticmethod
    def tovalues(keys, codec):
        '''return a list of values from a list of keys and a list of codec values'''
        return [codec[key] for key in keys]

    @staticmethod
    def tonumpy(valuelist, func=None, **kwargs):
        '''return a Numpy Array from a list of values converted by func'''
        if func is None:
            func = identity
        if func == 'index':
            return np.array(list(range(len(valuelist))))
        valList = util.funclist(valuelist, func, **kwargs)
        if isinstance(valList[0], str):
            try:
                datetime.datetime.fromisoformat(valList[0])
            except:
                return np.array(valList)
            return np.array(valList, dtype=np.datetime64)
        if isinstance(valList[0], datetime.datetime):
            return np.array(valList, dtype=np.datetime64)
        return np.array(valList)

    @staticmethod
    def tocodec(values, keys=None):
        '''extract a list of unique values'''
        if not keys:
            return list(set(values))
        ind, codec = zip(*sorted(set(zip(keys, values))))
        return list(codec)

    @staticmethod
    def transpose(idxlist):
        '''exchange row/column in a list of list'''
        if not isinstance(idxlist, list):
            raise utilError('index not transposable')
        if not idxlist:
            return []
        size = min([len(ix) for ix in idxlist])
        return [[ix[ind] for ix in idxlist] for ind in range(size)]

    @staticmethod
    def tuple(idx):
        '''transform a list of list in a list of tuple'''
        return [val if not isinstance(val, list) else tuple(val) for val in idx]

    @staticmethod
    def tupled(idx):
        '''transform a list of list in a tuple of tuple'''
        return tuple([val if not isinstance(val, list) else util.tupled(val) for val in idx])

class utilError(Exception):
    ''' util Exception'''
    # pass
