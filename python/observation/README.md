# Code organization
The Environmental Sensing code is grouped into classes :
- [Observation](./esobservation.py) : class derived from the Dataset class with specificities linked to the notion of observation (ISO 19456 Observation and Measurement)
- [Dataset](./dataset.py) : class for tabular data and multi-dimensional data
- [Field](./field.py) : class for structured list of data (component of Dataset)
- [ESValue](./esValue_base.py) : classes for extended values (ESValue, DatationValue, LocationValue, PropertyValue, NamedValue, ExternValue) 

Other classes are present : 
- [Es](./esconstante.py) for constants used in the other classes
- [Timeslot](./timeslot.py) for date interval or set of date interval used in ESValue classes
- [util](./util.py) for utilities
