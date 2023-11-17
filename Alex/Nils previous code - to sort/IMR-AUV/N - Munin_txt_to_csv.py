import os
import glob
import argparse
from datetime import date, datetime, timezone
import pandas as pd
import numpy as np
import csv
import math
from pathlib import Path

## dev
# directory = "C:/Users/a40754/Documents/AUV images/Mission_55_20220606_2"


parser = argparse.ArgumentParser()
# make a flag to provide the path to the files to process
parser.add_argument("-d", "--directory", type=str, nargs='?', help="Path to Hugin dive folder")

args = parser.parse_args()

directory = args.directory

if args.directory is None:
    # by default, it will look for the images in the folders within the WD
    directory = "./"



def main():
    # set pathway to standard data folder
    data_directory =  directory + "/cp/Data/"

    # make an output directory
    csv_directory = f"{directory}/csv"
    if os.path.exists(csv_directory):
        print("exporting to " + csv_directory)
    else:
        os.mkdir(csv_directory)  # create directory to write processed csv files
        print("Creating directory " + csv_directory + " -- exporting results there")

    # path to file containing headers
    format_file = f"{data_directory}format.txt"

    # open the format.txt file to get the headers
    with open(format_file, 'r') as f:
        linn = f.readlines()

    # all the txt files names
    # a table of row index and each line in the txt file
    df = pd.DataFrame({'line_index': range(0, len(linn) ), 'info': linn})
    # isolate the lines with the '.txt' pattern
    df['is_file'] = df['info'].str.contains('.txt') # mark those lines as filenames
    # extract actual filenames from the whole line
    df['filename'] = df['info'].str.replace('Format of file \"', '')
    df['filename'] = df['filename'].str.replace('\"', '').str.replace("\n",'')
    diveheaders = df

    # list all files that are in the dive folder
    dive_folder = Path(directory)
    dive_files = [f for f in dive_folder.rglob("*.txt") if f.is_file()] # list .txt files full name (path / name)
    dive_files = pd.DataFrame({'file': dive_files}) # add to table
    dive_files['filename'] = dive_files['file'].apply(os.path.basename) # make a filename column
    dive_files['path'] = dive_files['file'].apply(os.path.dirname) # make a path column

    # make a table of filenames
    headers_meta = diveheaders[diveheaders['is_file'] == True].copy()
    headers_meta['start'] = ''
    headers_meta['end'] = ''
    headers_meta['txtfiles_index'] = range(headers_meta.shape[0])
    # change column location
    # headers_meta.insert(1, "txtfiles_index", headers_meta.pop("txtfiles_index"))

    # attach file names and patways
    headers_meta = pd.merge(headers_meta, dive_files, on='filename')

    for i in range(headers_meta.shape[0]):

        # select the txt file to process
        txtfile = headers_meta.iloc[i]["filename"]

        print(txtfile)
        # extract start line
        n1 = headers_meta[(headers_meta["filename"] == txtfile)].iloc[0]["line_index"]
        # extract last line
        #n2 = headers_meta.iloc[i + 1]["line_index"]
        n2 = headers_meta.iloc[headers_meta[(headers_meta["filename"] == txtfile)].pop("txtfiles_index")+1].iloc[0]["line_index"]

        # update headers_meta table with start and end rows
        headers_meta["start"] = np.where(headers_meta["filename"] == txtfile, n1, headers_meta["start"])
        headers_meta["end"] = np.where(headers_meta["filename"] == txtfile, n2, headers_meta["end"])

        # extract all relevant line for that txt file
        d_i = diveheaders.iloc[n1:n2]

        # parse names so that we can find the headers of each file
        # remove (some of) the spaces in the middle of the column
        d_i = d_i.assign(info2=lambda x: x["info"].str.replace("   ", ""))
        # extract the column number
        d_i = d_i.assign(index=lambda x: x["info2"].str.extract(r"(\d+)") ) # .astype(int)
        d_i = d_i.assign(column=lambda x: x["info2"].str.extract(r": (.*)"))
        d_i["column"] = d_i["column"].str.replace(" ", "_").str.replace("__", "_")

        dnames_i = d_i.assign(file=txtfile)

        # open the actual data
        datafile = headers_meta[headers_meta["filename"] == txtfile]["file"].iloc[0]

        data = []
        with open(datafile) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                #print(row)
                data.append(row)
        data = pd.DataFrame(data)

        # remove first and last names in list of column names
        data.columns = dnames_i["column"].iloc[1:-1].tolist()

        # export as csv
        data.to_csv(csv_directory +"/"  + os.path.basename(datafile._str.replace(".txt",".csv")) ,index=False  )
        print(txtfile + " exported to: ", csv_directory +"/"  + os.path.basename(datafile._str.replace(".txt",".csv")) )

        # -- move on to next txt file --


    # export a table of metadata of available txt files
    headers_meta.to_csv(csv_directory +"/available_txtfiles.csv",index=False)


    internalnav = pd.read_csv(csv_directory + "/" +  "navpos.csv")
    # for the navpos table:
    internalnav = internalnav[['Time',
                        'NAVIGATION_SYSTEM_DATA_NAV_LATITUDE',
                        'NAVIGATION_SYSTEM_DATA_NAV_LONGITUDE',
                        'NAVIGATION_SYSTEM_DATA_NAV_DEPTH']]



    # for the depth and altitude
    internal_altitude = pd.read_csv(csv_directory + "/" + "depth.csv")
    internal_altitude = internal_altitude[['Time',
                       'PRESSURE_DATA_PRIMARY_PS_DEPTH',
                       'PRESSURE_DATA_SECONDARYPS_DEPTH',
                       'ALTITUDE_DATA_PRIMARY_ALT_ALTITUDE',
                       'ALTITUDE_DATA_SECONDARYALT_ALTITUDE',
                       'MOTION_DATA_PRIMARY_MD_PITCH' ]]


    # merge based on nearest time stamp
    internal_navs = pd.merge_asof(internalnav, internal_altitude, on='Time', allow_exact_matches=False)

    # convert the timestamp to a datetime object in the local timezone
    internal_navs["datetime"] = [ pd.Timestamp(s, unit='s', tz=timezone.utc).floor('S') for s in internal_navs["Time"]]

    pd.Timestamp(internal_navs["Time"], unit='s', tz=timezone.utc)

    # export csv
    internal_navs.to_csv(csv_directory + "/internalnavandalt.csv")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__=='__main__':
    main()





