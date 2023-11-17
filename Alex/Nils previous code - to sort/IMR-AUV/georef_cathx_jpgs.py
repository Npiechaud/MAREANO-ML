#!/usr/bin/env python

# Create .jgw world files for a folder of Cathx .jpg images to allow displaying
# the images in the right location on ArcGIS. Requires navigation and sensor 
# information, some available from the .jpg file (e.g. lat, long, altitude), 
# and some from fixed sensor settings (e.g. field of view)
#
# modified from pycathx.py by Joakim Skjefstad
# Alex Schimel, Joakim Skjefstad, Nils Piechaud

import argparse
import glob
import json
import os

import numpy as np
import utm
import xmltodict

number_of_bytes_to_read = 1024 # We assume all data is in first 1024 bytes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-folder", type=str, nargs='?')
    args = parser.parse_args()

    folder = args.folder

    # go through all jpgs in folder
    os.chdir(folder)
    for file in glob.glob("*.jpg"):
        filename = os.path.join(folder,file)
        with open(filename, "rb") as fp:
            header_bytes = fp.read(number_of_bytes_to_read)

            jfif_start = header_bytes.find(b"JFIF")
            xml_start = header_bytes.find(b"<?xml")
            image_start = header_bytes.find(b"<image>")
            image_end = header_bytes.find(b"</image>")

            if not jfif_start:
                print("No jfif start")
                exit("No jfif")

            if not xml_start:
                print("No xml start found")
                exit("No xml")

            if not image_start:
                print("No image start")
                exit("No image start")

            if not image_end:
                print("No image end found")
                exit("No image end")

            xml_string = header_bytes[xml_start:image_end+8].decode("utf-8")
            # print(xml_string)
            
            json_img_dict = xmltodict.parse(xml_string)

            # needed variables in jpeg file
            lat = np.asarray(json_img_dict['image']['Position']['Coords']['@lat'], dtype=float)
            lon = np.asarray(json_img_dict['image']['Position']['Coords']['@long'], dtype=float)
            alt = np.asarray(json_img_dict['image']['Position']['Depth']['@altitude'], dtype=float)
            dep = np.asarray(json_img_dict['image']['Position']['Depth']['@depth'], dtype=float)
            pit = np.asarray(json_img_dict['image']['Position']['Direction']['@pitch'], dtype=float)
            rol = np.asarray(json_img_dict['image']['Position']['Direction']['@roll'], dtype=float)
            yaw = np.asarray(json_img_dict['image']['Position']['Direction']['@yaw'], dtype=float)
            print(f'lat: {lat}, lon: {lon}, alt: {alt}, dep: {dep}, pit: {pit}, rol: {rol}, yaw: {yaw}')

            # other needed variables
            fov_width = 48.5 # FOV for width (horizontal) in degrees
            fov_height = 29 # FOV for height (vertical) in degrees
            siz_width = 4096 # number of pixels for image width (horizontal)
            siz_height = 2304 # number of pixels for image height (vertical)

            # next, do geometry calculations to figure the 6 variables needed in TFW. 
             
            # First we need to calculate the width/height of a pixel
            im_swath_width = 2*np.tan(np.radians(fov_width)/2)*alt # width of image in meters
            im_swath_height = 2*np.tan(np.radians(fov_height)/2)*alt # height of image in meters
            pix_width = im_swath_width/siz_width # width of a pixel in meters
            pix_height = im_swath_height/siz_height # height of a pixel in meters

            # from https://en.wikipedia.org/wiki/World_file
            # The generic meaning of the six parameters in a world file (as defined by Esri[1]) is:
            # Line 1: A: pixel size in the x-direction in map units/pixel
            # Line 2: D: rotation about y-axis
            # Line 3: B: rotation about x-axis
            # Line 4: E: pixel size in the y-direction in map units, almost always negative[3]
            # Line 5: C: x-coordinate of the center of the upper left pixel
            # Line 6: F: y-coordinate of the center of the upper left pixel
            # This description is however misleading in that the D and B parameters are not angular rotations, and that the A and E parameters do not correspond to the pixel size if D or B are not zero. The A, D, B and E parameters are sometimes named "x-scale", "y-skew", "x-skew" and "y-scale".
            # A better description of the A, D, B and E parameters is:
            # Line 1: A: x-component of the pixel width (x-scale)
            # Line 2: D: y-component of the pixel width (y-skew)
            # Line 3: B: x-component of the pixel height (x-skew)
            # Line 4: E: y-component of the pixel height (y-scale), typically negative
            # Line 5: C: x-coordinate of the center of the original image's upper left pixel transformed to the map
            # Line 6: F: y-coordinate of the center of the original image's upper left pixel transformed to the map

            # first, figure the rotation angle
            gridConv = 0 # to figure out
            image_dir = (yaw + gridConv)%360 # direction in degrees of image top, relative to GRID North, positive clockwise
            alphaRad = np.radians(-image_dir) # for trigo calculations, reversing sign as trigo calcs require ngles positive anti-clockwise

            # calculate A, D, B and E from the rotation angle. See images on the wiki page. 
            # Note, if we want to use square pixels, use B = D and E = -A
            A = pix_width*np.cos(alphaRad)
            D = pix_width*np.sin(alphaRad)
            B = pix_height*np.sin(alphaRad) # = D for square pixels
            E = -pix_height*np.cos(alphaRad) # = -A for square pixels

            # for C,F, we need a few things. 
            # First, project the navigation lat/long to the local UTM zone. That's for the
            # navigation reference point, so we need to add the offsets to the camera, and then
            # to the top-left pixel.

            # Navigation reference point in UTM. 
            # hard-coded forced UTM zone here. Instead, make it a parameter 
            set_zone_num = 33 # use 0 to force use the zone number in which lat/lon naturally falls
            if set_zone_num > 0:
                EG, NG, ZN, ZL = utm.from_latlon(lat, lon, set_zone_num) 
            else:
                EG, NG, ZN, ZL = utm.from_latlon(lat, lon) 

            # offsets, let's calculate them all first in the vehicle frame

            # find and complete offsets for the camera relative to nav reference point
            # for now using 0
            ref_to_cam_x = 0 # offset across track (positive starboard), in meters, of camera relative to nav reference point.
            ref_to_cam_y = 0 # offset along track (positive forward), in meters, of camera relative to nav reference point.

            # calculate offsets for the top-left pixel relative to center of the image
            # Note this is simplified, ideally take into account roll and pitch angles, which would skew the image
            imcenter_to_topleftpix_x = -im_swath_width/2
            imcenter_to_topleftpix_y = im_swath_height/2

            # total offsets
            # Note this assume cam's x,y is equal to image center x,y. In practice, account for roll and pitch here too.
            ref_to_topleftpix_x = ref_to_cam_x + imcenter_to_topleftpix_x
            ref_to_topleftpix_y = ref_to_cam_y + imcenter_to_topleftpix_y

            # transform offsets from vehicle frame (x,y) to geographic frame (easting, northing)
            ref_to_topleftpix_E =  ref_to_topleftpix_x*np.cos(-alphaRad) + ref_to_topleftpix_y*np.sin(-alphaRad)
            ref_to_topleftpix_N = -ref_to_topleftpix_x*np.sin(-alphaRad) + ref_to_topleftpix_y*np.cos(-alphaRad)

            # Finally, get easting/northing position of top-left pixel
            C = EG + ref_to_topleftpix_E
            F = NG + ref_to_topleftpix_N

            # finally, export as .jgw at the same location as .jpg files
            # Parameters must be written, one per line, in this order: A, D, B, E, C, F
            filename_jgw = filename.replace('.jpg','.jgw')
            param_list = [str(A)+'\n',str(D)+'\n',str(B)+'\n',str(E)+'\n',str(C)+'\n',str(F)]
            with open(filename_jgw, 'w') as f:
                f.writelines(param_list)
            f.close()

if __name__=='__main__':
    main()