## 1. GPU setup

* For your Deep Learning libraries (PyTorch, TensorFlow, etc.) to be able to use your GPU, you will need 1) a CUDA-supporting GPU and 2) the CUDA libraries. 
* To install CUDA libraries, install the CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit. You may need to restart your computer after installing.
* Mismatches between 1) the version of your GPU driver, 2) the CUDA version that this driver supports, 3) the CUDA version that you have installed, and 4) the CUDA version supported by your DL library are a very common source of issues. So you should verify all this. SOme tips:
    * You can check your GPU driver version by running "NVIDIA Control Panel", Menu, Help, System Information. The window may have a button telling you to download updates. The window will also tell you which GPU model you have.
    * Go to https://www.nvidia.com/Download/ to check what is the latest driver for your GPU model.
    * Open a command prompt and run `nvidia-smi`. The output information includes the driver version and the "highest CUDA version that the installed driver supports" in the top-right corner.
    * Verify on the documentation/website of your DL library which CUDA version(s) it supports.
    * In the command prompt, run `nvcc --version` to check what CUDA version you have installed.
    * If anything does not match, update your GPU driver, or your version of CUDA toolkit, or your DL library. Note that installing the CUDA toolkit should also update your GPU driver, so it's perhaps a good idea to start by re-installing or upating the CUDA toolkit.

## 2. Dependencies

When installing YOLOv8, all its dependencies including PyTorch are installed. But they do recommend you install PyTorch first because its requirements vary by operating system: https://docs.ultralytics.com/quickstart/. So, in order:

### 2.1. Create a conda environment with the right version of python

See dependencies in https://github.com/ultralytics/ultralytics/tree/main to find a correct python version.

```
conda --version
conda update conda
conda --version
conda create --name yolov8env python=3.9
conda activate yolov8env
python --version
```

We will install nothing else with conda. Everything else we will do with pip. As usual with conda/pip mixes, do not install anything else with conda after you have started installing things with pip, because conda is blind to pip installs so it will mess the requirements.

### 2.2. With the conda environment activated, install the correct version of pytorch with pip

See https://pytorch.org/get-started/locally to find a machine-appropriate command to type. Check the version of CUDA matches with what you have installed.

Ensure that PyTorch was installed correctly.

From the command line, type:

```
conda list torch
```

The output should return the PyTorch libraries you just installed:

```
# packages in environment at C:\Users\Schimel_Alexandre\.conda\envs\yolov8env:
#
# Name                    Version                   Build  Channel
torch                     2.1.0+cu121              pypi_0    pypi
torchaudio                2.1.0+cu121              pypi_0    pypi
torchvision               0.16.0+cu121             pypi_0    pypi
```

Verify the installation by running sample PyTorch code. Here we will construct a randomly initialized tensor. From the command line, type:

```
python
```

then enter the following code:

```
import torch
x = torch.rand(5, 3)
print(x)
```
The output should be something similar to:

```
tensor([[0.3380, 0.3845, 0.3217],
        [0.8337, 0.9050, 0.2650],
        [0.2979, 0.7141, 0.9069],
        [0.1449, 0.1132, 0.1375],
        [0.4675, 0.3947, 0.1426]])
```

Additionally, to check if your GPU driver and CUDA is enabled and accessible by PyTorch, run the following commands to return whether or not the CUDA driver is enabled:

```
torch.cuda.is_available()
```

The output should return:

```
True
```

For more verification of the PyTorch installation, check https://wandb.ai/wandb/common-ml-errors/reports/How-To-Use-GPU-with-PyTorch---VmlldzozMzAxMDk

### 2.3. With the conda environment activated, install yolov8 with pip

```
pip install ultralytics
```

Verify the installation:

```
conda list ultralytics
```

Output should return:
```
# packages in environment at C:\Users\Schimel_Alexandre\.conda\envs\yolov8env:
#
# Name                    Version                   Build  Channel
ultralytics               8.0.196                  pypi_0    pypi
```

Check it works with sample YOLO code. Start python with:

```
python
```

then enter the following code:

```
import ultralytics
ultralytics.checks()
```

Output expected:

```
Ultralytics YOLOv8.0.196  Python-3.9.18 torch-2.1.0+cu121 CUDA:0 (NVIDIA GeForce RTX 2070 with Max-Q Design, 8192MiB)
Setup complete  (12 CPUs, 31.8 GB RAM, 665.8/926.7 GB disk)
```

```
from ultralytics import YOLO
model = YOLO('yolov8n.pt') # load object-detection model
results = model.predict('https://ultralytics.com/images/zidane.jpg') # predict objects in image
```

Output should return:

```
Found https://ultralytics.com/images/zidane.jpg locally at zidane.jpg
image 1/1 C:\Users\Schimel_Alexandre\Code\Python\IMR-YOLO\zidane.jpg: 384x640 2 persons, 1 tie, 9.0ms
Speed: 3.0ms preprocess, 9.0ms inference, 3.0ms postprocess per image at shape (1, 3, 384, 640)
```

### 3. YOLO usage

See:
* https://github.com/ultralytics/ultralytics
* https://docs.ultralytics.com/usage/python/
