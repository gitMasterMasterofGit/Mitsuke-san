FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    pulseaudio \ 
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# copy app code into container
COPY /app/container .

# install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

#CMD ["python3", "FullProcess.py"]