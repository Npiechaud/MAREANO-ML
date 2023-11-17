# Seaweed AI - Identifying macroalgae in towed underwater video with Deep Learning

`seaweedai` is a Python package developed at NIWA to identify macroalgae species in underwater video footage from NIWA's SeaweedCam, using a deep-learning approach to image classification. It implements a transfer learning technique, fine-tuning the Inception V3 deep convolutional neural network that has been pretrained for image classification on the ImageNet dataset, as made available in the TensorFlow/Keras libraries.

Contact:
* Roberta D'Archino
* Alexandre Schimel
* Casey Peat

## 1. Install
### 1.1 Notes for implementation on Windows

Install `Git for Windows` (https://git-scm.com/download/win). To use `git`, navigate to the folder where the code resides (or where you wish to download it), right-click and select "Git Bash here" to open the command line prompt with git enabled.

Install `Anaconda` (https://www.anaconda.com/download). To use `conda`, search for `Anaconda Prompt` from the Windows task bar.

### 1.2 Project code

From the command prompt at a suitable download location, use the `git clone` command to download the `seaweedai` package in the current working directory:
```
git clone https://git.niwa.local/schimela/seaweedai.git
```
or
```
git clone git@git.niwa.local:schimela/seaweedai.git
```

Note: if the `seaweedai` code has been updated on gitlab since you cloned it, you can update your version with the `git pull` command from the `seaweedai` folder. Simply type:
```
git pull
```
### 1.3 Dependencies
Create a suitable conda environment from the requirements.yml file by typing:
```
conda env create --file /path/to/requirements.yml --prefix path/to/name_of_env
```
When the environment exists, activate the environment by typing:
```
conda activate path/to/name_of_env
```
### 1.4 GPU
This code uses Tensorflow version 1.13.

TensorFlow can run on the CPU, or using the GPU if it is CUDA-supported. See https://www.tensorflow.org/install/gpu#software_requirements for more information.

On the HPC, simply load the CUDA module by typing:
```
module load CUDA
```

Test the install by tying:
```
$ python
>>> import tensorflow as tf
>>> tf.test.is_gpu_available()
```
### 1.5. Run scripts

To run any of the script examples below, create a text file in the root folder of the 'seaweedai' package (e.g. 'mycodefolder' using the example above), copy the script in it, and save the file with the extension '.py' (e.g. C:\Users\myusername\mycodefolder\myscript.py). Then, from the anaconda prompt, in the 'seaweedai_env' environment and from the 'mycodefolder' folder, execute the contents of the script using the command:
```
python myscript.py
```

## 2. Data

### 2.1. Raw data
Raw data are videos from the SeaweedCam shallow-water drop-camera. They are in the QuickTime File Format (.MOV). The main repository for the videos is `R:\National\Datasets\Seaweed_Video_Data\raw_data`

Each survey with the SeaweedCam is coded as NIWA voyage codes using **SWC** as the "vessel" code, aka SWCXXYY with XX being the year and YY the survey number that year. The main repository for videos contain preliminary surveys from testing the sytem and two actual surveys: SWC1901 and SWC2001, both covering the Wellington South Coast (Island bay, Houghton Bay, Breaker Bay).

Each transect is recorded as a separate video. The name of the video file has the transect number as a suffix (e.g. `SWC1901_001.MOV` for transect #1). Occasionally, the system closes the video file and starts a new one DURING a transect. In these cases, the video files are appended with a letter (e.g. `SWC1901_009.MOV` and `SWC1901_009B.MOV` for transect #9).

### 2.2. Preprocessed data
The videos are preprocessed into two types of data:
* Individual frames extracted from the videos at regular intervals (1 every second), to use for labelling and training the models. They are recorded as png files named after the video and the frame number in the video (`prefix_frame.png`, e.g. `SWC1901_001_270.png` for frame #270 in video `SWC1901_001.MOV`).
* One csv file per video containing, for each extracted frame, the metadata hard-coded in the frame ('date', 'time', 'latitude', 'longitude'), the calculated time since start of video ('video_time'), or frame information ('prefix' and 'frame').

### 2.3. Labels

To inform on the content of the frames for training (labelling), we append additional columns to the csv files and complete each row.

Currently, the standard additional columns are: 
'comment', 'good_frame', 'turfing_or_foliose_algae_on_sand', 'sand', 'algae', 'Lessonia', 'Carpophyllum', 'Ecklonia', 'Ulva', 'Cystophora', 'Macrocystis', 'Sargassum', 'Marginariella', 'Caulerpa_flexilis', 'Caulerpa_brownii', 'Cyathea_brownii', 'Undaria', 'Landsburgia', 'cobbles'.

Others can be added. Ideally, respect the nomenclature:
* No spaces. Use underscores between words (e.g. good_frame)
* No capitalization for non-species (e.g. algae, cobbles)
* First word is capitalized for species (e.g. Lessonia, Caulerpa_brownii)

'comment' is a field for free use. All others only accept a limited number of entries: 0, 1, or 2 (or stay empty)

For 'good_frame':
* '0' (or empty) means 'this is a bad/unusable frame'. Typically applies to footage acquired while on the boat, too far from the bottom, stuck against the reef, view obstructed by algae, etc.
* '1' means 'this is a good/usable frame'.
* '2' means 'Unsure. Ignore this frame in training.'

For all others: 
* '0' (or empty) means 'absent'.
* '1' means 'present'.
* '2' means 'Unsure. Ignore this frame in training.'

The main repository for the prepared and labelled dataset is `R:\National\Datasets\Seaweed_Video_Data\ai\data`.

### 2.4. On the HPC

The code is already cloned from the repository and downloaded in `/nesi/project/niwa02671/code/seaweedai`.

The conda environment is already created at `/nesi/project/niwa02671/seaweedai_env`.

The labelled dataset for training/validation is already copied to `/nesi/project/niwa02671/data`.

The outputs from the training stage are in `/nesi/project/niwa02671/models`.

The raw videos were copied for the inference stage to `/nesi/nobackup/niwa02671/raw_data` (using nobackup because the size is too large for the regular project folder)


## 4. Preprocessing

Preprocessing is the task of extracting preprocessed data (.png frame files and .csv metadata files) from raw data (.MOV videos). These are performed with functions `seaweedai.preprocess.preprocess_videos.preprocess_video` for one video or `seaweedai.preprocess.preprocess_videos.preprocess_videos` for multiple videos.

### 4.1. preprocess_video

`preprocess_video` opens an input video and for every Nth frame, an can do either or both of:
1. extracting the metadata that is hard-coded in the frame, reformatting it (lat, long, date, time), adding information, and saving it all in a single csv file; and 
2. saving the frames as individual png files.

If you only want the frames (not the metadata in a csv file), set `output_csv_filepath` to the empty string `''`.

If you only want the metadata in a csv file (not the frames as png files), set `output_frames_dirpath` to the empty string `''`.

If `output_csv_filepath` is set to `'default'`, the csv file will be named in the format `<video_path>/<video_name>/<video_name>.csv`.

If `output_frames_dirpath` is set to `'default'`, the frames will be saved in the folder formatted as `<video_path>/<video_name>`.

If `prefix` is set to `'default'`m the name of the video will be used as prefix.

Example script:

```
from seaweedai.preprocess.preprocess_videos import preprocess_video

input_video_filepath = r'R:\National\Datasets\Seaweed_Video_Data\raw_data\Bay of Islands 2020\NINJABLD_S006_S001_W2.MOV'
every_nth_frame = 1000
verbose = 1
output_csv_filepath = 'default'
output_frames_dirpath = ''
prefix = 'default'

preprocess_video(input_video_filepath, every_nth_frame, verbose, output_csv_filepath, output_frames_dirpath, prefix)
```
### 4.2. preprocess_videos
`preprocess_videos` runs `preprocess_video` over videos found in a root folder specified in input. Substrings can be specified to limit the process to desired videos. To process all videos in the folder, use `input_videos_file_substrings = []`

Python script used for this project:
```
from seaweedai.preprocess.preprocess_videos import preprocess_videos

input_videos_root_dirpath = r'R:\National\Datasets\Seaweed_Video_Data\raw_data0'
input_videos_file_substrings = ['SWC1901', 'SWC2001'] # Only videos containing at least one of these strings will be processed
every_nth_frame = 30
verbose = 1
export_frames = True
export_metadata = True
output_dirpath = r'R:\National\Datasets\Seaweed_Video_Data\ai\data0'

preprocess_videos(input_videos_root_dirpath, input_videos_file_substrings, every_nth_frame, verbose, export_frames, export_metadata, output_dirpath)
```

## 5. Labelling

Once frames and the corresponding csv file are created, the labels must be manually informed.

### 5.1 csv approach

The main approach is to edit the csv file produced. Add categories as new columns and for each row, complete the corresponding cell with "0" (or leave empty) for absent, "1" for present, or "2" for uncertain.

You can use `seaweedai.label.add_categories_to_csv_files.add_categories_to_csv_file` to automatically add columns in one csv file, or `seaweedai.label.add_categories_to_csv_files.add_categories_to_csv_files` for all csv files within a root folder (recursively). Both functions can optionally prefill the cells with a set value. Not specifying the categories in input will add the default list of categories ('comment', 'good_frame', 'turfing_or_foliose_algae_on_sand', 'sand', 'algae', 'Lessonia', 'Carpophyllum', 'Ecklonia', 'Ulva', 'Cystophora', 'Macrocystis', 'Sargassum', 'Marginariella',
 'Caulerpa_flexilis', 'Caulerpa_brownii', 'Cyathea_brownii', 'Undaria', 'Landsburgia', 'cobbles').

Python script used for this project:
```
from seaweedai.label.add_categories_to_csv_files import add_categories_to_csv_files

input_root_dirpath = r'R:\National\Datasets\Seaweed_Video_Data\ai\data0'
add_categories_to_csv_files(input_root_dirpath)
```

### 5.2 folders approach
The issue with the approach of labelling in a csv file is that mistakes are difficult to correct. It is not easy to spot a wrong number in an array of numbers. It would be much easier to spot mistakes if frames with the same label were grouped into individual, distinct folders.

This alternative approach of labelling is possible:
1. Copy the entire set of frames obtained from pre-processing into a new folder named after a category of interest.
2. In this folder, create subfolders "0_absent", "1_present", and "2_uncertain".
3. Inspect frames and move them into the appropriate folder.

The default of this alternative approach is that if you use several categories, you need to copy the whole set of frames as many times as there are categories. This undesirable duplication of data is the reason why training operates on the labelled csv files, and not on folders of duplicated frames. It's also much slower as you go over each frame as many times as there are categories

A solution is to use both approaches:
1. Add categories to the csv file and label this file.
2. Turn this labelled csv into classified folders (using `seaweedai.label.csv_to_folder.csv_to_folder`)
3. Examine the contents of each folder and correct it if necessary (by moving frames between the "0_absent", "1_present", and "2_uncertain" subfolders of a category).
4. Turn this edited folder labelling into a new csv file (using `seaweedai.label.folder_to_csv.folder_to_csv`).

`seaweedai.label.csv_to_folder.csv_to_folder` automatically copies (or moves) png frames from an input folder, into the subfolders of an output folder containing subfolders named as per the labelling info in a csv file.

`seaweedai.label.folder_to_csv.folder_to_csv` writes and fills in a new csv file as per organization of frames in the subfolders (labels) of a category folder of a root folder. The function needs to know the original csv file to copy the metadata.


## 6. Training

Once the dataset is prepared (folders of frames + labelled csv file), one can run the training function, specifying (among other parameters) the path to the dataset and the desired category to run training on.

`seaweedai.train.trainer_categorical.trainer_categorical` performs this task. It will find the csv files in the subfolders of the data root folder (`data_root_dirpath`) and read the data for the category of interest (`category`) and relevant labels (`labels`). Datasets for the training and testing phases can be specified (`train_file_substrings` and `test_file_substrings`). The datasets can be resampled in different ways including limiting the dataset size (`max_datasize`), shuffling the dataset (`shuffle_dataset`), or equalizing the frequency of labels through subsampling and oversampling (`balance_dataset`). The function can also take several parameters for the model (`image_dim`) or training hyperparameters (`batch_size`, `num_epoch`). Outputs, including terminal log, tensorboard logs, and weights of the best model are saved into a folder named after the category of interest, in a main output folder (`experiment_root_dirpath`).

Command used on HPC for this project (repeat for all categories: good_frame, algae, Lessonia, Ecklonia, Carpophyllum):
```
python trainer_categorical.py \
--data_root_dirpath /nesi/project/niwa02671/data \
--experiment_root_dirpath /nesi/project/niwa02671/models \
--category good_frame \
--labels 0 1 \
--train_file_substrings SWC1901 SWC2001_011 SWC2001_018 \
--test_file_substrings SWC2001_002 SWC2001_008 SWC2001_010 \
--shuffle_dataset True \
--balance_dataset False \
--image_dim 299 \
--batch_size 32 \
--num_epoch 150
```

`trainer_categorical` only works for one category. Ideally, modify the code to allow looping on several training. But you will need to instantiate several tensorflow graphs.

Each instance of training is given a unique code based on the date and time of the start of training: `exp_YYYMMDD-HHMMSS`. This code is showing on the screen when starting the training, and all outputs are saved in folders bearing this code.

The training creates three types of outputs:
* A terminal log (`<experiment_root_dirpath>/<category>/terminal_logs/<training_code>.log` e.g. `R:\National\Datasets\Seaweed_Video_Data\ai\models\algae\terminal_logs\exp_20200907-123524.log`) — a text file containing (some of) the screen output of the command.
* The best model weights (`<experiment_root_dirpath>/<category>/model_weights/<training_code>/bestmodelweights.h5` e.g. `R:\National\Datasets\Seaweed_Video_Data\ai\models\algae\model_weights\exp_20200907-123524\bestmodelweights.h5`) — an HDF file containing the weights of the best model trained, to allow rebuilding the model for later inference.
* The tensorboard logs (in `<experiment_root_dirpath>/<category>/tensorboard_logs/<training_code>` e.g. `R:\National\Datasets\Seaweed_Video_Data\ai\models\algae\tensorboard_logs\exp_20200907-123524`)   — one or several files for TensorBoard, a tool for providing the measurements and visualizations needed during the machine learning workflow.

Tensorboard is a web app, started from your machine. In the terminal, type in the command line:
```
tensorboard --logdir path/to/tensorboard_logs
```
Then click on the link provided. This will open TensorBoard in your browser. 
Note this does not work from the HPC so you will have to copy over the logs from the HPC to your local machine.

All training outputs are on the HPC on `/nesi/project/niwa02671/models`. 

They were copied to `R:\National\Datasets\Seaweed_Video_Data\ai\models`


## 7. Inferencing

A trained model can be used for inferencing. One only needs the model weights file (.h5) that was produced by the training.

The main function for this is `seaweedai.inference.classify_videos.classify_videos`, which takes a root directory of videos (`videos_root_dirpath`) and a list of substrings (`videos_file_substrings`, to choose the videos in the folder), and apply a model with specified weights (`model_weights_filepath`) to predict the class of every Nth frame (`every_nth_frame`). The result is a csv file for each video, bearing the same name as the video, all saved in a folder (`output_csv_dirpath`). The csv file contain columns prefix (video name), frame (frame number) and the probabilities for each class, between 0 and 1.

Like the training, this function only works for one category at a time. Ideally, modify the code to allow looping on several models but you will need to instantiate several tensorflow graphs to separate the models.

HPC command used for this project (repeated for each model, with appropriate path to model weights and output dirpath):

```
python classify_videos.py \
--videos_root_dirpath /nesi/nobackup/niwa02671/raw_data \
--model_weights_filepath /nesi/project/niwa02671/models/good_frame/model_weights/exp_20200907-112706/bestmodelweights.h5 \
--output_csv_dirpath /nesi/project/niwa02671/outputs/good_frame
```

The results were initially saved on the HPC at `/nesi/project/niwa02671/outputs`. 

They were copied to `R:\National\Datasets\Seaweed_Video_Data\ai\outputs`.

## 8. Processing results

`seaweedai.inference.process_results.process_results` takes the results from the inference stage and metadata and process them into a single file suitable for import into a GIS.

Namely, the function: 
* reads all prediction csv files for all categories requested;
* reads all metadata csv files provided and interpolate latitude and longitude for each file;
* merge predictions and (interpolated) metadata;
* for each video, operate a process combining a number of consecutive frames and taking into account uncertainty;
* write all results into a single csv file.

The combination process consists of a weighted average where the model prediction value in the 0–1 range for a category (algae, or specie) is weighted by the usability of the frame (good_frame) in the 0–1 range. The weighted average is then turned into a hard category (aka “absent” if <0.5, or “present” if >0.5).

An estimate of uncertainty is also produced, using the minimum between 1) the absolute value of that weighted average, and 2) the average of the good_frame value. If that value is low (towards 0), it means the prediction for this group of frame is uncertain (either mostly unusable frames, or frames with mix of classes, or frames with low model confidence). If the value is high (towards 1), it means the prediction for this group of frame is rather certain (mostly usable frames AND consistent classification in the group AND high models confidence).

Python script used for this project:
```
from seaweedai.process.process_results import process_results

preds_root_dirpath = r'R:\National\Datasets\Seaweed_Video_Data\ai\outputs'
categories = ['algae', 'Ecklonia', 'Lessonia', 'Carpophyllum']
metadata_dirpath = r'R:\National\Datasets\Seaweed_Video_Data\ai\outputs\metadata'
output_csv_filepath = r'R:\National\Datasets\Seaweed_Video_Data\ai\outputs\out.csv'
interpolate_navigation = True
average_n_frames = 120

process_results(preds_root_dirpath, categories, metadata_dirpath, output_csv_filepath, interpolate_navigation, average_n_frames)
```
