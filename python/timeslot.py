# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 18:30:14 2022

@author: Philippe@loco-labs.io

The `ES.timeslot` module contains the `TimeSlot` and the `TimeInterval` classes.

# What is the TimeSlot Object ?

The TimeSlot Object is a representation of time intervals data and properties. For example,
 i can represent the working day of 2022-march-15 by a TimeSlot which inclde the following intervals:
- from 9 a.m. to 12 p.m.
- from 2 p.m. to 4:30 p.m.
- from 5 p.m. to 7:30 p.m.
i.e. a duration of 8 hours centered around 3 p.m. with bounds at 9 a.m. and 7:30 p.m.

# Main principles

The main principles are as follows :

<img src="./timeslot_data_structure.png" width="800">
    
## Data structure

A `TimeSlot` is a list of `TimeInterval`.

A `TimeInterval` is defined by to `datetime` objects (start and end)

Multiple properties are associated with the data :
    
- duration : sum of the lenght of each TimeInterval
- centroïd : instant assicited to the middle of the duration
- bounds : minimum, maximum and middle
- type : instant, interval or slot

## Relationships and assembly

Two `TimeSlot` can be compared with five statuses (equals, contains, whitin, disjoint, intersects).

Multiple operations between two objects can be performed :
    
- union between two `TimeSlot`
- intersection between two `TimeSlot`
- complementing a `TimeSlot` in an interval

