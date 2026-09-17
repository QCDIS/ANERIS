# ANERIS

The ANERIS project aims to tackle the rapid loss of ocean biodiversity by developing innovative tools and technology for monitoring, research and management of marine life, and introducing the concept of Operational Marine Biology (OMB). OMB is a biodiversity information system which allows long-term routine measurements of ocean and coastal ecosystems and their quick interpretation and dissemination to all relevant stakeholders.

## Non Indigenous Species (NIS) analysis workflow

|    |    |
| -- | -- |
| Model Developer | Pascal Hablützel |
| VLab Developer  | Quan Pan |
| Reference |  |

### Overview

This workflow enables large-scale biogeographic screening, invasion monitoring, and rapid detection of potential non-native occurrences.

The method contains the process for checking local occurrence status of marine species: native, introduced, invasive.

The main features in the NIS workflow:

- ✔️ Batch analysis of many species × location combinations  
- ✔️ Accurate **over-water distance** calculations using searoute  
- ✔️ Integration of multiple authoritative marine datasets  
- ✔️ Clean TSV output suitable for R, Python, GIS, or spreadsheets  
- ✔️ Human-readable introduction status labels  
- ✔️ Caches repeated API queries for speed  

### Datasets

The NIS workflow combines OBIS, Marine Regions, and WRiMS data to assess marine species occurrence status across locations.

Three datasets are used:

- **OBIS** (Ocean Biodiversity Information System)  
- **Marine Regions** gazetteer  
- **WoRMS / WRiMS** (World Register of Marine Species / World Register of Introduced Marine Species)  

### Methods

In the NIS workflow, every **location + species** pair is processed in the following steps:

1. Converts geographic coordinates (DMS → decimal degrees)  
2. Retrieves OBIS occurrences and calculates **sea-route distance** to the nearest known record  
3. Identifies Marine Regions containing the location  
4. Determines WRiMS invasiveness status (native, introduced, invasive, or unrecorded)  
5. Writes all results into a **single TSV output file**
