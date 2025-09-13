FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Install basics
RUN apt-get update && apt-get install -y \
    git wget curl ffmpeg sox python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install PyTorch with CUDA 12.1 support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# RVC training dependencies
RUN pip3 install librosa fairseq faiss-gpu tensorboard wandb

# Clone RVC repo (for training scripts + inference code)
RUN git clone https://github.com/lj1995/VoiceConversionWebUI.git rvc && \
    pip3 install -r rvc/requirements.txt

# Expose JupyterLab
EXPOSE 8888

CMD ["bash", "start.sh"]