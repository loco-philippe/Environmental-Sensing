#include "stdafx.h"			// à supprimer arduino

#include "ESObservation.h"
#include <algorithm>
#include <array>
#include <sstream>

#define ESSetDatation		ESSet<TimeValue, Datation>
#define ESSetLocation		ESSet<LocationValue, Location>
#define ESSetProperty		ESSet<PropertyValue, Property>
#define ESSetResultReal		ESSet<ResultValue<RealValue>,	Result>
#define ESSetResultInt		ESSet<ResultValue<IntValue>,	Result>
#define ESSetResultString	ESSet<ResultValue<StringValue>,	Result>
#define maxSizeJson			50000

using namespace std;

const std::string Datation		::ESclass = "datation";
const std::string Location		::ESclass = "location";
const std::string Result		::ESclass = "result";
const std::string Property		::ESclass = "property";
const std::string Observation	::ESclass = "observation";

ESSetLocation*	 Observation::setLocation()		{ if (element(Location::ESclass) != nullptr) return static_cast<ESSetLocation*	>(element(Location::ESclass)); else return nullptr;}
ESSetDatation*	 Observation::setDatation()		{ if (element(Datation::ESclass) != nullptr) return static_cast<ESSetDatation*	>(element(Datation::ESclass)); else return nullptr;}
ESSetProperty*	 Observation::setProperty()		{ if (element(Property::ESclass) != nullptr) return static_cast<ESSetProperty*	>(element(Property::ESclass)); else return nullptr;}
ESSetResultReal* Observation::setResultReal()	{ if (element(Result::ESclass)	 != nullptr) return static_cast<ESSetResultReal*>(element(Result  ::ESclass)); else return nullptr;}
ESSetResultInt*	 Observation::setResultInt()	{ if (element(Result::ESclass)	 != nullptr) return static_cast<ESSetResultInt*	>(element(Result  ::ESclass)); else return nullptr;}
ESSetResultString* Observation::setResultString(){ if (element(Result::ESclass)  != nullptr) return static_cast<ESSetResultString*>(element(Result::ESclass)); else return nullptr;}
Result*			 Observation::Result_()			{ if (element(Result::ESclass)	 != nullptr) return static_cast<Result*			>(element(Result  ::ESclass)); else return nullptr;}

int Observation::init(PropertyValue prop) { return addValue<PropertyValue, Property>(prop); }
int Observation::addValueSensor(RealValue val, TimeValue tim, LocationValue coor, int nprop) {
	ResultValue<RealValue> resVal(val);
	resVal.setindexRes(addIndex(tim, coor, nprop));
	return addValue<ResultValue<RealValue>, Result>(resVal);
}
int Observation::addValueSensor(StringValue val, TimeValue tim, LocationValue coor, int nprop) {
	ResultValue<StringValue> resVal(val);
	resVal.setindexRes(addIndex(tim, coor, nprop));
	return addValue<ResultValue<StringValue>, Result>(resVal);
}
indexRes Observation::addIndex(TimeValue tim, LocationValue coor, int nprop) {
	indexRes indval;
	indval.iloc = addValue<LocationValue, Location>(coor);
	indval.idat = addValue<TimeValue, Datation>(tim);
	indval.iprop = nprop;
	return indval;
}


