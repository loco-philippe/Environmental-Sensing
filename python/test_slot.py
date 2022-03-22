# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 20:50:18 2022

@author: Philippe@loco-labs.io

The `ES.test_slot` module contains the unit tests (class unittest) for the 
`TimeSlot` functions.
"""

import unittest, json


from timeslot import TimeSlot
from datetime import datetime, timedelta

matin = [ datetime(2020, 2, 4, 8), datetime(2020, 2, 4, 12)]
midi  = [ datetime(2020, 2, 4, 12), datetime(2020, 2, 4, 14)]
aprem  = [ datetime(2020, 2, 4, 14), datetime(2020, 2, 4, 18)]
travail = [matin, aprem]
pt1 = datetime(2020, 2, 4, 12, 5, 0)
pt2 = datetime(2020, 5, 4, 12, 5, 0)
pt3 = datetime(2020, 7, 4, 12, 5, 0)
tnull = datetime(1970, 1, 1, 0, 0, 0)
snull = (tnull.isoformat(), tnull.isoformat())
t1 = datetime(2021, 2, 4, 12, 5, 0)
t1n = json.dumps({'date1' : t1.isoformat()})
t2 = datetime(2021, 7, 4, 12, 5, 0)
t3 = datetime(2021, 5, 4, 12, 5, 0)

def _date(n): return datetime(2021, 1, n)
def _inte(n,m): return [_date(n), _date(m)]

class TestObsUnitaire(unittest.TestCase):
    '''Unit tests for `TimeSlot` '''

    def test_TimeSlot(self):
        s1 = TimeSlot(datetime(2001, 2, 3))
        s = TimeSlot('"2001-02-03T00:00:00"')
        self.assertTrue(s==s1)
        s = TimeSlot([datetime(2001, 2, 3), datetime(2001, 2, 1)])
        s1 = TimeSlot(['2001-02-03T00:00:00', datetime(2001, 2, 1)])
        s2 = TimeSlot('["2001-02-03T00:00:00","2001-02-01T00:00:00"]')
        self.assertTrue(s==s1==s2)
        s = TimeSlot('[["2001-02-03T00:00:00","2001-02-01T00:00:00"], ["2001-02-05T00:00:00","2001-02-06T00:00:00"]]')
        self.assertTrue(s.stype == 'slot')
        self.assertTrue(TimeSlot([matin, aprem]).centroid.bounds[1] == TimeSlot(matin).bounds[1])
        self.assertTrue(TimeSlot([matin, aprem]).bounds == TimeSlot([matin, midi, aprem]).bounds)

    def test_union(self):
        ts1 = TimeSlot([_inte(19,22), _inte(1,4), _inte(1,5), _inte(2,6), _inte(7,8), _inte(6,8), _inte(10,15), _inte(20,25)])  
        ts2 = TimeSlot([_inte(19,22), _inte(1,4), _inte(1,5), _inte(2,6)])
        ts3 = TimeSlot([_inte(7,8), _inte(6,8), _inte(10,15), _inte(20,25)])
        ts4 = TimeSlot([_inte(20,25)])
        ts5 = TimeSlot()
        self.assertEqual(ts1.duration / timedelta(days=1), 18.0)        
        self.assertEqual(len(ts1), 3)      
        self.assertEqual(TimeSlot(ts1.bounds).duration / timedelta(days=1), 24)      
        self.assertTrue(ts1 == ts2+ts3 == ts2+ts3+ts4 == ts2+ts3+ts4+ts5 == ts5+ts2+ts3+ts4 == ts1+ts1)

    def test_link(self):
        ts1 = TimeSlot([_inte(1,4), _inte(7,8)])
        ts2 = TimeSlot([_inte(11,14), _inte(9,10)])
        self.assertEqual(ts1.link(ts1), ('equals',    True))
        self.assertEqual(ts1.link(ts2), ('disjoint',  True))
        self.assertEqual(ts2.link(ts1), ('disjoint',  True))
        ts2 = TimeSlot([_inte(11,14), _inte(8,10)])
        self.assertEqual(ts1.link(ts2), ('disjoint',  False))
        self.assertEqual(ts2.link(ts1), ('disjoint',  False))
        ts2 = TimeSlot([_inte(2,3), _inte(6,9)])
        self.assertEqual(ts1.link(ts2), ('intersects', True))
        self.assertEqual(ts2.link(ts1), ('intersects', True))
        ts1 = TimeSlot([_inte(1,4), _inte(5,10)])
        self.assertEqual(ts1.link(ts2), ('contains',    True))
        self.assertEqual(ts2.link(ts1), ('within',  True))
        self.assertEqual(TimeSlot(_date(7)).link(ts2), ('within', True))
        self.assertEqual(TimeSlot(_date(2)).link(ts2), ('within', True))
        self.assertEqual(TimeSlot(_date(5)).link(ts2), ('disjoint', True))
        self.assertEqual(ts2.link(TimeSlot(_date(7))), ('contains', True))
        self.assertEqual(ts2.link(TimeSlot(_date(3))), ('contains', True))
        self.assertEqual(ts2.link(TimeSlot(_date(5))), ('disjoint', True))
        self.assertEqual(TimeSlot(_date(5)).link(TimeSlot(_date(5))), ('equals', True))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)        