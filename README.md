# NIS

|    |    |
| -- | -- |
| Model Developer | Pascal Hablützel |
| VLab Developer  | Quan Pan |
| Reference |  |

Checking local occurrence status of marine species: native, introduced, invasive  

*A tool for combining OBIS, Marine Regions, and WRiMS data to assess marine species occurrence status across locations.*

---

## Overview

This repository provides a Python script that automates the analysis of **marine species occurrences**, integrating data from:

- **OBIS** (Ocean Biodiversity Information System)  
- **Marine Regions** gazetteer  
- **WoRMS / WRiMS** (World Register of Marine Species / World Register of Introduced Marine Species)  

For every **location + species** pair, the script:

1. Converts geographic coordinates (DMS → decimal degrees)  
2. Retrieves OBIS occurrences and calculates **sea-route distance** to the nearest known record  
3. Identifies Marine Regions containing the location  
4. Determines WRiMS invasiveness status (native, introduced, invasive, or unrecorded)  
5. Writes all results into a **single TSV output file**

This workflow enables large-scale biogeographic screening, invasion monitoring, and rapid detection of potential non-native occurrences.

---

## Features

- ✔️ Batch analysis of many species × location combinations  
- ✔️ Accurate **over-water distance** calculations using searoute  
- ✔️ Integration of multiple authoritative marine datasets  
- ✔️ Clean TSV output suitable for R, Python, GIS, or spreadsheets  
- ✔️ Human-readable introduction status labels  
- ✔️ Caches repeated API queries for speed  
