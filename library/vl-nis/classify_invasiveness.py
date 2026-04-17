# classify_invasiveness

import os
import sys
import glob
from datetime import datetime

import re
import time
import math

import urllib.parse
import requests

import pandas as pd

# from tqdm import tqdm  # status bars


BASE_OBIS = "https://api.obis.org/v3"

BASE_MARINE_REGIONS = "https://www.marineregions.org/rest"
BASE_WORMS          = "https://www.marinespecies.org/rest"

_region_diag_cache = {}    


# NIS, Read input data
# =====

# 0. Small helpers
# .....
def dms_to_decimal(dms_str):
    """
    Convert a coordinate in DMS format like '51°06'39.3"N'
    or '2°36'13.6"E' to decimal degrees.
    """
    if not isinstance(dms_str, str):
        raise ValueError(f"Invalid DMS value: {dms_str}")

    # matches: degrees, minutes, seconds, hemisphere (N/S/E/W)
    m = re.match(
        r"^\s*(\d+)[°:\s]+(\d+)[\'’:\s]+(\d+(?:\.\d+)?)[\"”]?\s*([NSEW])\s*$",
        dms_str.strip()
    )
    if not m:
        raise ValueError(f"Cannot parse DMS: {dms_str}")

    deg, mins, secs, hemi = m.groups()
    deg = float(deg)
    mins = float(mins)
    secs = float(secs)

    decimal = deg + mins / 60.0 + secs / 3600.0
    if hemi in ("S", "W"):
        decimal = -decimal
    return decimal


# Find Closest Obis Occurrence
# =====

