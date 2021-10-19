#pragma once		// à supprimer arduino
#ifndef JSONES_
#define JSONES_
#include <iostream> // à supprimer arduino
#include <string>
#include <vector>
#include <map>
#include <array>
#include "ArduinoJson.h"

struct nValObs {
	int nPrp;
	int nDat;
	int nLoc;
	int nEch;
	int nRes;
};
struct indexRes {
	int idat;
	int iloc;
	int iprop;
};
class ObservingEMF;
class Observation;
class ESElement {
protected:
	std::map<std::string, std::string> mAtt;
	std::string typeES;
	std::string classES;
	std::string metaType;
	static const std::map<std::string, std::string> mTypeAtt; // ajout parameter
public:
	std::vector<ESElement*> pContenant;
	std::vector<ESElement*> pComposant;

	static const std::string metaTypeESObject;
	static void println(std::string nam, std::string pr);
	virtual std::string json(bool complet, bool value, bool detail) const = 0;

	static JsonObject deserialize(std::string json);
	static bool isESAtt(std::string element, std::string key);
	static bool isESObs(std::string esClass, JsonObject jObj); // à tester
	ESElement();
	void setAtt(std::string key, std::string value);
	void majMeta();  // à vérifier
	ESElement* element(std::string compos) const;
	bool isAtt(std::string key) const;
	std::string getAttAll(std::string key) const;
	std::map<std::string, std::string> getmAtt() const;
	std::string getAtt(std::string key) const;
	std::string getTypeES() const;
	std::string getClassES() const;
	std::string getMetaType() const;
	std::string jsonAtt(bool complet) const;   // parametre numérique
	void addComposant(ESElement* pCompos);
	virtual void print() const;
};
class ESObject : public ESElement {
public:
	std::string name; // à tester
	ESObject();
	virtual std::string json(bool complet, bool value, bool detail) const = 0;
};
class ESObs : public ESElement {
protected:
	int nValue;
public:
	ESObs();
	ESObs(Observation* pObs);
	int getNvalue() const;
	void setNvalue(int nval);
};

#endif