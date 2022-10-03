# Code organization
The Environmental Sensing code is grouped into classes :
- [Observation](./esobservation.py) : class derived from the Ilist class with specificities linked to the notion of observation (ISO 19456 Observation and Measurement)
- [Ilist](./ilist.py) : class for indexed lists and tabular data
- [Iindex](./iindex.py) : class for structured (component of Ilist)
- [ESValue](./esValue_base.py) : classes for extended values (ESValue, DatationValue, LocationValue, PropertyValue, NamedValue, ExternValue) 

Other classes are present : 
- [Es](./esconstante.py) for constants used in the other classes
- [Timeslot](./timeslot.py) for date interval or set of date interval used in ESValue classes
- [util](./util.py) for utilities
