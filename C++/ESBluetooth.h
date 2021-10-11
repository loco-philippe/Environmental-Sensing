#pragma once
#ifndef BLUEES_
#define BLUEES_
#include <iostream> // à supprimer arduino
#include <vector>
#include <map>
#include <string>

struct value290C {
	uint16_t  flags;
	uint8_t   sampling;
	uint32_t  period;   // uint24_t
	uint16_t  interval; // uint24_t
	uint8_t   application;
	uint8_t   uncertainty;
	//}  __attribute__((packed));
};

struct value2906 {
	uint16_t  lowerValue;
	uint16_t  upperValue;
//}  __attribute__((packed));
};

struct BLEpropertyValue {
	std::string	propertyId;
	std::string	sensorType;
	std::string	propertyType;
	float	lowerValue;
	float	upperValue;
	std::string	unit;
	std::string	samplingFunction;
	int		period;
	int		updateInterval;
	int		uncertainty;
	std::string	application;
};
struct BLEresultValue {
	float	value;
};
class BLEdescriptor {
public:
	BLEdescriptor(std::string uuid);
	void setValue(std::string val);
	void setValue(uint32_t* val, size_t len);
};
class BLECharacteristic {
public:
	BLEdescriptor * addDescriptor(BLEdescriptor*);
	void setValue(uint32_t* val, size_t len);
};
class BLEservice {
public:
	BLECharacteristic * createCharacteristic(std::string uuid, int num);
};

class BLEClient {
public:
	//BLEClient * createService(std::string uuid);
};
class BLEserver {
public:
	BLEservice * createService(std::string uuid);
};
class ESBluetooth {
public:
	std::string	UUID;
	std::string	unit;
	std::string	propertyId;
	std::string	sensorType;
	std::string	propertyType;
	float	lowerValue;
	float	upperValue;
	std::string	samplingFunction;
	int		period;
	int		updateInterval;
	int		uncertainty;
	std::string	application;
	float	value;
	bool meas;
	bool user;
	bool range;
	BLEserver*			pServer;
	BLEservice*			pServic;
	BLECharacteristic*	pCharac;
	BLEdescriptor*		pMeasurement;
	BLEdescriptor*		pCharUser;
	BLEdescriptor*		pValidRange;
public:
	ESBluetooth(std::string esUUID, BLEserver * pserver, bool measurement, bool charUser, bool validRange);
	void serverBLEService();
	void setPropValue();		//serveur
	void setResultValue();		//serveur

	void clientBLEService();
	void getPropValue();		//client
	void getResultValue();		//client

	uint32_t	setValueESS();
	void		getValueESS(float val);
	value2906   setValue2906();
	void		getValue2906(value2906 val);
	value290C   setValue290C();
	void		getValue290C(value290C val);
	std::string	setValue2901();
	void		getValue2901(std::string val);


};




#endif