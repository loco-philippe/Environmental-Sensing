# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:56:20 2023

@author: a lab in the Air
"""

## fichier file1.py
class toto(object):
    def __init__(self, a):
        self.a = a
        
## fichier file2.py
import file1
 
def affiche(self, nombre): print self.a, nombre
 
setattr(file1.toto, "affiche", affiche)

## fichier file3.py
import file2
import file1
 
test = file1.toto(5)
test.affiche(10)  ## 5, 10
       