# 1. OBIS helpers: occurrences
# .....
def get_obis_occurrences(scientific_name, limit=1000):
    """
    Retrieve occurrence coordinates for a given species from OBIS.
    Returns a list of dicts with:
      - decimalLatitude
      - decimalLongitude
      - occurrenceID (OBIS occurrence id, if present)
    """
    url = f"{BASE_OBIS}/occurrence"
    params = {
        "scientificname": scientific_name,
        "size": limit
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    records = []
    for rec in data.get("results", []):
        lat = rec.get("decimalLatitude")
        lon = rec.get("decimalLongitude")
        if lat is None or lon is None:
            continue
        records.append({
            "decimalLatitude": float(lat),
            "decimalLongitude": float(lon),
            "occurrenceID": rec.get("id")
        })
    return records


# 1. OBIS helpers: closest occurrence by sea-only distance
def find_closest_obis_occurrence(scientific_name, new_lat, new_lon, limit=200):
    """
    From all OBIS occurrences of 'scientific_name', find the one with
    the shortest sea-only distance to (new_lat, new_lon).
    """
    occurrences = get_obis_occurrences(scientific_name, limit=limit)
    if not occurrences:
        raise RuntimeError(
            f"No OBIS occurrences with coordinates found for '{scientific_name}'."
        )

    best = None

    # Progress bar over all OBIS records
    # for rec in tqdm(occurrences,
    #                 desc=f"Sea-routing OBIS for {scientific_name}",
    #                 unit="record",
    #                 leave=False):
    for rec in occurrences:
        lat = rec["decimalLatitude"]
        lon = rec["decimalLongitude"]

        try:
            d = sea_distance_km(new_lat, new_lon, lat, lon)
        except Exception as e:
            print(f"[WARN] sea routing failed for ({lat}, {lon}): {e}")
            d = None

        rec["sea_distance_km"] = d
        if d is None:
            continue

        if best is None or d < best["sea_distance_km"]:
            best = rec

    if best is None:
        raise RuntimeError(
            f"No valid sea-only distances could be computed to OBIS occurrences "
            f"for '{scientific_name}'."
        )

    print(f"  * sea_distance_km = {best["sea_distance_km"]} km, {rec["occurrenceID"]}")

    return best


def sea_distance_km(ref_lat, ref_lon, lat, lon):
    """
    Shortest sea route distance in km using searoute.

    Requires:
      pip install searoute
    """
    import searoute as sr  # imported here to avoid dependency if not needed

    origin = [ref_lon, ref_lat]     # searoute expects [lon, lat]
    destination = [lon, lat]

    route = sr.searoute(origin, destination, units="km")
    if route is None:
        return None
    return float(route.properties["length"])


# Classify with Progress
# =====

# 2. Marine Regions helpers (with bbox size filter)
# .....
# classify_with_progress(): get_filtered_mrgids_for_coord()

# cache for MRGID -> diagonal distance (km)

def bbox_diagonal_km_from_degrees(min_lat, min_lon, max_lat, max_lon):
    """
    Approximate diagonal distance (km) of a lat/lon bounding box
    using simple degree-to-km conversions.
    """
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        return None
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        return None

    dlat_deg = max_lat - min_lat
    dlon_deg = max_lon - min_lon

    # Normalize longitude difference to [-180, 180]
    if dlon_deg > 180:
        dlon_deg -= 360
    elif dlon_deg < -180:
        dlon_deg += 360

    lat_km_per_deg = 111.32
    mid_lat = (min_lat + max_lat) / 2.0
    lon_km_per_deg = 111.32 * math.cos(math.radians(mid_lat))

    dlat_km = dlat_deg * lat_km_per_deg
    dlon_km = dlon_deg * lon_km_per_deg

    diag_km = math.sqrt(dlat_km**2 + dlon_km**2)

    if diag_km > 25000:
        return None

    return diag_km


# .....
def get_region_bbox_diagonal_km(mrgid):
    """
    Get approximate diagonal (km) of the bounding box for a Marine Region (MRGID).
    Uses a small cache to avoid repeated calls for the same MRGID.
    """
    mrgid_str = str(mrgid)
    if mrgid_str in _region_diag_cache:
        return _region_diag_cache[mrgid_str]

    url = f"{BASE_MARINE_REGIONS}/getGazetteerRecordByMRGID.json/{mrgid_str}/"

    try:
        resp = requests.get(url, headers={"accept": "application/json"}, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[WARN] Request error for MRGID {mrgid_str}: {e}")
        _region_diag_cache[mrgid_str] = None
        return None

    try:
        data = resp.json()
    except ValueError:
        print(f"[WARN] Could not decode JSON for MRGID {mrgid_str}")
        _region_diag_cache[mrgid_str] = None
        return None

    # API may return a list or a dict
    if isinstance(data, list):
        if not data:
            _region_diag_cache[mrgid_str] = None
            return None
        data = data[0]

    if not isinstance(data, dict):
        _region_diag_cache[mrgid_str] = None
        return None

    min_lat = data.get("minLatitude")
    min_lon = data.get("minLongitude")
    max_lat = data.get("maxLatitude")
    max_lon = data.get("maxLongitude")

    if None in (min_lat, min_lon, max_lat, max_lon):
        _region_diag_cache[mrgid_str] = None
        return None

    try:
        min_lat = float(min_lat)
        min_lon = float(min_lon)
        max_lat = float(max_lat)
        max_lon = float(max_lon)
    except ValueError:
        _region_diag_cache[mrgid_str] = None
        return None

    diag_km = bbox_diagonal_km_from_degrees(min_lat, min_lon, max_lat, max_lon)
    _region_diag_cache[mrgid_str] = diag_km
    return diag_km


# classify_with_progress()
# .....
def get_filtered_mrgids_for_coord(lat_dd, lon_dd, max_diagonal_km=3000):
    """
    Get Marine Regions MRGIDs for a point and filter out regions whose bounding
    box diagonal is more than max_diagonal_km.

    Returns a list of MRGID strings that:
      - have bounding box info, AND
      - diagonal distance <= max_diagonal_km
    """
    try:
        lat = float(lat_dd)
        lon = float(lon_dd)
    except (TypeError, ValueError):
        return []

    url = f"{BASE_MARINE_REGIONS}/getGazetteerRecordsByLatLong.json/{lat}/{lon}/"

    try:
        resp = requests.get(url, headers={"accept": "application/json"}, timeout=15)
        resp.raise_for_status()
        regions = resp.json()
    except Exception as e:
        print(f"[WARN] Marine Regions request failed for {lat}, {lon}: {e}")
        return []

    if not regions or not isinstance(regions, list):
        return []

    filtered_mrgids = []

    for item in regions:
        mrgid = item.get("MRGID")
        if not mrgid:
            continue

        diag_km = get_region_bbox_diagonal_km(mrgid)

        # Keep only if bbox is known AND size <= threshold
        if diag_km is not None and diag_km <= max_diagonal_km:
            filtered_mrgids.append(str(mrgid))

    return filtered_mrgids


# 3. WoRMS/WRiMS helpers
# .....
# main(): classify_with_progress()

def get_aphia_id(scientific_name, marine_only=True):
    """
    Use WoRMS REST:
      GET /AphiaIDByName/{ScientificName}?marine_only=true

    Returns AphiaID (int) or None
    """
    _aphia_cache = {}
    
    if scientific_name in _aphia_cache:
        return _aphia_cache[scientific_name]

    encoded_name = urllib.parse.quote(scientific_name)
    url = f"{BASE_WORMS}/AphiaIDByName/{encoded_name}"

    params = {}
    if marine_only:
        params["marine_only"] = "true"

    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 204 or not r.text.strip():
            _aphia_cache[scientific_name] = None
            return None
        r.raise_for_status()
        text = r.text.strip()
        if text == "0":
            _aphia_cache[scientific_name] = None
            return None
        aphia_id = int(text)
    except Exception as e:
        print(f"[WARN] Could not get AphiaID for '{scientific_name}': {e}")
        _aphia_cache[scientific_name] = None
        return None

    _aphia_cache[scientific_name] = aphia_id
    time.sleep(0.1)
    return aphia_id


def get_distributions_for_aphia(aphia_id):
    """
    Use WoRMS REST:
      GET /AphiaDistributionsByAphiaID/{ID}

    Returns a list of dicts.
    """
    _dist_cache  = {}
    
    if aphia_id in _dist_cache:
        return _dist_cache[aphia_id]

    url = f"{BASE_WORMS}/AphiaDistributionsByAphiaID/{aphia_id}"

    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 204 or not r.text.strip():
            _dist_cache[aphia_id] = []
            return []
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            data = []
    except Exception as e:
        print(f"[WARN] Could not get distributions for AphiaID {aphia_id}: {e}")
        _dist_cache[aphia_id] = []
        return []

    _dist_cache[aphia_id] = data
    time.sleep(0.1)
    return data


def extract_mrgid_from_locationID(locationID):
    """
    distribution['locationID'] looks like:
      'http://marineregions.org/mrgid/7130'
    We want the numeric MRGID as string, e.g. '7130'.
    """
    if not isinstance(locationID, str):
        return None
    m = re.search(r"/mrgid/(\d+)", locationID)
    return m.group(1) if m else None


# .....
def classify_invasiveness(scientific_name, mrgids_for_location):
    """
    Returns dict with:
      wrims_has_record, wrims_invasive, wrims_establishment, wrims_matching_mrgid
    """
    if not mrgids_for_location:
        return {
            "wrims_has_record": False,
            "wrims_invasive": None,
            "wrims_establishment": None,
            "wrims_matching_mrgid": None
        }

    aphia_id = get_aphia_id(scientific_name)
    if aphia_id is None:
        return {
            "wrims_has_record": False,
            "wrims_invasive": None,
            "wrims_establishment": None,
            "wrims_matching_mrgid": None
        }

    distribs = get_distributions_for_aphia(aphia_id)
    if not distribs:
        return {
            "wrims_has_record": False,
            "wrims_invasive": None,
            "wrims_establishment": None,
            "wrims_matching_mrgid": None
        }

    # Build index: MRGID -> list of distribution entries
    mrgid_to_records = {}
    for d in distribs:
        loc_id = d.get("locationID")
        mrgid = extract_mrgid_from_locationID(loc_id)
        if not mrgid:
            continue
        mrgid_to_records.setdefault(mrgid, []).append(d)

    # Check if any of the location's MRGIDs appears in the distribution records
    for loc_mrgid in mrgids_for_location:
        recs = mrgid_to_records.get(loc_mrgid)
        if not recs:
            continue

        best_invasive = None
        best_establishment = None

        for d in recs:
            invasiveness = (d.get("invasiveness") or "").lower()
            establishment = (d.get("establishmentMeans") or "").lower()

            if "invasive" in invasiveness:
                best_invasive = "invasive"
                best_establishment = establishment or None
                break

            if any(word in establishment for word in
                   ["introduced", "alien", "non-indigenous", "nonindigenous"]):
                best_invasive = "introduced"
                best_establishment = establishment or "introduced"

        if best_invasive is not None:
            return {
                "wrims_has_record": True,
                "wrims_invasive": best_invasive,
                "wrims_establishment": best_establishment,
                "wrims_matching_mrgid": loc_mrgid,
            }

    # there are distributions, but nothing matching those MRGIDs with invasiveness info
    return {
        "wrims_has_record": True,
        "wrims_invasive": None,
        "wrims_establishment": None,
        "wrims_matching_mrgid": None
    }


# .....
def wrims_label(status_dict):
    """
    Human-friendly label.
    """
    if not status_dict["wrims_has_record"]:
        return "no WRiMS distribution record"

    inv = status_dict["wrims_invasive"]
    if inv == "invasive":
        return "probably invasive"
    if inv == "introduced":
        return "probably introduced"

    return "unknown status (possibly native)"
