# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 15:21:14 2021

@author: philippe@loco-labs.io


# Observation and Measurement

The ES (Environmental Sensing) package is built around the concept of Observation as define
in the ISO-19156 "observation and measurement" :  

*"This International Standard defines a conceptual schema for observations, and 
for features involved in sampling when making observations. These provide models 
for the exchange of information describing observation acts and their results, 
both within and between different scientific and technical communities."*   

# What is Environnemental Sensing project ?

The ES project is an implementation of the Standard :
    
- A data model that makes it possible to represent elementary observations 
(a simple one-off measurement), complex observations (multi-dimensions), 
detailed levels of representation (for example, the evolution of a plume of smoke).
- Data formats adapted to interfaces (binary payload for networks, json for requests 
or for NoSQL API, files)
- A library of connectors for different uses (sensors, database, storage, networks, etc.) 
in différents languages (python, C++)
- Bidirectional interfaces to data processing tools (eg Numpy, Xarray, GIS).

# Main principles

## Observation standard

## Index

## Dimension

## Json interface

## Binary interface

## Bluetooth mapping

## Xarray mapping

# Data model

An `ES.ESObservation.Observation` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
![classes observation](ESclasses.png "Observation class")

# What are the ES classes ?

The ES functions are divided according to the class hierarchy below :
 
![hierarchy observation](EShierarchie.png "Hierarchy Observation class")

Modules contain the following classes :
    
- ESObservation : `ES.ESObservation.Observation`, 
- ESValue : `ES.ESValue.DatationValue`, `ES.ESValue.LocationValue`, 
`ES.ESValue.PropertyValue`, `ES.ESValue.ResultValue`, `ES.ESValue.ESValue`, 
`ES.ESValue.ESIndexValue`, `ES.ESValue.ESSet`
- ESElement : `ES.ESElement.ESElement`, `ES.ESElement.ESObs`, `ES.ESElement.ESObject`.
- ESObs : `ES.ESObs.Location`, `ES.ESObs.Datation`, `ES.ESObs.Property`,
`ES.ESObs.Result`, `ES.ESObs.ESSetLocation`, `ES.ESObs.ESSetDatation`,
`ES.ESObs.ESSetProperty`, `ES.ESObs.ESSetResult`, 
- ESconstante : `ES.ESconstante.Es`.


"""
