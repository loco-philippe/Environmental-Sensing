# -*- coding: utf-8 -*-
"""
## ***Environnemantal Sensing Package***

Created on Fri Dec 24 15:21:14 2021

@author: philippe@loco-labs.io


# Why a project for Environnemental Data ?

The project was born from the following observations:
    
- there is no standard format (apart from the Environmental Sensing Service Bluetooth) 
used by the sensors to transmit the information (binary and textual),
- there is no data exchange format presenting at the same time a temporal, 
spatial and physical component (apart from file formats),
- we spend a lot of energy converting this type of data to make it usable.

# The Environnemental Sensing project

The ES project is made of :
    
- A data model that makes it possible to represent elementary observations 
(a simple one-off measurement), complex observations (multi-dimensions), 
detailed levels of representation (for example, the evolution of a plume of smoke).
- Data formats adapted to interfaces (binary payload for networks, json for requests 
or for NoSQL API, files)
- A library of connectors for different uses (sensors, database, storage, networks, etc.) 
in différents languages (python, C++)
- Bidirectional interfaces to data processing tools (eg Numpy, Xarray, GIS).

It allows to :
    
- Facilitate the use and sharing of environmental data
- Standardize both data acquisition equipment (sensors) and processing applications,
- Implement a software architecture replacing all coding / decoding operations 
(interfaces) by the use of standard connectors,
- Respect and rely on the main existing standards
- Collectively share and develop a set of open-source connectors responding to 
all situations (platform)

# Main principles

## Standards

The main standard about Environnemental Data is the ISO-19156 "observation and 
measurement" standard :    

*"This International Standard defines a conceptual schema for observations, and 
for features involved in sampling when making observations. These provide models 
for the exchange of information describing observation acts and their results, 
both within and between different scientific and technical communities."* 

But this standard specifies that: 
    
*"ISO 19156 concerns only concerns only interfaces visible from the outside and
 does not impose any restrictions on the underlying implementations"*

The other standards concern more restricted areas and are sometimes incompatible. 
They often remain at a syntactic and non-semantic level.
The proposed data structure is based on existing standards that it complements 
by ensuring convergence:    

<img src="./ES/standard.png" width="800">

## Data structure

An Observation is characterized by:

- "observed property": the observed property,
- "feature of interest": the object (most often a location) of the observation,
- "procedure": the information acquisition mode (sensor, model, etc.)
- "result": result of the observation or the measurement

The result is a set of values or objects ​​referenced according to the 3 dimensions:

- temporal,
- spatial,
- physical (observed property)

It can be converted into a 3-dimensional matrix, each result being indexed by 
temporal, spatial and physical values.

<img src="./ES/structure.png" width="800">

Common properties (indicators) are associated 
with each Observation. They allow processing to be performed on Observations 
without having to know their composition (eg bounding boxes, type of observation,
volume, etc.).   

*Note: This “domain range” indexed representation is preferred to an “interleaved”
tabular representation which associates temporal, spatial and physical values  
​​with each value of the result.*

## Index

## Dimension

## Json interface

## Binary interface

## Bluetooth mapping

## Xarray mapping

# Getting Started

## First Observation

<img src="./ES/first observation.png" width="800">
<img src="./ES/first observation2.png" width="800">
<img src="./ES/first observation carto.png" width="800">
<img src="./ES/first observation carto2.png" width="800">

## More complex Observation

<img src="./ES/complex observation.png" width="800">
<img src="./ES/complex observation2.png" width="800">
<img src="./ES/complex observation3.png" width="800">

## Synthesis

<img src="./ES/synthesis.png" width="800">
<img src="./ES/synthesis2.png" width="800">


# Quick overview

## Create an Observation

### Measuring station

### Mobile sensor

### Simulation

### Access information

### Visualize an Observation

## Generate an Exchange format

### Binary format

### Json format

### No SQL format

## Managing Observations

### Sort

### Aggregation

### Numpy export

### Xarray export

# Developpers documentation

## Data model

An `ESObservation.Observation` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
<img src="./ES/ESclasses.png" width="800">

## What are the ES classes ?

The ES functions are divided according to the class hierarchy below :
 
<img src="./ES/EShierarchie.png" width="800">

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
