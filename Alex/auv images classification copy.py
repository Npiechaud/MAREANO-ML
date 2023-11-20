import glob
import os
import shutil
import pandas as pd
from ultralytics import YOLO

# throws an error without that....
# os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
#os.chdir('C://repos//ultralytics')

# Initialize model
model = YOLO('yolov8m-cls.pt')  # load a pretrained model (recommended for training)

# Train
results = model.train(data='mnist160', task='classify', val=False, epochs=5, imgsz=64, device=0)

model.train(data="C:/Users/Schimel_Alexandre/Code/Python/IMR-YOLO/datasets/imcls/test_fish_no_fish",
            epochs=5, 
            device=0,
            name = 'fish_no-fish') # imgsz=768, 
model = YOLO("runs/classify/fish_no-fish/weights/best.pt") # Load model with final weights

# Alex: not sure what is this part but looks like a test
# auvimagesdir = "C:/Users/a40754/Documents/temp/Mission_55_20230401_6/pp/CathxC/cathx-0001-leadin-0001-04.cathx"
auvimagesdir = "C:/Users/Schimel_Alexandre/Code/Python/IMR-YOLO/datasets/imcls/test_fish_no_fish"
results = model.predict(
   source = auvimagesdir, # source, can be a path to a folder
   save = False, # save the images with the bbox drawn?
   save_conf = True, # save the confidence of predictions (will appear at the end of the polygon xy string
   save_txt = True, # save the predicted masks
   name = "auvQual/auvQualtest") # give a name the predictions folder


# Mission_55_20230401_6

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
      # give a name the predictions folder
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