std::map<int, std::string> Observation::obsCat = {
	{ -1, "obserror" },
	{ 0, "config" },
	{ 1, "top" },
	{ 2, "multiTop" },
	{ 10, "point" },
	{ 11, "track" },
	{ 12, "fixedTrack" },
	{ 20, "zoning" },
	{ 21, "multiTrack" },
	{ 22, "timeLoc" },
	{ 100, "measure" },
	{ 101, "record" },
	{ 102, "meanRecord" },
	{ 110, "feature" },
	{ 111, "obsUnique" },
	{ 112, "obsMeanFixed" },
	{ 120, "areaFeature" },
	{ 121, "obsMeanArea" },
	{ 122, "meanTimeLoc" },
	{ 200, "multiMeasure" },
	{ 201, "multiRecord" },
	{ 202, "measureHistory" },
	{ 210, "featureVariation" },
	{ 211, "obsSampled" },
	{ 212, "obsSequence" },
	{ 220, "measureLoc" },
	{ 221, "obsLoc" },
	{ 222, "obsTimeLoc" },
	{ 223, "obserror" }
};
Observation::Observation()							: ESObject() { init(); }
Observation::Observation(JsonObject obj)			: ESObject() { init(obj); }
Observation::Observation(std::string json)			: ESObject() { init(json); }
Observation::Observation(Observation const&  obs)	: ESObject() { init("{" + obs.json(1, 0, 1) + "}"); }
Observation& Observation::operator=(Observation const&  obs)	 { init("{" + obs.json(1, 0, 1) + "}"); return *this; }
void Observation::init(std::string json)  {
	init();
	const int capa(maxSizeJson);
	StaticJsonDocument<capa> doc;
	DeserializationError error = deserializeJson(doc, json);
	if (error) ESElement::println("deserializeJson() failed: ", error.c_str());
	else {
		JsonObject obj = doc.as<JsonObject>();
		if (obj.containsKey("type") && obj["type"] == Observation::ESclass) init(obj);
	}
}
void Observation::init(JsonObject obj) {
	init();
	if (obj.containsKey("id"))   setAtt("id", obj["id"]);
	JsonObject objAtt = obj["attributes"];
	if (objAtt.isNull()) {
		for (JsonPair p : obj) {
			if (ESElement::isESAtt(Observation::ESclass, (string)p.key().c_str())) setAtt((string)p.key().c_str(), p.value());
			if (p.key().c_str()[0] == '$') setAtt((string)p.key().c_str(), p.value());
		}
		if (ESSetDatation		::isESSet(obj))	ESSetDatation*		pTim = new ESSetDatation(this, obj);
		if (ESSetLocation		::isESSet(obj))	ESSetLocation*		pGeo = new ESSetLocation(this, obj);
		if (ESSetProperty		::isESSet(obj))	ESSetProperty*		pMea = new ESSetProperty(this, obj);
		if (ESSetResultReal		::isESSet(obj))	ESSetResultReal*	pRes = new ESSetResultReal(this, obj);
		if (ESSetResultInt		::isESSet(obj))	ESSetResultInt*		pRes = new ESSetResultInt(this, obj);
		if (ESSetResultString	::isESSet(obj))	ESSetResultString*	pRes = new ESSetResultString(this, obj);
	}
	else {
		for (JsonPair p : objAtt) {
			if (ESElement::isESAtt(Observation::ESclass, (string)p.key().c_str()))	setAtt((string)p.key().c_str(), p.value());
			if (p.key().c_str()[0] == '$') setAtt((string)p.key().c_str(), p.value());
			else if (p.key().c_str() == Property::ESclass)	ESSetProperty*	pMea = new ESSetProperty(this, p.value());
			else if (p.key().c_str() == Location::ESclass)	ESSetLocation*	pGeo = new ESSetLocation(this, p.value());
			else if (p.key().c_str() == Datation::ESclass)	ESSetDatation*	pTim = new ESSetDatation(this, p.value());
		}
		for (JsonPair p : objAtt) {
			if (p.key().c_str() == Result::ESclass) {
				JsonObject objRes = objAtt["result"];
				for (JsonPair pr : objRes) {
					if (pr.key().c_str() == RealValue::valueName)	ESSetResultReal*	pRes = new ESSetResultReal	(this, p.value());
					if (pr.key().c_str() == IntValue::valueName)	ESSetResultInt*		pRes = new ESSetResultInt	(this, p.value());
					if (pr.key().c_str() == StringValue::valueName)	ESSetResultString*	pRes = new ESSetResultString(this, p.value());
				}
			}
		}
	}
	majType();
}
void Observation::init() {	mAtt["ResultTime"] = "null"; classES = Observation::ESclass; typeES = Observation::ESclass; mAtt["id"] = "null";
tEch = -1;	tMeas = -1;	complet = 0;	pComposant.clear();	pContenant.clear(); majType();
}
void Observation::print() const {
	ESElement::print();
	std::stringstream ss;
	ss << complet << " " << tMeas << " " << tEch;
	ESElement::println("indic (complet, taux mesure, taux ech) ", ss.str());
	for (int i = 0; i < (int)pComposant.size(); i++) {
		std::stringstream ss1;
		ss1 << pComposant[i]->getmAtt()["type"] << " nValue : " << static_cast<ESObs *>(pComposant[i])->getNvalue();
		ESElement::println(pComposant[i]->getTypeES(), ss1.str());
	}
}
std::string Observation::json(bool comp, bool value, bool detail) const { 
	bool det = !complet;
	std::string json("");
	if (value) json = "{";
	json += "\"type\":\"observation\"," ;
	if (mAtt.at("id") != "null") json += "\"_id\":\"" + mAtt.at("id") + "\",";
	if (comp) json += "\"attributes\":{";
	json += ESElement::jsonAtt(comp);
	for (int i = 0; i < (int)pComposant.size(); i++) if (static_cast<ESObs *>(pComposant[i])->json(comp, 1, det) != "") json += static_cast<ESObs *>(pComposant[i])->json(comp, 1, det) + ",";
	if (json.back() == ',') json.pop_back();
	if (comp) json += "}";
	if (value) json += "}";
	return json;
}
int Observation::addValue(PropertyValue val) { return addValue<PropertyValue, Property>(val);}

