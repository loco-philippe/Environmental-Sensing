# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 15:21:14 2021

@author: philippe@loco-labs.io

# What is Environnemental Sensing ?

The ES (Environmental Sensing) package is built around the concept of Observation.
An `ES.ESObservation.Observation` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
![classes observation](ESclasses.png "Observation class")

# What are the ES classes ?

The ES functions are divided according to the class hierarchy below:
 
![hierarchy observation](EShierarchie.png "Hierarchy Observation class")

Modules contain the following classes :
    
- ESObservation : [Observation](ESObservation.html#ES.ESObservation.Observation), 
- ESValue : [DatationValue](ESValue.html#ES.ESValue.DatationValue), 
[LocationValue](ESValue.html#ES.ESValue.LocationValue), 
[PropertyValue](ESValue.html#ES.ESValue.PropertyValue), 
[ResultValue](ESValue.html#ES.ESValue.ResultValue), 
[ESValue](ESValue.html#ES.ESValue.ESValue), 
[ESIndexValue](ESValue.html#ES.ESValue.ESIndexValue), 
[ESSet](ESValue.html#ES.ESValue.ESSet)
- ESElement : [ESElement](ESElement.html#ES.ESElement.ESElement),
[ESObs](ESElement.html#ES.ESElement.ESObs) , 
[ESObject](ESElement.html#ES.ESElement.ESObject).
- ESObs : [Location](ESObs.html#ES.ESObs.Location),
[Datation](ESObs.html#ES.ESObs.Datation),
[Property](ESObs.html#ES.ESObs.Property),
[Result](ESObs.html#ES.ESObs.Result),
[ESSetLocation](ESObs.html#ES.ESObs.ESSetLocation),
[ESSetDatation](ESObs.html#ES.ESObs.ESSetDatation),
[ESSetProperty](ESObs.html#ES.ESObs.ESSetProperty),
[ESSetResult](ESObs.html#ES.ESObs.ESSetResult),
- ESconstante : [Es](ESconstante.html#ES.ESconstante.Es),

"""

