#pragma once
#ifndef OBSTYPE_
#define OBSTYPE_
#include <iostream>
#include <string>
#include "ESObservation.h"

class ObsFixe : public Observation {
protected:
	indexRes addTimeIndex(TimeValue tim, int nprop);
public:
	ObsFixe(LocationValue coor);
	int init(PropertyValue prop);
	int addValueFixe(RealValue val, TimeValue tim, int nprop);
	int addValueFixe(IntValue val, TimeValue tim, int nprop);
	int addValueFixe(StringValue val, TimeValue tim, int nprop);
};

class ObsSensor : public Observation {
protected:
	indexRes addIndex(TimeValue tim, LocationValue coor, int nprop);
public:
	ObsSensor();
	int init(PropertyValue prop);
	int addValueFixe(RealValue val, TimeValue tim, LocationValue coor, int nprop);
	int addValueFixe(IntValue val, TimeValue tim, LocationValue coor, int nprop);
	int addValueFixe(StringValue val, TimeValue tim, LocationValue coor, int nprop);
};

#endif