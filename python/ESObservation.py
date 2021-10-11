# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:40:06 2021

@author: a179227
"""
from ESObs import ESSetDatation, ESSetLocation, ESSetProperty, ESSetResult
from ESElement import ESObject, isESObs, isESAtt
from ESconstante import ES
from ESComponent import LocationValue, TimeValue, PropertyValue, \
    ResultValue, gshape
from shapely.geometry import shape
import json, folium
import numpy as np
import xarray as xr
import geopandas as gp
import matplotlib.pyplot as plt

class Observation(ESObject):
    """
    Classe liée à la structure interne
    """
    def __init__(self, jsontxt = ""):
        ESObject.__init__(self)
        self.option = ES.mOption.copy()
        self.score = -1
        self.complet = False
        self.mAtt[ES.obs_resultTime] = "null"
        self.classES = ES.obs_classES
        self.typeES = ES.obs_typeES
        self.mAtt[ES.type] = "obsError"
        self.mAtt[ES.obs_id] = "null"
        try:
            js=json.loads(jsontxt)
        except:
            return
        if type(js) != dict: return
        if ES.type not in list(js) or js[ES.type] != ES.obs_classES: return
        if ES.obs_id in list(js): self.mAtt[ES.obs_id] = js[ES.obs_id]
        if ES.obs_attributes in list(js): 
            if type(js[ES.obs_attributes]) == dict: js = js[ES.obs_attributes]
            else: return
        for k, v in js.items():
            if isESAtt(ES.obs_classES, k) or k[0] == '$': self.mAtt[k] = v
            if k == ES.parameter: 
                try:  self.parameter = json.dumps(v)
                except:  self.parameter = "null"
        if isESObs(ES.dat_classES, js): ESSetDatation(self, js)
        if isESObs(ES.loc_classES, js): ESSetLocation(self, js)
        if isESObs(ES.prp_classES, js): ESSetProperty(self, js)
        if isESObs(ES.res_classES, js): ESSetResult  (self, js)
        self.majType()

    @property
    def bounds(self):
        if self.setLocation : return shape(self).bounds
        else : return None

    @property
    def __geo_interface__(self):
        if self.setLocation : 
            return gshape(json.dumps(json.loads('{' \
                        + self.setLocation.json(False, False, False, False)\
                        + '}')["coordinates"])).__geo_interface__
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
                self.addValue(resv)
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
        
    def addValue(self, esValue):
        if type(esValue)== PropertyValue:
            if self.element(ES.prp_valueType) == None: 
                esSet = ESSetProperty(self)
            return self.element(ES.prp_valueType).addValue(PropertyValue, esValue)
        if type(esValue)== LocationValue:
            if self.element(ES.loc_valueType) == None: 
                esSet = ESSetLocation(self)
            return self.element(ES.loc_valueType).addValue(LocationValue, esValue)
        if type(esValue)== TimeValue:
            if self.element(ES.dat_valueType) == None: 
                esSet = ESSetDatation(self)
            return self.element(ES.dat_valueType).addValue(TimeValue, esValue)
        if type(esValue)== ResultValue:
            if self.element(ES.res_valueType) == None: 
                esSet = ESSetResult(self)
            return self.element(ES.res_valueType).addValue(ResultValue, esValue)
        else: return 0

    def addValueObservation(self, val, idat, iloc, iprop):
        return self.addValue(ResultValue(val, [idat, iloc, iprop]))

    def addValueSensor(self, val, tim, coor, nprop):
        return self.addValueObservation(val, self.addValue(tim), self.addValue(coor), nprop)

    def json(self): 
        if self.option["json_elt_type"]: option_type = 1
        else: option_type = 0
        js =""
        if self.option["json_obs_val"]: js = "{"
        js += '"' + ES.type +'":"' + ES.obs_classES +'",'
        if self.mAtt[ES.obs_id] != "null": js += '"' + ES.obs_id + '":"' + self.mAtt[ES.obs_id] + '",'
        if self.option["json_obs_attrib"]: js += '"' + ES.obs_attributes + '":{'
        js += self.jsonAtt(option_type)
        for cp in self.pComposant:
            js += cp.json(self.option["json_ESobs_class"], self.option["json_elt_type"], self.option["json_res_index"])
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
        if self.setLocation != None :
            dcinf[ES.json_nval_loc] = self.setLocation.nValue
        if self.setDatation != None :
            dcinf[ES.json_nval_dat] = self.setDatation.nValue
        if self.setProperty != None :
            dcinf[ES.json_nval_prp] = self.setProperty.nValue
        if self.setResult != None :
            dcinf[ES.json_nval_res] = self.setResult.nValue

    def jsonInfoBox(self, dcinf):
        if self.setLocation != None :
            dcinf[ES.loc_boxMin] = self.setLocation.boxMin.coor
            dcinf[ES.loc_boxMax] = self.setLocation.boxMax.coor
        if self.setDatation != None :
            dcinf[ES.dat_boxMin] = self.setDatation.boxMin.json(True)
            dcinf[ES.dat_boxMax] = self.setDatation.boxMax.json(True)

    def jsonInfoAutre(self, dcinf):
        dcinf[ES.obs_complet] = self.complet
        dcinf[ES.obs_score] = self.score
        if self.setResult != None :
            dcinf[ES.res_mRate] = self.setResult.measureRate
            dcinf[ES.res_sRate] = self.setResult.samplingRate
            dcinf[ES.res_dim] = self.setResult.dim
            dcinf[ES.res_nEch] = self.setResult.nEch

    def jsonInfo(self, types, nval, box, autre):
        dcinf = dict()
        if types : self.jsonInfoTypes(dcinf)
        if nval : self.jsonInfoNval(dcinf)
        if box : self.jsonInfoBox(dcinf)
        if autre: self.jsonInfoAutre(dcinf)
        ldel =[]
        for k,v in dcinf.items() :
            if type(v) == str and (v == "null" or v ==''): ldel.append(k)
            if type(v) == list and v == [-1, -1]: ldel.append(k) 
        for k in ldel : del dcinf[k]
        if len(dcinf) == 0 : return ""
        else : return '"' +ES.information + '":' + json.dumps(dcinf)

    def nValueObs(self):
        nPrp = nDat = nLoc = nEch = nRes = 0
        if self.setResult   != None: nEch = self.setResult.nEch
        if self.setResult   != None: nRes = self.setResult.nValue
        if self.setLocation != None: nLoc = self.setLocation.nValue
        if self.setDatation != None: nDat = self.setDatation.nValue
        if self.setProperty != None: nPrp = self.setProperty.nValue
        return [nPrp, nDat, nLoc, nEch, nRes]
    
    def typeObs(self):
        [nPrp, nDat, nLoc, nEch, nRes] = self.nValueObs()
        self.score = min(max(min(nEch, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2), -1), 223);
        if self.setResult != None and (self.setResult.error or self.setResult.getMaxIndex() == -1 or \
           self.setResult.nd > nDat or self.setResult.nl > nLoc or self.setResult.np > nPrp):
               self.mAtt[ES.type] = "obserror"
               return
        self.mAtt[ES.type] = ES.obsCat[self.score]
        if self.score == 222 and self.setResult.dim == 1:	self.mAtt[ES.type] = "obsPath"
        if self.score == 222 and self.setResult.dim == 2:	self.mAtt[ES.type] = "obsAreaSequence"
    
    def majType(self):
        [nprp, ndat, nloc, nEch, nRes] = self.nValueObs()
        nPrp = max(1, nprp)
        nDat = max(1, ndat)
        nLoc = max(1, nloc)
        self.complet = nRes > 0 and ( nRes == nLoc * nDat * nPrp or \
                                     (nRes == nDat * nPrp and nRes == nLoc * nPrp))
        if self.complet: self.setResult.majIndex(nRes, nPrp, nDat, nLoc)
        if self.setResult   != None: self.setResult.analyse()
        if self.setLocation != None: self.setLocation.analyse()
        if self.setDatation != None: self.setDatation.analyse()
        self.typeObs()

    def to_xarray(self, dataArray = True):
        if self.setResult == None: return None
        geoList = datList = prpList = resList = list()
        nLoc = nDat = nPrp = 0
        resList = self.setResult.valueList
        if self.setLocation != None: 
            geoList = [val.shap for val in self.setLocation.valueList]
            nLoc = self.setLocation.nValue
        if self.setDatation != None: 
            datList = [val.dtVal for val in self.setDatation.valueList]
            nDat = self.setDatation.nValue
        if self.setProperty != None:
            prpList = self.setProperty.valueList
            nPrp = self.setProperty.nValue
        nDatLoc = max(nDat, nLoc)
        lon = [geo.centroid.x for geo in geoList]
        lat = [geo.centroid.y for geo in geoList]
        geostr = [json.dumps(geo.__geo_interface__) for geo in geoList]
        datstr = [dat.isoformat() for dat in datList]
        if datstr == []: datgeostr = geostr
        elif geostr == []: datgeostr = datstr
        else : datgeostr = [datstr[min(i, nDat-1)] + geostr[min(i, nLoc-1)] for i in range(nDatLoc)]
        propstr = [pr.json(False) for pr in prpList]
        resvalue = [res.value for res in resList]
        attrslon = {"units":"degrees", "standard_name":"longitude"}
        attrslat = {"units":"degrees", "standard_name":"latitude"}
        attrslatlon = {"units":"lat, lon", "standard_name":"latitude - longitude"}
        attrstime = {"standard_name":"horodatage"}
        attrsprop = {"standard_name":"property"}
        attrstimeloc = {"standard_name":"Time - latitude - longitude"}
        attrsinfo = json.loads("{" + self.jsonInfo(True, False, True, False) + "}")["information"]
    
        coord={"prop"   : (["prop"], prpList,attrsprop),
               "propstr": (["prop"], propstr, attrsprop)}
        if self.setResult.dim == 1: 
            value = np.array(resvalue).reshape(nDatLoc, nPrp)
            point = np.arange(nDatLoc)
            coord["point"] = (["timeloc"], point)
            coord["timeloc"] = (["timeloc"], datgeostr, attrstimeloc)
            if nLoc == nDatLoc:
                coord["lon"] = (["timeloc"], lon, attrslon)
                coord["lat"] = (["timeloc"], lat, attrslat)
                coord["geometry"] = (["timeloc"], geoList, attrslatlon)
                coord["locstr"] = (["timeloc"], geostr, attrslatlon)
            if nDat == nDatLoc:
                coord["time"] = (["timeloc"], datList, attrstime)
                coord["timestr"] = (["timeloc"], datstr, attrstime)
        else : 
            value = np.array(resvalue).reshape(nDat, nLoc, nPrp)
            point = np.arange(nLoc)
            coord["geometry"] = (["loc"], geoList, attrslatlon)
            coord["loc"] = (["loc"], point)
            coord["lon"] = (["loc"], lon, attrslon)
            coord["lat"] = (["loc"], lat, attrslat)
            coord["locstr"] =  (["loc"],geostr, attrslatlon)
            coord["time"] = (["time"], datList, attrstime)
            coord["timestr"] = (["time"], datstr, attrstime)
        
        if dataArray and self.setResult.dim == 1 :
            ranking = np.arange(nDatLoc * nPrp).reshape(nDatLoc, nPrp)
            coord["ranking"] = (["timeloc", "prop"], ranking)
            return xr.DataArray(data = value, dims = ["timeloc", "prop"],
                               coords = coord, attrs = attrsinfo)        
        elif dataArray and self.setResult.dim == 2 :
            ranking = np.arange(nDat * nLoc * nPrp).reshape(nDat, nLoc, nPrp)
            coord["ranking"] = (["time", "loc", "prop"], ranking)
            return xr.DataArray(data = value, dims = ["time", "loc", "prop"],
                               coords= coord, attrs = attrsinfo)    
        elif not dataArray and self.setResult.dim == 1 :
            ranking = np.arange(nDatLoc)
            coord["ranking"] = (["timeloc"], ranking)
            coord.pop('prop')
            coord.pop('propstr')
            datas ={}
            for i in range(nPrp):
                prp = json.loads(prpList[i].json(True))
                datas[prp[ES.prp_propType]] = (["timeloc"], value[:,i])
            return xr.Dataset(data_vars = datas, coords = coord, attrs = attrsinfo)
        elif not dataArray and self.setResult.dim == 2 :
            ranking = np.arange(nDat * nLoc).reshape(nDat, nLoc)
            coord["ranking"] = (["time", "loc"], ranking)
            coord.pop('prop')
            coord.pop('propstr')
            datas ={}
            for i in range(nPrp):
                prp = json.loads(prpList[i].json(True))
                datas[prp[ES.prp_propType]] = (["time","loc"], value[:,:,i], 
                                              {"units": prp["unit"]})
            return xr.Dataset(data_vars = datas, coords =  coord, attrs =  attrsinfo)
        else : return None
    
    def plot(self):    
        if self.setResult.dim == 1 :
            obx = self.to_xarray().set_index(timeloc="point", prop = "propstr")
            if 'time' in obx.coords: obx.sortby(['time']).plot.line(x = 'time')
            else : obx.plot.line(x='point')
            obg = self.to_geoDataFrame()
            for i in range(len(self.setProperty)): obg.plot(obg.columns.array[i], legend=True)
        elif self.setResult.dim == 2:
            obx = self.to_xarray().set_index(prop = "propstr")
            obx.sortby(["time","loc", "prop"]).plot(x="time", y="loc", col="prop", col_wrap=2, size=5)
            obx.sortby(["time","loc", "prop"]).plot.line(x="time", col="prop", col_wrap=2, 
                           size=5)
            obg = self.to_geoDataFrame()
            for i in range(len(self.setProperty)): obg.plot(obg.columns.array[i], legend=True)
            plt.legend(obx.coords['loc'].to_index().to_list())
        plt.show()    

    def to_dataFrame(self):
        if self.setResult.dim > 0 : return self.to_xarray(False).to_dataframe()
        else : return None

    def to_geoDataFrame(self):
        if self.setResult.dim > 0 : return gp.GeoDataFrame(self.to_dataFrame())
        else : return None

    def choropleth(self):
        if self.setResult.dim == 1:
            m = folium.Map(location=self.setLocation.valueList[0].coorInv, zoom_start=6)
            folium.PolyLine(
                list(self.setLocation.valueList[i].coorInv for i in range(len(self.setLocation.valueList)))
            ).add_to(m)
            folium.Choropleth(
                geo_data=self.jsonFeature,
                name="test choropleth",
                data=self.to_dataFrame(),
                key_on="feature.id",
                columns=["point", json.loads(self.setProperty[0].json(False))[ES.prp_propType]],
                fill_color="BuGn",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="test choropleth"
            ).add_to(m)
            folium.LayerControl().add_to(m)
            return m
        return None

    '''def majTypeObs(self, nRes, nMeas, nDat, nLoc, nEch, dim):
        self.score = min(nEch, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2);
        self.mAtt[ES.type] = ES.obsCat[self.score]
        #self.mAtt[ES.obs_score] = self.score
        #if nRes * nMeas * nDat * nLoc < 1: return
        if self.score == 22 and dim == 1:	self.mAtt[ES.type] = "trackPath"
        if self.score == 22 and dim == 2:	self.mAtt[ES.type] = "timeZone"
        if self.score == 122 and dim == 1:	self.mAtt[ES.type] = "measAreaSequence"
        if self.score == 122 and dim == 2:	self.mAtt[ES.type] = "obsMeanPath"
        if self.score == 222 and dim == 1:	self.mAtt[ES.type] = "obsPath"
        if self.score == 222 and dim == 2:	self.mAtt[ES.type] = "obsAreaSequence"
        if self.setResult != None: 
            if (self.setResult.getMaxIndex() == -1 and \
               (((self.score == 202 or self.score == 212) and nRes != nDat * nMeas) or \
               ((self.score == 220 or self.score == 221) and nRes != nLoc * nMeas) or \
                (self.score == 222 and (nRes != nLoc * nMeas or nRes != nDat * nMeas) and \
                 nRes != nLoc * nDat * nMeas))): 
                self.mAtt[ES.type] = "obserror"
            self.setResult.dim = dim
            self.setResult.nEch = nEch'''

            
    '''def majType(self):
        self.majType2()
        return
        nMeas = nDat = nRes = nLoc = nEch = dim = nLocU = nDatU = 0
        indexe = False
        indic = [0, 0, 0, 0]
        for p in self.pComposant :
            if    p.classES == ES.prp_classES : nMeas = p.nValue
            elif  p.classES == ES.dat_classES : 
                nDat = p.nValue
                maxi = p.maxiBox()
                mini = p.miniBox()
                p.setBox(maxi, mini)
            elif  p.classES == ES.loc_classES : 
                nLoc = p.nValue
                maxi = p.maxiBox()
                mini = p.miniBox()
                p.setBox(maxi, mini)
            elif  p.classES == ES.res_classES : 
                nRes = p.nValue
                indexe = p.getMaxIndex() > -1
                if indexe:
                    indic = p.indicateur()
                    p.majIndic(indic[0], indic[1], indic[2], indic[3])
                    nEch = indic[0]; nDatU = indic[2]; nLocU = indic[3]; dim = indic[1]
        if not indexe:
            nEch = nRes / max(1, nMeas)
            sco = min(nEch, 2) * 100 + min(nLoc, 2) * 10 + min(nDat, 2)
            dim = 1
            if nEch < 2 and nLoc < 2 and nDat < 2: dim = 0
            if (sco == 22 or sco == 122) and nLoc != nDat: dim = 2
            if sco == 222 and nRes == nLoc * nDat * nMeas: dim = 2
            self.complet = sco  < 202 or sco == 210 or sco == 211 or \
                    ((sco == 202 or sco == 212) and nRes == nDat * nMeas) or \
                    ((sco == 220 or sco == 221) and nRes == nLoc * nMeas) or \
                     (sco == 222 and ((nRes == nLoc * nMeas and nLoc == nDat) or nRes == nLoc * nDat * nMeas))
            self.tMeas = 1; self.tEch = 1
            if (((sco == 202 or sco == 212) and nRes != nDat * nMeas) or \
                ((sco == 220 or sco == 221) and nRes != nLoc * nMeas) or \
                 (sco == 222 and (nRes != nLoc  * nMeas or nLoc != nDat) and nRes != nLoc * nDat * nMeas)):
                self.tMeas = 0; self.tEch = 0; dim = 0; self.complet = False
            self.majTypeObs(nRes, nMeas, nDat, nLoc, nEch, dim);
        else:
            self.complet = (nRes == nMeas * nLoc * nDat and dim == 2 and nEch == nLoc * nDat) or \
    			(nRes == nMeas * nLoc and nLoc == nDat and dim == 1 and nEch == nLoc) or \
    			(nRes * nMeas * nLoc * nDat > 0 and dim == 0 and nEch == 1)
            if nEch * nMeas > 0: self.tMeas = nRes / (nEch * nMeas)
            if self.complet: self.tMeas = 1.0
            if dim == 2 and nDat * nLoc > 0: self.tEch = nEch / (nDat * nLoc)
            if dim <  2 and max(nDat, nLoc) > 0: self.tEch = nEch / max(nDat, nLoc)
            if self.complet: self.tEch = 1.0
            self.majTypeObs(nRes, nMeas, min(nDatU, nDat), min(nLocU, nLoc), nEch, dim)
        if self.option["maj_index"] and self.setResult != None : 
            self.setResult.majIndexRes(nRes, nMeas, nDat, nLoc, nEch, dim)
        if self.option["maj_reset_index"] and self.complet : 
            self.setResult.resetIndexRes()'''

    '''def addIndexSensor(self, tim, coor, nprop):
        idat = 0; iloc = 1; iprop = 2
        indval = [-1, -1, -1]
        indval[iloc] = self.addValue(coor)
        indval[idat] = self.addValue(tim)
        indval[iprop] = nprop
        return indval'''

