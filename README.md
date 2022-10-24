# Chess Detection

Chess Detection is a system that allows the user to digitalize an image of a chessboard, hence rendering it able to be analyzed through Chess.com or Lichess.org.
For access to the piece detection model and the custom dataset it was used to be trained on, contact the author. 

## Setup

1. From the [Jetson Zoo](https://elinux.org/Jetson_Zoo) install:
    1. Tensorflow
        ~~~
        sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran
        sudo apt-get install python3-pip
        sudo pip3 install -U pip testresources setuptools==49.6.0
        sudo pip3 install -U numpy==1.19.4 future==0.18.2 mock==3.0.5 h5py==2.10.0 keras_preprocessing==1.1.1 keras_applications==1.0.8 gast==0.2.2 futures protobuf pybind11
        sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v46 tensorflow
        ~~~
        
    2. ONNX Runtime
        Download the .whl file from [here](https://nvidia.box.com/s/bfs688apyvor4eo8sf3y1oqtnarwafww) and run:
        ~~~
        pip3 install onnxruntime_gpu-1.8.0-cp36-cp36m-linux_aarch64.whl
        ~~~

2. Install OpenCV 4.5 with CUDA enabled. To do so, download and execute the script found [here](https://github.com/AastaNV/JEP/blob/b5209e3edfad0f3f6b33e0cbc7e15ca3a49701cf/script/install_opencv4.5.0_Jetson.sh). Warning, this process will take a few hours and you will need at least 4GB of swap space.

3. Install [onnx-tensorrt](https://github.com/onnx/onnx-tensorrt/).
    ~~~
    git clone --recursive https://github.com/onnx/onnx-tensorrt.git
    cd onnx-tensorrt
    git checkout 8.0-GA
    mkdir build && cd build
    cmake .. -DCUDA_INCLUDE_DIRS=/usr/local/cuda/include -DTENSORRT_ROOT=/usr/src/tensorrt -DGPU_ARCHS="53"
    make
    sudo make install
    export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH
    ~~~

### Utilities

- [jtop](https://github.com/rbonghi/jetson_stats) helps to monitor the usage of the Jetson Nano. To install:
    ~~~
    sudo -H pip install -U jetson-stats
    ~~~
    Then reboot the Jetson Nano. You can execute it by running `jtop`.

### Troubleshooting

- To upgrade CMake download [CMake 3.14.7](https://cmake.org/files/v3.14/cmake-3.14.7.tar.gz) and run:
    ~~~
    tar -zxvf cmake-3.14.7.tar.gz
    cd cmake-3.14.7
    sudo apt-get install libcurl4-openssl-dev
    sudo ./bootstrap
    sudo make
    sudo make install
    cmake --version
    ~~~

- To install [protobuf](https://github.com/protocolbuffers/protobuf/blob/master/src/README.md) download [protobuf 3.17.3](https://github.com/protocolbuffers/protobuf/releases/download/v3.17.3/protobuf-cpp-3.17.3.tar.gz) and run:
    ~~~
    tar -zxvf protobuf-cpp-3.17.3.tar.gz
    cd protobuf-3.17.3
    ./configure
    make
    sudo make install
    sudo ldconfig
    ~~~

- If you get the error message: `ImportError: /usr/lib/aarch64-linux-gnu/libgomp.so.1: cannot allocate memory in static TLS block` simply run:
    ~~~
    export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1
    ~~~
    In order to solve permanently the error, add that line to the end of your `~/.bashrc` file.

- If you get the error `Illegal instruction (core dumped)` run:
    ~~~
    export OPENBLAS_CORETYPE=ARMV8
    ~~~
    In order to solve permanently the error, add that line to the end of your `~/.bashrc` file.

- If you get the error `error: command 'aarch64-linux-gnu-gcc' failed with exit status 1` run:
    ~~~
    sudo apt-get install python3-dev
    ~~~


Note: You can find a list of version numbers for the python packages that have been tested to work in the `requirements.txt` file. Python 3.9 is used.

1. Depending on the inference engine install the following dependencies:
    - Keras with tensorflow backend. Slower than ONNX.
    - ONNX Runtime.
    - (Optional) TensorRT and PyCUDA. Fastest available, although more tricky to set up.

2. Create a `testing` folder with a 'test_input' subfolder where you will add your images.

3. Get access to the trained model on the custom dataset or train your own model using the piece_detection/train script by modyfing it to your needs.
4. Get access to the model for board detection
5. Run the detect.py script. Results will be saved in "testing/test_output" and a UI pygame app will be launched per image enabling you to generate FEN and navigate to Lichess.

## Contributing

Contributions are very welcome! Please check the 
[CONTRIBUTING](CONTRIBUTING.md) file for more information on how to
 contribute.
