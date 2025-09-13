FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg python3 python3-pip curl git sox && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Torch w/ CUDA 12.1
RUN python3 -m pip install --upgrade pip
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Pull RVC repo for inference modules

# Serverless + audio utils
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Your code
COPY handler.py .

CMD ["python3", "-u", "handler.py"]
