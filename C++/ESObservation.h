//#pragma once		// à supprimer arduino
#ifndef OBSES_
#define OBSES_
#include <string>
#include "ESElement.h"
#include "EScomponent.h"

template <typename Value, typename ObsClass>
class ESSet;
#define ESSetDatation		ESSet<TimeValue, Datation>
#define ESSetLocation		ESSet<LocationValue, Location>
#define ESSetProperty		ESSet<PropertyValue, Property>
#define ESSetResultReal		ESSet<ResultValue<RealValue>,	Result>
#define ESSetResultInt		ESSet<ResultValue<IntValue>,	Result>
#define ESSetResultString	ESSet<ResultValue<StringValue>,	Result>

class Location;
class Property;
class Result;
class Datation;
class Observation : public ESObject {
protected:
	static std::map<int, std::string> obsCat; // ajouter option
	indexRes addIndex(TimeValue tim, LocationValue coor, int nprop);
public:
	float tMeas, tEch;  // à supprimer
	int score;
	bool complet;
	nValObs nValueObs();
	void typeObs();
	ESSetLocation*		setLocation();
	ESSetDatation*		setDatation();
	ESSetProperty*		setProperty();
	ESSetResultReal*	setResultReal();
	ESSetResultInt*		setResultInt();
	ESSetResultString*	setResultString();
	Result*				Result_();
	static const std::string ESclass;	// ajout setloc, setdat, setres, setprop
	Observation();
	Observation(JsonObject obj);
	Observation(std::string json);
	Observation(Observation const&  obs);
	Observation& operator=(Observation const&  obs);
	void init(JsonObject obj);
	void init(std::string json);
	void init();

	void print() const;
	void majType();
	void majTypeObs(int nRes, int nPrp, int nDat, int nLoc, int nEch, int dim);

	template<typename Value, typename ObsClass> std::string getboxMin() const	{ 
		if (element(ObsClass::ESclass) == nullptr) return "null";
		return static_cast<ESSet<Value, ObsClass> *>	(element(ObsClass::ESclass))->getboxMin().json(1, 0);
	}
	template<typename Value, typename ObsClass> std::string getboxMax() const	{ 
		if (element(ObsClass::ESclass) == nullptr) return "null";
		return static_cast<ESSet<Value, ObsClass> *>	(element(ObsClass::ESclass))->getboxMax().json(1, 0);
	}
	template<typename Value, typename ObsClass> int		addValue(Value val)	{
		if (element(ObsClass::ESclass) == nullptr) ESSet<Value, ObsClass>*	pObsCl = new ESSet<Value, ObsClass>(this);
		return static_cast<ESSet<Value, ObsClass> *>	(element(ObsClass::ESclass))->addValue(val);
	}
	int addValue(PropertyValue val);
	std::string json(bool comp, bool value, bool detail) const;

