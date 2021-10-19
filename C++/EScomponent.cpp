#include "stdafx.h"    // à supprimer arduino
#include <algorithm>
#include "EScomponent.h"
#ifndef TEST_ES
	//#include <sstream>  // à ajouter arduino ??
#endif
using namespace std;

const std::string LocationValue::valueType	= "Point";
const std::string LocationValue::valueName	= "coordinates";
const std::string StringValue::valueType	= "string";
const std::string StringValue::valueName	= "strValue";
const std::string RealValue::valueType		= "real";
const std::string RealValue::valueName		= "realValue";
const std::string IntValue::valueType		= "int";
const std::string IntValue::valueName		= "intValue";
const std::string TimeValue::valueType		= "instant";
const std::string TimeValue::valueName		= "dateTime";
const std::string PropertyValue::valueType	= "list";
const std::string PropertyValue::valueName	= "propertyList";

const std::string PropertyValue::propTypeN	= "property";
const std::string PropertyValue::unitN		= "unit";
const std::string PropertyValue::samplingN	= "sampling";
const std::string PropertyValue::appliN		= "application";
const std::string PropertyValue::EMFIdN		= "EMFId";

ESIndexValue::ESIndexValue(indexRes in) { setindexRes(in); }
void ESIndexValue::setindexRes(indexRes in) { ind = in; }
indexRes ESIndexValue::getindexRes() const { return ind; }

StringValue::StringValue() { value = "null"; }
StringValue::StringValue(std::string val) { value = val; }
StringValue::StringValue(JsonVariant val) { value = val.as<string>(); }
StringValue StringValue::initValue() { return StringValue("null"); }
bool StringValue::operator==(StringValue const&  r) { return (value == r.value); }
std::string StringValue::json() const { if (value[0] == '{') return value; else return "\"" + value + "\""; }

RealValue::RealValue() { value = 0; }
RealValue::RealValue(float val) { value = val; }
RealValue::RealValue(JsonVariant val) { value = val.as<float>(); }
RealValue RealValue::initValue() { return RealValue(0); }
bool RealValue::operator==(RealValue const&  r) { return (value == r.value); }
std::string RealValue::json() const { stringstream ss; ss << value;	return ss.str(); }

IntValue::IntValue() { value = 0; }
IntValue::IntValue(int val) { value = val; }
IntValue::IntValue(JsonVariant val) { value = val.as<int>(); }
IntValue IntValue::initValue() { return IntValue(0); }
bool IntValue::operator==(IntValue const&  r) { return (value == r.value); }
std::string IntValue::json() const { stringstream ss; ss << value;	return ss.str(); }

LocationValue::LocationValue(float coord[], bool geo, bool cart) { init(coord, geo, cart); }
LocationValue::LocationValue(float coord[]) { init(coord, 1, 1); }
LocationValue::LocationValue(float coor1, float coor2) { float coord[3] = { 0,0,0, }; coord[0] = coor1; coord[1] = coor2; init(coord, 1, 1); }
LocationValue::LocationValue(JsonVariant locv) {
	JsonArray arr = locv.as<JsonArray>();
	float loc[3] = { arr[0], arr[1], arr[2] };
	init(loc, 1, 1); }
