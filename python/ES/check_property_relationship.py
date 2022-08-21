# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 16:39:16 2022
@author: philippe@loco-labs.io

Example to check the validity of relationship property
"""

def check_relationship(field1, field2):
    dist = len(set(zip(field1, field2)))
    len1 = len(set(field1))
    len2 = len(set(field2))
    
    if dist == len1 and dist > len2:    return "field 2 is derived from field 1"
    if dist == len2 and dist > len1:    return "field 1 is derived from field 2"    
    if dist == len1 and dist == len2:   return "field 2 and field 1 are coupled"
    if dist == len1 * len2:             return "field 2 and field 1 are crossed"
    return "field 1 and field 2 are linked"

example = [ [  'T1',    'T2',   'T2',    'T1',    'T2',   'T1'],
            [ 'jan',   'apr',  'jun',   'feb',   'may',  'jan'],
            ['john',  'paul', 'leah',  'paul',  'paul', 'john'],
            ['jock', 'paulo', 'lili', 'paulo', 'paulo', 'jock'],
            [  2020,    2020,   2021,    2021,    2022,   2022],
            [  's1',    's2',   's1',    's2',    's1',   's2']]

print(check_relationship(example[0], example[1]))  #field 1 is derived from field 2
print(check_relationship(example[2], example[3]))  #field 2 and field 1 are coupled
print(check_relationship(example[4], example[5]))  #field 2 and field 1 are crossed
print(check_relationship(example[1], example[4]))  #field 1 and field 2 are linked