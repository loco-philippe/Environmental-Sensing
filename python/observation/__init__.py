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
- the main standards used to exchange data are CSV file or JSON object. These two
 standards are not suitable and not optimized for complex data,
- we spend a lot of energy converting this type of data to make it usable.

# The Environmental Sensing project

The [ES project](https://github.com/loco-philippe/Environmental-Sensing#readme) is made of :

- A data model that makes it possible to represent elementary observations
(a simple one-off measurement), complex observations (multi-dimensions),
detailed levels of representation (for example, the evolution of a plume of smoke).
- Data formats adapted to interfaces (binary payload for networks, json for requests
or for NoSQL API, files)
- structured tools to structure, analyse and optimize data (e.g. control conceptual data
model cardinality in a dataset)
- A library of connectors for different uses (sensors, database, storage, networks, etc.)
in different languages (python, C++)
- Bidirectional interfaces to data processing tools (eg Numpy, Xarray, GIS).

It allows to :

- accelerate standards convergence
- Facilitate the use and sharing of environmental data
- Standardize both data acquisition equipment (sensors) and processing applications,
- Implement a software architecture replacing all coding / decoding operations
(interfaces) by the use of standard connectors,
- Respect and rely on the main existing standards
- Collectively share and develop a set of open-source connectors responding to
all situations (platform)

# Examples of achievements

- Bluetooth extension for Air Pollutants (available in sept-21)
- Add 'relationship' property in TableSchema (proposal)
- Development of 'indexed list' theory to deal with complex datasets (available)
- standard data exchange format suitable for complex data sets
(available, data size divided by 5 to 10)
- data interoperability connectors (available in python since july-22)

# Documentation

Documentation is available in other pages :

- The concepts of 'observation', 'indexed list' and 'ES value' are describe in
[the wiki](https://github.com/loco-philippe/Environmental-Sensing/wiki) and in
[the presentation](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/Ilist_principles.pdf).
- The non-regression tests are at
[this page](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Tests)
- Examples are
[here](https://github.com/loco-philippe/Environmental-Sensing/tree/main/python/Examples)
- data exchange standard for [observation](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/ObsJSON-Standard.pdf),
[indexed list](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/IlistJSON-Standard.pdf) and
[values](https://github.com/loco-philippe/Environmental-Sensing/tree/main/documentation/ESJSON-Standard.pdf)

Modules contain the following classes:

- Observation :

    - `python.observation.esobservation`

- ESValue :

    - `python.observation.esvalue`(`python.observation.esvalue.DatationValue`,
    - `python.observation.esvalue.LocationValue`,
    - `python.observation.esvalue.PropertyValue`, `python.observation.esvalue.NamedValue`,
    - `python.observation.esvalue.ExternValue`, `python.observation.esvalue_base.ESValue`)

- Datasets :

    - `python.observation.datasets.Sdataset`, 
    - `python.observation.datasets.Ndataset`, 

- Dataset (abstract classes):

    - `python.observation.dataset` , 
    - `python.observation.dataset_structure`, 
    - `python.observation.dataset_interface`
    - `python.observation.dataset_analysis`

- Field :

    - `python.observation.field`, `python.observation.ntvfieldructure`, 
    `python.observation.field_interface`

- TimeSlot :

    - `python.observation.timeslot`

- ES :

    - `python.observation.esconstante`.
"""
from observation.esobservation import Observation
#from observation.esvalue import NamedValue, DatationValue, LocationValue, PropertyValue, ExternValue
#from observation.esvalue_base import ESValue
from observation.dataset import Dataset, Ndataset, Sdataset
from observation.dataset_interface import DatasetInterface
from observation.dataset_structure import DatasetStructure
from observation.dataset_analysis import DatasetAnalysis
from observation.field import Field
from observation.field_interface import CborDecoder, FieldEncoder, FieldInterface
from observation.fields import Nfield, Sfield
#from observation.essearch import ESSearch
from observation.esconstante import ES, Es, _classval
from observation.util import util
#from observation.timeslot import TimeSlot
#from observation.dataset_analysis import Analysis
#print('package :', __package__)
