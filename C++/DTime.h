#ifndef DTIME_H
#define DTIME_H

/*#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif*/

#define DTIME_DAYS_UNTIL(y) ({((((y) - 1) * 365UL) + (((y) - 1) / 4) - (((y) - 1) / 100) + (((y) - 1) / 400));})
#define DTIME_DAYS_BETWEEN_YEARS(y1,y2) ({(DTIME_DAYS_UNTIL(((y1) > (y2)) ? (y1) : (y2)) - DTIME_DAYS_UNTIL(((y1) > (y2)) ? (y2) : (y1)));})
#define DTIME_LEAP_YEAR(y) ({!(((y) % 4) * (!((y) % 100) + ((y) % 400)));})
#define DTIME_MONTH_DAYS(y,m) ({(31 - (((m) > 2) ? ((((m) - 1) - (5 * ((m) > 7))) % 2) : (((m) - 1) * (3 - DTIME_LEAP_YEAR(y)))));})
#define DTIME_YEAR_DAYS_UNTIL(y,m) ({int d = 0; for(int i = 1; i < (m); i++) d += DTIME_MONTH_DAYS((y), i); d;})
#define DTIME_WEEKDAY(y,m,d) ({(DTIME_DAYS_UNTIL(y) + DTIME_YEAR_DAYS_UNTIL((y), (m)) + (d)) % 7;})

class DTime {
  public:
    const int &month = _month, &weekday = _weekday, &day = _day, &hour = _hour, &minute = _minute, &second = _second;
    const int &year = _year, &timestamp = _timestamp;

    explicit DTime() {};
    explicit DTime(int t): _timestamp(t) { decode();};
    DTime(int Y, int M, int D, int h, int m, int s);
    DTime(const DTime & z);
    DTime& operator=(const DTime & z);
    
    DTime setDate(int Y, int M, int D);
    DTime setTime(int h, int m, int s);
    DTime setTimestamp(int t);
    DTime tick();

    bool isLeapYear(int Y);
    int wday(int Y, int M, int D);

  private:
    int _month = 1, _weekday = 4, _day = 1, _hour = 0, _minute = 0, _second = 0;
    int _year = 1970;
    int _timestamp = 0;

    void decode();
    void encode();
};

#endif
