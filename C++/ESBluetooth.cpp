//#ifdef TEST_ES
	#include "stdafx.h"				// à supprimer àrduino
//#endif
#include "ESBluetooth.h"

using namespace std;

std::map<std::string, std::string> UUIDprop = {
	{ "PM1", "2BD5" },
{ "PM25", "2BD6" },
{ "PM10", "2BD7" }
};
std::map<std::string, std::string> propUUID = {
	{ "2BD5", "PM1" },
{ "2BD6", "PM25" },
{ "2BD7", "PM10" }
};
std::map<std::string, std::string> unitUUID = {
	{ "2BD5", "µg/m3" },
{ "2BD6", "µg/m36" },
{ "2BD7", "µg/m37" }
};
std::map<std::string, int> codeSampling = {
	{ "mean", 2 }
};
std::map<int, std::string> samplingCode = {
	{ 0, "mean" }
};
std::map<std::string, int> codeApplication = {
	{ "air", 0 }
};
std::map<int, std::string> applicationCode = {
	{ 0, "air" }
};
ESBluetooth::ESBluetooth() {};
ESBluetooth::ESBluetooth(std::string uuid) {
		unit = unitUUID[uuid];
	propertyId = "null";
	sensorType = "null";
	propertyType = propUUID[uuid];
	lowerValue = 0 ;
	upperValue = 0;
	samplingFunction = "null";
	period = 0;
	updateInterval = 0 ;
	uncertainty = 0;
	application = "null";
	value = 0;
};
void		ESBluetooth::setPropValue(ESserverCharac *pcharac) {
	if (pcharac->user) {
		pcharac->pCharUser->setValue(setValue2901());
		pcharac->pCharac->addDescriptor(pcharac->pCharUser);
	}
	value2906 validRange = setValue2906();
	if (pcharac->range) {
		pcharac->pValidRange->setValue((uint8_t*)&validRange, sizeof(validRange));
		pcharac->pCharac->addDescriptor(pcharac->pValidRange);
	}
	value290C measurement = setValue290C();
	if (pcharac->meas) {
		pcharac->pMeasurement->setValue((uint8_t*)&measurement, sizeof(measurement));
		pcharac->pCharac->addDescriptor(pcharac->pMeasurement);
	}
};
void		ESBluetooth::setResultValue(ESserverCharac *pcharac) {
	uint32_t valESS = setValueESS();
	pcharac->pCharac->setValue((uint8_t*)&valESS, sizeof(valESS));
};
void		ESBluetooth::getPropValue(ESclientCharac *pcharac) {		//client
	if (pcharac->user)  getValue2901(pcharac->pCharUser		->readValue());
	if (pcharac->range) getValue2906(pcharac->pValidRange	->readValue());
	if (pcharac->meas)  getValue290C(pcharac->pMeasurement	->readValue());
};	
void		ESBluetooth::getResultValue(ESclientCharac *pcharac) { getValueESS(pcharac->pRemoteCharac->readValue());};		//client
uint32_t	ESBluetooth::setValueESS() { return (uint32_t)value; };
void		ESBluetooth::getValueESS(std::string val) { value = (float)(*(uint32_t*)val.substr(0, 4).data()); };
value290C	ESBluetooth::setValue290C() {
	value290C val = { 0,0,0,0,0,0 };
	val.flags = 0;
	val.sampling =		(uint8_t)	codeSampling[samplingFunction];
	val.period =		(uint32_t)	period; // uint24_t
	val.interval =		(uint16_t)	updateInterval;  // uint24_t
	val.application =	(uint8_t)	codeApplication[application];
	val.uncertainty =	(uint8_t)	uncertainty;
	return val;
};
void		ESBluetooth::getValue290C(std::string val) {
	int sampling	= (int)(*(uint8_t*) val.substr(2,  1).data());
	int appli		= (int)(*(uint8_t*) val.substr(9,  1).data());
	period			= (int)(*(uint32_t*)val.substr(3,  4).data()); // uint24_t
	updateInterval	= (int)(*(uint16_t*)val.substr(7,  2).data());  // uint24_t
	uncertainty		= (int)(*(uint8_t*) val.substr(10, 1).data());
	samplingFunction= samplingCode[sampling];
	application		= applicationCode[appli];
};
std::string	ESBluetooth::setValue2901() {	return	propertyId;	}
void		ESBluetooth::getValue2901(std::string val) { propertyId = val; }
value2906   ESBluetooth::setValue2906() {
	int exponent = 0;
	value2906 val = { 0,0 };
	//val.lowerValue = (uint16_t)(lowerValue / pow(10, exponent));
	//val.upperValue = (uint16_t)(upperValue / pow(10, exponent));
	val.lowerValue = (uint16_t)lowerValue;
	val.upperValue = (uint16_t)upperValue;
	return val;
}
void		ESBluetooth::getValue2906(std::string val) {
	int exponent = 0;
	//lowerValue = (float)(*(uint16_t*)val.substr(0, 2).data()) * pow(10, exponent);
	//upperValue = (float)(*(uint16_t*)val.substr(2, 4).data()) * pow(10, exponent);
	lowerValue = (float)(*(uint16_t*)val.substr(0, 2).data()) ;
	upperValue = (float)(*(uint16_t*)val.substr(2, 4).data()) ;
}

