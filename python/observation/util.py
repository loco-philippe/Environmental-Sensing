# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 12:48:16 2022

@author: a179227
"""

from collections import Counter
from itertools import product
from copy import copy
import datetime, cbor2
from timeslot import TimeSlot, TimeInterval
import json
import re
import numpy as np
from ESValue import LocationValue, DatationValue, PropertyValue, NamedValue
from ESValue import ESValue, ExternValue
import math
from ESconstante import ES, _classval
from json import JSONDecodeError 


def identity(*args, **kwargs):
    '''return the same value as args or kwargs'''
    if len(args) > 0 : return args[0]
    if len(kwargs) > 0 : return kwargs[list(kwargs.keys())[0]]
    return None

_castfunc = {'datvalue':        DatationValue,
             'locvalue':        LocationValue,
             'prpvalue':        PropertyValue,
             'namvalue':        NamedValue,
             'extvalue':        ExternValue,
             'slot':            TimeSlot,
             #'ilist':           Ilist.from_obj,
             #'observation':     Observation,
             'datetime':        datetime.datetime.fromisoformat,
             'coordinates':     LocationValue._gshape}
_invcastfunc = {val:key for key,val in _castfunc.items()}

class CborDecoder(json.JSONDecoder):
    ''' Cbor extension for integer keys (codification keys)'''
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.codecbor)
        
    def codecbor(self, dic):
        dic2 = {}
        for k, v in dic.items(): 
            try: k2 = int(k)
            except: k2 = k
            dic2[k2] = v 
        return dic2

class IindexEncoder(json.JSONEncoder):
    """new json encoder for Iindex and Ilist"""
    def default(self, o) :
        if isinstance(o, datetime.datetime): return o.isoformat()
        option = {'encoded': False, 'encode_format': 'json'}
        if o.__class__.__name__ in ('Ilist', 'TimeSlot'): return o.json(**option)
        if issubclass(o.__class__, ESValue): return o.json(**option)
        try : return o.to_json(**option)
        except :
            try : return o.__to_json__()
            except : return json.JSONEncoder.default(self, o)
    
class util:
    ''' common functions for Iindex and Ilist class'''
#%% util
    c1 = re.compile('\d+\.?\d*[,\-_ ;:]')
    c2 = re.compile('[,\-_ ;:]\d+\.?\d*')


    @staticmethod
    def canonorder(lenidx): 
        '''return a list of crossed keys from a list of number of values'''
        listrange = [range(lidx) for lidx in lenidx] 
        return util.transpose(util.list(list(product(*listrange))))

    @staticmethod
    def cast(val, dtype=None, string=True, default=None, maxlen=None):
        ''' convert val in the type defined by the string dtype'''
        typeval = val.__class__.__name__
        if dtype == 'name':
            if typeval in ES.className and val.name: name = val.name
            else: name = default
            if maxlen: return name[:maxlen]
            return name
        if dtype == 'simple':
            if typeval in ES.className: return val.vSimple(string=string)
            else: return val
        if dtype == 'json':
            if typeval in ES.className: return val.json()
            else: return val
        if dtype == 'obj':
            if typeval in ES.className: return val.to_obj(encoded=False)
            else: return val
        if dtype == 'str':  
            if maxlen: return str(val)[:maxlen]
            else: return str(val)
        #if typeval in ES.ESclassName: return val
        if not dtype : return ESValue._castsimple(val)
        if dtype == 'int':
            try : return int(val.lstrip())
            except : return math.nan
        if dtype == 'float':
            if typeval in ['float', 'int']: return float(val)
            if typeval in ES.className: return val.to_float()
            try : return float(val.lstrip())
            except : return math.nan
        if dtype == 'datetime':
            try : return  TimeInterval._dattz(datetime.datetime.fromisoformat(val))
            except ValueError: return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        if dtype == 'coord':
            if util.c1.search(val) and util.c2.search(val) :
                return [float(util.c1.search(val)[0][:-1]), float(util.c2.search(val)[0][1:])]
            else : return [-1, -1]
        if typeval in ES.ESclassName: return val
        if dtype in ES.typeName: # tous les types environmental sensing
            return ESValue.from_obj(val, ES.typeName[dtype])
        raise utilError("dtype : " + dtype + " inconsistent with data")
        
    @staticmethod
    def castobj(lis, classvalue=None):
        ''' convert a list of values in the ESValue defined by the string classvalue'''
        if not lis: return lis
        return [util.castval(val, classvalue) for val in lis]
            
    @staticmethod
    def castval(val, classvalue=None):
        ''' convert a value in the ESValue defined by the string classvalue'''
        classn, name, value = ESValue._decodevalue(val)
        if classn: 
            classvalue = classn
        if classvalue is None: dtype = None
        else: dtype = ES.valname[classvalue]
        
        if dtype is None: 
            return util.cast(val)
        if classvalue in ES.ESclassName: # or dtype is None:
            return util.cast(ESValue.from_obj(val, classvalue), dtype) # ESValue.cast()
        if classvalue == ES.ES_clsName: 
            return _classval()[ESValue.valClassName(val)](val) #cast auto ESValue 
        if classvalue in ES.className: 
            return _classval()[classvalue](value)
        return val

    @staticmethod
    def couplinginfos(l1, l2):
        '''return a dict with the coupling info between two list'''
        if not l1 or not l2:
            return {'lencoupling': 0, 'rate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': 0, 'distmax': 0, 'diff': 0, 'typecoupl': 'null'}
        ls = len(util.tocodec(l1))
        lo = len(util.tocodec(l2))
        x0 = max(ls, lo)
        x1 = ls * lo
        diff = abs(ls - lo)
        if min(ls, lo) == 1: 
            if ls == 1: typec = 'derived'
            else: typec = 'derive'
            return {'lencoupling': x0, 'rate': 0, 'disttomin': 0, 'disttomax': 0,
                    'distmin': x0, 'distmax': x1, 'diff': diff, 'typecoupl': typec}
        x = len(util.tocodec([tuple((v1,v2)) for v1, v2 in zip(l1, l2)]))
        dic = {'lencoupling': x, 'rate': (x - x0) / (x1 - x0),
                'disttomin': x - x0,  'disttomax': x1 - x,
                'distmin': x0, 'distmax': x1, 'diff': diff}
        if   dic['rate'] == 0 and dic['diff'] == 0: dic['typecoupl'] = 'coupled'
        elif dic['rate'] == 0 and ls < lo:          dic['typecoupl'] = 'derived'
        elif dic['rate'] == 0 and ls > lo:          dic['typecoupl'] = 'derive'
        elif dic['rate'] == 1:                      dic['typecoupl'] = 'crossed'
        elif ls < lo:                               dic['typecoupl'] = 'linked'
        else:                                       dic['typecoupl'] = 'link'
        return dic

    @staticmethod 
    def decodeobj(bs=None, classname=None, context=True):
        '''Generate an Iindex data from a bytes, json or dict value

        *Parameters*

        - **bs** : bytes, string or dict data to convert
        - **classname** : string(default None) - classname to convert codec data
        - **context** : boolean (default True) - if False, only codec and keys are included

        *Returns* : tuple - name, typevaluedec, codec, parent, keys'''
        if bs is None: return (None, None, [], ES.nullparent, None)
        if   isinstance(bs, bytes): lis = cbor2.loads(bs)
        #elif isinstance(bs, str): lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, str) and bs[0] in ['{', '[']:
            lis = json.loads(bs, object_hook=CborDecoder().codecbor)
        elif isinstance(bs, list):  lis = bs
        else: lis = [bs]
        #else: raise utilError("the type of parameter is not available")
        if not isinstance(lis, list): raise utilError("the parameter has to be a list")
        
        if not lis:
            return (None, None, [], ES.nullparent, None)        
        if context and (not isinstance(lis[0], (str, dict, list)) or len(lis) > 3): 
            return (None, None, util.decodecodec(lis, classname), ES.nullparent, None)
        if not context and len(lis) > 2: 
            return (None, None, util.decodecodec(lis, classname), ES.nullparent, None)
        if len(lis) == 3 and isinstance(lis[0], (str, dict)) and isinstance(lis[1], list) \
            and isinstance(lis[2], (list, int)) and context: 
            return (*util.decodecontext(lis[0]), util.decodecodec(lis[1], classname), *util.decodekeys(lis[2]))
        if len(lis) == 2 and isinstance(lis[0], (str, dict)) and isinstance(lis[1], list) and context:
            return (*util.decodecontext(lis[0]), util.decodecodec(lis[1], classname), ES.nullparent, None)
        #if len(lis) == 2 and isinstance(lis[0], (tuple, list)) and isinstance(lis[1], (int, list)):
        if len(lis) == 2 and isinstance(lis[0], (tuple, list)) and util.iskeysobj(lis[1]):
            return (None, None, util.decodecodec(lis[0], classname), *util.decodekeys(lis[1]))
        #if len(lis) == 1 and isinstance(lis[0], list):
        #    return (None, None, util.decodecodec(lis[0], classname), ES.nullparent, None)
        return (None, None, util.decodecodec(lis, classname), ES.nullparent, None)
        
    @staticmethod
    def iskeysobj(obj):
        if isinstance(obj, int):                        return True
        if not isinstance(obj, list):                   return False
        if len(obj) == 0:                               return True
        if not isinstance(obj[0], int):                 return False
        if len(obj) == 1:                               return True
        if len(obj) > 2 and not isinstance(obj[1], int):return False
        if len(obj) == 2 and isinstance(obj[1], int):   return True
        if len(obj) == 2 and isinstance(obj[1], list): obj = obj[1]
        if not isinstance(obj, list):                   return False
        for i in range(len(obj)):
            if not isinstance(obj[i], int):             return False
        return True
        
    @staticmethod
    def decodecodec(codecobj, classname=ES.nam_clsName):
        '''Generate a codec list from a json value'''
        return [ESValue.from_obj(val, classname=classname) for val in codecobj]
        
    @staticmethod
    def decodecontext(context):
        '''Generate a tuple (name, dtype) from a json value'''
        if isinstance(context, dict) and len(context)==1:
            name, dtype = list(context.items())[0][0]
            if isinstance(name, str) and isinstance(dtype, str) and dtype in ES.typeName.keys():  
                return (name, ES.typeName[dtype])
            raise utilError('name or typevalue is unconsistent')
        if context in ES.typeName.keys(): return (context, ES.typeName[context])
        if isinstance(context, str): return (context, None)
        raise utilError('name or typevalue is unconsistent')

    @staticmethod
    def decodekeys(keys):
        '''Generate a tuple (parent, keys) from a json value'''
        if isinstance(keys, int): return (keys, None)
        if isinstance(keys, list) and len(keys) == 0:
            return (ES.nullparent, keys)
        if isinstance(keys, list) and len(keys) == 1 and isinstance(keys[0], int):
            return (keys[0], None)
        if isinstance(keys, list) and len(keys) == 2 and isinstance(keys[0], int) \
            and isinstance(keys[1], list): return (keys[0], keys[1])
        if isinstance(keys, list) and len(keys) > 1: return (ES.nullparent, keys)
        raise utilError('parent or keys is unconsistent')
    
    @staticmethod
    def encodeobj(codeclist, keyslist=None, name=None, fullcodec=False, simpleval=False, 
                  codecval=False, typevalue=None, parent=ES.nullparent, listunic=False, **kwargs):
        '''
        Return a formatted object with values, keys and codec.
        - Format can be json, bson or cbor
        - object can be string, bytes or dict

        *Parameters*
        - **codeclist** : list of codec ESValue to encode
        - **keyslist** : list (default = None) - int keys to encode, None if no keys 
        - **name** : string (default = None) - name to encode, None if no name 
        - **fullcodec** : boolean (default False) - if True, use a full codec
        - **typevalue** : string (default None) - type to convert values
        - **parent** : int (default ES.nullparent) - Ilist index linked to
        - **listunic** : boolean (default False) - if False, when len(result)=1 return value not list
        - **codecval** : boolean (default False) - if True, only list of codec values is included
        - **simpleval** : boolean (default False) - if True, only value (without name) is included

        *Parameters (kwargs)*

        - **encoded** : boolean (default False) - choice for return format (string/bytes if True, dict else)
        - **encode_format**  : string (default 'json')- choice for return format (json, cbor)
        - **codif** : dict (default ES.codeb). Numerical value for string in CBOR encoder
        - **untyped** : boolean (default False) - include dtype in the json if True

        *Returns* : string, bytes or dict'''
        option = {'encoded': False, 'encode_format': 'json', 'untyped': False,
                  'codif': {}, 'typevalue': typevalue} | kwargs
        js = []
        if not codecval:
            if name and typevalue:          js.append({name: typevalue})
            elif name:                      js.append(name)
            elif typevalue:                 js.append(typevalue)
        codlis = [util.json(cc, encoded=False, typevalue=None, simpleval=simpleval, 
                            fullcodec=fullcodec, untyped=option['untyped']) for cc in codeclist]
        if len(js) == 1 and isinstance(js[0], str): listunic = True
        if len(codlis) == 1 and not listunic and not isinstance(codlis[0], list):
            codlis = codlis[0]
        js.append(codlis)
        '''js.append([util.json(cc, encoded=False, typevalue=None, simpleval=simpleval, 
                             fullcodec=fullcodec, untyped=option['untyped']) 
                   for cc in codeclist])'''
        if not codecval: 
            if parent >= 0 and keyslist:    js.append([parent, keyslist])
            elif parent != ES.nullparent:   js.append(parent)
            elif keyslist:                  js.append(keyslist)      
        if len(js) == 1:                    js = js[0]
        if option['encoded'] and option['encode_format'] == 'json': 
            return json.dumps( js, cls=IindexEncoder)
        if option['encoded'] and option['encode_format'] == 'cbor': 
            return cbor2.dumps(js, datetime_as_timestamp=True, 
                               timezone=datetime.timezone.utc, canonical=True)
        return js

    @staticmethod
    def filter(func, lis, res, *args, **kwargs ):
        '''apply "func" to each value of "lis" and tests if equals "res".
        Return the list of index with True result.'''
        lisf = util.funclist(lis, func, *args, **kwargs)
        return [i for i in range(len(lis)) if lisf[i] == res]

    @staticmethod
    def funclist(value, func, *args, **kwargs):
        '''return the function func applied to the object value with parameters args and kwargs'''
        if func in (None, []) : return value
        lis = []
        if not (isinstance(value, list) or value.__class__.__name__ in ['Iindex', 'Ilist', 'Obs']):
            listval = [value]
        else : listval = value
        for val in listval :
            try : lis.append(val.func(*args, **kwargs))
            except :
                try : lis.append(func(val, *args, **kwargs))
                except :
                    try : lis.append(listval.func(val, *args, **kwargs))
                    except :
                        try : lis.append(func(listval, val, *args, **kwargs))
                        except : raise utilError("unable to apply func")
        if len(lis) == 1 : return lis[0]
        return lis

    @staticmethod
    def hash(listval):
        ''' return sum of hash values in the list'''
        return sum([hash(i) for i in listval])

    @staticmethod
    def idxfull(setidx):
        '''return additional keys for each index in the setidx list to have crossed setidx'''
        setcodec = [set(idx.keys) for idx in setidx]
        lenfull = util.mul([len(codec) for codec in setcodec])
        if lenfull <= len(setidx[0]) : return []
        complet = Counter(list(product(*setcodec))) 
        complet.subtract(Counter(util.tuple(util.transpose([idx.keys for idx in setidx]))))
        keysadd = util.transpose(util.list(list(complet.elements())))
        if not keysadd : return []
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
        if  value.__class__.__name__ in ES.valname:
            return value != value.__class__(nullvalue)
        return not value is None
    
    @staticmethod
    def idxlink(ref, l2):
        ''' return a dict for each different tuple (ref value, l2 value)'''
        lis = set(util.tuple(util.transpose([ref, l2])))
        if not len(lis) == len(set(ref)) : return {}
        return dict(lis)

    @staticmethod
    def json(val, **option):      
        val = ESValue._uncastsimple(val)
        if isinstance(val, (str, int, float, bool, list, dict, type(None), bytes)): 
            return val        
        if option['simpleval']: return val.json(**option)
        if val.__class__.__name__ in ES.ESclassName:      #ESValue
            if not option['typevalue']: return val.json(**option)
            else: return {_invcastfunc[val.__class__]: val.json(**option)} 
        if val.__class__.__name__ == 'Ilist':       return {ES.ili_valName: val.json(**option)}
        if val.__class__.__name__ == 'Iindex':      return {ES.iin_valName: val.json(**option)}
        if val.__class__.__name__ == 'Obs':         return {ES.obs_valName: val.to_obj(**option)}

    @staticmethod
    def list(tuplelists): 
        '''transform a list of tuples in a list of lists'''
        return list(map(list, tuplelists))

    @staticmethod
    def mul(values):
        '''return the product of values in a list or tuple '''
        mul = 1
        for val in values : mul *= val
        return mul

    @staticmethod
    def reindex(oldkeys, oldcodec, newcodec) :
        '''new keys with new order of codec'''
        dic= {newcodec[i]:i for i in range(len(newcodec))}
        return [dic[oldcodec[key]] for key in oldkeys]

    @staticmethod
    def reorder(values, sort=None):
        '''return a new values list following the order define by sort'''
        if not sort: return values
        return [values[ind] for ind in sort]
    
    @staticmethod
    def resetidx(values):
        '''return codec and keys from a list of values'''
        #t0 = time()
        codec = util.tocodec(values)
        #print('fin codec', time() - t0)
        return (codec, util.tokeys(values, codec))

    @staticmethod
    def pparent(row, infos): 
        '''return field 'pparent' '''  
        field =infos[row]
        if field['pparent'] != 0: return field['pparent']
        if   field['cat'] == 'primary': field['pparent'] = field['num']
        elif field['cat'] == 'unique' : field['pparent'] = -1
        else: field['pparent'] = util.pparent(field['parent'], infos)
        return field['pparent']

    @staticmethod
    def str(listvalues): 
        '''return a list with values in the str format'''
        return [str(val) for val in listvalues]

    @staticmethod
    def tokeys(values, codec=None):
        ''' return a list of keys from a list of values'''
        if not codec: codec = util.tocodec(values)
        #print('tokeys')
        #t0=time()
        dic = {codec[i]:i for i in range(len(codec))} #!!!!long
        #print('gendic', time()-t0)
        keys = [dic[val] for val in values]    # hyper long
        #print('genkeys', time()-t0)
        return keys
        #return [codec.index(val) for val in values]
 
    @staticmethod
    def tovalues(keys, codec):
        '''return a list of values from a list of keys and a list of codec values'''
        return [codec[key] for key in keys]

    @staticmethod
    def tonumpy(valuelist, func=None, **kwargs):
        '''return a Numpy Array from a list of values converted by func'''
        if func is None : func = identity
        if func == 'index' : return np.array(list(range(len(valuelist))))
        valList = util.funclist(valuelist, func, **kwargs)
        if isinstance(valList[0], str):
            try : datetime.datetime.fromisoformat(valList[0])
            except : return np.array(valList)
            return np.array(valList, dtype=np.datetime64)
        if isinstance(valList[0], datetime.datetime): return np.array(valList, dtype=np.datetime64)
        return np.array(valList)

    @staticmethod
    def tocodec(values, keys=None):
        '''extract a list of unique values'''
        if not keys: return list(set(values))
        ind, codec = zip(*sorted(set(zip(keys,values))))
        return list(codec)
    
    @staticmethod
    def transpose(idxlist):
        '''exchange row/column in a list of list'''
        if not isinstance(idxlist, list): raise utilError('index not transposable')
        if not idxlist: return []
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

    @staticmethod
    def listed(idx):
        '''transform a tuple of tuple in a list of list'''
        return [val if not isinstance(val, tuple) else util.listed(val) for val in idx]
    
    @staticmethod
    def typename(name, typevalue=None):
        if not name:            return typevalue
        if name in ES.typeName: return ES.typeName[name]
        if name[0:2] == 'ES':   return ES.ES_clsName
        return typevalue

class utilError(Exception):
    ''' util Exception'''
    #pass