FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* 

# link the "python" command to python3.10
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# install compatible torch version
RUN pip install --no-cache-dir \
  torch==2.1.2+cu118 \
  torchaudio==2.1.2+cu118 \
  --index-url https://download.pytorch.org/whl/cu118

# copy app code into container
COPY app /app/app/

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r /app/requirements.txt

# Pre-load the ML models
# TODO: make this compatible with settings
# RUN echo -e "import whisperx\nwhisperx.load_model('medium', device='cuda', compute_type='float16')" | python
# RUN echo -e "import whisperx\nwhisperx.load_align_model(language_code='ja', device='cuda', model_name='vumichien/wav2vec2-xls-r-300m-japanese-large-ver2')" | python
    
ENV PYTHONPATH=/app

#CMD ["python", "-m", "app.container.ContainerMain"]