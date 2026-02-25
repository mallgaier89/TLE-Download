# TLE-Download
Tools for programmatically downloading TLEs without overwhelming servers with too many requests. It will store new TLEs on file. If a TLE is requested using the getTle function, it checks if one is already on file, and if yes, if it is less than one day old. Only if it is outdated will it download a new one, limiting requests to 1 per day per ID.

use import getTle from tle_download

input is NORAD ID, output is the tle string.
usespathlib, datetime, and satellite_tle.
