# Environmental-Sensing

Make environmental data interoperable

## Why a project for Environmental Data ?

There is a great diversity of solutions dealing with environmental data and paradoxically, the interoperability between these solutions remains very low, which requires
the implementation of specific interfaces and leads to the original data being distorted through successive reprocessing.

This lack of interoperability results in a lack of transversal solution both at the level of use cases (integration of personal, family, professional, regional contexts)
and at the level of the life cycle of environmental data: (1) the production of data (acquisition, observation, modeling), (2) their sharing (networks, storage), (3) the exploitation of information (restitution, analysis).

The establishment of strong interoperability is conditioned by:

- The existence of a unique and shared data structure (standard)
- The availability of open tools for exploiting this structure (connectors),

Three additional conditions are necessary for this structure to be adopted and applied:

- A simple implementation adapted to each need,
- A construction of “convergence” rather than “questioning” of the existing,
- Compatibility with the “general interest” qualification of environmental data

## The Environmental Sensing project (ES project)

The Environmental Sensing project aims to:

- Facilitate the use and sharing of environmental data
- Standardize both data acquisition equipment (sensors) and processing applications,
- Reduce coding/decoding operations (interfaces) by using standard connectors,
- Converge the main existing standards
- Optimize the volume of data exchanged

## Work currently underway

- integrate a semantic dimension into JSON formats
- propose an alternative solution to the obsolete CSV format
- improve the quality of tabular data by better taking into account relationships between fields
- improve accessibility to data from sensors
  
## Examples of achievements

### sensors

- Bluetooth extension for Air Pollutants (available since sept-21)
  - [Environmental Sensing Service (ESS) Bluetooth](https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=294797)
  - [Extension Air pollutants in ESS Bluetooth](https://www.bluetooth.com/specifications/specs/gatt-specification-supplement-6/)
  - [ESS permitted Characteristics](https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/profiles_and_services/ess/ess_permitted_characteristics.yaml)
- Tools for micro-controlers
  - [C++ Implementation](https://github.com/loco-philippe/ES-sensor) (experimental)

### semantic JSON

- JSON-NTV : a semantic format for interoperability
  - [NTV repository](https://github.com/loco-philippe/NTV#readme)
  - [Internet-Draft](https://datatracker.ietf.org/doc/draft-thomy-json-ntv/)
  - [JSON-TAB](https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-TAB-standard.pdf) : A JSON-NTV format for tabular data

### tools for structured tabular data

- Tool for structuring Datasets([TAB-dataset repository](https://github.com/loco-philippe/tab-dataset#readme))
- [NTV-pandas repository](https://github.com/loco-philippe/ntv-pandas#readme) : Semantic, compact and reversible JSON-pandas converter

### tabular data analysis

- methodology
  - [Methodology](https://github.com/loco-philippe/tab-dataset/tree/main/docs/methodology.ipynb) for taking into account relationships between fields in tabular data
  - [a simple implementation](./property_relationship/example.ipynb) used to check the validity of relationship property
  - Add 'relationship' property in TableSchema [issue #803](https://github.com/frictionlessdata/specs/issues/803)
- tools
  - Tool for Dataset analysis([TAB-analysis repository](https://github.com/loco-philippe/tab-analysis#readme))

### ***If you are interested challenge us !*** We will be very happy to show you the relevance of our approach

## References

- Tabular data study

  - [Tabular data management](./documentation/FR_tabular_structure.ipynb)
  - [What future for the CSV format](./documentation/FR_format_csv.ipynb) ?
  - [Etalab Talk](./documentation/etalabtalk_26_01_23.pdf)
- Project presentation
  - overview of [tabular structures (french)](./documentation/FR_tabular_structure.ipynb)
  - [interoperability](./documentation/interoperability.pdf) of environmental data
  - general presentation of the Environmental Sensing project [document(french)](./documentation/ES-presentation.pdf) and [slides(french)](./documentation/presentation_projet.pdf)

*The Environmental Sensing project is one of the six [BlueHats Semester of Code](https://communs.numerique.gouv.fr/bluehats/bsoc-contributions-2022/) projects selected among the 40 projects identified by in March 22.*
