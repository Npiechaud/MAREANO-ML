# %%
import glob
import os
from ultralytics import YOLO

# throws an error without that....
# os.chdir('C:\\repos\\ultralytics')

# Load the model.
model = YOLO('yolov8m.pt')

# train object detection model
results = model.train(
    data="./S_borealis/data.yaml",
    task = 'detect',
    imgsz=960, epochs=5, batch=3, device=0, workers=0, name = "S_borealis" )

# predictions on images ============

# load the model:
model = YOLO("./runs/detect/S_borealis4/weights/best.pt")

# make predictions and export
images = glob.glob('./S_borealis/train/images/*.jpg')
#inputs = [images]  # list of np arrays
results = model(images)  # List of Results objects

# make prediction on an image and export results
results = model(images[2], save = True)
for image in images:
    results = model(image, save=True)

# get the bounding boxes
boxes = results[0].boxes

# annotate a video
results = model("C:/Users/a40754/OneDrive - Havforskningsinstituttet/IMR images/extracted/R2346VL2403_Sborealis_s.mp4",
                save_txt=True,
                save_conf=True,
                save=True )


