# -*- coding: utf-8 -*-
"""
## ***Environmental Sensing Package***

Created on Fri Dec 24 15:21:14 2021

@author: philippe@loco-labs.io


# Why a project for Environmental Data ?

The project was born from the following observations:
    
- there is no standard format (apart from the Environmental Sensing Service Bluetooth) 
used by the sensors to transmit the information (binary and textual),
- there is no data exchange format presenting at the same time a temporal, 
spatial and physical component (apart from file formats),
- we spend a lot of energy converting this type of data to make it usable.

# The Environmental Sensing project

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

The main standard about Environmental Data is the ISO-19156 "observation and 
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
without having to know their composition (e.g. bounding boxes, type of observation,
volume, etc.).   

## Index

<img src="./ES/index.png" width="800">

In a Observation, the Result is associated with a Datation, a Location and a Property.
In the usual tabular representations (like Excel or csv) there is one row for each Result
and a lot of columns for Datation, Location and Property.
This representation is simple and readable, but it duplicates the information and
 is not suitable for updates. 
 
In the ES project, we chose the indexed representation suitable for computer 
processing. Thus, the Result object is made up of its own attributes as well as
 an index to the Datation, Location and Property objects. 

## Dimension

<img src="./ES/dimension.png" width="800">

A result is associated with a property, a location and a date. The Result Object 
is therefore indexed with three axes (dimension = 3). But there are two cases 
where the dimension is reduced:
    
- if an axis has only one value
- if two axes are coupled

For example, if on a path we measure a property, the dimension is 1 (Location 
and Datation are coupled, Property has one value).

This notion is important because it conditions the modes of representation
 (e.g., plot).

## Json interface

The JSON format is used for Observation interchange. The ObsJSON format support
 the Observation data model. This means that an Observation generated from a 
 JSON format from another Observation is identical to this one.

This format is defined in the 
<a href="https://github.com/loco-philippe/Environnemental-Sensing/blob/main/documentation/ObsJSON%20-%20Standard.pdf" 
target="_blank">ObsJSON document</a>.

## Binary interface

The binary payload is necessary for exchanges with LPWAN networks (e.g. SigFox, 
LoRaWAN). The payload should be as compact as possible to minimize the Time-on-Air 
and reduce power consumption (for battery operated) devices. For example, the maximum
lenght of the payload is 12 bytes for SigFox and between 51 bytes and 222 bytes for LoRaWAN.

To obtain this maximum length, limitations are imposed.

<img src="./ES/binary.png" width="800">

The diagram above shows the structure of the payload.

*Note : The right side of the diagram explains the coding of the values. This coding 
is the same as that used by Bluetooth in the <a href=
"https://www.bluetooth.com/specifications/specs/environmental-sensing-service-1-0/" 
target="_blank">Environmental Sensing Service</a>.*

To obtain low payload, a specific process can be used (see below). It allows data
 to be sent in two stages: first send metadata, second (in operation use) send data.
 
<img src="./ES/sensor.png" width="800">

 
## Bluetooth mapping

The Environmental Sensing Service is a Bluetooth protocol for sensors. The data 
exposed in this protocol are compatible and consistent with the Observation data model. 
Thus, Bluetooth data is automatically converted into Observation data.
 
The diagram below shows the mapping of the two structures.

<img src="./ES/bluetooth.png" width="800">

## Xarray mapping

Xarray is very powerful to analyze and process multi-dimensional data. Xarray 
share the same principle as Observation: indexed multi-dimensional data. Thus, 
it's natural du use Xarray if you want to analyze Observation data.

The difference between Observation and Xarray is that Xarray uses matrix data and 
Observation uses only indexed data. Therefore, to transfer Observation data to Xarray 
we must complete data with 'nan' value to obtain a complete matrix with the right 
dimension (1, 2 or 3).

The diagram below shows the mapping of the two structures.

<img src="./ES/xarray.png" width="800">

# Getting Started

the code used, the results and the explanations are provided through "Jupyter 
Notebook" indicated in link in each chapter.
The Notebook files are 
<a href="https://github.com/loco-philippe/loco-philippe.github.io/tree/main/Example" target="_blank">
stored in Github</a> and can be replayed.

## First Observation

This chapter explain you 
<a href="./Example/first observation.html" target="_blank">(see the page here)</a> :
    
- how to create a simple and more complex Observation Object
- the different view of the data
- how the ObsJSON is structured 

## Observation for sensor

The sensors how use TCP/IP send the data with ObsJSON format (see above).
This chapter is dedicated to binary interface and explain you:
<a href="./Example/first observation.html" target="_blank">(see the page here)</a> :
    
- how to encode and decode binary data
- the processes to obtain low data

## Observation management

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

### Storage

# Developers documentation

## Data model

An `ESObservation.Observation` is an object representing a set of information having
spatial and temporal characteristics associated with measurable or observable
 properties.
<img src="./ES/ESclasses.png" width="800">

## What are the ES classes ?

The ES functions are divided according to the class hierarchy below:
 
<img src="./ES/EShierarchie.png" width="800">

Modules contain the following classes:
    
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


"""
<img src="./Example/first observation.png" width="800">
<img src="./Example/first observation2.png" width="800">
<img src="./Example/first observation carto.png" width="800">
<img src="./Example/first observation carto2.png" width="800">

## More complex Observation

<img src="./Example/complex observation.png" width="800">
<img src="./Example/complex observation2.png" width="800">
<img src="./Example/complex observation3.png" width="800">

## Synthesis

<img src="./Example/synthesis.png" width="800">
<img src="./Example/synthesis2.png" width="800">

*Note: This “domain range” indexed representation is preferred to an “interleaved”
tabular representation which associates temporal, spatial and physical values  
​​with each value of the result.*

[ObsJSON ](https://github.com/loco-philippe/Environnemental-Sensing/blob/main/documentation/ObsJSON%20-%20Standard.pdf)
document.

"""