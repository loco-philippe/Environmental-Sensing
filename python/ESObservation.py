# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: Philippe@loco-labs.io



The `ES.ESObservation` module contains the main class
of Environmental Sensing : `ES.ESObservation.Observation` class.

"""
from ESObs import ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult
from ESElement import ESObject, isESObs, isESAtt, isUserAtt
from ESconstante import ES, identity
from ESValue import LocationValue, DatationValue, PropertyValue, \
    ResultValue, gshape
from shapely.geometry import shape
import json, folium, struct
import numpy as np
import xarray as xr
#import geopandas as gp
import matplotlib.pyplot as plt

class Observation(ESObject):
    """
    An `ES.ESObservation.Observation` is made up of objects from the `ES.ESObs` class
     which each describe a dimension of this object.
    """
    def __init__(self, jso = {}, order = 'dlp'):
        ESObject.__init__(self)
        self.option = ES.mOption.copy()
        self.mAtt[ES.obs_reference] = 0
        ''' Attribut décrivant une `Observation` de référence utilisée pour compléter l'Observation actuelle.'''
        self.score = -1
        ''' Nature de l'assemblage des différents composants. Par exemple 122 
        indique qu'il s'agit d'une mesure unique sur un trajet'''
        self.complet = False
        ''' True si le nombre de résultats est cohérent avec le nombre d'objets de type Location, Datation et Property.'''
        self.mAtt[ES.obs_resultTime] = "null"
        self.classES = ES.obs_classES
        self.typeES = ES.obs_typeES
        self.mAtt[ES.type] = "obsError"
        self.mAtt[ES.obs_id] = "null"
        if type(jso) == str :
            try:
                js=json.loads(jso)
            except:
                return
        elif type(jso) == dict :
            js = jso.copy()
        else : return
        if js == {}: return
        if ES.type not in list(js) or js[ES.type] != ES.obs_classES: return
        if ES.obs_id in list(js): self.mAtt[ES.obs_id] = js[ES.obs_id]
        if ES.obs_attributes in list(js): 
            if type(js[ES.obs_attributes]) == dict: js = js[ES.obs_attributes]
            else: return
        self.addAttributes(js)
        if isESObs(ES.dat_classES, js): ESSetDatation(self, js)
        if isESObs(ES.loc_classES, js): ESSetLocation(self, js)
        if isESObs(ES.prp_classES, js): ESSetProperty(self, js)
        if isESObs(ES.res_classES, js): ESSetResult  (self, js)
        self.majType(order)

    def addAttributes(self, js):
        '''Ajout d'attributs à une Observation'''
        if type(js) != dict: return
        for k, v in js.items():
            if isESAtt(ES.obs_classES, k) or isUserAtt(k): self.mAtt[k] = v
            if k == ES.parameter: 
                try:  self.parameter = json.dumps(v)
                except:  self.parameter = "null"

    @property
    def bounds(self):
        '''boîte englobante de l'Observation'''
        if self.setLocation : return shape(self).bounds
        else : return None

    @property
    def __geo_interface__(self):
        '''if self.option["json_loc_point"] : indice = 0
        else : indice = 1'''
        if self.setLocation : 
            return gshape(self.setLocation.jsonSet(self.option)).__geo_interface__
            #return gshape(self.setLocation.geoInterface(self.option)).__geo_interface__
            '''return gshape(json.dumps(json.loads('{' \
                        #+ self.setLocation.json(False, False, False, False)\
                        + self.setLocation.geoInterface(self.option)\
                        #+ '}')["coordinates"])).__geo_interface__
                        + '}')[ES.loc_valName[indice]])).__geo_interface__'''
        else : return ""

    @property
    def jsonFeature(self):
        if self.setLocation : 
            geo = self.__geo_interface__
            if geo['type'] == "MultiPolygon": typ = "Polygon"
            else : typ = "Point"
            lis = list(dict((("type", typ), ("coordinates", geo['coordinates'][i]))) for i in range(len(geo['coordinates'])))
            fea = list(dict((("type","Feature"), ("id", i), ("geometry", lis[i]))) for i in range(len(geo['coordinates'])))
            return json.dumps(dict((("type","FeatureCollection"), ("features",fea))))            
        else: return ''  
            
    @property
    def setLocation(self):  return self.element(ES.loc_classES)
    ''' Objet `setLocation`s'il existe, None sinon.'''
    @property
    def setDatation(self):  return self.element(ES.dat_classES)
    @property
    def setProperty(self):  return self.element(ES.prp_classES)
    @property
    def setResult(self):  return self.element(ES.res_classES)

    def __copy__(self):
        opt = self.option
        self.option["json_obs_val"] = True
        cop = Observation(self.json())
        self.option = opt
        cop.option = opt
        return cop

    def __iadd__(self, other):
        other_opt = other.option
        self_opt = self.option
        ndat = nloc = nres = nprp = 0
        idat = 0; iloc = 1; iprp = 2
        other.option["maj_index"] = True
        other.majType()
        self.option["maj_index"] = True
        self.majType()
        if other.setResult != None and other.setResult.getMaxIndex() > -1:
            for resVal in other.setResult.valueList:
                ndat = self.addValue(other.setDatation.valueList[resVal.ind[idat]])
                nloc = self.addValue(other.setLocation.valueList[resVal.ind[iloc]])
                nprp = self.addValue(other.setProperty.valueList[resVal.ind[iprp]])
                resv = ResultValue(resVal.value)
                resv.ind = [ndat, nloc, nprp]
                self.addResultValue(resv)
            self.majType()
        other.option = other_opt
        self.option = self_opt
        return self
    
    def __add__(self, other):
        obres = self.__copy__()
        obres.__iadd__(other)
        return obres
    
    def extend(self, obs):
        for p in obs.pComposant :
            if self.element(p.classES) == None : self.addComposant(p)
        self.majType()    
        
    def addResultValue(self, esValue):
        return self.element(ES.res_valueType).addValue(ResultValue, esValue)
    
    def addValue(self, esValue):
        if type(esValue)== PropertyValue:
            if self.element(ES.prp_valueType) == None: esSet = ESSetProperty(self)
            return self.element(ES.prp_valueType).addValue(PropertyValue, esValue)
        elif type(esValue)== LocationValue:
            if self.element(ES.loc_valueType) == None: esSet = ESSetLocation(self)
            return self.element(ES.loc_valueType).addValue(LocationValue, esValue)
        elif type(esValue)== DatationValue:
            if self.element(ES.dat_valueType) == None: esSet = ESSetDatation(self)
            return self.element(ES.dat_valueType).addValue(DatationValue, esValue)
        else: return 0

    def addListResultValue(self, listEsValue):
        if type(listEsValue) != list : return
        if self.element(ES.res_valueType) == None: resSet = ESSetResult(self)
        else: resSet = self.setResult
        for val in listEsValue : resSet.addValue(ResultValue, ResultValue(val))
            #self.addResultValue(ResultValue(val) )

    def majList(self, ValueClass, listVal, info = 'name'):
        if ValueClass == DatationValue and self.setDatation != None : 
            if info == 'name': self.setDatation.majListName(listVal)
            else : self.setDatation.majListValue(ValueClass, listVal, info == 'base')
        elif ValueClass == LocationValue and self.setLocation != None : 
            if info == 'name': self.setLocation.majListName(listVal)
            else : self.setLocation.majListValue(ValueClass, listVal, info == 'base')
        elif ValueClass == PropertyValue and self.setProperty != None : 
            if info == 'name': self.setProperty.majListName(listVal)

    def addListValue(self, ValueClass, listEsValue):
        for val in listEsValue : self.addValue(ValueClass(val) )
        
    def addValueObservation(self, val, idat, iloc, iprp):
        if self.element(ES.res_valueType) == None: resSet = ESSetResult(self)
        return self.addResultValue(ResultValue(val, [idat, iloc, iprp]))

    def addListValueObservation(self, val, idat, iloc, iprp):
        for i in range(len(val)) :
            self.addResultValue(ResultValue(val[i], [idat[i], iloc[i], iprp[i]]))

    def addValueSensor(self, val, tim, coor, nprp):
        return self.addValueObservation(val, self.addValue(tim), self.addValue(coor), nprp)

    def json(self): 
        ''' Export de l'Observation sou s la forme dune chaîne de caractères au format JSON'''
        if self.option["json_elt_type"]: option_type = 1
        else: option_type = 0
        js =""
        '''variable interne retournée'''
        if self.option["json_obs_val"]: js = "{"
        js += '"' + ES.type +'":"' + ES.obs_classES +'",'
        if self.mAtt[ES.obs_id] != "null": js += '"' + ES.obs_id + '":"' + self.mAtt[ES.obs_id] + '",'
        if self.option["json_obs_attrib"]: js += '"' + ES.obs_attributes + '":{'
        js += self.jsonAtt(option_type)
        for cp in self.pComposant:
            js += cp.json(self.option)
            if js[-1] != ',': js += ","
        if self.option["json_param"] and self.parameter != "null": 
            js += '"' + ES.parameter +'":' + self.parameter + ','
        jsInfo = self.jsonInfo(self.option["json_info_type"], self.option["json_info_nval"],
                            self.option["json_info_box"], self.option["json_info_autre"])
        if jsInfo != "" : js +=  jsInfo + ','
        if js[-1] == ',': js = js[:-1]
        if self.option["json_obs_attrib"]: js += "}"
        if self.option["json_obs_val"]:    js += "}"
        return js
    
    def to_bytes(self):
        byt = bytes()
        code_el = ES.codeb[self.classES] 
        byt += struct.pack('<B', (code_el << 5) | self.mAtt[ES.obs_reference])
        if self.setProperty != None: 
            byt += self.setProperty.to_bytes(self.option["json_prp_name"])
        if self.setLocation != None: 
            byt += self.setLocation.to_bytes(self.option["json_loc_name"])
        if self.setDatation != None: 
            byt += self.setDatation.to_bytes(self.option["json_dat_name"])
        if self.setResult != None: 
            propList = [self.setProperty.valueList[i].pType 
                        for i in range(self.setProperty.nValue)]
            byt += self.setResult.to_bytes(False, self.option["json_res_index"], 
                                           self.option["bytes_res_format"], propList)
        return byt
        
    def from_bytes(self, byt):
        code_ob = (byt[0] & 0b11100000) >> 5
        self.mAtt[ES.obs_reference] = byt[0] & 0b00011111
        if code_ob != ES.codeb[self.classES]: return
        idx = 1
        while idx < byt.__len__() :
            code_el = (byt[idx] & 0b11100000) >> 5
            #forma =  byt[idx] & 0b00001111
            if   code_el == 1: es = ESSetLocation(self)
            elif code_el == 2: es = ESSetDatation(self)
            elif code_el == 3: es = ESSetProperty(self)
            elif code_el < 6:
                es = ESSetResult(self)
                if code_el == 5: 
                    propList = [self.setProperty.valueList[i].pType 
                            for i in range(self.setProperty.nValue)]
                else :
                    n = es.from_bytes(byt[idx:], [])
                    es.majIndex(es.nValue, self.setProperty.nValue, 
                            self.setDatation.nValue, self.setLocation.nValue)
                    propList = [self.setProperty.valueList[es.valueList[i].ind[2]].pType
                            for i in range(es.nValue)]
                    es.__init__()
            else: return
            if code_el < 4 : 
                idx += es.from_bytes(byt[idx:])
            else :
                idx += es.from_bytes(byt[idx:], propList)
    
    def jsonInfoTypes(self, dcinf):
        dcinf[ES.json_type_obs] = self.mAtt[ES.type]
        if self.setLocation != None :
            if self.setLocation.nValue > 1 : 
                dcinf[ES.json_type_loc] = ES.multi + self.setLocation.mAtt[ES.type]
            else :
                dcinf[ES.json_type_loc] = self.setLocation.mAtt[ES.type]
        if self.setDatation != None :
            if self.setDatation.nValue > 1 : 
                dcinf[ES.json_type_dat] = ES.multi + self.setDatation.mAtt[ES.type]
            else :
                dcinf[ES.json_type_dat] = self.setDatation.mAtt[ES.type]
        if self.setProperty != None :
            if self.setProperty.nValue > 1 : 
                dcinf[ES.json_type_prp] = ES.multi + self.setProperty.mAtt[ES.type]
            else :
                dcinf[ES.json_type_prp] = self.setProperty.mAtt[ES.type]
        if self.setResult != None :
            if self.setResult.nValue > 1 : 
                dcinf[ES.json_type_res] = ES.multi + self.setResult.mAtt[ES.type]
            else :
                dcinf[ES.json_type_res] = self.setResult.mAtt[ES.type]

    def jsonInfoNval(self, dcinf):
        if self.setLocation != None : dcinf[ES.json_nval_loc] = self.setLocation.nValue
        if self.setDatation != None : dcinf[ES.json_nval_dat] = self.setDatation.nValue
        if self.setProperty != None : dcinf[ES.json_nval_prp] = self.setProperty.nValue
        if self.setResult   != None : dcinf[ES.json_nval_res] = self.setResult.nValue

    def jsonInfoBox(self, dcinf):
        if self.setLocation != None :
            dcinf[ES.loc_boxMin] = self.setLocation.boxMin.point
            dcinf[ES.loc_boxMax] = self.setLocation.boxMax.point
        if self.setDatation != None :
            dcinf[ES.dat_boxMin] = self.setDatation.boxMin.json(ES.mOption)
            dcinf[ES.dat_boxMax] = self.setDatation.boxMax.json(ES.mOption)

    def jsonInfoAutre(self, dcinf):
        dcinf[ES.obs_complet] = self.complet
        dcinf[ES.obs_score] = self.score
        if self.setResult != None :
            dcinf[ES.res_mRate] = self.setResult.measureRate
            dcinf[ES.res_dim] = self.setResult.dim
            dcinf[ES.res_axes] = self.setResult.axes

    def jsonInfo(self, types, nval, box, autre):
        dcinf = dict()
        if types :  self.jsonInfoTypes(dcinf)
        if nval :   self.jsonInfoNval(dcinf)
        if box :    self.jsonInfoBox(dcinf)
        if autre:   self.jsonInfoAutre(dcinf)
        ldel =[]
        for k,v in dcinf.items() :
            if type(v) == str and (v == "null" or v =='')   : ldel.append(k)
            if type(v) == list and v == ES.nullCoor         : ldel.append(k) 
        for k in ldel :         del dcinf[k]
        if len(dcinf) == 0 :    return ""
        else :                  return '"' +ES.information + '":' + json.dumps(dcinf)

    def nValueObs(self):
        nPrp = nDat = nLoc = nRes = 0
        if self.setResult   != None: nRes = self.setResult.nValue
        if self.setLocation != None: nLoc = self.setLocation.nValue
        if self.setDatation != None: nDat = self.setDatation.nValue
        if self.setProperty != None: nPrp = self.setProperty.nValue
        return [nPrp, nDat, nLoc, nRes]

    def iloc(self, idat, iloc, iprp):
        if not self.complet : return dict()
        dic = dict()
        if self.setDatation != None and idat < self.setDatation.nValue: 
            dic[ES.dat_classES] = self.setDatation.valueList[idat].json(self.option)
        if self.setLocation != None and iloc < self.setLocation.nValue: 
            dic[ES.loc_classES] = self.setLocation.valueList[iloc].json(self.option)
        if self.setProperty != None and iprp < self.setProperty.nValue: 
            dic[ES.prp_classES] = self.setProperty.valueList[iprp].json(self.option)
        if self.setResult != None : 
            for i in range(self.setResult.nValue) : 
                if self.setResult.valueList[i].ind == [idat, iloc, iprp] : 
                    dic[ES.res_classES] = self.setResult.valueList[i].json(self.option)
        return dic
    
    def typeObs(self):
        [nPrp, nDat, nLoc, nRes] = self.nValueObs()
        self.score = min(max(min(nPrp, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2), -1), 229);
        if self.setResult == None or (self.setResult.error or self.setResult.getMaxIndex() == -1 or \
           self.setResult.nInd[0] > nDat or self.setResult.nInd[1] > nLoc or self.setResult.nInd[2] > nPrp):
               self.mAtt[ES.type] = "obserror"
               return
        if self.score == 22  and self.setResult.dim == 2:	self.score = 23
        if self.score == 122 and self.setResult.dim == 2:	self.score = 123
        if self.score == 202 and self.setResult.dim == 2:	self.score = 203
        if self.score == 212 and self.setResult.dim == 2:	self.score = 213
        if self.score == 220 and self.setResult.dim == 2:	self.score = 223
        if self.score == 221 and self.setResult.dim == 2:	self.score = 224
        if self.score == 222 and self.setResult.dim == 3:	self.score = 228
        if self.score == 222 and self.setResult.dim == 2 and 2 in self.setResult.axes:	self.score = 225
        if self.score == 222 and self.setResult.dim == 2 and 1 in self.setResult.axes:	self.score = 226
        if self.score == 222 and self.setResult.dim == 2 and 0 in self.setResult.axes:	self.score = 227
        self.mAtt[ES.type] = ES.obsCat[self.score]

    @staticmethod
    def sortAlign(npInd, list1, ind1, ind2):
        return [npInd[list(npInd[:,ind1]).index(i),:][ind2]  for i in list1]    
        
    def sort(self, order = [0, 1, 2], cross = True, sort = [[], [], []]):  
        if self.setResult == None or not self.setResult.isIndex() : return
        tr = tri = [[], [], []]
        for i in range(3) : tri[i] = self.sortSet(i, sort[i], False)
        npInd = np.array(self.setResult.vListIndex)
        if cross:
            for ax in self.setResult.axes : 
                if ax > 100 : 
                    tri[order[1]] = self.sortAlign(npInd, tri[order[0]], order[0], order[1])
                    tri[order[2]] = self.sortAlign(npInd, tri[order[0]], order[0], order[2])
                elif ax > 9 :
                    (first, second) = (ax//10, ax%10)
                    if order.index(second) < order.index(first) : (first, second) = (second, first)
                    tri[second] = self.sortAlign(npInd, tri[first], first, second)
        for i in range(3) : tr[i] = self.sortSet(i, tri[i])
        for resVal in self.setResult.valueList :
            for i in range(3) : resVal.ind[i] = tr[i].index(resVal.ind[i])
        resTri = self.setResult.sort()
    
    def sortSet(self, ax, tri = [], update = True):
        if ax == 0 and self.setDatation != None : return self.setDatation.sort(tri, update)
        if ax == 1 and self.setLocation != None : return self.setLocation.sort(tri, update)
        if ax == 2 and self.setProperty != None : return self.setProperty.sort(tri, update)
        return [0]
    
    def majType(self, order = 'dlp'):
        [nprp, ndat, nloc, nRes] = self.nValueObs()
        nPrp = max(1, nprp)
        nDat = max(1, ndat)
        nLoc = max(1, nloc)
        if len(order) == 3 : 
            self.complet = nRes == nLoc * nDat * nPrp \
                        or nRes == nDat * nPrp == nDat * nLoc \
                        or nRes == nLoc * nPrp == nLoc * nDat \
                        or nRes == nPrp * nLoc == nPrp * nDat \
                        or nRes == nLoc == nDat == nPrp
        if len(order) == 2 : 
            self.complet = nRes == nDat * nPrp == nDat * nLoc \
                        or nRes == nLoc * nPrp == nLoc * nDat \
                        or nRes == nPrp * nLoc == nPrp * nDat \
                        or nRes == nLoc == nDat == nPrp
        if len(order) == 1 : 
            self.complet = nRes == nLoc == nDat == nPrp
        
        if self.complet: self.setResult.majIndex(nRes, nPrp, nDat, nLoc, order)
        if self.setResult   != None: self.setResult.  analyse()
        if self.setLocation != None: self.setLocation.analyse()
        if self.setDatation != None: self.setDatation.analyse()
        self.typeObs()

    def xlist(self):
        xList = {}
        if self.setLocation != None: 
            xList['loc']    = self.setLocation.to_numpy()
            xList['locstr'] = self.setLocation.to_numpy(func = LocationValue.json)
            xList['loclon'] = self.setLocation.to_numpy(func = LocationValue.vPointX)
            xList['loclat'] = self.setLocation.to_numpy(func = LocationValue.vPointY)
            xList['locnam'] = self.setLocation.to_numpy(func = LocationValue.vName)
            xList['locran'] = np.arange(len(xList['loc']))
        if self.setDatation != None: 
            xList['dat']    = self.setDatation.to_numpy()
            xList['datstr'] = self.setDatation.to_numpy(func = DatationValue.json)
            xList['datnam'] = self.setDatation.to_numpy(func = DatationValue.vName)
            xList['datran'] = np.arange(len(xList['dat']))
        if self.setProperty != None: 
            xList['prp']    = self.setProperty.to_numpy()
            xList['prpstr'] = self.setProperty.to_numpy(func = PropertyValue.json)
            xList['prpnam'] = self.setProperty.to_numpy(func = PropertyValue.vName)
            xList['prpran'] = np.arange(len(xList['prp']))
        if self.setResult  != None: 
            xList['res']    = self.setResult.to_numpy()
            xList['resval'] = self.setResult.to_numpy(func = ResultValue.to_float)
            xList['resstr'] = self.setResult.to_numpy(func = ResultValue.json)
            xList['resnam'] = self.setResult.to_numpy(func = ResultValue.vName)
            xList['resran'] = np.arange(len(xList['res']))
        return xList

    def xAttrs(self) :
        attrs = ES.xattrs
        attrs['info']   = json.loads("{" + self.jsonInfo(True, False, True, False) + "}")["information"]
        return attrs

    def axeCoor(self, nValAxe) :
        for ax in self.setResult.axes :
            if ax > 100 : return ax
            if ax < 9 and nValAxe == ax : return ax
            elif ax > 9 and (nValAxe == ax//10 or nValAxe == ax%10) : return ax
        return None
    
    def xCoord(self, xList, attrs, dataArray, complet, numeric) :
        #nax = {'dat' : 0, 'loc' : 1, 'prp' : 2}
        coord = {}
        for key, val in xList.items() :
            if key[:3] != 'res' and self.axeCoor(ES.nax[key[:3]]) != None \
                and (complet or (not complet and len(key) == 3)):
                coord[key] = ([ES.axes[self.axeCoor(ES.nax[key[:3]])]], val, attrs[key[:3]])
                if key == 'loclon' : coord[key] = (coord[key][0], val, attrs['lon'])
                if key == 'loclat' : coord[key] = (coord[key][0], val, attrs['lat'])
        for ax in self.setResult.axes :
            if ax > 9 :
                le = len(xList[ES.axes[ax%10]])
                coord[ES.axes[ax]] = ([ES.axes[ax]], np.arange(le))
                if ax > 100 : lis = [str(xList['datstr'][i]) + xList['locstr'][i] + 
                                     xList['prpstr'][i] for i in range(le)]
                else : lis = [str(xList[ES.axes[ax%10]+'str'][i]) + 
                              str(xList[ES.axes[ax//10]+'str'][i]) for i in range(le)]
                coord[ES.axes[ax]+'str'] = ([ES.axes[ax]], lis)
        if numeric :
            if 'loc' in coord.keys() : coord['loc'] = (coord['loc'][0], xList['locran'], coord['loc'][2])
            if 'dat' in coord.keys() : coord['dat'] = (coord['dat'][0], xList['datstr'], coord['dat'][2])
            if 'prp' in coord.keys() : coord['prp'] = (coord['prp'][0], xList['prpran'], coord['prp'][2])
        return coord
    

    def to_xarray(self, dataArray = True, complet = False, info = False, numeric = False):
        if self.setResult.getMaxIndex() == -1 : return None
        self.sort()
        xList = self.xlist()
        attrs = self.xAttrs()
        coord = self.xCoord(xList, attrs, dataArray, complet, numeric = False)
        self.setResult.triAxe()
        dims = [ES.axes[ax] for ax in self.setResult.axes]
        if numeric  : xres = xList['resval']
        else        : xres = xList['res']
        if dataArray and info :
            return xr.DataArray(xres, coord, dims, attrs=attrs['info'])
        elif dataArray and not info :
            return xr.DataArray(xres, coord, dims)
        return None
    
    def plot(self, switch = False, method = 'line'):    
        if self.setResult.getMaxIndex() == -1 : return
        obx = self.to_xarray(numeric = True, complet=True)
        if len(obx.dims) == 2:
            order = (0,1)
            if switch : (order[0], order[1]) = (order[1], order[0])
            if method == 'line' :
                obx.plot.line(x=obx.dims[order[0]]+'str', hue=obx.dims[order[1]]+'str')
            elif method == 'pcolormesh' : 
                ext = ['', '']
                for i in (0,1):
                    if obx.dims[i] == 'dat' : ext[i] = 'str'
                    elif str(obx.coords[obx.dims[i]].dtype)[0] != 'i': ext[i] = 'ran'
                obx.plot(x=obx.dims[order[0]]+ext[order[0]], y=obx.dims[order[1]]+ext[order[1]])
            #τobg = self.to_geoDataFrame()
            #for i in range(len(self.setProperty)): obg.plot(obg.columns.array[i], legend=True)
        elif self.setResult.dim == 3:
            obx = self.to_xarray().set_index(prop = "prpstr")
            obx.sortby(["dat", "loc", "prp"]).plot(x="dat", y="loc", col="prp", col_wrap=2, size=5)
            obx.sortby(["dat", "loc", "prp"]).plot.line(    x="dat", col="prp", col_wrap=2, size=5)
            obg = self.to_geoDataFrame()
            for i in range(len(self.setProperty)): obg.plot(obg.columns.array[i], legend=True)
            plt.legend(obx.coords['loc'].to_index().to_list())
        plt.show()    

    def to_dataFrame(self):
        if self.setResult.dim > 0 : return self.to_xarray(False).to_dataframe()
        else : return None

    '''def majType(self, order = 'dlp'):
        [nprp, ndat, nloc, nEch, nRes] = self.nValueObs()
        nPrp = max(1, nprp)
        nDat = max(1, ndat)
        nLoc = max(1, nloc)
        self.complet = (len(order) == 3 and  nRes == nLoc * nDat * nPrp) \
                        or nRes == nDat * nPrp == nDat * nLoc \
                        or nRes == nLoc * nPrp == nLoc * nDat \
                        or nRes == nPrp * nLoc == nPrp * nDat \
                        or nRes == nLoc == nDat == nPrp \
                        or nRes == 1
        if self.complet: self.setResult.majIndex(nRes, nPrp, nDat, nLoc, order)
        if self.setResult   != None: self.setResult.analyse()
        if self.setLocation != None: self.setLocation.analyse()
        if self.setDatation != None: self.setDatation.analyse()
        self.typeObs()'''

    '''def to_geoDataFrame(self):
        if self.setResult.dim > 0 : return gp.GeoDataFrame(self.to_dataFrame())
        else : return None'''

    def choropleth(self):
        if self.setResult.dim == 1 or self.setResult.dim // 10 == 1:
            m = folium.Map(location=self.setLocation.valueList[0].coorInv, zoom_start=6)
            folium.PolyLine(
                list(self.setLocation.valueList[i].coorInv for i in range(len(self.setLocation.valueList)))
            ).add_to(m)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name="test choropleth",
                data=self.to_dataFrame(),
                key_on="feature.id",
                #columns=["point", json.loads(self.setProperty[0].json(False))[ES.prp_propType]],
                columns=["point", json.loads(self.setProperty[0].json(ES.mOption))[ES.prp_propType]],
                fill_color="BuGn",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="test choropleth"
            ).add_to(m)
            folium.LayerControl().add_to(m)
            return m
        return None

    '''def typeObs(self):
        [nPrp, nDat, nLoc, nEch, nRes] = self.nValueObs()
        self.score = min(max(min(nEch, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2), -1), 223);
        if self.setResult != None and (self.setResult.error or self.setResult.getMaxIndex() == -1 or \
           self.setResult.nd > nDat or self.setResult.nl > nLoc or self.setResult.np > nPrp):
               self.mAtt[ES.type] = "obserror"
               return
        self.mAtt[ES.type] = ES.obsCat[self.score]
        if self.score == 222 and self.setResult.dim == 1:	self.mAtt[ES.type] = "obsPath"
        if self.score == 222 and self.setResult.dim == 2:	self.mAtt[ES.type] = "obsAreaSequence"'''

    '''def tri2(self) :
        tup = [((self.setDatation.valueList[i], i)) for i in range(self.setDatation.nValue)]
        self.setDatation.iSort = [ v[1] for v in sorted(tup, key=lambda l: l[0])]
        tup = [((self.setLocation.valueList[i], i)) for i in range(self.setLocation.nValue)]
        self.setLocation.iSort = [ v[1] for v in sorted(tup, key=lambda l: l[0])]
        tup = [((self.setProperty.valueList[i], i)) for i in range(self.setProperty.nValue)]
        self.setProperty.iSort = [ v[1] for v in sorted(tup, key=lambda l: l[0])]
        tup = [(([self.setDatation.iSort[self.setResult.valueList[i].ind[0]],
                  self.setLocation.iSort[self.setResult.valueList[i].ind[1]],
                  self.setProperty.iSort[self.setResult.valueList[i].ind[2]]]
                  , i)) for i in range(self.setResult.nValue)]
        #tup = [((self.setResult.valueList[i], i)) for i in range(self.setResult.nValue)]
        self.setResult.iSort = [ v[1] for v in sorted(tup, key=lambda l: l[0])]'''

    '''def nValueObs(self):
        nPrp = nDat = nLoc = nEch = nRes = 0
        if self.setResult   != None: nEch = self.setResult.nEch
        if self.setResult   != None: nRes = self.setResult.nValue
        if self.setLocation != None: nLoc = self.setLocation.nValue
        if self.setDatation != None: nDat = self.setDatation.nValue
        if self.setProperty != None: nPrp = self.setProperty.nValue
        return [nPrp, nDat, nLoc, nEch, nRes]'''
    
    '''for ax in self.axes :
            coord[ES.axes[ax]]=([ES.axes[ax]], )
        
        
        [nPrp, nDat, nLoc, nRes] = self.nValueObs()
        nDatLoc = max(nDat, nLoc)
        coord = {}
        coord["prp"]            = (["prp"], xList['prp']        , attrs['prp'])
        coord["prpstr"]         = (["prp"], xList['prpstr']     , attrs['prp'])
        if self.setResult.dim == 1: 
            coord["datloc"]      = (["datloc"], np.arange(nDatLoc))
            coord["point"]      = (["datloc"], np.arange(nDatLoc))
            #coord["datloc"]     = (["datloc"], xList['datlocstr'], attrs['datloc'])
            if nLoc == nDatLoc:
                coord["lon"]    = (["datloc"], xList['lon']     , attrs['lon'])
                coord["lat"]    = (["datloc"], xList['lat']     , attrs['lat'])
                coord["geometry"] = (["datloc"], xList['loc']   , attrs['loc'])
                coord["locstr"] = (["datloc"], xList['locstr']  , attrs['loc'])
            if nDat == nDatLoc:
                coord["dat"]    = (["datloc"], xList['dat']     , attrs['dat'])
                #coord["datstr"] = (["datloc"], xList['datstr']  , attrs['dat'])
            if dataArray:
                ranking = np.arange(nDatLoc * nPrp).reshape(nDatLoc, nPrp)
                coord["ranking"] = (["datloc", "prp"]           , ranking)
            else :
                ranking = np.arange(nDatLoc)
                coord["ranking"] = (["datloc"], ranking)
                coord.pop('prp')
                coord.pop('prpstr')
        else : 
            coord["geometry"]   = (["loc"], xList['loc']    , attrs['loc'])
            coord["loc"]        = (["loc"], np.arange(nLoc))
            coord["lon"]        = (["loc"], xList['lon']    , attrs['lon'])
            coord["lat"]        = (["loc"], xList['lat']    , attrs['lat'])
            coord["locstr"]     = (["loc"], xList['locstr'] , attrs['loc'])
            coord["dat"]        = (["dat"], xList['dat']    , attrs['dat'])
            coord["datstr"]     = (["dat"], xList['datstr'] , attrs['dat'])
            if dataArray :
                ranking = np.arange(nDat * nLoc * nPrp).reshape(nDat, nLoc, nPrp)
                coord["ranking"] = (["dat", "loc", "prp"]   , ranking)
            else :
                ranking = np.arange(nDat * nLoc).reshape(nDat, nLoc)
                coord["ranking"] = (["dat", "loc"], ranking)
                coord.pop('prp')
                coord.pop('prpstr')
        return coord'''

    '''
        [nPrp, nDat, nLoc, nRes] = self.nValueObs()
        xList['loc'] = xList['dat'] = xList['prp'] = xList['res'] = list()
        xList['res']    = self.setResult.valueList
        if self.setLocation != None: xList['loc'] = [val.shap for val in self.setLocation.valueList]
        #if self.setLocation != None: xList['loc'] = self.setLocation.vListPoint
        #if self.setDatation != None: xList['dat'] = [val.instant for val in self.setDatation.valueList]
        if self.setDatation != None: xList['dat'] = self.setDatation.vListInstant
        if self.setProperty != None: xList['prp'] = self.setProperty.valueList
        xList['lon']    = [geo.centroid.x for geo in xList['loc']]
        xList['lat']    = [geo.centroid.y for geo in xList['loc']]
        #xList['lon']    = [geo[0] for geo in xList['loc']]
        #xList['lat']    = [geo[1] for geo in xList['loc']]
        xList['locstr'] = [json.dumps(geo.shap.__geo_interface__) for geo in self.setLocation.valueList]
        #xList['datstr'] = [dat.isoformat() for dat in xList['dat']]
        #if xList['datstr'] == []: xList['datlocstr'] = xList['locstr']
        #elif xList['locstr'] == []: xList['datlocstr'] = xList['datstr']
        #else : xList['datlocstr'] = [xList['datstr'][min(i, nDat-1)] + xList['locstr'][min(i, nLoc-1)] 
                                     #for i in range(max(nDat, nLoc))]
        xList['prpstr'] = [pr.json(ES.mOption) for pr in xList['prp']]
        xList['resvalue'] = [res.value for res in xList['res']]
        '''    

    '''def xCoord2(self, xList, attrs, dataArray) :
        [nPrp, nDat, nLoc, nRes] = self.nValueObs()
        nDatLoc = max(nDat, nLoc)
        coord = {}
        coord["prp"]            = (["prp"], xList['prp']        , attrs['prp'])
        coord["prpstr"]         = (["prp"], xList['prpstr']     , attrs['prp'])
        if self.setResult.dim == 1: 
            coord["datloc"]      = (["datloc"], np.arange(nDatLoc))
            coord["point"]      = (["datloc"], np.arange(nDatLoc))
            #coord["datloc"]     = (["datloc"], xList['datlocstr'], attrs['datloc'])
            if nLoc == nDatLoc:
                coord["lon"]    = (["datloc"], xList['lon']     , attrs['lon'])
                coord["lat"]    = (["datloc"], xList['lat']     , attrs['lat'])
                coord["geometry"] = (["datloc"], xList['loc']   , attrs['loc'])
                coord["locstr"] = (["datloc"], xList['locstr']  , attrs['loc'])
            if nDat == nDatLoc:
                coord["dat"]    = (["datloc"], xList['dat']     , attrs['dat'])
                #coord["datstr"] = (["datloc"], xList['datstr']  , attrs['dat'])
            if dataArray:
                ranking = np.arange(nDatLoc * nPrp).reshape(nDatLoc, nPrp)
                coord["ranking"] = (["datloc", "prp"]           , ranking)
            else :
                ranking = np.arange(nDatLoc)
                coord["ranking"] = (["datloc"], ranking)
                coord.pop('prp')
                coord.pop('prpstr')
        else : 
            coord["geometry"]   = (["loc"], xList['loc']    , attrs['loc'])
            coord["loc"]        = (["loc"], np.arange(nLoc))
            coord["lon"]        = (["loc"], xList['lon']    , attrs['lon'])
            coord["lat"]        = (["loc"], xList['lat']    , attrs['lat'])
            coord["locstr"]     = (["loc"], xList['locstr'] , attrs['loc'])
            coord["dat"]        = (["dat"], xList['dat']    , attrs['dat'])
            coord["datstr"]     = (["dat"], xList['datstr'] , attrs['dat'])
            if dataArray :
                ranking = np.arange(nDat * nLoc * nPrp).reshape(nDat, nLoc, nPrp)
                coord["ranking"] = (["dat", "loc", "prp"]   , ranking)
            else :
                ranking = np.arange(nDat * nLoc).reshape(nDat, nLoc)
                coord["ranking"] = (["dat", "loc"], ranking)
                coord.pop('prp')
                coord.pop('prpstr')
        return coord'''
    
        
        
    '''if self.setResult == None: return None
        xList = self.xlist()
        [nPrp, nDat, nLoc, nRes] = self.nValueObs()
        nDatLoc = max(nDat, nLoc)
        attrs = self.xAttrs()
        coord = self.xCoord(xList, attrs, dataArray)
        
        if self.setResult.dim == 1 :
            value = np.array(xList['resvalue']).reshape(nDatLoc, nPrp)
            if dataArray :
                return xr.DataArray(data=value, dims=["datloc", "prp"],
                                    coords=coord, attrs=attrs['info'])
            else :
                datas ={}
                for i in range(nPrp):
                    prp = json.loads(xList['prp'][i].json(ES.mOption))
                    datas[prp[ES.prp_propType]] = (["datloc"], value[:,i])
                return xr.Dataset(data_vars=datas, coords=coord, attrs=attrs['info'])
        elif self.setResult.dim == 2 :
            value = np.array(xList['resvalue']).reshape(nDat, nLoc, nPrp)
            if dataArray :
                return xr.DataArray(data=value, dims=["dat", "loc", "prp"],
                                    coords=coord, attrs=attrs['info'])    
            else :
                datas ={}
                for i in range(nPrp):
                    prp = json.loads(xList['prp'][i].json(ES.mOption))
                    datas[prp[ES.prp_propType]] = (["dat","loc"], value[:,:,i], 
                                                  {"units": prp["unit"]})
                return xr.Dataset(data_vars = datas, coords =  coord, attrs =  attrs['info'])
        else : return None'''
