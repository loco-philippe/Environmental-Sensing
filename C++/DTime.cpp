#include "stdafx.h"
#include "DTime.h"

DTime::DTime(int Y, int M, int D, int h, int m, int s) {
  _year = Y;
  _month = M;
  _day = D;
  _hour = h;
  _minute = m;
  _second = s;
  encode();
}

DTime::DTime(const DTime & z) {
	_year = z.year;
	_month = z.month;
	_day = z.day;
	_hour = z.hour;
	_minute = z.minute;
	_second = z.second;
	_timestamp = z.timestamp;
	_weekday = z.weekday;
}

DTime & DTime::operator=(const DTime & z) {
	_year = z.year;
	_month = z.month;
	_day = z.day;
	_hour = z.hour;
	_minute = z.minute;
	_second = z.second;
	_timestamp = z.timestamp;
	_weekday = z.weekday;
	return *this;
}

bool DTime::isLeapYear(int Y) {
  return !((Y % 4) * (!(Y % 100) + (Y % 400)));
}

DTime DTime::setDate(int Y, int M, int D) {
  _year = Y;
  _month = M;
  _day = D;
  encode();
  return *this;
}

DTime DTime::setTime(int h, int m, int s) {
  _hour = h;
  _minute = m;
  _second = s;
  encode();
  return *this;
}

DTime DTime::setTimestamp(int t) {
  _timestamp = t;
  decode();
  return *this;
}

DTime DTime::tick() {
  _timestamp++;
  decode();
  return *this;
}

int DTime::wday(int Y, int M, int D) {
  int n[12] = {31, 28 + isLeapYear(Y), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  Y = (D + (((Y - 1) * 365UL) + ((Y - 1) / 4) - ((Y - 1) / 100) + ((Y - 1) / 400))) % 7;
  while (M > 1) Y += n[--M - 1];
  return Y % 7;
}

void DTime::decode() {
  int t = _timestamp;
  _second = t % 60;
  _minute = (t /= 60) % 60;
  _hour = (t /= 60) % 24;

  t /= 24;
  for (_year = 1970; t >= (365 + isLeapYear(_year)); _year++) t -= (365 + isLeapYear(_year));

  int n[12] = {31, 28 + isLeapYear(_year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  for (_month = 1; t >= n[_month - 1]; _month++) t -= n[_month - 1];

  _day = t + 1;
  _weekday = wday(_year, _month, _day);
}

void DTime::encode() {
  _timestamp = ((_day - 1) * 86400UL) + (_hour * 3600UL) + (_minute * 60UL) + _second;

  int n[12] = {31, 28 + isLeapYear(_year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  for (int M = _month; M > 1;) _timestamp += (n[--M - 1] * 86400UL);

  for (int Y = _year; 1970 < Y; Y--) _timestamp += ((isLeapYear(Y - 1) + 365) * 86400UL);
  _weekday = wday(_year, _month, _day);
}
