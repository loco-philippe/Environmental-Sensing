#include "stdafx.h"
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
	{ "mean", 0 }
};
std::map<std::string, int> codeApplication = {
	{ "air", 0 }
};
BLEservice* BLEserver::createService(std::string uuid) { cout << "creation sce" << endl; return nullptr;};
BLECharacteristic* BLEservice::createCharacteristic(std::string uuid, int num) { cout << "  creation char " << uuid << endl; return nullptr; };
BLEdescriptor* BLECharacteristic::addDescriptor(BLEdescriptor* pdesc) { cout << "    ajout desc " << endl; return nullptr; };

BLEdescriptor::BLEdescriptor(std::string uuid) { cout << "    creation desc " << uuid << endl; };
void BLEdescriptor::setValue(std::string val) { cout << "set value desc string : " << val << endl; };
void BLEdescriptor::setValue(uint32_t* val, size_t len) { cout << "set value desc packed : " << val << "    " << len << endl; };
void BLECharacteristic::setValue(uint32_t* val, size_t len) { cout << "set value packed charac : " << val << "    " << len << endl; };


//ESBluetooth::ESBluetooth() { /*UUID = "test";*/ };
ESBluetooth::ESBluetooth(std::string esUUID, BLEserver * pserver, bool measurement, bool charUser, bool validRange) {
	UUID = esUUID;
	unit = unitUUID[esUUID];
	propertyId = "null";
	sensorType = "null";
	propertyType = propUUID[esUUID];
	lowerValue = 0 ;
	upperValue = 0;
	samplingFunction = "null";
	period = 0;
	updateInterval = 0 ;
	uncertainty = 0;
	application = "null";
	value = 0;
	meas = measurement;
	user = charUser;
	range = validRange;
	pServer = pserver;
	pServic = nullptr;
	pCharac = nullptr;
	pMeasurement = nullptr;
	pCharUser = nullptr;
	pValidRange = nullptr;
};
void ESBluetooth::serverBLEService() {
	pServic = pServer->createService("181a"); 
	pCharac = pServic->createCharacteristic(UUID, 0);
	if (meas) pMeasurement = pCharac->addDescriptor(new BLEdescriptor("290C"));
	if (user) pCharUser = pCharac->addDescriptor(new BLEdescriptor("2901"));
	if (range) pValidRange = pCharac->addDescriptor(new BLEdescriptor("2906"));
};
void ESBluetooth::setPropValue() {
	if (user) pCharUser->setValue(setValue2901());
	value2906 validRange = setValue2906();
	if (range) pValidRange->setValue((uint32_t*)&validRange, sizeof(validRange));
	value290C measurement = setValue290C();
	if (meas) pMeasurement->setValue((uint32_t*)&measurement, sizeof(measurement));
};
void ESBluetooth::setResultValue() {
	uint32_t valESS = setValueESS();
	pCharac->setValue((uint32_t*)&valESS, sizeof(valESS));
};
void ESBluetooth::clientBLEService() {
	BLERemoteService* pRemoteService = pClient->getService("181a");
	BLERemoteCharacteristic* pRemoteCharacteristic = pRemoteService->getCharacteristic(UUID);
	pRemoteMeasurement = pRemoteCharacteristic->getDescriptor("290C");
	pRemoteValidRange = pRemoteCharacteristic->getDescriptor("2906");
	pRemoteCharUser = pRemoteCharacteristic->getDescriptor("2901");

};
void ESBluetooth::getPropValue() {};		//client
void ESBluetooth::getResultValue() {};		//client

uint32_t	ESBluetooth::setValueESS() { return (uint32_t)value; };
void		ESBluetooth::getValueESS(float val) { value = val; };
value290C	ESBluetooth::setValue290C() {
	value290C val = { 0,0,0,0,0,0 };
	val.flags = 0;
	val.sampling =		(uint8_t)	codeSampling[samplingFunction];
	val.period =		(uint32_t)	period; // uint24_t
	val.interval =		(uint16_t)	updateInterval;  // uint24_t
	val.application =	(uint8_t)	codeApplication[application];
	val.uncertainty =	(uint8_t)	uncertainty;
	return val;
}
;
void		ESBluetooth::getValue290C(value290C val) {};

std::string	ESBluetooth::setValue2901() {	return	propertyId;	}
void		ESBluetooth::getValue2901(std::string val) { propertyId = val; }
value2906   ESBluetooth::setValue2906() {
	int exponent = 0;
	value2906 val = { 0,0 };
	val.lowerValue = (uint16_t)lowerValue / pow(10, exponent);
	val.upperValue = (uint16_t)upperValue / pow(10, exponent);
	return val;
}
void		ESBluetooth::getValue2906(value2906 val) {
	int exponent = 0;
	lowerValue = (float)val.lowerValue * pow(10, exponent);
	upperValue = (float)val.upperValue * pow(10, exponent);
}



/*void ESBluetooth::setPropValue(BLEpropertyValue prop) {
	propertyId = prop.propertyId;
	sensorType = prop.sensorType;
	lowerValue = prop.lowerValue;
	upperValue = prop.upperValue;
	samplingFunction = prop.samplingFunction;
	period = prop.period;
	updateInterval = prop.updateInterval;
	uncertainty = prop.uncertainty;
	application = prop.application;
};*/
/*BLEpropertyValue ESBluetoot::getProperty() {
};
BLEresultValue ESBluetoot::getResult() {
};*/
//BLEservice::BLEservice() { truc = 0; };

