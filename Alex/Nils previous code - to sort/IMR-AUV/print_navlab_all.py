#!/usr/bin/env python

# Read navlab_smooth.bin (Navlab-binary)
# 28. Jan 2023 - Joakim Skjefstad

import struct
from typing import NamedTuple

# Edit these
filename = "navlab_smooth.bin"
every_n_row = 100 # print every n rows

def print_only(row): # Check NavlabRow below for valid columns
    columns = row.timestamp, row.lat, row.lon, row.depth
    print(*columns, sep=';')

# Not these
bytes_per_row = 168 # bytes per row, navlab_smooth.bin has 168, 21 columns
number_of_doubles = str(round(bytes_per_row/8)) # 8 bytes per double (float), navlab_smooth.bin has 21 doubles

class NavlabRow(NamedTuple):
    timestamp: float
    lat: float
    lon: float
    depth: float
    roll: float
    pitch: float
    heading: float
    vel_north: float
    vel_east: float
    vel_down: float
    std_lat: float
    std_lon: float
    std_depth: float
    cov_lat_lon: float
    std_roll: float
    std_pitch: float
    std_heading: float
    std_vel_north: float
    std_vel_east: float
    std_vel_down: float
    cov_vel_north_vel_east: float

def main():
    with open(filename, "rb") as fp:
        while (data_bytes := fp.read(bytes_per_row)):
            row = NavlabRow._make(struct.unpack('<'+str(number_of_doubles)+'d', data_bytes))
            fp.seek((every_n_row-1)*bytes_per_row, 1)
            print_only(row)

if __name__=='__main__':
    main()