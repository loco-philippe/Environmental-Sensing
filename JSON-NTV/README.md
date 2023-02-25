    
# 0 - Abstract

Today, the semantic level of shared data remains low. It is very often limited to the type of data defined in the exchange formats (strings for CSV formats; 
numbers, strings, arrays and objects for JSON formats).

The proposed consists of adding a type and a name to the data exchanged (see also the [presentation document](https://github.com/loco-philippe/Environmental-Sensing/blob/main/JSON-NTV/JSON-NTV-standard.pdf)).

With this evolution any data, whatever its semantic level, can be identified, shared and interpreted in a consistent way.
The implementation of a type with a nested structure facilitates its appropriation.
Finally, compatibility with existing JSON structures allows progressive deployment.

# 1 - NTV structure

The constructed entities (called NTV for *named typed value*) are therefore a triplet with one mandatory element (the value in JSON format) and two optional elements (name, type).
>
> *For example, the location of Paris can be represented by:*
> - *a name: "Paris",*
> - *a type: the coordinates of a point according to the GeoJSON format,*
> - *a value: [ 2.3522, 48.8566]*

The easiest way to add this information is to use a JSON-object with a single member using the syntax [JSON-ND](https://github.com/glenkleidon/JSON-ND) for the first term of the member and the JSON-value for the second term of the member.
>
> *For the example above, the JSON representation is:*    
> *```{ "paris:point" : [2.3522, 48.8566] }```*

With this approach, three NTV entities are defined:
- a primitive entity which is not composed of any other entity (NTV-single),
- two structured entities: an unordered collection of NTV entities (NTV-set) and an ordered sequence of NTV entities (NTV-list).
      
as well as two JSON formats:
- simple format when the name and the type are not present (this is the usual case of CSV data),
- named format when the name or type is present (see example above for an NTV-single entity and below for a structured entity).
>
> *Example of an entity composed of two other entities:*
> - *```{ "cities::point": [[2.3522, 48.8566], [4.8357, 45.7640]] }``` for an NTV-list entity*
> - *```{ "cities::point": { "paris":[2.3522, 48.8566], "lyon":[4.8357, 45.7640] } }``` for an NTV-set entity*
>
> *Note: This syntax can also be used for CSV file headers*

The type incorporates a notion of `namespaces` that can be nested.
> *For example, the type: "ns1.ns2.type" means that:*
> - *ns1. is a namespace defined in the global namespace,*
> - *ns2. is a namespace defined in the ns1 namespace.,*
> - *type is defined in the ns2 namespace.*    
    
This structuring of type makes it possible to reference any type of data that has a JSON representation and to consolidate all the shared data structures within the same tree of types.

# 2 - JSON-NTV structure

The NTV triplet (name, type, value) is represented using a JSON-NTV format inspired by the RFC [JSON-ND](https://github.com/glenkleidon/JSON-ND) project :
- **```value```** (if name and type are not documented)
- **```{ "name" : value }```** (if name is documented but not type)
- **```{ ":type" : value }```** for primitive entities and **```{ "::type" : value }```** for structured entities (if type is documented but not name)
- **```{ "name:type" : value }```** for primitive entities and **```{ "name::type" : value }```** for structured entities (if type and name are documented).     

For an NTV-single, the value is the JSON-value of the entity. 
For an NTV-list, value is a JSON-array where JSON-elements are the JSON-NTV formats of included NTV entities. 
For an NTV-set, value is a JSON-object where JSON-members are the JSON-members of the JSON-NTV formats of included NTV entities. 

This JSON-NTV format allows full compatibility with existing JSON structures:
- a JSON-number, JSON-string or JSON-boolean is the representation of an NTV-single entity,
- a JSON-object with a single member is the representation of an NTV-single entity
- a JSON-array is the representation of an NTV-list entity
- a JSON-object without a single member is the representation of an NTV-set entity

# 2 - Examples of JSON-NTV representations
- NTV-single, simple format : 
   - ```"lyon"```
   - ```52.5```
   - ```{ }```
- NTV-single, named format : 
   - ```{ "paris:point" : [2.3522, 48.8566] }```
   - ```{ ":point" : [4.8357, 45.7640] }```
   - ```{ "city" : "paris" }```
- NTV-list, simple format : 
   - ```[ [2.3522, 48.8566], {"lyon" : [4.8357, 45.7640]} ]```
   - ```[ { ":point" : [2.3522, 48.8566]}, {":point" : [4.8357, 45.7640]} ]```
   - ```[ 4, 45 ]```
   - ```[ "paris" ]```
   - ```[ ]```
- NTV-list, named format : 
   - ```{ "cities::point" : [ [2.3522, 48.8566], [4.8357, 45.7640] ] }```
   - ```{ "::point" : [ [2.3522, 48.8566], {"lyon" : [4.8357, 45.7640]} ] }```
   - ```{ "simple list" : [ 4, 45.7 ] }```
   - ```{ "generic date::dat" : [ "2022-01-28T18-23-54Z", "2022-01-28", 1234.78 ] }```
- NTV-set, simple format : 
   - ```{ "nom”: "white", "prenom": "walter", "surnom": "heisenberg" }```
   - ```{ "paris:point" : [2.3522, 48.8566] , "lyon" : "france" }```
   - ```{ "paris" : [2.3522, 48.8566], "" : [4.8357, 45.7640] }```
- NTV-set, named format :
   - ```{ "cities::point": { "paris": [2.352, 48.856], "lyon": [4.835, 45.764]}}```
   - ```{ "cities" : { "paris:point" : [2.3522, 48.8566] , "lyon" : "france"} }```
   - ```{ "city" : { "paris" : [2.3522, 48.8566] } }```

# 3 - Data type

The structure of types by namespace makes it possible to have types corresponding to recognized standards at the global level.
Generic types can also be defined (calculation of the exact type when decoding the value).
    
The global namespace can include the following structures:

## 3.1 - Simple (JSON RFC8259)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| boolean (None)     | true                          |
| null (None)        | null                          |
| number (None)      | 45.2                          |
| string (None)      | "string"                      |
| array  (None)      | [1, 2, 3]                     |
| object (None)      | { "str": "test", "bool": true}|

## 3.2 - Datation (ISO8601 and Posix)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| year               | 1998                          |
| month              | 10                            |
| day                | 21                            |
| week               | 38                            |
| hour               | 20                            |
| minute             | 18                            |
| second             | 54                            |
| timeposix (dat)    | 123456.78                     |
| date (dat)         | “2022-01-28”                  |
| time (dat)         | “T18:23:54”,  “18:23”, “T18”  |
| datetime (dat)     | “2022-01-28T18-23-54Z”, “2022-01-28T18-23-54+0400”        |
| timearray (dat)    | [date1, date2]                |
| timeslot (dat)     | [timearray1, timearray2]      |   
    
## 3.3 - Duration (ISO8601 and Posix)

| type (generic type) | value example                                |
|---------------------|----------------------------------------------|
| timeinterval (dur)  | "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"  |
| durationiso (dur)   | "P0002-10- 15T10:30:20"                      |
| durposix (dur)      | 123456.78                                    |
     
## 3.4 - Location (RFC7946 and Open Location Code):

| type (generic type) | value example                                |
|---------------------|------------------------------|
| point (loc)         | [ 5.12, 45.256 ] (lon, lat)  |
| line (loc)          | [ point1, point2, point3 ]   |
| ring                | [ point1, point2, point3 ]   |
| multiline           | [ line1, line2, line3]       |
| polygon (loc)       | [ ring1, ring2, ring3]       |
| multipolygon (loc)  | [ poly1, poly2, poly3 ]      |
| bbox (loc)          | [ -10.0, -10.0, 10.0, 10.0 ] |
| geojson (loc)       | {“type”: “point”, “coordinates”: [40.0, 0.0] } |
| codeolc (loc)       | “8FW4V75V+8F6”               |

## 3.5 - Tabular data

| NTVtype  | NTVvalue                                               |
|----------|--------------------------------------------------------|
| row      | JSON-array of JSON-NTV                                 |
| field    | JSON-array of NTVvalue (following JSON-TAB format)     |
| table    | JSON-array of JSON-NTV fields with the same length     |


## 3.6 - Normalized strings

The type could be `uri`, cf exemples :
- "https://www.ietf.org/rfc/rfc3986.txt"
- "https://gallica.bnf.fr/ark:/12148/bpt6k107371t"
- "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
- "ni:///sha-256;UyaQV-Ev4rdLoHyJJWCi11OHfrYv9E1aGQAlMO2X_-Q"
- "geo:13.4125,103.86673" *(RFC5870)*
- "info:eu-repo/dai/nl/12345"
- "mailto:John.Doe@example.com"
- "news:comp.infosystems.www.servers.unix"
- "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"

## 3.7 - Namespaces

Namespaces could also be defined to reference for example:
- geopolitical entities: ISO3166-1 country code (for example "fr." for France)
- data catalogs, for example:

| NTVtype      | example JSON-NTV                                                     |
|--------------|----------------------------------------------------------------------|
| schemaorg.   | <div>{ “:schemaorg.propertyID”: “NO2” }</div><div>{ “:schemaorg.unitText”:”µg/m3”}</div>  |
| darwincore.  | { “:darwincore.acceptedNameUsage”: “Tamias minimus” }                |

## 3.8 - Identifiers

For example :
 
| type         | definition                      | exemple               |
|--------------|---------------------------------|-----------------------|
| fr.uic       | code UIC station                | 8757449               |
| fr.iata      | code IATA airport               | CDG                   |


# 4 - Example of using a `fr.` namespace

This namespace is dedicated to datasets associated with the France geopolitical namespace (see also the [presentation document](https://github.com/loco-philippe/Environmental-Sensing/blob/main/JSON-NTV/JSON-NTV-namespace-fr.pdf)).    
    
A namespace defines:
- identifiers used to access additional data,
- namespaces associated with catalogs or data sets,
- structured entities used to facilitate the use of data

## 4.1 - Identifiers
They could correspond to identifiers used in many referenced datasets (via a data schema or a data model).
   
For example :
 
| type         | definition                      | example               |
|--------------|---------------------------------|-----------------------|
| fr.dep       | code département                | 60                    |
| fr.cp        | code postal                     | 76450                 |
| fr.naf       | code NAF                        | 23                    |
| fr.siren     | code SIREN enterprise           | 418447363             |
| fr.fantoir   | code FANTOIR voie               | 4500023086F           |
| fr.uai       | code UAI établissement          | 0951099D              |
| fr.aca       | code académies                  | 22                    |
| fr.finessej  | code FINESS entité juridique    | 790001606             |
| fr.rna       | code WALDEC association         | 843S0843004860        |
| fr.spi       | code SPI numéro fiscal          | 1899582886173         |
| fr.nir       | code NIR sécurité sociale       | 164026005705953       |

## 4.2 Namespaces
Namespaces could correspond to catalogs or data sets whose data types are identified in data models or in referenced data schemas.

For example : 

|    type     | example JSON-NTV                                                                              |
|-------------|-----------------------------------------------------------------------------------------------|
| fr.sandre.  | <div>{ ":fr.sandre.CdStationHydro": K163 3010 01 }</div><div>{ ":fr.sandre.TypStationHydro": "standard" }</div>    |
| fr.synop.   | <div>{ ":fr.synop.numer_sta": 07130 }</div><div>{  ":fr.synop.t": 300, ":fr.synop.ff": 5 }</div>                   |
| fr.IRVE.    | <div>{ ":fr.IRVE.nom_station": "M2026" }</div><div>{ ":fr.IRVE.nom_operateur": "DEBELEC" }</div>                   |
| fr.BAN.     | <div>{ ":fr.BAN.numero": 54 }</div><div>{ ":fr.BAN.lon": 3.5124 }</div>                                            |

## 4.3 Entities
They could correspond to assemblies of data associated with a defined structure.
     
For example : 

|    type      | example JSON-NTV                                                                                                     |
|--------------|----------------------------------------------------------------------------------------------------------------------|
| fr.parcelle  | <div>{“maParcelle:fr.parcelle”: [ 84500, 0, I, 97]}</div><div><i>(fr.cp, fr.cadastre.préfixe, fr.cadastre.section, fr.cadastre.numéro)</i></div> |
| fr.adresse   | <div>{“monAdresse:fr.adresse”: [ 54, bis, rue de la mairie, 78730 ]</div><div><i>(fr.BAN.numero, fr.BAN.rep, fr.BAN.nom_voie, fr.cp)</i></div>  |
