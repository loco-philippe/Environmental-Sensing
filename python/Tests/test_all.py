# -*- coding: utf-8 -*-
"""
Created on Sat Jul 30 19:03:20 2022

@author: philippe@loco-labs.io
"""
import unittest
from observation import Es
#from test_esvalue import TestObsUnitaire
from test_dataset import Test_Dataset
from test_field import Test_Field

if __name__ == '__main__':
    ES = Es(False)
    unittest.main(verbosity=2)
    #print(ES.def_clsName, ES.def_dtype)
    ES = Es(True)
    unittest.main(verbosity=2)
    # test
    #print(ES.def_clsName, ES.def_dtype)