LocationValue::LocationValue() { float loc[3] = { -1, -1, -1 }; init(loc, 1, 1); }
LocationValue::LocationValue(LocationValue const&  c)				{ coor[0] = c.coor[0]; coor[1] = c.coor[1]; coor[2] = c.coor[2]; geod = c.geod; carto = c.carto; }
LocationValue& LocationValue::operator=(LocationValue const& c)	{ coor[0] = c.coor[0]; coor[1] = c.coor[1]; coor[2] = c.coor[2];  geod = c.geod; carto = c.carto; return *this; }
bool LocationValue::operator==(LocationValue const&  c)			{return (coor[0] == c.coor[0] && coor[1] == c.coor[1] && coor[2] == c.coor[2] && geod == c.geod && carto == c.carto); }
void LocationValue::init(float coord[], bool geo, bool cart) { coor[0] = coord[0]; coor[1] = coord[1]; coor[2] = coord[2]; geod = geo; carto = cart; }
void LocationValue::setCoor(float coord[]) { coor[0] = coord[0]; coor[1] = coord[1]; coor[2] = coord[2]; }
float LocationValue::getLat()const							{ return coor[1] * geod * carto + coor[0] * geod * (1 - carto) + geod - 1; }
float LocationValue::getLon()const							{ return coor[0] * geod * carto + coor[1] * geod * (1 - carto) + geod - 1; }
float LocationValue::getX()const								{ return coor[0] * (1 - geod) * carto + coor[1] * (1 - geod) * (1 - carto) - geod; }
float LocationValue::getY()const								{ return coor[1] * (1 - geod) * carto + coor[0] * (1 - geod) * (1 - carto) - geod; }
std::string LocationValue::json(bool unique, bool res_index) const {
	stringstream ss;
	if (coor[0] > 0 and coor[1] > 0) ss << "[" << coor[0] << ", " << coor[1] << "]";
	else ss << "";
	return ss.str();
}
LocationValue LocationValue::maxi(LocationValue x, LocationValue y) {
	float loc0[3] = { 0.f, 0.f, 0.f };
	LocationValue max(loc0, x.geod, x.carto);
	max.coor[0] = std::max(x.coor[0], y.coor[0]);
	max.coor[1] = std::max(x.coor[1], y.coor[1]);
	max.coor[2] = std::max(x.coor[2], y.coor[2]);
	return max;
}
LocationValue LocationValue::mini(LocationValue x, LocationValue y) {
	float loc0[3] = { 0.f, 0.f, 0.f };
	LocationValue min(loc0, x.geod, x.carto);
	min.coor[0] = std::min(x.coor[0], y.coor[0]);
	min.coor[1] = std::min(x.coor[1], y.coor[1]);
	min.coor[2] = std::min(x.coor[2], y.coor[2]);
	return min;
}
TimeValue::TimeValue() { setValue("null"); }
TimeValue::TimeValue(std::string tim) { setValue(tim); }
TimeValue::TimeValue(int y, int m, int d, int h, int mn, int s) { dtVal = DTime(y, m, d, h, mn, s); }
TimeValue::TimeValue(DTime tim) { dtVal = tim; }
TimeValue::TimeValue(JsonVariant tim){ setValue(tim.as<std::string>()); }
bool TimeValue::operator==(TimeValue const&  t) { return (getValue() == t.getValue()); }
void TimeValue::setValue(std::string tim) {
	std::string date = "null", timest = "null", millis = "null";
	int y(1970), m(01), d(01), h(00), mn(00), s(0);
	int nT(tim.find("T")), nPoint(tim.find("."));
	if (nT > 0) {
		date = tim.substr(0, nT);
		if (nPoint > 0)	timest = tim.substr(nT).substr(1, nPoint);
		else timest = tim.substr(nT + 1);
		if (nPoint > 0)	millis = tim.substr(nPoint + 1);
	}
	if (date.length() > 1) {
		int nT1(date.find("-")), nT2(-1);
		if (nT1 > 0) {
			nT2 = date.substr(nT1 + 1).find("-");
			stringstream day(date.substr(0, nT1));
			day >> d;
			if (nT2 > 0) {
				stringstream month(date.substr(nT1).substr(1, nT2));
				month >> m;
				stringstream year(date.substr(nT1 + nT2 + 2));
				year >> y;
			}
			else {
				stringstream month(date.substr(nT1 + 1));
				month >> m;
			}
		}
	}
	if (timest.length() > 1) {
		int nT1(timest.find(":")), nT2(-1);
		if (nT1 > 0) {
			nT2 = timest.substr(nT1 + 1).find(":");
			stringstream hour(timest.substr(0, nT1));
			hour >> h;
			if (nT2 > 0) {
				stringstream minute(timest.substr(nT1).substr(1, nT2));
				minute >> mn;
				stringstream second(timest.substr(nT1 + nT2 + 2));
				second >> s;
			}
			else {
				stringstream minute(timest.substr(nT1 + 1));
				minute >> mn;
			}
		}
	}
	dtVal = DTime(y, m, d, h, mn, s);
}
time_t TimeValue::getValue()const { return dtVal.timestamp; }
std::string TimeValue::json(bool unique, bool res_index) const {
	if (dtVal.timestamp < 0) return " ";
	stringstream ss;
	ss << "\"" << dtVal.day << "-" << dtVal.month << "-" << dtVal.year << "T" << dtVal.hour << ":" << dtVal.minute << ":" << dtVal.second << "\"";
	return ss.str();
}
TimeValue TimeValue::maxi(TimeValue x, TimeValue y) {
	TimeValue max = x;
	if (y.dtVal.timestamp > x.dtVal.timestamp) max = y;
	return max;
}
TimeValue TimeValue::mini(TimeValue x, TimeValue y) {
	TimeValue min = x;
	if ((y.dtVal.timestamp < x.dtVal.timestamp and y.dtVal.timestamp > 0) or x.dtVal.timestamp < 0) min = y;
	return min;
}

PropertyValue::PropertyValue() { init("null", "null", "null", "null", "null");}
PropertyValue::PropertyValue(std::string propType, std::string unite, std::string sampl, std::string appli, std::string EMF){ init(propType, unite, sampl, appli, EMF); }
PropertyValue::PropertyValue(std::string propType, std::string unite, std::string EMF) { init(propType, unite, "null", "null", EMF); }
PropertyValue::PropertyValue(std::string propType, std::string unite) { init(propType, unite, "null", "null", "null"); }
PropertyValue::PropertyValue(JsonVariant jsonVarObsProp) {
	init("null", "null", "null", "null", "null"); 
	JsonObject jsonObsProp = jsonVarObsProp.as<JsonObject>();
	for (JsonPair p : jsonObsProp) {
		string att = (string)p.key().c_str();
		string val = p.value();
		if (att == propTypeN) propertyType = val;
		else if (att == unitN) unit = val;
		else if (att == samplingN) sampling = val;
		else if (att == appliN) application = val;
	}
}
void PropertyValue::init(std::string propType, std::string unite, std::string sampl, std::string appli, std::string EMF) {
	propertyType = propType; unit = unite; sampling = sampl; application = appli;  EMFId = EMF; pContexte = nullptr;
}
bool PropertyValue::operator==(PropertyValue const&  p) { return (propertyType == p.propertyType && unit == p.unit && sampling == p.sampling && application == p.application && EMFId == p.EMFId); }
void PropertyValue::linkContext(ObservingEMF* pObservingEMF) { pContexte = pObservingEMF; }
void PropertyValue::setEMFId(std::string EMF) { EMFId = EMF; }
std::string PropertyValue::json(bool unique, bool res_index) const {
	std::string json = "";
	json += "{";
	if (propertyType != "null") json += "\"" + propTypeN + "\":\"" + propertyType + "\",";
	if (unit != "null") json += "\"" + unitN + "\":\"" + unit + "\",";
	if (sampling != "null") json += "\"" + samplingN + "\":\"" + sampling + "\",";
	if (application != "null") json += "\"" + appliN + "\":\"" + application + "\",";
	if (EMFId != "null") json += "\"" + EMFIdN + "\":\"" + EMFId + "\",";
	if (json != "{") json.pop_back();
	json += "}";
	return json;
}