nValObs Observation::nValueObs() {
	nValObs nVal = { 0,0,0,0,0 };
	if (element("real")		!= nullptr or element("Multireal")	!= nullptr) nVal.nRes = setResultReal()->size();
	if (element("string")	!= nullptr or element("Multistring")!= nullptr) nVal.nRes = setResultString()->size();
	if (element("int")		!= nullptr or element("Multiint")	!= nullptr) nVal.nRes = setResultInt()->size();
	if (element("datation") != nullptr)										nVal.nDat = setDatation()->size();
	if (element("location") != nullptr)										nVal.nLoc = setLocation()->size();
	if (element("property") != nullptr)										nVal.nPrp = setProperty()->size();
	if (nVal.nPrp > 0) nVal.nEch = nVal.nRes / nVal.nPrp;
	return nVal;
}
void Observation::typeObs() {
	nValObs nv = nValueObs();
	score = min(max(min(nv.nEch, 2) * 100 + min(nv.nLoc, 2) * 10 + min(nv.nDat, 2), -1), 223);
	mAtt["type"] = Observation::obsCat[score];
	if (score == 222 and Result_()->getdim() == 1)	mAtt["type"] = "obsPath";
	if (score == 222 and Result_()->getdim() == 2)	mAtt["type"] = "obsAreaSequence";
}

