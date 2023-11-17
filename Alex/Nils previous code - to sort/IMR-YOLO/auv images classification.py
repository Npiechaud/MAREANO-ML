import glob
import os
import shutil
import pandas as pd
from ultralytics import YOLO

# throws an error without that....
# os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
os.chdir('C://repos//ultralytics')


# Load a model
model = YOLO('yolov8s-cls.pt')  # load a pretrained model (recommended for training)

# Train the model
model.train(data="C:/Users/a40754/Documents/temp/Mission_55_20230401_6/pp/imageQual",
            epochs=25, imgsz=768, name = 'AUV_Quality')

# Predict with the model

model = YOLO("runs/classify/AUV_Quality/weights/best.pt")

auvimagesdir = "C:/Users/a40754/Documents/temp/Mission_55_20230401_6/pp/CathxC/cathx-0001-leadin-0001-04.cathx"

results = model.predict(
   # source, can be a path to a folder
   source=auvimagesdir,
   # save the images with the bbox drawn?
   save=False,
   # save the confidence of predictions (will appear at the end of the polygon xy string
   save_conf = True,
   # save the predicted masks
   save_txt=True,
   # give a name the predctions folder
   name = "auvQual/auvQualtest" )


Mission_55_20230401_6

# list the dirs
imagefolders = glob.glob("C:/Users/a40754/Documents/temp/Mission_55_20230401_6/pp/CathxC/cathx-**")

# take all the folder names that do not have
imagefolders = [x for x in imagefolders if 'zip' not in x]

# cycle through all the folders
folder = imagefolders[0]
for folder in imagefolders:
   print(folder)
   # make predictions
   results = model.predict(
      # source, can be a path to a folder
      source=folder,
      # save the images with the bbox drawn?
      save=False,
      # save the confidence of predictions (will appear at the end of the polygon xy string
      save_conf=True,
      # save the predicted masks
      save_txt=True,
      # give a name the predctions folder
      name="auvQual/" + os.path.basename(folder) )

# opening the labels and moving good images over
# set pathway to your predictions directory
predictions_dir = "C:/repos/ultralytics/runs/classify/auvQual/auvQualtest/labels"

#  pathway to folder where your images are
images_dir = "C:/Users/a40754/Documents/temp/Mission_55_20230401_6/pp/CathxC"
images_path =  glob.glob(images_dir + '/**/*.jpg' )

images_meta = pd.DataFrame()
images_meta['images_path'] = images_path
images_meta['filename'] = [os.path.basename(image_path) for image_path in images_path]

# open all the labels txt
labels_txt = glob.glob(predictions_dir + '/*.txt')

imageQuality = []
for txt in labels_txt:
   print(txt)

   # open the label txt
   df = pd.read_csv(txt, header=None, sep=' ')
   df.columns = ["score","class"]
   df['filename'] = os.path.basename(txt).replace('.txt', '.jpg')

   # is it good or bad?
   df = df.sort_values(by = "score", ascending=False )

   # what class has the highest score?
   quality = df.iloc[0]['class']
   print(os.path.basename(txt).replace('.txt', '.jpg') , ' - - - ',quality)

   # if it is good, copy it over to the "good" image folder
   if quality == "goodish":
      img_path = images_meta[images_meta['filename'] == df.iloc[0]['filename']]['images_path'].values
      # take the matching image and put it the new folder
      shutil.copyfile(
         src= img_path[0] ,
         dst= 'C:/Users/a40754/Documents/temp/Mission_55_20230401_6/pp/Images/' + os.path.basename( img_path[0])
      )
   else:
      print('droping image')











