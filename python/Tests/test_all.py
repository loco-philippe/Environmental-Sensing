# -*- coding: utf-8 -*-
"""
Created on Sat Jul 30 19:03:20 2022

@author: a179227
"""
import unittest
from test_esvalue import TestObsUnitaire
from test_ilist import Test_Ilist
from test_iindex import Test_iindex
from ESconstante  import Es

if __name__ == '__main__':
    ES = Es(False)
    unittest.main(verbosity=2)   
    #print(ES.def_clsName, ES.def_dtype)
    ES = Es(True)
    unittest.main(verbosity=2)
    #test
    #print(ES.def_clsName, ES.def_dtype)

