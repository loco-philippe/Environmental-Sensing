#include "stdafx.h"
#include "BLE.h"

using namespace std;

BLEService* BLEServer::createService(std::string uuid) { cout << "creation sce" << endl; return nullptr; };
BLECharacteristic* BLEService::createCharacteristic(std::string uuid, int num) { cout << "  creation char " << uuid << endl; return nullptr; };
void BLECharacteristic::addDescriptor(BLEDescriptor* pdesc) { cout << "    ajout desc " << endl; };
BLEDescriptor::BLEDescriptor(std::string uuid) { cout << "    creation desc " << uuid << endl; };
void BLEDescriptor::setValue(std::string val) { cout << "set value desc string : " << val << endl; };
void BLEDescriptor::setValue(uint8_t* val, size_t len) { cout << "set value desc packed : " << val << "    " << len << endl; };
void BLECharacteristic::setValue(uint8_t* val, size_t len) { cout << "set value packed charac : " << val << "    " << len << endl; };
void BLEclient::disconnect() {};
BLERemoteService * BLEclient::getService(std::string uuid) { cout << "creation remote sce" << endl; return nullptr; };
BLERemoteCharacteristic * BLERemoteService::getCharacteristic(std::string uuid) { cout << "  creation remote char " << uuid << endl; return nullptr; };
BLERemoteDescriptor::BLERemoteDescriptor(std::string uuid) { cout << "    creation remote desc " << uuid << endl; };
BLERemoteDescriptor * BLERemoteCharacteristic::getDescriptor(std::string uuid) { cout << "    ajout remote desc " << uuid << endl; return nullptr; };
std::string BLERemoteDescriptor::readValue() { cout << "read value desc string : " << endl; return "readvaluedesc"; };
std::string BLERemoteCharacteristic::readValue() { cout << "read value char string : " << endl; return "readvaluechar"; };
std::string BLERemoteService::readValue() { cout << "read value serv string : " << endl; return "readvalueserv"; };