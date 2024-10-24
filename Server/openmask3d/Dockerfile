#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-devel

# Setup supported CUDA architectures.
ENV TORCH_CUDA_ARCH_LIST="6.1 7.0 7.5 8.6 8.9"
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
ENV FORCE_CUDA=1

# Install system dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git make build-essential libopenblas-dev libgl-dev libx11-dev \
    && rm -rf /var/lib/apt/lists/*

# Install torch-scatter.
RUN pip install torch-scatter -f https://data.pyg.org/whl/torch-2.3.1+cu118.html

# Install Detectron2.
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git@710e7795d0eeadf9def0e7ef957eea13532e34cf' --no-deps

# Create third_party directory.
RUN mkdir /third_party
WORKDIR /third_party

# Install MinkowskiEngine with explicit CUDA paths and build flags.
RUN git clone --recursive https://github.com/NVIDIA/MinkowskiEngine \
    && cd MinkowskiEngine \
    && git checkout 02fc608bea4c0549b0a7b00ca1bf15dee4a0b228 \
    && FORCE_CUDA=1 python setup.py install --force_cuda --blas=openblas

# Install miscallaneous dependencies.
RUN pip install pyyaml==5.4.1 --no-build-isolation
RUN pip install pytorch-lightning==2.4.0 \
    fire==0.7.0 \
    imageio==2.36.0 \
    tqdm \
    wandb==0.18.5 \
    python-dotenv==1.0.1 \
    pyviz3d==0.3.7 \
    scipy==1.14.1 \
    plyfile==1.1 \
    scikit-learn==1.5.2 \
    trimesh==4.5.1 \
    loguru==0.7.2 \
    albumentations==1.4.18 \
    volumentations==0.1.8 \
    antlr4-python3-runtime==4.8 \
    black==24.10.0 \
    omegaconf==2.0.6 \
    hydra-core==1.0.7 \
    pynvml==11.5.3 \
    gpustat==1.1.1 \
    tabulate==0.9.0 \
    pytest==8.3.3 \
    tensorboardX==2.6.2.2 \
    yapf==0.32.0 \
    termcolor==2.5.0 \
    addict==2.4.0 \
    blessed==1.20.0 \
    gorilla-core==0.2.7.8 \
    matplotlib==3.9.2 \
    cython==3.0.11 \
    pycocotools==2.0.8 \
    h5py==3.12.1 \
    transforms3d==0.4.2 \
    open3d==0.18.0 \
    torchmetrics==1.5.0 \
    fvcore==0.1.5.post20221221 \
    cloudpickle==3.1.0 \
    pillow==9.5.0 \
    ftfy==6.3.0 \
    regex==2024.9.11

# Clone OpenMask3D.
RUN git clone --recursive https://github.com/OpenMask3D/openmask3d.git \
    && cd openmask3d \
    && git checkout 3bc3fc52693b25668d0e91d55a2ea714544a4749

# Install PointNet2.
RUN cd openmask3d/openmask3d/class_agnostic_mask_computation/third_party/pointnet2 \
    && pip install .

# Install CLIP and Segment Anything.
RUN pip install git+https://github.com/openai/CLIP.git@a9b1bf5920416aaeaec965c25dd9e8f98c864f16 --no-deps
RUN pip install git+https://github.com/facebookresearch/segment-anything.git@6fdee8f2727f4506cfbbe553e23b895e27956588 --no-deps

# Prepare all checkpoints.
RUN python -c "import clip; clip.load('ViT-L/14@336px','cpu')"
COPY checkpoints/sam_vit_h_4b8939.pth checkpoints/sam_vit_h_4b8939.pth
COPY checkpoints/scannet200_model.ckpt checkpoints/scannet200_model.ckpt

# Mount OpenMask3D.
RUN cd openmask3d && pip install -e .
ENV PYTHONPATH=/third_party/openmask3d/openmask3d/class_agnostic_mask_computation

# Prepare web server.
WORKDIR /root
RUN pip install flask

COPY api.py api.py
EXPOSE 80

ENV OMP_NUM_THREADS=3
CMD ["python", "-u", "api.py"]

# To build the image:                    docker build --tag openmask3d .
# To run the image in server mode:       docker run --gpus all -v .\resources\scene_example:/root/input -v .\output\:/root/output openmask3d
# To run the image in interactive mode:  docker run --gpus all -v .\resources\scene_example:/root/input -v .\output\:/root/output -it openmask3d bash