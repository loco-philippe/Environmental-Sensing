#ifdef TEST_ES
	//#pragma once
	#include <iostream> // à supprimer arduino
#endif
#ifndef BLE_
#define BLE_
#include <vector>
#include <map>
#include <string>

class BLEDescriptor {
public:
	BLEDescriptor(std::string uuid);
	void setValue(std::string val);
	void setValue(uint8_t* val, size_t len);
};
class BLECharacteristic {
public:
	static const int PROPERTY_READ = 1;
	void addDescriptor(BLEDescriptor*);
	void setValue(uint8_t* val, size_t len);
};
class BLEService {
public:
	BLECharacteristic * createCharacteristic(std::string uuid, int num);
};
class BLEServer {
public:
	BLEService * createService(std::string uuid);
};
class BLERemoteDescriptor {
public:
	BLERemoteDescriptor(std::string uuid);
	std::string readValue();
};
class BLERemoteCharacteristic {
public:
	BLERemoteDescriptor * getDescriptor(std::string uuid);
	std::string readValue();
};
class BLERemoteService {
public:
	BLERemoteCharacteristic * getCharacteristic(std::string uuid);
	std::string readValue();
};
class BLEclient {
public:
	BLERemoteService * getService(std::string uuid);
	void disconnect();
};

#endif