"""
from datetime import datetime, timedelta
import json, numpy, pandas
from ESconstante import ES #, _identity

class TimeSlot:
    '''        
    *Attributes (for @property see methods)* :

    - **slot** : list of `TimeInterval`

    The methods defined in this class are : 
    
    *dynamic value property (getters)*
    
    - `TimeSlot.bounds`
    - `TimeSlot.centroid`
    - `TimeSlot.duration`
    - `TimeSlot.instant`
    - `TimeSlot.middle`
    - `TimeSlot.interval`
    - `TimeSlot.stype`
     
    *instance methods*

    - `TimeSlot.json`
    - `TimeSlot.link`
    - `TimeSlot.timetuple`
    - `TimeSlot.union`
    '''
    def __init__(self, val=None):
        '''
        TimeSlot constructor.

        *Parameters*
        
        - **val** : date, interval, list of interval (default None) - with several formats 
        (tuple, list, string, datetime, TimeSlot, TimeInterval, numpy datetime64, pandas timestamp)
        
        *Returns* : None'''          
        slot = []
        if type(val) == str:
            try:        val = json.loads(val)   
            except:
                try:    val = datetime.fromisoformat(val)
                except: val = None    
        if val == None : 
            self.slot = slot
            return
        if type(val) == tuple: val = list(val)
        if type(val) == list and len(val) == 2 and type(val[0]) != TimeInterval:  
            try :                         slot.append(TimeInterval(val))
            except :
                for interv in val :       slot.append(TimeInterval(interv))
        elif type(val) == list:  
            try :
                for interv in val :       slot.append(TimeInterval(interv))
            except :                      slot.append(TimeInterval(val))
        elif type(val) == TimeSlot :      slot = val.slot
        elif type(val) == TimeInterval :  slot.append(val)
        else :                            slot.append(TimeInterval(val))
        self.slot= TimeSlot._reduced(slot)
        
    def __add__(self, other):
        ''' Add other's values to self's values in a new TimeSlot'''
        return TimeSlot(TimeSlot._reduced(self.slot + other.slot))

    def __iadd__(self, other):
        ''' Add other's values to self's values'''
        self.slot = self._reduced(self.slot + other.slot)
        
    def __contains__(self, item):
        ''' item of extval'''
        return item in self.slot

    def __getitem__(self, index):
        ''' return interval item'''
        return self.slot[index]

    def __setitem__(self, index, interv): 
        ''' modify interval item'''
        if index < 0 or index >= len(self) : raise TimeSlotError("out of bounds")
        self.slot[index] = TimeInterval(interv)
        self.slot= TimeSlot._reduced(self.slot)
        
    def __len__(self): 
        '''return the number of intervals included'''
        return len(self.slot)
    
    def __repr__(self): 
        ''' return the type of slot and the json representation'''
        return self.stype + '\n' + self.json(True)
    
    def __eq__(self, other):
        '''equal if the slots are equals'''
        try: return self.slot == other.slot
        except: return False
               
    def __lt__(self, other): 
        '''compare the earliest dates'''
        return self.slot[0] < other.slot[0]

    def __hash__(self): return hash(self.json(True))

    @property
    def bounds(self): 
        '''return a tuple with the start and end dates with isoformat string'''
        return (self.slot[0].start.isoformat(), self.slot[len(self) - 1].end.isoformat())

    @property
    def centroid(self):
        '''return a TimeSlot with the date corresponding to the middle of the duration'''
        return TimeSlot(self.instant)
    
    @property
    def duration(self):
        '''cumulative duration of each interval (timedelta format)'''
        duration = timedelta()
        for interv in self.slot : duration += interv.duration
        return duration
    
    @property
    def instant(self): 
        '''return the date corresponding to the middle of the duration (datetime format)'''
        duration = self.duration / 2
        for interv in self.slot :
            if duration > interv.duration : 
                duration -= interv.duration
            else :
                return interv.start + duration
    
    @property
    def middle(self): 
        '''return the date corresponding to the middle of the bounds (datetime format)'''
        return self.bounds.instant
    
    @property
    def interval(self): 
        '''return a list with the start and end dates (datetime format)'''
        return [self.slot[0].start, self.slot[len(self) - 1].end]
    
    @property
    def stype(self):
        '''return a string with the type of TimeSlot (instant, interval, slot)'''
        if len(self.slot) == 1 : return self.slot[0].stype
        else : return 'slot'

    def json(self, json_string=False): 
        '''
        Return json structure with the list of TimeInterval.

        *Parameters*
        
        - **json_string** : defaut False - if True return string, else return dict
                
        *Returns* : string or dict'''
        if len(self) == 1 : js = self.slot[0].json(False)
        else : js = [interv.json(False) for interv in self.slot]
        if json_string : return json.dumps(js)
        else : return js

    def link(self, other):
        '''
        Return the status (string) of the link between two TimeSlot (self and other).
        - equals     : if self and other are the same
        - disjoint   : if self's intervals and other's intervals are all disjoint
        - within     : if all self's intervals are included in other's intervals
        - contains   : if all other's intervals are included in self's intervals
        - intersects : in the others cases

        *Parameters*
        
        - **other** : TimeSlot to be compared
                
        *Returns* 
        
        - **tuple** : (string(status), boolean(full or not))'''
        if self.stype == 'instant' : point, oslot = self[0], other
        elif other.stype == 'instant' : point, oslot = other[0], self
        else : point = None
        if point is not None :
            contains = equals = False
            for interv in oslot:
                contains = contains or interv.link(point) == 'contains'
                equals = equals or interv.link(point) == 'equals'
            if equals and not contains : return ('equals', True)
            if contains and point == other[0] : return ('contains', True) 
            if contains and point == self[0] : return ('within', True)
            return ('disjoint', True)
        else :
            union = self + other
            link = 'intersects'
            full = True
            if   union.duration == self.duration == other.duration : 
                full = len(union) == len(self) == len(other)
                link = 'equals'
            elif union.duration == self.duration :
                full = len(union) == len(self)
                link = 'contains'
            elif union.duration == other.duration :
                full = len(union) == len(other)
                link = 'within'
            elif union.duration == self.duration + other.duration : 
                full = len(union) == len(self) + len(other)
                link = 'disjoint'
            return (link, full)

    def timetuple(self, index=0, json_string=False): 
        '''
        Return json structure with the list of TimeInterval (timetuple filter).

        *Parameters*
        
        - **index** : integer, defaut 0 - timetuple format to apply :
            - 0 : year
            - 1 : month
            - 2 : day
            - 3 : hour
            - 4 : minute
            - 5 : seconds
            - 6 : weekday
            - 7 : yearday
            - 8 : isdst (1 when daylight savings time is in effect, 0 when is not)
        - **json_string** : defaut False - if True return string, else return dict
                
        *Returns* : string or dict'''
        if len(self) == 1 : js = self.slot[0].timetuple(index, False)
        else : js = [interv.timetuple(index, False) for interv in self.slot]
        if json_string : return json.dumps(js)
        else : return js
    
    def union(self, other):
        ''' Add other's values to self's values in a new TimeSlot (same as __add__)'''
        return self.__add__(other)

    @staticmethod    
    def _reduced(listinterv):
        ''' return an ordered and non-overlapping list of TimeInterval from any TimeInterval list'''
        if type(listinterv) != list or len(listinterv) == 0 : return []
        union = []
        slot = sorted(listinterv)
        interv = slot[0]
        i = j = 0
        while i < len(slot) :
            for j in range(i + 1, len(slot)):
                if   interv.link(slot[j]) == 'within'      : interv = slot[j]
                elif interv.link(slot[j]) == 'intersects'  : interv = interv.union(slot[j])
                elif interv.link(slot[j]) == 'disjoint' :
                    union.append(interv)
                    interv = slot[j]
                    i = j
                    break
            if j >= len(slot) - 1 : 
                union.append(interv)
                break
        return union
    
class TimeInterval:    # !!! interval
    '''        
    *Attributes (for @property see methods)* :

    - **start** : datetime Object - start of `TimeInterval`
    - **end**   : datetime Object - end of `TimeInterval`

    The methods defined in this class are : 
    
    *dynamic value property (getters)*
    
    - `TimeInterval.bounds`
    - `TimeInterval.centroid`
    - `TimeInterval.duration`
    - `TimeInterval.instant`
    - `TimeInterval.stype`
     
    *instance methods*

    - `TimeInterval.json`
    - `TimeInterval.link`
    - `TimeInterval.timetuple`
    - `TimeInterval.union`
    '''    
    def __init__(self, val= ES.nullDate):
        '''
        TimeInterval constructor.

        *Parameters*
        
        - **val** : date, interval (default ES.nullDate) - with several formats 
        (list, string, datetime, TimeInterval, numpy datetime64, pandas timestamp)
        
        *Returns* : None'''          
        self.start = self.end = ES.nullDate
        if type(val) == str:
            try:
                sl = datetime.fromisoformat(val)
                if sl != None : self.start = self.end = sl
                return
            except:
                try:     val = json.loads(val)
                except:  val = ES.nullDate    
        if   type(val) == list : self._initInterval(val)
        elif type(val) == TimeInterval :  self.start, self.end = val.start, val.end
        else : 
            dat = self._initDat(val)
            if dat != None : self.start = self.end = dat

    def __repr__(self):
        ''' return the type of interval and the json representation'''
        return self.stype + '\n' + self.json(True)
    
    def __eq__(self, other):
        '''equal if the 'start' and 'end' dates are equals'''
        return self.start == other.start and self.end == other.end

    def __lt__(self, other): 
        '''compare the earliest dates (start)'''
        return self.start < other.start

    def __hash__(self): return hash(self.json(True))
        
    @property
    def bounds(self): 
        '''return a tuple with the start and end dates with isoformat string'''
        return (self.start.isoformat(), self.end.isoformat())
        
    @property
    def centroid(self):
        '''return a TimeInterval with the date corresponding to the middle of the interval'''
        return TimeInterval(self.instant)
    
    @property
    def duration(self):
        '''duration between 'end' and 'start' date (timedelta format)'''
        return self.end - self.start
    
    @property
    def instant(self): 
        '''return the date corresponding to the middle of the duration (datetime format)'''
        return self.start + (self.end - self.start) / 2

    @property
    def stype(self):
        '''return a string with the type of TimeInterval (instant, interval)'''
        if self.start == self.end : return 'instant'
        else : return 'interval'

    def json(self, json_string=False): 
        '''
        Return json structure (date if 'instant' or [strat, end] if 'interval') 
        with datetime.isoformat for dates.

        *Parameters*
        
        - **json_string** : defaut False - if True return string, else return dict
                
        *Returns* : string or dict'''
        if self.stype == 'instant' : js = self.start.isoformat()
        elif self.stype == 'interval' : js = [self.start.isoformat(), self.end.isoformat()]
        if json_string : return json.dumps(js)
        else : return js

    def link(self, other):
        '''
        Return the status (string) of the link between two TimeIntervals (self and other).
        - equals     : if self and other are the same
        - disjoint   : if self's interval and other's interval are disjoint
        - within     : if other's interval is included in self's interval
        - contains   : if self's interval is included in other's interval
        - intersects : in the others cases

        *Parameters*
        
        - **other** : TimeInterval to be compared
                
        *Returns* : string'''
        if self.start == other.start and self.end == other.end : return 'equals'
        if self.start <= other.start and self.end >= other.end : return 'contains'
        if self.start >= other.start and self.end <= other.end : return 'within'
        if self.start <= other.end and self.end >= other.start : return 'intersects'
        return 'disjoint'

    def timetuple(self, index=0, json_string=False): 
        '''
        Return json structure (timetuple filter).

        *Parameters*
        
        - **index** : integer, defaut 0 - timetuple format to apply :
            - 0 : year
            - 1 : month
            - 2 : day
            - 3 : hour
            - 4 : minute
            - 5 : seconds
            - 6 : weekday
            - 7 : yearday
            - 8 : isdst (1 when daylight savings time is in effect, 0 when is not)
        - **json_string** : defaut False - if True return string, else return dict
                
        *Returns* : string or dict'''
        if index not in [0,1,2,3,4,5,6,7,8] : return None
        if self.stype == 'instant' : js = self.start.timetuple()[index]
        elif self.stype == 'interval' : js = [self.start.timetuple()[index], self.end.timetuple()[index]]
        if json_string : return json.dumps(js)
        else : return js

    def union(self, other):
        ''' Add other's values to self's values in a new TimeInterval 
        if self and other are not disjoint'''
        if self.link(other) != 'disjoint' : return TimeInterval([min(self.start, other.start), max(self.end, other.end)])
        else : return None

    def _initInterval(self, val):
        '''initialization of start and end dates from a list'''
        self.start = self.end = self._initDat(val[0])
        if len(val) > 1 : self.end = self._initDat(val[1])
        else :    self.start = self.end = self._initDat(val)
        if self.end < self.start : self.start, self.end = self.end, self.start

    def _initDat(self, val):
        '''initialization of start and end dates from a unique value 
        (datetime, string, numpy.datetime64, pandas Timestamp)'''
        if   type(val) == datetime: res = val
        elif type(val) == str:
            try : res = datetime.fromisoformat(val)
            except: res = ES.nullDate
        elif type(val) == numpy.datetime64 :
            res = pandas.Timestamp(val).to_pydatetime()
        elif type(val) == pandas._libs.tslibs.timestamps.Timestamp :
            res = val.to_pydatetime()
        else : raise TimeSlotError("impossible to convert in a date")
        return res

class TimeSlotError(Exception):
    pass
    