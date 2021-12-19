#ifndef BLUEES_
#define BLUEES_
#ifdef TEST_ES
	//#pragma once		// à supprimer arduino
	#include <iostream> // à supprimer arduino
#endif
#include <vector>
#include <map>
#include <string>
#ifdef TEST_ES
	#include "BLE.h"	// à remplacer arduino lignes suivantes
#endif
#ifndef TEST_ES
	#include <BLEDevice.h>
	#include <BLEUtils.h>
	#include <BLEServer.h>
#endif
const std::string Umeas("290C");
const std::string Uuser("2901");
const std::string Urange("2906");

struct value290C {
	uint16_t  flags;
	uint8_t   sampling;
	uint32_t  period;   // uint24_t
	uint16_t  interval; // uint24_t
	uint8_t   application;
	uint8_t   uncertainty;
}
#ifndef TEST_ES
	  __attribute__((packed))	// à ajouter arduino
#endif
;
struct value2906 {
	uint16_t  lowerValue;
	uint16_t  upperValue;
}
#ifndef TEST_ES
__attribute__((packed))	// à ajouter arduino
#endif
;
struct BLEpropertyValue {
	std::string	propertyId;
	std::string	sensorType;
	std::string	propertyType;
	float		lowerValue;
	float		upperValue;
	std::string	unit;
	std::string	samplingFunction;
	int			period;
	int			updateInterval;
	int			uncertainty;
	std::string	application;
};
struct BLEresultValue {
	float	value;
};
struct ESserverCharac {
	bool meas;
	bool user;
	bool range;
	std::string uuid;
	BLECharacteristic*	pCharac;
	BLEDescriptor*		pMeasurement;
	BLEDescriptor*		pCharUser;
	BLEDescriptor*		pValidRange;
	ESserverCharac(BLEService* pServic, std::string UUID) {
		uuid = UUID;
		pCharac = pServic->createCharacteristic(uuid, BLECharacteristic::PROPERTY_READ);
		meas = 1;
		user = 1;
		range = 1;
		pMeasurement = new BLEDescriptor(Umeas);
		pCharUser = new BLEDescriptor(Uuser);
		pValidRange = new BLEDescriptor(Urange);
	}
};
struct ESclientCharac {
	bool charac = 0;
	bool meas = 1;
	bool user  = 1;
	bool range = 1;
	std::string uuid;
	BLERemoteCharacteristic*	pRemoteCharac;
	BLERemoteDescriptor*		pMeasurement;
	BLERemoteDescriptor*		pCharUser;
	BLERemoteDescriptor*		pValidRange;
	ESclientCharac(BLERemoteService* pRemoteServic, std::string charUUID) {
		uuid = charUUID;
		pRemoteCharac = pRemoteServic->getCharacteristic(charUUID);
#ifndef TEST_ES
		charac = pRemoteCharac != nullptr;
#else
		charac = 1;		//à enlever
#endif
		if (charac) {
			pMeasurement= pRemoteCharac->getDescriptor(Umeas); meas  = pMeasurement	!= nullptr;
			pCharUser	= pRemoteCharac->getDescriptor(Uuser); user  = pCharUser	!= nullptr;
			pValidRange = pRemoteCharac->getDescriptor(Urange); range = pCharUser	!= nullptr;
		};
	}
};
class ESBluetooth {
public:
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
public:
	ESBluetooth();
	ESBluetooth(std::string uuid);
	void setPropValue(ESserverCharac *pcharac);		//serveur
	void setResultValue(ESserverCharac *pcharac);		//serveur

	void getPropValue(ESclientCharac *pcharac);		//client
	void getResultValue(ESclientCharac *pcharac);		//client

	uint32_t	setValueESS();
	void		getValueESS(std::string val);
	value2906   setValue2906();
	void		getValue2906(std::string val);
	value290C   setValue290C();
	void		getValue290C(std::string val);
	std::string	setValue2901();
	void		getValue2901(std::string val);

};

#endif