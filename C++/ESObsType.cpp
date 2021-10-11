#include "stdafx.h"
#include "ESObsType.h"

using namespace std;

ObsFixe::ObsFixe(LocationValue coor): Observation() {	addValue<LocationValue, Location>(coor);}
int ObsFixe::init(PropertyValue prop) {	return addValue<PropertyValue, Property>(prop);}
int ObsFixe::addValueFixe(RealValue val, TimeValue tim, int nprop) {
	ResultValue<RealValue> resVal(val);
	resVal.setindexRes(addTimeIndex(tim, nprop));
	return addValue<ResultValue<RealValue>, Result>(resVal);
}
int ObsFixe::addValueFixe(IntValue val, TimeValue tim, int nprop) {
	ResultValue<IntValue> resVal(val);
	resVal.setindexRes(addTimeIndex(tim, nprop));
	return addValue<ResultValue<IntValue>, Result>(resVal);
}
int ObsFixe::addValueFixe(StringValue val, TimeValue tim, int nprop) {
	ResultValue<StringValue> resVal(val);
	resVal.setindexRes(addTimeIndex(tim, nprop));
	return addValue<ResultValue<StringValue>, Result>(resVal);
}
indexRes ObsFixe::addTimeIndex(TimeValue tim, int nprop) {
	indexRes indval;
	indval.iloc = 0;
	indval.idat = addValue<TimeValue, Datation>(tim);
	indval.iprop = nprop;
	return indval;
}

