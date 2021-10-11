#pragma once
#ifndef EMFES_
#define EMFES_
//#include <iostream>
#include <string>
#include <vector>
#include <map>
#include "ArduinoJson.h"
#include "ESObservation.h"
#include "ESElement.h"

class MainEMF : public ESObject {
public:
	MainEMF();
	MainEMF(JsonObject obj);
	void init();
	void print();
	void majType();
	std::string json(bool complet, bool value, bool detail) const;
};

class ObservingEMF : public ESObject {
public:
	ObservingEMF();
	ObservingEMF(MainEMF* pEMF);
	ObservingEMF(MainEMF* pEMF, JsonObject obj);
	void init(MainEMF* pEMF);
	void majType();
	std::string json(bool complet, bool value, bool detail) const;
};

#endif