void Observation::majTypeObs(int nRes, int nPrp, int nDat, int nLoc, int nEch, int dim) {
	bool echDat, echLoc, locDat;
	score = min(nEch, 2) * 100 + min(nLoc,2) * 10 + min(nDat, 2);
	stringstream ss; ss << score;
	mAtt["type"] = Observation::obsCat[score];
	mAtt["score"] = ss.str();
	if (nRes * nPrp * nDat * nLoc < 1) return;
	if (score == 22 and dim == 1)	mAtt["type"] = "trackPath";
	if (score == 22 and dim == 2)	mAtt["type"] = "timeZone";
	if (score == 122 and dim == 1)	mAtt["type"] = "measAreaSequence";
	if (score == 122 and dim == 2)	mAtt["type"] = "obsMeanPath";
	if (score == 222 and dim == 1)	mAtt["type"] = "obsPath";
	if (score == 222 and dim == 2)	mAtt["type"] = "obsAreaSequence";
	if (Result_() != nullptr)
		if (Result_()->getMaxIndex() == -1 && \
			((score == 202 or score == 212) && nRes != nDat) or ((score == 220 or score == 221) && nRes != nLoc) or (score == 222 && (nRes != nLoc or nLoc != nDat) && nRes != nLoc * nDat)) \
		mAtt["type"] = "obserror";
}
void Observation::majType() {
	int nPrp(0), nDat(0), nRes(0), nLoc(0), nEch(0), dim(0), nLocU(0), nDatU(0);
	bool indexe(0);
	array<int, 4> indic;
	for (int i = 0; i < (int)pComposant.size(); i++) {
		if (pComposant[i]->getClassES() == Property::ESclass) {
			nPrp = static_cast<Result *>(pComposant[i])->getNvalue();
		}
		else if (pComposant[i]->getClassES() == Datation::ESclass) {
			nDat = static_cast<Result *>(pComposant[i])->getNvalue();
			static_cast<ESSetDatation *>	(pComposant[i])->analyse();
		}
		else if (pComposant[i]->getClassES() == Location::ESclass) {
			nLoc = static_cast<Result *>(pComposant[i])->getNvalue();
			static_cast<ESSetLocation *>	(pComposant[i])->analyse();
		}
		else if (pComposant[i]->getClassES() == Result::ESclass) {
			nRes = static_cast<Result *>(pComposant[i])->getNvalue();
			indexe = static_cast<Result *>(pComposant[i])->getMaxIndex() > -1;
			if (indexe) {
				indic = static_cast<Result *>	(pComposant[i])->indicateur();
				static_cast<Result *>(pComposant[i])->majIndic(indic[0], indic[1], indic[2], indic[3]);
				nEch = indic[0]; nDatU = indic[2]; nLocU = indic[3]; dim = indic[1];
			}
		}
	}
	if (!indexe)
	{
		int sco = min(nRes, 2) * 100 + min(nLoc, 2) * 10 + min(nDat, 2);
		dim = 1;
		if (nRes < 2 && nLoc < 2 && nDat < 2) dim = 0;
		if ((sco == 22 or sco == 122) && nLoc != nDat) dim = 2;
		if (sco == 222 && nRes == nLoc * nDat) dim = 2;
		complet = sco < 202 or sco == 210 or sco == 211 or ((sco == 202 or sco == 212) && nRes == nDat) or ((sco == 220 or sco == 221) && nRes == nLoc) \
			or (sco == 222 && ((nRes == nLoc && nLoc == nDat) or nRes == nLoc * nDat));
		tMeas = 1; tEch = 1;
		if (((sco == 202 or sco == 212) && nRes != nDat) or ((sco == 220 or sco == 221) && nRes != nLoc) or (sco == 222 && (nRes != nLoc or nLoc != nDat) && nRes != nLoc * nDat)) \
			{ tMeas = 0, tEch = 0; dim = 0; complet = 0; }
		majTypeObs(nRes, nPrp, nDat, nLoc, nRes, dim);
	} else {
		complet = (nRes == nPrp * nLoc * nDat and dim == 2 and nEch == nLoc * nDat) or \
			(nRes == nPrp * nLoc and nLoc == nDat and dim == 1 and nEch == nLoc) or \
			(nRes * nPrp * nLoc * nDat > 0 and dim == 0 and nEch == 1);
		if (nEch * nPrp > 0) tMeas = (float)nRes / float(nEch * nPrp);
		if (complet) tMeas = 1.0;
		if (dim == 2 and nDat * nLoc > 0) tEch = (float)nEch / float(nDat * nLoc);
		if (dim <  2 and max(nDat, nLoc) > 0) tEch = (float)nEch / float(max(nDat, nLoc));
		if (complet) tEch = 1.0;
		majTypeObs(nRes, nPrp, min(nDatU, nDat), min(nLocU, nLoc), nEch, dim);
		typeObs();
	}
	if (Result_() != nullptr) Result_()->majindexRes(nRes, nPrp, nDat, nLoc, nEch);
	stringstream co; co << complet;	mAtt["complet"] = co.str();
	stringstream tm; tm << tMeas;	mAtt["measureRate"] = tm.str();
	stringstream te; te << tEch;	mAtt["samplingRate"] = te.str();
}

