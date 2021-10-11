#include "stdafx.h"
#include "ESEMF.h"

using namespace std;

MainEMF::MainEMF() : ESObject() { init(); }
MainEMF::MainEMF(JsonObject obj) : ESObject() {
	init();
	JsonObject objEMF = obj["mainEMF"];
	if (objEMF.containsKey("id"))   setAtt("id", objEMF["id"]);
	if (objEMF.containsKey("type")) setAtt("type", objEMF["type"]);
	JsonObject objAtt = objEMF["attributes"];
	if (objAtt.isNull()) {
		ObservingEMF* pProp = new ObservingEMF(this, objEMF);
		for (JsonPair p : objEMF) if (ESElement::isESAtt("mainEMF", (string)p.key().c_str())) setAtt((string)p.key().c_str(), p.value());
	}
	else
		for (JsonPair p : objAtt)
			if (p.key() == "ObservingEMF") {
				if (p.value().is<JsonArray>()) {
					JsonArray prop = p.value().as<JsonArray>();
					for (int i = 0; i < (int)prop.size(); i++) ObservingEMF* pProp = new ObservingEMF(this, prop[i]);
				}
				else ObservingEMF* pProp = new ObservingEMF(this, p.value());
			}
			else if (ESElement::isESAtt("mainEMF", (string)p.key().c_str()))	setAtt((string)p.key().c_str(), p.value());
			majType();
}
void MainEMF::init() { mAtt["EMFType"] = "null"; mAtt["softwareRev"] = "null"; mAtt["manufactureName"] = "null"; classES = "mainEMF"; typeES = "mainEMF";
	mAtt["type"] = "EMFError"; mAtt["id"] = "null"; }
void MainEMF::print() {
	ESElement::print();
	for (int i = 0; i < (int)pComposant.size(); i++)	ESElement::println(" ", pComposant[i]->getTypeES()) ;
}
std::string MainEMF::json(bool complet, bool value, bool detail) const {
	std::string json("");
	bool multiEMF = pComposant.size() > 1;
	if (value) json = "{";
	json += "\"" + typeES + "\":{";
	if (mAtt.at("id") != "null") json += "\"id\":\"" + mAtt.at("id") + "\",";
	if (complet) json += "\"type\":\"" + mAtt.at("type") + "\",";
	if (multiEMF and complet) json += "\"attributes\":{";
	json += ESElement::jsonAtt(complet);
	if (multiEMF) json += "\"ObservingEMF\":[";
	for (int i = 0; i < (int)pComposant.size(); i++) if (static_cast<ObservingEMF *>(pComposant[i])->json(complet, false, detail) != "") \
		json += static_cast<ObservingEMF *>(pComposant[i])->json(complet, false, detail);
	if (multiEMF) json.back() = '],';
	if (json.back() == ',') json.back() = '}';
	if (value) json += "}";
	return json;
	
	//return endJson(complet, value, ESElement::json(complet, value, detail)); 
}
void MainEMF::majType() {
	if (pComposant.size() > 1) 	mAtt["type"] = "EMFMultiple";
	else if (pComposant.size() == 1) 	mAtt["type"] = "EMFUnique";
}

ObservingEMF::ObservingEMF() : ESObject() { init(nullptr); }
ObservingEMF::ObservingEMF(MainEMF* pEMF) : ESObject() { init(pEMF); }
ObservingEMF::ObservingEMF(MainEMF* pEMF, JsonObject obj) : ESObject() {
	init(pEMF);
	for (JsonPair p : obj)  if (ESElement::isESAtt("ObservingEMF", (string)p.key().c_str())) setAtt((string)p.key().c_str(), p.value());
}
void ObservingEMF::init(MainEMF* pEMF) {
	mAtt["id"] = "null"; mAtt["PropertyValue"] = "null"; mAtt["propertyType"] = "null"; classES = "ObservingEMF"; mAtt["type"] = "propError"; typeES = "ObservingEMF"; majType();
	if (pEMF != nullptr) pEMF->addComposant(this);
}
void ObservingEMF::majType() { if (mAtt["PropertyValue"] != "null") mAtt["type"] = "propUnique"; }
std::string ObservingEMF::json(bool complet, bool value, bool detail) const { 
	std::string json("");
	if (value) json = "{";
	json += "\"" + typeES + "\":{";
	if (mAtt.at("id") != "null") json += "\"id\":\"" + mAtt.at("id") + "\",";
	if (complet) json += "\"type\":\"" + mAtt.at("type") + "\",";
	json += ESElement::jsonAtt(complet);
	if (json.back() == ',') json.back() = '}';
	if (value) json += "}";
	return json;


	//return endJson(complet, value, ESElement::json(complet, value, detail)); 
}

