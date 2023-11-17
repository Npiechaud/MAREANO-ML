#!/usr/bin/env python

# Read navlab_smooth.bin (Navlab-binary), output to csv
# 28. Jan 2023 - Joakim Skjefstad

# usage:
# navlab_to_csv.py -filename="navlab_smooth.bin"
# optional arguments:
# [-nth_row=99] skip 99 rows before outputting next to csv file. 99 rows = 1 Hz, 999 rows = 0.1 Hz
# [-max_row=2000] stop after reaching 2000 rows from original file
# navlab_smooth.bin seems to have 100 Hz, one sample every 0.01s

import struct
import argparse
import csv

class NavlabSmoothRow:
    __slots__ = "timestamp", "lat", "lon", "depth", "roll", "pitch", "hdg", "vel_n", "vel_e", "vel_down",\
                "std_lat", "std_lon", "std_depth", "cov_latlon", "std_roll", "std_pitch", "std_hdg",\
                "std_vel_n", "std_vel_e", "std_vel_down", "cov_vel_n_vel_e"

    def bytes_to_variables(self, databytes):
        try:
            elem_list = struct.unpack('<21d', databytes) # 168 bytes
            self.timestamp = elem_list[0]
            self.lat = elem_list[1]
            self.lon = elem_list[2]
            self.depth = elem_list[3]
            self.roll = elem_list[4]
            self.pitch = elem_list[5]
            self.hdg = elem_list[6]
            self.vel_n = elem_list[7]
            self.vel_e = elem_list[8]
            self.vel_down = elem_list[9]
            self.std_lat = elem_list[10]
            self.std_lon = elem_list[11]
            self.std_depth = elem_list[12]
            self.cov_latlon = elem_list[13]
            self.std_roll = elem_list[14]
            self.std_pitch = elem_list[15]
            self.std_hdg = elem_list[16]
            self.std_vel_n = elem_list[17]
            self.std_vel_e = elem_list[18]
            self.std_vel_down = elem_list[19]
            self.cov_vel_n_vel_e = elem_list[20]
        except TypeError:
            print("TypeError in NavlabSmoothRow instance, exiting")
            exit()

    def __init__(self, data_bytes):
        self.bytes_to_variables(data_bytes)

    def __str__(self):
        return f'NavlabSmoothRow: {self.timestamp} {self.lat} {self.lon} {self.depth} {self.hdg}'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-filename", type=str, nargs='?')
    parser.add_argument("-nth_row", type=int, nargs='?')
    parser.add_argument("-max_row", type=int, nargs='?')
    args = parser.parse_args()

    filename = args.filename
    nth_row = args.nth_row
    max_row = args.max_row

    if args.filename is None:
        filename = "navlab_smooth.bin"
    if args.nth_row is None:
        nth_row = None
    if args.max_row is None:
        max_row = None

    with open(filename, "rb") as fp:
        current_bytes = 0
        bytes_per_row = 168

        with open('output.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')

            # Header to csv
            csvwriter.writerow(["r.timestamp", "r.lat", "r.lon", "r.depth"])

            while (data_bytes := fp.read(bytes_per_row)):
                current_bytes = current_bytes + bytes_per_row
                r = NavlabSmoothRow(data_bytes)

                print(r)

                # Data to csv, remember to change header too
                csvwriter.writerow([r.timestamp, r.lat, r.lon, r.depth])

                if nth_row:
                    fp.seek(nth_row*168, 1)

                if max_row and current_bytes > (max_row*168):
                    print("Max row", max_row, "reached, returning")
                    return

if __name__=='__main__':
    main()