#include "stdafx.h"  // à supprimer arduino
#include <sstream>
#include "ESElement.h"
#include "ESObservation.h"

using namespace std;

const std::map<std::string, std::string> ESElement::mTypeAtt = {
{ "ResultSetTime",		"observation" },
{ "ResultSetQuality",	"ResultSet" },
{ "propertyType",	"PropertyValue" },
{ "EMFType",		"ObservingEMF" },
{ "ResultSetNature",	"ObservingEMF" },
{ "lowerValue",		"ObservingEMF" },
{ "upperValue",		"ObservingEMF" },
{ "period",			"ObservingEMF" },
{ "uncertainty",	"ObservingEMF" },
{ "unit",			"PropertyValue" },
{ "sampling",		"PropertyValue" },
{ "application",	"PropertyValue" }
};
const std::string ESElement::metaTypeESObject	= "ESObject";


ESElement::ESElement() { mAtt["type"] = "null"; typeES = "null"; classES = "null"; pContenant.clear(); pComposant.clear(); }
void ESElement::setAtt(std::string key, std::string value)	{ mAtt[key] = value; }
std::string ESElement::getAtt(std::string key) const		{ if (isAtt(key)) return  mAtt.at(key); return "null"; }
std::string ESElement::getTypeES() const					{ return typeES; }
std::string ESElement::getClassES() const					{ return classES; }
std::string ESElement::getMetaType() const					{ return metaType; }
std::map<std::string, std::string> ESElement::getmAtt() const { return mAtt; }
bool ESElement::isAtt(std::string key) const				{
	for (std::map<string, string>::const_iterator it = mAtt.begin(); it != mAtt.end(); ++it) if (it->first == key) return 1;
	return 0;
}
bool ESElement::isESAtt(std::string esClass, std::string key) {
	for (std::pair<string, string> couple : ESElement::mTypeAtt) if (couple.second == esClass and couple.first == key) return 1;
	return 0;
}
bool ESElement::isESObs(std::string esClass, JsonObject jObj) {
	bool esObs = 0;
	JsonObject objAtt = jObj[esClass];
	if (objAtt.isNull()) {
		for (JsonPair p : jObj) {
			if ((string)p.key().c_str() == esClass) esObs = 1;
			for (std::pair<string, string> couple : ESElement::mTypeAtt)
				if ((string)p.key().c_str() == couple.first and esClass == couple.second) esObs = 1;
		}
	} else esObs = 1;
	return esObs;
}
JsonObject ESElement::deserialize(std::string json) {
	const int capa = 1000;
	StaticJsonDocument<capa> doc;
	DeserializationError error = deserializeJson(doc, json);
	JsonObject obj = doc.as<JsonObject>();
	return obj;
}
std::string ESElement::getAttAll(std::string key) const {
	if (isAtt(key)) return mAtt.at(key);
	for (int i = 0; i < (int)pComposant.size(); i++) if (pComposant[i]->getAttAll(key) != "null") return pComposant[i]->getAttAll(key);
	return "null";
}
void ESElement::addComposant(ESElement* pCompos) {
	pComposant.push_back(pCompos);
	pCompos->pContenant.push_back(this);
}
void ESElement::println(std::string nam, std::string pr) { 
#ifdef TEST_ES
	cout << nam << " : " << pr << endl;					// standard
#else
	Serial.println((nam + " : " + pr).c_str());		// arduino
#endif
}
ESElement* ESElement::element(std::string comp) const {
	for (int i = 0; i < (int)pComposant.size(); i++) {
		if (pComposant[i]->getTypeES() == comp or pComposant[i]->getClassES() == comp or pComposant[i]->getMetaType() == comp or pComposant[i]->mAtt["type"] == comp)
			return pComposant[i];
		else if (pComposant[i]->element(comp) != nullptr) return pComposant[i]->element(comp);
	}
	return nullptr;
}
void ESElement::majMeta() { for (int i = 0; i < (int)pContenant.size(); i++) if (pContenant[i]->getTypeES() == Observation::ESclass) static_cast<Observation*>(pContenant[i])->majType(); }
void ESElement::print() const {
	std::stringstream ss;
	ESElement::println("classES, typeES : ", classES + " " + typeES);
	for (std::map<string, string>::const_iterator it = mAtt.begin(); it != mAtt.end(); ++it) ESElement::println(it->first, it->second);
	ss << pComposant.size();
	if (pComposant.size() > 0) ESElement::println("nombre de composants", ss.str());
	ss << pContenant.size();
	if (pContenant.size() > 0) ESElement::println("nombre de contenants", ss.str());
}
std::string ESElement::jsonAtt(bool complet) const {
	std::string json(""), deb, fin, firs, val;
	for (std::map<string, string>::const_iterator it = mAtt.begin(); it != mAtt.end(); ++it) {
		val = it->second;
		if ((complet or it->first[0] == '$') && (val != "null")) {
			if (it->first == "type" or it->first == "nval") firs = it->first + classES;
			else firs = it->first;
			deb = ""; fin = "";
			if (val[0] != '{' && val[0] != '[' && val[0] != '+' && val[0] != '-' && val[0] != '0' && val[0] != '1' && val[0] != '2' && val[0] != '3' && \
				val[0] != '4' && val[0] != '5' && val[0] != '6' && val[0] != '7' && val[0] != '8' && val[0] != '9' && val[0] != '"') {
				deb = "\""; fin = "\"";
			}
			json += "\"" + firs + "\":" + deb + val + fin + ",";
		}
	}
	return json;
}
ESObject::ESObject() : ESElement() { metaType = "ESObject"; name = "observation xx"; }

ESObs::ESObs() : ESElement() { metaType = "ESObs"; nValue = 0; }
ESObs::ESObs(Observation* pObs) : ESElement() { metaType = "ESObs"; nValue = 0; if (pObs != nullptr) pObs->addComposant(this); }
int ESObs::getNvalue() const { return nValue; }
void ESObs::setNvalue(int nval) { nValue = nval; stringstream nv; nv << nValue; mAtt["nval"] = nv.str(); }

