# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 18:30:14 2022

@author: a179227
"""
from datetime import datetime
import json, numpy, pandas, copy
from ESconstante import ES #, _identity

class TimeSlot:
    def __init__(self, val= ES.nullDate):
        self.slot = []
        self.type = 'null'
        if type(val) == str:
            try:
                sl = datetime.fromisoformat(val)
                if sl != None :
                    self.slot.append([sl, sl])
                    self.type ='instant'
                return
            except:
                try:
                    val = json.loads(val)
                except:
                    val = ES.nullDate    
        #from ESValue import DatationValue
        if type(val) == list:  
            if type(val[0]) == list : 
                for interv in val : self._initInterval(interv)
            else : self._initInterval(val)
        elif type(val) == TimeSlot :
            self.slot = val.slot
        else : 
            dat = self._initDat(val)
            if dat != None : self.slot.append([dat,dat])
        if len(self.slot) > 1 : self.type = 'slot'
        elif len(self.slot) == 1 and self.slot[0][0] == self.slot[0][1] : self.type = 'instant'
        elif len(self.slot) == 1: self.type = 'interval'
        
    def _initInterval(self, val):
        res = None
        if type(val) == list :
            dat1 = dat2 = self._initDat(val[0])
            if len(val) > 1 : dat2 = self._initDat(val[1])
        else : 
            dat1 = dat2 = self._initDat(val)
        self.slot.append([min(dat1, dat2), max(dat1, dat2)])
        '''
        if dat1 == ES.nullDate :
            if dat2 == ES.nullDate : res = None
            else: res = [dat2, dat2]
        else: 
            if dat1 == ES.nullDate : res = [dat1, dat1]
            else: res = [min(dat1, dat2), max(dat1, dat2)]
        if res != None : self.slot.append(res)
        '''            
    def _initDat(self, val):
        res = ES.nullDate
        if   type(val) == datetime: 
            res = val
        elif type(val) == str:
            try : res = datetime.fromisoformat(val)
            except: res = ES.nullDate
        elif type(val) == numpy.datetime64 :
            res = pandas.Timestamp(val).to_pydatetime()
        elif type(val) == pandas._libs.tslibs.timestamps.Timestamp :
            res = val.to_pydatetime()
        #if res == ES.nullDate : return None
        #else : return res
        return res

    def __repr__(self): return self.type + '\n' + self.json(True)
    
    def __eq__(self, other): return self.slot == other.slot

    def __lt__(self, other): return self.instant < other.instant

    def __hash__(self): return hash(self.json(True))

    def json(self, string=False): 
        if self.type == 'null' : js = ES.nullDate
        if self.type == 'instant' : js = self.slot[0][0].isoformat()
        elif self.type == 'interval' : 
            js = [[self.slot[0][0].isoformat(), self.slot[0][1].isoformat()]]
        elif self.type == 'slot' :
            js = list()
            for interv in self.slot :
                js.append([interv[0].isoformat(), interv[1].isoformat()])
        if string : return json.dumps(js)
        else : return js

    @property
    def bounds(self): return (self.interval[0].isoformat(), self.interval[1].isoformat())
        
    @property
    def instant(self): 
        return self.interval[0] + (self.interval[1] - self.interval[0]) / 2
    @property
    def interval(self): 
        if self.type == 'instant' : 
            return [self.slot[0][0], self.slot[0][0]]
        elif self.type == 'interval' : 
            return self.slot[0]
        elif self.type == 'slot' :
            mini = self.slot[0][0]
            maxi = self.slot[0][1]
            for interv in self.slot :
                mini = min(mini, interv[0])
                maxi = max(maxi, interv[1])
            return [mini, maxi]
        else : return [ES.nullDate, ES.nullDate]
    
    def union(self, other):
        res = copy.deepcopy(self.slot)
        for interv in other.slot : res.append(interv)
        return TimeSlot(res)