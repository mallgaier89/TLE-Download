# -*- coding: utf-8 -*-
"""
Convert satellite_tle CSV output (new CelesTrak format) to classic 3-line TLE string.
"""

import csv
import io
from datetime import datetime
from math import floor, log10


def _spacetrak_fmt(value):
    """Format a float as TLE space-track notation: SNNNNN±E (8 chars)."""
    if value == 0.0:
        return " 00000-0"
    sign = ' ' if value >= 0 else '-'
    abs_val = abs(value)
    exp = floor(log10(abs_val)) + 1        # normalise so 0.1 <= mantissa < 1
    mantissa_int = round(abs_val / (10 ** exp) * 1e5)
    if mantissa_int >= 100000:             # handle rounding overflow
        mantissa_int //= 10
        exp += 1
    exp_sign = '+' if exp >= 0 else '-'
    return f"{sign}{mantissa_int:05d}{exp_sign}{abs(exp)}"


def _tle_checksum(line):
    """Sum digits + 1 for each '-', mod 10, over first 68 chars."""
    return sum(int(c) if c.isdigit() else (1 if c == '-' else 0)
               for c in line[:68]) % 10


def csv_to_tle(tle_tuple):
    """
    Convert satellite_tle CSV output to a classic 3-line TLE string.
    NORAD IDs above 59999 are capped to 59999; checksums are recomputed.

    Parameters
    ----------
    tle_tuple : tuple of str
        3-element tuple as returned by fetch_tle_from_celestrak:
        (header_row, data_row, '').

    Returns
    -------
    str
        3-line TLE string (name \\n line1 \\n line2).
    """
    headers = next(csv.reader(io.StringIO(tle_tuple[0])))
    values  = next(csv.reader(io.StringIO(tle_tuple[1])))
    r = dict(zip(headers, values))

    name           = r['OBJECT_NAME'].strip()
    norad_id       = int(r['NORAD_CAT_ID'])
    norad_tle      = min(norad_id, 59999)          # cap if needed
    classification = r['CLASSIFICATION_TYPE'].strip()

    # --- International Designator (8 chars): YYLLLPPP ---
    # OBJECT_ID format: "YYYY-LLLP[P[P]]"
    yr, rest   = r['OBJECT_ID'].strip().split('-')
    intl_desig = yr[-2:] + rest[:3] + rest[3:].ljust(3)   # e.g. "18070A  "

    # --- Epoch: YYDDD.DDDDDDDD (14 chars) ---
    ep = datetime.fromisoformat(r['EPOCH'])
    day_frac = (ep.hour * 3600 + ep.minute * 60
                + ep.second + ep.microsecond / 1e6) / 86400
    epoch_str = f"{ep.year % 100:02d}{ep.timetuple().tm_yday + day_frac:012.8f}"

    # --- ndot: signed decimal, 10 chars " .NNNNNNNN" ---
    ndot     = float(r['MEAN_MOTION_DOT'])
    ndot_str = (' ' if ndot >= 0 else '-') + f"{abs(ndot):.8f}"[1:]  # strip leading "0"

    ndot2_str = _spacetrak_fmt(float(r['MEAN_MOTION_DDOT']))
    bstar_str = _spacetrak_fmt(float(r['BSTAR']))

    # --- Assemble Line 1 (68 chars + checksum) ---
    line1 = (f"1 {norad_tle:05d}{classification} {intl_desig} {epoch_str} "
             f"{ndot_str} {ndot2_str} {bstar_str} "
             f"{int(r['EPHEMERIS_TYPE'])} {int(r['ELEMENT_SET_NO']):4d}")
    line1 += str(_tle_checksum(line1))

    # --- Eccentricity: 7 digits, no decimal point ---
    ecc_str = f"{float(r['ECCENTRICITY']):.7f}"[2:]   # "0.0006139" -> "0006139"

    # --- Assemble Line 2 (68 chars + checksum) ---
    line2 = (f"2 {norad_tle:05d} {float(r['INCLINATION']):8.4f} "
             f"{float(r['RA_OF_ASC_NODE']):8.4f} {ecc_str} "
             f"{float(r['ARG_OF_PERICENTER']):8.4f} {float(r['MEAN_ANOMALY']):8.4f} "
             f"{float(r['MEAN_MOTION']):11.8f}{int(r['REV_AT_EPOCH']):5d}")
    line2 += str(_tle_checksum(line2))

    return f"{name}\n{line1}\n{line2}"


# =============================================================================
# Test
# =============================================================================
if __name__ == '__main__':

    test_input = (
        'OBJECT_NAME,OBJECT_ID,EPOCH,MEAN_MOTION,ECCENTRICITY,INCLINATION,'
        'RA_OF_ASC_NODE,ARG_OF_PERICENTER,MEAN_ANOMALY,EPHEMERIS_TYPE,'
        'CLASSIFICATION_TYPE,NORAD_CAT_ID,ELEMENT_SET_NO,REV_AT_EPOCH,'
        'BSTAR,MEAN_MOTION_DOT,MEAN_MOTION_DDOT',
        'ICESAT-2,2018-070A,2026-06-25T00:17:37.313088,15.28350526,'
        '.00061392,92.0079,293.0932,93.2467,266.9485,0,U,43613,999,'
        '43365,.40037453E-3,.11058E-3,0',
        ''
    )

    tle_string = csv_to_tle(test_input)

    print(tle_string)
    print("Line lengths:", [len(l) for l in tle_string.split('\n')])
