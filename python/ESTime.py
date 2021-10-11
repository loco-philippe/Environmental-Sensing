# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 09:26:46 2021

@author: a179227
"""


from datetime import datetime

class InTime : 
    def __init__(self):
        self.type = "null"
        self.centre = 0
        
class Instant(InTime) :
    def __init__(self, val):
        InTime.__init__(self)
        self.dtVal= val
        self.type = "inst"
        self.centre = val
        
class Interval(InTime) :
    def __init__(self, val1, val2):
        InTime.__init__(self)
        self.dtIntVal= [val1, val2]
        self.centre = (val1 +val2) / 2

class TimeVal:
    def __init__(self, *args):
        if len(args) == 1:
            self.tShape = Instant(args[0])
        elif len(args) == 2:
            self.tShape = Interval(args[0], args[1])
        self.centre = self.tShape.centre
        self.type = self.tShape.type
        
t1 = TimeVal(2)
t2 = TimeVal(4)
it1 = TimeVal(4, 8)

print(t2.centre, it1.centre)
print(t2.type, it1.type)
