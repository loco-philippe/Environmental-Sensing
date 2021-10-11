# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 13:35:28 2021

@author: a179227
"""
class Es:
    pass

ES = Es()

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

ES.obj_metaType     = "ESObject"
ES.obs_metaType     = "ESObs"
#ES.elt_metaType     = "ESElement"

ES.obs_classES      = "observation"
ES.dat_classES      = "datation"
ES.loc_classES      = "location"
ES.prp_classES      = "property"
ES.res_classES      = "result"

ES.obs_attributes   = "attributes"
ES.obs_id           = "id"
ES.obs_resultTime   = "ResultTime"
ES.obs_complet      = "complet"
ES.obs_score        = "score"

ES.res_mRate        = "measureRate"
ES.res_sRate        = "samplingRate"
ES.res_nEch         = "nEch"
ES.res_dim          = "dim"

ES.set_nValue       = "nval"

ES.obs_typeES       = "observation"
ES.set_typeES       = "set"

ES.dat_boxMin       = "timeBoxMin"
ES.dat_boxMax       = "timeBoxMax"

ES.loc_boxMin       = "boudingBoxMin"
ES.loc_boxMax       = "boudingBoxMax"

ES.prp_propType	    = "property";
ES.prp_unit		    = "unit";
ES.prp_sampling	    = "sampling";
ES.prp_appli		= "application";
ES.prp_EMFId		= "EMFId";

ES.dat_valueName    = "dateTime"
ES.dat_valueType    = "instant"
ES.loc_valueName    = "coordinates"
ES.loc_valueType    = "Point"
ES.prp_valueName    = "propertyList"
ES.prp_valueType    = "list"
ES.res_valueName    = "value"
ES.res_valueType    = "real_int_str"
ES.real_valueType   = "real"
ES.int_valueType    = "int"
ES.str_valueType    = "string"

ES.mOption = {"json_res_index" : False, # affiche index
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
              #"maj_index" : False, # dans majtype
              "maj_reset_index" : False # dans majtype
              }

mValObs  = { ES.loc_valueName   : ES.loc_classES  ,
             ES.dat_valueName   : ES.dat_classES  ,
             ES.res_valueName   : ES.res_classES  ,
             ES.prp_valueName   : ES.prp_classES  }

mTypeAtt = {ES.type             : ES.obs_classES  ,
            ES.obs_resultTime   : ES.obs_classES  ,
            "ResultQuality"     : ES.res_classES  ,
            "EMFType "          : "ObservingEMF"  ,
            "ResultNature "     : "ObservingEMF"  ,
            "lowerValue "       : "ObservingEMF"  ,
            "upperValue "       : "ObservingEMF"  ,
            "period "           : "ObservingEMF"  ,
            "uncertainty "      : "ObservingEMF"  }

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
	 22 :"timeLoc" ,
	 100 :"measure" ,
	 101 :"record" ,
	 102 :"meanRecord" ,
	 110 :"feature" ,
	 111 :"obsUnique" ,
	 112 :"obsMeanFixed" ,
	 120 :"areaFeature" ,
	 121 :"obsMeanArea" ,
	 122 :"meanTimeLoc" ,
	 200 :"multiMeasure" ,
	 201 :"multiRecord" ,
	 202 :"measureHistory" ,
	 210 :"featureVariation" ,
	 211 :"obsSampled" ,
	 212 :"obsSequence" ,
	 220 :"measureLoc" ,
	 221 :"obsLoc" ,
	 222 :"obsTimeLoc", 
	 223 :"obserror" 
}
'''
class obsVide:
    pass

CObservation = obsVide()
CCoordinates = obsVide()
CIntValue = obsVide()
CRealValue = obsVide()
CStringValue = obsVide()
CTimeValue = obsVide()
CPropertyValue = obsVide()
CDatation = obsVide()
CLocation = obsVide()
CResult = obsVide()
CResultValue = obsVide()
CProperty = obsVide()

CCoordinates.jsonName		= "coordinates";
CResultValue.jsonName		= "resultValue";
CStringValue.jsonName		= "stringValue";
CRealValue.jsonName		= "realValue";
CIntValue.jsonName		= "intValue";
CTimeValue.jsonName		= "phenomenonTime";
CPropertyValue.jsonName	= "PropertyValue";
CDatation.jsonName = "phenomenonTime";
CLocation.jsonName		= "coordinates";
CProperty.jsonName	= "PropertyValue";
CResult.jsonName		= "resultValue";


CDatation.ESclass = "datation";
CLocation.ESclass = "location";
CResult.ESclass	= "result";
CProperty.ESclass = "property";
CObservation.name = 'observation'
CProperty.name = 'property'
CDatation.name = 'datation'
CLocation.name = 'location'
CResult.name = 'result'
CCoordinates.EStype		= "geometry";
CCoordinates.type			= "point";
CResultValue.EStype		= "ResultSet";
CResultValue.type			= "result";
CStringValue.EStype		= "ResultSet";
CStringValue.type			= "stringRes";
CRealValue.EStype			= "ResultSet";
CRealValue.type			= "realRes";
CIntValue.EStype			= "ResultSet";
CIntValue.type			= "intRes";
CTimeValue.EStype			= "TimeStampSet";
CTimeValue.type			= "date";
CPropertyValue.EStype		= "PropertySet";
CPropertyValue.type		= "meas";
CPropertyValue.propTypeN	= "PropertyType";
CPropertyValue.unitN		= "unit";
CPropertyValue.samplingN	= "sampling";
CPropertyValue.appliN		= "application";
CPropertyValue.EMFIdN		= "EMFId";
'''

