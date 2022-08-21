# -*- coding: utf-8 -*-
"""
***Environmental Sensing Package***

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

# Documentation

The concepts of 'observation', 'indexed list' and 'ES value' are describe in 
[this page](https://github.com/loco-philippe/Environmental-Sensing/wiki).

The non-regression tests are at 
[this page](https://github.com/loco-philippe/Environmental-Sensing/blob/main/python/Tests)

Examples are [here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Example)

Modules contain the following classes:
    
- ESObservation : 
    
    - `ES.ESObservation`
    
- ESValue : 
    
    - `ES.ESValue`(`ES.ESValue.DatationValue`, `ES.ESValue.LocationValue`, `ES.ESValue.PropertyValue`,
    `ES.ESValue.NamedValue`, `ES.ESValue.ExternValue`, `ES.ESValue.ESValue`)
    
- Ilist : 
    
    - `ES.ilist`
    
- Iindex : 
    
    - `ES.iindex`
    
- TimeSlot : 
    
    - `ES.timeslot`

- ESconstante : 
    
    - `ES.ESconstante`.
"""