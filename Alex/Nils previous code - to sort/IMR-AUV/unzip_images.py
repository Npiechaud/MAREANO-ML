import os
import glob
import shutil
import argparse
from datetime import datetime, timezone
from dateutil import tz
import pandas as pd

# supply path to standard Hugin data folder in Command Line Interface
# ! python "unzip_images.py" -d "C:/Users/path/to/dive/Mission_55_20220606_2"
# ! python "unzip_images.py" -d "C:/Users/a40754/Documents/AUV images/Mission_55_20220606_2"

# it will look for the images within that dive and extract them all into a separate folder for each chunk
# Note that it will not process all images but the first and last images batches often contain midwater images that cannot be stitched
# it will also create a table of images, respective pathways and timestamps read from the images names for merging with the navigation

parser = argparse.ArgumentParser()
# make a flag to provide the path to the files to process
parser.add_argument("-d", "--directory", type=str, nargs='?', help="Path to Hugin dive folder")
# parser.add_argument("-s", "--skipfirst", type=str, nargs='?', help="Decide to skip first and last")

args = parser.parse_args()

directory = args.directory

if args.directory is None:
    # by default, it will look for the images in the folders within the WD
    directory = "./"

def main():
    # set pathway to Cathx standard folder
    zip_directory = directory + "/pp/CathxC/"

    # list zipfiles
    zips = glob.glob(zip_directory + "*cathx.zip")
    # remove the first and last batches of images as they are usually full of errors
    # zips = zips[1:]
    # zips = zips[:-1]

    # prepare an images table
    images_df = pd.DataFrame()

    # extract each into a new folder
    # zip = zips[0]
    for zip in zips:
        extract_dir = zip.replace(".zip","")
        print(extract_dir)
        # unzip it
        shutil.unpack_archive(zip, extract_dir)
        # remove the .bin files from the extracted folders
        os.unlink(extract_dir + "/caminfo.bin")
        os.unlink(extract_dir + "/navdata.bin")
        # make a csv table of the image names
        images = glob.glob(extract_dir + "/*.jpg")
        # make a vector of image names
        images_names = [os.path.basename(image) for image in images]
        # extract time as character strings and make a timestamp
        dataset = []
        for image in images:
            image_name = os.path.basename(image)
            # extract time as character strings
            DT = os.path.basename(image_name).replace("image_D", "").replace("T", " ").replace(".jpg", "")[:-3]
            # convert name to timestamp
            s_spl = DT.split("-")
            s_new = ":".join(s_spl[:-1]) + '.' + s_spl[-1]
            dt = datetime.strptime(s_new, "%Y:%m:%d %H:%M:%S.%f").astimezone(tz.UTC)
            ts = dt.timestamp()
            # time stamps in time stamps formats
            # get the indexes of images within each second - the last characters in the string should be 0,1,2
            index = image_name.replace(".jpg", "")[-1:]

            # make a csv table with
            d = ({'file_path': image,
                  'filename': image_name,
                  'DATETIME': DT,
                  'datetime': dt,
                  'timestamp': ts,
                  'index': index})
            # attach to the table of the
            dataset.append(d)

        df = pd.DataFrame(dataset)
        # export csv to the chunk's directory
        df.to_csv(extract_dir + '/' + os.path.basename(extract_dir) + '.csv')

        # append the subfolder table to the images table
        df["chunk"] = os.path.basename(extract_dir)
        # Append chunk table to whole dive table
        images_df = pd.concat([images_df,df])


    # export images table at root of images directory (the pathway supplied in CLI)
    # make an output directory
    csv_directory = f"{directory}/csv"
    if os.path.exists(csv_directory):
        print("exporting to " + csv_directory)
    else:
        os.mkdir(csv_directory)  # create directory to write processed csv files
        print("Creating directory " + csv_directory + " -- exporting results there")

    images_df.to_csv(csv_directory + "/" + os.path.basename(directory) + "_images.csv",index=False )
    print("Images table exported to: " + csv_directory + "/" + os.path.basename(directory) + "_images.csv" )

if __name__=='__main__':
    main()