Location::Location() : ESObs() { init(); }
Location::Location(Observation* pObs) : ESObs(pObs) { init(); }
void Location::init() { boxMin = LocationValue(); boxMax = LocationValue();  classES = ESclass; }
LocationValue Location::getboxMin() const { return boxMin; }
LocationValue Location::getboxMax() const { return boxMax; }

Property::Property() : ESObs() { init(); }
Property::Property(Observation* pObs) : ESObs(pObs) { init(); }
void Property::init() { classES = ESclass; }

Result::Result() : ESObs() { init(); }
Result::Result(Observation* pObs) : ESObs(pObs) { init(); }
void Result::init() { classES = ESclass; nEch = 0; dim = 0; nDatUse = 0; nLocUse = 0;}
void Result::majIndic(int ech, int dimension, int datU, int locU) {
	nEch = ech; dim = dimension; nDatUse = datU; nLocUse = locU;
	stringstream ec; ec << nEch;	mAtt["nEch"] = ec.str();
	stringstream di; di << dim;		mAtt["dim"] = di.str();
}
int Result::getnEch() const { return nEch; }
int Result::getnDatU() const { return nDatUse; }
int Result::getnLocU() const { return nLocUse; }
int Result::getdim() const { return dim; }

void Result::majindexRes(int nRes, int nPrp, int nDat, int nLoc, int nEch) {
	int il(0), id(0), ip(0);
	if (getMaxIndex() > -1) return;
	if (nRes == nPrp * nDat * nLoc)
		for (int i = 0; i < nRes; i++) {
			if (nLoc * nPrp > 0) {
				id = i / (nLoc * nPrp);
				il = (i % (nLoc * nPrp)) / nPrp;
				if (nPrp > 0) ip = (i % (nLoc * nPrp)) % nPrp;
			}
			if (getmAtt()["type"] == StringValue::valueType) (*static_cast<ESSetResultString*>	(this))[i].setindexRes({ id, il, ip });
			if (getmAtt()["type"] == RealValue::valueType)	(*static_cast<ESSetResultReal*>		(this))[i].setindexRes({ id, il, ip });
			if (getmAtt()["type"] == IntValue::valueType)	(*static_cast<ESSetResultInt*>		(this))[i].setindexRes({ id, il, ip });
		}
	else if (nRes == nPrp * nDat and nRes == nPrp * nLoc)
		for (int i = 0; i < nRes; i++) {
			if (nPrp > 0) {
				int idloc = i / nPrp;
				ip = i % nPrp;
				if (nRes == nPrp * nDat) id = idloc;
				if (nRes == nPrp * nLoc) il = idloc;
			}
			if (getmAtt()["type"] == StringValue::valueType) (*static_cast<ESSetResultString*>	(this))[i].setindexRes({ id, il, ip });
			if (getmAtt()["type"] == RealValue::valueType)	(*static_cast<ESSetResultReal*>		(this))[i].setindexRes({ id, il, ip });
			if (getmAtt()["type"] == IntValue::valueType)	(*static_cast<ESSetResultInt*>		(this))[i].setindexRes({ id, il, ip });
		}
}
Datation::Datation() : ESObs() { init(); }
Datation::Datation(Observation* pObs) : ESObs(pObs) { init(); }
void Datation::init() { boxMin = TimeValue(); boxMax = TimeValue();  classES = ESclass; }
TimeValue Datation::getboxMin() const { return boxMin; }
TimeValue Datation::getboxMax() const { return boxMax; }