	int init(PropertyValue prop);
	int addValueSensor(RealValue val, TimeValue tim, LocationValue coor, int nprop); // ajout addvalueobs
	int addValueSensor(StringValue val, TimeValue tim, LocationValue coor, int nprop); // ajout addvalueobs

};
class Location : public ESObs {
protected:
	LocationValue boxMin;
	LocationValue boxMax;  
public:
	static const std::string ESclass;
	Location();
	Location(Observation* pObs);
	void init();
	virtual std::string json(bool complet, bool value, bool detail) const = 0;
	LocationValue getboxMin() const;
	LocationValue getboxMax() const;
};
class Property : public ESObs {
public:
	static const std::string ESclass;
	Property();
	Property(Observation* pObs);
	void init();
	virtual std::string json(bool complet, bool value, bool detail) const = 0;
};
class Result : public ESObs {
protected:					// ajout error, nd, nl, np, measureRate, samplingRate
	int nDatUse;	// à supprimer
	int nLocUse;	// à supprimer
public:
	int nEch;
	int dim;
	static const std::string ESclass;
	Result();
	Result(Observation* pObs);
	void init();
	void majindexRes(int nRes, int nPrp, int nDat, int nLoc, int nEch); // à déplcaer
	void majIndic(int ech, int dimension, int datU, int locU);  // à supprimer
	virtual std::string json(bool complet, bool value, bool detail) const = 0;
	virtual int getMaxIndex() = 0;
	virtual std::array<int, 4> indicateur() const = 0; // à supprimer
	int getnEch() const;
	int getnDatU() const;
	int getnLocU() const;
	int getdim() const;
};
class Datation : public ESObs {
protected:
	TimeValue boxMin;
	TimeValue boxMax;
public:
	static const std::string ESclass;
	Datation();
	Datation(Observation* pObs);
	void init();
	virtual std::string json(bool complet, bool value, bool detail) const = 0;
	TimeValue getboxMin() const;
	TimeValue getboxMax() const;
};
template <typename Value, typename ObsClass>
class ESSet : public ObsClass {
protected:
	std::vector<Value> valueList;
public:
	ESSet() : ObsClass(nullptr) { init(); }
	ESSet(Observation* pObs) : ObsClass(pObs) { init(); }
	ESSet(Observation* pObs, JsonObject obj) : ObsClass(pObs) {
		init();
		for (JsonPair p : obj) if (ESElement::isESAtt("\"" + ObsClass::ESclass + "\"", (std::string)p.key().c_str())) ObsClass::setAtt((std::string)p.key().c_str(), p.value());
		for (JsonPair p : obj) if ((std::string)p.key().c_str() == Value::valueName) {
			if (p.value().is<JsonArray>()) {
				JsonArray arr = p.value().as<JsonArray>();
				for (int i = 0; i < (int)arr.size(); i++) addJsonValue(arr[i]);
			}
			else addJsonValue(p.value());
		}
	}
	void init() { ObsClass::typeES = "set"; ObsClass::mAtt["type"] = Value::valueType; }
	int getMaxIndex() {
		int maxInd = -1;
		for (int i = 0; i < size(); i++) maxInd = max(max(max(maxInd, valueList[i].getindexRes().idat), valueList[i].getindexRes().iloc), valueList[i].getindexRes().iprop);
		return maxInd;
	}
	void analyse() {
		if (ObsClass::ESclass == Datation::ESclass or ObsClass::ESclass == Location::ESclass) {
			if (valueList.size() < 1) { ObsClass::boxMax = Value(); ObsClass::boxMin = Value(); }
			else {
				Value minimum(valueList[0]);
				Value maximum(valueList[0]);
				for (int i = 1; i < (int)valueList.size(); i++) { minimum = Value::mini(valueList[i], minimum); maximum = Value::maxi(valueList[i], maximum); }
				ObsClass::boxMax = maximum; ObsClass::boxMin = minimum;
				ObsClass::mAtt["BoxMin"] = ObsClass::boxMin.json(1, 1);
				ObsClass::mAtt["BoxMax"] = ObsClass::boxMax.json(1, 1);
			}
		}
		else if (ObsClass::ESclass == Result::ESclass) { int i = 0; }
	}
	static bool isESSet(JsonObject obj) {
		bool esSet = 0;
		for (JsonPair p : obj) if (ESElement::isESAtt("\"" + ObsClass::ESclass + "\"", (std::string)p.key().c_str())) esSet = 1; //cout << "is1 : " << (std::string)p.key().c_str() << endl;}
		for (JsonPair p : obj) if ((std::string)p.key().c_str() == Value::valueName)  esSet = 1; //cout << "is2 : " << Value::jsonName << endl;	}
		return esSet;
	}
	void addJsonValue(JsonVariant jsonValue) { addValue(Value(jsonValue)); }
	int addValue(Value value) {
		for (int i = 0; i < (int)valueList.size(); i++) if (valueList[i] == value) return i;
		valueList.push_back(value);
		ObsClass::setNvalue(valueList.size());
		if (ObsClass::getNvalue() > 1) ObsClass::mAtt["type"] = "Multi" + Value::valueType;
		ESElement::majMeta();
		return valueList.size() - 1;
	}
	int size() const { return valueList.size(); }
	Value&	operator[](int num) { return valueList[num]; }
	Value	operator[](int num) const { return valueList[num]; }
	std::string jsonSet(bool detail) const {
		std::string json = "";
		if (valueList.size() == 1) json += valueList[0].json(1, detail);
		else if (valueList.size() > 1) {
			json += "[";
			for (int i = 0; i < (int)valueList.size(); i++) json += valueList[i].json(0, detail) + ",";
			json.pop_back();
			json += "]";
		}
		return json;
	}
	std::string json(bool complet, bool value, bool detail) const {
		std::string json("");
		if (ObsClass::getNvalue() == 0) return "";
		if (complet) json = "\"" + ObsClass::ESclass + "\":{";
		json += ESElement::jsonAtt(complet) + "\"" + Value::valueName + "\":" + jsonSet(detail) + ",";
		if (json.back() == ',') json.pop_back();
		if (complet) json += '}';
		return json;
	}
	void print() const { ESElement::print(); ESElement::println("\"" + Value::valueName + "\"", jsonSet(1)); }
	std::array<int, 4> indicateur() const {
		std::array<int, 4> indic;
		int nEch(0), nEchDat(0), nEchLoc(0), maxi(0), dim(0);
		int iProp(0), iDat(0), iLoc(0), nDat(0), nLoc(0);
		bool trouve = 0;
		if (valueList.size() < 1) return { 0, 0, 0, 0 };
		for (int i = 0; i < (int)valueList.size(); i++) {
			iProp = max(iProp, valueList[i].getindexRes().iprop);
			iDat = max(iDat, valueList[i].getindexRes().idat);
			iLoc = max(iLoc, valueList[i].getindexRes().iloc);
		}
		for (int id = 0; id < iDat + 1; id++) {
			maxi = 0;
			for (int il = 0; il < iLoc + 1; il++) {
				trouve = 0;
				for (int i = 0; i < (int)valueList.size(); i++)
					if (!trouve and valueList[i].getindexRes().idat == id and valueList[i].getindexRes().iloc == il) { trouve = 1; nEch++; maxi++; }
			}
			if (trouve) nDat++;
			nEchDat = max(nEchDat, maxi);
		}
		for (int il = 0; il < iLoc + 1; il++) {
			maxi = 0;
			for (int id = 0; id < iDat + 1; id++) {
				trouve = 0;
				for (int i = 0; i < (int)valueList.size(); i++)
					if (!trouve and valueList[i].getindexRes().idat == id and valueList[i].getindexRes().iloc == il) { trouve = 1; maxi++; }
			}
			if (trouve) nLoc++;
			nEchLoc = max(nEchLoc, maxi);
		}
		if (nEch > 1) {
			if (nEchLoc < 2 or nEchDat < 2) dim = 1;
			else dim = 2;
		}
		indic[0] = nEch;
		indic[1] = dim;
		indic[2] = nDat;
		indic[3] = nLoc;
		return indic;
	}
};

#endif