# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 13:35:28 2021

@author: a179227
"""
from datetime import datetime

class Es:
    pass

def inv(mp)     : return dict(zip(mp.values(), mp.keys()))
def invnum(mp)  : return dict(zip([k[0] for k in list(mp.values())], mp.keys()))


ES = Es()

ES.debug            = False

ES.json_nval_loc    = "nvalloc"
ES.json_nval_dat    = "nvaldat"
ES.json_nval_res    = "nvalres"
ES.json_nval_prp    = "nvalprop"
ES.json_type_loc    = "typeloc"
ES.json_type_obs    = "typeobs"
ES.json_type_dat    = "typedat"
ES.json_type_res    = "typeres"
ES.json_type_prp    = "typeprop"

ES.parameter        = "parameter"
ES.information      = "information"
ES.type             = "type"
ES.multi            = "Multi"
ES.obs              = "obs"
ES.dat              = "dat"
ES.loc              = "loc"
ES.prp              = "prp"
ES.res              = "res"
ES.coordinates      = "coordinates"

ES.nullDate         = datetime(1970, 1, 1)
ES.nullCoor         = [-1, -1]
ES.nullInd          = [-1, -1, -1]
ES.nullName         = ""

ES.obj_metaType     = "ESObject"
ES.obs_metaType     = "ESObs"

ES.nul_classES      = "nullClass"
ES.obs_classES      = "observation"
ES.dat_classES      = "datation"
ES.loc_classES      = "location"
ES.prp_classES      = "property"
ES.res_classES      = "result"

ES.obs_attributes   = "attributes"
ES.obs_id           = "id"
ES.obs_resultTime   = "ResultTime"
ES.obs_complet      = "complet"
ES.obs_reference    = "reference"
ES.obs_score        = "score"

ES.res_mRate        = "measureRate"
ES.res_sRate        = "samplingRate"
ES.res_nEch         = "nEch"
ES.res_dim          = "dim"
ES.res_axes         = "axes"
ES.set_nValue       = "nval"

ES.obs_typeES       = "observation"
ES.set_typeES       = "set"

ES.dat_boxMin       = "timeBoxMin"
ES.dat_boxMax       = "timeBoxMax"

ES.loc_boxMin       = "boudingBoxMin"
ES.loc_boxMax       = "boudingBoxMax"

ES.prp_propType	    = "prp";
ES.prp_unit		    = "unit";
ES.prp_sampling	    = "samplingFunction";
ES.prp_appli		= "application";
ES.prp_EMFId		= "EMFId";
ES.prp_sensorType	= "sensorType";
ES.prp_upperValue	= "upperValue";
ES.prp_lowerValue	= "lowerValue";
ES.prp_period	    = "period";
ES.prp_interval	    = "updateInterval";
ES.prp_uncertain    = "uncertainty";
ES.prp_name         = "name";

#ES.dat_nullName     = ""
#ES.dat_valName      = ["instant", "slot", "datName"]
ES.dat_valName      = ["instant", "slot"]
ES.dat_valueType    = "datationValue"
#ES.loc_nullName     = ""
#ES.loc_valName      = ["point", "shape", "locName"]
ES.loc_valName      = ["point", "shape"]
ES.loc_valueType    = "locationValue"
#ES.prp_nullName     = ""
ES.prp_valName      = ["prpType", "characteristic"]
ES.prp_valueType    = "propertyValue"
#ES.res_nullName     = ""
ES.res_valName      = ["value"]
ES.res_valueType    = "resultValue"
ES.real_valueType   = "real"
ES.int_valueType    = "int"
ES.str_valueType    = "string"

ES.mOption = {"json_res_index" : False, # affiche index
              "json_prp_type" : True, # affiche name ou property
              "json_prp_name" : False, # affiche name ou property
              "json_dat_instant" : True, # affiche instant (ou mean de slot)
              "json_dat_name" : False, # affiche name ou instant/slot
              "json_loc_point" : True, # affiche point (ou shape.centroid)
              "json_loc_name" : False, # affiche name ou instant/slot
              "json_ESobs_class" : False, # json des ESobs
              "json_elt_type" : False, # jsonAtt avec type xxxx
              "json_obs_val" : True, #key:val ou val
              "json_obs_attrib" : False, # avec key = attributes
              "json_param" : False, # ok
              "json_info_type" : True,
              "json_info_nval" : True,
              "json_info_box" : True,
              "json_info_autre" : True,
              "unic_index" : True, # dans ESSet
              "bytes_res_format" : "null", # calculé à partir de propperty si "null"
              "maj_reset_index" : False, # dans majtype
              "sort_order" : [0,1,2]
              }
mValObs  = { ES.loc_valName[0]  : ES.loc_classES  ,
             ES.loc_valName[1]  : ES.loc_classES  ,
             #ES.loc_valName[2]  : ES.loc_classES  ,
             ES.dat_valName[0]  : ES.dat_classES  ,
             ES.dat_valName[1]  : ES.dat_classES  ,
             #ES.dat_valName[2]  : ES.dat_classES  ,
             ES.prp_valName[0]  : ES.prp_classES  ,
             ES.prp_valName[1]  : ES.prp_classES  ,
             ES.res_valName[0]  : ES.res_classES  }

mTypeAtt = {ES.type             : ES.obs_classES  ,
            ES.information      : ES.nul_classES  ,
            ES.obs_resultTime   : ES.obs_classES  ,
            ES.obs_reference    : ES.obs_classES  ,
            "ResultQuality"     : ES.res_classES  ,            
            ES.prp_propType	    : ES.prp_classES  ,
            ES.prp_unit		    : ES.prp_classES  ,
            ES.prp_sampling	    : ES.prp_classES  ,
            ES.prp_appli        : ES.prp_classES  ,
            ES.prp_EMFId		: ES.prp_classES  ,
            ES.prp_sensorType	: ES.prp_classES  ,
            ES.prp_upperValue	: ES.prp_classES  ,
            ES.prp_lowerValue	: ES.prp_classES  ,
            ES.prp_period	    : ES.prp_classES  ,
            ES.prp_interval	    : ES.prp_classES  ,
            ES.prp_uncertain    : ES.prp_classES  ,
            "EMFType "          : "ObservingEMF"  ,
            "ResultNature "     : "ObservingEMF"  }

mDistRef = [48.87, 2.35] # coordonnées Paris lat/lon

ES.codeb = {ES.obs_classES  :   5 ,
            ES.dat_classES  :   2 ,
            ES.loc_classES  :   1 ,
            ES.res_classES  :   4 ,
            ES.prp_classES  :   3 ,
            ES.loc_valueType:   1 ,
            ES.dat_valueType:   2 ,
            ES.prp_valueType:   3 }

ES.vName = {ES.obs_classES  :   ES.obs ,
            ES.dat_classES  :   ES.dat ,
            ES.loc_classES  :   ES.loc ,
            ES.res_classES  :   ES.res ,
            ES.prp_classES  :   ES.prp }

ES.obsCat = {
	 -1 :"obserror" ,
	 0  :"config" ,
	 1  :"top" ,
	 2  :"multiTop" ,
	 10 :"point" ,
	 11 :"track" ,
	 12 :"fixedTrack" ,
	 20 :"zoning" ,
	 21 :"multiTrack" ,
	 22 :"datloc" ,
	 23 :"datloc" ,
	 100 :"measure" ,
	 101 :"record" ,
	 102 :"meanRecord" ,
	 110 :"feature" ,
	 111 :"obsUnique" ,
	 112 :"obsMeanFixed" ,
	 120 :"areaFeature" ,
	 121 :"obsMeanArea" ,
	 122 :"meanTimeLoc" ,
	 123 :"meanTimeLoc" ,
	 200 :"multiMeasure" ,
	 201 :"multiRecord" ,
	 202 :"measureHistory" ,
	 201 :"multiRecord" ,
	 203 :"featureVariation" ,
	 211 :"obsSampled" ,
	 212 :"obsSequence" ,
	 213 :"obsSequence" ,
	 220 :"measureLoc" ,
	 221 :"obsLoc" ,
	 222 :"obsTimeLoc", 
	 223 :"obsTimeLoc", 
	 224 :"obsTimeLoc", 
	 225 :"obsTimeLoc", 
	 226 :"obsTimeLoc", 
	 227 :"obsTimeLoc", 
	 228 :"obsTimeLoc", 
	 229 :"obserror" 
}
ES.prop ={'null'    : (0 , 'e', 2,  0, 0, '-'   ),
          'utf-8'   : (2 ,  '', 0,  0, 0, '-'   ),
          'sfloat'  : (15, 'e', 2,  0, 0, '-'   ),
          'uint16'  : (3 , 'H', 2,  0, 0, '-'   ),
          'uint8'   : (7 , 'B', 1,  0, 0, '-'   ),
          'sint24'  : (13, 'l', 3,  0, 0, '-'   ),
          'uint24'  : (14, 'L', 3,  0, 0, '-'   ),
          'sint8'   : (6 , 'b', 1,  0, 0, '-'   ),
          'sint16'  : (8 , 'h', 4,  0, 0, '-'   ),
          'uint32'  : (4 , 'L', 4,  0, 0, '-'   ),
          'PM25'    : (21, 'e', 2,  1, 2, 'kg/m3'),
          'PM10'    : (22, 'e', 2,  0, 0, 'kg/m3'),
          'CO2'     : (23, 'H', 2,  0, 0, 'ppm' ),
          'temp'    : (24, 'h', 2, -2, 0, '°C'  )
          }
ES.cnum = invnum(ES.prop)

ES.sampling = { 'null'              : 0,
               'instantaneous'      : 1,
               'arithmetic mean'    : 2,
               'RMS'                : 3,
               'maximum'            : 4,
               'minimum'            : 5,
               'accumulated'        : 6,
               'count'              : 7}
ES.invSampling = inv(ES.sampling)
ES.application = { 'null'                       : 0,
               'air'                            : 1,
               'water'                          : 2,
               'barometric'                     : 3,
               'soil'                           : 4,
               'infrared'                       : 5,
               'map database'                   : 6,
               'barometric elevation source'    : 7}
ES.invApplication = inv(ES.application)

ES.axes = { 0  :    'dat',   # axes : [0,1,2], [0,21], [2, 10], [1, 20]
            1  :	'loc',   #        [0, 1],  [0, 2], [1, 2], [120]
            2  :	'prp',
            10 :	'datloc',
            20 :	'datprp',
            21 :	'locprp',
            120:	'datlocprp'}

