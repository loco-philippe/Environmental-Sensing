# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 13:35:28 2021

@author: philippe@loco-labs.io

This module describes the constants and default values used in other modules.
"""
import datetime, math
from typing import Dict

def _classval():
    from ESValue import LocationValue, DatationValue, PropertyValue, \
        NamedValue, ExternValue
    from timeslot import TimeSlot
    from ESObservation import Observation
    from ilist import Ilist
    from iindex import Iindex
    import datetime
    return {ES.obs_clsName: Observation,
            ES.dat_clsName: DatationValue,
            ES.loc_clsName: LocationValue,
            ES.prp_clsName: PropertyValue,
            ES.ext_clsName: ExternValue,
            ES.nam_clsName: NamedValue,
            ES.ili_clsName: Ilist,
            ES.iin_clsName: Iindex,
            #ES.coo_clsName: coordinate,
            ES.tim_clsName: datetime.datetime,
            ES.slo_clsName: TimeSlot,
            ES.dat_classES: DatationValue,
            ES.loc_classES: LocationValue,
            ES.prp_classES: PropertyValue,
            ES.res_classES: NamedValue}

def _classESval():
    from ESValue import LocationValue, DatationValue, PropertyValue, \
        NamedValue, ExternValue
    return {ES.obs_clsName: ExternValue,
            ES.dat_clsName: DatationValue,
            ES.loc_clsName: LocationValue,
            ES.prp_clsName: PropertyValue,
            ES.ext_clsName: ExternValue,
            ES.nam_clsName: NamedValue,
            ES.ili_clsName: ExternValue,
            #ES.coo_clsName: coordinate,
            ES.tim_clsName: DatationValue,
            ES.slo_clsName: DatationValue,
            ES.dat_classES: DatationValue,
            ES.loc_classES: LocationValue,
            ES.prp_classES: PropertyValue,
            ES.res_classES : NamedValue}

class Es:
    ''' initialization of constant data. '''

    def _identity(self, x) : return x
    def _inv(self, mp)     : return {val:key for key,val in mp.items()}
    #def _inv(self, mp)     : return dict(zip(mp.values(), mp.keys()))
    def _invnum(self, mp)  : return dict(zip([k[0] for k in list(mp.values())], mp.keys()))

    def __init__(self, defnone=True):
        self._initName()
        self._initReferenceValue()
        self._initStruct()
        self._initByte()
        #'''Application initialization (boolean)'''
        self.debug = False
        self._initDefaultValue(defnone)

    def _initStruct(self) :
        #%% option initialization (dict)
        self.mOption : Dict = {
                      "untyped"             : True, # pas de type dans le json
                      "encoded"             : True, # sortie bson/json ou dict
                      "encode_format"       : 'json', # sortie bson ou json
                      "simpleval"           : False, #only value in json
                      "json_res_index"      : True, # affiche index
                      "json_prp_name"       : False, # affiche name ou property
                      "json_dat_name"       : False, # affiche name ou instant/slot
                      "json_loc_name"       : False, # affiche name ou instant/slot
                      "json_param"          : False, # ok
                      "json_info"           : False, # si True, ok pour tous les info_
                      "json_info_type"      : False,
                      "json_info_nval"      : False,
                      "json_info_box"       : False,
                      "json_info_other"     : False,
                      "unic_index"          : True,  # dans add
                      #"add_equal"           : "full",  # sinon "value ou "name" pour les comparaisons
                      "bytes_res_format"    : self.nullDict, # calculé à partir de propperty si "null"
                      "prp_dict"            : False, # si True, prp_type doit être dans ES.prop
                      "sort_order"          : 'dlp',
                      "codif"               : {}   #self.codeb sinon
                      }
        ''' Default options for `ES.ESObservation.Observation`'''

        #%% observation initialization (dict)
        self.vName: Dict = {  self.obs_classES  :   self.obs ,
                        self.dat_classES  :   self.dat ,
                        self.loc_classES  :   self.loc ,
                        self.res_classES  :   self.res ,
                        self.prp_classES  :   self.prp }
        '''name for json classES identification '''

        """self.mValObs: Dict = {self.loc_valName  : self.loc_classES  ,
                        self.dat_valName  : self.dat_classES  ,
                        self.prp_valName  : self.prp_classES  ,
                        self.res_valName  : self.res_classES  }
        '''assignment of ESValue name to ESObs objects '''"""

        self.json_type: list = [self.json_type_dat, self.json_type_loc, self.json_type_prp, self.json_type_res]
        '''ordered list for json_type '''

        self.json_nval: list = [self.json_nval_dat, self.json_nval_loc, self.json_nval_prp, self.json_nval_res]
        '''ordered list for json_type '''

        self.esObsClass: list = [self.dat_classES, self.loc_classES, self.prp_classES, self.res_classES]
        '''ordered list for classES '''

        """self.esObsId: dict = { self.dat_classES : 0, self.loc_classES : 1, self.prp_classES : 2, self.res_classES : 3}
        '''ordered dict value for classES '''  """

        self.mTypeAtt: Dict ={self.type            : self.obs_classES  ,
                        self.information     : self.nul_classES  ,
                        self.obs_resultTime  : self.obs_classES  ,
                        self.obs_reference   : self.obs_classES  ,
                        self.obs_id          : self.obs_classES  ,
                        "ResultQuality"      : self.res_classES  ,
                        self.prp_type        : self.prp_classES  ,
                        self.prp_unit		   : self.prp_classES  ,
                        self.prp_sampling	   : self.prp_classES  ,
                        self.prp_appli       : self.prp_classES  ,
                        self.prp_EMFId		   : self.prp_classES  ,
                        self.prp_sensorType	: self.prp_classES  ,
                        self.prp_upperValue	: self.prp_classES  ,
                        self.prp_lowerValue	: self.prp_classES  ,
                        self.prp_period	   : self.prp_classES  ,
                        self.prp_interval	   : self.prp_classES  ,
                        self.prp_uncertain   : self.prp_classES  ,
                        "EMFType "           : "ObservingEMF"  ,
                        "ResultNature "      : "ObservingEMF"  }
        ''' Assignment of attributes to ESObs objects '''

        self.obsCat: Dict = {
                            -1 :"obserror" ,
                            0 : 'config'  ,
                            1 : 'top'  ,
                            2 : 'sequence'  ,
                            10 : 'point'  ,
                            11 : 'track'  ,
                            12 : 'datTrack'  ,
                            20 : 'zoning'  ,
                            21 : 'datZoning'  ,
                            22 : 'path'  ,
                            23 : 'areaSequence'  ,
                            100 : 'property'  ,
                            101 : 'record'  ,
                            102 : 'DatRecord'  ,
                            110 : 'feature'  ,
                            111 : 'obs'  ,
                            112 : 'obsDat'  ,
                            120 : 'areaFeature'  ,
                            121 : 'obsLoc'  ,
                            122 : 'obsPath'  ,
                            123 : 'obsAreaSequence'  ,
                            200 : 'multiFeature'  ,
                            201 : 'datMultiFeature'  ,
                            202 : 'multiRecord'  ,
                            203 : 'multiFeatureSequence'  ,
                            210 : 'multiFeatureVariation'  ,
                            211 : 'obsFeature'  ,
                            212 : 'obsRecord'  ,
                            213 : 'obsGridRecord'  ,
                            220 : 'areaFeature'  ,
                            223 : 'multiAreaFeature'  ,
                            221 : 'obsAreaFeature'  ,
                            224 : 'multiObsAreaFeature'  ,
                            222 : 'obsPathFeature'  ,
                            225 : 'FeatureobsAreaSequence'  ,
                            226 : 'areaObsrecord'  ,
                            227 : 'histoObsareaFeature'  ,
                            228 : 'obsGrid'  ,
                            }
        ''' Default name for `ES.ESObservation.Observation.score` '''

        #%% Xarray initialization (dict)
        self.nax: Dict = {'dat' : 0, 'loc' : 1, 'prp' : 2,
                          'd'   : 0, 'l'   : 1, 'p'   : 2}
        '''Dictionnary for axis Number '''

        self.axes: Dict = {
            0  :  'dat',   # axes : [0,1,2], [0,21], [2, 10], [1, 20]
            1  :	'loc',   #        [0, 1],  [0, 2], [1, 2], [120]
            2  :	'prp',
            10 :	'datloc',
            20 :	'datprp',
            21 :	'locprp',
            120:	'datlocprp'}
        '''Dictionnary for Xarray axis name '''

        self.xattrs: Dict = {
            'lon' : {"units":"degrees",   "standard_name":"longitude"},
            'lat' : {"units":"degrees",   "standard_name":"latitude"},
            'loc' : {"units":"lon, lat",  "standard_name":"longitude - latitude"},
            'dat' : {                     "standard_name":"horodatage"},
            'prp' : {                     "standard_name":"property"}}
        '''Dictionnary for Xarray attrs informations '''

        #%% typevalue initialization (dict)        
        self.typeName: Dict = {
            self.obs_valName : self.obs_clsName,
            self.dat_valName : self.dat_clsName,
            self.loc_valName : self.loc_clsName,
            self.prp_valName : self.prp_clsName,
            self.ext_valName : self.ext_clsName,
            self.nam_valName : self.nam_clsName,
            self.ili_valName : self.ili_clsName,
            self.iin_valName : self.iin_clsName,
            self.slo_valName : self.slo_clsName,
            #self.coo_valName : self.coo_clsName,
            #self.tim_valName : self.tim_clsName,
            self.res_classES : self.ES_clsName,
            self.dat_classES : self.dat_clsName,
            self.loc_classES : self.loc_clsName,
            self.prp_classES : self.prp_clsName,
            }
        self.valname : Dict = dict(zip(list(self.typeName.values())[:10], 
                                       list(self.typeName.keys())[:10]))
        self.className : list = list(self.typeName.values())

        self.EStypeName: Dict = {
            self.dat_valName : self.dat_clsName,
            self.loc_valName : self.loc_clsName,
            self.prp_valName : self.prp_clsName,
            self.ext_valName : self.ext_clsName,
            self.nam_valName : self.nam_clsName,
            }
        self.ESvalName : Dict = self._inv(self.EStypeName)
        self.ESclassName : list = list(self.EStypeName.values())
        
        #%% reserved
        self.reserved: list = [
            self.json_nval_loc,
            self.json_nval_dat,
            self.json_nval_res,
            self.json_nval_prp,
            self.json_type_loc,
            self.json_type_obs,
            self.json_type_dat,
            self.json_type_res,
            self.json_type_prp,

            #self.parameter    ,
            self.param        ,
            self.information  ,
            self.type         ,
            self.multi        ,
            self.obs          ,
            self.dat          ,
            self.loc          ,
            self.prp          ,
            self.res          ,
            self.coordinates  ,
            self.index        ,
            self.idxref       ,
            self.order        ,

            self.nul_classES  ,
            self.obs_classES  ,
            self.dat_classES  ,
            self.loc_classES  ,
            self.prp_classES  ,
            self.res_classES  ,

            self.obs_attributes,
            self.obs_id       ,
            self.obs_resultTime,
            self.obs_complet   ,
            self.obs_reference ,
            self.obs_score     ,
            self.obs_order     ,
            self.obs_idxref    ,

            self.res_mRate     ,
            self.res_nEch      ,
            self.res_dim       ,
            self.res_axes      ,
            self.set_nValue    ,

            self.dat_box       ,
            self.loc_box       ,

            self.prp_type	   ,
            self.prp_unit		,
            self.prp_sampling	,
            self.prp_appli		,
            self.prp_EMFId		,
            self.prp_sensorType,
            self.prp_upperValue,
            self.prp_lowerValue,
            self.prp_period	   ,
            self.prp_interval	,
            self.prp_uncertain ,
            self.prp_name      ,

            self.dat_valName   ,
            self.loc_valName   ,
            self.prp_valName   ,
            self.res_valName   ]

    def _initByte(self) :
    #%% init byte
        ''' Byte initialization (code) '''

        self.codeb: Dict = {self.dat_classES  :   1 ,
                            self.loc_classES  :   2 ,
                            self.res_classES  :   4 ,
                            self.prp_classES  :   3 ,
                            self.res_value    :   5 ,
                            self.index        :   6 ,
                            self.variable     :   7}
        self.invcodeb: Dict = self._inv(self.codeb)
        ''' Code for bynary interface `ES.ESObservation.Observation.from_bytes` and
        `ES.ESObservation.Observation.to_bytes` '''
        self.codevalue: Dict = {'name': 1,
                                'value': 2,
                                'namemini':3,
                                'valuemini':4}
        self.invcodevalue: Dict = self._inv(self.codevalue)
        ''' Code for bynary interface `ES.ESObservation.Observation.from_bytes` and
        `ES.ESObservation.Observation.to_bytes` '''
        self.minivalue: list = [3,4]
        self.namevalue: list = [1,3]
        
        #  format : (code_ES, python format, lenght, dexp, bexp, unit)
        self.prop: Dict ={'utf-8'       : (2 ,  '', 0,  0, 0, self.nullDict),
                          'sfloat'      : (15, 'e', 2,  0, 0, self.nullDict),
                          'uint16'      : (3 , 'H', 2,  0, 0, self.nullDict),
                          'uint8'       : (7 , 'B', 1,  0, 0, self.nullDict),
                          'sint24'      : (13, 'l', 3,  0, 0, self.nullDict),
                          'uint24'      : (14, 'L', 3,  0, 0, self.nullDict),
                          'sint8'       : (6 , 'b', 1,  0, 0, self.nullDict),
                          'sint16'      : (8 , 'h', 4,  0, 0, self.nullDict),
                          'uint32'      : (4 , 'L', 4,  0, 0, self.nullDict),
                          'PM25'        : (21, 'e', 2,  1, 2, 'kg/m3'      ),
                          'PM10'        : (22, 'e', 2,  0, 0, 'kg/m3'      ),
                          'CO2'         : (23, 'H', 2,  0, 0, 'ppm'        ),
                          'temp'        : (24, 'h', 2, -2, 0, '°C'         ),
                          'Temp'        : (24, 'e', 2,  0, 0, '°C'         ),
                          self.nullDict : (0 , 'e', 2,  0, 0, self.nullDict)}
        self.invProp: Dict = self._invnum(self.prop)
        self.bytedict: Dict = {self.dat_classES : ['namemini', 'value'],
                               self.loc_classES : ['namemini', 'value'],
                               self.prp_classES : ['valuemini'        ],
                               self.res_classES : ['namemini', 'sfloat'],
                               self.variable    : ['namemini', 'value']}

        '''Dictionnary for property codification (BLE - Environnemental Sensing Service) '''

        self.sampling: Dict = { self.nullDict       : 0,
                               'instantaneous'      : 1,
                               'arithmetic mean'    : 2,
                               'RMS'                : 3,
                               'maximum'            : 4,
                               'minimum'            : 5,
                               'accumulated'        : 6,
                               'count'              : 7}
        '''Dictionnary for property sampling mode (BLE - Environnemental Sensing Service) '''

        self.invSampling: Dict = self._inv(self.sampling)
        '''Dictionnary for property sampling mode (BLE - Environnemental Sensing Service) '''

        self.application: Dict = { self.nullDict        : 0,
                       'air'                            : 1,
                       'water'                          : 2,
                       'barometric'                     : 3,
                       'soil'                           : 4,
                       'infrared'                       : 5,
                       'map database'                   : 6,
                       'barometric elevation source'    : 7}
        '''Dictionnary for property application (BLE - Environnemental Sensing Service) '''

        self.invApplication = self._inv(self.application)
        '''Dictionnary for property application (BLE - Environnemental Sensing Service) '''

    def _initName(self) :
    #%% init name
        ''' Name initialization (string) '''
        self.json_nval_loc    = "nvalloc"
        self.json_nval_dat    = "nvaldat"
        self.json_nval_res    = "nvalres"
        self.json_nval_prp    = "nvalprop"
        self.json_type_loc    = "typeloc"
        self.json_type_obs    = "typeobs"
        self.json_type_dat    = "typedat"
        self.json_type_res    = "typeres"
        self.json_type_prp    = "typeprop"

        self.data             = "data"
        self.datetime         = "datetime"
        self.ilist            = 'ilist'
        self.timeslot         = 'timeslot'
        #self.parameter        = "parameter"
        self.id               = "id"
        self.param            = "param"
        self.information      = "information"
        self.type             = "type"
        self.multi            = "Multi"
        self.obs              = "obs"
        self.dat              = "dat"
        self.loc              = "loc"
        self.prp              = "prp"
        self.res              = "res"
        self.coordinates      = "coordinates"
        self.index            = "index"
        self.idxref           = "idxref"
        self.variable         = "variable"
        self.order            = "order"
        self.name             = "name"

        self.nul_classES      = "nullClass"
        self.obs_classES      = "observation"
        self.dat_classES      = "datation"
        self.loc_classES      = "location"
        self.prp_classES      = "property"
        self.res_classES      = "result"

        self.obs_attributes   = "attributes"
        self.obs_id           = "id"
        self.obs_name         = "name"
        self.obs_data         = "data"
        self.obs_param        = "param"
        self.obs_resultTime   = "ResultTime"
        self.obs_complet      = "complet"
        self.obs_reference    = "reference"
        self.obs_score        = "score"
        self.obs_order        = "order"
        self.obs_idxref       = "idxref"

        self.res_mRate        = "measureRate"
        self.res_nEch         = "nEch"
        self.res_dim          = "dim"
        self.res_axes         = "axes"
        self.set_nValue       = "nval"
        self.res_value        = "resvalue"
        
        self.dat_box            = "datationBox"
        self.loc_box            = "locationBox"
        self.geo_box            = "geobox"
        self.prp_box            = "propertyBox"

        self.prp_type	        = "prp";
        self.prp_unit		    = "unit";
        self.prp_sampling	    = "samplingFunction";
        self.prp_appli		    = "application";
        self.prp_EMFId		    = "EMFId";
        self.prp_sensorType	    = "sensorType";
        self.prp_upperValue	    = "upperValue";
        self.prp_lowerValue	    = "lowerValue";
        self.prp_period	        = "period";
        self.prp_interval	    = "updateInterval";
        self.prp_uncertain      = "uncertainty";
        self.prp_name           = "name";

        self.obs_valName      = "observation"
        self.dat_valName      = "datvalue"
        self.loc_valName      = "locvalue"
        self.prp_valName      = "prpvalue"
        self.ext_valName      = "extvalue"
        self.nam_valName      = "namvalue"
        self.res_valName      = "resvalue"
        self.ili_valName      = "ilist"
        self.iin_valName      = "iindex"
        self.coo_valName      = "coordinate"
        self.tim_valName      = "datetime"
        self.slo_valName      = "timeslot"

        self.obs_clsName      = 'Observation'
        self.dat_clsName      = 'DatationValue'
        self.loc_clsName      = 'LocationValue'
        self.prp_clsName      = 'PropertyValue'
        self.ext_clsName      = 'ExternValue'
        self.nam_clsName      = 'NamedValue'
        self.ili_clsName      = 'Ilist'
        self.iin_clsName      = 'Iindex'
        self.coo_clsName      = 'coordinate'
        self.tim_clsName      = 'datetime'
        self.slo_clsName      = 'TimeSlot'
        self.ES_clsName       = 'ESValue'
        
        self.filter           = '$filter'
        
    def _initReferenceValue(self):
    #%% init reference value
        ''' Reference value initialization '''
        self.defaultindex     = '$default'
        self.variable         = -1
        self.nullparent       = -2
        self.miniStr          = 10
        self.distRef          = [48.87, 2.35] # coordonnées Paris lat/lon
        #self.nullDate         = datetime(1970, 1, 1)
        self.nullDate         = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        self.nullCoor         = [-1, -1]
        self.nullInd          = [-1, -1, -1]
        self.nullAtt          = "null"
        #self.nullPrp          = {}
        self.nullPrp          = {'prp':'-'}
        self.nullName         = ""
        self.nullDict         = "-"
        self.nullInt          = 0
        self.nullVal          = math.nan
        self.nullExternVal    = None
        self.nullValues = (self.nullDate, self.nullCoor, self.nullInd, self.nullName,
                           self.nullAtt, self.nullDict, self.nullName, self.nullVal, 
                           self.nullPrp)
        
    def _initDefaultValue(self, defnone=True):
    #%% init default value
        ''' Default value initialization '''
        if defnone : self.def_clsName      = None
        else: self.def_clsName      = self.nam_clsName
        if self.def_clsName: self.def_dtype = self.valname[self.def_clsName]
        else: self.def_dtype = None

ES = Es(defnone=True)
