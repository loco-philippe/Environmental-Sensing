# Environmental-Sensing
Make environmental data interoperable

# Why a project for Environmental Data ?

The project was born from the following observations:
    
- there is no standard format used by the sensors (apart from the Environmental Sensing Service Bluetooth) to transmit the information (binary and textual),
- there is no data exchange format presenting at the same time a temporal, 
spatial and physical component (apart from file formats),
- the main standards used to exchange data are CSV file or JSON object. These two
 standards are not suitable and not optimized for complex data,
- we spend a lot of energy converting this type of data to make it usable.

# The Environmental Sensing project (ES project)

The open-source ES project is made of :
    
- A data model that makes it possible to represent elementary observations 
(a simple one-off measurement), complex observations (multi-dimensions), 
detailed levels of representation (for example, the evolution of a plume of smoke).
- Data formats adapted to interfaces (binary payload for networks, json for requests 
or for NoSQL API, files)
- structured tools to structure, analyse and optimize data (e.g. control conceptual data 
model cardinality in a dataset)
- A library of connectors for different uses (sensors, database, storage, networks, etc.) 
in différents languages (python, C++)
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
- data exchange standard format suitable for complex data sets (available, data size divided by 5 to 10)
- data interoperability connectors (available in python since july-22)

### ***If you are interested challenge us !*** We will be very happy to show you the relevance of our approach

# Documentation

- project presentation
    - [data exchange standard - ObsJSON](https://github.com/loco-philippe/Environnemental-Sensing/blob/main/documentation/ObsJSON%20-%20Standard.pdf)
    - [Environmental Sensing project](https://github.com/loco-philippe/Environnemental-Sensing/blob/main/documentation/ES%20-%20Standard.pdf)
    - [Ilist principles presentation](https://github.com/loco-philippe/Environnemental-Sensing/blob/main/documentation/Ilist_principles.pdf)
- [Connectors documentation](https://loco-philippe.github.io/ES.html)
- Bluetooth standard for Environmental data
    - [Environmental Sensing Service (ESS) Bluetooth](https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=294797)
    - [Extension Air pollutants in ESS Bluetooth](https://www.bluetooth.com/specifications/specs/gatt-specification-supplement-6/)
    - [ESS permitted Characteristics](https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/permitted_characteristics.pdf)
