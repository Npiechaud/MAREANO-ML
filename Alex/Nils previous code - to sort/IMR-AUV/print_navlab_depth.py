#!/usr/bin/env python

# Read SmoothedPressure.bin (Navlab-binary)
# 28. Jan 2023 - Joakim Skjefstad

import struct
from typing import NamedTuple

# Edit these
filename = "SmoothedPressure.bin"
every_n_row = 100 # print every n rows

def print_only(row): # Check NavlabRow below for valid columns
    timestamp_corr = row.timestamp/1000000 # we need to move decimal to right place
    columns = timestamp_corr, row.depth
    print(*columns, sep=';')

# Not these
bytes_per_row = 16 # bytes per row, SmoothedPressure.bin has 16, 2 columns
number_of_doubles = str(round(bytes_per_row/8)) # 8 bytes per double (float), SmoothedPressure.bin has 2 doubles

class NavlabRow(NamedTuple):
    timestamp: float
    depth: float

def main():
    with open(filename, "rb") as fp:
        while (data_bytes := fp.read(bytes_per_row)):
            row = NavlabRow._make(struct.unpack('<'+str(number_of_doubles)+'d', data_bytes))
            fp.seek((every_n_row-1)*bytes_per_row, 1)
            print_only(row)

if __name__=='__main__':
    main()