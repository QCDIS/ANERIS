# classify_invasiveness

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
