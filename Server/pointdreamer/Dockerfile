#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

# Setup supported CUDA architectures.
ENV TORCH_CUDA_ARCH_LIST="6.1 7.0 7.5 8.6 8.9"
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
ENV FORCE_CUDA=1

# Install system dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git make build-essential libgl-dev libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install prerequisites.
RUN pip install kaolin==0.15.0 -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.1.0_cu118.html
RUN pip install git+https://github.com/NVlabs/nvdiffrast/
RUN pip install torch-cluster==1.6.3 -f https://data.pyg.org/whl/torch-2.1.0%2Bcu118/torch_cluster-1.6.3%2Bpt21cu118-cp38-cp38-linux_x86_64.whl
RUN pip install ninja==1.11.1.1 \
    xatlas==0.0.9 \
    gdown==5.2.0 \
    plyfile==1.1 \
    tensorboard==2.18.0 \
    scikit-image==0.24.0 \
    trimesh==4.5.1 \
    open3d==0.18.0 \
    munch==4.0.0 \
    pymcubes==0.1.6 \
    torch-geometric==2.6.1 \
    opencv-python==4.10.0.84 \
    kiui==0.2.14 \
    pymeshlab==2023.12.post2 \
    rich==13.9.3

# Create third_party directory.
RUN mkdir /third_party
WORKDIR /third_party

# Install PointDreamer and its dependencies.
RUN git clone --recursive https://github.com/YuQiao0303/PointDreamer.git \
    && cd PointDreamer \
    && git checkout c0933e5f62be6ce1e02c7a2f48cffcc779ad186d


# Prepare all checkpoints.
RUN cd PointDreamer && python -c "from models.DDNM.ddnm_inpainting import Inpainter; Inpainter('cpu')"
COPY checkpoints/checkpoint.pth /third_party/PointDreamer/models/POCO/checkpoint.pth

WORKDIR /root

# To build the image:                    docker build --tag pointdreamer .
# To run the image in interactive mode:  docker run --gpus all -v .\resources\scene_example:/root/input -v .\output\:/root/output -it pointdreamer bash