#pragma once		// à supprimer arduino
#ifndef ESCOMPO_
#define ESCOMPO_
//#include <iostream>   // à ajouter arduino ??
#include <string>
#include <vector>
#include "ArduinoJson.h"
#include <time.h>
#include "DTime.h"
#include "ESElement.h"
#include <sstream>

class ESValue {
protected:
	//std::string valueName;
	//std::string valueType;
public:
	virtual std::string json(bool unique, bool detail) const = 0;
};
class LocationValue : public ESValue {
protected:
	float coor[3];
	bool geod; // 1 : WGS, 0 : projection
	bool carto; // 1 : lon lat / X Y, 0 : lat lon / Y X
public:
	//static const std::string EStype;
	static const std::string valueType;
	static const std::string valueName;
	LocationValue(float coord[], bool geo, bool cart);
	LocationValue(float coord[]);
	LocationValue(float coor1, float coor2);
	LocationValue(JsonVariant locv);
	LocationValue();
	LocationValue(LocationValue const&  locv);
	LocationValue& operator=(LocationValue const&  locv);
	bool operator==(LocationValue const&  locv);
	void init(float coord[], bool geo, bool cart);
	void setCoor(float coord[]);
	float getLat() const;
	float getLon() const;
	float getX() const;
	float getY() const;
	std::string json(bool unique, bool detail) const;
	static LocationValue maxi(LocationValue x, LocationValue y);
	static LocationValue mini(LocationValue x, LocationValue y);
};
class ESIndexValue : public ESValue {
protected:
	indexRes ind;
public:
	ESIndexValue(indexRes in);
	void setindexRes(indexRes in);
	indexRes getindexRes() const;
};

template <typename RValue>
class ResultValue : public ESIndexValue {
protected:
	//indexRes ind;
	RValue value;
public:
	//static const std::string EStype; 
	static const std::string valueName;
	static const std::string valueType; 
public:
	ResultValue() : ESIndexValue({ -1, -1, -1 }) { value.initValue(); }
	ResultValue(RValue val) : ESIndexValue({ -1, -1, -1 }) { value = val; }
	ResultValue(RValue val, indexRes in) : ESIndexValue(in) { setValue(val);}
	ResultValue(JsonVariant val) : ESIndexValue({ -1, -1, -1 }) {
		if (val.is<JsonArray>()) {
			JsonArray arr = val.as<JsonArray>();
			JsonVariant val2 = arr[0];
			setValue(RValue(val2));
			JsonArray ind = arr[1].as<JsonArray>();
			setindexRes({ ind[0], ind[1], ind[2] });
		}
		else {
			setValue(RValue(val));
			setindexRes({ -1, -1, -1 });
		}
		//cout << "resval (d,l,p) : " << value << " " << ind.idat << " " << ind.iloc << " " << ind.iprop << endl;
	}
	void init() { value.initValue(); setindexRes({ -1, -1, -1 }); }
	bool operator==(ResultValue const&  r) { return (value == r.value); }
	void setValue(RValue val) { value = val; }
	RValue getValue() const { return value; }
	std::string json(bool unique, bool res_index) const {
		//cout << " value indexRes id il ip : " << value << " " << ind.idat << " " << ind.iloc << " " << ind.iprop << endl;
		std::stringstream ss;
		if (res_index)	ss << "[" << value.json() << ", [" << ind.idat << ", " << ind.iloc << ", " << ind.iprop << "]]";
		else 			ss << value.json();
		return ss.str();
	}
};
//template <typename RValue> const std::string ResultValue<RValue>::EStype	(RValue::EStype);
template <typename RValue> const std::string ResultValue<RValue>::valueName	(RValue::valueName);
template <typename RValue> const std::string ResultValue<RValue>::valueType		(RValue::valueType);

class StringValue {
protected:
	std::string value;
public:
	//static const std::string EStype;
	static const std::string valueType;
	static const std::string valueName;
	StringValue();
	StringValue(std::string val);
	StringValue(JsonVariant val);
	StringValue initValue();
	bool operator==(StringValue const&  res);
	std::string json() const;
};
class RealValue {
protected:
	float value;
public:
	//static const std::string EStype;
	static const std::string valueType;
	static const std::string valueName;
	RealValue();
	RealValue(float val);
	RealValue(JsonVariant val);
	RealValue initValue();
	bool operator==(RealValue const&  res);
	std::string json() const;
};
class IntValue {
protected:
	int value;
public:
	//static const std::string EStype;
	static const std::string valueType;
	static const std::string valueName;
	IntValue();
	IntValue(int val);
	IntValue(JsonVariant val);
	IntValue initValue();
	bool operator==(IntValue const&  res);
	std::string json() const;
};
class TimeValue : public ESValue {
protected:
	DTime dtVal;
public:
	static const std::string EStype;
	static const std::string valueType;
	static const std::string valueName;
	TimeValue();
	TimeValue(int y, int m, int d, int h, int mn, int s);
	TimeValue(JsonVariant tim);
	TimeValue(std::string tim);
	TimeValue(DTime tim);
	bool operator==(TimeValue const&  time);
	void setValue(std::string tim);
	time_t getValue() const;
	std::string json(bool unique, bool res_index) const;
	static TimeValue maxi(TimeValue x, TimeValue y);
	static TimeValue mini(TimeValue x, TimeValue y);
};
class PropertyValue : public ESValue {
protected:
	std::string EMFId;
	std::string propertyType;
	std::string unit;
	std::string sampling;
	std::string application;
	ObservingEMF* pContexte;
public:
	//static const std::string EStype;
	static const std::string valueType;
	static const std::string valueName;
	static const std::string propTypeN;
	static const std::string unitN;
	static const std::string samplingN;
	static const std::string appliN;
	static const std::string EMFIdN;
	PropertyValue();
	PropertyValue(std::string propType, std::string unite, std::string sampl, std::string appli, std::string EMF);
	PropertyValue(std::string propType, std::string unite, std::string EMF);
	PropertyValue(std::string propType, std::string unite);
	PropertyValue(JsonVariant jsonObsProp);
	bool operator==(PropertyValue const&  prop);
	void init(std::string propType, std::string unite, std::string sampl, std::string appli, std::string EMF );
	void linkContext(ObservingEMF* pObservingEMF);
	void setEMFId(std::string EMF);
	std::string json(bool unique, bool res_index) const;
};

#endif	
